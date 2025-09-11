from flask import current_app as app
from marshmallow import (
    Schema,
    fields,
    pre_dump,
    pre_load,
    validate,
    validates_schema,
)
from marshmallow.exceptions import ValidationError

from ..models import DataAttribute
from ..models.processing_models import (
    AttributeType,
    ContinuousRule,
    DefaultValue,
    DiscreteCategory,
    DiscreteRules,
    DiscreteRulesCategory,
    DissolveAdjacentModel,
    GeoBuffer,
    KeepOverlap,
    MergeOverlapModel,
    ModelType,
    MRSort,
    MRSortCriterion,
    PrefDefaultValues,
    ProcessingModel,
    WeightedSum,
    WeightedSumOperand,
    ZonePropositionGenerator,
)
from .base import (
    BaseSchema,
    FieldMethod,
    FieldPluck,
    OneOfSchema,
    OneOfSchemaWithType,
    constant_enum,
)
from .geo_data import BaseDataAttributeSchema


class PrefModelBaseSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ProcessingModel
        dump_only = ("id", "model_type", "data_generator", "used_attributes")

    model_type = fields.Enum(ModelType, required=True)
    data_generator = fields.Pluck("DataGeneratorSchema", "id")
    used_attributes = FieldMethod(
        fields.Nested(
            BaseDataAttributeSchema,
            only=("id", "name", "data", "type"),
            many=True,
        ),
        "get_used_attributes",
    )

    def get_used_attributes(self, obj):
        return [
            {
                "id": attribute.id,
                "name": attribute.name,
                "data": {"id": attribute.data_id, "name": attribute.data.name},
                "type": attribute.type.name,
            }
            for attribute in obj.get_used_input_attributes()
        ]


class PrefModelBaseCreationSchema(PrefModelBaseSchema):
    pass


class MergeOverlapModelSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = MergeOverlapModel
        fields = (
            "id",
            "model_type",
            "data_generator",
            "cut_to_extent",
            "keep_overlap",
            "name",
            "used_attributes",
        )

    keep_overlap = fields.Enum(KeepOverlap)
    model_type = fields.Enum(
        constant_enum(ModelType.merge_overlap), required=True
    )


class MergeOverlapModelCreationSchema(MergeOverlapModelSchema):
    pass


class DissolveAdjacentModelSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = DissolveAdjacentModel

    model_type = fields.Enum(
        constant_enum(ModelType.dissolve_adjacent), required=True
    )


class DissolveAdjacentModelCreationSchema(DissolveAdjacentModelSchema):
    pass


class GeoBufferSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = GeoBuffer
        fields = (
            "id",
            "model_type",
            "data_generator",
            "cut_to_extent",
            "radius",
            "name",
            "used_attributes",
        )

    model_type = fields.Enum(
        constant_enum(ModelType.geo_buffer), required=True
    )


class GeoBufferCreationSchema(GeoBufferSchema):
    pass


class DiscreteCategorySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DiscreteCategory
        fields = ("id", "name", "position")
        load_only = ("position",)


class DiscreteRulesCategorySchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DiscreteRulesCategory
        fields = ("id", "name", "position", "rules")


class DiscreteRulesSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = DiscreteRules
        fields = (
            "id",
            "model_type",
            "data_generator",
            "cut_to_extent",
            "categories",
            "name",
            "used_attributes",
        )

    model_type = fields.Enum(
        constant_enum(ModelType.categories_rule), required=True
    )
    categories = fields.Nested(
        DiscreteRulesCategorySchema, many=True, only=("name", "rules")
    )


class DiscreteRulesCreationSchema(DiscreteRulesSchema):
    pass


class MRSortCriterionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = MRSortCriterion
        fields = (
            "attribute_id",
            "mrsort_id",
            "attribute",
            "profiles",
            "weight",
            "maximize",
        )
        load_only = ("attribute_id", "mrsort_id")
        dump_only = ("attribute",)

    attribute_id = fields.Integer()
    mrsort_id = fields.Integer()
    attribute = fields.Nested(
        BaseDataAttributeSchema, only=("id", "name", "data")
    )


class MRSortSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = MRSort
        fields = (
            "id",
            "model_type",
            "data_generator",
            "cut_to_extent",
            "categories",
            "criteria",
            "majority_threshold",
            "name",
            "used_attributes",
        )

    model_type = fields.Enum(constant_enum(ModelType.mrsort), required=True)
    categories = FieldMethod(
        fields.Nested(DiscreteCategorySchema, many=True),
        serialize="get_categories",
        deserialize="load_categories",
    )
    criteria = FieldMethod(
        fields.Nested(
            MRSortCriterionSchema(exclude=("mrsort_id",)), many=True
        ),
        "get_criteria",
        deserialize="load_criteria",
    )

    def get_categories(self, obj):
        schema = DiscreteCategorySchema(many=True)
        data = schema.dump(obj.categories)
        return data

    def load_categories(self, value):
        """Load the categories from a dictionary.

        If there is already an existing category with the same name,
        reuse the same object instance.
        """
        new_categories = []
        schema = DiscreteCategorySchema()
        # Check if the MR-Sort instance exists
        if self.instance is not None:
            categories = {c.name: c for c in self.instance.categories}
        else:
            categories = {}
        # Create the categories instances
        for category_data in value:
            name = category_data.get("name")
            # Get the category with the same name if it exists
            instance = categories.get(name, None)
            category_obj = schema.load(category_data, instance=instance)
            new_categories.append(category_obj)
        # Set the position used for the ordering in the database
        for position, category in enumerate(new_categories):
            category.position = position
        return new_categories

    def get_criteria(self, obj):
        schema = MRSortCriterionSchema(
            many=True, only=("attribute", "profiles", "weight", "maximize")
        )
        data = schema.dump(obj.criteria)
        return data

    def load_criteria(self, value):
        new_criteria = []
        schema = MRSortCriterionSchema()
        for criterion_data in value:
            criterion_data["mrsort_id"] = self.instance.id
            instance = schema.get_instance(criterion_data)
            criterion_obj = schema.load(criterion_data, instance=instance)
            new_criteria.append(criterion_obj)
        return new_criteria

    @pre_dump
    def init_criteria(self, mrsort, **kwargs):
        """Load the criteria of the MR-Sort data"""
        app.logger.info("Update the MR-Sort criteria")
        mrsort.init_criteria()
        mrsort.update()
        return mrsort


class MRSortCreationSchema(MRSortSchema):
    pass


class DefaultValueSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = DefaultValue
        fields = ("attribute", "value")

    attribute = FieldPluck(DataAttribute, "id")


class PrefDefaultValuesAttributeSchema(Schema):
    id = fields.Integer()
    name = fields.String()
    attribute = fields.String()
    type = fields.Enum(AttributeType, required=True)


class PrefDefaultValuesBaseSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema):
        model = PrefDefaultValues

    # As it has no deserialize method we don't need to add it to the dump_only
    # fields
    attributes_list = FieldMethod(
        fields.Nested(PrefDefaultValuesAttributeSchema, many=True),
        "get_attributes_list",
    )
    default_values = fields.Nested(
        DefaultValueSchema, many=True, only=("attribute", "value")
    )

    def get_attributes_list(self, obj):
        attrs = []
        for input_data in obj.data_generator.input_data:
            if input_data.data is None:
                continue
            for attr in input_data.data.attributes:
                attrs.append(
                    {
                        "id": attr.id,
                        "name": input_data.name,
                        "attribute": attr.name,
                        "type": attr.type.name,
                    }
                )
        return attrs


class WeightedSumOperandSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = WeightedSumOperand

    attribute = FieldPluck(DataAttribute, "id")


class WeightedSumSchema(PrefDefaultValuesBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = WeightedSum

    model_type = fields.Enum(
        constant_enum(ModelType.weighted_sum), required=True
    )
    operands = fields.Nested(
        WeightedSumOperandSchema, many=True, only=("attribute", "weight")
    )


class WeightedSumCreationSchema(WeightedSumSchema):
    pass


class ContinuousRuleSchema(PrefDefaultValuesBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = ContinuousRule

    model_type = fields.Enum(
        constant_enum(ModelType.continuous_rule), required=True
    )


class ContinuousRuleCreationSchema(ContinuousRuleSchema):
    pass


class ZonePropositionGeneratorSchema(PrefModelBaseSchema):
    class Meta(PrefModelBaseSchema.Meta):
        model = ZonePropositionGenerator

    geo_size = fields.Float(required=False, allow_none=False)
    model_type = fields.Enum(
        constant_enum(ModelType.zone_proposition), required=True
    )
    size = fields.Integer(
        validate=validate.Range(1, 1000), required=False, allow_none=False
    )
    mutation = fields.Float(
        validate=validate.Range(0, 1), required=False, allow_none=False
    )
    children = fields.Integer(
        validate=validate.Range(0, None), required=False, allow_none=False
    )
    filter_clusters = fields.Boolean(required=False, allow_none=False)

    @validates_schema
    def validate_children(self, data, **kwargs):
        if self.get_future_field(data, "children") > self.get_future_field(
            data, "size"
        ):
            raise ValidationError(
                "Cannot create more children than the parent population"
            )

    @validates_schema
    def validate_end_condition(self, data, **kwargs):
        if (
            self.get_future_field(data, "duration") is None
            and self.get_future_field(data, "iterations") is None
        ):
            raise ValidationError("Need at least one exit condition")


class ZonePropositionGeneratorCreationSchema(ZonePropositionGeneratorSchema):
    geo_size = fields.Float(required=False, allow_none=False, missing=0)
    size = fields.Integer(
        validate=validate.Range(1, 1000), missing=80, allow_none=False
    )
    mutation = fields.Float(
        validate=validate.Range(0, 1), missing=0.02, allow_none=False
    )
    children = fields.Integer(
        validate=validate.Range(0, None), missing=60, allow_none=False
    )
    filter_clusters = fields.Boolean(missing=True, allow_none=False)

    @pre_load
    def default_end_condition(self, data, **kwargs):
        if "duration" in data or "iterations" in data:
            return data
        data["iterations"] = 1
        return data


class ProcessingModelSchema(OneOfSchema, PrefModelBaseSchema):
    type_field = "model_type"
    type_schemas = {
        ModelType.categories_rule.name: DiscreteRulesSchema,
        ModelType.continuous_rule.name: ContinuousRuleSchema,
        ModelType.geo_buffer.name: GeoBufferSchema,
        ModelType.mrsort.name: MRSortSchema,
        ModelType.weighted_sum.name: WeightedSumSchema,
        ModelType.merge_overlap.name: MergeOverlapModelSchema,
        ModelType.dissolve_adjacent.name: DissolveAdjacentModelSchema,
        ModelType.zone_proposition.name: ZonePropositionGeneratorSchema,
    }

    def get_obj_type(self, obj):
        return obj.model_type.name


class ProcessingModelCreationSchema(
    OneOfSchemaWithType, PrefModelBaseCreationSchema
):
    type_field = "model_type"
    type_schemas = {
        ModelType.categories_rule.name: DiscreteRulesCreationSchema,
        ModelType.continuous_rule.name: ContinuousRuleCreationSchema,
        ModelType.geo_buffer.name: GeoBufferCreationSchema,
        ModelType.mrsort.name: MRSortCreationSchema,
        ModelType.weighted_sum.name: WeightedSumCreationSchema,
        ModelType.merge_overlap.name: MergeOverlapModelCreationSchema,
        ModelType.dissolve_adjacent.name: DissolveAdjacentModelCreationSchema,
        ModelType.zone_proposition.name: ZonePropositionGeneratorCreationSchema,  # noqa: E501
    }

    def get_obj_type(self, obj):
        return obj.model_type.name
