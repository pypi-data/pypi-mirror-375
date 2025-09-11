from celery import Celery
from flask import Flask

from ..tasks import ContextTask

celery = Celery()


def init_app(app: Flask):
    celery.main = app.import_name
    celery.conf.result_backend = app.config["CELERY_RESULT_BACKEND"]
    celery.conf.broker_url = app.config["CELERY_BROKER_URL"]
    celery.conf.update(app.config)

    ContextTask.app_context = app.app_context()
    celery.Task = ContextTask
