from . import create_app
from .cli import init_app as init_cli
from .extensions import init_app as init_extensions

# Following is necessary for worker to be launched with
# celery -A deseasion.backend.app.celery worker
from .extensions.celery import celery  # noqa: F401

app = create_app("instance/config.py")
init_extensions(app)
init_cli(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
