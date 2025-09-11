"""Add creation/modification timestamps to ProjectData

Revision ID: 141e705ab129
Revises: 5f84e56d0465f
Create Date: 2025-04-01 14:24:30.773709

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "141e705ab129"
down_revision = "5f84e56d0465f"
branch_labels = None
depends_on = None


project_data = sa.Table(
    "project_data",
    sa.MetaData(),
    sa.Column(
        "data_type",
        sa.Enum("geo_data", "generator", "global_data", name="datatype"),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("data_id", sa.Integer(), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("last_update", sa.DateTime(), nullable=True),
    sa.Column("project_id", sa.Integer(), nullable=False),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column("name", sa.String(), nullable=True),
    sa.Column("active_model_id", sa.Integer(), nullable=True),
)


def upgrade():
    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("created_at", sa.DateTime(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("modified_at", sa.DateTime(), nullable=True)
        )

    # Create dummy creation date to last update
    op.execute(sa.text("UPDATE project_data SET created_at = last_update"))

    # Create dummy modified date to last update
    op.execute(sa.text("UPDATE project_data SET modified_at = last_update"))

    # Change modified date of generators so they are outdated
    now = datetime.now(timezone.utc)
    op.execute(
        project_data.update()
        .values(modified_at=now)
        .where(project_data.c.data_type == "generator")
    )


def downgrade():
    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_column("modified_at")
        batch_op.drop_column("created_at")
