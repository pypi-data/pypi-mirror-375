"""Make MR-Sort explainability self-sufficient.

Revision ID: 5f84e56d0465f
Revises: a212e7950484
Create Date: 2025-04-01 14:45:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "5f84e56d0465f"
down_revision = "a212e7950484"
branch_labels = None
depends_on = None


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
    conn = op.get_bind()
    # Get all geo features with non-polygon geometry
    nb = conn.execute(
        sa.text("SELECT count(id) FROM feature WHERE explainability != '[]'")
    ).fetchone()[0]
    res = conn.execute(
        sa.select(feature.c["id", "explainability"]).where(
            feature.c.explainability != []
        )
    )
    i = 0
    progress_bar(i, nb)
    for id, explain in res:
        if explain["model_type"] in ("mrsort", "geo_buffer"):
            conn.execute(
                feature.update()
                .values(explainability=[])
                .where(feature.c.id == id)
            )
        i += 1
        progress_bar(i, nb)


def downgrade():
    pass
