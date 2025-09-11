"""This module implements requests functions to external servers.
"""

import requests
from flask import current_app as app

from ..exceptions import ExternalRequestError


def get_external_timeout() -> float:
    """Return external requests timeout.

    Taken from app config 'EXTERNAL_REQUEST_TIMEOUT', defaults to 10.

    :return:
    """
    return app.config.get("EXTERNAL_REQUEST_TIMEOUT", 10)


def get_requests_proxies() -> dict | None:
    """Return set up requests proxies.

    Taken from app config 'HTTP_PROXY' and 'HTTPS_PROXY'.
    Defaults to `None` if no proxy set up.

    :return:
    """
    proxies = {}
    if "HTTP_PROXY" in app.config:
        proxies["http"] = app.config["HTTP_PROXY"]
    if "HTTPS_PROXY" in app.config:
        proxies["https"] = app.config["HTTPS_PROXY"]
    if len(proxies) > 0:
        return proxies
    return None


def get(
    url: str,
    params: dict | None,
    timeout: float | None = None,
    request_type: str | None = None,
    proxies: dict | None = None,
    **kwargs,
) -> requests.Response:
    """Perform GET request and return response.

    :param url:
    :param params: query arguments
    :param timeout: request timeout
    :param request_type: request type (only used in raised error if this fails)
    :param proxies: requests proxy
    :raises ExternalRequestError: if request fails
    :return:
    """
    timeout = timeout or get_external_timeout()
    proxies = proxies or get_requests_proxies()
    try:
        response = requests.get(
            url, params=params, timeout=timeout, proxies=proxies, **kwargs
        )
        response.raise_for_status()
        return response
    except requests.Timeout as e:
        raise ExternalRequestError(
            e.request.url, "request timeout", request_type
        )
    except requests.ConnectionError as e:
        raise ExternalRequestError(
            e.request.url, "could not reach server", request_type
        )
    except requests.HTTPError as e:
        raise ExternalRequestError(
            e.request.url,
            f"server responded with error {e.response.status_code}",
            request_type,
        )
    except requests.RequestException as e:
        if e.request is None:
            raise ExternalRequestError(
                url, "Server URL is invalid", request_type
            )
        raise ExternalRequestError(e.request.url, str(e), request_type)
