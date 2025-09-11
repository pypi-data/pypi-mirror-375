import functools
from typing import Type

from flask import jsonify, request
from marshmallow import Schema

from ..exceptions import PermissionError, RequestError
from ..services.permission_service import has_permission, has_permission_for_id


def get_json_content(exception=True):
    content = request.get_json()
    if content is None and exception:
        raise RequestError(
            "Invalid content: Accepting application/json type", 400
        )
    return content


def dump_data(serializer, **kwargs):
    dict_data = {}
    for k, v in kwargs.items():
        serialized = serializer.dump(v)
        dict_data[k] = serialized
    return jsonify(**dict_data)


def check_permission(obj):
    """Check if the user of the request has permissions on the object

    Raises:
        PermissionError if the user does not have permissions
    """
    if not has_permission(obj):
        raise PermissionError


def check_permission_for_id(obj_class, obj_id):
    """Check if the user of the request has permissions on the object with the
    given id

    Raises:
        PermissionError if the user does not have permissions
    """
    if not has_permission_for_id(obj_class, obj_id):
        raise PermissionError


_openapi_types = {"int": "integer", "bool": "boolean", "str": "string"}


def type2openapi(type_: type | str) -> str:
    """Convert python type to openAPI compliant type.

    :param type_:
    :return: openAPI type
    """
    _type = type_.__name__ if isinstance(type_, type) else type_
    return _openapi_types.get(_type, _type)


def with_request_body(
    schema: Schema | Type[Schema] | list[Schema | Type[Schema]] | str = None,
    description: str = "",
    required: bool = True,
    content: dict = None,
):
    """Annotate operation function with openAPI requestBody.

    If `schema` is set, it will add an application/json content with it as
    schema.

    :param schema:
        either a schema or schema instance (for one schema) or a list of
        schema instances or classes (for polymorphism with response type).
        Can also be a string that will be used 'as is' for the schema
        reference.
    :param description:
    :param required:
    :param content:
    """

    def decorate(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        wrapped.__apispec__ = getattr(func, "__apispec__", {})
        wrapped.__apispec__["requestBody"] = {
            "schema": schema,
            "description": description,
            "required": required,
            "content": content or {},
        }
        return wrapped

    return decorate


def with_response(
    status: int,
    schema: Schema | Type[Schema] | list[Schema | Type[Schema]] | str = None,
    description: str = "",
    content: dict | None = None,
):
    """Annotate operation function with openAPI response.

    If `schema` is set, it will add an application/json content with it as
    schema.

    :param status:
    :param schema:
        either a schema or schema instance (for one schema) or a list of
        schema instances or classes (for polymorphism with response type).
        Can also be a string that will be used 'as is' for the schema
        reference.
    :param description:
    :param content:
    """

    def decorate(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        wrapped.__apispec__ = getattr(func, "__apispec__", {})
        wrapped.__apispec__["responses"] = wrapped.__apispec__.get(
            "responses", {}
        )
        wrapped.__apispec__["responses"][status] = {
            "schema": schema,
            "description": description,
            "content": content or {},
        }
        return wrapped

    return decorate


def with_query_arg(
    name: str,
    type_: str | type | None = None,
    required: bool = True,
    description: str = "",
    **kwargs,
):
    """Annotate operation function with openAPI parameters for query args.

    :param name:
    :param type_:
    :param required:
    :param description:

    .. note::
        any additional keyword argument is added as is in the openAPI parameter
        created by this decorator
    """

    def decorate(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)

        wrapped.__apispec__ = getattr(func, "__apispec__", {})
        wrapped.__apispec__["parameters"] = wrapped.__apispec__.get(
            "parameters", []
        )
        parameter = {
            "in": "query",
            "name": name,
            "required": required,
            "description": description,
        }
        if type_ is not None:
            parameter["schema"] = {"type": type2openapi(type_)}
        parameter = {**parameter, **kwargs}
        wrapped.__apispec__["parameters"].append(parameter)
        return wrapped

    return decorate
