import io

import simplejson as json
from flask import jsonify, request, send_file
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from ..exceptions import (
    CapabilitiesXMLParsingError,
    ExternalRequestError,
    RequestError,
    UploadError,
)
from ..models import (
    BaseData,
    DataAttribute,
    Feature,
    GeoData,
    GeoDataType,
    GlobalData,
    PermissionAbility,
    StreamGeoData,
    db,
)
from ..schemas import (
    BaseDataFeaturesSchema,
    DataAttributeGetResponse,
    DataAttributeSchema,
    DataAttributeSchemaWithValues,
    DataAttributeWithValuesGetResponse,
    DataSchema,
    DataTypeSetSchema,
    FeatureResponseSchema,
    FeatureSchema,
    GeoDataAccessResponseSchema,
    GeoDataAccessSchema,
    GeoDataGetResponse,
    GeoDataListResponseSchema,
    GeoDataSchema,
    GeoOnlyDataSchema,
    GlobalDataAccessResponseSchema,
    GlobalDataAccessSchema,
    GlobalDataCreationSchema,
    GlobalDataSchema,
    MessageSchema,
    StreamGeoDataAccessResponseSchema,
    StreamGeoDataAccessSchema,
    StreamGeoDataListResponseSchema,
    StreamGeoDataResponseSchema,
    StreamGeoDataSchema,
    WFSGeoDataCreationSchema,
    WMSGeoDataCreationSchema,
)
from ..services import (
    data_service,
    geo_data_service,
    geo_data_stream_service,
    get_global_data_service,
)
from ..services.auth_service import check_jwt_authentication, token_required
from ..services.geo_data_loading_service import (
    create_global_data,
    get_geo_data_download,
    get_temporary_directory,
    load_from_wfs,
    load_from_wms,
    load_raster_from_files,
    load_vector_from_files,
    load_wfs,
    load_wms,
    post_load_normalization,
)
from ..services.permission_service import has_ability
from .utils import (
    dump_data,
    get_json_content,
    with_query_arg,
    with_request_body,
    with_response,
)


class DataListAPI(Resource):
    def parse_types(self, args) -> set[str]:
        res = set()
        types = args.get("type", None)
        all_types_names = {_t.name for _t in GeoDataType}
        if types is None or types == [""]:
            return all_types_names
        for _type in types:
            if _type in all_types_names:
                res.add(GeoDataType[_type].name)
        return res

    @token_required
    @with_query_arg(
        "type",
        schema=DataTypeSetSchema,
        required=False,
        description="The types of data to return",
    )
    @with_response(
        status=200,
        schema=DataSchema(many=True),
        description="List of all data the user has access to",
    )
    def get(self):
        """
        Get the list of all the data for the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: No user logged in.

        .. :quickref: Data; Get the list of accessible data
        """
        parser = reqparse.RequestParser()
        parser.add_argument("type", type=str, location="args", action="append")
        args = parser.parse_args()
        types = self.parse_types(args)
        user = check_jwt_authentication(request)
        if user is None:
            raise PermissionError("No user logged in")
        data_list = data_service.get_all_authorized_data(user, types)
        return jsonify(DataSchema(many=True).dump(data_list))


class DataAPI(Resource):
    @token_required
    @with_response(status=200, schema=DataSchema, description="Data details")
    def get(self, data_id):
        """
        Get a data from its id.

        :param int data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this data.
        :status 404: The data doesn't exist.

        .. :quickref: Data; Get the data details
        """
        data = data_service.get_if_authorized(data_id)
        return jsonify(DataSchema().dump(data))


class GlobalDataListAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=GlobalDataSchema(many=True),
        description="List of all global data the user has access to",
    )
    def get(self):
        """
        Get the list of all the global data for the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: No user logged in.

        .. :quickref: Globaldata; Get the list of accessible global data
        """
        user = check_jwt_authentication(request)
        if user is None:
            raise PermissionError("No user logged in")
        data_list = get_global_data_service.get_all_authorized_data(user)
        return jsonify(GlobalDataSchema(many=True).dump(data_list))

    @token_required
    @with_request_body(
        schema=GlobalDataCreationSchema, description="Global data details"
    )
    @with_response(
        status=200,
        schema=GlobalDataSchema,
        description="Created global data details",
    )
    @has_ability(PermissionAbility.create_geo_data)
    def post(self):
        """
        Create an existing global data.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to create global data.

        .. :quickref: Globaldata; Create a global data
        """
        user = check_jwt_authentication(request)
        content = get_json_content()
        schema = GlobalDataSchema()
        data_json = GlobalDataCreationSchema().load(content)
        data = create_global_data(**data_json)
        data.upload_user = user
        data.update()
        return jsonify(schema.dump(data))


class GlobalDataAPI(Resource):
    @token_required
    @with_response(
        status=200, schema=GlobalDataSchema, description="Global data details"
    )
    def get(self, data_id):
        """
        Get a global data from its id.

        :param int data_id: The id of the global data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this global data.
        :status 404: The global data doesn't exist.

        .. :quickref: Globaldata; Get the global data details
        """
        data = get_global_data_service.get_if_authorized(data_id)
        return jsonify(GlobalDataSchema().dump(data))

    @token_required
    @with_response(
        status=200,
        schema=MessageSchema,
        description="Global data successfully deleted",
    )
    def delete(self, data_id):
        """
        Delete a global data.

        :param int data_id: The id of the global -data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400:
            The global data is used as input in other data and cannot be
            deleted.
        :status 403: The user is not allowed to delete the global data.
        :status 404: The global data doesn't exist.

        .. :quickref: Globaldata; Delete a global data
        """
        data = get_global_data_service.get_if_authorized(data_id)
        try:
            data.delete()
        except IntegrityError:
            raise RequestError(
                "The global data is referenced by other objects and cannot "
                "be deleted",
                400,
            )
        return jsonify(message="global data {} deleted".format(data_id))

    @token_required
    @with_request_body(
        schema=GlobalDataSchema, description="New global data details"
    )
    @with_response(
        status=200,
        schema=GlobalDataSchema,
        description="Global data updated details",
    )
    def put(self, data_id):
        """
        Update an existing global data.

        :param int data_id: The id of the global data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to modify the global data.
        :status 404: The global data doesn't exist.

        .. :quickref: Globaldata; Update a global data
        """
        content = get_json_content()
        schema = GlobalDataSchema()
        data = get_global_data_service.get_if_authorized(data_id)
        if "properties" in content:
            for prop in data.properties:
                db.session.delete(prop)
        data = schema.load(content, instance=data)
        if "properties" in content:
            properties = {prop.attribute: prop for prop in data.properties}
            for attr in data.attributes:
                prop = properties.get(attr)
                if prop:
                    db.session.add(attr)
                    db.session.add(prop)
                else:
                    db.session.delete(attr)
        data.update()
        return jsonify(schema.dump(data))


class GlobalDataAccessAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=GlobalDataAccessResponseSchema,
        description="Global data permissions",
    )
    def get(self, data_id):
        """
        Return the list of permissions for the global data.

        The user must be the owner of the global data.

        :param int data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the data.
        :status 404: The global data doesn't exist.

        .. :quickref: Globaldata; Get the global data permissions
        """
        data = GlobalData.get_by_id(data_id)
        if data is None:
            raise RequestError("The global data does not exist", 404)
        user = check_jwt_authentication(request)
        if data.upload_user is None or data.upload_user is not user:
            raise PermissionError(
                "The user is not the owner of the global data"
            )
        schema = GlobalDataAccessSchema()
        return dump_data(schema, access=data)

    @token_required
    @with_request_body(
        schema=GlobalDataAccessSchema,
        description="New global data permissions",
    )
    @with_response(
        status=200,
        schema=GlobalDataAccessResponseSchema,
        description="Global data updated permissions",
    )
    def put(self, data_id):
        """
        Update the list of permissions for the global data.

        The user must be the owner of the global data.

        :param int data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the data.
        :status 404: The global data doesn't exist.

        .. :quickref: Globaldata; Modify the global data permissions
        """
        data = GlobalData.get_by_id(data_id)
        if data is None:
            raise RequestError("The global data does not exist", 404)
        user = check_jwt_authentication(request)
        if data.upload_user is None or data.upload_user is not user:
            raise PermissionError(
                "The user is not the owner of the global data"
            )
        schema = GlobalDataAccessSchema()
        content = get_json_content()
        data = schema.load(content, instance=data)
        if not any([p.user is data.upload_user for p in data.permissions]):
            data.permissions.append(
                GlobalData.Permission(user=data.upload_user)
            )
        data.update()
        return dump_data(schema, access=data)


class GeoDataAPI(Resource):
    @token_required
    @with_response(
        status=200, schema=GeoDataGetResponse, description="Geodata details"
    )
    def get(self, geo_data_id):
        """
        Get a geo-data from its id.

        :param int geo_data_id: The id of the geo-data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this geo-data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Get the geodata details
        """
        geo_data = geo_data_service.get_if_authorized(geo_data_id)
        return dump_data(GeoOnlyDataSchema(), geodata=geo_data)

    @token_required
    @with_response(
        status=200,
        schema=MessageSchema,
        description="Geodata successfully deleted",
    )
    def delete(self, geo_data_id):
        """
        Delete a geodata and its features.

        :param int geo_data_id: The id of the geo-data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400:
            The geo-data is used as input in other data and cannot be deleted.
        :status 403: The user is not allowed to delete the geo-data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Delete a geodata
        """
        geo_data = geo_data_service.get_if_authorized(geo_data_id)
        try:
            geo_data.delete()
        except IntegrityError:
            raise RequestError(
                "The geo data is referenced by other objects and cannot "
                "be deleted",
                400,
            )
        return jsonify(message="geo-data {} deleted".format(geo_data_id))

    @token_required
    @with_request_body(schema=GeoDataSchema, description="New geodata details")
    @with_response(
        status=200,
        schema=GeoDataGetResponse,
        description="Geodata updated details",
    )
    def put(self, geo_data_id):
        """
        Update an existing geo-data.

        :param int geo_data_id: The id of the geo-data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to modify the geo-data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Update a geodata
        """
        content = get_json_content()
        schema = GeoDataSchema()
        geo_data = geo_data_service.get_if_authorized(geo_data_id)
        data = schema.load(content, instance=geo_data)
        data.update()
        return dump_data(schema, geodata=data)


class StreamGeoDataAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=StreamGeoDataResponseSchema,
        description="Geodata stream details",
    )
    def get(self, stream_geo_data_id):
        """
        Get a geo-data stream from its id.

        :param int stream_geo_data_id: The id of the geo-data stream.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this geo-data stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Get the geodata stream details
        """
        stream = geo_data_stream_service.get_if_authorized(stream_geo_data_id)
        return dump_data(StreamGeoDataSchema(), stream=stream)

    @token_required
    @with_response(
        status=200,
        schema=MessageSchema,
        description="Geodata stream successfully deleted",
    )
    def delete(self, stream_geo_data_id):
        """
        Delete a geodata stream.

        :param int stream_geo_data_id: The id of the geo-data stream.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to delete the geo-data stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Delete a geodata stream
        """
        stream = geo_data_stream_service.get_if_authorized(stream_geo_data_id)
        try:
            stream.delete()
        except IntegrityError:
            # This should not happen as stream is detached gracefully
            # beforehand
            raise RequestError(
                "The geo data stream is referenced by other objects and cannot"
                " be deleted",
                500,
            )
        return jsonify(
            message="geo-data stream {} deleted".format(stream_geo_data_id)
        )

    @token_required
    @with_request_body(
        schema=StreamGeoDataSchema, description="New geodata stream details"
    )
    @with_response(
        status=200,
        schema=StreamGeoDataResponseSchema,
        description="Geodata stream updated details",
    )
    def put(self, stream_geo_data_id):
        """
        Update an existing geo-data stream.

        :param int stream_geo_data_id: The id of the geo-data stream.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to modify the geo-data stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Update a geodata stream
        """
        content = get_json_content()
        stream = geo_data_stream_service.get_if_authorized(stream_geo_data_id)
        schema = StreamGeoDataSchema.type_schemas[stream.type.name]()
        stream = schema.load(content, instance=stream)
        stream.update()
        return dump_data(schema, stream=stream)


class StreamGeoDataUpdateAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=StreamGeoDataResponseSchema,
        description="Geodata stream updated details",
    )
    def post(self, stream_geo_data_id):
        """
        Update features preview of an existing geo-data stream.

        :param int stream_geo_data_id: The id of the geo-data stream.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: The stream could not be retrieved with given parameters.
        :status 403: The user is not allowed to modify the geo-data stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Update features preview of a geodata stream
        """  # noqa: E501
        stream = geo_data_stream_service.get_if_authorized(stream_geo_data_id)
        schema = StreamGeoDataSchema.type_schemas[stream.type.name]()
        try:
            if stream.type == GeoDataType.wfs:
                features = load_from_wfs(stream, stream.attributes)
            else:
                attribute = None
                if len(stream.attributes) == 1:
                    attribute = stream.attributes[0]
                features = load_from_wms(
                    stream,
                    old_attribute=attribute,
                )
        except (
            CapabilitiesXMLParsingError,
            ExternalRequestError,
            KeyError,
        ) as exc:
            raise RequestError(str(exc), 400)
        # List the data attributes
        attrs = []
        for f in features:
            for p in f.properties:
                if p.attribute not in attrs:
                    attrs.append(p.attribute)
        stream.features = features
        stream.extent = None
        stream.attributes = attrs
        stream.update()
        post_load_normalization(stream)
        return dump_data(schema, stream=stream)


class DataAttributeAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=[DataAttributeGetResponse, DataAttributeWithValuesGetResponse],
        description="Details of an attribute",
    )
    @with_query_arg(
        "values",
        bool,
        required=False,
        description="Return the values of the attribute. Default: false",
    )
    def get(self, attribute_id):
        """
        Get the details of an attribute of a geo-data.

        The details contain the name of the attribute,
        its type and some statistics about its values.

        :param int attribute_id: The id of the data attribute.
        :query bool values: Return the values of the attribute. Default: False.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the geo-data attribute.
        :status 404: The geo-data attribute doesn't exist.

        .. :quickref: Geodata; Get the details of an attribute
        """
        # TODO: Should verify the user has permission to view the data
        parser = reqparse.RequestParser()
        parser.add_argument("values", type=bool, location="args")
        args = parser.parse_args()
        attribute = DataAttribute.get_by_id(attribute_id)
        geo_data_service.check_permission(attribute.data)
        if args.get("values", False):
            schema = DataAttributeSchemaWithValues()
        else:
            schema = DataAttributeSchema()
        return dump_data(schema, attribute=attribute)


class DataDownloadAPI(Resource):
    @token_required
    @with_query_arg(
        "outputFormat",
        str,
        required=False,
        description=(
            "Desired output format (leave blank for zip shapefile/json)"
        ),
    )
    @with_response(
        status=200,
        description="Data in specified file format",
        content={
            "application/octet-stream": {"type": "string", "format": "binary"}
        },
    )
    def get(self, data_id):
        """
        Return the data in desired format.

        :param int data_id: The id of the data to download.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the data.
        :status 404: The data doesn't exist.
        :status 415: Output format is not supported.
        :status 500:
            There was an error with the geometry while creating the file.

        .. :quickref: Data; Download a data as a file
        """
        parser = reqparse.RequestParser()
        parser.add_argument("outputFormat", type=str, location="args")
        args = parser.parse_args()
        geo_data = data_service.get_if_authorized(data_id)
        with get_temporary_directory() as temp_dir:
            filename, file_object = get_geo_data_download(
                geo_data, temp_dir, args.get("outputFormat")
            )
            return send_file(
                file_object, as_attachment=True, download_name=filename
            )


class GeoDataUploadAPI(Resource):
    @token_required
    @with_request_body(
        description="Geodata as zipped/filelist shapefile or other format",
        content={
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                        }
                    },
                }
            }
        },
    )
    @with_response(
        status=200,
        schema=GeoDataGetResponse,
        description="Uploaded geodata details",
    )
    @has_ability(PermissionAbility.create_geo_data)
    def post(self):
        """
        Create a new geo-data from the uploaded files.

        The uploaded file can either be a .zip file containing all the required
        shapefile files, the list of shapefile files or a single file
        containing vector geodata.

        :form file: The list of files.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to create geo-data.
        :status 415: There is an error in the uploaded file.

        .. :quickref: Geodata; Upload a vector geodata
        """
        if "file" in request.files:
            user = check_jwt_authentication(request)
            files_list = request.files.getlist("file")
            try:
                geo_data = load_vector_from_files(files_list)
            except UploadError as err:
                raise RequestError(str(err), 415)
            post_load_normalization(geo_data)
            geo_data.upload_user = user
            geo_data.update()
            return dump_data(GeoDataSchema(), geodata=geo_data)


class WFSGeoDataUploadAPI(Resource):
    @token_required
    @with_request_body(
        schema=WFSGeoDataCreationSchema,
        description="Parameters necessary to find the WFS stream online",
    )
    @with_response(
        status=200,
        schema=StreamGeoDataResponseSchema,
        description="Uploaded WFS geodata stream details",
    )
    @has_ability(PermissionAbility.create_geo_data)
    def post(self):
        """
        Create a new geo-data stream.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: The stream could not be retrieved with given parameters.
        :status 403: The user is not allowed to create geo-data stream.

        .. :quickref: StreamGeoData; Upload a WFS geo data stream
        """
        user = check_jwt_authentication(request)
        content = get_json_content()
        stream = WFSGeoDataCreationSchema().load(content)
        try:
            stream = load_wfs(stream)
        except (
            CapabilitiesXMLParsingError,
            ExternalRequestError,
            KeyError,
        ) as exc:
            raise RequestError(str(exc), 400)
        stream.upload_user = user
        stream.create()
        post_load_normalization(stream)
        return dump_data(StreamGeoDataSchema(), stream=stream)


class WMSGeoDataUploadAPI(Resource):
    @token_required
    @with_request_body(
        schema=WMSGeoDataCreationSchema,
        description="Parameters necessary to find the WMS stream online",
    )
    @with_response(
        status=200,
        schema=StreamGeoDataResponseSchema,
        description="Uploaded WMS geodata stream details",
    )
    @has_ability(PermissionAbility.create_geo_data)
    def post(self):
        """
        Create a new geo-data stream.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: The stream could not be retrieved with given parameters.
        :status 403: The user is not allowed to create geo-data stream.

        .. :quickref: StreamGeoData; Upload a WMS geo data stream
        """
        user = check_jwt_authentication(request)
        content = get_json_content()
        stream = WMSGeoDataCreationSchema().load(content)
        try:
            stream = load_wms(stream)
        except (
            CapabilitiesXMLParsingError,
            ExternalRequestError,
            KeyError,
        ) as exc:
            raise RequestError(str(exc), 400)
        stream.upload_user = user
        stream.create()
        post_load_normalization(stream)
        return dump_data(StreamGeoDataSchema(), stream=stream)


class GeoDataUploadRasterAPI(Resource):
    @token_required
    @with_request_body(
        description="Geodata as a raster image",
        content={
            "multipart/form-data": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "file": {
                            "type": "array",
                            "items": {"type": "string", "format": "binary"},
                        },
                        "classes": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "number"},
                            },
                        },
                        "start": {"type": "number"},
                        "step": {"type": "number"},
                        "stop": {"type": "number"},
                    },
                }
            }
        },
    )
    @with_response(
        status=200,
        schema=GeoDataGetResponse,
        description="Uploaded geodata details",
    )
    @has_ability(PermissionAbility.create_geo_data)
    def post(self):
        """
        Create a new vectorized geo-data from the uploaded raster file.

        The raster data is reclassified using the classes given,
        to group multiple values together
        and transform the raster file in vector geometries.

        For example, classes of ``[[0, 10, 5], [10, 100, 50]]``
        would assign the value 5 to all the raster cells in [0, 10[,
        the value 50 to all the cells in [10, 100[,
        and 0 or 100 to the cells outside that range.

        :form file: The raster file.
        :form classes:
            The classes to reclassify the raster values
            (list ``[[low, high, value], ...]``).
        :form start:
            The starting value for classes creation
            (if `classes` not provided).
        :form step:
            The step value for classes creation (if `classes` not provided).
        :form stop:
            The stop value for classes creation (if `classes` not provided).
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to create geo-data.
        :status 415: There is an error in the uploaded file.

        .. :quickref: Geodata; Upload a raster geodata
        """
        if "file" in request.files:
            user = check_jwt_authentication(request)
            files_list = request.files.getlist("file")
            _classes_str = request.form.get("classes", "")
            _start_str = request.form.get("start", "")
            _step_str = request.form.get("step", "")
            _stop_str = request.form.get("stop", "")
            classes = (
                None if len(_classes_str) == 0 else json.loads(_classes_str)
            )  # parse the classes as json
            start = (
                None if len(_start_str) == 0 else json.loads(_start_str)
            )  # parse the start as json
            step = (
                None if len(_step_str) == 0 else json.loads(_step_str)
            )  # parse the step as json
            stop = (
                None if len(_stop_str) == 0 else json.loads(_stop_str)
            )  # parse the stop as json
            try:
                geo_data = load_raster_from_files(
                    files_list,
                    classes=classes,
                    start=start,
                    step=step,
                    stop=stop,
                )
            except UploadError as err:
                raise RequestError(str(err), 415)
            post_load_normalization(geo_data)
            geo_data.upload_user = user
            geo_data.update()
        return dump_data(GeoDataSchema(), geodata=geo_data)


class GeoDataAccessAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=GeoDataAccessResponseSchema,
        description="Geodata permissions",
    )
    def get(self, geo_data_id):
        """
        Return the list of permissions for the geo-data.

        The user must be the owner of the geodata.

        :param int geo_data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Get the geodata permissions
        """
        geo_data = GeoData.get_by_id(geo_data_id)
        if geo_data is None:
            raise RequestError("The geo data does not exist", 404)
        user = check_jwt_authentication(request)
        if geo_data.upload_user is None or geo_data.upload_user is not user:
            raise PermissionError("The user is not the owner of the geo-data")
        schema = GeoDataAccessSchema()
        return dump_data(schema, access=geo_data)

    @token_required
    @with_request_body(
        schema=GeoDataAccessSchema, description="New geodata permissions"
    )
    @with_response(
        status=200,
        schema=GeoDataAccessResponseSchema,
        description="Geodata updated permissions",
    )
    def put(self, geo_data_id):
        """
        Update the list of permissions for the geo-data.

        The user must be the owner of the geodata.

        :param int geo_data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Modify the geodata permissions
        """
        geo_data = GeoData.get_by_id(geo_data_id)
        if geo_data is None:
            raise RequestError("The geo data does not exist", 404)
        user = check_jwt_authentication(request)
        if geo_data.upload_user is None or geo_data.upload_user is not user:
            raise PermissionError("The user is not the owner of the geo-data")
        schema = GeoDataAccessSchema()
        content = get_json_content()
        geo_data = schema.load(content, instance=geo_data)
        if not any(
            [p.user is geo_data.upload_user for p in geo_data.permissions]
        ):
            geo_data.permissions.append(
                GeoData.Permission(user=geo_data.upload_user)
            )
        geo_data.update()
        return dump_data(schema, access=geo_data)


class GeoDataListAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=GeoDataListResponseSchema,
        description="List of all geodata the user has access to",
    )
    def get(self):
        """
        Get the list of all the geo-data for the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: No user logged in.

        .. :quickref: Geodata; Get the list of accessible geodata
        """
        user = check_jwt_authentication(request)
        if user is None:
            raise PermissionError("No user logged in")
        geo_data_list = geo_data_service.get_all_authorized_geo_data(user)
        return dump_data(GeoDataSchema(many=True), geodata=geo_data_list)


class StreamGeoDataAccessAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=StreamGeoDataAccessResponseSchema,
        description="Geodata stream permissions",
    )
    def get(self, stream_geo_data_id):
        """
        Return the list of permissions for the geo-data stream.

        The user must be the owner of the geodata stream.

        :param int stream_geo_data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the geodata stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Get the geodata stream permissions
        """
        stream = BaseData.get_by_id(stream_geo_data_id)
        user = check_jwt_authentication(request)
        if not isinstance(stream, StreamGeoData):
            raise RequestError("The geo data stream does not exist", 404)
        if stream.upload_user is not user:
            raise PermissionError(
                "The user is not the owner of the geo-data stream"
            )
        schema = StreamGeoDataAccessSchema()
        return dump_data(schema, access=stream)

    @token_required
    @with_request_body(
        schema=StreamGeoDataAccessSchema,
        description="New geodata stream permissions",
    )
    @with_response(
        status=200,
        schema=StreamGeoDataAccessResponseSchema,
        description="Geodata stream updated permissions",
    )
    def put(self, stream_geo_data_id):
        """
        Update the list of permissions for the geo-data.

        The user must be the owner of the geodata stream.

        :param int stream_geo_data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the owner of the geodata stream.
        :status 404: The geo-data stream doesn't exist.

        .. :quickref: StreamGeoData; Modify the geodata stream permissions
        """
        stream = BaseData.get_by_id(stream_geo_data_id)
        if not isinstance(stream, StreamGeoData):
            raise RequestError("The geo data stream does not exist", 404)
        user = check_jwt_authentication(request)
        if stream.upload_user is None or stream.upload_user is not user:
            raise PermissionError(
                "The user is not the owner of the geo-data stream"
            )
        schema = StreamGeoDataAccessSchema()
        content = get_json_content()
        stream = schema.load(content, instance=stream)
        if not any([p.user is stream.upload_user for p in stream.permissions]):
            stream.permissions.append(
                BaseData.Permission(user=stream.upload_user)
            )
        stream.update()
        return dump_data(schema, access=stream)


class StreamDataListAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=StreamGeoDataListResponseSchema,
        description="List of geodata streams the user has access to",
    )
    def get(self):
        """
        Get the list of all the geo-data stream for the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: No user logged in.

        .. :quickref: StreamGeoData; Get the list of accessible geodata streams
        """
        user = check_jwt_authentication(request)
        if user is None:
            raise PermissionError("No user logged in")
        stream_list = geo_data_stream_service.get_all_authorized_geo_data(user)
        return dump_data(StreamGeoDataSchema(many=True), stream=stream_list)


class FeatureAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=FeatureResponseSchema,
        description="Geodata feature details",
    )
    def get(self, feature_id):
        """
        Return the details of the feature.

        :param int feature_id: The id of the feature.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access the geo-data with this feature.
        :status 404: The geo-data feature doesn't exist.

        .. :quickref: Feature; Get the feature details
        """
        feature = Feature.get_by_id(feature_id)
        if feature is None:
            raise RequestError("The geo data feature does not exist", 404)
        geo_data_service.check_permission(feature.data)
        return dump_data(FeatureSchema(), feature=feature)


class FeatureInputsAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=BaseDataFeaturesSchema,
        description="Data feature inputs",
    )
    def get(self, feature_id, data_id):
        """
        Return the inputs of the feature in specified data.

        :param int feature_id: The id of the feature.
        :param int data_id: The id of the input data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access the geo-data with this feature.
        :status 404: The geo-data feature or data doesn't exist.

        .. :quickref: Feature; Get the feature inputs from data.
        """
        feature = Feature.get_by_id(feature_id)
        if feature is None:
            raise RequestError("The geo data feature does not exist", 404)
        data = BaseData.get_by_id(data_id)
        if data is None:
            raise RequestError("The input data does not exist", 404)
        geo_data_service.check_permission(feature.data)
        features = feature.get_input_features(data_id)
        return jsonify({"features": [f.id for f in features]})


class FeatureOutputsAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=BaseDataFeaturesSchema,
        description="Data feature outputs",
    )
    def get(self, feature_id, data_id):
        """
        Return the outputs of the feature in specified data.

        :param int feature_id: The id of the feature.
        :param int data_id: The id of the output data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access the geo-data with this feature.
        :status 404: The geo-data feature or data doesn't exist.

        .. :quickref: Feature; Get the feature outputs from data.
        """
        feature = Feature.get_by_id(feature_id)
        if feature is None:
            raise RequestError("The geo data feature does not exist", 404)
        data = BaseData.get_by_id(data_id)
        if data is None:
            raise RequestError("The output data does not exist", 404)
        geo_data_service.check_permission(feature.data)
        features = feature.get_output_features(data_id)
        return jsonify({"features": [f.id for f in features]})


class GeoDataVectorTileAPI(Resource):
    @token_required
    @with_response(
        status=200,
        description="Requested tile (might be empty)",
        content={
            "application/vnd.mapbox-vector-tile": {
                "type": "string",
                "format": "binary",
            }
        },
    )
    @with_query_arg(
        "property",
        str,
        required=False,
        description=(
            "The name of the property to return as the 'value' attribute. "
            "Default: None"
        ),
    )
    def get(self, geo_data_id, z, x, y):
        """
        Return a Mapbox Vector Tile of the geo-data.

        :param int geo_data_id: The id of the geo-data.
        :param int z: The tile zoom level.
        :param int x: The tile x index.
        :param int y: The tile y index.
        :query str property:
            The name of the property to return as the ``value`` attribute.
            None by default.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this geo-data.
        :status 404: The geo-data doesn't exist.

        .. :quickref: Geodata; Get a vector tile
        """
        geo_data_service.get_if_authorized(geo_data_id)
        parser = reqparse.RequestParser()
        parser.add_argument("property", type=str, location="args")
        args = parser.parse_args()
        property_arg = args.get("property", None)
        mvt = geo_data_service.get_vector_tile(
            geo_data_id, z, x, y, property_name=property_arg
        )
        return send_file(
            io.BytesIO(mvt), mimetype="application/vnd.mapbox-vector-tile"
        )
