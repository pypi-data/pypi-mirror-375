from datetime import datetime, timedelta

import jwt

from .exceptions import InvalidAuthenticationHeader


class JWTHandler:
    secret_key = ""
    token_validity = 900
    signing_algorithm = "HS256"
    header_prefix = "Bearer"
    authentication_header = "Authorization"

    def init_app(self, app):
        self.app = app
        self.secret_key = app.config["API_TOKEN_SECRET_KEY"]
        self.token_validity = app.config.get(
            "API_TOKEN_VALIDITY", self.token_validity
        )
        self.refresh_validity = app.config.get("API_REFRESH_VALIDITY", None)
        self.signing_algorithm = app.config.get(
            "API_JWT_ALGORITHM", self.signing_algorithm
        )
        self.header_prefix = app.config.get(
            "API_JWT_HEADER_PREFIX", self.header_prefix
        )
        self.authentication_header = app.config.get(
            "API_JWT_AUTHENTICATION_HEADER", self.authentication_header
        )

    def create_base_payload(self):
        issue_time = datetime.utcnow()
        payload = {
            "iat": issue_time,
            "exp": issue_time + timedelta(seconds=self.token_validity),
        }
        return payload

    def create_token(self, payload):
        """Encode the payload in a JSON Web Token, and create
        the registered claims (eg. 'iat', 'exp')
        """
        base_payload = self.create_base_payload()
        payload.update(base_payload)  # overwrite the payload with base_payload
        return jwt.encode(
            payload, self.secret_key, algorithm=self.signing_algorithm
        )

    def create_user_token(self, user_id, payload=None):
        """Create a token for a user"""
        base_user_payload = {"sub": user_id}
        if payload is None:
            payload = base_user_payload
        else:
            payload.update(base_user_payload)
        return self.create_token(payload)

    def create_user_refresh_token(self, user_id):
        issue_time = datetime.utcnow()
        payload = {
            "sub": user_id,
            "iat": issue_time,
            "exp": issue_time + timedelta(seconds=self.refresh_validity),
        }
        return jwt.encode(
            payload, self.secret_key, algorithm=self.signing_algorithm
        )

    def get_token_exp(self, token):
        """Returns the expiration date of the token"""
        data = self.decode(token)
        return data.get("exp", None)

    def get_user_id(self, token):
        """Returns the user_id from a token"""
        data = self.decode(token)
        user_id = data.get("sub", None)
        return user_id

    def get_token_from_request(self, request):
        """Get the token from the flask request"""
        authorization = request.headers.get(self.authentication_header, None)
        if authorization is not None:
            try:
                auth_type, auth_cred = authorization.split(" ")
            except ValueError:
                raise InvalidAuthenticationHeader(
                    "Invalid JWT authentication header"
                )
            if auth_type == self.header_prefix:
                return auth_cred
            else:
                raise InvalidAuthenticationHeader(
                    "Incorrect authentication type for the JWT"
                )
        return None

    def encode(self, payload):
        """Encode the payload in a JSON Web Token"""
        return jwt.encode(
            payload, self.secret_key, algorithm=self.signing_algorithm
        )

    def decode(self, token):
        """Decode a JSON Web Token"""
        return jwt.decode(
            token, self.secret_key, algorithms=[self.signing_algorithm]
        )


jwt_handler = JWTHandler()
