"""add project template permissions

Revision ID: c6e3da96b784
Revises: 2657de160d2c
Create Date: 2025-05-27 16:27:22.815170

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c6e3da96b784"
down_revision = "2657de160d2c"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        sa.text(
            "INSERT INTO project_permission (object_id, user_id) "
            "SELECT id, manager_id FROM project WHERE is_template=true"
        )
    )


def downgrade():
    op.execute(
        sa.text(
            "DELETE FROM project_permission WHERE object_id IN ("
            "SELECT id FROM project WHERE is_template=true"
            ")"
        )
    )
