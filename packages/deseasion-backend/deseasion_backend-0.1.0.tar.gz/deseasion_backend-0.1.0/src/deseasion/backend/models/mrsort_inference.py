from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection

from . import db
from .mixins import BaseModelMixin, ModelMixin


class MRSortInferenceAlternative(ModelMixin, db.Model):
    """Alternatives for the inference of the MR-Sort model.

    Attributes:
        category: The assigned category.
        visible: Visible in the list of inference alternatives.
        mrsort: MR-Sort model.
    """

    __tablename__ = "mrsort_inference_alternative"

    category_id = db.Column(
        db.Integer, db.ForeignKey("discrete_category.id", ondelete="SET NULL")
    )
    mrsort_id = db.Column(
        db.Integer,
        db.ForeignKey("processing_model.id", ondelete="CASCADE"),
        nullable=False,
    )

    mrsort = db.relationship(
        "MRSort",
        backref=backref("inference_alternatives", cascade="all,delete-orphan"),
    )
    category = db.relationship("DiscreteCategory")
    inference_values = db.relationship(
        "MRSortInferenceValue",
        collection_class=attribute_mapped_collection("criterion"),
        cascade="all,delete-orphan",
        back_populates="alternative",
    )
    values = association_proxy(
        "inference_values",
        "value",
        creator=lambda k, v: MRSortInferenceValue(criterion=k, value=v),
    )


class MRSortInferenceValue(BaseModelMixin, db.Model):
    __tablename__ = "mrsort_inference_value"

    mrsort_id = db.Column(db.Integer, primary_key=True)
    attribute_id = db.Column(db.Integer, primary_key=True)
    alternative_id = db.Column(
        db.Integer,
        db.ForeignKey("mrsort_inference_alternative.id", ondelete="CASCADE"),
        primary_key=True,
    )
    value = db.Column(JSONB)

    __table_args__ = (
        db.ForeignKeyConstraint(
            ["mrsort_id", "attribute_id"],
            ["mrsort_criterion.mrsort_id", "mrsort_criterion.attribute_id"],
            ondelete="CASCADE",
        ),
    )

    criterion = db.relationship(
        "MRSortCriterion",
        backref=backref("inference_values", cascade="delete,delete-orphan"),
    )
    alternative = db.relationship(
        "MRSortInferenceAlternative", back_populates="inference_values"
    )
