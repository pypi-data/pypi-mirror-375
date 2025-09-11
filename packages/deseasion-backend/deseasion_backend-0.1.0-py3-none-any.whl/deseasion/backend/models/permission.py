from enum import Enum

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref

from . import db
from .mixins import ModelMixin


def find_tablename(cls):
    """Find `__tablename__` attribute in class tree.

    :raises AttributeError: if attribute `__tablename__` is never set in tree
    :return: closest set `__tablename__` attribute found
    """
    if cls.__tablename__ is None:
        for scls in cls.__bases__:
            if issubclass(scls, db.Model):
                return find_tablename(scls)
        raise AttributeError(f"cannot find {cls} __tablename__")
    return cls.__tablename__


class HasPermissions:
    """Mixin to create a permission table for the object

    Inspired from SQLAlchemy's example:
    http://docs.sqlalchemy.org/en/rel_1_1/_modules/examples/generic_associations/table_per_related.html
    """  # E501

    is_public = db.Column(db.Boolean, default=False, nullable=False)

    @declared_attr
    def permissions(cls):
        """Create new a permissions table linking a user with an object

        The table created will be called '<name>_permission', with <name> being
        the name of the table where this mixin is used
        """
        cls.Permission = type(
            "{}Permission".format(cls.__name__),
            (ModelMixin, db.Model),
            dict(
                __tablename__="{}_permission".format(find_tablename(cls)),
                object_id=db.Column(
                    db.Integer,
                    db.ForeignKey("{}.id".format(find_tablename(cls))),
                ),
                object=db.relationship(cls),
                user_id=db.Column(
                    db.Integer, db.ForeignKey("user.id"), nullable=False
                ),
                user=db.relationship("User"),
            ),
        )
        return db.relationship(cls.Permission, cascade="all,delete-orphan")

    def is_user_authorized(self, user):
        """Check if the user has a permission on this object

        Returns a boolean indicating if the user has a permission on the object
        """
        return self.is_public or any(
            (user.id == perm.user_id for perm in self.permissions)
        )


class PermissionAbility(Enum):
    create_project = 1
    create_geo_data = 2


class UserPermission(ModelMixin, db.Model):
    __tablename__ = "user_permission"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    ability = db.Column(db.Enum(PermissionAbility), nullable=False)

    user = db.relationship(
        "User",
        backref=backref(
            "permissions", lazy="select", cascade="all,delete-orphan"
        ),
    )
