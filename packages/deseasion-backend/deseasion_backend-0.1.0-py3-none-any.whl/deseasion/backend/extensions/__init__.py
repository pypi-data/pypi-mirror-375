from flask import Flask

from . import celery as celery_ext
from . import migrate as migrate_ext
from . import swagger as swagger_ext


def init_app(app: Flask):
    swagger_ext.init_app(app)
    celery_ext.init_app(app)
    migrate_ext.init_app(app)
