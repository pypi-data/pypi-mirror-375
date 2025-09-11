import logging
import os

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import default_exceptions
from werkzeug.middleware.profiler import ProfilerMiddleware

from .exceptions import RequestError
from .models import db
from .resources import api
from .security import jwt_handler


def create_app(instance_config_file=None) -> Flask:
    instance_path = os.path.abspath(os.getcwd())
    app = Flask(
        __name__,
        instance_relative_config=True,
        instance_path=instance_path,
        static_folder=None,
    )

    handler = logging.StreamHandler()
    handler.setLevel(logging.WARNING)
    app.logger.addHandler(handler)

    app.config.from_object("deseasion.backend.config")
    if instance_config_file:
        app.config.from_pyfile(instance_config_file, silent=True)

    if app.config.get("PROFILE", False):
        app.wsgi_app = ProfilerMiddleware(
            app.wsgi_app, profile_dir=app.config["PROFILE_DIR"]
        )

    db.init_app(app)
    api.init_app(app)
    jwt_handler.init_app(app)

    @app.errorhandler(RequestError)
    def handler_request_error(error):
        app.logger.info("Request error: {}".format(str(error)), exc_info=True)
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(ValidationError)
    def handler_validation_error(error):
        app.logger.info(
            "Validation error: {}".format(str(error)), exc_info=True
        )
        response = jsonify(
            {"message": "Validation error", "errors": error.messages}
        )
        response.status_code = 400
        return response

    def handler_http_exception(error):
        response = jsonify({"message": error.description, "error": str(error)})
        response.status_code = error.code
        return response

    # trap the default http exceptions (HTTPException subclasses)
    # https://github.com/pallets/flask/issues/941
    for code in default_exceptions:
        app.register_error_handler(code, handler_http_exception)

    @app.errorhandler(Exception)
    def handler_exception(error):
        app.logger.warning("Unhandled exception:", exc_info=True)
        response = jsonify({"message": "Internal Server Error"})
        response.status_code = 500
        return response

    return app
