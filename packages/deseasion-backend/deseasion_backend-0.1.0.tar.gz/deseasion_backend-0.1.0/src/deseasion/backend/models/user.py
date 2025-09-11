from datetime import datetime

from passlib.apps import custom_app_context as pwd_context

from ..exceptions import UserTokenError
from ..security import jwt_handler
from . import db
from .mixins import ModelMixin


class UserRefreshToken(ModelMixin, db.Model):
    __tablename__ = "user_refresh_token"

    user_id = db.Column(db.ForeignKey("user.id"))
    refresh_token = db.Column(db.LargeBinary)
    expiration = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="tokens")

    def __init__(self, token):
        self.refresh_token = token
        self.expiration = datetime.fromtimestamp(
            jwt_handler.get_token_exp(token)
        )


class User(ModelMixin, db.Model):
    """Represents a user"""

    __tablename__ = "user"

    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password_hash = db.Column(db.String)

    tokens = db.relationship(
        "UserRefreshToken",
        single_parent=True,
        back_populates="user",
        cascade="all,delete-orphan",
    )

    def __init__(self, username, email, password=None):
        """Initialise the user"""
        self.username = username
        self.email = email
        if password is not None:
            self.set_password(password)
        self.tokens = []

    def __repr__(self):
        return "<User(username={}, email={}>".format(self.username, self.email)

    @classmethod
    def get_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_from_jwt(cls, token):
        user_id = jwt_handler.get_user_id(token)
        if user_id is not None:
            return cls.get_by_id(user_id)
        else:
            raise UserTokenError(
                "No valid user found for the token {}".format(token)
            )

    @classmethod
    def get_from_refresh_token(cls, token):
        user_id = jwt_handler.get_user_id(token)
        if user_id is not None:
            user = cls.get_by_id(user_id)
            if user.check_refresh_token(token) is False:
                raise UserTokenError(
                    "The refresh token can be read but is not valid"
                )
            else:
                return user
        else:
            raise UserTokenError("No found for the token {}".format(token))

    def set_password(self, password):
        """Set the password_hash from the given password"""
        self.password_hash = pwd_context.encrypt(password)

    def check_password(self, password):
        """Check if the password is correct"""
        return pwd_context.verify(password, self.password_hash)

    def create_jwt(self):
        """Create a JSON Web Token for this user"""
        token = jwt_handler.create_user_token(self.id)
        return token

    def create_refresh_token(self):
        """Creates a JSON refresh token, and associates it to the user"""
        refresh = jwt_handler.create_user_refresh_token(self.id)
        self.tokens.append(UserRefreshToken(refresh.encode()))
        return refresh

    def check_refresh_token(self, refresh_token):
        """Checks if the refresh is saved in the database for the current user.

        WARNING: Does not check the validity of the token, checks only if it
        exists for the current user

        Args:
            refresh_token - the token to check. Can be a str or a bytes object
        """
        for token in self.tokens:
            try:
                if token.refresh_token == refresh_token.encode():
                    return True
            except AttributeError:
                if token.refresh_token == refresh_token:
                    return True
        return False
