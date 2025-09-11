import enum
import numbers
from copy import copy, deepcopy
from datetime import datetime
from functools import total_ordering
from typing import Type

import simplejson as json
from geoalchemy2.shape import to_shape
from geoalchemy2.types import Geometry
from pandas import DataFrame
from shapely.geometry import mapping
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from . import db
from .mixins import ModelMixin, TimestampMixin
from .permission import HasPermissions


class GeoDataType(enum.Enum):
    geo_data = 1
    generated_geo_data = 2
    global_data = 3
    wfs = 4
    wms = 5


class BaseData(HasPermissions, TimestampMixin, db.Model):
    type = db.Column(db.Enum(GeoDataType))  # inheritance discriminator
    name = db.Column(db.String, nullable=False)
    original_name = db.Column(db.String)
    description = db.Column(db.String)
    _properties_modified_at = db.Column("properties_modified_at", db.DateTime)

    attributes = db.relationship(
        "DataAttribute", back_populates="data", cascade="all,delete-orphan"
    )

    features = db.relationship(
        "Feature", back_populates="data", cascade="all,delete-orphan"
    )
    shares = db.relationship(
        "DataShare", cascade="all,delete-orphan", back_populates="data"
    )

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, name, features=[], description=None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.features = features
        self.description = description

    def __repr__(self):
        return "<BaseData(name={})>".format(self.name)

    def __deepcopy__(self, memo):
        cls = type(self)
        other = cls(
            name=self.name,
        )
        memo[id(self)] = other
        return other

    def load_properties(self, force=False):
        """Load the model properties and save them to the database

        Args:
            force (bool): to force the loading of the properties
        """
        if (
            force
            or self.modified_at is None
            or self._properties_modified_at is None
            or self._properties_modified_at < self.modified_at
        ):
            for attribute in self.attributes:
                attribute.load_statistics()
            self._properties_modified_at = datetime.utcnow()
            self.save()


class BaseGeoData(BaseData):
    extent_filter = db.Column(Geometry)
    extent = db.Column(Geometry)

    @declared_attr
    def features(cls):
        return db.relationship(
            "GeoFeature", back_populates="data", cascade="all,delete-orphan"
        )

    __mapper_args__ = {"polymorphic_abstract": True}

    def __repr__(self):
        return "<BaseGeoData(name={})>".format(self.name)

    def __deepcopy__(self, memo):
        cls = type(self)
        other = cls(
            name=self.name,
        )
        memo[id(self)] = other
        other.features = [deepcopy(f, memo) for f in self.features]
        return other

    def as_geojson(self):
        features_geojson = [f.as_geojson() for f in self.features]
        collection = {
            "type": "FeatureCollection",
            "features": features_geojson,
        }
        return collection

    def load_extent(self):
        self.extent = (
            db.session.query(
                db.func.st_envelope(db.func.st_collect(GeoFeature.geom))
            )
            .filter_by(data_id=self.id)
            .one()[0]
        )

    def load_properties(self, force=False):
        """Load the model properties and save them to the database

        Args:
            force (bool): to force the loading of the properties
        """
        if (
            force
            or self.modified_at is None
            or self._properties_modified_at is None
            or self._properties_modified_at < self.modified_at
        ):
            self.load_extent()
            for attribute in self.attributes:
                attribute.load_statistics()
            self._properties_modified_at = datetime.utcnow()
            self.save()


class UploadableData:
    upload_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    @declared_attr
    def _upload_user(cls):
        return db.relationship("User")

    @hybrid_property
    def upload_user(self):
        return self._upload_user

    @upload_user.setter
    def upload_user(self, user):
        """Make sure that the user has permissions on the data."""
        self._upload_user = user
        if user is not None:
            self.permissions.append(type(self).Permission(user=user))


class StreamGeoData:
    title = db.Column(db.String)
    url = db.Column(db.String, nullable=False)
    keywords = db.Column(ARRAY(db.String, dimensions=1))
    version = db.Column(db.String)


class WFSGeoData(UploadableData, StreamGeoData, BaseGeoData):
    __tablename__ = "wfs_geo_data"

    id = db.Column(db.Integer, db.ForeignKey("base_data.id"), primary_key=True)
    feature_type = db.Column(db.String, nullable=False)

    __mapper_args__ = {"polymorphic_identity": GeoDataType.wfs}

    def __init__(
        self,
        url: str,
        feature_type: str,
        name: str = None,
        original_name: str = None,
        is_public: bool = False,
        title: str = None,
        description: str = None,
        keywords: list = None,
        **kwargs,
    ):
        super().__init__(
            name=(name or feature_type),
            is_public=is_public,
            description=description,
            **kwargs,
        )
        self.url = url
        self.original_name = original_name
        self.title = title
        self.keywords = keywords if keywords else []
        self.feature_type = feature_type

    def __repr__(self):
        return "<WFSGeoData(name={})>".format(self.name)

    def __deepcopy__(self, memo):
        print("{}".format(self.name))
        memo[id(self)] = self
        return self


class WMSGeoData(UploadableData, StreamGeoData, BaseGeoData):
    __tablename__ = "wms_geo_data"

    id = db.Column(db.Integer, db.ForeignKey("base_data.id"), primary_key=True)
    classes = db.Column(ARRAY(db.Float, dimensions=2))
    start = db.Column(db.Float)
    step = db.Column(db.Float)
    stop = db.Column(db.Float)
    layer = db.Column(db.String, nullable=False)
    resolution = db.Column(db.Float)

    __mapper_args__ = {"polymorphic_identity": GeoDataType.wms}

    def __init__(
        self,
        url: str,
        layer: str,
        name: str = None,
        original_name: str = None,
        is_public: bool = False,
        title: str = None,
        description: str = None,
        keywords: list = None,
        classes: list[list[float]] = None,
        start: float = None,
        step: float = None,
        stop: float = None,
        **kwargs,
    ):
        super().__init__(
            name=(name or layer),
            is_public=is_public,
            description=description,
            **kwargs,
        )
        self.url = url
        self.original_name = original_name
        self.title = title
        self.keywords = keywords if keywords else []
        self.layer = layer
        self.classes = classes
        self.start = start
        self.step = step
        self.stop = stop

    def __repr__(self):
        return "<WMSGeoData(name={})>".format(self.name)

    def __deepcopy__(self, memo):
        print("{}".format(self.name))
        memo[id(self)] = self
        return self


class GlobalData(UploadableData, BaseData):
    __tablename__ = "global_data"

    id = db.Column(db.Integer, db.ForeignKey("base_data.id"), primary_key=True)
    feature_id = db.Column(db.Integer, db.ForeignKey("feature.id"))
    feature = db.relationship(
        "Feature",
        cascade="all",
        primaryjoin="global_data.c.feature_id == feature.c.id",
        post_update=True,
    )
    properties = db.relationship(
        "DataValue",
        cascade="all",
        primaryjoin=(
            "global_data.c.feature_id == foreign(data_value.c.feature_id)"
        ),
        post_update=True,
    )

    __mapper_args__ = {"polymorphic_identity": GeoDataType.global_data}

    def __init__(self, feature, **kwargs):
        super().__init__(**kwargs)
        self.feature = feature

    def __repr__(self):
        properties = {val.attribute.name: val.value for val in self.properties}
        return f"<GlobalData(name={self.name}, properties={properties})>"

    def __deepcopy__(self, memo):
        print("{}".format(self.name))
        memo[id(self)] = self
        return self

    def get_property(self, prop):
        """Returns the value of the property"""
        return self.feature.get_property(prop)

    def _choose_attribute_type(self, value) -> Type["DataAttribute"]:
        """Create new DataValue and DataAttribute based on value.

        :param prop: property name (attribute name)
        :param value:
        :return: created data value object (not persisted yet!)
        """
        match value:
            case int() | float():
                return DataAttributeQuantitative
            case _:
                return DataAttributeNominal

    def set_property(self, prop, value):
        """Set property value.

        Try to reuse existing attribute if type matches.

        :param prop: property name (attribute name)
        :param value: new property value
        """
        old_prop = None
        for p in self.properties:
            if p.attribute.name == prop:
                old_prop = p
                break
        attr_type = self._choose_attribute_type(value)
        if old_prop is None or not isinstance(old_prop.attribute, attr_type):
            attr = attr_type(name=prop, data=self)
            db.session.add(attr)
        else:
            attr = old_prop.attribute
            db.session.delete(old_prop)
        db.session.add(
            attr.get_value_class()(
                value=value, attribute=attr, feature=self.feature
            )
        )
        db.session.commit()


class GeoData(UploadableData, BaseGeoData):
    """Table for the geographical data loaded from files.

    Attributes:
        original_name (str): The name of the file.
        source_driver (str): Which format the original data used.
        upload_user_id (int): Reference to the user who uploaded the data.
        description (str): A description text.
    """

    __tablename__ = "geo_data"

    id = db.Column(db.Integer, db.ForeignKey("base_data.id"), primary_key=True)
    source_driver = db.Column(db.String)

    __mapper_args__ = {"polymorphic_identity": GeoDataType.geo_data}

    def __init__(
        self,
        *args,
        original_name=None,
        source_driver=None,
        is_public=False,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.original_name = original_name
        self.source_driver = source_driver
        self.is_public = is_public

    def __deepcopy__(self, memo):
        print("{}".format(self.name))
        memo[id(self)] = self
        return self

    def __repr__(self):
        return "<GeoData(name={}, source_driver={})>".format(
            self.name, self.source_driver
        )


class GeneratedGeoData(BaseGeoData):
    """Table for the geographical data generated by the processing model in the
    projects."""

    __mapper_args__ = {"polymorphic_identity": GeoDataType.generated_geo_data}

    project_data = db.relationship(
        "DynamicData",
        uselist=False,
        foreign_keys="DynamicData.data_id",
    )

    def __repr__(self):
        return "<GeneratedGeoDate(name={})>".format(self.name)

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.features = [deepcopy(f, memo) for f in self.features]
        other.project_data = deepcopy(self.project_data, memo)
        return other


class AttributeType(enum.Enum):
    quantitative = 1
    nominal = 2
    ordinal = 3


class DataAttribute(ModelMixin, db.Model):
    __tablename__ = "data_attribute"

    type = db.Column(db.Enum(AttributeType))
    name = db.Column(db.String, nullable=False)
    statistics = db.Column(JSONB)
    data_id = db.Column(
        db.Integer, db.ForeignKey("base_data.id"), nullable=False, index=True
    )

    data = db.relationship("BaseData", back_populates="attributes")
    values = db.relationship(
        "DataValue", back_populates="attribute", cascade="all,delete-orphan"
    )

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, **kwargs):
        print("Attribute {} created".format(kwargs.get("name")))
        super().__init__(**kwargs)

    def __deepcopy__(self, memo):
        if self.data.type is GeoDataType.geo_data:
            memo[id(self)] = self
            return self
        else:
            cls = type(self)
            other = cls(
                name=self.name,
            )
            memo[id(self)] = other
            other.name = self.name
            other.data = deepcopy(
                self.data, memo
            )  # TODO: do not duplicate data
            other.values = [deepcopy(v, memo) for v in self.values]
            return other

    def new_copy(self):
        cls = self.__class__
        return cls(type=self.type, name=self.name)

    def load_statistics(self):
        """Load statistics about the attribute values.

        The stats are calculated using pandas' describe function.
        """
        values = [v.value for v in self.values]
        self.statistics = {"total": len(values)}
        df = DataFrame(values)
        if len(values) > 0 and len(df.columns) > 0:
            stats = df.describe(include="all")
            stats_dict = json.loads(stats[0].to_json())
            for key, value in stats_dict.items():
                if "%" in key:
                    self.statistics.setdefault("percentiles", {})[key] = value
                else:
                    self.statistics[key] = value

    def get_value_class(self):
        raise NotImplementedError

    def same_as(self, other) -> bool:
        """Check attribute is same as other.

        :param other: other data attribute or ``None``
        :return: ``True`` if they are the same, ``False`` otherwise

        .. warning:: This does not check values or statistics
        """
        return (
            isinstance(other, DataAttribute)
            and self.type == other.type
            and self.name == other.name
        )


class DataAttributeQuantitative(DataAttribute):
    __mapper_args__ = {"polymorphic_identity": AttributeType.quantitative}

    def get_value_class(self):
        return DataValueQuantitative


class DataAttributeNominal(DataAttribute):
    __mapper_args__ = {"polymorphic_identity": AttributeType.nominal}

    def get_value_class(self):
        return DataValueNominal


class DataAttributeOrdinal(DataAttribute):
    order = db.Column(JSONB)  # maybe not the best type?

    __mapper_args__ = {"polymorphic_identity": AttributeType.ordinal}

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.order = copy(self.order)
        return other

    def new_copy(self):
        obj = super().new_copy()
        obj.order = list(self.order)
        return obj

    def get_value_class(self):
        return DataValueOrdinal

    def same_as(self, other) -> bool:
        """Check attribute is same as other.

        :param other: other data attribute or ``None``
        :return: ``True`` if they are the same, ``False`` otherwise

        .. warning:: This does not check values or statistics
        """
        return super().same_as(other) and self.order == other.order


@total_ordering
class DataValue(ModelMixin, db.Model):
    __tablename__ = "data_value"

    type = db.Column(db.Enum(AttributeType))
    attribute_id = db.Column(
        db.Integer, db.ForeignKey("data_attribute.id"), index=True
    )
    feature_id = db.Column(
        db.Integer, db.ForeignKey("feature.id", ondelete="CASCADE"), index=True
    )
    value = db.Column(JSONB)

    __table_args__ = (db.UniqueConstraint("attribute_id", "feature_id"),)
    __mapper_args__ = {"polymorphic_on": type}

    attribute = db.relationship("DataAttribute", back_populates="values")
    feature = db.relationship("Feature", back_populates="properties")

    def __hash__(self):
        return hash((self.id, self.attribute_id, self.feature_id, self.value))

    def __lt__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.value = copy(self.value)
        other.attribute = deepcopy(self.attribute, memo)
        other.feature = deepcopy(self.feature, memo)
        return other


class DataValueQuantitative(DataValue):
    __mapper_args__ = {"polymorphic_identity": AttributeType.quantitative}

    def _check_type(self, other):
        if isinstance(other, DataValueQuantitative) is False:
            raise TypeError

    def __hash__(self):
        return super().__hash__()

    def __add__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(value=self.value + other)
        elif isinstance(other, DataValueQuantitative):
            return self.__class__(value=self.value + other.value)
        else:
            return NotImplemented

    def __radd__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(value=self.value + other)
        elif isinstance(other, DataValueQuantitative):
            return self.__class__(value=self.value + other.value)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return self.__class__(value=(self.value / other))
        elif isinstance(other, DataValueQuantitative):
            return self.__class__(value=(self.value / other.value))
        else:
            return NotImplemented

    def __lt__(self, other):
        """Check if self < other."""
        self._check_type(other)
        return self.value < other.value

    def __eq__(self, other):
        """Check if self == other."""
        self._check_type(other)
        return self.value == other.value


class DataValueNominal(DataValue):
    __mapper_args__ = {"polymorphic_identity": AttributeType.nominal}

    def _check_type(self, other):
        if isinstance(other, DataValueNominal) is False:
            raise TypeError

    def __hash__(self):
        return super().__hash__()

    def __lt__(self, other):
        """Check if self < other."""
        raise TypeError

    def __eq__(self, other):
        """Check if self == other."""
        self._check_type(other)
        return self.value == other.value


class DataValueOrdinal(DataValue):
    __mapper_args__ = {"polymorphic_identity": AttributeType.ordinal}

    def _check_type(self, other):
        if (
            isinstance(self.attribute, DataAttributeOrdinal) is False
            or self.attribute is not other.attribute
        ):
            raise TypeError

    def __hash__(self):
        return super().__hash__()

    def __lt__(self, other):
        """Check if self < other."""
        self._check_type(other)
        order = self.attribute.order
        return order.index(self.value) > order.index(other.value)

    def __eq__(self, other):
        """Check if self == other."""
        self._check_type(other)
        order = self.attribute.order
        return order.index(self.value) == order.index(other.value)


class FeatureType(enum.Enum):
    feature = 1
    geo_feature = 2


feature_input_assoc = db.Table(
    "feature_input_association",
    db.Model.metadata,
    db.Column(
        "feature_id",
        db.Integer,
        db.ForeignKey("feature.id"),
        primary_key=True,
    ),
    db.Column(
        "input_feature_id",
        db.Integer,
        db.ForeignKey("feature.id"),
        primary_key=True,
    ),
)


class Feature(ModelMixin, db.Model):
    """Table for the data features.

    Attributes:
        properties (dict): The properties or attributes of the feature.
        data_id (int): Reference to the data.
    """

    __tablename__ = "feature"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(FeatureType))  # inheritance discriminator
    data_id = db.Column(
        db.Integer, db.ForeignKey("base_data.id"), nullable=False
    )
    execution_artifact = db.Column(JSONB)
    input_features = db.relationship(
        "Feature",
        secondary=feature_input_assoc,
        primaryjoin=(id == feature_input_assoc.c.feature_id),
        secondaryjoin=(id == feature_input_assoc.c.input_feature_id),
        backref="output_features",
        order_by=feature_input_assoc.c.input_feature_id,
    )

    data = db.relationship("BaseData", back_populates="features")
    properties = db.relationship(
        "DataValue", back_populates="feature", cascade="all,delete-orphan"
    )

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": FeatureType.feature,
    }

    def __init__(
        self,
        *args,
        properties=[],
        execution_artifact=None,
        input_features=[],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.execution_artifact = execution_artifact or {}
        self.properties = properties
        self.input_features = input_features

    def __deepcopy__(self, memo):
        cls = type(self)
        other = cls(execution_artifact=copy(self.execution_artifact))
        memo[id(self)] = other
        other.data = deepcopy(self.data, memo)
        other.properties = [deepcopy(p, memo) for p in self.properties]
        return other

    def get_property(self, prop):
        """Returns the value of the property"""
        for p in self.properties:
            if p.attribute.name == prop:
                return p.value

    def get_input_data(self):
        """Returns the list of input data."""
        input_data = set()
        for feature in self.input_features:
            input_data.add(feature.data)
        return sorted(input_data, key=lambda d: d.id)

    def get_input_features(self, data_id):
        """Returns the input features belonging to provided data."""
        return [
            feature
            for feature in self.input_features
            if feature.data_id == data_id
        ]

    def get_output_data(self):
        """Returns the list of output data."""
        output_data = set()
        for feature in self.output_features:
            output_data.add(feature.data)
        return sorted(output_data, key=lambda d: d.id)

    def get_output_features(self, data_id):
        """Returns the output features belonging to provided data."""
        return [
            feature
            for feature in self.output_features
            if feature.data_id == data_id
        ]

    def explain(self):
        """Return explanation for feature values.

        This is empty except for generated geo data features.

        :return:
        """
        if self.data.type != GeoDataType.generated_geo_data:
            return {}
        return self.data.project_data.explain(self)


class GeoFeature(Feature):
    """Table for the geo-data features.

    Attributes:
        geom: The geometry of the feature.
        properties (dict): The properties or attributes of the feature.
        data_id (int): Reference to the geo-data.
    """

    __tablename__ = "geo_feature"

    id = db.Column(db.Integer, db.ForeignKey("feature.id"), primary_key=True)
    data = db.relationship("BaseGeoData", back_populates="features")
    geom = db.Column(Geometry)

    __mapper_args__ = {"polymorphic_identity": FeatureType.geo_feature}

    def __init__(self, geom, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geom = geom

    def as_geojson(self):
        """Return the feature as a GeoJSON data."""
        geometry = mapping(to_shape(self.geom))
        geojson = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {p.attribute.name: p.value for p in self.properties},
        }
        return geojson

    def __deepcopy__(self, memo):
        cls = type(self)
        other = cls(
            geom=copy(self.geom),
            execution_artifact=copy(self.execution_artifact),
        )
        memo[id(self)] = other
        other.data = deepcopy(self.data, memo)
        other.properties = [deepcopy(p, memo) for p in self.properties]
        return other
