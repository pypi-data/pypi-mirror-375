from sqlalchemy.orm import joinedload
from sqlalchemy.sql import text

from ..exceptions import PermissionError, RequestError
from ..models import (
    BaseData,
    BaseGeoData,
    GeneratedGeoData,
    GeoData,
    GeoDataType,
    GlobalData,
    StreamGeoData,
    db,
)
from ..models.geo_data import UploadableData
from .permission_service import has_permission


class DataService:
    __model__ = BaseData

    def has_permission(self, data, user=None):
        """
        Return if the current user is authorized to access the data.

        Args:
            data: A data object.

        Returns: authorization as bool
        """
        if isinstance(data, UploadableData):
            return has_permission(data, user)
        elif isinstance(data, GeneratedGeoData) and data.project_data:
            return has_permission(data.project_data.project, user)
        return False

    def check_permission(self, data):
        """
        Check if the current user is authorized to access the data.

        Args:
            data: A data object.

        Raises:
            PermissionError is the user is not authorized to use the data.
        """
        if not self.has_permission(data):
            raise PermissionError

    def get_if_authorized(self, data_id):
        """
        Return the global data if the user is authorized to access it.

        Args:
            data_id (int): The id of the data to return.

        Raises:
            RequestError (code 404) if the data does not exist.

        Returns:
            The data.
        """
        data = BaseData.get_by_id(data_id)
        if data is None:
            raise RequestError("The data does not exist", 404)
        self.check_permission(data)
        return data

    def get_all_authorized_data(self, user, types: set[str]):
        """
        Return the list of all the data.

        Args:
            user: User for which to get the data.

        Returns:
            A list of `Data` objects.
        """
        data_list = (
            BaseData.query.where(BaseData.type.in_(types))
            .order_by(BaseData.id)
            .all()
        )
        return list(filter(lambda d: self.has_permission(d, user), data_list))


class GlobalDataService:
    __model__ = GlobalData

    def check_permission(self, data):
        """
        Check if the current user is authorized to access the global data.

        Args:
            data: A global data object.

        Raises:
            PermissionError is the user is not authorized to use the global
            data.
        """
        if isinstance(data, UploadableData):
            if not has_permission(data):
                raise PermissionError

    def get_if_authorized(self, data_id):
        """
        Return the global data if the user is authorized to access it.

        Args:
            data_id (int): The id of the global data to return.

        Raises:
            RequestError (code 404) if the global data does not exist.

        Returns:
            The data.
        """
        data = GlobalData.get_by_id(data_id)
        if data is None:
            raise RequestError("The global data does not exist", 404)
        self.check_permission(data)
        return data

    def get_all_authorized_data(self, user):
        """
        Return the list of all the global data.

        Args:
            user: User for which to get the global data.

        Returns:
            A list of `GlobalData` objects.
        """
        data_list = (
            GlobalData.query.options(joinedload(GlobalData.permissions))
            .order_by(GlobalData.id)
            .all()
        )
        return list(filter(lambda g: has_permission(g, user), data_list))


class StreamGeoDataService:
    __model__ = StreamGeoData

    def check_permission(self, data):
        """
        Check if the current user is authorized to access the data.

        Args:
            data: A geo-data stream object.

        Raises:
            PermissionError is the user is not authorized to use the data.
        """
        if isinstance(data, StreamGeoData):
            if not has_permission(data):
                raise PermissionError

    def get_if_authorized(self, stream_geo_data_id):
        """
        Return the geo data stream if the user is authorized to access it.

        Args:
            stream_geo_data_id (int): The id of the geo data stream to return.

        Raises:
            RequestError (code 404) if the stream does not exist.

        Returns:
            The geo data stream.
        """
        data = BaseData.get_by_id(stream_geo_data_id)
        if not isinstance(data, StreamGeoData):
            raise RequestError("The geo data stream does not exist", 404)
        self.check_permission(data)
        return data

    def get_all_authorized_geo_data(self, user):
        """
        Return the list of all the geo data streams.

        Args:
            user: User for which to get the geo data streams.

        Returns:
            A list of `StreamGeoData` objects.
        """
        data_list = (
            BaseData.query.options(joinedload(BaseData.permissions))
            .where(BaseData.type.in_([GeoDataType.wfs, GeoDataType.wms]))
            .order_by(BaseData.id)
            .all()
        )
        return list(filter(lambda g: has_permission(g, user), data_list))


class GeoDataService:
    __model__ = BaseGeoData

    def check_permission(self, data):
        """
        Check if the current user is authorized to access the data.

        Args:
            data: A geo-data object.

        Raises:
            PermissionError is the user is not authorized to use the data.
        """
        if isinstance(data, UploadableData):
            if not has_permission(data):
                raise PermissionError
        elif isinstance(data, GeneratedGeoData):
            if not has_permission(data.project_data.project):
                raise PermissionError

    def get_if_authorized(self, geo_data_id):
        """
        Return the geo data if the user is authorized to access it.

        Args:
            geo_data_id (int): The id of the geo data to return.

        Raises:
            RequestError (code 404) if the data does not exist.

        Returns:
            The geo data.
        """
        data = BaseGeoData.get_by_id(geo_data_id)
        if data is None:
            raise RequestError("The geo data does not exist", 404)
        self.check_permission(data)
        return data

    def get_all_authorized_geo_data(self, user):
        """
        Return the list of all the geo data (not the generated geo data).

        Args:
            user: User for which to get the geo data.

        Returns:
            A list of `GeoData` objects.
        """
        data_list = (
            GeoData.query.options(
                joinedload(GeoData.attributes), joinedload(GeoData.permissions)
            )
            .order_by(GeoData.id)
            .all()
        )
        return list(filter(lambda g: has_permission(g, user), data_list))

    def get_vector_tile(self, geo_data_id, z, x, y, property_name=None):
        """
        Return the geo data features as a Mapbox Vector Tile.

        The geometries are simplified to the zoom level (z coordinate) and
        projected as web mercator. If a `property_name` is specified.
        Geometry near the poles are clipped as they cannot be transformed to
        Web Mercator Projection (EPSG:3857).
        The clipping is done above 85° North and below -85° South.

        Args:
            geo_data_id (int): The id of the geo data to return.
            z (int): Z coordinate of the tile (zoom level).
            x (int): X coordinate of the tile.
            y (int): Y coordinate of the tile.
            property_name (str): The name of a property to return as an
                attribute in the geometries. Default: None.

        Returns:
            A string representing a Mapbox Vector Tile.
        """
        # Calculate the resolution for the zoom level
        # https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Resolution_and_Scale  # noqa: E501
        tolerance = 156543.03 / (2**z)
        # exclude geometry too near the poles:
        # ST_Intersection(geom, ST_MakeEnvelope(-180, -85, 180, 85, 4326))
        # https://gis.stackexchange.com/questions/357847/postgis-vector-tiles-zoom-affects-tile-production  # noqa: E501
        # https://en.wikipedia.org/wiki/Web_Mercator_projection
        if property_name is not None:
            q = (
                "SELECT ST_AsMVT(q) FROM ("
                "SELECT f.id as id, v.value->>0 as value, "
                "ST_AsMVTGeom(ST_SimplifyVW(ST_Transform("
                "ST_Intersection(f.geom, ST_MakeEnvelope("
                "-180, -85, 180, 85, 4326)), 3857), :tolerance), "
                "TileBBox(:z, :x, :y)) AS geom "
                "FROM geo_feature f "
                "INNER JOIN feature bf ON f.id = bf.id "
                "LEFT JOIN data_attribute a ON bf.data_id = a.data_id "
                "LEFT JOIN data_value v ON a.id = v.attribute_id "
                "AND f.id = v.feature_id "
                "WHERE bf.data_id = :geo_data_id AND f.geom && "
                "TileBBox(:z, :x, :y, 4326) "
                "AND a.name = :prop) q"
            )
            keys = {
                "tolerance": tolerance,
                "z": z,
                "x": x,
                "y": y,
                "geo_data_id": geo_data_id,
                "prop": property_name,
            }
        else:
            q = (
                "SELECT ST_AsMVT(q) FROM ("
                "SELECT f.id, ST_AsMVTGeom(ST_SimplifyVW("
                "ST_Transform(ST_Intersection(f.geom, ST_MakeEnvelope("
                "-180, -85, 180, 85, 4326)), 3857), :tolerance), "
                "TileBBox(:z, :x, :y)) AS geom "
                "FROM geo_feature f "
                "INNER JOIN feature bf ON f.id = bf.id "
                "WHERE bf.data_id = :geo_data_id AND f.geom && "
                "TileBBox(:z, :x, :y, 4326)) q"
            )
            keys = {
                "tolerance": tolerance,
                "z": z,
                "x": x,
                "y": y,
                "geo_data_id": geo_data_id,
            }
        result = db.session.execute(text(q), keys)
        mvt = result.first()[0]
        return mvt
