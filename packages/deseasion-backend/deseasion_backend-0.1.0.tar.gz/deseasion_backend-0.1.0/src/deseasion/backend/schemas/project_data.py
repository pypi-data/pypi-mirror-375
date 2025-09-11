from marshmallow import fields, validates

from ..models import (
    BaseGeoData,
    DataGenerator,
    DataGeo,
    DataStream,
    DataType,
    ProjectData,
    ProjectGlobalData,
)
from .base import (
    BaseSchema,
    FieldMethod,
    FieldPluck,
    OneOfSchema,
    OneOfSchemaWithType,
    constant_enum,
)
from .geo_data import BaseDataAttributeSchema, StreamGeoDataSchema
from .processing_models import (
    PrefModelBaseSchema,
    ProcessingModelCreationSchema,
)
from .project import ProjectSchema
from .utils import validate_name


class ProjectDataBaseSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ProjectData
        dump_only = (
            "id",
            "data_type",
            "data",
            "last_update",
            "project",
            "is_outdated",
            "used_input_attributes",
            "used_output_attributes",
        )

    project = fields.Nested(ProjectSchema)
    data = FieldPluck(BaseGeoData, "id")
    data_type = fields.Enum(DataType, required=True)
    attributes = FieldMethod(
        fields.Nested(
            BaseDataAttributeSchema,
            only=("id", "name", "type", "statistics"),
            many=True,
        ),
        "get_attributes_list",
    )
    input_data = FieldPluck(ProjectData, "id", many=True)
    output_data = FieldPluck(ProjectData, "id", many=True)
    used_input_attributes = FieldMethod(
        fields.Nested(
            BaseDataAttributeSchema,
            only=("id", "name", "data", "type"),
            many=True,
        ),
        "get_used_input_attributes",
    )
    used_output_attributes = FieldMethod(
        fields.Nested(
            BaseDataAttributeSchema,
            only=("id", "name", "data", "type"),
            many=True,
        ),
        "get_used_output_attributes",
    )
    is_outdated = FieldMethod(fields.Boolean(), "check_outdated")

    @validates("name")
    def validate_name(self, value, **kwargs):
        validate_name(value)

    def get_attributes_list(self, obj):
        return obj.get_attributes_list()

    def get_used_input_attributes(self, obj):
        return [
            {
                "id": attribute.id,
                "name": attribute.name,
                "data": {"id": attribute.data_id, "name": attribute.data.name},
                "type": attribute.type.name,
            }
            for attribute in obj.get_used_input_attributes()
        ]

    def get_used_output_attributes(self, obj):
        return [
            {
                "id": attribute.id,
                "name": attribute.name,
                "data": {"id": attribute.data_id, "name": attribute.data.name},
                "type": attribute.type.name,
            }
            for attribute in obj.get_used_attributes()
        ]

    def check_outdated(self, obj):
        return obj.is_outdated()


class ProjectDataBaseCreationSchema(ProjectDataBaseSchema):
    pass


class DataGeoSchema(ProjectDataBaseSchema):
    class Meta(ProjectDataBaseSchema.Meta):
        model = DataGeo
        fields = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "description",
            "name",
            "data",
            "attributes",
            "input_data",
            "output_data",
            "used_input_attributes",
            "used_output_attributes",
            "data_id",
            "is_outdated",
        )
        dump_only = (
            "id",
            "data_type",
            "data",
            "used_input_attributes",
            "used_output_attributes",
            "last_update",
            "created_at",
            "modified_at",
            "project",
            "is_outdated",
        )
        load_only = ("data_id",)

    data_id = fields.Integer()
    data_type = fields.Enum(constant_enum(DataType.geo_data), required=True)


class DataGeoCreationSchema(DataGeoSchema):
    """Schema for the creation of a new project geo data"""

    data_id = fields.Integer(required=True)


class ProjectGlobalDataSchema(ProjectDataBaseSchema):
    class Meta(ProjectDataBaseSchema.Meta):
        model = ProjectGlobalData
        fields = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "description",
            "name",
            "data",
            "attributes",
            "input_data",
            "output_data",
            "used_input_attributes",
            "used_output_attributes",
            "data_id",
            "is_outdated",
        )
        dump_only = (
            "id",
            "data_type",
            "data",
            "used_input_attributes",
            "used_output_attributes",
            "last_update",
            "created_at",
            "modified_at",
            "project",
            "is_outdated",
        )
        load_only = ("data_id",)

    data_id = fields.Integer()
    data_type = fields.Enum(constant_enum(DataType.global_data), required=True)


class ProjectGlobalDataCreationSchema(ProjectGlobalDataSchema):
    """Schema for the creation of a new project global data"""

    data_id = fields.Integer(required=True)


class DataStreamSubStreamSchema(StreamGeoDataSchema):
    # Dummy schema necessary as nested OneOfSchema with only/exclude fields
    # breaks the OpenAPI specification (only one schema will be created when
    # nested, no matter the differences in excluded/only fields)
    pass


class DataStreamSchema(ProjectDataBaseSchema):
    class Meta(ProjectDataBaseSchema.Meta):
        model = DataStream
        fields = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "description",
            "name",
            "data",
            "stream",
            "attributes",
            "input_data",
            "output_data",
            "used_input_attributes",
            "used_output_attributes",
            "stream_id",
            "classes",
            "start",
            "step",
            "stop",
            "resolution",
            "is_outdated",
        )
        dump_only = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "data",
            "used_input_attributes",
            "used_output_attributes",
            "stream",
            "is_outdated",
        )
        load_only = ("stream_id",)

    stream_id = fields.Integer(required=False)
    data_type = fields.Enum(constant_enum(DataType.data_stream), required=True)
    stream = fields.Nested(
        DataStreamSubStreamSchema,
        only=("id", "type"),
    )
    classes = fields.List(fields.List(fields.Float), allow_none=True)


class DataStreamCreationSchema(DataStreamSchema):
    """Schema for the creation of a new project global data"""

    stream_id = fields.Integer(required=True)


class DataGeneratorSchema(ProjectDataBaseSchema):
    class Meta(ProjectDataBaseSchema.Meta):
        model = DataGenerator
        fields = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "description",
            "name",
            "input_data",
            "output_data",
            "data",
            "processing_model",
            "attributes",
            "used_input_attributes",
            "used_output_attributes",
            "is_outdated",
            "proc_models_list",
        )
        dump_only = (
            "id",
            "data_type",
            "created_at",
            "modified_at",
            "last_update",
            "project",
            "data",
            "used_input_attributes",
            "used_output_attributes",
            "is_outdated",
            "proc_models_list",
        )

    data_type = fields.Enum(constant_enum(DataType.generator), required=True)
    # This field is used to create new processing models
    processing_model = fields.Nested(
        ProcessingModelCreationSchema(exclude=("data_generator",))
    )
    proc_models_list = fields.Nested(
        PrefModelBaseSchema,
        attribute="_processing_models",
        many=True,
        only=("id", "model_type", "name"),
    )


class DataGeneratorCreationSchema(DataGeneratorSchema):
    name = fields.String(required=True, allow_none=False)


# The inheritance from ProjectDataBaseSchema is necessary so fields.Pluck
# nesting this schema will work (they test field on ProjectDataSchema
# not on its type schemas)
class ProjectDataSchema(OneOfSchema, ProjectDataBaseSchema):
    type_field = "data_type"
    type_schemas = {
        DataType.geo_data.name: DataGeoSchema,
        DataType.generator.name: DataGeneratorSchema,
        DataType.global_data.name: ProjectGlobalDataSchema,
        DataType.data_stream.name: DataStreamSchema,
    }

    def get_obj_type(self, obj):
        return obj.data_type.name


class ProjectDataCreationSchema(
    OneOfSchemaWithType, ProjectDataBaseCreationSchema
):
    type_field = "data_type"
    type_schemas = {
        DataType.geo_data.name: DataGeoCreationSchema,
        DataType.generator.name: DataGeneratorCreationSchema,
        DataType.global_data.name: ProjectGlobalDataCreationSchema,
        DataType.data_stream.name: DataStreamCreationSchema,
    }

    def get_obj_type(self, obj):
        return obj.data_type.name


class ProjectDataGeneratorCreationSchema(
    OneOfSchemaWithType, ProjectDataBaseCreationSchema
):
    type_field = "data_type"
    type_schemas = {DataType.generator.name: DataGeneratorCreationSchema}

    def get_obj_type(self, obj):
        return obj.data_type.name
