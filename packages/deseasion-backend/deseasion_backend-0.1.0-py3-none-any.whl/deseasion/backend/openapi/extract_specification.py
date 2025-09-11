"""This module gathers functions/classes to extract openAPI specification
from this API.

It can be used as a python function or script.

.. code:: python

    from deseasion.backend.openapi.extract_specification import extract_openapi

    spec = extract_openapi()

.. code:: bash

    python -m deseasion.backend.openapi.extract_specification
"""

import importlib.resources
import inspect
import logging
import re
import sys
from typing import Type

import yaml
from apispec import APISpec, BasePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec.ext.marshmallow.common import (
    get_unique_schema_name,
    make_schema_key,
    resolve_schema_instance,
)
from flask_restful import Api, Resource
from marshmallow import Schema, fields

from ..resources import api
from ..resources.utils import type2openapi
from ..schemas import *  # noqa: F403 (import all schemas for processing)


def get_schemas_classes(
    namespace: str | None = None,
) -> dict[str, Type[BaseSchema]]:  # noqa: F405
    """Get all schema classes from :mod:`api`.

    :param namespace:
        namespace from which to extract specification
        Defaults: ``__name__``
    :return: schema classes as a dictionary
    """
    namespace = namespace or __name__
    res = {}
    for name, obj in inspect.getmembers(sys.modules[namespace]):
        if inspect.isclass(obj) and issubclass(obj, Schema) and obj != Schema:
            res[name.replace("Schema", "")] = obj
    return res


def enum_fields2properties(self, field, **kwargs):
    """Helper function to convert enum field to openAPI spec.

    :param field:
    :return: openAPI spec
    """
    res = {}
    if isinstance(field, fields.Enum):
        values = []
        for member in field.enum:
            values.append(member.name)
        res["type"] = "string"
        res["enum"] = values
    return res


def pluck_fields2properties(self, field, **kwargs) -> dict:
    """Helper function to convert pluck field to openAPI spec.

    It uses a reference on the plucked field instead of its type.

    :param field:
    :return: openAPI spec
    """
    res = {}
    if isinstance(field, fields.Pluck):
        nested = (
            field.nested
            if isinstance(field.nested, str)
            else field.nested.__name__
        )
        ref = nested.replace("Schema", "")
        ref_field = f"#/components/schemas/{ref}/properties/{field.only[0]}"
        if field.many:
            res["items"] = res.get("items", {})
            res["items"]["$ref"] = ref_field
        else:
            res["$ref"] = ref_field
    return res


def method_fields2properties(self, field, **kwargs) -> dict:
    """Helper function to convert method field to openAPI spec.

    It uses the `field.field` field as the actual field to convert.

    :param field:
    :return: openAPI spec
    """
    ret = {}
    if isinstance(field, FieldMethod):  # noqa: F405
        ret = self.field2property(field.field)
    return ret


class MyMarshmallowPlugin(MarshmallowPlugin):
    """This class is a modified version of the basic Marshmallow plugin.

    It is capable of handling :class:`api.schemas.OneOfSchema` schemas.
    """

    schema_names = {}

    def schema_helper(self, name, _, schema=None, **kwargs):
        """Definition helper that allows using a marshmallow
        :class:`Schema <marshmallow.Schema>` to provide OpenAPI
        metadata.

        It was modified to handle correctly :class:`api.schemas.OneOfSchema`
        schemas.

        :param type|Schema schema: A marshmallow Schema class or instance.
        """
        if schema is None:
            return None

        schema_instance = resolve_schema_instance(schema)

        schema_key = make_schema_key(schema_instance)
        self.warn_if_schema_already_in_spec(schema_key)
        assert self.converter is not None, "init_spec has not yet been called"
        self.converter.refs[schema_key] = name

        if isinstance(schema_instance, OneOfSchema):  # noqa: F405
            json_schema = {
                "oneOf": [],
                "discriminator": {
                    "propertyName": schema_instance.type_field,
                    "mapping": {},
                },
            }
            for subname, sch_init in schema_instance.type_schemas.items():
                sch = sch_init(openapi=True)
                subsch_key = make_schema_key(sch)
                if subsch_key not in self.converter.refs:
                    new_subname = self.schema_names[sch.__class__]
                    self.spec.components.schema(
                        get_unique_schema_name(
                            self.spec.components, new_subname
                        ),
                        schema=sch,
                    )
                sch_ref = (
                    f"#/components/schemas/{self.converter.refs[subsch_key]}"
                )
                json_schema["oneOf"].append({"$ref": sch_ref})
                json_schema["discriminator"]["mapping"][subname] = sch_ref
            return json_schema

        return self.converter.schema2jsonschema(schema_instance)


def deep_update(dico: dict, new_dico: dict):
    """Perform a deep update on the first dictionnary with content of second.

    It handles nested dictionary structures, and lists.
    Everything else is updated the regular way.

    :param dico: dictionnary to update
    :param new_dico: updated data as a dictionnary
    """
    for k, v in new_dico.items():
        if k not in dico:
            dico[k] = v
        elif (  # noqa: E721
            type(dico[k]) == list and type(v) == list
        ):  # Make sure to exclude strings
            dico[k] += v
        elif isinstance(dico[k], dict) and isinstance(v, dict):
            deep_update(dico[k], v)
        else:
            dico[k] = v


class FlaskRestfulPlugin(BasePlugin):
    """This class is a :mod:`apispec` plugin made to handle
    :class:`flask_restful.Resource`.
    """

    def init_spec(self, spec: APISpec) -> None:
        """Initialize plugin with APISpec object

        :param APISpec spec: APISpec object this plugin instance is attached to
        """
        self.spec = spec

    def path_helper(
        self,
        path: str | None = None,
        operations: dict | None = None,
        parameters: list[dict] | None = None,
        *,
        resource: Type[Resource] | None = None,
        api: Api | None,
    ):
        """Add path to openAPI specification.

        :param api: ref to API
        :param path: endpoint of path (unused here)
        :param operations: operations statically defined on path
        :param parameters: parameters statically defined on path
        :param resource: API resource
        :raises ValueError: if `resource` is not found in `api`
        :return: openAPI path specification
        """
        assert resource is not None
        assert api is not None

        parameters = [] or parameters
        operations = {} or operations

        for klass, endpoints, _ in api.resources:
            if klass == resource:
                res = self.resource2openapi(klass, endpoints[0])
                operations.update(res["operations"])
                parameters += res.get("parameters", [])
                return res["path"]
        raise ValueError(f"Resource {resource.__name__} not found in API")

    @staticmethod
    def extract_doc_strings(func):
        """Extract any openAPI useful information from operation doc-string.

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI specification
        """
        res = {}
        doc = func.__doc__
        if doc is None:
            return res
        res["description"] = ""
        lines = iter(doc.splitlines())
        # Read description
        while (line := next(lines, None)) is not None:
            line = line.lstrip()
            if line.startswith(":"):
                break
            else:
                res["description"] += "\n" + line
        res["description"] = res["description"].strip()
        # Read rest of doc string
        tree = []
        current_node = None
        while line is not None:
            line = line.strip()
            if line == "---":
                # Reaching yaml part => abort
                break
            if re.match(r"^:", line):
                header = re.findall(r"^:[^:]*:", line)[0]
                if header.startswith(":param"):
                    # Parsing a path parameter
                    description = line[len(header) :].strip()
                    type_, arg = (
                        re.sub(r"^:param ", "", header)
                        .rstrip()[:-1]
                        .split(" ")
                    )
                    current_node = ["param", arg, type_, description]
                elif header.startswith(":status"):
                    # Parsing a response status
                    description = line[len(header) :].strip()
                    status = re.findall(r"\d+", header)[0]
                    current_node = ["status", status, description]
                else:
                    current_node = None
                tree.append(current_node)
            elif re.match(r"^.. :quickref: ", line):
                header = re.findall(r"^.. :quickref: ", line)[0]
                quickref = line[len(header) :]
                tag, description = quickref.split(";")[:2]
                current_node = ["quickref", tag, description]
                tree.append(current_node)
            elif current_node is not None:
                current_node[-1] += " " + line
            line = next(lines, None)

        for node in tree:
            match node:
                case None:
                    continue
                case ["param", arg, type_, description]:
                    res["parameters"] = res.get("parameters", [])
                    res["parameters"].append(
                        {
                            "name": arg,
                            "in": "path",
                            "required": True,
                            "schema": {"type": type2openapi(type_)},
                            "description": description.rstrip().lstrip(),
                        }
                    )
                case ["status", status, description]:
                    res["responses"] = res.get("responses", {})
                    res["responses"][str(status)] = {
                        "description": description.lstrip().rstrip()
                    }
                case ["quickref", tag, description]:
                    res["tags"] = res.get("tags", [])
                    res["tags"].append(tag)
                    res["summary"] = description.rstrip().lstrip()
        return res

    def resource2openapi(self, resource: Type[Resource], endpoint: str):
        """Convert API resource to openAPI specication.

        It extract spec from doc-string and special decorators
        (those modifying `func.__apispec__`).

        :param resource:
        :param endpoint: path endpoint
        :return: _description_
        """
        res = {"path": endpoint, "operations": {}}
        for method in resource.methods:
            func = getattr(resource, method.lower())
            operation = FlaskRestfulPlugin.extract_doc_strings(func)
            deep_update(operation, self.apispec_attr2openapi(func) or {})
            operation["responses"] = operation.get("responses", {})
            if "200" not in operation["responses"]:
                operation["responses"]["200"] = {"description": ""}
            res["operations"][method.lower()] = operation

        groups = re.findall(r"<[^<]*>", endpoint)
        if len(groups) == 0:
            return res
        res["parameters"] = []
        for group in groups:
            type_, arg = re.sub(r"[<>]", "", group).split(":")
            res["parameters"].append(
                {
                    "name": arg,
                    "in": "path",
                    "required": True,
                    "schema": {"type": type2openapi(type_)},
                }
            )
            res["path"] = res["path"].replace(group, f"{{{arg}}}")
        return res

    @property
    def marshmallow_plugin(self) -> MarshmallowPlugin | None:
        """Return :class:`MarshmallowPlugin` plugin if it is used to build
        the specification.

        :return:
        """
        for plugin in self.spec.plugins:
            if isinstance(plugin, MarshmallowPlugin):
                return plugin
        return None

    def _find_schema(self, schema: Schema) -> str | None:
        """Find name under which a schema is registered.

        :param schema:
        :return: registered name or ``None``
        """
        key = make_schema_key(schema)
        return self.marshmallow_plugin.converter.refs.get(key, None)

    def apispec_attr2openapi(self, func) -> dict:
        """Extract operation openAPI spec from function decorators.

        It extract spec from special decorators
        (those modifying `func.__apispec__`).

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI spec
        """
        return {
            **self.apispec_parameters2openapi(func),
            **self.apispec_responses2openapi(func),
            **self.apispec_requestBody2openapi(func),
            **self.apispec_security2openapi(func),
        }

    def apispec_security2openapi(self, func) -> dict:
        """Extract operation security openAPI spec from function decorators.

        It extract spec from `func.__apispec__['security']`.

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI spec
        """
        if not hasattr(func, "__apispec__"):
            return {}
        apispec_attr: dict = func.__apispec__
        if "security" not in apispec_attr:
            return {}
        return {"security": apispec_attr.get("security", [])}

    def apispec_parameters2openapi(self, func) -> dict:
        """Extract operation parameters openAPI spec from function decorators.

        It extract spec from `func.__apispec__['parameters']`.

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI spec
        """
        if not hasattr(func, "__apispec__"):
            return {}
        apispec_attr: dict = func.__apispec__
        if "parameters" not in apispec_attr:
            return {}
        return {"parameters": apispec_attr.get("parameters", [])}

    def apispec_requestBody2openapi(self, func) -> dict:
        """Extract operation request body openAPI spec from function
        decorators.

        It extract spec from `func.__apispec__['requestBody']`.

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI spec
        """
        if not hasattr(func, "__apispec__"):
            return {}
        apispec_attr: dict = func.__apispec__
        if "requestBody" not in apispec_attr:
            return {}
        request = apispec_attr.get("requestBody", {})

        res = {}
        res["requestBody"] = {
            "description": request.get("description", ""),
            "content": request.get("content", {}),
            "required": request.get("required", True),
        }
        schema = request.get("schema", None)
        if isinstance(schema, str):
            deep_update(
                res["requestBody"]["content"],
                {"application/json": {"schema": {"$ref": schema}}},
            )
        elif isinstance(schema, list):
            names = []
            if self.marshmallow_plugin:
                for sch in schema:
                    schema_instance = resolve_schema_instance(sch)
                    name = self._find_schema(schema_instance)
                    if name is None:
                        name = get_unique_schema_name(
                            self.spec.components,
                            type(schema_instance).__name__,
                        )
                        self.spec.components.schema(
                            name, schema=schema_instance
                        )
                    names.append(name)
            deep_update(
                res["requestBody"]["content"],
                {
                    "application/json": {
                        "schema": {
                            "oneOf": [
                                {"$ref": f"#/components/schemas/{name}"}
                                for name in names
                            ]
                        }
                    }
                },
            )
        elif isinstance(schema, type) or isinstance(schema, Schema):
            schema_instance = resolve_schema_instance(schema)
            if self.marshmallow_plugin:
                name = self._find_schema(schema_instance)
                if name is None:
                    name = get_unique_schema_name(
                        self.spec.components, type(schema_instance).__name__
                    )
                    self.spec.components.schema(name, schema=schema_instance)
                if isinstance(schema, Schema) and schema.many:
                    deep_update(
                        res["requestBody"]["content"],
                        {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": f"#/components/schemas/{name}"
                                    },
                                }
                            }
                        },
                    )
                else:
                    deep_update(
                        res["requestBody"]["content"],
                        {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{name}"
                                }
                            }
                        },
                    )
        return res

    def apispec_responses2openapi(self, func) -> dict:
        """Extract operation responses openAPI spec from function decorators.

        It extract spec from `func.__apispec__['responses']`.

        :param func: operation function (get, put, post, etc.)
        :return: operation openAPI spec
        """
        if not hasattr(func, "__apispec__"):
            return {}
        apispec_attr: dict = func.__apispec__
        if "responses" not in apispec_attr:
            return {}

        res = {}
        res["responses"] = {}
        for status, response in apispec_attr.get("responses", {}).items():
            res["responses"][str(status)] = {
                "description": response.get("description", ""),
                "content": response.get("content", {}),
            }
            schema = response.get("schema", None)
            if isinstance(schema, str):
                deep_update(
                    res["responses"][str(status)]["content"],
                    {"application/json": {"schema": {"$ref": schema}}},
                )
            elif isinstance(schema, list):
                names = []
                if self.marshmallow_plugin:
                    for sch in schema:
                        schema_instance = resolve_schema_instance(sch)
                        name = self._find_schema(schema_instance)
                        if name is None:
                            name = get_unique_schema_name(
                                self.spec.components,
                                type(schema_instance).__name__,
                            )
                            self.spec.components.schema(
                                name, schema=schema_instance
                            )
                        names.append(name)
                deep_update(
                    res["responses"][str(status)]["content"],
                    {
                        "application/json": {
                            "schema": {
                                "oneOf": [
                                    {"$ref": f"#/components/schemas/{name}"}
                                    for name in names
                                ]
                            }
                        }
                    },
                )
            elif isinstance(schema, type) or isinstance(schema, Schema):
                schema_instance = resolve_schema_instance(schema)
                if self.marshmallow_plugin:
                    name = self._find_schema(schema_instance)
                    if name is None:
                        name = get_unique_schema_name(
                            self.spec.components,
                            type(schema_instance).__name__,
                        )
                        self.spec.components.schema(
                            name, schema=schema_instance
                        )
                    if isinstance(schema, Schema) and schema.many:
                        deep_update(
                            res["responses"][str(status)]["content"],
                            {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": (
                                                f"#/components/schemas/{name}"
                                            )
                                        },
                                    }
                                }
                            },
                        )
                    else:
                        deep_update(
                            res["responses"][str(status)]["content"],
                            {
                                "application/json": {
                                    "schema": {
                                        "$ref": f"#/components/schemas/{name}"
                                    }
                                }
                            },
                        )

        return res


def extract_openapi(namespace: str | None = None) -> APISpec:
    logging.info("Extract openAPI specification")
    spec_path = importlib.resources.files(
        "deseasion.backend.openapi"
    ).joinpath("spec_geo_json.yml")
    with spec_path.open("r") as f:
        geo_json_spec = yaml.safe_load(f)

    ma_plugin = MyMarshmallowPlugin()
    plugins = [ma_plugin, FlaskRestfulPlugin()]
    spec = APISpec(
        "DESEASION API",
        "2.0.2",
        "3.0.2",
        servers=[
            {
                "url": "/api",
                "description": "Production Server (behind reverse-proxy)",
            },
            {
                "url": "/",
                "description": (
                    "Test Server (backend only without reverse proxy)"
                ),
            },
        ],
        components=geo_json_spec.get("components", {}),
        plugins=plugins,
    )
    ma_plugin.converter.add_attribute_function(enum_fields2properties)
    ma_plugin.converter.add_attribute_function(method_fields2properties)

    schema_classes = get_schemas_classes(namespace)
    ma_plugin.schema_names = {klass: k for k, klass in schema_classes.items()}

    for k, klass in schema_classes.items():
        schema_instance = resolve_schema_instance(klass)
        schema_key = make_schema_key(schema_instance)
        if schema_key not in ma_plugin.converter.refs:
            spec.components.schema(
                get_unique_schema_name(spec.components, k), schema=klass
            )
    logging.debug(
        f"Schemas added:{len(spec.components.schemas)} found: "
        f"{len(schema_classes)}"
    )

    spec.components.security_scheme(
        "bearerAuth",
        {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
    )
    spec.components.security_scheme(
        "basicAuth",
        {
            "type": "http",
            "scheme": "basic",
            "description": "Provide access token",
        },
    )
    spec.components.security_scheme(
        "refreshAuth",
        {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Provide refresh token",
        },
    )

    for klass, _, _ in api.resources:
        spec.path(resource=klass, api=api)

    return spec


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    spec = extract_openapi()
    print(spec.to_yaml())
