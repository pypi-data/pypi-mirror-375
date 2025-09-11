import time
from collections import defaultdict

import numpy as np
from flask import current_app as app
from geoalchemy2 import Geography, Geometry
from geoalchemy2.shape import from_shape, to_shape
from pandas import DataFrame
from rtree import index as rindex
from shapely.errors import TopologicalError
from shapely.geometry import MultiPolygon, Polygon
from shapely.geometry.base import BaseMultipartGeometry
from shapely.ops import unary_union
from shapely.prepared import prep

from ..exceptions import ProcessingError
from ..services import genetic_algorithm_service as ga_service
from ..services.geo_data_loading_service import post_load_normalization
from . import db
from .genetic_algorithm import GeneticAlgorithm
from .geo_data import (
    DataAttributeNominal,
    DataAttributeOrdinal,
    DataAttributeQuantitative,
    GeneratedGeoData,
    GeoFeature,
    GlobalData,
)
from .processing_model_utils import evaluate_continuous_rule
from .processing_models import (
    ContinuousRule,
    DiscreteRules,
    DissolveAdjacentModel,
    GeoBuffer,
    MergeOverlapModel,
    MRSort,
    PrefDefaultValues,
    WeightedSum,
    ZonePropositionGenerator,
)


def check_geom_type(geom):
    result = None
    if geom.type == "Polygon":
        result = geom
    elif (
        geom.type in ("MultiPolygon", "GeometryCollection")
        and not geom.is_empty
    ):
        geoms = []
        for g in geom.geoms:
            new_geom = check_geom_type(g)
            if new_geom is not None and not new_geom.is_empty:
                geoms.append(new_geom)
        if len(geoms) == 1:
            result = geoms[0]
        elif len(geoms) > 1:
            result = MultiPolygon(geoms)
    if result is not None and result.area <= 1e-08:
        result = None
    if result is not None:
        return result.buffer(0)
    else:
        return Polygon()


class GeometryFeature:
    def __init__(self, ids, geometry):
        self.ids = frozenset(ids)
        self.geometry = geometry

    @classmethod
    def from_dict(cls, value):
        from shapely.wkt import loads

        return cls(ids=value["ids"], geometry=loads(value["geometry"]))

    def to_dict(self):
        from shapely.wkt import dumps

        return {"ids": list(self.ids), "geometry": dumps(self.geometry)}

    def intersection(self, other):
        ids = self.ids | other.ids
        try:
            geometry = self.geometry.intersection(other.geometry)
            return GeometryFeature(ids=ids, geometry=geometry)
        except TopologicalError:
            app.logger.warning(
                "Topological error in the intersection of {} and {}".format(
                    self.ids, other.ids
                )
            )
            return GeometryFeature(ids=ids, geometry=Polygon())

    def difference(self, other):
        ids = self.ids
        try:
            geometry = self.geometry.difference(other.geometry)
            return GeometryFeature(ids=ids, geometry=geometry)
        except TopologicalError:
            app.logger.warning(
                "Topological error in the intersection of {} and {}".format(
                    self.ids, other.ids
                )
            )
            return GeometryFeature(ids=ids, geometry=Polygon())

    def difference_union(self, geoms):
        ids = self.ids
        # FIXME: Fix the errors instead of simply ignoring them
        try:
            geom_union = unary_union([g.geometry for g in geoms])
        except ValueError:
            app.logger.warning(
                "Error in the union of geometries of {} and {}".format(
                    ids, [g.ids for g in geoms]
                )
            )
            return GeometryFeature(ids=ids, geometry=Polygon())
        if geom_union.is_empty:
            return GeometryFeature(ids=ids, geometry=self.geometry)
        try:
            geometry = self.geometry.difference(geom_union)
        except TopologicalError:
            app.logger.warning(
                "Topological error in the difference of {} and {}".format(
                    ids, [g.ids for g in geoms]
                )
            )
            return GeometryFeature(ids=ids, geometry=Polygon())
        return GeometryFeature(ids=ids, geometry=geometry)

    def split_multi_geometries(self) -> list["GeometryFeature"]:
        match self.geometry:
            case BaseMultipartGeometry():
                res = []
                for g in self.geometry.geoms:
                    res.append(GeometryFeature(self.ids, g))
                return res
            case _:
                return [self]

    def is_valid(self):
        return self.geometry.is_valid

    def is_empty(self):
        return self.geometry.is_empty

    def intersects(self, other):
        return self.geometry.intersects(other.geometry)

    def touches(self, other):
        return self.geometry.touches(other.geometry)


class ModelProcessingService:
    def decompose(self, geometries_1, geometries_2, r_tree1, feedback):
        geoms = []
        rtree_final = rindex.Index()

        def add_geometry(geom):
            g = check_geom_type(geom.geometry)
            if g is None or g.is_empty:
                return
            geom.geometry = g
            for _geom in geom.split_multi_geometries():
                rtree_final.insert(len(geoms), _geom.geometry.bounds)
                geoms.append(_geom)

        count = 0
        total = len(geometries_1) + len(geometries_2)

        r_tree2 = rindex.Index()
        for id2, geom2 in enumerate(geometries_2):
            r_tree2.insert(id2, geom2.geometry.bounds)
            prepared_geom2 = prep(geom2.geometry)
            geoms1 = []
            for id1 in r_tree1.intersection(geom2.geometry.bounds):
                if prepared_geom2.intersects(geometries_1[id1].geometry):
                    g = geom2.intersection(geometries_1[id1])
                    add_geometry(g)
                    geoms1.append(geometries_1[id1])
            g = geom2.difference_union(geoms1)
            add_geometry(g)
            count += 1
            feedback.set_progress(count, total)

        for geom1 in geometries_1:
            prepared_geom1 = prep(geom1.geometry)
            geoms2 = [
                geometries_2[id2]
                for id2 in r_tree2.intersection(geom1.geometry.bounds)
                if prepared_geom1.intersects(geometries_2[id2].geometry)
            ]
            g = geom1.difference_union(geoms2)
            add_geometry(g)
            count += 1
            feedback.set_progress(count, total)

        return geoms, rtree_final

    def buffer_geometries(self, distance, geometries):
        """Create a buffer around the geometries.

        The geometries are cast to a geography type in PostGIS, allowing to use
        a distance in metres for the buffer.

        Args:
            distance: The distance of the buffer.
            geometries (iterable): Iterable of GeometryFeature objects

        Returns:
            A new list of GeometryFeature objects with a buffer around the
            geometries.
        """
        q = db.select(
            db.cast(
                db.func.st_buffer(
                    db.cast(db.column("geom"), Geography), distance
                ),
                Geometry,
            )
        )
        q = q.select_from(
            db.func.unnest([g.geometry.wkt for g in geometries]).alias("geom")
        )
        result = db.session.execute(q).fetchall()
        buffered = [
            GeometryFeature(g.ids, to_shape(res[0]))
            for g, res in zip(geometries, result)
        ]
        return buffered

    def _get_default_values(self, model):
        values = {}
        for d in model.input_data:
            if d.data is not None:
                attrs = d.data.attributes
                attributes = {}
                for attr in attrs:
                    value = None
                    if isinstance(model, PrefDefaultValues):
                        # replace by default values
                        value = model.get_default_value(attr)
                    attributes[attr.name] = value
                values[d.name] = {
                    "properties": {"area": None},
                    "attributes": attributes,
                }
        return values

    def _get_sandbox_data(self, model, geometries, input_features):
        features_ids = frozenset.union(*(g.ids for g in geometries))
        q = db.session.query(
            GeoFeature, db.func.st_area(db.cast(GeoFeature.geom, Geography))
        )
        q = q.filter(GeoFeature.id.in_(list(features_ids)))
        q_result = q.all()

        features_data = {}
        project_data_names = {
            d.data.id: d.name for d in model.input_data if d.data is not None
        }
        default_values = self._get_default_values(model)

        for f, area in q_result:
            properties = {"area": area}
            attributes = {p.attribute.name: p.value for p in f.properties}
            if isinstance(model, ContinuousRule):
                # replace None by default values
                for p in f.properties:
                    if p.value is not None and not isinstance(p.value, float):
                        continue
                    if (
                        isinstance(p.value, float)
                        and p.value == p.value
                        and p.value != float("inf")
                        and p.value != -float("inf")
                    ):
                        continue
                    attr = p.attribute
                    attributes[attr.name] = model.get_default_value(attr)
            features_data[f.id] = {
                "name": project_data_names[f.data.id],
                "data": {"properties": properties, "attributes": attributes},
            }

        for fId in features_ids - set(features_data.keys()):
            f = input_features[fId]
            properties = {"area": None}
            attributes = {p.attribute.name: p.value for p in f.properties}
            if isinstance(model, ContinuousRule):
                # replace None by default values
                for p in f.properties:
                    if p.value is not None and not isinstance(p.value, float):
                        continue
                    if (
                        isinstance(p.value, float)
                        and p.value == p.value
                        and p.value != float("inf")
                        and p.value != -float("inf")
                    ):
                        continue
                    attr = p.attribute
                    attributes[attr.name] = model.get_default_value(attr)
            features_data[f.id] = {
                "name": project_data_names[f.data.id],
                "data": {"properties": properties, "attributes": attributes},
            }

        process_list = []
        areas = self.get_geometries_area(geometries)
        for g, area in zip(geometries, areas):
            data = {}
            data[model.data_generator.name] = {
                "properties": {"area": area},
                "attributes": {},
            }
            for f_id in g.ids:
                feature = features_data[f_id]
                data[feature["name"]] = feature["data"]
            for k, v in default_values.items():
                if k not in data:
                    data[k] = v
            process_list.append(data)

        return process_list

    def _get_attributes_stats(self, model):
        """
        Return the statistics of the input data attributes.

        The statistics are returned as a dictionary containing the stats in the
        form {'data name': {'attribute name': {'stat1': value, 'stat2': value,
        ...}}}

        The returned statistics are 'min', 'max', 'mean', 'std' and 'count' if
        they already exist in the attribute.
        Percentiles are also returned from 'percentile_0' to 'percentile_100'.
        """
        input_attributes = []
        for data in model.input_data:
            if data.data is not None:
                input_attributes += data.data.attributes
        stats = defaultdict(dict)
        for attr in input_attributes:
            keys = ["min", "max", "mean", "std", "count"]
            if attr.statistics is not None:
                attr_stat = {}
                for stat_key, stat_val in attr.statistics.items():
                    if stat_key in keys:
                        keys.remove(stat_key)
                        attr_stat[stat_key] = stat_val
                try:
                    df = DataFrame([v.value for v in attr.values])
                    series = df.quantile(np.arange(0, 1.01, 0.01))[0]
                    for k, v in series.items():
                        attr_stat["percentile_{}".format(int(k * 100))] = v
                except (TypeError, ValueError):
                    app.logger.info(
                        "The attribute is not a number, percentiles ignored"
                    )
                stats[attr.data.name][attr.name] = attr_stat
        return dict(stats) if len(stats) > 0 else None

    def _get_inference_data(self, model, geometries, features):
        attributes = []
        for d in model.input_data:
            if d.data is not None:
                attributes += d.data.attributes
        data_list = []
        for geometry in geometries:
            data = {a: None for a in attributes}
            for f_id in geometry.ids:
                feature = features.get(f_id)
                for value in feature.properties:
                    data[value.attribute] = value.value
            data_list.append(data)
        return data_list

    def _get_result_attributes(self, result_list, model):
        old_attrs = {}
        if model.data_generator.data is not None:
            old_attrs = {
                a.name: a for a in model.data_generator.data.attributes
            }
        is_quantitative = (
            lambda v: isinstance(v, int) or isinstance(v, float) or v is None
        )
        attrs = {}
        for properties in result_list:
            for name, value in properties.items():
                if name not in attrs:
                    if is_quantitative(value):
                        new = DataAttributeQuantitative(name=name)
                    else:
                        new = DataAttributeNominal(name=name)
                    if name in old_attrs:
                        old = old_attrs[name]
                        if new.type == old.type:
                            new = old
                    attrs[name] = new
                if isinstance(
                    attrs[name], DataAttributeQuantitative
                ) and not is_quantitative(value):
                    attrs[name] = DataAttributeNominal(name=name)
        return attrs

    def get_decomposed_data(self, model):
        # TODO: Find a cleaner way to get the decomposed data values
        geometries, features = self._process_regular_geometries(model)
        return self._get_inference_data(model, geometries, features)

    def _process_rule(self, model, feedback):
        """Process a rule model."""
        geometries, features = self._process_regular_geometries(
            model, feedback
        )
        data_json = self._get_sandbox_data(model, geometries, features)
        data_stats = self._get_attributes_stats(model)
        result_list = evaluate_continuous_rule(
            data=data_json, rule=model.rule, stats=data_stats
        )
        attrs = self._get_result_attributes(result_list, model)
        new_features = []
        for result, g in zip(result_list, geometries):
            values = []
            input_features = [features[fid] for fid in g.ids]
            new_feature = GeoFeature(
                geom=from_shape(g.geometry, srid=4326),
                input_features=input_features,
            )
            for name, value in result.items():
                # Ignore null values
                if value is None:
                    continue
                attr = attrs[name]
                cls = attr.get_value_class()
                values.append(
                    cls(value=value, attribute=attr, feature=new_feature)
                )
            # If the feature has values
            if len(values) > 0:
                new_features.append(new_feature)
        return new_features

    def _process_model_buffer(self, model, feedback):
        """Copy the attributes from the geometries."""
        geometries, features_dict = self._process_buffer_geometry(
            model, feedback
        )
        geo_data = None
        for f in features_dict.values():
            if geo_data is None:
                geo_data = f.data
            else:
                assert geo_data is f.data
        old_attrs = {}
        if model.data_generator.data is not None:
            old_attrs = {
                a.name: a for a in model.data_generator.data.attributes
            }
        attrs = {}
        for a in geo_data.attributes:
            old_attr = old_attrs.get(a.name)
            attrs[a.id] = old_attr if a.same_as(old_attr) else a.new_copy()

        new_features = []
        for g in geometries:
            f_id = list(g.ids)[0]  # Copy attributes from the first geometry
            old_feature = features_dict[f_id]
            new_feature = GeoFeature(
                geom=from_shape(g.geometry, srid=4326),
                input_features=[old_feature],
            )
            new_props = []
            for v in old_feature.properties:
                cls = attrs[v.attribute_id].get_value_class()
                val = cls(
                    value=v.value,
                    attribute=attrs[v.attribute_id],
                    feature=new_feature,
                )
                new_props.append(val)
            new_features.append(new_feature)
        return new_features

    def _process_criteria_rules(self, model, feedback):
        """Process criteria rules.

        A category will be assigned for each of the resulting features, in a
        'category' attribute.

        Returns:
            A list of Feature objects.
        """
        geometries, features = self._process_regular_geometries(
            model, feedback
        )
        data_json = self._get_sandbox_data(model, geometries, features)
        data_stats = self._get_attributes_stats(model)
        results = []
        for category in model.categories:
            evaluation = category.evaluate_data(data_json, data_stats)
            results.append((category.name, category.rules, evaluation))
        final = np.ma.masked_all_like(data_json)
        final_rule = np.ma.masked_all_like(data_json)
        for categ, rules, evaluation in results:
            for rule, row in zip(rules, evaluation):
                mask = np.where(row & final.mask)
                final[mask] = categ
                final_rule[mask] = rule
        if np.ma.is_masked(final):
            raise ProcessingError("No rule validated")
        # TODO: Send a warning if several categories are valid
        # (r.count(True) > 1)
        order = [c.name for c in model.categories]
        attribute = DataAttributeOrdinal(name="category", order=order)
        if model.data_generator.data is not None:
            for attr in model.data_generator.data.attributes:
                if attribute.same_as(attr):
                    attribute = attr
                    break
        new_features = []
        for categ, rule, g, data in zip(
            final, final_rule, geometries, data_json
        ):
            input_features = [features[fid] for fid in g.ids]
            new_feature = GeoFeature(
                geom=from_shape(g.geometry, srid=4326),
                execution_artifact={"rule": rule},
                input_features=input_features,
            )
            cls = attribute.get_value_class()
            cls(value=categ, attribute=attribute, feature=new_feature)
            new_features.append(new_feature)
        return new_features

    def _process_mr_sort(self, model, feedback):
        """Process using the MR-Sort algorithm.

        Each resulting feature will be assigned a category by the MR-Sort
        algorithm, in a 'category' attribute.

        Returns:
            A list of Feature objects.
        """
        geometries, features = self._process_regular_geometries(
            model, feedback
        )
        data_json = self._get_sandbox_data(model, geometries, features)
        new_features = []
        order = [c.name for c in model.categories]
        attribute = DataAttributeOrdinal(name="category", order=order)
        if model.data_generator.data is not None:
            for attr in model.data_generator.data.attributes:
                if attribute.same_as(attr):
                    attribute = attr
                    break
        profiles = {}
        for criterion in model.criteria:
            for index, value in enumerate(criterion.profiles):
                if index not in profiles:
                    profiles[index] = []
                profiles[index].append(
                    (
                        criterion.attribute.data.name,
                        criterion.attribute.name,
                        value,
                    )
                )
        for data, g in zip(data_json, geometries):
            attributes = []
            input_features = [features[fid] for fid in g.ids]
            for d_name, props in data.items():
                if d_name == model.data_generator.name:
                    continue
                for prop, val in props["attributes"].items():
                    attributes.append((d_name, prop, val))
            category = model.check_category(attributes)
            new_feature = GeoFeature(
                geom=from_shape(g.geometry, srid=4326),
                input_features=input_features,
            )
            cls = attribute.get_value_class()
            props = [
                cls(
                    value=category.name,
                    attribute=attribute,
                    feature=new_feature,
                )
            ]
            new_features.append(new_feature)
        return new_features

    def _process_weighted_sum(self, model, feedback):
        geometries, features = self._process_regular_geometries(
            model, feedback
        )
        new_features = []
        attribute = DataAttributeQuantitative(name="result")
        if model.data_generator.data is not None:
            for attr in model.data_generator.data.attributes:
                if attribute.same_as(attr):
                    attribute = attr
                    break
        default_values = {
            d.attribute_id: d.value for d in model.default_values
        }
        for geom in geometries:
            value = None
            input_features = [features[fid] for fid in geom.ids]
            vals = {
                p.attribute_id: p.value
                for f in input_features
                for p in f.properties
            }
            for operand in model.operands:
                new_val = vals.get(operand.attribute_id)
                if new_val is None:
                    new_val = default_values.get(operand.attribute_id)
                if new_val is not None:
                    new_val = operand.weight * new_val
                    value = new_val if value is None else value + new_val
                else:
                    # Ignore the feature if there is no default value
                    value = None
                    break
            if value is not None:
                new_feature = GeoFeature(
                    geom=from_shape(geom.geometry, srid=4326),
                    input_features=input_features,
                )
                cls = attribute.get_value_class()
                props = [  # noqa: F841 (those props are persisted by ORM)
                    cls(value=value, attribute=attribute, feature=new_feature)
                ]
                new_features.append(new_feature)
        return new_features

    def _decompose_features(self, geometries: list[GeometryFeature], feedback):
        rtree = rindex.Index()
        geoms: dict[int, GeometryFeature] = {}

        def add_geometry(geom, id_=None):
            if id_ is not None and id_ in geoms:
                rtree.delete(id_, geoms[id_].geometry.bounds)
            ids_ = [] if id_ is None else [id_]
            # Split multi-part geometries on insertion/edition
            for _geom in geom.split_multi_geometries():
                id_ = ids_.pop() if len(ids_) > 0 else len(geoms)
                rtree.insert(id_, _geom.geometry.bounds)
                geoms[id_] = _geom

        for g in geometries:
            add_geometry(g)

        res = []
        id1 = -1
        feedback.set_message("Decomposing overlaps")
        while id1 < len(geoms) - 1:
            id1 += 1
            geom1 = geoms[id1]
            if geom1 is None:
                feedback.set_progress(id1, len(geoms))
                continue
            rtree.delete(id1, geom1.geometry.bounds)
            for id2 in rtree.intersection(geom1.geometry.bounds):
                geom2 = geoms[id2]
                try:
                    if not geom1.intersects(geom2):
                        continue

                    intersection = geom1.intersection(geom2)
                    intersection.geometry = check_geom_type(
                        intersection.geometry
                    )
                except TopologicalError:
                    intersection = None
                    app.logger.warning("Intersection error in the overlap")
                if intersection is not None and not intersection.is_empty():
                    add_geometry(intersection)
                else:
                    continue

                try:
                    g2diff = geom2.difference(geom1)
                    g2diff.geometry = check_geom_type(g2diff.geometry)
                except TopologicalError:
                    g2diff = None
                    app.logger.warning("Difference error in the overlap")
                if g2diff is not None and not g2diff.is_empty():
                    add_geometry(g2diff, id2)
                else:
                    rtree.delete(id2, geom2.geometry.bounds)
                    geoms[id2] = None

                try:
                    g1diff = geom1.difference(geom2)
                    g1diff.geometry = check_geom_type(g1diff.geometry)
                except TopologicalError:
                    g1diff = None
                    app.logger.warning("Difference error in the overlap")
                if g1diff is not None and not g1diff.is_empty():
                    geom1 = g1diff
                else:
                    geom1 = None
                    break
            if geom1 is not None:
                for geom in geom1.split_multi_geometries():
                    res.append(geom)
            feedback.set_progress(id1, len(geoms))
        feedback.forget_message()
        return res

    def _process_buffer_geometry(self, model, feedback):
        """Create a buffer around the geometries.

        Returns:
            A list of GeometryFeature and the dict of input features.
        """
        # Prepare the extent
        extent = to_shape(model.data_generator.project.extent)
        extent_prep = prep(extent)
        # Check the input data is correct
        if len(model.input_data) != 1:
            raise ProcessingError("Incorrect number of input data")
        input_data = model.input_data[0]
        if input_data.data is None:
            raise ProcessingError("No geometries for the input data")
        # Convert the features to Shapely geometries
        geoms = []
        features = {}
        for feature in input_data.data.features:
            geom = to_shape(feature.geom)
            geoms.append(GeometryFeature(ids=[feature.id], geometry=geom))
            features[feature.id] = feature
        # Buffer
        geometries = self.buffer_geometries(model.radius, geoms)
        # Filter the geometries that intersect with the extent
        filtered = []
        for geom in geometries:
            if extent_prep.intersects(geom.geometry):
                if model.cut_to_extent:
                    geom.geometry = geom.geometry.intersection(extent)
                filtered.append(geom)
        return filtered, features

    def _process_regular_geometries(self, model, feedback=None):
        """Decompose the geometries.

        .. todo:: rename to something like `flatten_geometry_sets`

        Returns:
            A list of GeometryFeature, and the dict of features
        """
        send_feedback = (
            (lambda *args, **kwargs: None)
            if feedback is None
            else feedback.set_message
        )
        # Prepare the extent
        extent = to_shape(model.data_generator.project.extent)
        extent_prep = prep(extent)
        # Convert the features to Shapely geometries and cut them to the extent
        # if needed
        input_geometries = []
        input_features = {}
        data_list = (i.data for i in model.input_data if i.data is not None)
        global_features_ids = []
        for data in data_list:
            if isinstance(data, GlobalData) and data.feature:
                input_features[data.feature.id] = data.feature
                global_features_ids.append(data.feature.id)
                continue
            geoms = []
            for feature in data.features:
                geom = to_shape(feature.geom)
                if extent_prep.intersects(geom) and not geom.is_empty:
                    if model.cut_to_extent:
                        geom = geom.intersection(extent)
                    geoms.append(
                        GeometryFeature(ids=[feature.id], geometry=geom)
                    )
                    input_features[feature.id] = feature
            input_geometries.append(geoms)
        # Check the input data exists
        if len(input_geometries) == 0:
            raise ProcessingError("No input data exist")
        # Decompose the geometries
        geometries = input_geometries[0]
        rtree = rindex.Index()
        for i, g in enumerate(geometries):
            rtree.insert(i, g.geometry.bounds)
        for i, geoms in enumerate(input_geometries[1:]):
            send_feedback(
                "Decomposing geometries ({}/{})".format(
                    i + 1, len(input_geometries) - 1
                )
            )
            geometries, rtree = self.decompose(
                geometries, geoms, rtree, feedback=feedback
            )
        # Add global input features
        geometries = [
            GeometryFeature(
                list(geom.ids) + global_features_ids, geom.geometry
            )
            for geom in geometries
        ]

        return geometries, input_features

    def _process_overlap(self, model, feedback):
        # Prepare the extent
        extent = to_shape(model.data_generator.project.extent)
        extent_prep = prep(extent)
        # Check the input data is correct
        if len(model.input_data) != 1:
            raise ProcessingError("Incorrect number of input data")
        input_data = model.input_data[0]
        if input_data.data is None:
            raise ProcessingError("No geometries for the input data")
        # Convert the features to Shapely geometries
        # Filter geometries that intersects with the extend
        geoms = []
        features = {}
        for feature in input_data.data.features:
            geom = to_shape(feature.geom)
            if extent_prep.intersects(geom):
                if model.cut_to_extent:
                    geom = geom.intersection(extent)
                geoms.append(GeometryFeature(ids=[feature.id], geometry=geom))
                features[feature.id] = (geom, feature)

        # Duplicate all input attributes
        old_attrs = {}
        if model.data_generator.data is not None:
            old_attrs = {
                a.name: a for a in model.data_generator.data.attributes
            }
        attrs = {}
        for a in input_data.data.attributes:
            old_attr = old_attrs.get(a.name)
            attrs[a.id] = old_attr if a.same_as(old_attr) else a.new_copy()

        new_features = []
        geoms = self._decompose_features(geoms, feedback=feedback)
        attr_values = defaultdict(list)
        for geom in geoms:
            input_features = []
            new_feature = GeoFeature(geom=from_shape(geom.geometry, srid=4326))
            g1 = prep(geom.geometry)
            tmp_values = defaultdict(list)
            for id2 in geom.ids:
                # Each geometry was split multiple times
                # We cannot be sure that all input feature ids intersect with
                # resulting geometry
                geom2, feature2 = features[id2]
                if g1.intersects(geom2):
                    input_features.append(feature2)
                    for value in feature2.properties:
                        if value is not None:
                            attr = attrs[value.attribute_id]
                            tmp_values[attr].append(value)
            new_feature.input_features = input_features
            values = []
            for attr, vals in tmp_values.items():
                if len(vals) >= 1:
                    try:
                        val = attr.get_value_class()(
                            value=model.get_overlap_value(vals),
                            attribute=attr,
                            feature=new_feature,
                        )
                        attr_values[attr].append(val)
                    except TypeError:
                        raise ProcessingError(
                            "Error overlapping the values types."
                        )
            new_features.append(new_feature)
        for attr, values in attr_values.items():
            attr.values = values
        return new_features

    def process_model(self, model, feedback):
        """Process the model on the geometries.

        Args:
            model: A processing model.
            geometries (list): A list of GeometryFeature objects.

        Returns:
            A list of Feature objects.
        """
        features = []
        feedback.set_message("Processing model")
        if isinstance(model, GeoBuffer):
            features = self._process_model_buffer(model, feedback)
        elif isinstance(model, ContinuousRule):
            features = self._process_rule(model, feedback)
        elif isinstance(model, DiscreteRules):
            features = self._process_criteria_rules(model, feedback)
        elif isinstance(model, MRSort):
            features = self._process_mr_sort(model, feedback)
        elif isinstance(model, WeightedSum):
            features = self._process_weighted_sum(model, feedback)
        elif isinstance(model, MergeOverlapModel):
            features = self._process_overlap(model, feedback)
        elif isinstance(model, DissolveAdjacentModel):
            features = self._process_dissolve(model, feedback)
        elif isinstance(model, ZonePropositionGenerator):
            features = self._process_zone_proposition(model, feedback)
        else:
            raise ValueError
        return features

    def set_project_data_features(
        self, project_data, features, filter_none=True
    ):
        """Save the features.

        If a geo data already exists, the old features are replaced by the
        features given in arguements.
        If no geo data exists, a new one is created using the features.

        Args:
            project_data (ProjectData)
            features (list of GeoFeature)
            filter_none (bool): Remove the features with only None values
                (default: True)
        """
        if filter_none:
            # Remove features without values
            features_original = list(features)
            features = []
            for feat in features_original:
                if any((v.value is not None for v in feat.properties)):
                    features.append(feat)

        # Remove features with empty geometries
        features = list(
            filter(lambda f: to_shape(f.geom).is_empty is False, features)
        )

        # List the data attributes
        attrs = []
        for f in features:
            for p in f.properties:
                if p.attribute not in attrs:
                    attrs.append(p.attribute)

        if project_data.data is None:
            # Create a new data...
            project_data.data = GeneratedGeoData(
                name=project_data.name,
                features=features,
                attributes=attrs,
            )
        else:
            # ...or modify the old one
            data = project_data.data
            data.name = project_data.name
            data.features = features
            data.extent = None
            data.attributes = attrs
        project_data.data.update()
        post_load_normalization(project_data.data)
        project_data.update_full()

    def get_geometries_area(self, geometries):
        """Return the areas of the geometries.

        Calculates the area in PostGIS by casting the geometries to Geography
        data, allowing to have the area in square metres.

        Args:
            geometries (list): List of GeometryFeature objects.
        """
        q = db.select(db.func.st_area(db.cast(db.column("geom"), Geography)))
        q = q.select_from(
            db.func.unnest([g.geometry.wkt for g in geometries]).alias("geom")
        )
        q_result = db.session.execute(q).fetchall()
        areas = [r[0] for r in q_result]
        return areas

    def _process_dissolve(self, model, feedback):
        """Dissolve the adjacent geometries with the same attributes.

        Does not do anything if the dissolve_adjacent attribute of the model is
        not set. Otherwise, if two geometries touch each other and have the
        same values for their attributes, they will be merged in a single
        geometry.
        """
        # Prepare the extent
        extent = to_shape(model.data_generator.project.extent)
        extent_prep = prep(extent)
        # Check the input data is correct
        if len(model.input_data) != 1:
            raise ProcessingError("Incorrect number of input data")
        input_data = model.input_data[0]
        if input_data.data is None:
            raise ProcessingError("No geometries for the input data")

        # Duplicate all input attributes
        old_attrs = {}
        if model.data_generator.data is not None:
            old_attrs = {
                a.name: a for a in model.data_generator.data.attributes
            }
        attrs = {}
        for a in input_data.data.attributes:
            old_attr = old_attrs.get(a.name)
            attrs[a.id] = old_attr if a.same_as(old_attr) else a.new_copy()

        # Convert the features to Shapely geometries
        # Filter geometries that intersects with the extend
        # Group the geometries when the features have identical attributes
        # values
        # keys are a tuple of (attribute, value) and values are lists of
        # shapely geometries
        grouped = defaultdict(list)
        grouped_features = defaultdict(list)
        for feature in input_data.data.features:
            geom = to_shape(feature.geom)
            if extent_prep.intersects(geom):
                if model.cut_to_extent:
                    geom = geom.intersection(extent)
                f_key = tuple(
                    (prop.attribute_id, prop.value)
                    for prop in feature.properties
                )
                grouped[f_key].append(geom)
                grouped_features[f_key].append(feature)

        # Create the new features
        new_features = []
        attr_values = defaultdict(list)
        for key, geoms in grouped.items():
            # Union of each group of geometries
            union = unary_union(geoms)
            # If the union creates a multi-polygon, separate it in a list of
            # polygons
            assert union.geom_type in ("MultiPolygon", "Polygon")
            new_geoms = (
                list(union.geoms)
                if union.geom_type == "MultiPolygon"
                else [union]
            )
            for new_geom in new_geoms:
                new_prep_geom = prep(new_geom)
                input_features = []
                for feature, geom in zip(grouped_features[key], geoms):
                    if new_prep_geom.intersects(geom):
                        input_features.append(feature)
                new_feature = GeoFeature(
                    geom=from_shape(new_geom, srid=4326),
                    input_features=input_features,
                )
                for attr_id, value in key:
                    attr = attrs[attr_id]
                    cls = attr.get_value_class()
                    val = cls(
                        value=value,
                        attribute=attr,
                        feature=new_feature,
                    )
                    attr_values[attr].append(val)
                new_features.append(new_feature)
        for attr, values in attr_values.items():
            attr.values = values
        return new_features

    def _process_zone_proposition(self, model, feedback):
        """Make recommendations for zones.

        :param model:
        :param feedback:
        :raises ProcessingError: if there is not exactly 1 input_data
        :raises ProcessingError: if input_data has no geometry
        :raises ProcessingError: if no end-condition is set for model
        :return: generated zones as features
        """
        # Check the input data is correct
        if len(model.input_data) != 1:
            raise ProcessingError("Incorrect number of input data")
        input_data = model.input_data[0]
        if input_data.data is None:
            raise ProcessingError("No geometries for the input data")
        iterations, duration = model.iterations, model.duration
        if iterations is None and duration is None:
            raise ProcessingError("No end condition for zone proposition run")
        ga_ctx = ga_service.ga_context_from_decision_map(
            input_data,
            model.geo_size,
            proj=(
                "+proj=cea +lon_0=0 +lat_ts=45 +x_0=0 +y_0=0 +ellps=WGS84 "
                "+datum=WGS84 +units=m +no_defs"
            ),
        )
        ga = GeneticAlgorithm(ga_ctx, **model.ga_params())
        time_start = time.time()
        iteration_continue, duration_continue = True, True
        while iteration_continue and duration_continue:
            ga.iterate()
            current_duration = time.time() - time_start
            iteration_continue = (
                ga.iteration < iterations if iterations is not None else True
            )
            duration_continue = (
                current_duration < duration if duration is not None else True
            )
            if iterations is not None and duration is None:
                progress_count = ga.iteration
                progress_total = iterations
            elif iterations is None and duration is not None:
                progress_count = current_duration
                progress_total = duration
            elif ga.iteration / iterations >= current_duration / duration:
                progress_count = ga.iteration
                progress_total = iterations
            else:
                progress_count = current_duration
                progress_total = duration
            feedback.set_progress(progress_count, progress_total)
        features = []
        population = ga.filter_best()
        attribute = DataAttributeQuantitative(name="fitness")
        value_cls = attribute.get_value_class()
        for individual in population.individuals:
            value = value_cls(value=individual.fitness, attribute=attribute)
            feature = GeoFeature(
                from_shape(
                    individual.as_geometry(proj="epsg:4326"), srid=4326
                ),
                properties=[value],
                input_features=individual.inputs,
                execution_artifact=individual.execution_artifact,
            )
            features.append(feature)
        return features

    def dissolve_adjacent_features(self, data_id):
        """Dissolve the adjacent features with the same attributes values."""
        q = "SELECT dissolve_adjacent(:data_id)"
        keys = {"data_id": data_id}
        db.session.execute(q, keys)
