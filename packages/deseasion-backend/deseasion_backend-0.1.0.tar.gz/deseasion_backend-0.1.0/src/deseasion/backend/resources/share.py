from flask import jsonify, request, send_file
from flask_restful import Resource, reqparse

from ..exceptions import RequestError
from ..models import DataShare
from ..schemas import (
    DataShareSchema,
    MessageSchema,
    ProjectSharesGetResponseSchema,
    ShareBaseDataPostResponseSchema,
)
from ..services import data_service, project_service
from ..services.auth_service import check_jwt_authentication, token_required
from ..services.geo_data_loading_service import (
    get_geo_data_download,
    get_temporary_directory,
)
from .utils import (
    dump_data,
    get_json_content,
    with_query_arg,
    with_request_body,
    with_response,
)


class ShareDataListAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectSharesGetResponseSchema,
        description="List all data shares",
    )
    def get(self):
        """
        Get the list of data shares.

        :status 403: The user is not logged in.

        .. :quickref: Shares; Get list of data shares
        """
        user = check_jwt_authentication(request)
        if user is None:
            raise PermissionError("No user logged in")
        shares = DataShare.query.all()
        shared = list(
            filter(
                lambda s: not s.is_expired()
                and data_service.has_permission(s.data, user),
                shares,
            )
        )
        schema = DataShareSchema(many=True)
        return dump_data(schema, shared=shared)


class ProjectSharesAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectSharesGetResponseSchema,
        description="List of data shares of the project",
    )
    def get(self, project_id):
        """
        Get the list of data shares of a project.

        :param int project_id: The id of the project.
        :status 403: The user is not allowed to access the project.
        :status 404: The project does not exist.

        .. :quickref: Project; Get list of data shares
        """
        shared = project_service.get_authorized_shares(project_id)
        schema = DataShareSchema(many=True)
        return dump_data(schema, shared=shared)


class ShareBaseDataAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ShareBaseDataPostResponseSchema,
        description="New data share details",
    )
    @with_request_body(
        schema=DataShareSchema, description="New data share details to create"
    )
    def post(self, data_id):
        """
        Create a new data share.

        :param int data_id: The id of the data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project data.
        :status 404: The project data does not exist.

        .. :quickref: Data; Share data
        """
        data = data_service.get_if_authorized(data_id)
        content = get_json_content()
        schema = DataShareSchema()
        share = schema.load(content)
        share.data = data
        share.create()
        return dump_data(schema, share=share)

    @token_required
    @with_response(
        200,
        schema=ProjectSharesGetResponseSchema,
        description="List of shares of the data",
    )
    def get(self, data_id):
        """
        Get the list of shares of a data.

        :param int data_id: The id of the data.
        :status 403: The user is not allowed to access the data.
        :status 404: The data does not exist.

        .. :quickref: Data; Get list of data shares
        """
        data = data_service.get_if_authorized(data_id)
        shared = []
        for share in data.shares:
            if not share.is_expired():
                shared.append(share)
        schema = DataShareSchema(many=True)
        return dump_data(schema, shared=shared)


class DataShareAPI(Resource):
    @with_query_arg(
        "outputFormat",
        str,
        required=False,
        description="Desired output format (leave blank for zip shapefile)",
    )
    @with_response(
        status=200,
        description="Geodata in specified file format",
        content={
            "application/octet-stream": {"type": "string", "format": "binary"}
        },
    )
    def get(self, uid):
        """Return the geometries of a shared data.

        :param str uid: The uid of a data share.
        :status 404: The share does not exist at this time.
        :status 415: Output format is not supported.
        :status 500:
            There was an error with the geometry while creating the file or
            data type is currently not supported for download.

        .. :quickref: Shares; Download a shared geodata
        """
        parser = reqparse.RequestParser()
        parser.add_argument("outputFormat", type=str, location="args")
        args = parser.parse_args()

        share = DataShare.get_by_uid(uid)
        if share is None or share.is_expired():
            raise RequestError("Share not existing", 404)
        data = share.data
        with get_temporary_directory() as temp_dir:
            filename, file_object = get_geo_data_download(
                data, temp_dir, args.get("outputFormat")
            )
            return send_file(
                file_object, as_attachment=True, download_name=filename
            )

    @token_required
    @with_response(
        200,
        schema=MessageSchema,
        description="Data share deleted successfully",
    )
    def delete(self, uid):
        """Delete a data share.

        :param str uid: The uid of a data share.
        :status 403: The user cannot delete share on this project.
        :status 404: The share or its project data does not exist.

        .. :quickref: Shares; Delete a data share
        """
        share = DataShare.get_by_uid(uid)
        if share is None or share.is_expired():
            raise RequestError("Share not existing", 404)
        data_service.get_if_authorized(share.data_id)
        share.expired = True
        share.update()
        return jsonify(message="share {} set to expired".format(uid))
