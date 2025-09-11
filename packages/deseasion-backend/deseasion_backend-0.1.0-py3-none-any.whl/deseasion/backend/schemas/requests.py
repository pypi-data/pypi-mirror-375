"""This module contains all schemas used as response/requestBody types.
"""

from marshmallow import Schema, fields

from ..models import (
    DataType,
    GeoDataType,
    ProcessingModel,
    ProjectData,
    ProjectTaskType,
)
from .base import FieldPluck, OneOfSchema, constant_enum
from .geo_data import (
    BaseGeoDataSchema,
    DataAttributeSchema,
    DataAttributeSchemaWithValues,
    FeatureSchema,
    GeoDataAccessSchema,
    GeoDataSchema,
    GeoOnlyDataSchema,
    GlobalDataAccessSchema,
    StreamGeoDataAccessSchema,
    StreamGeoDataSchema,
)
from .mrsort_inference import MRSortInferenceSchema
from .processing_models import ProcessingModelSchema
from .project import (
    ProjectAccessSchema,
    ProjectSchema,
    TemplateAccessSchema,
    TemplateSchema,
)
from .project_data import (
    DataStreamSubStreamSchema,
    ProjectDataBaseSchema,
    ProjectDataSchema,
)
from .schemas import ProjectTaskSchema, UserSchema
from .share import DataShareSchema


class MessageSchema(Schema):
    """This represents a simple message.

    Mainly used for error responses.
    """

    message = fields.String()


class DataAttributeGetResponse(Schema):
    attribute = fields.Nested(DataAttributeSchema)


class DataAttributeWithValuesGetResponse(Schema):
    attribute = fields.Nested(DataAttributeSchemaWithValues)


class GeoDataGetResponse(Schema):
    geodata = fields.Nested(GeoOnlyDataSchema())


class GeoDataListResponseSchema(Schema):
    geodata = fields.Nested(GeoDataSchema, many=True)


class GeoDataAccessResponseSchema(Schema):
    access = fields.Nested(GeoDataAccessSchema)


class StreamGeoDataResponseSchema(Schema):
    stream = fields.Nested(StreamGeoDataSchema)


class StreamGeoDataListResponseSchema(Schema):
    stream = fields.Nested(StreamGeoDataSchema, many=True)


class StreamGeoDataAccessResponseSchema(Schema):
    access = fields.Nested(StreamGeoDataAccessSchema)


class StreamGeoDataPostRequestSchema(Schema):
    url = fields.String(required=True)


class WMSGeoDataPostRequestSchema(StreamGeoDataPostRequestSchema):
    classes = fields.List(fields.List(fields.Float), required=False)


class WMSStreamClassesSchema(Schema):
    classes = fields.List(fields.List(fields.Float), required=False)
    step = fields.Float(required=False)
    start = fields.Float(required=False)
    stop = fields.Float(required=False)
    resolution = fields.Float(required=False)


class FeatureResponseSchema(Schema):
    feature = fields.Nested(FeatureSchema)


class UserAccessTokenResponseSchema(Schema):
    access_token = fields.String()
    token_type = fields.String()


class UserTokenResponseSchema(UserAccessTokenResponseSchema):
    refresh_token = fields.String()


class ProjectDataListGetResponseSchema(Schema):
    project_data = fields.Nested(ProjectDataSchema, many=True)


class ProjectProcessTaskSchema(ProjectTaskSchema):
    type = fields.Enum(constant_enum(ProjectTaskType.process_project_data))


class ProjectDataPostResponseSchema(Schema):
    task = fields.Nested(ProjectProcessTaskSchema)


class ProjectDataGetResponseSchema(Schema):
    project_data = fields.Nested(ProjectDataSchema)


class ProjectDataInputListPostResponseSchema(Schema):
    input_data = fields.Nested(
        ProjectDataBaseSchema, only=("id", "name", "data_type"), many=True
    )


class ProjectDataActiveModelPutResponseSchema(Schema):
    processing_model = fields.Nested(ProcessingModelSchema)


class ProjectDataModelChangePostRequestBodySchema(Schema):
    id = FieldPluck(ProcessingModel, "id", required=True)


class MRSortInferenceGetResponseSchema(Schema):
    inference_data = fields.Nested(MRSortInferenceSchema)


class ProjectListGetResponseSchema(Schema):
    projects = fields.Nested(ProjectSchema, many=True)


class ProjectFromTemplateRequestBody(Schema):
    template = fields.Integer(required=True)
    name = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    extent = fields.List(
        fields.Float(),
        metadata={"minItems": 4, "maxItems": 4},
        allow_none=True,
    )


class ProjectGetResponseSchema(Schema):
    project = fields.Nested(ProjectSchema)


class ProjectPermissionGetResponseSchema(Schema):
    access = fields.Nested(ProjectAccessSchema)


class TemplatePermissionGetResponseSchema(Schema):
    access = fields.Nested(TemplateAccessSchema)


class ProjectSharedDataListPostResponseSchema(Schema):
    data_list = fields.Nested(
        ProjectDataBaseSchema,
        only=("name", "id", "data", "data_type"),
        many=True,
    )


class ProjectSharedBaseDataSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    data = fields.Pluck(BaseGeoDataSchema, "id")
    data_type = fields.Enum(DataType)
    is_outdated = fields.Boolean()
    input_data = FieldPluck(ProjectData, "id", many=True)
    output_data = FieldPluck(ProjectData, "id", many=True)


class ProjectSharedGeoDataSchema(ProjectSharedBaseDataSchema):
    data_type = fields.Enum(constant_enum(DataType.geo_data))


class ProjectSharedGlobalDataSchema(ProjectSharedBaseDataSchema):
    data_type = fields.Enum(constant_enum(DataType.global_data))


class ProjectSharedDataStreamSchema(ProjectSharedBaseDataSchema):
    data_type = fields.Enum(constant_enum(DataType.data_stream))
    stream = fields.Nested(
        DataStreamSubStreamSchema,
        only=("id", "type"),
    )


class ProjectSharedGeneratedDataSchema(ProjectSharedBaseDataSchema):
    data_type = fields.Enum(constant_enum(DataType.generator))
    processing_model = fields.Nested(
        ProcessingModelSchema(exclude=("data_generator",))
    )


class ProjectSharedDataSchema(OneOfSchema, ProjectSharedBaseDataSchema):
    type_field = "data_type"
    type_schemas = {
        DataType.geo_data.name: ProjectSharedGeoDataSchema,
        DataType.generator.name: ProjectSharedGeneratedDataSchema,
        DataType.global_data.name: ProjectSharedGlobalDataSchema,
        DataType.data_stream.name: ProjectSharedDataStreamSchema,
    }

    def get_obj_type(self, obj):
        return obj.data_type.name


class ProjectSharedDataListGetResponseSchema(Schema):
    data_list = fields.Nested(ProjectSharedDataSchema, many=True)


class ProjectTemplatePostResponseSchema(Schema):
    template = fields.Nested(TemplateSchema)


class ProjectTemplateListGetResponseSchema(Schema):
    templates = fields.Nested(TemplateSchema, many=True)


class ProjectSharesGetResponseSchema(Schema):
    shared = fields.Nested(DataShareSchema, many=True)


class ShareBaseDataPostResponseSchema(Schema):
    shared = fields.Nested(DataShareSchema)


class ProjectTaskListGetResponseSchema(Schema):
    tasks = fields.Nested(ProjectTaskSchema, many=True)
    total = fields.Integer()


class TaskGetResponseSchema(Schema):
    task = fields.Nested(ProjectTaskSchema)


class UserListGetResponseSchema(Schema):
    users = fields.Nested(UserSchema, only=("id", "username"), many=True)


class GlobalDataAccessResponseSchema(Schema):
    access = fields.Nested(GlobalDataAccessSchema)


class DataAttributeRemappingSchema(Schema):
    old_attribute = fields.Integer(required=True, allow_none=False)
    new_attribute = fields.Integer(required=True, allow_none=False)


class ProjectDataReplaceInputsPostRequestBodySchema(Schema):
    attributes_mapping = fields.Nested(
        DataAttributeRemappingSchema,
        many=True,
        required=True,
        allow_none=False,
        metadata={
            "description": "list mapping of old data attributes to new ones"
        },
    )


class DataTypeSetSchema(Schema):
    type = fields.List(fields.Enum(GeoDataType))
