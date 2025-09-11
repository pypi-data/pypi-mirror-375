from .geo_data import (
    DataService,
    GeoDataService,
    GlobalDataService,
    StreamGeoDataService,
)
from .processing_model import ProcessingModelService
from .project import ProjectService
from .project_data import ProjectDataService

project_service = ProjectService()
project_data_service = ProjectDataService()
data_service = DataService()
geo_data_service = GeoDataService()
geo_data_stream_service = StreamGeoDataService()
processing_model_service = ProcessingModelService()
get_global_data_service = GlobalDataService()
