"""Remove explainability field

Revision ID: 339b5d6198df
Revises: 141e705ab129
Create Date: 2025-04-08 11:38:17.264425

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "339b5d6198df"
down_revision = "141e705ab129"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "feature",
        sa.Column(
            "execution_artifact",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    conn = op.get_bind()
    nb_op = conn.execute(
        sa.text("SELECT count(id) FROM feature WHERE explainability != '[]'")
    ).fetchone()[0]
    res = conn.execute(
        sa.text(
            "SELECT id, explainability FROM feature "
            "WHERE explainability != '[]'"
        )
    )
    i = 0
    progress_bar(i, nb_op)
    for id, explainability in res:
        if not isinstance(explainability, dict):
            continue
        if explainability["model_type"] == "categories_rule":
            conn.execute(
                sa.text(
                    f"UPDATE feature SET execution_artifact = "
                    f"'{{\"rule\": \"{explainability['rule']}\"}}' "
                    f"WHERE id = {id}"
                )
            )
        i += 1
        progress_bar(i, nb_op)

    op.drop_column("feature", "explainability")


def downgrade():
    with op.batch_alter_table("feature", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "explainability",
                postgresql.JSONB(astext_type=sa.Text()),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.drop_column("execution_artifact")
