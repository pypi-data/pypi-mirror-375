import enum

from celery import states
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import backref

from . import db
from .mixins import ModelMixin


class ProjectTaskType(enum.Enum):
    process_project_data = 1
    update_stream = 2


class ProjectTaskModel(ModelMixin, db.Model):
    """Save the details of a celery task.

    Attributes:
        task_id (str): The id of the Celery task.
        started_at (datetime): When the task was started.
        finished_at (datetime): When the task was finished.
        state:
            The state of the task ('PENDING', 'STARTED', 'FAILED' or 'REVOKED')
        error_message (str): A description of the error if the task failed.
        type:
            The type of task
            ('process_project_data' or 'update_stream').
        params: The arguments used for the task.
        project_id: The id of the project in which this task is executed.
    """

    __tablename__ = "project_task"

    task_id = db.Column(db.String)
    started_at = db.Column(db.DateTime)
    finished_at = db.Column(db.DateTime)
    state = db.Column(db.String)
    error_message = db.Column(db.String)
    type = db.Column(db.Enum(ProjectTaskType))
    params = db.Column(JSONB)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )

    # lazy loading for cascading the deletion of the project and zone
    # proposition
    project = db.relationship(
        "Project",
        backref=backref(
            "project_tasks", lazy="select", cascade="delete,delete-orphan"
        ),
    )

    def __init__(
        self, task_id, project=None, started_at=None, finished_at=None
    ):
        self.task_id = task_id
        self.project = project
        self.started_at = started_at
        self.finished_at = finished_at
        self.state = states.PENDING

    @classmethod
    def get_by_task_id(cls, task_id):
        """Returns the first task in the database with the given task id"""
        return cls.query.filter_by(task_id=task_id).first()
