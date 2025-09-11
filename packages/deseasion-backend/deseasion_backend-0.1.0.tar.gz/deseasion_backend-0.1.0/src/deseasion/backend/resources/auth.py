from flask import jsonify, request
from flask_restful import Resource

from ..exceptions import RequestError
from ..models import User
from ..schemas import (
    UserAccessTokenResponseSchema,
    UserSchema,
    UserTokenResponseSchema,
)
from ..security import jwt_handler
from ..services import auth_service
from .utils import dump_data, with_response


class LoginAPI(Resource):
    def create_user_token_response(self, user):
        """
        Create a new authentication and refresh token for the user.
        """
        token = user.create_jwt()
        refresh = user.create_refresh_token()
        data = {
            "access_token": token,
            "refresh_token": refresh,
            "token_type": jwt_handler.header_prefix,
        }
        return data

    @auth_service.basic_authenticated
    @with_response(
        status=200,
        schema=UserTokenResponseSchema,
        description="User access and refresh tokens",
    )
    def get(self, user: User):
        """
        Log the user in and return an authentication and a refresh token.

        :reqheader Authorization: `Basic authentication <https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#Basic_authentication_scheme>`_, ``user:password`` encoded in base64.
        :resjson str access_token: Access token.
        :resjson str refresh_token:
            Token to use for creating a new authentication token.
        :resjson str token_type: Type of the token

        .. :quickref: Authentication; Log the user in"""  # noqa: E501
        data = self.create_user_token_response(user)
        user.update()
        return jsonify(**data)


class RefreshAPI(Resource):
    def create_new_jwt(self, user):
        """
        Create a new authentication token for the user.
        """
        token = user.create_jwt()
        data = {"access_token": token, "token_type": jwt_handler.header_prefix}
        return data

    @auth_service.refresh_token_required
    @with_response(
        status=200,
        schema=UserAccessTokenResponseSchema,
        description="Refreshed user access token",
    )
    def get(self, user: User):
        """
        Create a new authentication token from the refresh token.

        :reqheader Authorization: The refresh token received when login in.
        :resjson str access_token: Access token.
        :resjson str token_type: Type of the token

        .. :quickref: Authentication; Create a new authentication token
        """
        data = self.create_new_jwt(user)
        return jsonify(**data)


class UserAPI(Resource):
    @auth_service.token_required
    @with_response(
        status=200, schema=UserSchema, description="Current user details"
    )
    def get(self):
        """
        Return the details of the current user.

        :reqheader Authorization:
            JSON Web Token with Bearer scheme
            (``Authorization: Bearer <token>``).

        .. :quickref: User; Get the details of the current user
        """
        user = auth_service.check_jwt_authentication(request)
        if user is None:
            raise RequestError("No user connected", 401)
        else:
            return dump_data(UserSchema(), user=user)
