from celery import chain, group
from flask import current_app as app
from flask import jsonify
from flask_restful import Resource, reqparse
from flask_restful.inputs import boolean

from ..exceptions import InferenceError, RequestError
from ..models import DataAttribute, DataType, MRSort, ProjectTaskModel, db
from ..models.project_data_utils import ProjectDataProcessingService
from ..schemas import (
    DataGeneratorSchema,
    DataGeoSchema,
    DataStreamSchema,
    MessageSchema,
    MRSortInferenceGetResponseSchema,
    MRSortInferenceSchema,
    ProcessingModelSchema,
    ProjectDataActiveModelPutResponseSchema,
    ProjectDataGetResponseSchema,
    ProjectDataListGetResponseSchema,
    ProjectDataModelChangePostRequestBodySchema,
    ProjectDataPostResponseSchema,
    ProjectDataReplaceInputsPostRequestBodySchema,
    ProjectDataSchema,
    ProjectGlobalDataSchema,
    ProjectSharedDataListGetResponseSchema,
    ProjectTaskSchema,
)
from ..services import processing_model_service, project_data_service
from ..services.auth_service import token_required
from .utils import (
    dump_data,
    get_json_content,
    with_query_arg,
    with_request_body,
    with_response,
)


class ProjectDataListAPI(Resource):
    def parse_ids(self, args):
        """Returns the list of integer ids parsed from the comma-separated
        query arguments"""
        ids_str = args.get("ids", None)
        try:
            ids = (
                [
                    int(data_id)
                    for data_id in ids_str.split(",")
                    if len(data_id) > 0
                ]
                if ids_str is not None
                else []
            )
        except ValueError:
            raise RequestError(
                "The ids must be integers separated by a comma", 400
            )
        if len(ids) == 0:
            raise RequestError("A list of the ids is required", 400)
        return ids

    def parse_fields(self, args):
        """Returns the list of string fields parsed from the comma-separated
        query arguments"""
        fields_str = args.get("fields", None)
        fields = fields_str.split(",") if fields_str is not None else None
        return fields

    @token_required
    @with_query_arg(
        "fields",
        schema={"type": "array", "items": {"type": "string"}},
        required=False,
        description="The list of project data fields to return. Default: all.",
        style="form",
        explode=False,
    )
    @with_query_arg(
        "ids",
        schema={"type": "array", "items": {"type": "integer"}},
        description="The list of project data ids",
        style="form",
        explode=False,
    )
    @with_response(
        200,
        ProjectDataListGetResponseSchema,
        description="List of project data with wanted fields",
    )
    def get(self):
        """
        Returns the list of project data

        :query ids: The list of comma separated data ids (**required**).
        :query fields:
            The list of fields to return. Default: Return all fields.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403:
            The user is not allowed to access at least one project data.
        :status 404: At least one project data does not exist.

        .. :quickref: Project data; Get the list of project data
        """
        parser = reqparse.RequestParser()
        parser.add_argument("ids", type=str, location="args")
        parser.add_argument("fields", type=str, location="args")
        args = parser.parse_args()
        ids = self.parse_ids(args)
        fields = self.parse_fields(args)
        data_list = [
            project_data_service.get_if_authorized(data_id) for data_id in ids
        ]
        serialized = []
        for data in data_list:
            data_dict = ProjectDataSchema().dump(data)
            if fields is not None:
                data_dict = {k: v for k, v in data_dict.items() if k in fields}
            serialized.append(data_dict)
        return jsonify(project_data=serialized)


class ProjectDataAPI(Resource):
    def create_process_task(self, data_id):
        """Create the appropriate type of task to process data"""
        data = project_data_service.get_if_authorized(data_id)
        if data.data_type == DataType.data_stream:
            return processing_model_service.update_stream_process(data.id)
        else:
            return processing_model_service.task_process(
                data.processing_model.id
            )

    def get_chained_tasks(self, data):
        """Start the celery tasks"""
        data_id_groups = project_data_service.get_grouped_dependant_data_ids(
            data
        )
        tasks = []
        for data_id_group in data_id_groups:
            # TODO: Group process of data
            if len(data_id_group) == 1:
                tasks.append(self.create_process_task(data_id_group[0]))
            elif len(data_id_group) > 1:
                grouped = [
                    self.create_process_task(data_id)
                    for data_id in data_id_group
                ]
                tasks.append(group(*grouped))
        if len(tasks) == 1:
            task = tasks[0]
            app.logger.info("starting task: {}".format(task))
            return task
        elif len(tasks) > 1:
            chain_signature = chain(*tasks)
            app.logger.info(
                "starting chain of tasks: {}".format(chain_signature)
            )
            return chain_signature

    def process_data(self, data_id, chain=False):
        """Process the data in an asynchronous task

        Args:
            data_id (int): the id of the data to process
            chain (bool):
                also process the required dependencies (default: False)
        """
        # TODO: Repair chained processing
        data = project_data_service.get_if_authorized(data_id)
        if chain:
            task_s = self.get_chained_tasks(data)
        else:
            task_s = self.create_process_task(data.id)
        task = task_s.apply_async(countdown=1)
        # Temporary object which is not persisted
        # to send the task_id to the user
        temporary_task = ProjectTaskModel(
            task_id=task.id, project=data.project
        )
        return dump_data(ProjectTaskSchema(), task=temporary_task)

    @token_required
    @with_response(
        202,
        schema=ProjectDataPostResponseSchema,
        description="Details of the newly created asynchronously running task",
    )
    @with_query_arg(
        "chain",
        bool,
        required=False,
        description="Also process the required dependencies. Default: False.",
    )
    @with_query_arg(
        "action",
        str,
        description=(
            "Action to execute on the data: currently only 'process' is "
            "supported."
        ),
    )
    def post(self, data_id):
        """
        Process the project's data.

        :param int data_id: The id of the project's data.
        :query str action:
            Action to execute on the data: currently only ``process`` is
            supported (**required**).
        :query bool chain:
            Also process the required dependencies. Default: False.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 202:
            The data is being processed asynchronously.
            The detail of the running task is returned.
        :status 400: The ``action`` is incorrect.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Process the project's data
        """
        parser = reqparse.RequestParser()
        parser.add_argument("action", type=str, location="args", required=True)
        parser.add_argument(
            "chain", type=boolean, location="args", default=False
        )
        args = parser.parse_args()
        if args.get("action") == "process":
            chain = args.get("chain")
            resp = self.process_data(data_id, chain)
            resp.status_code = 202
            return resp
        else:
            raise RequestError("Unknown action")

    @token_required
    @with_response(
        200,
        schema=ProjectDataGetResponseSchema,
        description="Details of the project data",
    )
    def get(self, data_id):
        """
        Return the details of the project's data.

        The schema used to serialize the data will depend on the data_type
        attribute.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Get the details of the project's data
        """
        data = project_data_service.get_if_authorized(data_id)
        return dump_data(ProjectDataSchema(), project_data=data)

    @token_required
    @with_response(
        200,
        schema=MessageSchema,
        description="Project data successfully deleted",
    )
    def delete(self, data_id):
        """
        Delete the project's data.

        :param int data_id: The id the project's data.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Delete the project's data
        """
        project_data = project_data_service.get_if_authorized(data_id)
        project_data.delete()
        return jsonify(message="Data {} deleted".format(data_id))

    @token_required
    @with_response(
        status=200,
        schema=ProjectDataGetResponseSchema,
        description="Updated details of the project data",
    )
    @with_request_body(
        ProjectDataSchema, description="New project data details"
    )
    def put(self, data_id):
        """
        Modify the project's data.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: There is an error in the json data.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Modify the project's data
        """
        project_data = project_data_service.get_if_authorized(data_id)
        content = get_json_content()
        ps = ProjectDataProcessingService()
        input_data = content.pop("input_data", None)
        output_data = content.pop("output_data", None)
        if input_data is not None or output_data is not None:
            data_graph = ps.get_project_data_graph(project_data.project)
            new_output_data = []
            if input_data is not None:
                data_graph[project_data] = [
                    project_data_service.get_if_authorized(pdata_id)
                    for pdata_id in input_data
                ]
            if output_data is not None:
                deleted_outputs = []
                for pdata in project_data.output_data:
                    if pdata.id not in output_data:
                        deleted_outputs.append(pdata.id)
                        data_graph[pdata].remove(project_data)
                for pdata_id in output_data:
                    pdata = project_data_service.get_if_authorized(pdata_id)
                    if pdata not in project_data.output_data:
                        data_graph[pdata].append(project_data)
                    new_output_data.append(pdata)

            # Need to make graph with ids otherwise topological sort will
            # create new ProjectData when cloning the dictionary
            graph = {
                p.id: [idata.id for idata in inputs]
                for p, inputs in data_graph.items()
            }
            try:
                ps._topological_sort(graph)
            except TypeError:
                raise RequestError(
                    (
                        "change of data inputs create cycles in project data "
                        "graph"
                    ),
                    400,
                )

            if input_data is not None:
                prev_inputs = project_data.input_data
                project_data.input_data = []
                try:
                    for pdata in data_graph[project_data]:
                        project_data.add_input(pdata)
                except (TypeError, ValueError) as exc:
                    raise RequestError(str(exc), 400)

                # Detach cleanly old input data
                ps.detach_input(
                    project_data,
                    set(prev_inputs) - set(project_data.input_data),
                )
            if output_data is not None:
                prev_outputs = project_data.output_data
                project_data.output_data = []
                try:
                    for pdata in new_output_data:
                        pdata.add_input(project_data)
                except (TypeError, ValueError) as exc:
                    raise RequestError(str(exc), 400)

                for pdata in set(prev_outputs) | set(project_data.output_data):
                    if pdata not in project_data.output_data:
                        # Detach cleanly old output data
                        ps.detach_input(pdata, [project_data])
                    pdata.on_modification()
                    db.session.add(pdata)

        new_name = content.pop("name", project_data.name)
        if new_name != project_data.name:
            ps.rename_data(project_data, new_name)

        sch = ProjectDataSchema.type_schemas[project_data.data_type.name]()
        try:
            with db.session.no_autoflush:
                data = sch.load(content, instance=project_data)
        except NameError as error:
            raise RequestError(str(error), 400)
        if len(content) > 0 or input_data is not None:
            data.on_modification()
        db.session.commit()
        return dump_data(sch, project_data=data)


class ProjectDataActiveModelAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=ProjectDataActiveModelPutResponseSchema,
        description="Updated active model of project data",
    )
    @with_request_body(
        schema=ProcessingModelSchema, description="New active model details"
    )
    def put(self, data_id):
        """
        Update the active processing model of the data.

        The type of processing model cannot be modified.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Modify the active processing model of the project data
        """  # noqa: E501
        project_data = project_data_service.get_if_authorized(data_id)
        content = get_json_content()
        model = project_data.processing_model
        schema = ProcessingModelSchema.type_schemas[model.model_type.name]
        schema = schema()
        model = schema.load(content, instance=model)
        model.update()
        project_data.update()
        return dump_data(schema, processing_model=model)


class ProjectDataModelAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=ProjectDataActiveModelPutResponseSchema,
        description="Updated model of project data",
    )
    @with_request_body(
        schema=ProcessingModelSchema, description="New model details"
    )
    def put(self, data_id, model_id):
        """
        Update the processing model of the data.

        The type of processing model cannot be modified.

        :param int data_id: The id the project's data.
        :param int model_id: The id the processing model.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404:
            Either the project data or processing model does not exist.

        .. :quickref: Project data; Modify the processing model of the project data
        """  # noqa: E501
        project_data = project_data_service.get_if_authorized(data_id)
        models_list = project_data._processing_models
        for model in models_list:
            if model.id == model_id:
                break
        else:
            raise RequestError(
                "The processing model does not exist in this project data", 404
            )
        content = get_json_content()
        schema = ProcessingModelSchema.type_schemas[model.model_type.name]
        schema = schema()
        model = schema.load(content, instance=model)
        model.update()
        project_data.update()
        return dump_data(schema, processing_model=model)

    @token_required
    @with_response(
        200,
        schema=MessageSchema,
        description="Preference model deleted successfully",
    )
    def delete(self, data_id, model_id):
        """
        Delete the processing model of the data.

        :param int data_id: The id the project's data.
        :param int model_id: The id the processing model.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400:
            The processing model is the only one for the data so cannot be
            deleted.
        :status 403: The user is not allowed to access the project.
        :status 404:
            Either the project data or processing model does not exist.

        .. :quickref: Project data; Delete the processing model of the project data
        """  # noqa: E501
        project_data = project_data_service.get_if_authorized(data_id)
        models_list = project_data._processing_models
        for i, model in enumerate(models_list):
            if model.id == model_id:
                break
        else:
            raise RequestError(
                "The processing model does not exist in this project data", 404
            )
        if len(models_list) == 1:
            raise RequestError(
                "The model cannot be deleted as it is the only model in the "
                "project data"
            )
        if model is project_data.processing_model:
            if i < len(models_list) - 1:
                project_data.processing_model = models_list[i + 1]
            else:
                project_data.processing_model = models_list[i - 1]
        model.delete()
        return jsonify(message="Model {} deleted".format(model_id))


class ProjectDataModelChangeAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=ProjectDataActiveModelPutResponseSchema,
        description="Details of the project data active model",
    )
    @with_request_body(
        ProjectDataModelChangePostRequestBodySchema,
        description="Id of the processing model to set as the active model",
    )
    def post(self, data_id):
        """Change the active processing model.

        :param int data_id: The id of the project's data.
        :resjson int id: Id of the processing model to set as the active model.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allower to access the project.
        :status 404: The project data or processing model does not exist.
        :status 400: The content is incorrect.

        .. :quickref: Project data; Change the processing model of the project data.
        """  # noqa: E501
        project_data = project_data_service.get_if_authorized(data_id)
        content = get_json_content()
        try:
            model_id = content.pop("id")
        except KeyError:
            raise RequestError("No processing_model id found")
        if len(content) > 0:
            raise RequestError(
                "The post data should only contain the model id"
            )
        for model in project_data._processing_models:
            if model.id == model_id:
                break
        else:
            raise RequestError(
                "The processing model does not exist for this project data",
                404,
            )
        project_data._processing_model = model
        project_data.update()
        schema = ProcessingModelSchema.type_schemas[model.model_type.name]
        schema = schema()
        return dump_data(schema, processing_model=model)


class ProjectDataInputSubgraphAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectSharedDataListGetResponseSchema,
        description="Project data input subgraph",
    )
    def get(self, data_id):
        """
        Return the input data subgraph spanning from the project data.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project data.
        :status 404: The project data doesn't exist.

        .. :quickref: Project data; Get the project data input subgraph
        """
        project_data = project_data_service.get_if_authorized(data_id)
        ps = ProjectDataProcessingService()
        graph = ps.get_input_graph(project_data)

        dump_schemas = {
            DataType.geo_data: DataGeoSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.generator: DataGeneratorSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "processing_model",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.global_data: ProjectGlobalDataSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.data_stream: DataStreamSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                    "stream",
                )
            ),
        }
        res = []
        for projdata in graph:
            res.append(dump_schemas[projdata.data_type].dump(projdata))
        return {"data_list": res}


class ProjectDataOutputSubgraphAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectSharedDataListGetResponseSchema,
        description="Project data output subgraph",
    )
    def get(self, data_id):
        """
        Return the output data subgraph spanning from the project data.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project data.
        :status 404: The project data doesn't exist.

        .. :quickref: Project data; Get the project data output subgraph
        """
        project_data = project_data_service.get_if_authorized(data_id)
        ps = ProjectDataProcessingService()
        graph = ps.get_output_graph(project_data)

        dump_schemas = {
            DataType.geo_data: DataGeoSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.generator: DataGeneratorSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "processing_model",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.global_data: ProjectGlobalDataSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                )
            ),
            DataType.data_stream: DataStreamSchema(
                only=(
                    "name",
                    "id",
                    "data",
                    "data_type",
                    "is_outdated",
                    "input_data",
                    "output_data",
                    "stream",
                )
            ),
        }
        res = []
        for projdata in graph:
            res.append(dump_schemas[projdata.data_type].dump(projdata))
        return {"data_list": res}


class ProjectDataReplaceInputAttributesAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectDataGetResponseSchema,
        description="Details of the project data",
    )
    @with_request_body(schema=ProjectDataReplaceInputsPostRequestBodySchema)
    def post(self, data_id):
        """Replace project data input attributes.

        It replaces usage of old attributes given by new attributes given,
        assuming the old attributes given are attributes of this project's data
        and that the new attributes given are not already used as inputs
        alongside some of the old attributes.

        Its main usage is threfore to replace whole project data
        (all their attributes) by completely unused other project data.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: Remapping could not proceed with given arguments.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: Project data; Replace project data input attributes
        """
        data = project_data_service.get_if_authorized(data_id)
        content = get_json_content()
        args = ProjectDataReplaceInputsPostRequestBodySchema().load(content)

        attributes_mapping = {}
        for item in args["attributes_mapping"]:
            old_attr_id = item["old_attribute"]
            new_attr_id = item["new_attribute"]
            old_attr = DataAttribute.get_by_id(old_attr_id)
            new_attr = DataAttribute.get_by_id(new_attr_id)
            if old_attr is None or new_attr is None:
                raise RequestError("attributes mapping is invalid", 400)
            attributes_mapping[old_attr] = new_attr
        try:
            ProjectDataProcessingService().replace_input_attributes(
                data, attributes_mapping
            )
        except (ValueError, TypeError) as exc:
            raise RequestError(str(exc), 400)

        ps = ProjectDataProcessingService()
        data_graph = ps.get_project_data_graph(data.project)
        # Need to make graph with ids otherwise topological sort will create
        # new ProjectData when cloning the dictionary
        graph = {
            p.id: [idata.id for idata in inputs]
            for p, inputs in data_graph.items()
        }
        try:
            ps._topological_sort(graph)
        except TypeError:
            raise RequestError(
                "new data input creates cycles in project data graph", 400
            )
        data.save()

        return dump_data(ProjectDataSchema(), project_data=data)


class MRSortInferenceAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=MRSortInferenceGetResponseSchema,
        description="MR-Sort inference model details",
    )
    def get(self, data_id):
        """
        Return the details of the MR-Sort inference model for the project's
        data.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: The processing model is not an MR-Sort model.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: MR-Sort; Get the MR-Sort inference model details
        """
        project_data = project_data_service.get_if_authorized(data_id)
        model = project_data.processing_model
        if not isinstance(project_data.processing_model, MRSort):
            raise RequestError("Only works with an MR-Sort model")
        return dump_data(MRSortInferenceSchema(), inference_data=model)

    def infer_mrsort(self, model):
        try:
            processing_model_service.infer_model(model)
        except InferenceError:
            raise RequestError("Error in the inference of the model", 500)
        return "ok"

    def load_alternatives(self, model):
        processing_model_service.load_mrsort_inference_data(model)
        return dump_data(MRSortInferenceSchema(), inference_data=model)

    @token_required
    @with_response(
        200,
        schema=MRSortInferenceGetResponseSchema,
        content={
            "text/plain": {"schema": {"type": "string", "example": "ok"}}
        },
        description=(
            "MR-Sort inference model details if action ``load`` is successful,"
            " 'ok' if action ``infer`` is successful"
        ),
    )
    @with_query_arg(
        "action",
        description=(
            "The action to execute:\n- ``load`` will load the inference "
            "alternatives\n- ``infer`` will try to infer the MR-Sort model "
            "from the alternatives"
        ),
        schema={"type": "string", "enum": ["infer", "load"]},
    )
    def post(self, data_id):
        """
        Execute an action on the MR-Sort inference model.

        :param int data_id: The id the project's data.
        :query str action:
            The action to execute: ``load`` will load the inference
            alternatives, ``infer`` will try to infer the MR-Sort model from
            the alternatives (**required**).
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400:
            The model is not an MR-Sort model or ``action`` is incorrect.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.
        :status 500: Inference error

        .. :quickref: MR-Sort; Execute an action on the MR-Sort inference model
        """
        parser = reqparse.RequestParser()
        parser.add_argument("action", type=str, location="args", required=True)
        args = parser.parse_args()
        project_data = project_data_service.get_if_authorized(data_id)
        model = project_data.processing_model
        if not isinstance(project_data.processing_model, MRSort):
            raise RequestError("Only works with an MR-Sort model")
        if args.get("action") == "load":
            return self.load_alternatives(model)
        elif args.get("action") == "infer":
            return self.infer_mrsort(model)
        else:
            raise RequestError("Unknwon action")

    @token_required
    @with_response(
        200,
        schema=MRSortInferenceGetResponseSchema,
        description="New MR-Sort inference model details",
    )
    @with_request_body(
        schema=MRSortInferenceSchema,
        description="New MR-Sort inference model details",
    )
    def put(self, data_id):
        """
        Modify the MR-Sort inference model.

        :param int data_id: The id the project's data.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: The processing model is not an MR-Sort model.
        :status 403: The user is not allowed to access the project.
        :status 404: The data does not exist.

        .. :quickref: MR-Sort; Modify the MR-Sort inference model
        """
        project_data = project_data_service.get_if_authorized(data_id)
        model = project_data.processing_model
        if not isinstance(model, MRSort):
            raise RequestError("Only works with an MR-Sort model")
        content = get_json_content()
        schema = MRSortInferenceSchema()
        model = schema.load(content, instance=model)
        model.update()
        project_data.update()
        return dump_data(schema, inference_data=model)
