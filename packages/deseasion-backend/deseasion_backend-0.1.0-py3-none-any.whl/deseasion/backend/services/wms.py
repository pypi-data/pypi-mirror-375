import re
from dataclasses import dataclass
from math import cos, pi
from typing import Any

import bs4
import rasterio
import rasterio.errors

from ..exceptions import (
    CapabilitiesXMLParsingError,
    ExternalRequestError,
    UploadError,
)
from .requests import get
from .wfs import version2int

PREFERRED_FORMATS = ["geotiff", "tiff" "svg", "png"]


@dataclass
class WMSLayer:
    """This dataclass is meant for holding information parsed from
    a <Layer> XML tag in a WMS GetCapabilities query response.

    .. todo::
        Add other srs options from server, and use them to make the
        projection server-side if possible. Must be able to compare srs
        on multiple formats for that...
    """

    name: str
    title: str
    description: str
    keywords: list[str]
    styles: list[str]
    srs: list[str]
    bbox: list[tuple[str, float, float, float, float]]  # first str is CRS
    min_scale_denominator: float = 1
    max_scale_denominator: float = float("inf")
    parent: "WMSLayer" = None

    @property
    def default_style(self) -> str:
        """Default map style (first one from :attr:`styles` list)"""
        return self.styles[0]

    @property
    def queryable(self) -> bool:
        """Return ``True`` if layer has sufficient information to be
        queryable.

        Indeed because of layers tree structure, often root layer is a
        placeholder for default/common attributes but is not queryable.
        """
        return (
            self.name is not None
            and len(self.styles) > 0
            and len(self.srs) > 0
            and len(self.bbox) > 0
        )


@dataclass
class WMSCapabilities:
    """This dataclass holds information parsed from a WMS GetCapabilities query
    XML response.
    """

    url: str
    version: str
    layers: dict[str, WMSLayer]
    formats: list[str]

    @property
    def queryable_layers(self) -> dict[str, WMSLayer]:
        """Return dictionary of queryable layers"""
        return {k: v for k, v in self.layers.items() if v.queryable}


def convert_raw_crs(raw_crs: str) -> str:
    """Convert a crs/srs XML tag content into a usable srs string.

    :param raw_crs: crs/srs XML tag content
    :return: srs/csr usable for projections

    .. note::
        This function is here for future proofing this module.
        Indeed for now, raw crs are directly usable, but it may change with
        future WMS versions.
    """
    return raw_crs


def parse_layer(
    layer: bs4.Tag, version: str, parent: WMSLayer = None
) -> WMSLayer:
    """Parse a XML <Layer> tag.

    :param layer: XML <Layer> tag
    :param version: WMS version
    ;param parent: parent WMS layer if any
    :return: information describing the layer
    """
    version_int = version2int(version)
    title = "".join(layer.find("Title").contents)
    name_tag = layer.find("Name")
    if name_tag is not None:
        name = "".join(name_tag.contents)
    else:
        name = None
    description_tag = layer.find("Abstract")
    description = (
        "" if description_tag is None else "\n".join(description_tag.contents)
    )
    keywords = []
    keyword_iter = []
    if version_int >= (1, 1):
        keyword_tag = layer.find("KeywordList")
        if keyword_tag is not None:
            keyword_iter = keyword_tag.contents
    else:
        keyword_tag = layer.find("Keywords")
        if keyword_tag is not None:
            keyword_iter = ",".join(keyword_tag.contents).split(",")
    for key in keyword_iter:
        match key:
            case str():
                if len(re.findall(r"\S", key)) == 0:
                    continue
                keywords.append(key.strip())
            case bs4.Tag(name="Keyword"):
                keywords.append("".join(key.contents).strip())
    srs = [] if parent is None else parent.srs.copy()
    if version_int >= (1, 3):
        for crs_tag in layer.findAll("CRS"):
            srs.append(convert_raw_crs("".join(crs_tag.contents).strip()))
    else:
        for crs_tag in layer.findAll("SRS"):
            srs += re.findall(r"\S+", " ".join(layer.find("SRS").contents))
    styles = [] if parent is None else parent.styles.copy()
    for style_tag in layer.findAll("Style", recursive=False):
        styles.append("".join(style_tag.find("Name").contents))
    bbox = [] if parent is None else parent.bbox.copy()
    if version_int >= (1, 3):
        geobbox = layer.find("EX_GeographicBoundingBox")
        if geobbox is not None:
            bbox.insert(
                0,
                (
                    "EPSG:4326",
                    float(
                        "".join(geobbox.find("southBoundLatitude").contents)
                    ),
                    float(
                        "".join(geobbox.find("westBoundLongitude").contents)
                    ),
                    float(
                        "".join(geobbox.find("northBoundLatitude").contents)
                    ),
                    float(
                        "".join(geobbox.find("eastBoundLongitude").contents)
                    ),
                ),
            )
    elif version_int >= (1,):
        latlongbbox = layer.find("LatLonBoundingBox")
        if latlongbbox is not None:
            bbox.insert(
                0,
                (
                    "EPSG:4326",
                    float(latlongbbox.attrs.get("minx")),
                    float(latlongbbox.attrs.get("miny")),
                    float(latlongbbox.attrs.get("maxx")),
                    float(latlongbbox.attrs.get("maxy")),
                ),
            )
    for bbox_tag in layer.findAll("BoundingBox"):
        crs = bbox_tag.attrs.get("CRS" if version_int >= (1, 3) else "SRS")
        bbox.append(
            (
                crs,
                float(bbox_tag.attrs.get("minx")),
                float(bbox_tag.attrs.get("miny")),
                float(bbox_tag.attrs.get("maxx")),
                float(bbox_tag.attrs.get("maxy")),
            )
        )
    min_scale = None if parent is None else parent.min_scale_denominator
    max_scale = None if parent is None else parent.max_scale_denominator
    if version_int >= (1, 3):
        min_scale_tag = layer.find("MinScaleDenominator")
        if min_scale_tag is not None:
            min_scale = float("".join(min_scale_tag.contents))
        max_scale_tag = layer.find("MaxScaleDenominator")
        if max_scale_tag is not None:
            max_scale = float("".join(max_scale_tag.contents))

    return WMSLayer(
        name,
        title,
        description,
        keywords,
        styles,
        srs,
        bbox,
        min_scale,
        max_scale,
        parent=parent,
    )


def parse_layers_tree(
    layer_tag: bs4.Tag, version: str, parent: WMSLayer = None
) -> dict[str, WMSLayer]:
    """Parse a layer tag and all its subtags layers as well.

    :param layer_tag:
    :param version: WMS version
    :param parent:
        information about parent layer (some will be merged current layer to
        apply inherited attributes of parent), defaults to ``None``
    :return: information about all layers found in the tag tree
    """
    try:
        layer_info = parse_layer(layer_tag, version, parent)
    except (AttributeError, IndexError) as e:
        raise CapabilitiesXMLParsingError(str(e))
    res = {layer_info.name: layer_info}
    for subtag in layer_tag.find_all("Layer", recursive=False):
        res = {**res, **parse_layers_tree(subtag, version, layer_info)}
    return res


def parse_capabilities(
    capabilities: bs4.Tag,
) -> tuple[str, WMSCapabilities, list[str]]:
    """Parse a <WMS_Capabilities> XML tag for information.

    :param capabilities: XML tag
    :raises CapabilitiesXMLParsingError:
        if XML parsing of `capabilities` failed
    :return: WMS server capabilities
    """
    if capabilities is None:
        raise CapabilitiesXMLParsingError("cannot find tag 'Capabilities'")
    if not isinstance(capabilities, bs4.element.Tag):
        raise CapabilitiesXMLParsingError(
            f"Malformed GetCapabilities XML: 'Capabilities' should be a tag"
            f" instead of a {type(capabilities)}"
        )
    if "version" not in capabilities.attrs:
        raise CapabilitiesXMLParsingError(
            "Malformed GetCapabilities XML: cannot find 'version'"
        )
    version = capabilities.attrs.get("version")
    version_int = version2int(version)
    layers = {}
    for layer_tag in capabilities.find("Capability").find_all(
        "Layer", recursive=False
    ):
        layers = {**layers, **parse_layers_tree(layer_tag, version)}
    formats = []
    if version_int >= (1, 1):
        try:
            for format_tag in capabilities.find("GetMap").find_all("Format"):
                formats.append("".join(format_tag.contents))
        except AttributeError:
            raise CapabilitiesXMLParsingError("cannot find GetMap XML tag")
    else:
        try:
            for format_tag in (
                capabilities.find("Map")
                .find("Format")
                .find_all(lambda t: isinstance(t, bs4.Tag))
            ):
                formats.append("".join(format_tag.name.strip()))
        except AttributeError:
            raise CapabilitiesXMLParsingError("cannot find GetMap XML tag")

    return version, layers, formats


def get_capabilities(url: str, version: str = None) -> WMSCapabilities:
    """Perform WMS GetCapabilities request and parse informations.

    :param url: WMS server URL
    :param version:
        preferred WFS version number (actual is negotiated with server)
    :raises CapabilitiesXMLParsingError:
        if XML parsing of GetCapabilities response failed
    :raises ExternalRequestError:
        if GetCapabilities request to WMS server failed
    :return: WMS server capabilities
    """
    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetCapabilities",
    }
    if version is not None:
        params["version"] = version
    response = get(url, params=params, request_type="GetCapabilities")
    soup = bs4.BeautifulSoup(response.content, features="xml")
    return WMSCapabilities(
        url,
        *parse_capabilities(soup.find(lambda tag: "Capabilities" in tag.name)),
    )


def choose_output_format(formats: list[str]) -> str:
    """Choose preferred available output format.

    :param formats: server available output formats
    :return: chosen one
    """
    _formats = [f.lower() for f in formats]

    for pf in PREFERRED_FORMATS:
        for f, format in zip(_formats, formats):
            if f.replace("image/", "") == pf:
                return format
    # Hail Mary: take first format and see if it will work
    return formats[0]


def bbox_to_size(
    wg84_bbox: tuple[float, float, float, float], resolution: float
) -> tuple[float, float]:
    """Compute ideal image size from EPSG:4236 bounding box.

    :param wg84_bbox: EPSG:4236 bounding box
    :param resolution: maximum size of a pixel (in meters)
    :return: image size
    """
    # PIXEL_SIZE = 0.00028  # resolution of one screen pixel in m
    EARTH_RADIUS = 6378137  # m
    _width_coeff = (wg84_bbox[3] - wg84_bbox[1]) * EARTH_RADIUS * pi / 180
    if wg84_bbox[2] * wg84_bbox[0] <= 0:
        width = _width_coeff
    else:
        width_up = _width_coeff * cos(wg84_bbox[2] * pi / 180)
        width_down = _width_coeff * cos(wg84_bbox[0] * pi / 180)
        width = max(width_down, width_up)
    height = (wg84_bbox[2] - wg84_bbox[0]) * EARTH_RADIUS * pi / 180
    return int(width / resolution), int(height / resolution)


def get_map(
    url: str,
    layer: str,
    version: str = None,
    bbox: tuple[float, float, float, float] = None,
    crs: str = None,
    style: str = None,
    format: str = None,
    size: tuple[float, float] = None,
    resolution: float = None,
    **kwargs,
) -> tuple[Any, Any]:
    """Perform a WMS GetMap request and retrieve result.

    :param url: WMS server URL
    :param layer:
    :param version: WMS version preferred (actual is negotiated with server)
    :param bbox:
        bounding box for image, defaults will take 'best' available bounding
        box (MUST also provide `crs` if set) from server
    :param crs:
        coordinate reference system in which to return image, defaults will
        take 'best' available coordinate reference system from server
    :param style:
        style to apply to image, defaults will take first one defined on server
    :param format:
        image output format, defaults will choose the most appropriate output
        format for this application
    :param size:
        size of image in pixels (width, height), defaults to None
    :param resolution:
        resolution of 1 pixel in meters, defaults to 1000.0
        (unused if `size` argument is set)
    :raises KeyError:
        if we cannot find a server defined bounding box for user provided `crs`
    :raises ValueError:
        if `size` was not provided and cannot be inferred
    :raises UploadError:
        if the GetMap response could not be loaded into geodata
    :raises ExternalRequestError: if GetMap request to WMS server failed
    :raises CapabilitiesXMLParsingError:
        if XML parsing of GetCapabilities failed
    :return: tuple with first result image then source object
    """
    resolution = resolution or 1000.0
    capabilities = get_capabilities(url, version)
    layer_data = capabilities.layers[layer]
    version = capabilities.version
    version_int = version2int(version)
    format = format or choose_output_format(capabilities.formats)
    style = style or layer_data.default_style
    if crs is None:
        for bbox_tuple in layer_data.bbox:
            if bbox_tuple[0] in layer_data.srs:
                crs = bbox_tuple[0]
                bbox = bbox_tuple[1:]
                break
    if bbox is None:
        for bbox_tuple in layer_data.bbox:
            if bbox_tuple[0] == crs:
                bbox = bbox_tuple[1:]
                break
    if bbox is None:
        raise KeyError(
            f"No BoundingBox provided for crs {crs} and none are defined "
            "on server"
        )
    params = {
        "SERVICE": "WMS",
        "LAYERS": [layer],
        "BBOX": ",".join(str(p) for p in bbox),
        "FORMAT": format,
        "STYLES": [style],
    }

    if version_int >= (1, 3):
        params["CRS"] = crs
    else:
        params["SRS"] = crs
    if version_int >= (1, 1):
        params["VERSION"] = version
        params["REQUEST"] = "GetMap"
    else:
        params["WMTVER"] = version
        params["REQUEST"] = "Map"
    for k, v in kwargs.items():
        params[k.capitalize()] = v
    if size is None:
        for bbox_tuple in layer_data.bbox:
            if bbox_tuple[0] == "EPSG:4326":
                wgs84_bbox = bbox_tuple[1:]
                size = bbox_to_size(wgs84_bbox, resolution)
                break
    if size is None:
        raise ValueError(
            "Argument 'size' could not be inferred and was not provided"
        )
    params["WIDTH"] = size[0]
    params["HEIGHT"] = size[1]
    response = get(url, params=params, request_type="GetMap")
    try:
        with rasterio.MemoryFile(response.content) as memfile:
            with memfile.open(crs=crs) as src:
                img = src.read(1, masked=True)
                return img, src
    except rasterio.errors.RasterioIOError:
        try:
            if "xml" not in response.headers.get("content-type", "").lower():
                raise UploadError(
                    f"Cannot load geodata from URL: {response.url}"
                )
            soup = bs4.BeautifulSoup(response.content, features="xml")
            etag = soup.find("ServiceExceptionReport").find("ServiceException")
            srv_msg = f"{etag.attrs['code']}: " + "".join(
                etag.contents
            ).replace("\n", "")
        except (IndexError, AttributeError):
            raise UploadError(f"Cannot load geodata from URL: {response.url}")
        raise ExternalRequestError(
            response.url,
            f"WMS server cannot return geodata. {srv_msg}",
            request_type="GetMap",
        )
