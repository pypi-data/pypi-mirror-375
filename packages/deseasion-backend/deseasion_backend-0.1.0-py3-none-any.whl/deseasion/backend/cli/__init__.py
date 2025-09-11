from flask import Flask


def init_app(app: Flask):
    from .db import register_commands as register_db_commands
    from .user import user_cli

    app.cli.add_command(user_cli)
    register_db_commands(app)
