from datetime import datetime
from typing import Self

from . import db


class BaseModelMixin:
    def save(self):
        """Commit the object to the database"""
        db.session.commit()

    def create(self):
        """Persist the current object in the database"""
        db.session.add(self)
        self.save()
        return self

    def delete(self):
        """Delete the current object from the database"""
        db.session.delete(self)
        db.session.commit()

    def on_modification(self):
        """Callback called when updating the data."""
        pass

    def update(self):
        """Update the current object"""
        self.on_modification()
        self.save()


class ModelMixin(BaseModelMixin):
    """CRUD mixin for the models"""

    id = db.Column(db.Integer, primary_key=True)

    def delete(self):
        super().delete()
        self.id = None

    @classmethod
    def get_by_id(cls, id) -> Self:
        """Returns the instance with the given id"""
        return cls.query.filter_by(id=id).first()


class TimestampMixin(ModelMixin):
    """CRUD mixin, extend with created_at and modified_at fields"""

    created_at = db.Column(db.DateTime)
    modified_at = db.Column(db.DateTime)

    def create(self):
        """Persist the object in the database, with a creation and modification
        date"""
        self.created_at = datetime.utcnow()
        self.modified_at = self.created_at
        return super().create()

    def on_modification(self):
        """Set the modification time"""
        super().on_modification()
        self.update_modified()

    def update_created(self):
        self.created_at = datetime.utcnow()

    def update_modified(self):
        self.modified_at = datetime.utcnow()
