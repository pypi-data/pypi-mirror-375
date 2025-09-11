"""Remove project root data

Revision ID: 2657de160d2c
Revises: 89755dd43f58
Create Date: 2025-04-11 14:17:23.027086

"""

import sqlalchemy as sa
from alembic import op

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "2657de160d2c"
down_revision = "89755dd43f58"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("project_root")


def downgrade():
    op.create_table(
        "project_root",
        sa.Column(
            "project_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "project_root_data_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name="fk_project_root_project_id_project",
        ),
        sa.ForeignKeyConstraint(
            ["project_root_data_id"],
            ["project_data.id"],
            name="fk_project_root_project_root_data_id_project_data",
        ),
        sa.PrimaryKeyConstraint("project_id", name="pk_project_root"),
    )
    conn = op.get_bind()
    nb = conn.execute(sa.text("SELECT count(id) FROM project")).fetchone()[0]
    count = 0
    progress_bar(count, nb)
    for (project_id,) in conn.execute(sa.text("SELECT id FROM project")):
        pdata = conn.execute(
            sa.text(
                "SELECT id FROM project_data "
                f"WHERE project_id = {project_id} AND data_type = 'generator'"
            )
        ).fetchone()
        pdata = None if pdata is None else pdata[0]
        if pdata is None:
            # Create a blank DataGenerator named "Root"
            pdata = conn.execute(
                sa.text(
                    "INSERT INTO project_data "
                    "(data_type, project_id, name, description) "
                    f"VALUES ('generator', {project_id}, 'Root', '') "
                    "RETURNING id"
                )
            ).fetchone()[0]
            # Add default blank category_rules
            model = conn.execute(
                sa.text(
                    "INSERT INTO processing_model "
                    "(model_type, data_generator_id, name, cut_to_extent, "
                    "keep_overlap) "
                    f"VALUES ('categories_rule', {pdata}, '', true, 'max') "
                    "RETURNING id"
                )
            ).fetchone()[0]
            # Make it its active model
            conn.execute(
                sa.text(
                    f"UPDATE project_data SET active_model_id = {model} "
                    f"WHERE id = {pdata}"
                )
            )
        # Make project_data the root data of project
        conn.execute(
            sa.text(
                f"INSERT INTO project_root (project_id, project_root_data_id) "
                f"VALUES ({project_id}, {pdata})"
            )
        )
        count += 1
        progress_bar(count, nb)
