from copy import copy, deepcopy

from geoalchemy2.shape import from_shape
from geoalchemy2.types import Geometry
from shapely.geometry import box
from sqlalchemy.ext.hybrid import hybrid_property

from . import db
from .mixins import TimestampMixin
from .permission import HasPermissions


class ProjectBase(TimestampMixin, HasPermissions, db.Model):
    __tablename__ = "project"

    is_template = db.Column(db.Boolean, nullable=False)
    name = db.Column(db.String, nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    description = db.Column(db.String)
    extent = db.Column(Geometry, nullable=False)

    _manager = db.relationship("User")
    data_list = db.relationship(
        "ProjectData",
        cascade="all,delete-orphan",
        backref="project",
        primaryjoin="ProjectData.project_id == Project.id",
    )

    __mapper_args__ = {"polymorphic_on": is_template}

    def __init__(
        self, name, manager=None, description="", extent=None, is_public=False
    ):
        self.name = name
        self.description = description
        self.manager = manager
        if extent is None:
            shp_box = box(-180.0, -90.0, 180.0, 90.0)
            extent = from_shape(shp_box, srid=4326)
        self.extent = extent
        self.is_public = is_public

    @hybrid_property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, user):
        self._manager = user
        if user is not None:
            self.permissions.append(ProjectBase.Permission(user=user))


class Template(ProjectBase):
    """
    Represents the template of a project.

    A template does not have permissions.
    Only the manager of the template should have access to it.
    """

    __mapper_args__ = {"polymorphic_identity": True}
    __tablename__ = None

    def __repr__(self):
        return "<Template(name={})>".format(self.name)

    @classmethod
    def from_project(cls, project, manager=None):
        """Create a new project template from an existing project."""
        manager = manager or project.manager
        template = cls(
            name=project.name,
            manager=manager,
            description=project.description,
            extent=copy(project.extent),
            is_public=project.is_public,
        )
        # memo used by deepcopy
        # it would here consider that the references to the project
        # are in fact references to the template
        memo = {id(project): template}
        template.data_list = [deepcopy(d, memo) for d in project.data_list]
        return template


class Project(ProjectBase):
    """Represents a project and its data"""

    __mapper_args__ = {"polymorphic_identity": False}
    __tablename__ = None

    def __repr__(self):
        return "<Project(name={}, manager_id={}>".format(
            self.name, self.manager_id
        )

    @classmethod
    def from_template(cls, template, manager=None):
        """
        Create a project from a template.

        The manager of the project will be the owner of the template.

        Args:
            template: the template to copy
        """
        manager = manager or template.manager
        project = cls(
            name=template.name,
            manager=manager,
            description=template.description,
            extent=copy(template.extent),
        )
        memo = {id(template): project}
        project.data_list = [deepcopy(d, memo) for d in template.data_list]
        return project
