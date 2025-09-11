from importlib import resources

from flask import Flask
from flask_migrate import Migrate

from ..models import db

migrate = Migrate()


def init_app(app: Flask):
    """Create the migrate group of commands."""
    with resources.path("deseasion.backend", "migrations") as migrations_path:
        migrate.init_app(app, db, str(migrations_path))
