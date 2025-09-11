from getpass import getpass

from flask.cli import AppGroup

from ..models import PermissionAbility, User, UserPermission

user_cli = AppGroup("user", short_help="Enable manipulations of users")


@user_cli.command("create")
def create_user_command():
    """Create a user."""
    email = input("Email: ")
    if "@" not in email:
        raise ValueError("Invalid email, should contain the '@' character")
    _username = input("Username: ")
    username = email.split("@")[0] if len(_username) == 0 else _username
    password = getpass("Password: ")
    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        raise ValueError("The password doesn't match")
    user = User(username=username, email=email, password=password)
    create_project = input("Allow to create projects? (y/n) [y]: ").lower()
    create_data = input("Allow to upload geo-data? (y/n) [y]: ").lower()
    if len(create_project) == 0 or create_data.lower()[0] == "y":
        user.permissions.append(
            UserPermission(ability=PermissionAbility.create_project)
        )
    if len(create_data) == 0 or create_data.lower()[0] == "y":
        user.permissions.append(
            UserPermission(ability=PermissionAbility.create_geo_data)
        )
    user.create()
