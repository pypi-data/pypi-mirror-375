"""Add extent_filter to data

Revision ID: 337e01e5199e
Revises: bb99ff70c7bf
Create Date: 2025-06-26 12:17:46.133271

"""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = "337e01e5199e"
down_revision = "bb99ff70c7bf"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("base_data", schema=None) as batch_op:
        batch_op.add_geospatial_column(
            sa.Column(
                "extent_filter",
                Geometry(
                    spatial_index=False,
                    from_text="ST_GeomFromEWKT",
                    name="geometry",
                ),
                nullable=True,
            )
        )
        batch_op.create_geospatial_index(
            "idx_base_data_extent_filter",
            ["extent_filter"],
            unique=False,
            postgresql_using="gist",
            postgresql_ops={},
        )


def downgrade():
    with op.batch_alter_table("base_data", schema=None) as batch_op:
        batch_op.drop_geospatial_index(
            "idx_base_data_extent_filter",
            postgresql_using="gist",
            column_name="extent_filter",
        )
        batch_op.drop_geospatial_column("extent_filter")
