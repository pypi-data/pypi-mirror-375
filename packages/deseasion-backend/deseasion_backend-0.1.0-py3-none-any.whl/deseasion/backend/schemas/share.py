from marshmallow import fields

from ..models import DataShare
from .base import BaseSchema
from .geo_data import BaseDataSchema


class DataShareSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        # This schema is used for creation/retrieval only
        model = DataShare
        fields = (
            "id",
            "uid",
            "expiration",
            "expired",
            "data",
        )
        dump_only = ("id", "uid", "data")

    data = fields.Nested(BaseDataSchema, only=("id", "type"))
