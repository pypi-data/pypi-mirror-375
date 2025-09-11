from functools import wraps

from flask import current_app as app
from flask import request
from jwt import DecodeError, ExpiredSignatureError, InvalidTokenError
from werkzeug.datastructures import Authorization

from ..exceptions import RequestError, UserTokenError
from ..models import User
from ..security import jwt_handler


def check_credentials(username, password):
    """Returns the user with the given credentials, or None"""
    user = User.get_by_username(username)
    if user is not None and user.check_password(password):
        return user
    return None


def is_jwt_valid(request_data):
    """Return True if the JWT token is valid, False otherwise"""
    token = jwt_handler.get_token_from_request(request_data)
    try:
        user_id = jwt_handler.get_user_id(token)
        return user_id is not None
    except InvalidTokenError:
        # JWT is not valid
        return False


def check_jwt_authentication(request_data):
    """Return the user corresponding to the JWT, or None"""
    token = jwt_handler.get_token_from_request(request_data)
    if token is None:
        raise RequestError("No authentication token provided", 401)
    try:
        return User.get_from_jwt(token)
    except UserTokenError as err:
        raise RequestError(str(err), 401)
    except ExpiredSignatureError:
        raise RequestError("Invalid JSON Web Token: the token is expired", 401)
    except DecodeError:
        raise RequestError(
            "Invalid JSON Web Token: the signature is not valid", 401
        )
    except InvalidTokenError:
        # the token is not valid
        # TODO: handle the expired tokens
        raise RequestError("Invalid JSON Web Token", 401)
    return None


def check_refresh_token(request_data):
    """Return the user if the refresh token is valid."""
    token = jwt_handler.get_token_from_request(request_data)
    if token is None:
        raise RequestError("No refresh token provided", 401)
    try:
        return User.get_from_refresh_token(token)
    except UserTokenError as err:
        raise RequestError(str(err), 401)
    except ExpiredSignatureError:
        raise RequestError(
            "Invalid refresh JSON Web Token: the token is expired", 401
        )
    except DecodeError:
        raise RequestError(
            "Invalid refresh JSON Web Token: the signature is not valid", 401
        )
    except InvalidTokenError:
        raise RequestError("Invalid refresh JSON Web Token", 401)
    return None


def check_basic_authentication(request_data):
    """Return the user corresponding to the Basic credentials, or None"""
    header = app.config.get("API_BASIC_AUTHENTICATION_HEADER", "Authorization")
    auth_header = request.headers.get(header, None)
    authorization = Authorization.from_header(auth_header)
    if authorization is not None:
        # valid authorization header for basic authentication
        username = authorization["username"]
        password = authorization["password"]
        user = check_credentials(username, password)
        if user is None:
            raise RequestError("Invalid credentials", 401)
        return user
    raise RequestError("No authorization header found", 401)


def refresh_token_required(fn):
    """Authenticate user with refresh token.

    Also add user to list of keyargs.

    :param fn:
    :return:
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = check_refresh_token(request)
        return fn(*args, user=user, **kwargs)

    wrapper.__apispec__ = getattr(fn, "__apispec__", {})
    wrapper.__apispec__["security"] = wrapper.__apispec__.get("security", [])
    wrapper.__apispec__["security"].append({"refreshAuth": []})
    wrapper.__apispec__["responses"] = wrapper.__apispec__.get("responses", {})
    wrapper.__apispec__["responses"][401] = {
        # "schema": MessageSchema,
        "description": "Invalid or missing refresh token",
    }
    return wrapper


def basic_authenticated(fn):
    """Authenticate user with basic authentication.

    Also add user to list of keyargs.

    :param fn:
    :return:
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = check_basic_authentication(request)
        return fn(*args, user=user, **kwargs)

    wrapper.__apispec__ = getattr(fn, "__apispec__", {})
    wrapper.__apispec__["security"] = wrapper.__apispec__.get("security", [])
    wrapper.__apispec__["security"].append({"basicAuth": []})
    wrapper.__apispec__["responses"] = wrapper.__apispec__.get("responses", {})
    wrapper.__apispec__["responses"][401] = {
        # "schema": MessageSchema,
        "description": "Error with basic authentification",
    }
    return wrapper


def token_required(fn):
    """wrapper to verify that the request contains a jwt token

    sends a 401 error if the token is missing or incorrect
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if is_jwt_valid(request):
            return fn(*args, **kwargs)
        else:
            raise RequestError("JSON Web Token invalid", 401)

    wrapper.__apispec__ = getattr(fn, "__apispec__", {})
    wrapper.__apispec__["security"] = wrapper.__apispec__.get("security", [])
    wrapper.__apispec__["security"].append({"bearerAuth": []})
    wrapper.__apispec__["responses"] = wrapper.__apispec__.get("responses", {})
    wrapper.__apispec__["responses"][401] = {
        # "schema": MessageSchema,
        "description": "Error with token authentification",
    }
    return wrapper
