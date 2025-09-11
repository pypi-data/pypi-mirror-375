import enum
import io
import tokenize
from collections import defaultdict
from copy import deepcopy

import numpy as np
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import backref, validates

from ..exceptions import GeometryTypeError, ProcessingError
from . import db
from .geo_data import (
    AttributeType,
    DataAttribute,
    DataAttributeOrdinal,
    DataValueNominal,
    DataValueQuantitative,
    Feature,
)
from .mixins import BaseModelMixin, ModelMixin
from .processing_model_utils import evaluate_discrete_rule


class KeepOverlap(enum.Enum):
    min = 1
    max = 2
    sum = 3
    average = 4


class ModelType(enum.Enum):
    categories_rule = 1
    continuous_rule = 2
    geo_buffer = 3
    mrsort = 4
    weighted_sum = 5
    merge_overlap = 6
    dissolve_adjacent = 7
    zone_proposition = 8


class ProcessingModel(ModelMixin, db.Model):
    __tablename__ = "processing_model"

    model_type = db.Column(db.Enum(ModelType))
    name = db.Column(db.String)
    data_generator_id = db.Column(
        db.Integer, db.ForeignKey("project_data.id"), nullable=False
    )
    cut_to_extent = db.Column(db.Boolean)

    data_generator = db.relationship(
        "DataGenerator",
        back_populates="_processing_models",
        foreign_keys=[data_generator_id],
    )

    __mapper_args__ = {"polymorphic_on": model_type}

    def __init__(
        self,
        cut_to_extent=True,
        name="",
        **kwargs,
    ):
        self.cut_to_extent = cut_to_extent
        self.name = name

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.name = self.name
        other.cut_to_extent = self.cut_to_extent
        other.data_generator = deepcopy(self.data_generator, memo)
        return other

    @property
    def input_data(self):
        return self.data_generator.input_data

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        Here it retuns all input attributes.

        :return:
        """
        return {
            attr
            for data in self.input_data
            if data.data is not None
            for attr in data.data.attributes
        }

    def get_used_input_attributes(self) -> list[DataAttribute]:
        """Get list of used input attributes in a model definition.

        :return:
        """
        return sorted(
            self._get_used_input_attributes(), key=lambda a: (a.data.id, a.id)
        )

    def explain(self, feature: Feature) -> dict:
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = {
            "model_type": self.model_type.name,
            "disaggregation": [],
        }
        for input_feature in feature.input_features:
            for prop in input_feature.properties:
                if prop.attribute not in self._get_used_input_attributes():
                    continue
                if prop.value is not None:
                    explanation["disaggregation"].append(
                        {
                            "data": prop.attribute.data.name,
                            "attribute": prop.attribute.name,
                            "value": prop.value,
                        }
                    )
        return explanation


class MergeOverlapModel(ProcessingModel):
    keep_overlap = db.Column(
        db.Enum(KeepOverlap), default=KeepOverlap.max, nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": ModelType.merge_overlap}

    def __init__(self, keep_overlap=KeepOverlap.max, **kwargs):
        super().__init__(**kwargs)
        self.keep_overlap = keep_overlap

    def get_overlap_value(self, values):
        """Return the overlap value filtered through the overlap function.

        Args:
            values: A list of the values.
        """
        if isinstance(values[0], DataValueNominal):
            raise TypeError("Cannot aggregate overlapping nominal values")
        if self.keep_overlap == KeepOverlap.max:
            return max(values).value
        if self.keep_overlap == KeepOverlap.min:
            return min(values).value
        if not isinstance(values[0], DataValueQuantitative):
            raise TypeError(
                "Ordinal values can only be aggregated with "
                f"keep_overlap in ['min', 'max'], found {self.keep_overlap}"
            )
        if self.keep_overlap == KeepOverlap.sum:
            return sum(values).value
        if self.keep_overlap == KeepOverlap.average:
            return sum(values) / len(values).value

    def process_overlap(self, entity):
        """Decompose the overlapping attributes, and keep the chosen value
        (all, worse or best)"""
        try:
            result = entity.decompose_intersection()
        except GeometryTypeError:
            raise ProcessingError(
                "The overlapping geometries are not polygons."
            )
        for feature in result.features:
            for prop, values in feature.data.attributes.items():
                values = [v for v in values if v is not None]
                if values is None or len(values) < 1:
                    val = values
                elif len(values) == 1:
                    val = values[0]
                else:
                    try:
                        val = self.get_overlap_value(values)
                    except TypeError:
                        raise ProcessingError(
                            "Error overlapping the value types."
                        )
                feature.data.attributes[prop] = val
        return result

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = {
            "model_type": self.model_type.name,
            "keep_overlap": self.keep_overlap.name,
            "aggregated": [],
        }
        tmp_values = defaultdict(list)
        for input_feature in feature.input_features:
            for prop in input_feature.properties:
                if prop.attribute not in self._get_used_input_attributes():
                    continue
                if prop.value is not None:
                    tmp_values[prop.attribute].append(prop.value)
        for attr, vals in tmp_values.items():
            if len(vals) > 0:
                explanation["aggregated"].append(
                    {
                        "data": attr.data.name,
                        "attribute": attr.name,
                        "values": vals,
                    }
                )
        return explanation

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.keep_overlap = self.keep_overlap
        return other


class DissolveAdjacentModel(ProcessingModel):
    __mapper_args__ = {"polymorphic_identity": ModelType.dissolve_adjacent}

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        return {"model_type": self.model_type.name}


def _extract_attributes_from_code(
    code: str, model: ProcessingModel
) -> set[DataAttribute]:
    """Extract attributes from code.

    :param code:
    :param model: processing model
    :return: set of attributes used in code
    """
    imput_attributes = {}
    for data in model.input_data:
        if data.data is None:
            continue
        for attribute in data.data.attributes:
            imput_attributes[(data.name, attribute.name)] = attribute
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    res = set()
    i = 0
    while i < len(tokens) - 2:
        token = tokens[i]
        if (
            token.type == tokenize.NAME
            and tokens[i + 1].type == tokenize.OP
            and tokens[i + 1].string == "."
            and tokens[i + 2].type == tokenize.NAME
            and (token.string, tokens[i + 2].string) in imput_attributes
        ):
            res.add(imput_attributes[(token.string, tokens[i + 2].string)])
            i += 3
        else:
            i += 1

    return res


def _replace_variables_code(
    code: str,
    variables_mapping: dict[tuple[str, str], tuple[str, str]],
) -> str:
    """Replace attribute variables in code by new ones.

    :param code:
    :param variables_mapping: mapping of old variables to new ones
    :return: new code
    """
    tokens = list(tokenize.generate_tokens(io.StringIO(code).readline))
    res = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if (
            token.type == tokenize.NAME
            and i < len(tokens) - 2
            and tokens[i + 1].type == tokenize.OP
            and tokens[i + 1].string == "."
            and tokens[i + 2].type == tokenize.NAME
        ):
            new_data, new_attr = variables_mapping.get(
                (token.string, tokens[i + 2].string),
                (token.string, tokens[i + 2].string),
            )
            res.append(
                tokenize.TokenInfo(
                    type=tokenize.NAME,
                    string=new_data,
                    start=token.start,
                    end=token.end,
                    line=token.line,
                )
            )
            res.append(tokens[i + 1])
            res.append(
                tokenize.TokenInfo(
                    type=tokenize.NAME,
                    string=new_attr,
                    start=tokens[i + 2].start,
                    end=tokens[i + 2].end,
                    line=tokens[i + 2].line,
                )
            )
            i += 3
        else:
            res.append(token)
            i += 1

    return tokenize.untokenize(res)


class DefaultValue(BaseModelMixin, db.Model):
    attribute_id = db.Column(
        db.Integer,
        db.ForeignKey("data_attribute.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    model_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_model.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    value = db.Column(JSONB)

    attribute = db.relationship("DataAttribute")
    model = db.relationship(
        "PrefDefaultValues", back_populates="default_values"
    )

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.attribute = deepcopy(self.attribute, memo)
        other.model = deepcopy(self.model, memo)
        other.value = self.value
        return other


class PrefDefaultValues(ProcessingModel):
    default_values = db.relationship(
        "DefaultValue", back_populates="model", cascade="all,delete-orphan"
    )

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.default_values = [deepcopy(d, memo) for d in self.default_values]
        return other

    # @validates('default_values')
    # def validate_default_values(self, key, default_value):
    # TODO: Check that the attribute is in the input data of the model
    # pass

    def get_default_value(self, attribute):
        """Returns the default value for the attribute.

        Returns:
            The default value if it exists, or None otherwise
        """
        try:
            return next(
                d.value
                for d in self.default_values
                if d.attribute_id == attribute.id
            )
        except StopIteration:
            return None

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = {
            "model_type": self.model_type.name,
            "disaggregation": [],
        }
        input_map = {
            f.data: {prop.attribute: prop.value for prop in f.properties}
            for f in feature.input_features
        }
        for attr in self.get_used_input_attributes():
            value = self.get_default_value(attr)
            if (
                attr.data in input_map
                and attr in input_map[attr.data]
                and input_map[attr.data][attr] is not None
            ):
                value = input_map[attr.data][attr]
            if value is not None:
                explanation["disaggregation"].append(
                    {
                        "data": attr.data.name,
                        "attribute": attr.name,
                        "value": value,
                    }
                )
        return explanation


class GeoBuffer(ProcessingModel):
    """Model to create a buffer around the geometry."""

    radius = db.Column(db.BigInteger)

    __mapper_args__ = {"polymorphic_identity": ModelType.geo_buffer}

    def __init__(self, radius=None, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.radius = self.radius
        return other

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = super().explain(feature)
        explanation["radius"] = self.radius
        return explanation


class DiscreteCategory(ModelMixin, db.Model):
    """Model for creating data using discrete values (categories)."""

    __tablename__ = "discrete_category"

    type = db.Column(db.String)
    name = db.Column(db.String)
    position = db.Column(db.Integer)
    preference_model_id = db.Column(
        db.Integer, db.ForeignKey("processing_model.id", ondelete="CASCADE")
    )

    preference_model = db.relationship("DiscreteModel")

    __mapper_args__ = {
        "polymorphic_on": type,
        "polymorphic_identity": "discrete_category",
    }

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name

    def __deepcopy__(self, memo):
        other = type(self)(name=self.name, position=self.position)
        memo[id(self)] = other
        other.preference_model = deepcopy(self.preference_model, memo)
        return other


class DiscreteRulesCategory(DiscreteCategory):
    rules = db.Column(ARRAY(db.String, dimensions=1))

    __mapper_args__ = {"polymorphic_identity": "discrete_rules_category"}

    def __init__(self, rules=[], **kwargs):
        super().__init__(**kwargs)
        self.rules = rules

    def __deepcopy__(self, memo):
        other = type(self)(name=self.name)
        memo[id(self)] = other
        other.preference_model = deepcopy(self.preference_model, memo)
        other.rules = deepcopy(self.rules, memo)
        return other

    def evaluate_data(self, data, stats=None):
        evaluation = np.full_like(
            data,
            fill_value=False,
            dtype=bool,
            shape=(len(self.rules), len(data)),
        )
        for i, rule in enumerate(self.rules):
            evaluation[i, :] = evaluate_discrete_rule(data, rule, stats)
        return evaluation


class DiscreteModel(ProcessingModel):
    categories = db.relationship(
        "DiscreteCategory",
        order_by="DiscreteCategory.position",
        cascade="all,delete-orphan",
        collection_class=ordering_list("position"),
        back_populates="preference_model",
    )


class DiscreteRules(DiscreteModel):
    """Used to create a geo-data containing discrete values (ie. categories)
    from rules."""

    categories = db.relationship(
        "DiscreteRulesCategory",
        order_by="DiscreteRulesCategory.position",
        cascade="all,delete-orphan",
        collection_class=ordering_list("position"),
        back_populates="preference_model",
    )

    __mapper_args__ = {"polymorphic_identity": ModelType.categories_rule}

    def __init__(self, categories=[], **kwargs):
        super().__init__(**kwargs)
        self.categories = categories

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.categories = [deepcopy(c, memo) for c in self.categories]
        return other

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        :return:
        """
        attributes = set()
        for category in self.categories:
            for rule in category.rules:
                attributes |= _extract_attributes_from_code(rule, self)
        return attributes

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = super().explain(feature)
        explanation["rule"] = feature.execution_artifact["rule"]
        return explanation


class MRSort(DiscreteModel):
    """Used to create a geo-data using the MR-Sort algorithm.

    Attributes:
        categories (list): The categories for the sorting algorithm.
            Best category first.
        majority_threshold (float): The cut threshold for the concordance
            condition. At least half the sum of the criteria weights.
    """

    majority_threshold = db.Column(db.Float)

    criteria = db.relationship(
        "MRSortCriterion", back_populates="mrsort", cascade="all,delete-orphan"
    )

    __mapper_args__ = {"polymorphic_identity": ModelType.mrsort}

    def __init__(self, criteria=[], categories=[], **kwargs):
        super().__init__(**kwargs)
        self.criteria = criteria
        self.categories = categories

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.majority_threshold = self.majority_threshold
        other.criteria = [deepcopy(c, memo) for c in self.criteria]
        other.categories = [deepcopy(c, memo) for c in self.categories]
        return other

    @validates("criteria")
    def validate_criteria(self, key, criterion):
        """Verify that the criterion references an input_data."""
        attributes = []
        for data in self.input_data:
            if data.data is not None:
                attributes += data.data.attributes
        assert (
            criterion.attribute in attributes
        ), "The criterion references an invalid data."
        return criterion

    def init_criteria(self):
        criteria = []
        for data in self.input_data:
            if data.data is not None:
                for attr in data.data.attributes:
                    if attr.type is AttributeType.quantitative:
                        for crit in self.criteria:
                            if crit.attribute is attr:
                                criterion = crit
                                break
                        else:
                            criterion = MRSortCriterion(
                                attribute=attr, mrsort_id=self.id
                            )
                        criteria.append(criterion)
        self.criteria = criteria

    def compute_weights(self, attributes, profile_index, criteria_lookup=None):
        """Compute weights where feature is better than profile.

        :param attributes: list of (data name, attribute name, value)
        :param profile_index: index of profile to compare to
        :param criteria_lookup:
            dict mapping (data name, attribute name) to criteria,
            computed if absent
        :return:
            weights for attributes where feature is better than profile
            indexed by (data name, attribute name)
        """
        criteria_lookup = criteria_lookup or {
            (c.attribute.data.name, c.attribute.name): c for c in self.criteria
        }
        weights = {}
        for name, attribute, value in attributes:
            criterion = criteria_lookup.get((name, attribute), None)
            if criterion is not None and criterion.is_better(
                value, profile_index
            ):
                weights[(name, attribute)] = criterion.weight
        return weights

    def check_category(self, attributes):
        """Execute the MR-Sort algorithm on the attributes.

        Args:
            attributes (list): List of ('name', 'attribute', value).

        Raises:
            AttributeError: If the attribute ('name', 'attribute') does not
                correspond to any criterion.
        """
        categories = self.categories[::-1]  # reverse the order (worst first)
        result = categories[0]
        criteria_lookup = {
            (c.attribute.data.name, c.attribute.name): c for c in self.criteria
        }
        for index, category in enumerate(categories[1:]):
            weights = self.compute_weights(attributes, index, criteria_lookup)
            total = sum(weights.values())
            if total >= self.majority_threshold:
                result = category
            else:
                break
        return result

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        :return:
        """
        return {
            criterion.attribute
            for criterion in self.criteria
            if criterion.attribute is not None
        }

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = super().explain(feature)
        explanation["majority_threshold"] = self.majority_threshold
        category_name = feature.get_property("category")
        attributes = []
        for value in explanation["disaggregation"]:
            attributes.append(
                (value["data"], value["attribute"], value["value"])
            )
        lower = None
        upper = None
        explanation["categories"] = []
        for index, cat in enumerate(
            sorted(self.categories, key=lambda c: c.position)
        ):
            explanation["categories"].append(cat.name)
            if cat.name != category_name:
                continue
            if index > 0:
                upper = len(self.categories) - index - 1
            if index < len(self.categories) - 1:
                lower = len(self.categories) - index - 2
        if lower is not None:
            explanation["lower"] = []
            lower_weights = self.compute_weights(attributes, lower)
        if upper is not None:
            explanation["upper"] = []
            upper_weights = self.compute_weights(attributes, upper)

        explanation["criteria"] = []
        for crit in self.criteria:
            explanation["criteria"].append(
                {
                    "data": crit.attribute.data.name,
                    "attribute": crit.attribute.name,
                    "maximize": crit.maximize,
                }
            )
            if lower is not None:
                explanation["lower"].append(
                    {
                        "data": crit.attribute.data.name,
                        "attribute": crit.attribute.name,
                        "value": crit.profiles[lower],
                        "weight": lower_weights.get(
                            (crit.attribute.data.name, crit.attribute.name), 0
                        ),
                    }
                )
            if upper is not None:
                explanation["upper"].append(
                    {
                        "data": crit.attribute.data.name,
                        "attribute": crit.attribute.name,
                        "value": crit.profiles[upper],
                        "weight": upper_weights.get(
                            (crit.attribute.data.name, crit.attribute.name), 0
                        ),
                    }
                )

        return explanation


class MRSortCriterion(BaseModelMixin, db.Model):
    """Contain the criterion data for the MR-Sort algorithm.

    Attributes:
        profiles: The values for the profiles of the categories.
            Worst value first.
        weight (float):
            The weight of the criterion in the algorithm.
        maximize (bool):
            Preference direction (maximize if True, minimize if False).
            Default: True.
    """

    __tablename__ = "mrsort_criterion"

    profiles = db.Column(ARRAY(db.Float, dimensions=1))
    weight = db.Column(db.Float)
    maximize = db.Column(db.Boolean, nullable=False, default=False)
    mrsort_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_model.id", ondelete="CASCADE"),
        primary_key=True,
    )
    attribute_id = db.Column(
        db.Integer,
        db.ForeignKey("data_attribute.id", ondelete="CASCADE"),
        primary_key=True,
    )

    attribute = db.relationship(
        "DataAttribute",
        backref=backref("mrsort_criteria", cascade="delete,delete-orphan"),
    )
    mrsort = db.relationship("MRSort", back_populates="criteria")

    def __init__(
        self, mrsort=None, profiles=[], weight=0, maximize=True, **kwargs
    ):
        super().__init__(**kwargs)
        self.profiles = profiles
        self.weight = weight
        self.maximize = maximize

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.profiles = deepcopy(self.profiles, memo)
        other.weight = self.weight
        other.maximize = self.maximize
        other.attribute = deepcopy(self.attribute, memo)
        other.mrsort = deepcopy(self.mrsort, memo)
        return other

    def is_better(self, value, profile_index):
        """Check if the value is better than the profile for the given index.

        Args:
            value (number): The value to check.
            profile_index (int): Index of the profile in the profiles list.
        """
        if value is None:
            return False
        if self.maximize:
            return value >= self.profiles[profile_index]
        else:
            return value <= self.profiles[profile_index]


class ContinuousRule(PrefDefaultValues):
    """Used to create a geo-data containing continuous values from a rule"""

    rule = db.Column(db.String)

    __mapper_args__ = {"polymorphic_identity": ModelType.continuous_rule}

    def __init__(self, rule="", default_values=[], **kwargs):
        super().__init__(**kwargs)
        self.rule = rule
        self.default_values = default_values
        self.model_type = ModelType.continuous_rule

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.rule = self.rule
        return other

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        :return:
        """
        return _extract_attributes_from_code(self.rule, self)


class WeightedSum(PrefDefaultValues):
    operands = db.relationship(
        "WeightedSumOperand",
        back_populates="model",
        cascade="all,delete-orphan",
    )

    __mapper_args__ = {"polymorphic_identity": ModelType.weighted_sum}

    def __init__(self, operands=None, **kwargs):
        super().__init__(**kwargs)
        if operands is None:
            self.operands = [WeightedSumOperand(weight=1)]
        else:
            self.operands = operands

    def __deepcopy__(self, memo):
        other = super().__deepcopy__(memo)
        other.operands = [deepcopy(o, memo) for o in self.operands]
        return other

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        :return:
        """
        return {
            op.attribute for op in self.operands if op.attribute is not None
        }

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = super().explain(feature)
        properties = {
            (p["data"], p["attribute"]): p["value"]
            for p in explanation.pop("disaggregation")
        }
        default_values = {
            (d.attribute.data.name, d.attribute.name): d.value
            for d in self.default_values
        }
        explanation["disaggregation"] = []
        for operand in self.operands:
            index = (operand.attribute.data.name, operand.attribute.name)
            val = properties.get(index)
            if val is None:
                val = default_values.get(index)
            if val is not None:
                explanation["disaggregation"].append(
                    {
                        "data": operand.attribute.data.name,
                        "attribute": operand.attribute.name,
                        "value": val,
                        "weight": operand.weight,
                    }
                )
        return explanation


class WeightedSumOperand(ModelMixin, db.Model):
    __tablename__ = "weighted_sum_operand"

    attribute_id = db.Column(
        db.Integer, db.ForeignKey("data_attribute.id", ondelete="SET NULL")
    )
    weight = db.Column(db.Float)
    model_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_model.id", ondelete="CASCADE"),
        nullable=False,
    )

    attribute = db.relationship("DataAttribute")
    model = db.relationship("WeightedSum", back_populates="operands")

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.attribute = deepcopy(self.attribute, memo)
        other.model = deepcopy(self.model, memo)
        other.weight = self.weight
        return other


class ZonePropositionGenerator(ProcessingModel):
    geo_size = db.Column(db.Float)
    iterations = db.Column(db.Integer)
    duration = db.Column(db.Float)

    size = db.Column(db.Integer)
    mutation = db.Column(db.Float)
    children = db.Column(db.Integer)
    filter_clusters = db.Column(db.Boolean)

    __mapper_args__ = {"polymorphic_identity": ModelType.zone_proposition}

    def __init__(
        self,
        geo_size=0,
        size=80,
        mutation=0.02,
        children=60,
        filter_clusters=True,
        iterations=None,
        duration=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.geo_size = geo_size
        self.size = size
        self.mutation = mutation
        self.children = children
        self.filter_clusters = filter_clusters
        self.iterations = iterations
        self.duration = duration

    def __deepcopy__(self, memo):
        other = type(self)()
        memo[id(self)] = other
        other.name = self.name
        other.cut_to_extent = self.cut_to_extent
        other.geo_size = self.geo_size
        other.iterations = self.iterations
        other.duration = self.duration
        other.size = self.size
        other.mutation = self.mutation
        other.children = self.children
        other.filter_clusters = self.filter_clusters
        other.data_generator = deepcopy(self.data_generator, memo)
        return other

    def ga_params(self):
        return {
            "size": self.size,
            "mutation": self.mutation,
            "children": self.children,
            "filter_clusters": self.filter_clusters,
        }

    def _get_used_input_attributes(self) -> set[DataAttribute]:
        """Get set of used input attributes in a model definition.

        Here it retuns all input attributes.

        :return:
        """
        if len(self.input_data) == 0:
            return set()
        input_data = self.input_data[0]
        if input_data.data is None:
            return set()
        if len(input_data.data.attributes) == 0:
            return set()
        return {input_data.data.attributes[0]}

    def explain(self, feature):
        """Explain feature wrt the model.

        :param feature: feature computed by the model
        :return: explanation as a dict
        """
        explanation = {
            "model_type": self.model_type.name,
            "disaggregation": [],
        }
        _attributes = self.get_used_input_attributes()
        attribute = None if len(_attributes) == 0 else _attributes[0]
        is_ordinal_attribute = isinstance(attribute, DataAttributeOrdinal)
        feature_artifacts = {
            artifact["feature"]: artifact
            for artifact in feature.execution_artifact["features"]
        }
        for input_feature in feature.input_features:
            area = feature_artifacts[input_feature.id]["area"]
            for prop in input_feature.properties:
                if prop.attribute != attribute:
                    continue
                if prop.value is not None:
                    value = float(
                        len(attribute.order)
                        - attribute.order.index(prop.value)
                        if is_ordinal_attribute
                        else prop.value
                    )
                    explanation["disaggregation"].append(
                        {
                            "data": attribute.data.name,
                            "attribute": attribute.name,
                            "value": prop.value,
                            "numeric_value": value,
                            "area": area,
                            "fitness": feature_artifacts[input_feature.id][
                                "fitness"
                            ],
                        }
                    )
        return explanation
