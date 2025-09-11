from geoalchemy2.shape import from_shape, to_shape
from marshmallow import fields
from shapely.geometry import box

from ..exceptions import InvalidValue
from ..models import Project, ProjectData, Template, User
from .base import BaseSchema, FieldMethod, FieldPluck
from .schemas import UserSchema


class ProjectSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Project
        exclude = ("_manager", "permissions", "project_tasks")
        dump_only = (
            "id",
            "is_template",
            "data_list",
            "created_at",
            "modified_at",
            "is_public",
            "manager",
        )

    name = fields.String()  # prevent the name field from being required
    manager = fields.Nested(UserSchema, only=("id", "username"))
    extent = FieldMethod(
        fields.List(fields.Float()),
        serialize="get_extent",
        deserialize="load_extent",
        allow_none=True,
        metadata={"minItems": 4, "maxItems": 4},
    )
    is_template = fields.Boolean(
        required=False
    )  # prevent complaint when field not set
    data_list = FieldPluck(ProjectData, "id", many=True)

    def get_extent(self, obj):
        """Returns the Geometry extent as a str "xmin,ymin,xmax,ymax" """
        if obj.extent is None:
            return None
        else:
            extent = to_shape(obj.extent)
            coords = [coord for coord in extent.bounds]
            return coords

    def load_extent(self, value):
        """Loads the extent "xmin,ymin,xmax,ymax" as a Geometry"""
        if value is not None:
            if (
                -180 <= value[0] <= 180
                and -90 <= value[1] <= 90
                and -180 <= value[2] <= 180
                and -90 <= value[3] <= 90
            ):
                extent = box(*value)
                return from_shape(extent, srid=4326)
            else:
                raise InvalidValue(
                    "Error in the extent value, should be within "
                    "[-180,-90,180,90]"
                )
        else:
            return None


class ProjectCreationSchema(ProjectSchema):
    name = fields.String(required=True, allow_none=False)


class ProjectPermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Project.Permission
        update_fields = ("user",)
        fields = ("user",)

    user = FieldPluck(User, "id")


class ProjectAccessSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Project
        update_fields = ("is_public", "permissions")
        fields = ("permissions", "is_public")

    permissions = fields.Nested(ProjectPermissionSchema, many=True)
    is_template = fields.Boolean(
        required=False
    )  # prevent complaint when field not set


class TemplateSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Template
        update_fields = ("name", "description")
        fields = (
            "id",
            "name",
            "description",
            "created_at",
            "manager",
        )
        dump_only = ("id", "created_at", "manager")

    manager = fields.Nested(UserSchema, only=("id", "username"))
    is_template = fields.Boolean(
        required=False
    )  # prevent complaint when field not set


class TemplatePermissionSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Template.Permission
        update_fields = ("user",)
        fields = ("user",)

    user = FieldPluck(User, "id")


class TemplateAccessSchema(BaseSchema):
    class Meta(BaseSchema.Meta):
        model = Template
        update_fields = ("is_public", "permissions")
        fields = ("permissions", "is_public")

    permissions = fields.Nested(TemplatePermissionSchema, many=True)
    is_template = fields.Boolean(
        required=False
    )  # prevent complaint when field not set
