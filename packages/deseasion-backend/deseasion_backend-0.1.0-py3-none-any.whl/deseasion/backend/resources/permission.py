from flask_restful import Resource

from ..schemas import UserListGetResponseSchema, UserSchema
from ..services.auth_service import token_required
from ..services.permission_service import get_all_users
from .utils import dump_data, with_response


class UserListAPI(Resource):
    @token_required
    @with_response(
        status=200,
        schema=UserListGetResponseSchema,
        description="List of all users",
    )
    def get(self):
        """
        Return the list of all the users.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).

        .. :quickref: User; Get the list of users
        """
        users = get_all_users()
        schema = UserSchema(only=("id", "username"), many=True)
        return dump_data(schema, users=users)
