from flask import send_file
from flask_restful import Resource, reqparse

from ..exceptions import RequestError
from ..models import ZoneProposition
from ..services.auth_service import token_required
from ..services.geo_data_loading_service import (
    get_geo_data_download,
    get_temporary_directory,
)
from .utils import check_permission, with_query_arg, with_response


class ZonePropositionAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema="#/components/schemas/FeatureCollection",
        description="Features of the recommended zone",
    )
    def get(self, proposition_id):
        """
        Return the details of the recommended zones.

        :param int proposition_id: The id for the recommended zones.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The resource doesn't exist.

        .. :quickref: Zone proposition; Get the details of a zone proposition
        """
        proposition = ZoneProposition.get_by_id(proposition_id)
        if proposition is None:
            raise RequestError("The zone proposition does not exist", 404)
        project = proposition.project
        check_permission(project)
        features = [f.as_geojson() for f in proposition.data.features]
        return {"features": features}


class ZonePropositionDownloadAPI(Resource):
    @token_required
    @with_query_arg(
        "outputFormat",
        str,
        required=False,
        description="Desired output format (leave blank for zip shapefile)",
    )
    @with_response(
        status=200,
        description="Zone Proposition as Geodata in specified file format",
        content={
            "application/octet-stream": {"type": "string", "format": "binary"}
        },
    )
    def get(self, proposition_id):
        """
        Return the recommended zones as geodata.

        :param int proposition_id: The id for the recommended zones.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The resource doesn't exist.
        :status 500:
            There was an error with the geometry while creating the file.

        .. :quickref: Zone proposition; Download zone proposition as geodata
        """
        parser = reqparse.RequestParser()
        parser.add_argument("outputFormat", type=str, location="args")
        args = parser.parse_args()
        proposition = ZoneProposition.get_by_id(proposition_id)
        if proposition is None:
            raise RequestError("The zone proposition does not exist", 404)
        project = proposition.project
        check_permission(project)
        with get_temporary_directory() as temp_dir:
            filename, file_object = get_geo_data_download(
                proposition.data, temp_dir, args.get("outputFormat")
            )
            return send_file(
                file_object, as_attachment=True, download_name=filename
            )
