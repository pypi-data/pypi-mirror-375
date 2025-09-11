import enum

from marshmallow import fields
from marshmallow.utils import is_collection
from marshmallow_oneofschema import OneOfSchema as _OneOfSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from ..models import db


def constant_enum(value) -> type[enum.Enum]:
    """This creates an enum with a single value.

    Its use should be limited to schema polymorphism so a type discriminator
    which is an enumeration of all possible types (children types) is set
    as only the child type in the child.

    :param value: either a single enum item or any object
    :return: enumeration class with only `value` as item

    .. note::
        might override a String field as well if the parent class type
        discriminator field was left open for future appendings, this is
        generally how schema polymorphism is implemented in OpenAPI 3.0+.
        In this case, the closed enumeration must be done in the oneOf classes.
    """
    match value:
        case enum.Enum():
            return enum.Enum(f"enum{value}", {value.name: value.value})
        case _:
            return enum.Enum(f"enum{value}", {value: value})


class FieldMethod(fields.Method):
    """This class represents a field method with an alternative field to use as
    source for OpenAPI specification.

    :param spec_field:
        alternative field to use as source for openAPI specification
    :param serialize: serialization method used
    :param deserialize: deserialization method used
    """

    def __init__(
        self,
        spec_field: fields.Field,
        serialize: str | None = None,
        deserialize: str | None = None,
        **kwargs,
    ):
        self.field = spec_field
        super().__init__(
            serialize=serialize, deserialize=deserialize, **kwargs
        )


class FieldLookupNested(fields.Nested):
    """Nested field which will try to load an existing object.

    https://github.com/marshmallow-code/marshmallow-sqlalchemy/issues/117
    """

    default_error_messages = {
        "type": "Invalid input type. Expected a list.",
        "missing": "Could not find related object {input}.",
    }

    def get_instance_or_fail(self, data):
        instance = self.schema.get_instance(data)
        if not instance:
            self.fail("missing", input=data)
        return instance

    def _deserialize(self, value, attr, data):
        if self.many and not is_collection(value):
            self.fail("type", input=value, type=value.__class__.__name__)

        if self.many:
            return [self.get_instance_or_fail(item) for item in value]

        return self.get_instance_or_fail(value)


class BaseSchema(SQLAlchemyAutoSchema):
    """This is the base class for all schemas converting Json and SQL Models.

    There are multiple cases for schemas:

    * One schema for all CRU operations: then simply put all fields
    * Two schemas for update and retrieval:
      then make one schema with non-modifiable fields as `dump_only` in
      :attr:`Meta`
    * Two schemas for creation and retrieval:
      then make one schema with non-created fields as `dump_only` in
      :attr:`Meta` (can also add write-only fields in `load_only`)
    * Three schemas for creation, update and retrieval:
      split creation schema, then make other schema as an update/retrieval
      shared schema
    * Careful when associating a resource within another, as the update of one
      could update the other. If a single schema is used to represent both
      a resource as itself and the same one nested, the `id` field will be
      broken (non-writable for the resource as itself, writable for the nesting
      resource).

    .. note::

        * Fields with foreign keys are not created by default
        * Relationship fields are not created by default
        * FIelds added manually are not required and non-nullable by default
    """

    class Meta:
        sqla_session = db.session
        strict = True
        load_instance = True

    def get_future_field(self, data, key):
        """Return field value (from instance or serialized data).

        :param data: serialized data that will update instance
        :param key: field name
        :return: value
        """
        return data.get(
            key, None if self.instance is None else getattr(self.instance, key)
        )


class FieldPluck(fields.Pluck):
    """This class creates a pluck field for a SQL model.

    It creates a new schema for this model, only containing the field to pluck.

    :param model: SQL model class to pluck
    :param field_name: field to pluck
    """

    def __init__(self, model, field_name, **kwargs):
        meta_dict = {
            "model": model,
            "fields": (field_name,),
        }
        sch_dict = {"Meta": type("Meta", (BaseSchema.Meta,), meta_dict)}
        schema = type(f"Pluck{model.__name__}Schema", (BaseSchema,), sch_dict)
        super().__init__(schema, field_name, **kwargs)


class OneOfSchema(_OneOfSchema):
    """This class is a wrapper for
    :class:`marshmallow_oneofschema.OneOfSchema`.

    It adds one feature necessary to this backend:

    * Pass schema constructor args and kwargs to typed schemas
    """

    def __init__(self, *args, many=False, **kwargs):
        self._schema_args = args
        self._schema_kwargs = kwargs

        # Wrap schema initialization to add arguments
        self.type_schemas = {
            k: self.with_args(v) for k, v in self.type_schemas.items()
        }

        super(OneOfSchema, self).__init__(many=many)

    def with_args(self, schema):
        """Create a child schema constructor.

        Pass *args and **kwargs which were given when building the oneof schema
        instance.

        :param schema: child schema to prepare
        :return: child schema constructor
        """

        def init_schema(openapi=False):
            """Initialize a child schema.

            Pass *args and **kwargs which were given at parent schema
            instantiation.

            :param openapi:
                indicates whether this schema is created for populating
                an openAPI specification or not, defaults to ``False``
            """
            return schema(*self._schema_args, **self._schema_kwargs)

        return init_schema


class OneOfSchemaWithType(OneOfSchema):
    """This class is a wrapper for
    :class:`marshmallow_oneofschema.OneOfSchema`.

    It is to be used for schemas needing the type to appear in the openapi
    specification while being removed upon deserialization.
    This is typically the case for oneOf creation schemas.
    """

    def with_args(self, schema):
        """Create a child schema constructor.

        Pass *args and **kwargs which were given when building the oneof schema
        instance.

        :param schema: child schema to prepare
        :return: child schema constructor
        """

        def init_schema(openapi=False):
            """Initialize a child schema.

            Pass *args and **kwargs which were given at parent schema
            instantiation.
            Make parent `type_field` field writable by removing it from the
            `dump_only` fields and setting :attr:`dump_only` to ``False`` if
            `openapi` is ``True``.

            :param openapi:
                indicates whether this schema is created for populating
                an openAPI specification or not, defaults to ``False``
            """
            sch = schema(*self._schema_args, **self._schema_kwargs)
            if openapi:
                sch.fields.get(self.type_field).dump_only = False
                sch.dump_only = tuple(set(sch.dump_only) - {self.type_field})
            return sch

        return init_schema
