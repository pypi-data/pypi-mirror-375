from flask import jsonify, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError

from ..exceptions import RequestError
from ..models import DataAttribute, DataType, PermissionAbility, Project, db
from ..models.project_data_utils import ProjectDataProcessingService
from ..schemas import (
    DataGeneratorSchema,
    DataGeoSchema,
    DataStreamSchema,
    MessageSchema,
    ProjectAccessSchema,
    ProjectCreationSchema,
    ProjectDataBaseSchema,
    ProjectDataCreationSchema,
    ProjectDataReplaceInputsPostRequestBodySchema,
    ProjectFromTemplateRequestBody,
    ProjectGetResponseSchema,
    ProjectGlobalDataSchema,
    ProjectListGetResponseSchema,
    ProjectPermissionGetResponseSchema,
    ProjectSchema,
    ProjectSharedDataListGetResponseSchema,
    ProjectSharedDataListPostResponseSchema,
    ProjectTemplateListGetResponseSchema,
    ProjectTemplatePostResponseSchema,
    TemplateAccessSchema,
    TemplatePermissionGetResponseSchema,
    TemplateSchema,
)
from ..services import (
    geo_data_service,
    geo_data_stream_service,
    project_data_service,
    project_service,
)
from ..services.auth_service import check_jwt_authentication, token_required
from ..services.permission_service import has_ability
from .utils import (
    dump_data,
    get_json_content,
    with_query_arg,
    with_request_body,
    with_response,
)


class ProjectListAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectListGetResponseSchema,
        description="Full list of accessible projects",
    )
    def get(self):
        """
        Return the full list of projects accessible by the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).

        .. :quickref: Project; Get the list of accessible projects
        """
        projects = project_service.get_all_authorized_projects()
        return dump_data(ProjectSchema(many=True), projects=projects)

    @token_required
    @has_ability(PermissionAbility.create_project)
    @with_response(
        200,
        schema=ProjectGetResponseSchema,
        description="Created project details",
    )
    @with_request_body(
        schema=[ProjectCreationSchema, ProjectFromTemplateRequestBody],
        description=(
            "Either the project details or the template from which to create "
            "it"
        ),
    )
    def post(self):
        """
        Create a new project.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to create projects.

        .. :quickref: Project; Create a new project
        """
        user = check_jwt_authentication(request)
        content = get_json_content()
        schema = ProjectCreationSchema()
        if "template" in content.keys():
            # load the project from the template using the template id
            template_id = content.pop("template")
            with db.session.no_autoflush:
                project = project_service.create_project_from_template(
                    template_id, user
                )
            print(project, project.is_template)
            # update the project with the content
            project = schema.load(content, instance=project)
        else:
            project = schema.load(content)
            project.manager = user
        project.create()
        return dump_data(schema, project=project)


class ProjectAPI(Resource):
    @token_required
    @with_response(
        200, schema=ProjectGetResponseSchema, description="Project details"
    )
    def get(self, project_id):
        """
        Return the project details for a given id.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Get the project details
        """
        project = project_service.get_if_authorized(project_id)
        return dump_data(ProjectSchema(), project=project)

    @token_required
    @with_response(
        200, schema=ProjectGetResponseSchema, description="New project details"
    )
    @with_request_body(schema=ProjectSchema, description="New project details")
    def put(self, project_id):
        """
        Update the project details.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to modify this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Update the project details
        """
        project = project_service.get_if_authorized(project_id)
        content = get_json_content()
        schema = ProjectSchema()
        project = schema.load(content, instance=project)
        project.update()
        return dump_data(schema, project=project)

    @token_required
    @with_response(
        200, schema=MessageSchema, description="Project successfully deleted"
    )
    def delete(self, project_id):
        """
        Delete the project.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400:
            The project is referenced by other objects and cannot be deleted.
        :status 403: The user is not allowed to delete this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Delete the project
        """
        project = project_service.get_if_authorized(project_id)
        try:
            project.delete()
        except IntegrityError:
            raise RequestError(
                (
                    "The project is referenced by other objects and cannot be "
                    "deleted"
                ),
                400,
            )
        return jsonify(message="project {} deleted".format(project_id))


class ProjectPermissionsAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectPermissionGetResponseSchema,
        description="Project permissions",
    )
    def get(self, project_id):
        """
        Allow the project manager to get the list of permissions.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the manager of this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Get the project permissions
        """
        user = check_jwt_authentication(request)
        project = project_service.get_if_manager(project_id, user)
        schema = ProjectAccessSchema()
        return dump_data(schema, access=project)

    @token_required
    @with_response(
        200,
        schema=ProjectPermissionGetResponseSchema,
        description="New project permissions",
    )
    @with_request_body(
        schema=ProjectAccessSchema, description="New project permissions"
    )
    def put(self, project_id):
        """
        Allow to modify the list of permissions for the project.

        Only the project manager is allowed to modify the permissions.
        The project manager is always added to the list of authorized users.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the manager of this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Modify the project permissions
        """
        user = check_jwt_authentication(request)
        project = project_service.get_if_manager(project_id, user)
        schema = ProjectAccessSchema()
        content = get_json_content()
        project = schema.load(content, instance=project)
        if not any([p.user is project.manager for p in project.permissions]):
            # always authorize the manager of the project
            project.permissions.append(
                Project.Permission(user=project.manager)
            )
        project.update()
        return dump_data(schema, access=project)


class ProjectSharedDataListAPI(Resource):
    def load_content(self):
        """Loads the content and the data_type from the request body"""
        content = get_json_content()
        try:
            data_type_str = content.pop("data_type")
            data_type = DataType[data_type_str]
        except KeyError:
            raise RequestError(
                'The json data should contain a "data_type" field with a one '
                "of the following values: "
                "{}".format(", ".join(d.name for d in DataType)),
                400,
            )
        return content, data_type

    @token_required
    @with_response(
        200,
        schema=ProjectSharedDataListPostResponseSchema,
        description="List of project shared data",
    )
    @with_request_body(
        schema=ProjectDataCreationSchema,
        description="New project data details",
    )
    def post(self, project_id):
        """
        Create a new project data in the project.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: There is an error in the json schema for the data,
                     or the data/stream already exists in the project.
        :status 403: The user is not allowed to access this project, the data
                     or the stream.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Create a new data in the project
        """
        project = project_service.get_if_authorized(project_id)
        content, data_type = self.load_content()
        schema = ProjectDataCreationSchema.type_schemas[data_type.name]
        try:
            input_data = content.pop("input_data", [])
            output_data = content.pop("output_data", [])
            project_data = schema().load(content)
        except NameError as error:
            raise RequestError(str(error), 400)
        if project_data.data_type != DataType.generator:
            if project_data.data_type in (
                DataType.geo_data,
                DataType.global_data,
            ):
                geo_data_service.check_permission(project_data.data)
            else:
                geo_data_stream_service.check_permission(project_data.stream)
            for d in project.data_list:
                if project_data.data_type in (
                    DataType.geo_data,
                    DataType.global_data,
                ):
                    if d.data is not None and project_data.data == d.data:
                        raise RequestError(
                            "This data is already shared in the project", 400
                        )
                elif d.data_type == project_data.data_type:
                    # Both are DataStream
                    if (
                        d.stream is not None
                        and project_data.stream == d.stream
                    ):
                        raise RequestError(
                            "This stream is already shared in the project", 400
                        )
        project_data.project = project

        try:
            for data_input_id in input_data:
                project_data.add_input(
                    project_data_service.get_if_authorized(data_input_id)
                )

            for data_output_id in output_data:
                output = project_data_service.get_if_authorized(data_output_id)
                output.add_input(project_data)
                output.on_modification()
                db.session.add(output)
        except (TypeError, ValueError) as exc:
            raise RequestError(str(exc), 400)

        ps = ProjectDataProcessingService()
        data_graph = ps.get_project_data_graph(project)
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

        project_data.create()
        dump_sch = ProjectDataBaseSchema(
            only=(
                "name",
                "id",
                "data",
                "data_type",
                "input_data",
                "output_data",
            ),
            many=True,
        )
        return dump_data(dump_sch, data_list=project.data_list)

    @token_required
    @with_response(
        200,
        schema=ProjectSharedDataListGetResponseSchema,
        description="List of project shared data",
    )
    def get(self, project_id):
        """
        Return the list of project data in the project.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access this project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Get the list of data in the project
        """
        project = project_service.get_if_authorized(project_id)
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
        for projdata in project.data_list:
            res.append(dump_schemas[projdata.data_type].dump(projdata))
        return {"data_list": res}


class ProjectReplaceInputAttributesAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectSharedDataListPostResponseSchema,
        description="List of project data",
    )
    @with_request_body(schema=ProjectDataReplaceInputsPostRequestBodySchema)
    def post(self, project_id):
        """Replace project data attributes usage.

        It replaces usage of old attributes given by new attributes given,
        assuming the old attributes given are attributes of this project's data
        and that the new attributes given are not already used as inputs
        alongside some of the old attributes.

        Its main usage is threfore to replace whole project data
        (all their attributes) by completely unused other project data.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 400: Remapping could not proceed with given arguments.
        :status 403: The user is not allowed to access this project, or a data
        :status 404: The project or a data doesn't exist.

        .. :quickref: Project; Replace project data attributes usage
        """
        ps = ProjectDataProcessingService()

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
            project = project_service.replace_input_attributes(
                project_id, attributes_mapping
            )
        except (ValueError, TypeError) as exc:
            raise RequestError(str(exc), 400)

        data_graph = ps.get_project_data_graph(project)
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
        db.session.commit()

        dump_sch = ProjectDataBaseSchema(
            only=(
                "name",
                "id",
                "data",
                "data_type",
                "input_data",
                "output_data",
            ),
            many=True,
        )
        return dump_data(dump_sch, data_list=project.data_list)


class ProjectTemplateAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectTemplatePostResponseSchema,
        description="Created template details",
    )
    def post(self, project_id):
        """Create a template from a project.

        :param int project_id: The id of the project.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the project.
        :status 404: The project doesn't exist.

        .. :quickref: Project; Create a template from project
        """
        user = check_jwt_authentication(request)
        with db.session.no_autoflush:
            template = project_service.create_template_from_project(
                project_id, user
            )
        schema = TemplateSchema()
        content = get_json_content()
        template = schema.load(content, instance=template)
        template.create()
        return dump_data(schema, template=template)


class TemplateListAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectTemplateListGetResponseSchema,
        description="List of accessible project templates",
    )
    @with_query_arg(
        "managed",
        bool,
        required=False,
        description=(
            "Return all accessible templates if false or absent, "
            "only managed templates otherwise",
        ),
    )
    def get(self):
        """
        Return the list of templates of the user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).

        .. :quickref: Template; Get the list of accessible templates
        """
        parser = reqparse.RequestParser()
        parser.add_argument("managed", type=bool, location="args")
        args = parser.parse_args()
        user = check_jwt_authentication(request)
        if args.get("managed", False):
            templates = project_service.get_managed_templates(user)
        else:
            templates = project_service.get_user_templates(user)
        return dump_data(TemplateSchema(many=True), templates=templates)


class TemplateAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=ProjectTemplatePostResponseSchema,
        description="New project template details",
    )
    @with_request_body(
        schema=TemplateSchema, description="New project template details"
    )
    def put(self, template_id):
        """Modify a project template.

        :param int template_id: The id of the project template.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to access the template.
        :status 404: The template doesn't exist.

        .. :quickref: Template; Modify a project template
        """
        user = check_jwt_authentication(request)
        template = project_service.get_template_if_manager(template_id, user)
        content = get_json_content()
        schema = TemplateSchema()
        template = schema.load(content, instance=template)
        template.update()
        return dump_data(schema, template=template)

    @token_required
    @with_response(
        200, schema=MessageSchema, description="Template deleted successfully"
    )
    def delete(self, template_id):
        """Delete a project template.

        :param int template_id: The id of the project template.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not allowed to delete the template.
        :status 404: The template doesn't exist.

        .. :quickref: Template; Delete a project template
        """
        user = check_jwt_authentication(request)
        template = project_service.get_template_if_manager(template_id, user)
        template.delete()
        return jsonify(message="template {} deleted".format(template_id))


class TemplatePermissionsAPI(Resource):
    @token_required
    @with_response(
        200,
        schema=TemplatePermissionGetResponseSchema,
        description="Template permissions",
    )
    def get(self, template_id):
        """
        Allow the template manager to get the list of permissions.

        :param int template_id: The id of the template.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the manager of this template.
        :status 404: The template doesn't exist.

        .. :quickref: Template; Get the template permissions
        """
        user = check_jwt_authentication(request)
        template = project_service.get_template_if_manager(template_id, user)
        schema = TemplateAccessSchema()
        return dump_data(schema, access=template)

    @token_required
    @with_response(
        200,
        schema=TemplatePermissionGetResponseSchema,
        description="New template permissions",
    )
    @with_request_body(
        schema=TemplateAccessSchema, description="New template permissions"
    )
    def put(self, template_id):
        """
        Allow to modify the list of permissions for the template.

        Only the template manager is allowed to modify the permissions.
        The template manager is always added to the list of authorized users.

        :param int template_id: The id of the template.
        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).
        :status 403: The user is not the manager of this template.
        :status 404: The template doesn't exist.

        .. :quickref: Template; Modify the template permissions
        """
        user = check_jwt_authentication(request)
        template = project_service.get_template_if_manager(template_id, user)
        schema = ProjectAccessSchema()
        content = get_json_content()
        template = schema.load(content, instance=template)
        if not any([p.user is template.manager for p in template.permissions]):
            # always authorize the manager of the project
            template.permissions.append(
                Project.Permission(user=template.manager)
            )
        template.update()
        return dump_data(schema, access=template)
