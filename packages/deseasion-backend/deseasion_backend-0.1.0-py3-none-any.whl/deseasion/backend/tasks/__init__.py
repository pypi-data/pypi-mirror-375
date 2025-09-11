from datetime import datetime

from celery import Task, shared_task, states
from celery.result import AsyncResult
from celery.signals import (
    task_failure,
    task_postrun,
    task_prerun,
    task_revoked,
)

from ..exceptions import ProcessingError
from ..models import (
    DataStream,
    GeoDataType,
    ProcessingModel,
    ProjectTaskModel,
    ProjectTaskType,
    db,
)
from ..models.geo_data_utils import ModelProcessingService
from ..services.geo_data_loading_service import load_from_wfs, load_from_wms


class ContextTask(Task):
    app_context = None

    def __call__(self, *args, **kwargs):
        with self.app_context:
            return self.run(*args, **kwargs)


class ProgressFeedback:
    def __init__(self, task):
        self._task = task
        self.message = None

    def set_progress(self, count, total):
        progress = int(100 * count / total)
        self._task.update_state(
            state=states.STARTED,
            meta={"progress": progress, "message": self.message},
        )

    def set_message(self, message):
        self.message = message
        self._task.update_state(
            state=states.STARTED, meta={"message": message}
        )

    def forget_message(self):
        self.message = None
        self._task.update_state(state=states.STARTED, meta={"message": None})


@shared_task(name=ProjectTaskType.process_project_data.name, bind=True)
def process_and_set_model(self, *, model_id):
    """Process the model and save the new data."""
    model = ProcessingModel.get_by_id(model_id)
    processing_service = ModelProcessingService()
    feedback = ProgressFeedback(self)
    with db.session.no_autoflush:
        features = processing_service.process_model(model, feedback=feedback)
        processing_service.set_project_data_features(
            model.data_generator, features
        )


@shared_task(name=ProjectTaskType.update_stream.name, bind=True)
def update_stream_data(
    *args,
    data_id,
):
    """Update the DataStream data field."""
    data_stream = DataStream.get_by_id(data_id)
    processing_service = ModelProcessingService()
    stream = data_stream.stream
    with db.session.no_autoflush:
        if stream.type == GeoDataType.wfs:
            attributes = (
                data_stream.data.attributes if data_stream.data else None
            )
            features = load_from_wfs(stream, attributes)
        else:
            attribute = None
            if data_stream.data and len(data_stream.data.attributes) == 1:
                attribute = data_stream.data.attributes[0]
            features = load_from_wms(
                stream,
                classes=data_stream.classes,
                start=data_stream.start,
                step=data_stream.step,
                stop=data_stream.stop,
                resolution=data_stream.resolution,
                old_attribute=attribute,
            )
        # Keep features with only None values (it's an input, we keep it as is)
        processing_service.set_project_data_features(
            data_stream, features, filter_none=False
        )


@task_prerun.connect
def project_task_prerun(task_id, task, args, kwargs, **kw):
    """Prerun signal for the tasks."""
    try:
        task_type = ProjectTaskType[task.name]
    except KeyError:
        return
    time = datetime.utcnow()
    with task.app_context:
        project = None
        if task_type == ProjectTaskType.process_project_data:
            model_id = kwargs["model_id"]
            model = ProcessingModel.get_by_id(model_id)
            project = model.data_generator.project
        elif task_type == ProjectTaskType.update_stream:
            data_stream_id = kwargs["data_id"]
            data_stream = DataStream.get_by_id(data_stream_id)
            project = data_stream.project
        if project is not None:
            task_model = ProjectTaskModel(
                task_id=task_id, project=project, started_at=time
            )
            task_model.type = task_type
            task_model.params = kwargs
            task_model.state = states.STARTED
            task_model.create()
    print("task {} ({}) started at {}".format(task.name, task_id, time))


@task_postrun.connect
def project_task_postrun(task_id, task, args, kwargs, retval, state, **kw):
    """Postrun signal for the tasks

    If the task name is 'process_project_data', the final status and finish
    time is saved to the database.
    """
    if state is None:
        result = AsyncResult(task_id)
        state = result.state
    time = datetime.utcnow()
    with task.app_context:  # use the flask application context
        task_model = ProjectTaskModel.get_by_task_id(task_id)
        if task_model is not None:
            task_model.finished_at = time
            task_model.state = state
            task_model.update()
    print(
        "task {} ({}) finishing with state {} at {}".format(
            task.name, task_id, state, time
        )
    )


@task_failure.connect
def project_task_failure(
    task_id, exception, args, kwargs, traceback, einfo, **kw
):
    """Save the 'FAILED' state and the error message when a task fails"""
    if isinstance(exception, ProcessingError):
        with process_and_set_model.app_context:
            task_model = ProjectTaskModel.get_by_task_id(task_id)
            if task_model is not None:
                task_model.error_message = str(exception)
                task_model.finished_at = datetime.utcnow()
                task_model.update()


@task_revoked.connect
def project_task_revoked(request, terminated, signum, expired, **wk):
    """Save the 'REVOKED' state and the time when a task is revoked"""
    with request.task.app_context:
        task_model = ProjectTaskModel.get_by_task_id(request.task_id)
        if task_model is not None:
            task_model.finished_at = datetime.utcnow()
            task_model.state = states.REVOKED
            task_model.update()
