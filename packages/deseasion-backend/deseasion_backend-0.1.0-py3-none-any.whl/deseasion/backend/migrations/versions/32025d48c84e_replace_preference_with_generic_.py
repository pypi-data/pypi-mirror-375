"""Replace preference with generic processing

Revision ID: 32025d48c84e
Revises: d1a3e922d5d0
Create Date: 2025-02-14 16:18:30.860615

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql  # noqa: F401

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "32025d48c84e"
down_revision = "d1a3e922d5d0"
branch_labels = None
depends_on = None


preftype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    name="preftype",
)


modeltype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    name="modeltype",
)


feature = sa.Table(
    "feature",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum("feature", "geo_feature", name="featuretype"),
        nullable=True,
    ),
    sa.Column("data_id", sa.Integer(), nullable=True),
    sa.Column(
        "explainability",
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
)


def upgrade():
    op.rename_table("preference_model", "processing_model")
    op.alter_column(
        "processing_model", "pref_type", new_column_name="model_type"
    )
    modeltype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE processing_model ALTER COLUMN model_type TYPE modeltype"
        " USING model_type::text::modeltype"
    )
    preftype.drop(op.get_bind(), checkfirst=False)

    with op.batch_alter_table("default_value", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_default_value_model_id_preference_model", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_default_value_model_id_processing_model"),
            "processing_model",
            ["model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("discrete_category", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_discrete_category_preference_model_id_preference_model",
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            batch_op.f(
                "fk_discrete_category_preference_model_id_processing_model"
            ),
            "processing_model",
            ["preference_model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("mrsort_criterion", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_mrsort_criterion_mrsort_id_preference_model",
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_mrsort_criterion_mrsort_id_processing_model"),
            "processing_model",
            ["mrsort_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table(
        "mrsort_inference_alternative", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            "fk_mrsort_inference_alternative_mrsort_id_preference_model",
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            batch_op.f(
                "fk_mrsort_inference_alternative_mrsort_id_processing_model"
            ),
            "processing_model",
            ["mrsort_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_project_data_active_model_id_preference_model",
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_project_data_active_model_id_processing_model"),
            "processing_model",
            ["active_model_id"],
            ["id"],
        )

    with op.batch_alter_table("weighted_sum_operand", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_weighted_sum_operand_model_id_preference_model",
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_weighted_sum_operand_model_id_processing_model"),
            "processing_model",
            ["model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    conn = op.get_bind()
    # Get all features with an explanation
    nb = conn.execute(
        sa.text("SELECT count(id) FROM feature WHERE explainability != '[]'")
    ).fetchone()[0]
    res = conn.execute(
        sa.select(feature.c["id", "explainability"]).where(
            feature.c.explainability != "[]"
        )
    )
    i = 0
    progress_bar(i, nb)
    for id, explain in res:
        explain["model_type"] = explain.pop("pref_type")
        conn.execute(
            feature.update()
            .values(explainability=explain)
            .where(feature.c.id == id)
        )
        i += 1
        progress_bar(i, nb)


def downgrade():
    op.rename_table("processing_model", "preference_model")
    op.alter_column(
        "preference_model", "model_type", new_column_name="pref_type"
    )
    preftype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN pref_type TYPE preftype"
        " USING pref_type::text::preftype"
    )
    modeltype.drop(op.get_bind(), checkfirst=False)

    with op.batch_alter_table("weighted_sum_operand", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_weighted_sum_operand_model_id_processing_model"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_weighted_sum_operand_model_id_preference_model",
            "preference_model",
            ["model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_project_data_active_model_id_processing_model"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_project_data_active_model_id_preference_model",
            "preference_model",
            ["active_model_id"],
            ["id"],
        )

    with op.batch_alter_table(
        "mrsort_inference_alternative", schema=None
    ) as batch_op:
        batch_op.drop_constraint(
            batch_op.f(
                "fk_mrsort_inference_alternative_mrsort_id_processing_model"
            ),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_mrsort_inference_alternative_mrsort_id_preference_model",
            "preference_model",
            ["mrsort_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("mrsort_criterion", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_mrsort_criterion_mrsort_id_processing_model"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_mrsort_criterion_mrsort_id_preference_model",
            "preference_model",
            ["mrsort_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("discrete_category", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f(
                "fk_discrete_category_preference_model_id_processing_model"
            ),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_discrete_category_preference_model_id_preference_model",
            "preference_model",
            ["preference_model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    with op.batch_alter_table("default_value", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_default_value_model_id_processing_model"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_default_value_model_id_preference_model",
            "preference_model",
            ["model_id"],
            ["id"],
            ondelete="CASCADE",
        )

    conn = op.get_bind()
    # Get all features with an explanation
    nb = conn.execute(
        sa.text("SELECT count(id) FROM feature WHERE explainability != '[]'")
    ).fetchone()[0]
    res = conn.execute(
        sa.select(feature.c["id", "explainability"]).where(
            feature.c.explainability != "[]"
        )
    )
    i = 0
    progress_bar(i, nb)
    for id, explain in res:
        explain["pref_type"] = explain.pop("model_type")
        conn.execute(
            feature.update()
            .values(explainability=explain)
            .where(feature.c.id == id)
        )
        i += 1
        progress_bar(i, nb)
