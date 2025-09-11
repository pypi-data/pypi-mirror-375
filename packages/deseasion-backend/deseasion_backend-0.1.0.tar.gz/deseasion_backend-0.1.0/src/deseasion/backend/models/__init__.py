from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(None, metadata=metadata)

from .geo_data import (  # noqa: E402
    AttributeType,
    BaseData,
    BaseGeoData,
    DataAttribute,
    DataAttributeNominal,
    DataAttributeOrdinal,
    DataAttributeQuantitative,
    DataValue,
    Feature,
    FeatureType,
    GeneratedGeoData,
    GeoData,
    GeoDataType,
    GeoFeature,
    GlobalData,
    StreamGeoData,
    WFSGeoData,
    WMSGeoData,
)
from .permission import PermissionAbility, UserPermission  # noqa: E402
from .processing_models import (  # noqa: E402
    ContinuousRule,
    DiscreteCategory,
    DiscreteRules,
    DiscreteRulesCategory,
    GeoBuffer,
    KeepOverlap,
    ModelType,
    MRSort,
    MRSortCriterion,
    ProcessingModel,
)
from .project import Project, Template  # noqa: E402
from .project_data import (  # noqa: E402
    DataGenerator,
    DataGeo,
    DataStream,
    DataType,
    DynamicData,
    ProjectData,
    ProjectGlobalData,
)
from .share import DataShare  # noqa: E402
from .tasks import ProjectTaskModel, ProjectTaskType  # noqa: E402
from .user import User  # noqa: E402

__all__ = [
    "AttributeType",
    "BaseData",
    "BaseGeoData",
    "DataAttribute",
    "DataAttributeNominal",
    "DataAttributeOrdinal",
    "DataAttributeQuantitative",
    "DataValue",
    "Feature",
    "FeatureType",
    "GeneratedGeoData",
    "GeoData",
    "GeoDataType",
    "GeoFeature",
    "GlobalData",
    "GeoDataType",
    "StreamGeoData",
    "WFSGeoData",
    "WMSGeoData",
    "PermissionAbility",
    "UserPermission",
    "ContinuousRule",
    "DiscreteCategory",
    "DiscreteRules",
    "DiscreteRulesCategory",
    "GeoBuffer",
    "KeepOverlap",
    "MRSort",
    "MRSortCriterion",
    "ProcessingModel",
    "ModelType",
    "Project",
    "Template",
    "DataGenerator",
    "DataGeo",
    "DataType",
    "ProjectData",
    "ProjectGlobalData",
    "DataStream",
    "DynamicData",
    "DataShare",
    "ProjectTaskModel",
    "ProjectTaskType",
    "User",
]
