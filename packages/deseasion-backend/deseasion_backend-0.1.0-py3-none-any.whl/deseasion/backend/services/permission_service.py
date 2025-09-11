from functools import wraps

from flask import request

from ..exceptions import PermissionError
from ..models import User, db
from .auth_service import check_jwt_authentication


def has_permission(obj, user=None):
    """Check if the user of the request is authorized to use the object

    Returns a boolean indicating if the user has permissions on the object.

    Args:
        user:
            The user to check for the permission.
            Default: None (load the user from the token).
    """
    if user is None:
        user = check_jwt_authentication(request)
    if user is None:
        return False
    return obj.is_user_authorized(user)


def has_permission_for_id(obj_class, obj_id):
    """Check if the user of the request is authorized to use the object with
    the given id"""
    user = check_jwt_authentication(request)
    if user is None:
        return False
    obj = obj_class.get_by_id(obj_id)
    return obj.is_user_authorized(user)


def has_ability(ability):
    """Check that a user has the necessary ability

    Executes the decorated function if the user has the abilty, otherwise
    raises an error.

    Raises:
        PermissionError if the user does not have the ability
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = check_jwt_authentication(request)
            if any([ability is p.ability for p in user.permissions]):
                return fn(*args, **kwargs)
            raise PermissionError

        return wrapper

    return decorator


def get_all_users():
    """Returns the list of all the users in the application"""
    return db.session.query(User).order_by(User.id).all()
