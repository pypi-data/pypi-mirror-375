import importlib.resources as pkg_resources

import click
from alembic import command
from alembic.migration import MigrationContext
from flask import Flask
from sqlalchemy.sql import text

from .. import sql
from ..models import db


def register_commands(app: Flask):
    db_cli_group = app.cli.commands["db"]

    @db_cli_group.command()
    @click.option(
        "-d",
        "--directory",
        default=None,
        help=('Migration script directory (default is "migrations")'),
    )
    @click.option(
        "--tag",
        default=None,
        help=(
            'Arbitrary "tag" name - can be used by custom env.py ' "scripts"
        ),
    )
    @click.option(
        "-f",
        "--force",
        default=False,
        is_flag=True,
        help="Force database initialization (even if already initialized)",
    )
    @click.option(
        "-x",
        "--x-arg",
        multiple=True,
        help="Additional arguments consumed by custom env.py scripts",
    )
    def create(directory, tag, force, x_arg):
        """Creates all the SQLAlchemy tables and add SQL functions."""

        config = app.extensions["migrate"].migrate.get_config(
            directory, x_arg=x_arg
        )

        engine = db.get_engine()
        with engine.connect() as conn:
            migration_ctx = MigrationContext.configure(conn)
            current = migration_ctx.get_current_revision()

        if current is None or force:
            db.create_all()
            with (
                pkg_resources.files(sql)
                .joinpath("dissolve_adjacent.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            with (
                pkg_resources.files(sql)
                .joinpath("tile_bbox.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            with (
                pkg_resources.files(sql)
                .joinpath("trigger_feature_make_valid.sql")
                .open("r") as f
            ):
                db.session.execute(text(f.read()))
            db.session.commit()
            command.stamp(config, revision="head", tag=tag)
        else:
            print(
                "Database already exists. You may force its creation "
                "with '--force' option (may break database).\n"
                "If wanting to upgrade it, use 'flask db upgrade' command "
                "instead."
            )

    @db_cli_group.command()
    @click.option(
        "-d",
        "--directory",
        default=None,
        help=('Migration script directory (default is "migrations")'),
    )
    @click.option(
        "-x",
        "--x-arg",
        multiple=True,
        help="Additional arguments consumed by custom env.py scripts",
    )
    def drop(directory, x_arg):
        """Drops all the SQLAlchemy tables."""

        config = app.extensions["migrate"].migrate.get_config(
            directory, x_arg=x_arg
        )

        if input("Your data will be lost. Continue? (Y/y): ")[0] in ["Y", "y"]:
            db.drop_all()
            command.stamp(config, revision=None)
