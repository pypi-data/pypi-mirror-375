import enum
from copy import deepcopy
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declared_attr

from . import db
from .geo_data import (
    BaseData,
    DataAttribute,
    Feature,
    GeoData,
    GlobalData,
    StreamGeoData,
    WMSGeoData,
)
from .mixins import BaseModelMixin, TimestampMixin


class DataType(enum.Enum):
    geo_data = 1
    generator = 2
    global_data = 3
    data_stream = 4


input_assoc = db.Table(
    "data_input_association",
    db.Model.metadata,
    db.Column(
        "project_data_id",
        db.Integer,
        db.ForeignKey("project_data.id"),
        primary_key=True,
    ),
    db.Column(
        "input_data_id",
        db.Integer,
        db.ForeignKey("project_data.id"),
        primary_key=True,
    ),
)


class ProjectData(TimestampMixin, db.Model):
    __tablename__ = "project_data"

    data_type = db.Column(db.Enum(DataType))
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey("base_data.id"))
    last_update = db.Column(db.DateTime)
    project_id = db.Column(
        db.Integer, db.ForeignKey("project.id"), nullable=False
    )
    description = db.Column(db.String)
    name = db.Column(db.String)

    input_data = db.relationship(
        "ProjectData",
        secondary=input_assoc,
        primaryjoin=(id == input_assoc.c.project_data_id),
        secondaryjoin=(id == input_assoc.c.input_data_id),
        backref="output_data",
        order_by=input_assoc.c.input_data_id,
    )
    data = db.relationship("BaseData", foreign_keys=[data_id])

    __mapper_args__ = {"polymorphic_on": data_type}

    def __init__(self, name=None, project=None, description="", input_data=[]):
        self.project = project
        self.input_data = []
        for data in input_data:
            self.add_input(data)
        self.last_update = None
        self.name = name
        self.description = description

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.name = self.name
        other.description = self.description
        other.project = deepcopy(self.project, memo)
        other.input_data = [deepcopy(d, memo) for d in self.input_data]
        other.data = deepcopy(self.data, memo)
        return other

    def update_full(self):
        """Update project data.

        This makes sure that :attr:`ProjectData.last_update` field is equal
        to :attr:`ProjectData.modified_at` after update and database commit.
        So :meth:`ProjectData.is_outdated` method works as intended.

        :return:
        """
        super().update_modified()
        self.last_update = self.modified_at
        return super().save()

    def add_input(self, project_data):
        """Add input data.

        :param project_data:
        :raises ValueError: if `project_data` is from a different project
        """
        if project_data.project != self.project:
            raise ValueError("cannot add input data from other projects")
        self.input_data.append(project_data)

    def is_outdated(self):
        """Checks if input data are more recent than this object"""
        if self.last_update is None or self.last_update < self.modified_at:
            return True
        for data in self.input_data:
            if data.last_update is not None:
                if (
                    self.last_update is None
                    or data.last_update > self.last_update
                ):
                    return True
            if data.is_outdated():
                return True
        return False

    def get_attributes_list(self):
        """Returns the list of attributes of the features for this data.

        Returns:
            a dictionary with the following keys:
            "id", "name", "type", "statistics"
        """
        if self.data is not None:
            attr_list = []
            for attribute in self.data.attributes:
                attribute.load_statistics()
                attr_list.append(
                    {
                        "id": attribute.id,
                        "name": attribute.name,
                        "type": attribute.type.name,
                        "statistics": attribute.statistics,
                    }
                )
            return attr_list
        else:
            return []

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Return set of used input attributes of project data.

        :param data:
        :return: used input attributes
        """
        return set()

    def get_used_input_attributes(self) -> list[DataAttribute]:
        """Get used input attributes of project data if the user is authorized
        to access it.

        This list contains al inputl attributes used at least once in a
        processing model of the project data.

        Returns:
            Used input attributes.
        """
        return sorted(
            self._get_used_input_attributes(), key=lambda a: (a.data.id, a.id)
        )

    def _get_used_attributes(self) -> set[DataAttribute]:
        """Return set of used attributes of project data.

        This set contains all attributes used at least once in a processing
        model of the project data.

        :param data:
        :return: used input attributes
        """
        attributes = set()
        if self.data is None:
            return attributes
        for ref in self.output_data:
            attributes |= {
                attr
                for attr in ref._get_used_input_attributes()
                if attr.data_id == self.data.id
            }
        return attributes

    def get_used_attributes(self) -> list[DataAttribute]:
        """Get used attributes of project data if the user is authorized
        to access it.

        This list contains all attributes used at least once in a processing
        model of the downstream project data.

        Returns:
            Used attributes.
        """
        return sorted(self._get_used_attributes(), key=lambda a: a.id)

    def _explain_uptodate(self, feature: Feature) -> dict:
        """Explain uptodate feature values wrt the project data.

        :param feature: feature part of the project data
        :return: explanation as a dict
        """
        return {}

    def explain(self, feature: Feature) -> dict:
        """Explain feature values wrt the project data.

        :param feature:
        :raises ValueError: if `feature` does not belong to this project data
        :return: explanation as a dict
        """
        if self.is_outdated():
            return {}
        if feature.data_id != self.data_id:
            raise ValueError("feature does not belong to this project data")
        return self._explain_uptodate(feature)


class DataGeo(ProjectData):
    data = db.relationship("GeoData", foreign_keys=[ProjectData.data_id])

    __mapper_args__ = {"polymorphic_identity": DataType.geo_data}

    def __init__(self, data=None, data_id=None, **kwargs):
        if data is None and data_id is not None:
            data = GeoData.get_by_id(data_id)
        elif data is not None and data_id is not None:
            raise ValueError(
                "Only one of the parameters data or data_id must be passed"
            )
        if kwargs.get("name") is None and data is not None:
            kwargs["name"] = data.name
        super().__init__(**kwargs)
        self.data = data  # TODO: Verify the data is not None
        self.last_update = None

    def create(self):
        """Persist the object in the database, with a creation, modification
        and last updat edate"""
        self.created_at = datetime.now(timezone.utc)
        self.modified_at = self.created_at
        self.last_update = self.created_at
        return BaseModelMixin.create(self)

    def __repr__(self):
        return (
            "<DataGeo(name={s.name}, project_id={s.project_id}, "
            "data_id={s.data_id})>".format(s=self)
        )

    def add_input(self, project_data):
        """Add input (always fail).

        :param project_data:
        :raises TypeError: data doesn't accept inputs
        """
        raise TypeError(f"cannot add input in a {type(self).__name__} object")

    def is_outdated(self):
        """Checks if input data are more recent than this object"""
        return False


class ProjectGlobalData(ProjectData):
    data = db.relationship("GlobalData", foreign_keys=[ProjectData.data_id])

    __mapper_args__ = {"polymorphic_identity": DataType.global_data}

    def __init__(self, data=None, data_id=None, **kwargs):
        if data is None and data_id is not None:
            data = GlobalData.get_by_id(data_id)
        elif data is not None and data_id is not None:
            raise ValueError(
                "Only one of the parameters data or data_id must be passed"
            )
        if kwargs.get("name") is None and data is not None:
            kwargs["name"] = data.name
        super().__init__(**kwargs)
        self.data = data  # TODO: Verify the data is not None
        self.last_update = None

    def create(self):
        """Persist the object in the database, with a creation, modification
        and last updat edate"""
        self.created_at = datetime.now(timezone.utc)
        self.modified_at = self.created_at
        self.last_update = self.created_at
        return BaseModelMixin.create(self)

    def __repr__(self):
        return (
            "<ProjectGlobalData(name={s.name}, project_id={s.project_id}, "
            "data_id={s.data_id})>".format(s=self)
        )

    def add_input(self, project_data):
        """Add input (always fail).

        :param project_data:
        :raises TypeError: data doesn't accept inputs
        """
        raise TypeError(f"cannot add input in a {type(self).__name__} object")

    def is_outdated(self):
        """Checks if input data are more recent than this object"""
        return False


class DynamicData(ProjectData):
    @declared_attr
    def data(cls):
        return db.relationship(
            "GeneratedGeoData",
            single_parent=True,
            cascade="all,delete-orphan",
            foreign_keys=[ProjectData.data_id],
        )

    __mapper_args__ = {"polymorphic_abstract": True}


class DataStream(DynamicData):
    stream_id = db.Column(db.Integer, db.ForeignKey("base_data.id"))
    stream = db.relationship(BaseData, foreign_keys=[stream_id])
    classes = db.Column(ARRAY(db.Float, dimensions=2), nullable=True)
    start = db.Column(db.Float, nullable=True)
    step = db.Column(db.Float, nullable=True)
    stop = db.Column(db.Float, nullable=True)
    resolution = db.Column(db.Float, nullable=True)

    __mapper_args__ = {"polymorphic_identity": DataType.data_stream}

    def __init__(self, stream=None, stream_id=None, **kwargs):
        if stream is None and stream_id is not None:
            stream = BaseData.get_by_id(stream_id)
        elif stream is not None and stream_id is not None:
            raise ValueError(
                "Only one of the parameters stream or stream_id must be passed"
            )
        if not isinstance(stream, StreamGeoData):
            raise TypeError("'stream' field must reference a valid stream")
        if kwargs.get("name") is None and stream is not None:
            kwargs["name"] = stream.name
        if kwargs.get("description") is None and stream is not None:
            kwargs["description"] = stream.description
        if isinstance(stream, WMSGeoData):
            self.classes = kwargs.pop("classes", stream.classes)
            self.start = kwargs.pop("start", stream.start)
            self.step = kwargs.pop("step", stream.step)
            self.stop = kwargs.pop("stop", stream.stop)
            self.resolution = kwargs.pop("resolution", stream.resolution)
        super().__init__(**kwargs)
        self.stream = stream

    def __repr__(self):
        return (
            "<DataStream(name={s.name}, project_id={s.project_id}, "
            "stream_id={s.stream_id})>".format(s=self)
        )

    def __deepcopy__(self, memo):
        other = type(self)(self.stream)
        memo[id(self)] = other
        other.name = self.name
        other.description = self.description
        other.project = deepcopy(self.project, memo)
        other.input_data = [deepcopy(d, memo) for d in self.input_data]
        other.data = deepcopy(self.data, memo)
        if isinstance(self.stream, WMSGeoData):
            other.classes = self.classes
            other.start = self.start
            other.step = self.step
            other.stop = self.stop
            other.resolution = self.resolution
        return other

    def add_input(self, project_data):
        """Add input (always fail).

        :param project_data:
        :raises TypeError: data doesn't accept inputs
        """
        raise TypeError(f"cannot add input in a {type(self).__name__} object")


class DataGenerator(DynamicData):
    active_model_id = db.Column(
        db.Integer, db.ForeignKey("processing_model.id")
    )

    _processing_models = db.relationship(
        "ProcessingModel",
        cascade="all,delete-orphan",
        back_populates="data_generator",
        foreign_keys="[ProcessingModel.data_generator_id]",
        order_by="ProcessingModel.id",
    )
    _processing_model = db.relationship(
        "ProcessingModel",
        cascade="all",
        primaryjoin="project_data.c.active_model_id == processing_model.c.id",
        post_update=True,
    )

    __mapper_args__ = {"polymorphic_identity": DataType.generator}

    def __init__(self, processing_model=None, **kwargs):
        super().__init__(**kwargs)
        if self.processing_model is None:
            self.processing_model = processing_model
        self.data = None

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other._processing_model = deepcopy(self._processing_model, memo)
        other._processing_models = [
            deepcopy(p, memo) for p in self._processing_models
        ]
        return other

    @property
    def processing_model(self):
        return self._processing_model

    @processing_model.setter
    def processing_model(self, model):
        self._processing_model = model
        if model not in self._processing_models:
            self._processing_models.append(model)

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Return set of used input attributes of project data.

        This set contains all input attributes used at least once in a
        processing model of the project data.

        :return: used input attributes
        """
        attributes = set()
        for model in self._processing_models:
            attributes |= model._get_used_input_attributes()
        return attributes

    def _explain_uptodate(self, feature: Feature) -> dict:
        """Explain uptodate feature values wrt the project data.

        :param feature: feature part of the project data
        :return: explanation as a dict
        """
        return self.processing_model.explain(feature)


@db.event.listens_for(DataGenerator.name, "set", propagate=True)
def generator_name_set(target, value, oldvalue, initiator):
    """Event to modify the generated geo-data name when the project data name
    is modified"""
    if value != oldvalue and target.data is not None:
        target.data.name = value
