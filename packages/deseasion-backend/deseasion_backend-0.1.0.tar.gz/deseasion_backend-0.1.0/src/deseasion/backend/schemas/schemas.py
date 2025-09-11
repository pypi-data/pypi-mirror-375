from celery.result import AsyncResult
from marshmallow import Schema, fields

from ..models import ProjectTaskModel, ProjectTaskType, User
from .base import BaseSchema, FieldMethod


class DefaultValueSchema(Schema):
    """Schema to use for creating or updating a default value"""

    name = fields.String(required=True)
    attribute = fields.String(required=True)
    default_value = fields.Field(required=True)


class DefaultValueDeletionSchema(Schema):
    """Schema to use when deleting a default value"""

    name = fields.String(required=True)
    attribute = fields.String(required=True)


class ProjectTaskSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = ProjectTaskModel
        # This schema is read-only so we do not need to change the write/read
        # fields
        # If this changes, we will need to define those and perhaps a creation
        # schema

    type = fields.Enum(ProjectTaskType, required=True)
    info = FieldMethod(fields.Dict(allow_none=True), "get_info")

    def get_info(self, obj):
        """Return the info if the task has the STARTED state."""
        result = AsyncResult(obj.task_id)
        if isinstance(result.info, dict):
            return result.info


class UserSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = User
        exclude = ("password_hash", "tokens", "permissions")
        # This schema is read-only so we do not need to change the write/read
        # fields
        # If this changes, we will need to define those and perhaps a creation
        # schema
