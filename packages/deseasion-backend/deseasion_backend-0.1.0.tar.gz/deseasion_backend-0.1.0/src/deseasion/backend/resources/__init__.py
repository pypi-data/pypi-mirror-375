from flask_restful import Api

from .auth import LoginAPI, RefreshAPI, UserAPI
from .geo_data import (
    DataAPI,
    DataAttributeAPI,
    DataDownloadAPI,
    DataListAPI,
    FeatureAPI,
    FeatureInputsAPI,
    FeatureOutputsAPI,
    GeoDataAccessAPI,
    GeoDataAPI,
    GeoDataListAPI,
    GeoDataUploadAPI,
    GeoDataUploadRasterAPI,
    GeoDataVectorTileAPI,
    GlobalDataAccessAPI,
    GlobalDataAPI,
    GlobalDataListAPI,
    StreamDataListAPI,
    StreamGeoDataAccessAPI,
    StreamGeoDataAPI,
    StreamGeoDataUpdateAPI,
    WFSGeoDataUploadAPI,
    WMSGeoDataUploadAPI,
)
from .permission import UserListAPI
from .project import (
    ProjectAPI,
    ProjectListAPI,
    ProjectPermissionsAPI,
    ProjectReplaceInputAttributesAPI,
    ProjectSharedDataListAPI,
    ProjectTemplateAPI,
    TemplateAPI,
    TemplateListAPI,
    TemplatePermissionsAPI,
)
from .project_data import (
    MRSortInferenceAPI,
    ProjectDataActiveModelAPI,
    ProjectDataAPI,
    ProjectDataInputSubgraphAPI,
    ProjectDataListAPI,
    ProjectDataModelAPI,
    ProjectDataModelChangeAPI,
    ProjectDataOutputSubgraphAPI,
    ProjectDataReplaceInputAttributesAPI,
)
from .share import (
    DataShareAPI,
    ProjectSharesAPI,
    ShareBaseDataAPI,
    ShareDataListAPI,
)
from .tasks import ProjectTaskListAPI, TaskAPI

api = Api()

api.add_resource(DataListAPI, "/data")
api.add_resource(DataAPI, "/data/<int:data_id>")

api.add_resource(GlobalDataListAPI, "/global-data")
api.add_resource(GlobalDataAPI, "/global-data/<int:data_id>")
api.add_resource(GlobalDataAccessAPI, "/global-data/<int:data_id>/permissions")

api.add_resource(GeoDataListAPI, "/geo-data")
api.add_resource(
    GeoDataVectorTileAPI,
    "/geo-data/<int:geo_data_id>/tiles/<int:z>/<int:x>/<int:y>",
)
api.add_resource(GeoDataAPI, "/geo-data/<int:geo_data_id>")
api.add_resource(GeoDataAccessAPI, "/geo-data/<int:geo_data_id>/permissions")
api.add_resource(DataDownloadAPI, "/data/<int:data_id>/export")
api.add_resource(GeoDataUploadAPI, "/geo-data/upload")
api.add_resource(GeoDataUploadRasterAPI, "/geo-data/upload-raster")
api.add_resource(StreamDataListAPI, "/stream-geo-data")
api.add_resource(StreamGeoDataAPI, "/stream-geo-data/<int:stream_geo_data_id>")
api.add_resource(
    StreamGeoDataAccessAPI,
    "/stream-geo-data/<int:stream_geo_data_id>/permissions",
)
api.add_resource(
    StreamGeoDataUpdateAPI,
    "/stream-geo-data/<int:stream_geo_data_id>/update-data",
)
api.add_resource(WFSGeoDataUploadAPI, "/stream-geo-data/upload-wfs")
api.add_resource(WMSGeoDataUploadAPI, "/stream-geo-data/upload-wms")
api.add_resource(DataAttributeAPI, "/attribute/<int:attribute_id>")
api.add_resource(FeatureAPI, "/feature/<int:feature_id>")
api.add_resource(
    FeatureInputsAPI, "/feature/<int:feature_id>/input-data/<int:data_id>"
)
api.add_resource(
    FeatureOutputsAPI, "/feature/<int:feature_id>/output-data/<int:data_id>"
)

api.add_resource(ProjectListAPI, "/projects")
api.add_resource(ProjectAPI, "/project/<int:project_id>")
api.add_resource(
    ProjectPermissionsAPI, "/project/<int:project_id>/permissions"
)
api.add_resource(ProjectSharedDataListAPI, "/project/<int:project_id>/data")
api.add_resource(ProjectTaskListAPI, "/project/<int:project_id>/tasks")
api.add_resource(ProjectSharesAPI, "/project/<int:project_id>/shared")
api.add_resource(ProjectTemplateAPI, "/project/<int:project_id>/template")
api.add_resource(
    ProjectReplaceInputAttributesAPI,
    "/project/<int:project_id>/replace-attributes",
)
api.add_resource(TemplateListAPI, "/templates")
api.add_resource(TemplateAPI, "/template/<int:template_id>")
api.add_resource(
    TemplatePermissionsAPI, "/template/<int:template_id>/permissions"
)

api.add_resource(TaskAPI, "/task/<string:task_id>")

api.add_resource(ProjectDataListAPI, "/project-data")
api.add_resource(ProjectDataAPI, "/project-data/<int:data_id>")
api.add_resource(
    ProjectDataActiveModelAPI, "/project-data/<int:data_id>/model"
)
api.add_resource(
    ProjectDataModelAPI, "/project-data/<int:data_id>/model/<int:model_id>"
)
api.add_resource(
    ProjectDataModelChangeAPI, "/project-data/<int:data_id>/model/change"
)
api.add_resource(
    MRSortInferenceAPI, "/project-data/<int:data_id>/mr-sort-inference"
)
api.add_resource(
    ProjectDataInputSubgraphAPI, "/project-data/<int:data_id>/input-graph"
)
api.add_resource(
    ProjectDataOutputSubgraphAPI, "/project-data/<int:data_id>/output-graph"
)
api.add_resource(
    ProjectDataReplaceInputAttributesAPI,
    "/project-data/<int:data_id>/replace-attributes",
)
api.add_resource(ShareBaseDataAPI, "/data/<int:data_id>/share")
api.add_resource(ShareDataListAPI, "/shares")
api.add_resource(DataShareAPI, "/shares/<string:uid>")

api.add_resource(UserListAPI, "/users")
api.add_resource(LoginAPI, "/login")
api.add_resource(RefreshAPI, "/refresh")
api.add_resource(UserAPI, "/user")
