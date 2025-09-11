"""replace project data shares with data shares

Revision ID: 163a9f52cac3
Revises: c6e3da96b784
Create Date: 2025-06-13 14:23:25.338030

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "163a9f52cac3"
down_revision = "c6e3da96b784"
branch_labels = None
depends_on = None


def upgrade():
    # Remove foreign key constraint on data_share.data_id
    with op.batch_alter_table("data_share", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_data_share_data_id_project_data", type_="foreignkey"
        )

    op.execute(
        sa.text(
            """
UPDATE data_share
SET data_id = project_data.data_id
FROM project_data
WHERE data_share.data_id = project_data.id;
"""
        )
    )
    op.execute(sa.text("DELETE FROM data_share WHERE data_id IS NULL"))

    # Add updated foreign key constraint on data_share.data_id
    with op.batch_alter_table("data_share", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_data_share_data_id_base_data"),
            "base_data",
            ["data_id"],
            ["id"],
        )


def downgrade():
    # Remove foreign key constraint on data_share.data_id
    with op.batch_alter_table("data_share", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_data_share_data_id_base_data"), type_="foreignkey"
        )

    op.execute(
        sa.text(
            """
DELETE FROM data_share WHERE id IN
(
    SELECT s.id FROM data_share s
    JOIN base_data d ON s.data_id = d.id
    WHERE d.type != 'generated_geo_data'
)
"""
        )
    )
    op.execute(
        sa.text(
            """
UPDATE data_share
SET data_id = project_data.id
FROM project_data
WHERE data_share.data_id = project_data.data_id;
"""
        )
    )
    op.execute(sa.text("DELETE FROM data_share WHERE data_id IS NULL"))

    # Add updated foreign key constraint on data_share.data_id
    with op.batch_alter_table("data_share", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_data_share_data_id_project_data"),
            "project_data",
            ["data_id"],
            ["id"],
        )
