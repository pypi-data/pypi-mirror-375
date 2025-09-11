import io
import json
import os
import subprocess as sp
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator
from uuid import uuid4
from zipfile import ZipFile, is_zipfile

import fiona
import fiona.errors
import geopandas as gpd
import numpy as np
import pyproj
import pyproj.crs
import rasterio
import yaml
from fiona.crs import from_epsg
from flask import current_app as app
from geoalchemy2.shape import from_shape, to_shape
from rasterio.features import shapes
from scipy import ndimage
from shapely.geometry import LinearRing, LineString, Point, Polygon, shape
from shapely.geometry.base import BaseGeometry, BaseMultipartGeometry
from shapely.ops import transform
from shapely.prepared import prep
from werkzeug.utils import secure_filename

from ..exceptions import RequestError, UploadError
from ..models import db
from ..models.geo_data import (
    BaseGeoData,
    DataAttribute,
    DataAttributeNominal,
    DataAttributeQuantitative,
    Feature,
    GeoData,
    GeoFeature,
    GlobalData,
    WFSGeoData,
    WMSGeoData,
)
from . import wfs, wms

DEFAULT_SRID = 4326
DEFAULT_PROJECTION = f"epsg:{DEFAULT_SRID}"
DEFAULT_DRIVER = "ESRI Shapefile"


def get_temporary_directory():
    """
    Return a TemporaryDirectory object.

    If the 'TEMP_DIR' defined in the application configuration exists,
    the TemporaryDirectory object will use this location. Otherwise,
    use the system temporary directory.

    Returns:
        A file object directory which can be used in a context manager and
        will be deleted on completion of the context.
    """
    temp_dir_conf = app.config.get("TEMP_DIR", None)
    if temp_dir_conf is None or os.path.isdir(temp_dir_conf) is False:
        temp_dir = None
    else:
        temp_dir = temp_dir_conf
    return TemporaryDirectory(dir=temp_dir)


def convert_to_polygon(geom: BaseGeometry) -> Polygon:
    """Try converting geometry to a polygon.

    :param geom:
    :raises TypeError:
        if `geom` cannot be converted to a :class:`shapely.Polygon`
    :return: result as a polygon
    """
    match geom:
        case Polygon():
            return geom
        case Point():
            return Polygon(list(geom.coords) * 4)
        case LinearRing():
            return Polygon(geom.coords)
        case LineString():
            coords = list(geom.coords)
            return Polygon(coords + coords[::-1])
        case _:
            raise TypeError(
                f"{type(geom).__name__} cannot be converted to Polygon"
            )


def split_multi_geometry(
    geom: BaseGeometry,
) -> Generator[BaseGeometry, None, None]:
    """Return list of connex geometries forming the geometry.

    :param geom: a geometry
    :return:
    """
    match geom:
        case BaseMultipartGeometry():
            for g in geom.geoms:
                yield from split_multi_geometry(g)
        case _:
            yield geom


def post_load_normalization(data: BaseGeoData):
    """Split multi-geometry features of persisted base geo data.

    The resulting features are then persisted back to the database.

    :param data: persisted base geo data object

    .. warning::
        This is intended to be used immedialetly after data features creation.
        Only values and input features are preserved, output features are not!
    """
    memo = {}
    memo[id(data)] = data
    for attr in data.attributes:
        memo[id(attr)] = attr
    features_list = []
    for feature in data.features:
        geom = to_shape(feature.geom)
        parts = list(split_multi_geometry(geom))
        if len(parts) > 1:
            feature.geom = from_shape(parts.pop(0), srid=DEFAULT_SRID)
            features_list.append(feature)
            for g in parts:
                new_feature = deepcopy(feature, memo)
                new_feature.geom = from_shape(g, srid=DEFAULT_SRID)
                new_feature.input_features = feature.input_features
                features_list.append(new_feature)
    db.session.add_all(features_list)
    db.session.commit()


def normalize_geometry(df: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Normalize geopandas dataframe geometry type.

    If geometry column has more than 1 type, then it is converted to polygons.
    Otherwise it is not changed.

    :param df: geopandas dataframe
    :return: normalized geopandas dataframe

    .. warning::
        Dataframe is modified in place! It is also returned for chainability
        of methods or functions.
    """
    geom_types = gpd.io.file.infer_schema(df)["geometry"]
    if isinstance(geom_types, str):
        geom_types = [geom_types]
    if len(geom_types) == 1:
        return df

    df.geometry = df.geometry.apply(convert_to_polygon)
    return df


def create_value_classes(
    start: float, stop: float, step: float
) -> list[list[float]]:
    """Create value classes from range.

    This is to be used to discretize raster geodata values so to create larger
    vector features sharing a same value class.
    Each class is a list with `[start_value, stop_value, class_value]`
    (i.e values between `start_value` and `stop_value` are replaced by
    `class_value`).

    :param start:
    :param stop:
    :param step:
    :return: value classes
    """
    range_ = np.arange(start, stop, step).tolist()
    if range_[-1] < stop:
        range_.append(stop)
    return [
        [_start, _stop, _start]
        for _start, _stop in zip(range_[:-1], range_[1:])
    ]


def save_geo_data(geo_data: BaseGeoData, directory, file_ext=None):
    """
    Save a geo data to the directory.

    It also adds following metadata as geo data fields:
    * explainability: feature explainability if any

    Returns:
        The name of the new directory.
    """
    properties = []
    for feature in geo_data.features:
        prop = {
            p.attribute.name: p.value
            for p in feature.properties
            if p.attribute.name != "fid"
        }
        prop["explainability"] = json.dumps(feature.explain())
        properties.append(prop)
    df = gpd.GeoDataFrame(
        properties,
        geometry=gpd.GeoSeries([to_shape(f.geom) for f in geo_data.features]),
        crs=from_epsg(DEFAULT_SRID),
    )

    # Normalize geometry to polygons if more than 1 type
    df = normalize_geometry(df)

    # Convert the booleans to int (booleans are not valid shapefile values)
    # see https://github.com/geopandas/geopandas/issues/437
    coltypes = gpd.io.file.infer_schema(df)["properties"]
    for colname, coltype in coltypes.items():
        if coltype == "bool":
            app.logger.info(
                "bool converted as int in {} while saving the data {}"
                "".format(colname, geo_data.name)
            )
            df[colname] = df[colname].astype("int")

    filename = secure_filename(geo_data.name)
    if file_ext is not None and file_ext.lower() != "zip":
        filename += "." + file_ext
    path = os.path.join(directory, filename)
    try:
        df.to_file(path)
    except fiona.errors.GeometryTypeValidationError:
        raise RequestError("Error in the geometries types", 500)
    except fiona.errors.DriverError:
        raise RequestError(f"File format unsupported '{file_ext}'", 415)
    return filename


def save_global_data(global_data: GlobalData, directory, file_ext=None):
    file_ext = file_ext or "json"
    properties = {p.attribute.name: p.value for p in global_data.properties}
    filename = secure_filename(global_data.name) + "." + file_ext
    path = os.path.join(directory, filename)
    with open(path, "w") as f:
        if file_ext == "json":
            json.dump(properties, f)
        elif file_ext == "yaml" or file_ext == "yml":
            yaml.dump(properties, f)
        else:
            raise RequestError(f"File format unsupported '{file_ext}'", 415)
    return filename


def get_geo_data_download(data, working_dir, file_ext=None):
    """Write the geo data to a file-like object."""
    match data:
        case BaseGeoData():
            filename = save_geo_data(data, working_dir, file_ext)
        case GlobalData():
            filename = save_global_data(data, working_dir, file_ext)
    path = os.path.join(working_dir, filename)
    print(filename, path)
    print(os.path.isfile(path), os.path.isdir(path))
    if os.path.isfile(path):
        return filename, path
    elif os.path.isdir(path):
        buff = io.BytesIO()
        with ZipFile(buff, "w") as zf:
            files = os.listdir(path)
            for f in files:
                zf.write(os.path.join(path, f), os.path.join(filename, f))
        buff.flush()
        buff.seek(0)
        return filename + ".zip", buff


def ogr2ogr_reproject(file_in, dir_out):
    """
    Reproject the file in WGS84 using ogr2ogr and return the name of the new
    file.

    Args:
        file_in (str): Path of the input shapefile.
        dir_out (str): Directory to save the reprojected file.

    Returns:
        The path of the reprojected file, or None if there was an error.
    """
    ogr2ogr_bin = app.config.get("OGR2OGR_BIN", None)
    if ogr2ogr_bin is None:
        return None
    if os.path.isfile(ogr2ogr_bin) is False:
        app.logger.warning("ogr2ogr not found at {}".format(ogr2ogr_bin))
        return None
    out_filename = str(uuid4())
    file_out = os.path.join(dir_out, out_filename)
    args = [
        ogr2ogr_bin,
        "-f",
        DEFAULT_DRIVER,
        file_out,
        file_in,
        "-t_srs",
        DEFAULT_PROJECTION.upper(),
    ]
    try:
        sp.check_call(args)
        return out_filename
    except FileNotFoundError:
        return None
    except sp.CalledProcessError:
        return None


def validate_shp_filenames(filenames):
    """
    Validate the file names.

    A shapefile data must have at least 3 files with the extensions .shp, .shx
    and .dbf.

    Raises:
        UploadError:
            if a required file (shp, dbf or shx) is missing, or if
            more than one file is found
    """
    if len(filenames) < 3:
        raise UploadError(
            "The shapefile should contain at least 3 files: "
            ".shp, .shx and .dbf"
        )
    f_exts = []
    for f in filenames:
        _, f_ext = os.path.splitext(f)
        f_exts.append(f_ext.lower())
    required = (".shp", ".shx", ".dbf")
    missing = list(filter(lambda x: x not in f_exts, required))
    if len(missing) > 0:
        raise UploadError(
            "Missing files extensions: {}".format(", ".join(missing))
        )


def create_extent_filter(extent_filter: BaseGeometry = None):
    """Create a filter function which returns True if a geometry is
    filtered out.

    :param extent_filter:
        geometry used to filter in geometries, defaults to None
    :return: filter boolean function
    """
    if extent_filter is None:
        return lambda g: False
    extent_prep = prep(extent_filter)
    return lambda g, e=extent_prep: not e.intersects(g)


def create_global_data(
    name, properties: dict[str, Any], **kwargs
) -> GlobalData:
    """Create a global data object.

    :param name:
    :param properties: set of properties organized by attribute
    :return: created global data object
    """
    data = GlobalData(name=name, feature=None, **kwargs)
    data.update_created()
    db.session.add(data)
    feature = Feature(data=data)
    data.feature = feature
    db.session.add(feature)
    values = []
    for aname, avalue in properties.items():
        attr = data._choose_attribute_type(avalue)(name=aname, data=data)
        values.append(
            attr.get_value_class()(
                value=avalue, attribute=attr, feature=feature
            )
        )
        data.attributes.append(attr)
    db.session.add_all(values)
    db.session.commit()
    return data


def load_vector_file(path, extent_filter: BaseGeometry = None):
    """
    Create and return a GeoData object created from a vector file.

    Tries to reproject the geometries to EPSG:4326.
    """
    with fiona.open(path, "r") as source:
        project = None
        if source.crs != {}:
            proj_out = pyproj.crs.CRS(DEFAULT_PROJECTION)
            proj_in = pyproj.crs.CRS(source.crs)
            if not proj_in.equals(proj_out):
                project = pyproj.Transformer.from_crs(
                    proj_in, proj_out
                ).transform
        geo_data = GeoData(
            name=source.name,
            original_name=source.name,
            source_driver=source.driver,
        )
        geo_data.update_created()
        # Generate an id for the geo data
        db.session.add(geo_data)
        db.session.flush()
        features = []
        values = []
        for aname, atype in source.schema["properties"].items():
            proptype = fiona.prop_type(atype)
            if proptype in (int, float):
                attr = DataAttributeQuantitative(
                    name=aname, data_id=geo_data.id
                )
            else:
                attr = DataAttributeNominal(name=aname, data_id=geo_data.id)
            geo_data.attributes.append(attr)
        attributes_dict = {a.name: a for a in geo_data.attributes}
        extent_filter_fn = create_extent_filter(extent_filter)
        for s_feature in source:
            geom = shape(s_feature["geometry"])
            if project is not None:
                geom = transform(project, geom)
            if extent_filter_fn(geom):
                # Ignore geometry outside extent (if set)
                continue
            geom_geometry = from_shape(geom, srid=DEFAULT_SRID)
            feature = GeoFeature(geom=geom_geometry, data_id=geo_data.id)
            geo_data.features.append(feature)
            props = s_feature["properties"]
            for prop, val in props.items():
                cls = attributes_dict[prop].get_value_class()
                values.append(
                    cls(
                        value=val,
                        attribute=attributes_dict[prop],
                        feature=feature,
                    )
                )
        db.session.add_all(values)
        db.session.add_all(features)
        db.session.commit()
        return geo_data


def load_wfs(wfs_stream: WFSGeoData) -> WFSGeoData:
    """Create and return a StreamGeoData object created from a WFS URL.

    :param wfs_stream:
        WFS stream to load (can be partial as long as it contains at least
        the server URL and feature type)
    :raise KeyError: if `wfs_stream.feature_type` is not found on WFS server
    :return:

    .. note:: WFS object is not persisted!
    """
    capabilities = wfs.get_capabilities(wfs_stream.url, wfs_stream.version)
    if wfs_stream.feature_type not in capabilities.feature_types:
        raise KeyError(
            f"No feature type found on server {wfs_stream.url} with given "
            f"name '{wfs_stream.feature_type}'"
        )
    feature_info = capabilities.feature_types[wfs_stream.feature_type]
    # Do we really need original_name field?
    wfs_stream.original_name = wfs_stream.feature_type
    wfs_stream.name = secure_filename(feature_info.name)
    wfs_stream.title = feature_info.title
    wfs_stream.description = feature_info.description
    wfs_stream.keywords = feature_info.keywords

    # Load features so stream can be viewed directly
    features = load_from_wfs(wfs_stream)
    # List the data attributes
    attrs = []
    for f in features:
        for p in f.properties:
            if p.attribute not in attrs:
                attrs.append(p.attribute)
    wfs_stream.features = features
    wfs_stream.attributes = attrs

    return wfs_stream


def load_from_wfs(
    wfs_stream: WFSGeoData,
    old_attributes: list[DataAttribute] = None,
) -> list[GeoFeature]:
    """Create and return a GeoData object created from a WFS stream.

    Tries to reproject the geometries to EPSG:4326.

    :param wfs_stream:
    :return: geo data version of the `wfs_stream` stream
    """
    df = wfs.get_feature(
        wfs_stream.url, wfs_stream.feature_type, wfs_stream.version
    )
    if df.crs:
        df = df.to_crs(DEFAULT_PROJECTION)
    old_attributes = old_attributes or []
    old_attrs_dict = {attr.name: attr for attr in old_attributes}
    attributes_dict = {}
    features = []
    for aname, atype in df.dtypes.items():
        if aname == df.geometry.name:
            continue
        if atype in (float, int):
            attr = DataAttributeQuantitative(name=aname)
        else:
            attr = DataAttributeNominal(name=aname)
        old_attr = old_attrs_dict.get(aname, attr)
        attributes_dict[aname] = old_attr if attr.same_as(old_attr) else attr

    attr_values = defaultdict(list)
    extent_filter = (
        None
        if wfs_stream.extent_filter is None
        else to_shape(wfs_stream.extent_filter)
    )
    extent_filter_fn = create_extent_filter(extent_filter)
    for s_feature, geom in zip(df.iterfeatures(), df.geometry.values):
        if extent_filter_fn(geom):
            # Ignore geometry outside extent (if set)
            continue
        geom_geometry = from_shape(geom, srid=DEFAULT_SRID)
        feature = GeoFeature(geom=geom_geometry)
        features.append(feature)
        for prop, val in s_feature["properties"].items():
            cls = attributes_dict[prop].get_value_class()
            attr_values[attributes_dict[prop]].append(
                cls(
                    value=val,
                    attribute=attributes_dict[prop],
                    feature=feature,
                )
            )

    return features


def load_vector_from_files(files, extent_filter: BaseGeometry = None):
    """
    Create a new GeoData from a list of files.

    Saves the files in a temporary directory and load them as a new GeoData
    object.
    """
    with get_temporary_directory() as temp_dir:
        temp_files = []
        for f in files:
            # This file datastructure can be read only once
            # Without it the is_zipfile test seem to empty it for later cases
            # so other file type are not read properly
            path = os.path.join(temp_dir, secure_filename(f.filename))
            f.save(path)
            temp_files.append(path)
        if len(temp_files) == 1 and is_zipfile(temp_files[0]):
            # Pre-treatment on zipped shapefile
            file = temp_files.pop(0)
            with ZipFile(file) as zip_file:
                zip_infos = []
                for zi in zip_file.infolist():
                    basename = os.path.basename(zi.filename)
                    if basename != "":
                        zi.filename = secure_filename(basename)
                        zip_infos.append(zi)
                for zi in zip_infos:
                    temp_files.append(zip_file.extract(zi, path=temp_dir))
        if len(temp_files) > 1:
            # Shapefile
            validate_shp_filenames(temp_files)
            shape_file = None
            for f_name in temp_files:
                f_root, f_ext = os.path.splitext(f_name)
                if f_ext == ".shp":
                    # Stop at the first .shp file
                    shape_file = f_name
                    break
            if shape_file is None:
                raise UploadError("No file .shp found.")
            file_in = shape_file
        else:
            # Any other format
            file_in = temp_files[0]

        out_filename = ogr2ogr_reproject(file_in, temp_dir)
        fname = out_filename if out_filename is not None else file_in
        try:
            return load_vector_file(
                os.path.join(temp_dir, fname), extent_filter
            )
        except fiona.errors.DriverError as exc:
            message = str(exc).replace(
                os.path.join(temp_dir, fname), Path(file_in).suffix
            )
            raise UploadError(message)


def reclassify(array, classes=None, start=None, step=None, stop=None):
    """Reclassify the raster values."""
    if classes is None:
        _flattened = array[~np.isnan(array)].data.flatten()
        start = min(_flattened) if start is None else start
        stop = max(_flattened) if stop is None else stop
        step = step or (stop - start) / 100
        classes = create_value_classes(start, stop, step)

    result = np.ma.masked_invalid(array)
    min_value, max_value = float("inf"), -float("inf")
    min_label, max_label = None, None
    for c in classes:
        v_min, v_max = sorted((c[0], c[1]))
        v_val = c[2]
        if v_min < min_value:
            min_value = v_min
            min_label = v_val
        if v_max > max_value:
            max_value = v_max
            max_label = v_val
        result.data[
            np.where((array >= v_min) & (array < v_max) & ~result.mask)
        ] = v_val
    result.data[np.where((array < min_value) & ~result.mask)] = min_label
    result.data[np.where((array >= max_value) & ~result.mask)] = max_label
    return result


def load_from_geotiff(
    path,
    classes,
    start: float = None,
    step: float = None,
    stop: float = None,
    smooth=False,
    extent_filter: BaseGeometry = None,
):
    """Create a new geo-data from a GeoTiff file.

    Args:
        path (str): The path of the GeoTIFF file.
        classes (list):
            The classes of the vector features, a list of (min, max, value).
        start (float):
            The starting value for classes creation
            (if `classes` not provided).
        step (float):
            The step value for classes creation (if `classes` not provided).
        stop (float): The stop value for classes (if `classes` not provided).
        smooth (bool):
            Whether to smooth the raster using a percentile_filter.
            Default: False.
        extent_filter (shapely.BaseGeometry):
            Geometry filtering in features to keep.
            Default: None (no filter).
    """
    with rasterio.open(path) as src:
        image = src.read(1, masked=True)

    name = src.name
    name = os.path.basename(name)
    name = os.path.splitext(name)[0]
    features = _load_features_from_raster(
        image,
        src,
        classes=classes,
        start=start,
        step=step,
        stop=stop,
        smooth=smooth,
        extent_filter=extent_filter,
    )
    # List the data attributes
    attrs = []
    for f in features:
        for p in f.properties:
            if p.attribute not in attrs:
                attrs.append(p.attribute)
    geo_data = GeoData(
        name=name,
        original_name=name,
        source_driver=src.driver,
        features=features,
        attributes=attrs,
    )
    geo_data.create()
    return geo_data


def load_wms(wms_stream: WMSGeoData) -> WMSGeoData:
    """Create and return a StreamGeoData object created from a WFS URL.

    :param wms_stream:
        WMS stream to load (can be partial as long as it contains at least
        the server URL and layer)
    :raise KeyError: if `wms_stream.layer` is not found on WMS server
    :return:

    .. note:: WMS object is not persisted!
    """
    capabilities = wms.get_capabilities(wms_stream.url, wms_stream.version)
    if wms_stream.layer not in capabilities.queryable_layers:
        raise KeyError(
            f"No queryable layer found on server {wms_stream.url} "
            f"with given name '{wms_stream.layer}'"
        )
    layer_info = capabilities.layers[wms_stream.layer]
    # Do we really need original_name field?
    wms_stream.original_name = wms_stream.layer
    wms_stream.name = secure_filename(layer_info.name)
    wms_stream.title = layer_info.title
    wms_stream.description = layer_info.description
    wms_stream.keywords = layer_info.keywords

    # Load features so stream can be viewed directly
    features = load_from_wms(
        wms_stream,
        classes=wms_stream.classes,
        start=wms_stream.start,
        step=wms_stream.step,
        stop=wms_stream.stop,
        resolution=wms_stream.resolution,
    )
    # List the data attributes
    attrs = []
    for f in features:
        for p in f.properties:
            if p.attribute not in attrs:
                attrs.append(p.attribute)
    wms_stream.features = features
    wms_stream.attributes = attrs

    return wms_stream


def load_from_wms(
    wms_stream: WMSGeoData,
    classes: list = None,
    start: float = None,
    step: float = None,
    stop: float = None,
    smooth: bool = False,
    resolution: float = None,
    old_attribute: DataAttribute = None,
) -> list[GeoFeature]:
    """Create a new geo-data from a WMS url.

    :param wms_stream: The WMS stream.
    :param classes:
        The classes of the vector features, a list of (min, max, value).
    :param start:
        The starting value for classes creation (if `classes` not provided).
    :param step:
        The step value for classes creation (if `classes` not provided).
    :param stop: The stop value for classes (if `classes` not provided).
    :param smooth:
        Whether to smooth the raster using a percentile_filter.
        Default: False.
    """
    img, src = wms.get_map(
        wms_stream.url,
        wms_stream.layer,
        wms_stream.version,
        resolution=resolution,
    )
    extent_filter = (
        None
        if wms_stream.extent_filter is None
        else to_shape(wms_stream.extent_filter)
    )
    geodata = _load_features_from_raster(
        img,
        src,
        classes=classes,
        start=start,
        step=step,
        stop=stop,
        smooth=smooth,
        old_attribute=old_attribute,
        extent_filter=extent_filter,
    )
    return geodata


def _load_features_from_raster(
    image,
    src,
    classes: list[list[float]] = None,
    start: float = None,
    step: float = None,
    stop: float = None,
    smooth: bool = False,
    old_attribute: DataAttribute = None,
    extent_filter: BaseGeometry = None,
) -> list[GeoFeature]:
    """Load GeoFeatures from raster image.

    Args:
        image: the loaded raster image (previously read from `src`)
        src: dataset reader
        classes (list):
            The classes of the vector features, a list of (min, max, value).
        start (float):
            The starting value for classes creation
            (if `classes` not provided).
        step (float):
            The step value for classes creation (if `classes` not provided).
        stop (float):
            The stop value for classes (if `classes` not provided).
        smooth (bool):
            Whether to smooth the raster using a percentile_filter.
            Default: False.
        extent_filter (shapely.BaseGeometry):
            Geometry filtering in features to keep.
            Default: None (no filter).
    """
    image = image.astype(np.float32)
    image[np.where(image.mask)] = np.nan
    image = reclassify(image, classes, start=start, step=step, stop=stop)

    if smooth:
        filtered = ndimage.percentile_filter(image, percentile=25, size=7)
        np.copyto(image.data, filtered, where=(~image.mask))

    results = [
        {"value": v, "geometry": s}
        for i, (s, v) in enumerate(
            shapes(
                image,
                mask=(~image.mask & np.isfinite(image.data)),
                transform=src.transform,
            )
        )
    ]

    project = None
    if src.crs != {}:
        proj_out = pyproj.crs.CRS(DEFAULT_PROJECTION)
        proj_in = pyproj.crs.CRS(src.crs)
        if not proj_in.equals(proj_out):
            project = pyproj.Transformer.from_crs(proj_in, proj_out).transform

    if all(
        (
            isinstance(r["value"], int) or isinstance(r["value"], float)
            for r in results
        )
    ):
        attr = DataAttributeQuantitative(name="value")
    else:
        attr = DataAttributeNominal(name="value")
    if old_attribute is not None:
        attr = old_attribute if attr.same_as(old_attribute) else attr

    features = []
    values = []
    val_cls = attr.get_value_class()
    extent_filter_fn = create_extent_filter(extent_filter)
    for result in results:
        geom = shape(result["geometry"])
        if project is not None:
            geom = transform(project, geom)
        if extent_filter_fn(geom):
            # Ignore geometry outside extent (if set)
            continue
        geom_geometry = from_shape(geom, srid=DEFAULT_SRID)
        feature = GeoFeature(geom=geom_geometry)
        values.append(
            val_cls(value=result["value"], attribute=attr, feature=feature)
        )
        features.append(feature)
    return features


def load_raster_from_files(
    files,
    classes: list = None,
    start: float = None,
    step: float = None,
    stop: float = None,
    extent_filter: BaseGeometry = None,
):
    """Create a new vectorized GeoData from a raster file."""
    with get_temporary_directory() as temp_dir:
        if len(files) != 1:
            raise UploadError("A raster data should use only one GeoTiff file")
        file_obj = files[0]
        file_name = secure_filename(file_obj.filename)
        file_path = os.path.join(temp_dir, file_name)
        file_obj.save(file_path)
        geo_data = load_from_geotiff(
            file_path,
            classes=classes,
            start=start,
            step=step,
            stop=stop,
            extent_filter=extent_filter,
        )
        return geo_data
