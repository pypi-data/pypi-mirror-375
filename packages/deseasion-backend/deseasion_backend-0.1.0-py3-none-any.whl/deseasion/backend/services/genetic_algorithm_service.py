from collections import defaultdict
from functools import partial

import geopandas as gpd
import pyproj
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import box
from shapely.ops import transform

from ..exceptions import ProcessingError
from ..models.genetic_algorithm import GAContext, GeneticAlgorithm
from ..models.geo_data import (
    AttributeType,
    DataAttributeQuantitative,
    GeoFeature,
)


def get_smallest_bounds(geometry_extent, project_extent, proj="epsg:3857"):
    """Return the bounds of the intersection of the two geometries."""
    proj_wgs84 = pyproj.Proj(init="epsg:4326")
    proj_other = pyproj.Proj(proj)
    project_to_wgs84 = partial(
        pyproj.transform, proj_other, proj_wgs84, always_xy=True
    )
    project_to_other = partial(
        pyproj.transform, proj_wgs84, proj_other, always_xy=True
    )
    b1 = transform(project_to_wgs84, geometry_extent)
    intersection = b1.intersection(project_extent)
    bounds = transform(project_to_other, intersection).bounds
    return bounds


def ga_context_from_decision_map(decision_map, geo_size, proj="epsg:3857"):
    proj_in = pyproj.Proj(init="epsg:4326")
    proj_out = pyproj.Proj(proj)
    project = partial(pyproj.transform, proj_in, proj_out)

    geo_data = decision_map.data
    attribute = geo_data.attributes[0]  # TODO: Allow to choose the attribute
    if attribute.type not in (
        AttributeType.ordinal,
        AttributeType.quantitative,
    ):
        raise ProcessingError("The attribute is not a number or a category")
    data = defaultdict(list)
    input_features = []
    for feature in geo_data.features:
        if proj_in.is_exact_same(proj_out):
            geometry = to_shape(feature.geom)
        else:
            geometry = transform(project, to_shape(feature.geom))
        geometry = geometry.buffer(
            0
        )  # use a buffer to correct invalid geometries
        value = next(
            p.value for p in feature.properties if p.attribute is attribute
        )
        input_features.append(feature)
        data["geometry"].append(geometry)
        if attribute.type is AttributeType.ordinal:
            data["value"].append(
                len(attribute.order) - attribute.order.index(value)
            )
        elif attribute.type is AttributeType.quantitative:
            data["value"].append(value)
    project_extent = to_shape(decision_map.project.extent)
    df = gpd.GeoDataFrame(data)
    not_empty = df[~df.geometry.is_empty]
    geoms_bounds = box(*not_empty.total_bounds)
    bounds = get_smallest_bounds(geoms_bounds, project_extent, proj)
    ga_ctx = GAContext(
        df, input_features, geo_size=geo_size, bounds=bounds, proj=proj
    )
    return ga_ctx


def ga_parametrized(context, params):
    return GeneticAlgorithm(context, **params)


def zone_proposition_from_genetic_algorithm(genetic_algorithm):
    features = []
    population = genetic_algorithm.filter_best()
    attribute = DataAttributeQuantitative(name="fitness")
    value_cls = attribute.get_value_class()
    for individual in population.individuals:
        value = value_cls(value=individual.fitness, attribute=attribute)
        feature = GeoFeature(
            from_shape(individual.as_geometry(proj="epsg:4326"), srid=4326),
            properties=[value],
        )
        features.append(feature)
    return features
