from ..exceptions import PermissionError, RequestError
from ..models import (
    DataAttribute,
    DataShare,
    GeneratedGeoData,
    Project,
    ProjectTaskModel,
    Template,
)
from ..models.project_data_utils import ProjectDataProcessingService
from .permission_service import has_permission


class ProjectService:
    __model__ = Project

    def get_if_authorized(self, project_id, user=None):
        """
        Return the project if the user has the permissions to view it.

        Args:
            project_id (int): Id of the project to return.
            user: User object.

        Raises:
            PermissionError if the user is not authorized to view this project.
        """
        project = self.__model__.get_by_id(project_id)
        if project is None:
            raise RequestError("The project does not exist", 404)
        if not has_permission(project, user):
            raise PermissionError
        return project

    def get_template_if_authorized(self, template_id, user=None):
        template = Template.get_by_id(template_id)
        if template is None:
            raise RequestError("The template does not exist", 404)
        if not has_permission(template, user):
            raise PermissionError
        return template

    def get_template_if_manager(self, template_id, user=None):
        assert user is not None
        template = self.get_template_if_authorized(template_id, user)
        if template.manager is not user or template.manager is None:
            raise PermissionError
        return template

    def get_all_authorized_projects(self, user=None):
        """
        Return the list of all project viewable by the user.

        The templates are not returned by this function.
        """
        project_list = Project.query.order_by(Project.id).all()
        return list(filter(lambda p: has_permission(p, user), project_list))

    def get_if_manager(self, project_id, user):
        """Return the project if the user if the project's manager."""
        assert user is not None
        project = self.get_if_authorized(project_id, user)
        if project.manager is not user or project.manager is None:
            raise PermissionError
        return project

    def get_user_templates(self, user=None):
        """Return the templates of the user."""
        template_list = Template.query.order_by(Template.id).all()
        return list(filter(lambda p: has_permission(p, user), template_list))

    def get_managed_templates(self, user):
        """Return the managed templates of the user."""
        query = Template.query.filter_by(manager=user)
        return query.order_by(Template.id).all()

    def get_project_tasks(self, project_id, limit=None, offset=None):
        """Return the list of tasks started in the project.

        Args:
            project_id (int): The id of the project.
            limit (int):
                The number of tasks to return. Default: None (all the tasks).
            offset (int):
                Offset for the tasks list.
                Default: None (start from the beginning).
        """
        project = self.get_if_authorized(project_id)
        query = ProjectTaskModel.query.filter_by(project_id=project.id)
        query = query.order_by(ProjectTaskModel.started_at.desc())
        if limit is not None:
            query = query.limit(limit)
        if offset is not None:
            query = query.offset(offset)
        return query.all()

    def get_total_project_tasks(self, project_id):
        """Return the total number of tasks in this project."""
        project = self.get_if_authorized(project_id)
        query = ProjectTaskModel.query.filter_by(project_id=project.id)
        return query.count()

    def create_template_from_project(self, project_id, user):
        """Create a template from a project."""
        project = self.get_if_authorized(project_id, user)
        template = Template.from_project(project, user)
        return template

    def create_project_from_template(self, template_id, manager):
        """
        Create a new projet from a JSON template.

        Args:
            template (std): The JSON template of the project. Will be modified.
            manager (User): The user that will be the manager of the project.
        """
        template = self.get_template_if_authorized(template_id, manager)
        project = Project.from_template(template, manager)
        return project

    def replace_input_attributes(
        self,
        project_id,
        attributes_mapping: dict[DataAttribute, DataAttribute],
    ) -> Project:
        """Replace input attributes of project data by new ones.

        :param project_id:
        :param attributes_mapping: mapping of old attributes to new ones
        :raise ValueError:
            * if project data graph cycles would be introduced
            * if some attributes are not in any data of the project
            * if some new attributes introduced were already in the data inputs
        :raise TypeError: if an attribute has changed its type
        :return: modified project
        """
        project = self.get_if_authorized(project_id)
        ps = ProjectDataProcessingService()

        old_attributes = set(attributes_mapping.keys())
        for data in project.data_list:
            to_replace_atts = (
                data._get_used_input_attributes() & old_attributes
            )
            if len(to_replace_atts) == 0:
                continue
            ps.replace_input_attributes(data, attributes_mapping)
        return project

    def get_authorized_shares(self, project_id: int) -> list[DataShare]:
        """Get all project data shares which the user has authorization for.

        :param project_id:
        :return: authorized data shares
        """
        project = self.get_if_authorized(project_id)
        shared = []
        for data in project.data_list:
            if data.data is None:
                continue
            match data.data:
                case GeneratedGeoData():
                    pass
                case _:
                    if not has_permission(data.data):
                        continue
            for share in data.data.shares:
                if not share.is_expired():
                    shared.append(share)
        return shared
