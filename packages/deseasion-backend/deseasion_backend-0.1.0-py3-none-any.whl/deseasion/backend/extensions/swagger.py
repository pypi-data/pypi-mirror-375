from flasgger import Swagger
from flask import Flask

swagger = Swagger()


def init_app(app: Flask):
    """Extract OpenAPI specification and create swagger"""
    from ..openapi.extract_specification import extract_openapi

    spec = extract_openapi()
    swagger.template = spec.to_dict()
    swagger.init_app(app)
