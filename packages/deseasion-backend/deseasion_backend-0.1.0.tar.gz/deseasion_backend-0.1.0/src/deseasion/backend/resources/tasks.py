from celery.result import AsyncResult
from flask import jsonify
from flask_restful import Resource, reqparse

from ..exceptions import RequestError
from ..models import ProjectTaskModel
from ..schemas import (
    MessageSchema,
    ProjectTaskListGetResponseSchema,
    ProjectTaskSchema,
    TaskGetResponseSchema,
)
from ..services import project_service
from ..services.auth_service import token_required
from .utils import check_permission, dump_data, with_query_arg, with_response


class ProjectTaskListAPI(Resource):
    def get_tasks_list_schemas(self, project_id, limit=None, offset=None):
        """Returns the list of tasks concerning the data of a project"""
        task_models = project_service.get_project_tasks(
            project_id, limit=limit, offset=offset
        )
        schema = ProjectTaskSchema(many=True)
        data = {
            "tasks": schema.dump(task_models),
            "total": project_service.get_total_project_tasks(project_id),
        }
        return jsonify(**data)

    @token_required
    @with_response(
        200,
        schema=ProjectTaskListGetResponseSchema,
        description="List of project tasks",
    )
    @with_query_arg(
        "limit",
        int,
        required=False,
        description="Maximum number of tasks to return. Default: all",
    )
    @with_query_arg(
        "offset",
        int,
        required=False,
        description="Number of tasks to skip. Default: None",
    )
    def get(self, project_id):
        """
        Return the list of tasks for the project

        :param int project_id: The id of the project.
        :query int limit: Number of tasks to return.
        :query int offset:
            Number of tasks to skip (e.g., a value of ``25`` means the first 25
            tasks will not be returned).
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Get the list of tasks in a project
        """
        project_service.get_if_authorized(project_id)
        parser = reqparse.RequestParser()
        parser.add_argument("limit", type=int, location="args")
        parser.add_argument("offset", type=int, location="args")
        args = parser.parse_args()
        limit = args.get("limit", None)
        offset = args.get("offset", None)
        return self.get_tasks_list_schemas(
            project_id, limit=limit, offset=offset
        )


class TaskAPI(Resource):
    @token_required
    @with_response(
        200, schema=TaskGetResponseSchema, description="Details of the task"
    )
    def get(self, task_id):
        """
        Return the details of the task.

        :param int task_id: The id of the task.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access the project for this task.
        :status 404: The task doesn't exist.

        .. :quickref: Task; Get the details of the task
        """
        task = ProjectTaskModel.get_by_task_id(task_id)
        if task is None:
            raise RequestError("Task not found", 404)
        check_permission(task.project)
        return dump_data(ProjectTaskSchema(), task=task)

    @token_required
    @with_response(
        200, schema=MessageSchema, description="Task revoked successfully"
    )
    def delete(self, task_id):
        """
        Revoke the task.

        :param int task_id: The id of the task.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access the project for this task.
        :status 404: The task doesn't exist.

        .. :quickref: Task; Revoke the task
        """
        task = ProjectTaskModel.get_by_task_id(task_id)
        if task is None:
            raise RequestError(f"Task {task_id} does not exist", 404)
        check_permission(task.project)
        result = AsyncResult(task_id)
        result.revoke(terminate=True)
        return jsonify(message="task {} deleted".format(task_id))
