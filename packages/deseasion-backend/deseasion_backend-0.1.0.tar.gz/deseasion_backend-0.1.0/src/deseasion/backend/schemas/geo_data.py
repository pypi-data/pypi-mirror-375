from geoalchemy2.shape import from_shape, to_shape
from marshmallow import Schema, fields, pre_dump, validates
from shapely.geometry import box

from ..models import (
    AttributeType,
    BaseData,
    BaseGeoData,
    DataAttribute,
    DataAttributeNominal,
    DataAttributeOrdinal,
    DataAttributeQuantitative,
    Feature,
    FeatureType,
    GeneratedGeoData,
    GeoData,
    GeoDataType,
    GlobalData,
    KeepOverlap,
    ModelType,
    ProjectData,
    WFSGeoData,
    WMSGeoData,
)
from .base import (
    BaseSchema,
    FieldMethod,
    FieldPluck,
    OneOfSchema,
    constant_enum,
)
from .schemas import UserSchema
from .utils import validate_name


class BaseDataAttributeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DataAttribute
        fields = ("id", "name", "statistics", "data", "type")
        # This schema is never use for creation nor update
        # so basically all fields are not updatable nor creatable (no write)
        dump_only = ("id", "name", "statistics", "data", "type")

    data = fields.Nested("BaseDataSchema", only=("id", "name"))
    type = fields.Enum(
        AttributeType,
        required=True,
        metadata={"description": "Type of attribute"},
    )

    def get_values(self, obj):
        return [v.value for v in obj.values]


class BaseDataAttributeSchemaWithValues(BaseDataAttributeSchema):
    class Meta(BaseDataAttributeSchema.Meta):
        model = DataAttribute
        fields = ("id", "name", "statistics", "data", "values", "type")
        # This schema is never use for creation nor update
        # so basically all fields are not updatable nor creatable (no write)
        dump_only = ("id", "name", "statistics", "data", "values", "type")

    values = FieldMethod(fields.List(fields.Dict), "get_values")

    def get_values(self, obj):
        return [v.value for v in obj.values]


class DataAttributeQuantitativeSchema(BaseDataAttributeSchema):
    class Meta(BaseDataAttributeSchema.Meta):
        model = DataAttributeQuantitative

    type = fields.Enum(
        constant_enum(AttributeType.quantitative), required=True
    )


class DataAttributeNominalSchema(BaseDataAttributeSchema):
    class Meta(BaseDataAttributeSchema.Meta):
        model = DataAttributeNominal

    type = fields.Enum(constant_enum(AttributeType.nominal), required=True)


class DataAttributeOrdinalSchema(BaseDataAttributeSchema):
    class Meta(BaseDataAttributeSchema.Meta):
        model = DataAttributeOrdinal
        fields = ("id", "name", "statistics", "order", "data", "type")
        # This schema is never use for creation nor update
        # so basically all fields are not updatable nor creatable (no write)
        dump_only = ("id", "name", "statistics", "order", "data", "type")

    type = fields.Enum(constant_enum(AttributeType.ordinal), required=True)


class DataAttributeQuantitativeSchemaWithValues(
    BaseDataAttributeSchemaWithValues
):
    class Meta(BaseDataAttributeSchemaWithValues.Meta):
        model = DataAttributeQuantitative

    type = fields.Enum(
        constant_enum(AttributeType.quantitative), required=True
    )


class DataAttributeNominalSchemaWithValues(BaseDataAttributeSchemaWithValues):
    class Meta(BaseDataAttributeSchemaWithValues.Meta):
        model = DataAttributeNominal

    type = fields.Enum(constant_enum(AttributeType.nominal), required=True)


class DataAttributeOrdinalSchemaWithValues(BaseDataAttributeSchemaWithValues):
    class Meta(BaseDataAttributeSchemaWithValues.Meta):
        model = DataAttributeOrdinal
        fields = (
            "id",
            "name",
            "statistics",
            "order",
            "data",
            "values",
            "type",
        )
        # This schema is never use for creation nor update
        # so basically all fields are not updatable nor creatable (no write)
        dump_only = (
            "id",
            "name",
            "statistics",
            "order",
            "data",
            "values",
            "type",
        )

    type = fields.Enum(constant_enum(AttributeType.ordinal), required=True)


class DataAttributeSchema(OneOfSchema, BaseDataAttributeSchema):
    type_schemas = {
        AttributeType.quantitative.name: DataAttributeQuantitativeSchema,
        AttributeType.nominal.name: DataAttributeNominalSchema,
        AttributeType.ordinal.name: DataAttributeOrdinalSchema,
    }

    def get_obj_type(self, obj):
        return obj.type.name


class DataAttributeSchemaWithValues(
    OneOfSchema, BaseDataAttributeSchemaWithValues
):
    type_schemas = {
        AttributeType.quantitative.name: (
            DataAttributeQuantitativeSchemaWithValues
        ),
        AttributeType.nominal.name: DataAttributeNominalSchemaWithValues,
        AttributeType.ordinal.name: DataAttributeOrdinalSchemaWithValues,
    }

    def get_obj_type(self, obj):
        return obj.type.name


class BaseDataSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = BaseData
        fields = (
            "id",
            "type",
            "name",
            "description",
            "attributes",
            "created_at",
            "modified_at",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = ("id", "type", "attributes", "created_at", "modified_at")

    type = fields.Enum(GeoDataType)
    name = fields.String(required=False)
    attributes = fields.Nested(
        DataAttributeSchema, many=True, exclude=("data",)
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        validate_name(value)

    @pre_dump
    def load_properties(self, data, **kwargs):
        """Load the computed properties of the object (stats, attributes...)"""
        data.load_properties()
        return data


class BaseGeoDataSchema(BaseDataSchema):
    class Meta(BaseDataSchema.Meta):
        model = BaseGeoData
        fields = (
            "id",
            "type",
            "name",
            "description",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = (
            "id",
            "type",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
        )

    extent = FieldMethod(
        fields.List(fields.Float()),
        "get_extent",
        metadata={"minItems": 4, "maxItems": 4},
    )
    extent_filter = FieldMethod(
        fields.List(fields.Float()),
        "get_extent_filter",
        "set_extent_filter",
        metadata={"minItems": 4, "maxItems": 4},
    )

    def get_extent(self, obj):
        """Returns the extent of the data (xmin,ymin,xmax,ymax)"""
        if obj.extent is None:
            return [-180.0, -90.0, 180.0, 90.0]
        extent = to_shape(obj.extent)
        return extent.bounds

    def get_extent_filter(self, obj):
        """Returns the extent filter of the data (xmin,ymin,xmax,ymax)"""
        if obj.extent_filter is None:
            return [-180.0, -90.0, 180.0, 90.0]
        extent_filter = to_shape(obj.extent_filter)
        return extent_filter.bounds

    def set_extent_filter(self, extent):
        """Set the extent filter of the data (xmin,ymin,xmax,ymax)"""
        if extent:
            geom = box(*extent)
            return from_shape(geom)
        return None


class WFSGeoDataSchema(BaseGeoDataSchema):
    class Meta(BaseGeoDataSchema.Meta):
        model = WFSGeoData
        fields = (
            "id",
            "type",
            "name",
            "description",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
            "is_public",
            "original_name",
            "title",
            "url",
            "keywords",
            "version",
            "feature_type",
            "upload_user",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = (
            "id",
            "url",
            "type",
            "attributes",
            "extent",
            "is_public",
            "feature_type",
            "upload_user",
            "original_name",
            "created_at",
            "modified_at",
        )

    type = fields.Enum(constant_enum(GeoDataType.wfs))
    upload_user = fields.Nested(UserSchema, only=("id", "username"))


class WFSGeoDataCreationSchema(WFSGeoDataSchema):
    class Meta(WFSGeoDataSchema.Meta):
        exclude = (
            "id",
            "type",
            "name",
            "attributes",
            "extent",
            "original_name",
            "title",
            "description",
            "keywords",
            "upload_user",
            "is_public",
            "created_at",
            "modified_at",
        )
        dump_only = ()


class WMSGeoDataSchema(BaseGeoDataSchema):
    class Meta(BaseGeoDataSchema.Meta):
        model = WMSGeoData
        fields = (
            "id",
            "type",
            "name",
            "description",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
            "is_public",
            "original_name",
            "title",
            "url",
            "keywords",
            "version",
            "classes",
            "start",
            "stop",
            "step",
            "layer",
            "resolution",
            "upload_user",
        )
        dump_only = (
            "id",
            "url",
            "type",
            "attributes",
            "extent",
            "is_public",
            "layer",
            "upload_user",
            "original_name",
            "created_at",
            "modified_at",
        )

    type = fields.Enum(constant_enum(GeoDataType.wms))
    classes = fields.List(fields.List(fields.Float))
    upload_user = fields.Nested(UserSchema, only=("id", "username"))


class WMSGeoDataCreationSchema(WMSGeoDataSchema):
    class Meta(WMSGeoDataSchema.Meta):
        exclude = (
            "id",
            "type",
            "name",
            "original_name",
            "title",
            "description",
            "keywords",
            "upload_user",
            "is_public",
            "created_at",
            "modified_at",
        )
        dump_only = ()


class StreamGeoDataSchema(OneOfSchema, BaseGeoDataSchema):
    type_field = "type"
    type_schemas = {
        GeoDataType.wfs.name: WFSGeoDataSchema,
        GeoDataType.wms.name: WMSGeoDataSchema,
    }

    def get_obj_type(self, obj):
        return obj.type.name


class StreamGeoDataPermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = BaseData.Permission
        # All fields can be used for creation, update and retrieval
        fields = ("user",)

    user = fields.Pluck(UserSchema, "id")


class StreamGeoDataAccessSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = BaseData
        # All fields can be used for creation, update and retrieval
        fields = ("is_public", "permissions")

    permissions = fields.Nested(StreamGeoDataPermissionSchema, many=True)


class GlobalDataSchema(BaseDataSchema):
    class Meta(BaseDataSchema.Meta):
        model = GlobalData
        fields = (
            "id",
            "type",
            "name",
            "description",
            "attributes",
            "properties",
            "upload_user",
            "is_public",
            "created_at",
            "modified_at",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = (
            "id",
            "type",
            "attributes",
            "upload_user",
            "is_public",
            "created_at",
            "modified_at",
        )

    type = fields.Enum(constant_enum(GeoDataType.global_data))
    upload_user = fields.Nested(UserSchema, only=("id", "username"))
    properties = FieldMethod(
        fields.Dict(),
        "get_properties",
        deserialize="set_properties",
        metadata={"description": "properties organized by property name"},
        required=False,
    )

    def get_properties(self, obj):
        return {p.attribute.name: p.value for p in obj.properties}

    def set_properties(self, properties):
        # If persisting changes
        #    need to delete old properties beforehand
        #    and add attribute with properties afterwards
        attributes = {attr.name: attr for attr in self.instance.attributes}
        new_properties = []
        for key, value in properties.items():
            old_attr = attributes.get(key, None)
            attr_type = self.instance._choose_attribute_type(value)
            attr = (
                old_attr
                if isinstance(old_attr, attr_type)
                else attr_type(name=key, data=self.instance)
            )
            new_properties.append(
                attr.get_value_class()(
                    value=value, attribute=attr, feature=self.instance.feature
                )
            )
        return new_properties


class GlobalDataCreationSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=False)
    properties = fields.Dict(
        metadata={"description": "properties organized by property name"},
        required=True,
    )

    @validates("name")
    def validate_name(self, value, **kwargs):
        validate_name(value)


class GeoDataSchema(BaseGeoDataSchema):
    class Meta(BaseGeoDataSchema.Meta):
        model = GeoData
        update_fields = ("name", "description")
        fields = (
            "id",
            "type",
            "name",
            "original_name",
            "source_driver",
            "upload_user",
            "description",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
            "is_public",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = (
            "id",
            "type",
            "original_name",
            "source_driver",
            "upload_user",
            "attributes",
            "extent",
            "extent_filter",
            "created_at",
            "modified_at",
            "is_public",
        )

    type = fields.Enum(constant_enum(GeoDataType.geo_data))
    upload_user = fields.Nested(UserSchema, only=("id", "username"))


class GeneratedGeoDataSchema(BaseGeoDataSchema):
    class Meta(BaseGeoDataSchema.Meta):
        model = GeneratedGeoData
        fields = (
            "id",
            "type",
            "name",
            "attributes",
            "extent",
            "created_at",
            "modified_at",
            "project_data",
        )
        # This schema is never use for creation, so all below fields are the
        # non-updatable
        # is_public can only be changed through permission schema
        dump_only = (
            "id",
            "type",
            "attributes",
            "extent",
            "created_at",
            "modified_at",
            "project_data",
        )

    type = fields.Enum(constant_enum(GeoDataType.generated_geo_data))
    project_data = FieldPluck(ProjectData, "id")


class DataSchema(OneOfSchema, BaseDataSchema):
    type_field = "type"
    type_schemas = {
        GeoDataType.global_data.name: GlobalDataSchema,
        GeoDataType.geo_data.name: GeoDataSchema,
        GeoDataType.generated_geo_data.name: GeneratedGeoDataSchema,
        GeoDataType.wfs.name: WFSGeoDataSchema,
        GeoDataType.wms.name: WMSGeoDataSchema,
    }

    def get_obj_type(self, obj):
        return obj.type.name


class GeoOnlyDataSchema(OneOfSchema, BaseDataSchema):
    type_field = "type"
    type_schemas = {
        GeoDataType.geo_data.name: GeoDataSchema,
        GeoDataType.generated_geo_data.name: GeneratedGeoDataSchema,
        GeoDataType.wfs.name: WFSGeoDataSchema,
        GeoDataType.wms.name: WMSGeoDataSchema,
    }

    def get_obj_type(self, obj):
        return obj.type.name


class GeoDataPermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = GeoData.Permission
        # All fields can be used for creation, update and retrieval
        fields = ("user",)

    user = fields.Pluck(UserSchema, "id")


class GeoDataAccessSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = GeoData
        # All fields can be used for creation, update and retrieval
        fields = ("is_public", "permissions")

    permissions = fields.Nested(GeoDataPermissionSchema, many=True)


class GlobalDataPermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = GlobalData.Permission
        # All fields can be used for creation, update and retrieval
        fields = ("user",)

    user = fields.Pluck(UserSchema, "id")


class GlobalDataAccessSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = GlobalData
        # All fields can be used for creation, update and retrieval
        fields = ("is_public", "permissions")

    permissions = fields.Nested(GlobalDataPermissionSchema, many=True)


class BaseDisaggregationCriterionSchema(Schema):
    data = fields.String()
    attribute = fields.String()
    value = fields.Raw()


class DisaggregationCriterionWeightedSumSchema(
    BaseDisaggregationCriterionSchema
):
    weight = fields.Float()


class DisaggregationCriterionZonePropositionSchema(
    BaseDisaggregationCriterionSchema
):
    numeric_value = fields.Float()
    area = fields.Float()
    fitness = fields.Float()


class BaseExplainabilitySchema(Schema):
    model_type = fields.Enum(ModelType)


class BaseModelExplainabilitySchema(Schema):
    disaggregation = fields.Nested(
        BaseDisaggregationCriterionSchema, many=True
    )


class ExplainabilityContinuousRuleSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.continuous_rule))


class ExplainabilityBufferSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.geo_buffer))
    radius = fields.Integer()


class ExplainabilityWeightedSumSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.weighted_sum))
    disaggregation = fields.Nested(
        DisaggregationCriterionWeightedSumSchema, many=True
    )


class ExplainabilityDiscreteModelSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.categories_rule))
    rule = fields.String()


class ProfileCriterionSchema(Schema):
    data = fields.String(allow_none=False)
    attribute = fields.String(allow_none=False)
    value = fields.Raw(allow_none=False)
    weight = fields.Float(allow_none=False)


class ExplainabilityMRSortCriterionSchema(Schema):
    data = fields.String()
    attribute = fields.String()
    maximize = fields.Boolean()


class ExplainabilityMRSortSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.mrsort))
    lower = fields.Nested(ProfileCriterionSchema, many=True, allow_none=True)
    upper = fields.Nested(ProfileCriterionSchema, many=True, allow_none=True)
    categories = fields.List(fields.String(allow_none=False))
    criteria = fields.Nested(
        BaseDisaggregationCriterionSchema,
        only=("data", "attribute"),
        many=True,
    )
    majority_threshold = fields.Float()


class ExplainabilityAttributeWithValues(Schema):
    data = fields.String()
    attribute = fields.String()
    values = fields.List(fields.Raw(allow_none=False))


class ExplainabilityOverlapSchema(BaseExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.merge_overlap))
    aggregated = fields.Nested(ExplainabilityAttributeWithValues, many=True)
    keep_overlap = fields.Enum(KeepOverlap)


class ExplainabilityMergedFeaturesSchema(BaseExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.dissolve_adjacent))


class ExplainabilityZonePropositionSchema(BaseModelExplainabilitySchema):
    model_type = fields.Enum(constant_enum(ModelType.zone_proposition))
    disaggregation = fields.Nested(
        DisaggregationCriterionZonePropositionSchema, many=True
    )


class ExplainabilitySchema(OneOfSchema, BaseExplainabilitySchema):
    type_field = "model_type"
    type_schemas = {
        ModelType.categories_rule.name: ExplainabilityDiscreteModelSchema,
        ModelType.continuous_rule.name: ExplainabilityContinuousRuleSchema,
        ModelType.geo_buffer.name: ExplainabilityBufferSchema,
        ModelType.mrsort.name: ExplainabilityMRSortSchema,
        ModelType.weighted_sum.name: ExplainabilityWeightedSumSchema,
        ModelType.merge_overlap.name: ExplainabilityOverlapSchema,
        ModelType.dissolve_adjacent.name: ExplainabilityMergedFeaturesSchema,
        ModelType.zone_proposition.name: ExplainabilityZonePropositionSchema,
    }

    def get_obj_type(self, obj):
        return obj.model_type.name


class FeatureSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Feature
        fields = (
            "id",
            "type",
            "data",
            "properties",
            "explainability",
            "execution_artifact",
            "input_data",
            "output_data",
        )
        # This schema is never use for creation nor update
        # so basically all fields are not updatable nor creatable (no write)
        dump_only = (
            "id",
            "type",
            "data",
            "properties",
            "explainability",
            "execution_artifact",
            "input_data",
            "output_data",
        )

    type = fields.Enum(FeatureType)
    properties = FieldMethod(
        fields.Dict(),
        "get_properties",
        metadata={
            "description": "feature properties organized by property name"
        },
    )
    explainability = FieldMethod(
        fields.Nested(ExplainabilitySchema), serialize="get_explainability"
    )
    execution_artifact = FieldMethod(
        fields.Nested(ExplainabilitySchema), serialize="get_execution_artifact"
    )
    input_data = FieldMethod(
        fields.Nested(BaseDataSchema, many=True),
        serialize="get_input_data",
    )
    output_data = FieldMethod(
        fields.Nested(BaseDataSchema, many=True),
        serialize="get_output_data",
    )
    data = FieldPluck(BaseData, "id")

    def get_input_data(self, obj):
        return BaseDataSchema(many=True).dump(obj.get_input_data())

    def get_output_data(self, obj):
        return BaseDataSchema(many=True).dump(obj.get_output_data())

    def get_properties(self, obj):
        return {p.attribute.name: p.value for p in obj.properties}

    def get_explainability(self, obj):
        return obj.explain()

    def get_execution_artifact(self, obj):
        return obj.execution_artifact


class BaseDataFeaturesSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = BaseData
        fields = ("features",)
        dump_only = ("features",)

    features = FieldPluck(Feature, "id", many=True)
