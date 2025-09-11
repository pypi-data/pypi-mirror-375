import re
from dataclasses import dataclass

import bs4
import geopandas as gpd
from fiona import BytesCollection
from fiona.errors import DriverError

from ..exceptions import (
    CapabilitiesXMLParsingError,
    ExternalRequestError,
    UploadError,
)
from .requests import get


@dataclass
class WFSFeatureType:
    """This dataclass is meant for holding information parsed from
    a <FeatureType> XML tag in a WFS GetCapabilities query response.

    .. todo::
        Add other srs options from server, and use them to make the
        projection server-side if possible. Must be able to compare srs
        on multiple formats for that...
    """

    name: str
    title: str
    description: str
    keywords: list[str]
    srs: list[str]

    @property
    def default_srs(self) -> str:
        """Default SRS projection (first one from :attr:`srs` list)"""
        return self.srs[0]


@dataclass
class WFSCapabilities:
    """This dataclass holds information parsed from a WFS GetCapabilities query
    XML response.
    """

    url: str
    version: str
    feature_types: dict[str, WFSFeatureType]


def version2int(version: str) -> tuple[int, ...]:
    """Convert version string to int tuple.

    :param version:
    :return: version int tuple in same order
    """
    return tuple(int(v) for v in version.split("."))


def convert_raw_crs(raw_crs: str) -> str:
    """Convert a crs/srs XML tag content into a usable srs string.

    Formats converted:

    * http://www.opengis.net/def/crs/epsg/0/<EPSG code>
    * http://www.opengis.net/gml/srs/epsg.xml#<EPSG code>

    Any other formats than the first 2 are passed as is, so all WFS standard
    srs formats are handled.

    :param raw_crs: crs/srs XML tag content
    :return: srs/csr usable for projections
    """
    if raw_crs.startswith("http") and "epsg.xml" in raw_crs:
        return f"EPSG:{raw_crs.split('#')[-1]}"
    if raw_crs.startswith("http") and "epsg" in raw_crs:
        return f"EPSG:{raw_crs.split('/')[-1]}"
    return raw_crs


def parse_feature_type(feature_type: bs4.Tag, version: str) -> WFSFeatureType:
    """Parse a XML <FeatureType> tag.

    :param feature_type: XML <FeatureType> tag
    :param version: WFS version
    :return: information describing the feature type

    .. todo:: Add other srs/crs options to srs
    """
    version_int = version2int(version)
    name = "".join(feature_type.find("Name").contents)
    title = "".join(feature_type.find("Title").contents)
    description = "\n".join(feature_type.find("Abstract").contents)
    keywords = []
    keyword_tag = feature_type.find("Keywords")
    for key in keyword_tag.contents:
        match key:
            case str():
                if len(re.findall(r"\S", key)) == 0:
                    continue
                keywords.append(key.strip())
            case bs4.Tag(name="Keyword"):
                keywords.append("".join(key.contents).strip())
    srs = []
    if version_int < (1, 1):
        srs.append(
            convert_raw_crs("".join(feature_type.find("SRS").contents).strip())
        )
    elif version_int >= (2, 0):
        srs.append(
            convert_raw_crs(
                "".join(feature_type.find("DefaultCRS").contents).strip()
            )
        )
    else:
        srs.append(
            convert_raw_crs(
                "".join(feature_type.find("DefaultSRS").contents).strip()
            )
        )

    return WFSFeatureType(name, title, description, keywords, srs)


def parse_capabilities(
    capabilities: bs4.Tag,
) -> tuple[str, dict[str, WFSFeatureType]]:
    """Parse a <WFS_Capabilities> XML tag for information.

    :param capabilities: XML tag
    :raises CapabilitiesXMLParsingError:
        if XML parsing of `capabilities` failed
    :return: WFS server capabilities
    """
    if capabilities is None:
        raise CapabilitiesXMLParsingError("cannot find tag 'WFS_Capabilities'")
    if not isinstance(capabilities, bs4.element.Tag):
        raise CapabilitiesXMLParsingError(
            f"Malformed GetCapabilities XML: 'WFS_Capabilities' should be a "
            f"tag instead of a {type(capabilities)}"
        )
    if "version" not in capabilities.attrs:
        raise CapabilitiesXMLParsingError(
            "Malformed GetCapabilities XML: cannot find 'version'"
        )
    version = capabilities.attrs.get("version")
    layers = {}
    for feature_tag in capabilities.find_all("FeatureType"):
        try:
            layer = parse_feature_type(feature_tag, version)
            layers[layer.name] = layer
        except (AttributeError, IndexError) as e:
            raise CapabilitiesXMLParsingError(str(e))
    return version, layers


def get_capabilities(url: str, version: str = None) -> WFSCapabilities:
    """Perform WFS GetCapabilities request and parse informations.

    :param url: WFS server URL
    :param version: WFS version number, negotiated with server if not set
    :raises CapabilitiesXMLParsingError:
        if XML parsing of `capabilities` failed
    :raises ExternalRequestError:
        if GetCapabilities request to WFS server failed
    :return: WFS server capabilities
    """
    params = {
        "service": "WFS",
        "request": "GetCapabilities",
    }
    if version is not None:
        params["version"] = version
    response = get(url, params=params, request_type="GetCapabilities")
    soup = bs4.BeautifulSoup(response.content, features="xml")
    return WFSCapabilities(
        url, *parse_capabilities(soup.find("WFS_Capabilities"))
    )


def get_feature(
    url: str, feature_type: str, version: str = None, srs: str = None, **kwargs
) -> gpd.GeoDataFrame:
    """Perform WFS GetFeature request and return geographic data.

    :param url: WFS server URL
    :param feature_type: feature type to retrieve
    :param version:
        preferred WFS version number (actual is negotiated with server)
    :param srs: coordinate system to use, use feature type default if not set
    :raises CapabilitiesXMLParsingError:
        if XML parsing of GetCapabilities response failed
    :raises ExternalRequestError:
        if GetCapabilities or GetFeature request to WFS server failed
    :raises UploadError:
        if the GetFeature response could not be loaded into geodata
    :return: geographic data
    """
    capabilities = get_capabilities(url, version)
    layer_data = capabilities.feature_types[feature_type]
    version = capabilities.version
    params = {
        "service": "WFS",
        "request": "GetFeature",
        "version": version,
    }
    version_int = version2int(version)
    if version_int >= (2, 0):
        params["typeNames"] = [feature_type]
    else:
        params["typeName"] = feature_type
    if srs is not None:
        params["srsName"] = srs
    params = {**params, **kwargs}
    response = get(url, params=params, request_type="GetFeature")
    try:
        with BytesCollection(response.content) as features:
            df = gpd.GeoDataFrame.from_features(
                features, crs=(srs or layer_data.default_srs)
            )
        return df
    except DriverError:
        try:
            if "xml" not in response.headers.get("content-type", "").lower():
                raise UploadError(
                    f"Cannot load geodata from URL: {response.url}"
                )
            soup = bs4.BeautifulSoup(response.content, features="xml")
            if version_int >= (1, 1):
                etag = soup.find("Exception")
                sub_etag = etag.find("ExceptionText")
                srv_msg = f"{etag.attrs['exceptionCode']}: " + "".join(
                    sub_etag.contents
                ).replace("\n", "")
            else:
                etag = soup.find("ServiceException")
                srv_msg = f"{etag.attrs['code']}: " + "".join(
                    etag.contents
                ).replace("\n", "")
        except (AttributeError, IndexError):
            raise UploadError(f"Cannot load geodata from URL: {response.url}")
        raise ExternalRequestError(
            response.url,
            f"WFS server cannot return geodata. {srv_msg}",
            request_type="GetFeature",
        )
