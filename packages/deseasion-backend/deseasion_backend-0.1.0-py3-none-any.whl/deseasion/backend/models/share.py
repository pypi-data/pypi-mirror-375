import uuid
from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID

from . import db
from .mixins import ModelMixin


class DataShare(ModelMixin, db.Model):
    __tablename__ = "data_share"

    data_id = db.Column(
        db.Integer, db.ForeignKey("base_data.id"), nullable=False
    )
    uid = db.Column(
        UUID, unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    expiration = db.Column(db.DateTime)
    expired = db.Column(db.Boolean, default=False)

    data = db.relationship("BaseData", back_populates="shares")

    @classmethod
    def get_by_uid(cls, uid):
        return cls.query.filter_by(uid=uid).first()

    def is_expired(self):
        if self.expiration is None:
            date_expired = False
        else:
            date_expired = self.expiration < datetime.now()
        return date_expired or self.expired
