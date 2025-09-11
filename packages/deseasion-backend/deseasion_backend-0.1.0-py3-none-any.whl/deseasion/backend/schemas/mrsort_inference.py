from marshmallow import fields
from marshmallow_sqlalchemy import field_for

from ..models.mrsort_inference import MRSortInferenceAlternative
from ..models.processing_models import MRSort, MRSortCriterion
from .base import BaseSchema, FieldMethod
from .geo_data import BaseDataAttributeSchema
from .processing_models import DiscreteCategorySchema


class MRSortInferenceAlternativeSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = MRSortInferenceAlternative
        fields = ("id", "category_id", "values")
        # This schema is only used nested, so `id` field is necessary
        # it won't be modifiable but will indicate which object to modify
        dump_only = ("values",)

    category_id = field_for(
        MRSortInferenceAlternative, "category_id", allow_none=True
    )
    values = fields.Function(
        lambda obj: {k.attribute_id: v for k, v in obj.values.items()}
    )


class MRSortInferenceCriterionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = MRSortCriterion
        fields = ("attribute_id", "mrsort_id", "maximize", "attribute")
        load_only = ("attribute_id", "mrsort_id")
        dump_only = ("attribute",)

    mrsort_id = fields.Integer()
    attribute_id = fields.Integer()
    attribute = fields.Nested(
        BaseDataAttributeSchema, only=("id", "name", "data")
    )


class MRSortInferenceSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = MRSort
        fields = ("criteria", "categories", "alternatives")
        dump_only = ("categories",)

    alternatives = fields.Nested(
        MRSortInferenceAlternativeSchema,
        many=True,
        attribute="inference_alternatives",
    )
    criteria = FieldMethod(
        fields.Nested(
            MRSortInferenceCriterionSchema(exclude=("mrsort_id",)), many=True
        ),
        "get_criteria",
        deserialize="load_criteria",
    )
    categories = fields.Nested(
        DiscreteCategorySchema, many=True, only=("name", "id")
    )

    def get_criteria(self, obj):
        schema = MRSortInferenceCriterionSchema(
            many=True, only=("attribute", "maximize")
        )
        data = schema.dump(obj.criteria)
        return data

    def load_criteria(self, value):
        new_criteria = []
        schema = MRSortInferenceCriterionSchema()
        for criterion_data in value:
            criterion_data["mrsort_id"] = self.instance.id
            instance = schema.get_instance(criterion_data)
            criterion_obj = schema.load(criterion_data, instance=instance)
            new_criteria.append(criterion_obj)
        return new_criteria
