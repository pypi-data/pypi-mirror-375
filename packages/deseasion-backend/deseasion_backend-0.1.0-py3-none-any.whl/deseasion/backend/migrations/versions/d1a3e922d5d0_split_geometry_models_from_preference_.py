"""Split geometry models from preference models

Revision ID: d1a3e922d5d0
Revises: 9a7260e6a3bf
Create Date: 2025-02-12 15:57:55.461329

"""

import sqlalchemy as sa
from alembic import op

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "d1a3e922d5d0"
down_revision = "9a7260e6a3bf"
branch_labels = None
depends_on = None


old_preftype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    name="preftype",
)
new_preftype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    name="preftype",
)
tmp_preftype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    name="_preftype",
)


old_keepoverlap = sa.Enum(
    "all",
    "min",
    "max",
    "sum",
    "average",
    name="keepoverlap",
)
new_keepoverlap = sa.Enum(
    "min",
    "max",
    "sum",
    "average",
    name="keepoverlap",
)
tmp_keepoverlap = sa.Enum(
    "all",
    "min",
    "max",
    "sum",
    "average",
    name="_keepoverlap",
)


project_root = sa.Table(
    "project_root",
    sa.MetaData(),
    sa.Column("project_id", sa.Integer(), nullable=False),
    sa.Column("project_root_data_id", sa.Integer(), nullable=False),
)


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
    sa.Column("last_update", sa.DateTime(), nullable=True),
    sa.Column("project_id", sa.Integer(), nullable=False),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column("name", sa.String(), nullable=True),
    sa.Column("active_model_id", sa.Integer(), nullable=True),
)


input_assoc = sa.Table(
    "data_input_association",
    sa.MetaData(),
    sa.Column("project_data_id", sa.Integer(), nullable=False),
    sa.Column("input_data_id", sa.Integer(), nullable=False),
)


preference_model = sa.Table(
    "preference_model",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("pref_type", new_preftype, nullable=True),
    sa.Column("name", sa.String(), nullable=True),
    sa.Column("data_generator_id", sa.Integer(), nullable=False),
    sa.Column("cut_to_extent", sa.Boolean(), nullable=True),
    sa.Column(
        "keep_overlap",
        sa.Enum("all", "min", "max", "sum", "average", name="keepoverlap"),
        nullable=False,
    ),
    sa.Column("radius", sa.BigInteger(), nullable=True),
    sa.Column("majority_threshold", sa.Float(), nullable=True),
    sa.Column("rule", sa.String(), nullable=True),
)

old_preference_model = sa.Table(
    "preference_model",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("pref_type", new_preftype, nullable=True),
    sa.Column("name", sa.String(), nullable=True),
    sa.Column("data_generator_id", sa.Integer(), nullable=False),
    sa.Column(
        "keep_overlap",
        sa.Enum("all", "min", "max", "sum", "average", name="keepoverlap"),
        nullable=False,
    ),
    sa.Column("cut_to_extent", sa.Boolean(), nullable=True),
    sa.Column("dissolve_adjacent", sa.Boolean(), nullable=True),
    sa.Column("radius", sa.BigInteger(), nullable=True),
    sa.Column("majority_threshold", sa.Float(), nullable=True),
    sa.Column("rule", sa.String(), nullable=True),
)


def upgrade():
    # Replace old preftype with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_preftype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN pref_type TYPE _preftype"
        " USING pref_type::text::_preftype"
    )
    old_preftype.drop(op.get_bind(), checkfirst=False)
    new_preftype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN pref_type TYPE preftype"
        " USING pref_type::text::preftype"
    )
    tmp_preftype.drop(op.get_bind(), checkfirst=False)

    conn = op.get_bind()

    nb_migration_ops = conn.execute(
        sa.text(
            "SELECT count(pdata.id) FROM project_data AS pdata "
            "JOIN preference_model as pref ON pdata.active_model_id = pref.id "
            "WHERE pref.dissolve_adjacent = true"
        )
    ).fetchone()[0]
    nb_migration_ops += conn.execute(
        sa.text(
            "SELECT count(pdata.id) FROM project_data AS pdata "
            "JOIN preference_model as pref ON pdata.active_model_id = pref.id "
            "WHERE pref.keep_overlap != 'all'"
        )
    ).fetchone()[0]
    op_it = 0
    progress_bar(op_it, nb_migration_ops)

    # Get all project data with active model with dissolve adjacent to true
    res = conn.execute(
        sa.select(
            project_data.c[
                "id", "project_id", "name", "data_id", "last_update"
            ],
            old_preference_model.c["cut_to_extent"],
            project_root.c["project_root_data_id"],
        )
        .join(
            old_preference_model,
            project_data.c.active_model_id == old_preference_model.c.id,
        )
        .join(
            project_root,
            project_root.c.project_id == project_data.c.project_id,
        )
        .where(
            old_preference_model.c.dissolve_adjacent
            == True  # noqa: E712, E501
        )
    )
    for (
        pdata_id,
        project_id,
        name,
        data_id,
        last_update,
        cut_to_e,
        project_root_id,
    ) in res:
        # Insert new empty data generator in project
        # And give it current generated data
        new_pdata = conn.execute(
            project_data.insert()
            .values(
                data_type="generator",
                project_id=project_id,
                name=name,
                data_id=data_id,
                last_update=last_update,
            )
            .returning(project_data.c.id)
        ).first()
        # Insert new dissolve_adjacent model into created data generator
        new_model = conn.execute(
            preference_model.insert()
            .values(
                pref_type="dissolve_adjacent",
                data_generator_id=new_pdata[0],
                cut_to_extent=cut_to_e,
                keep_overlap="all",
            )
            .returning(preference_model.c.id)
        ).first()
        # Make dissolve adjacent model active
        conn.execute(
            project_data.update()
            .where(project_data.c.id == new_pdata[0])
            .values(active_model_id=new_model[0])
        )
        # Detach generated data from old project data
        # Reset last_update of current project data which data is moved
        conn.execute(
            project_data.update()
            .where(project_data.c.id == pdata_id)
            .values(data_id=None, last_update=None)
        )
        # Rewire all project data inputs from project data to new data
        # generator
        conn.execute(
            input_assoc.update()
            .where(input_assoc.c.input_data_id == pdata_id)
            .values(input_data_id=new_pdata[0])
        )
        # Add project data as an input to new data generator
        conn.execute(
            input_assoc.insert().values(
                project_data_id=new_pdata[0], input_data_id=pdata_id
            )
        )
        if pdata_id == project_root_id:
            # Data is root of project => update to new project data
            conn.execute(
                project_root.update()
                .where(project_root.c.project_id == project_id)
                .values(project_root_data_id=new_pdata[0])
            )
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    # Remove dissolve_adjacent preference model column
    with op.batch_alter_table("preference_model", schema=None) as batch_op:
        batch_op.drop_column("dissolve_adjacent")

    res = conn.execute(
        sa.select(
            project_data.c[
                "id", "project_id", "name", "data_id", "last_update"
            ],
            old_preference_model.c["cut_to_extent", "keep_overlap"],
            project_root.c["project_root_data_id"],
        )
        .join(
            old_preference_model,
            project_data.c.active_model_id == old_preference_model.c.id,
        )
        .join(
            project_root,
            project_root.c.project_id == project_data.c.project_id,
        )
        .where(old_preference_model.c.keep_overlap != "all")
    )
    for (
        pdata_id,
        project_id,
        name,
        data_id,
        last_update,
        cut_to_e,
        keep_overlap,
        project_root_id,
    ) in res:
        # Insert new empty data generator in project
        # And give it current generated data
        new_pdata = conn.execute(
            project_data.insert()
            .values(
                data_type="generator",
                project_id=project_id,
                name=name,
                data_id=data_id,
                last_update=last_update,
            )
            .returning(project_data.c.id)
        ).first()
        # Insert new merge_overlap model into created data generator
        new_model = conn.execute(
            preference_model.insert()
            .values(
                pref_type="merge_overlap",
                data_generator_id=new_pdata[0],
                cut_to_extent=cut_to_e,
                keep_overlap=keep_overlap,
            )
            .returning(preference_model.c.id)
        ).first()
        # Make merge overlap model active
        conn.execute(
            project_data.update()
            .where(project_data.c.id == new_pdata[0])
            .values(active_model_id=new_model[0])
        )
        # Detach generated data from old project data
        # Reset last_update of current project data which data is moved
        conn.execute(
            project_data.update()
            .where(project_data.c.id == pdata_id)
            .values(data_id=None, last_update=None)
        )
        # Rewire all project data inputs from project data to new data
        # generator
        conn.execute(
            input_assoc.update()
            .where(input_assoc.c.input_data_id == pdata_id)
            .values(input_data_id=new_pdata[0])
        )
        # Add project data as an input to new data generator
        conn.execute(
            input_assoc.insert().values(
                project_data_id=new_pdata[0], input_data_id=pdata_id
            )
        )
        if pdata_id == project_root_id:
            # Data is root of project => update to new project data
            conn.execute(
                project_root.update()
                .where(project_root.c.project_id == project_id)
                .values(project_root_data_id=new_pdata[0])
            )
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    # Remove all keep_overlap 'all' values, replace with default
    op.execute(
        preference_model.update()
        .where(preference_model.c.keep_overlap == "all")
        .values(keep_overlap="max")
    )

    # Replace old keepoverlap with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_keepoverlap.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN keep_overlap "
        "TYPE _keepoverlap USING keep_overlap::text::_keepoverlap"
    )
    old_keepoverlap.drop(op.get_bind(), checkfirst=False)
    new_keepoverlap.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN keep_overlap "
        "TYPE keepoverlap USING keep_overlap::text::keepoverlap"
    )
    tmp_keepoverlap.drop(op.get_bind(), checkfirst=False)


def downgrade():
    # Replace new keepoverlap with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_keepoverlap.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN keep_overlap "
        "TYPE _keepoverlap USING keep_overlap::text::_keepoverlap"
    )
    new_keepoverlap.drop(op.get_bind(), checkfirst=False)
    old_keepoverlap.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN keep_overlap "
        "TYPE keepoverlap USING keep_overlap::text::keepoverlap"
    )
    tmp_keepoverlap.drop(op.get_bind(), checkfirst=False)

    with op.batch_alter_table("preference_model", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "dissolve_adjacent",
                sa.BOOLEAN(),
                autoincrement=False,
                nullable=True,
                default=False,
            )
        )

    # Replace keep_overlap with default 'all' in all but merge_overlap models
    op.execute(
        old_preference_model.update()
        .where(
            old_preference_model.c.pref_type != "merge_overlap"
        )  # noqa: E711
        .values(keep_overlap="all")
    )

    conn = op.get_bind()

    nb_migration_ops = conn.execute(
        sa.text(
            "SELECT count(pdata.id) FROM project_data AS pdata "
            "JOIN preference_model as pref ON pdata.active_model_id = pref.id "
            "WHERE pref.pref_type IN ('dissolve_adjacent', 'merge_overlap')"
        )
    ).fetchone()[0]
    op_it = 0
    progress_bar(op_it, nb_migration_ops)

    # Get all project data with active model dissolve adjacent
    res = conn.execute(
        sa.select(
            project_data.c["id", "last_update", "data_id", "project_id"],
            project_root.c["project_root_data_id"],
        )
        .join(
            old_preference_model,
            project_data.c.active_model_id == old_preference_model.c.id,
        )
        .join(
            project_root,
            project_root.c.project_id == project_data.c.project_id,
        )
        .where(old_preference_model.c.pref_type == "dissolve_adjacent")
    )
    for (
        pdata_id,
        last_update,
        data_id,
        project_id,
        project_root_id,
    ) in res:
        # Get unique input of project data
        input_id = conn.execute(
            sa.select(input_assoc.c["input_data_id"]).where(
                input_assoc.c.project_data_id == pdata_id
            )
        ).fetchone()[0]

        # Get every other output of project data's input
        other_outputs_of_input = conn.execute(
            input_assoc.select().where(
                input_assoc.c.input_data_id == input_id,
                input_assoc.c.project_data_id != pdata_id,
            )
        ).all()
        # Rewire all project data outputs to input data
        conn.execute(
            input_assoc.update()
            .where(input_assoc.c.input_data_id == pdata_id)
            .values(input_data_id=input_id)
        )
        # Remove link between project data and its input
        conn.execute(
            input_assoc.delete().where(
                input_assoc.c.project_data_id == pdata_id
            )
        )
        if pdata_id == project_root_id:
            # Data is root of project => update to new project data
            conn.execute(
                project_root.update()
                .where(project_root.c.project_id == project_id)
                .values(project_root_data_id=input_id)
            )

        if len(other_outputs_of_input) == 0:
            # project data is the only output of its input data
            # We can merge them
            input_model = conn.execute(
                sa.select(
                    old_preference_model.c["id"],
                )
                .join(
                    project_data,
                    old_preference_model.c.data_generator_id
                    == project_data.c.id,
                )
                .where(
                    old_preference_model.c.data_generator_id == input_id,
                    old_preference_model.c.id
                    == project_data.c.active_model_id,
                )
            ).first()
            # Make input data active model dissolve adjacent
            conn.execute(
                old_preference_model.update()
                .where(old_preference_model.c.id == input_model[0])
                .values(dissolve_adjacent=True)
            )
            # Move generated data from project data to input data
            conn.execute(
                project_data.update()
                .where(project_data.c.id == input_id)
                .values(data_id=data_id, last_update=last_update)
            )
        # Set project data active model to null
        # So to remove references to project_data
        conn.execute(
            project_data.update()
            .where(project_data.c.id == pdata_id)
            .values(active_model_id=None)
        )
        # Remove project_data models
        conn.execute(
            old_preference_model.delete().where(
                old_preference_model.c.data_generator_id == pdata_id
            )
        )
        # Remove project data
        conn.execute(
            project_data.delete().where(project_data.c.id == pdata_id)
        )
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    # Get all project data with an active merge_overlap model
    res = conn.execute(
        sa.select(
            project_data.c["id", "last_update", "data_id", "project_id"],
            old_preference_model.c["keep_overlap", "dissolve_adjacent"],
            project_root.c["project_root_data_id"],
        )
        .join(
            old_preference_model,
            project_data.c.active_model_id == old_preference_model.c.id,
        )
        .join(
            project_root,
            project_root.c.project_id == project_data.c.project_id,
        )
        .where(old_preference_model.c.pref_type == "merge_overlap")
    )
    for (
        pdata_id,
        last_update,
        data_id,
        project_id,
        keep_overlap,
        dissolve_adjacent,
        project_root_id,
    ) in res:
        # Get unique input of project data
        input_id = conn.execute(
            sa.select(input_assoc.c["input_data_id"]).where(
                input_assoc.c.project_data_id == pdata_id
            )
        ).fetchone()[0]

        # Get every other output of project data's input
        other_outputs_of_input = conn.execute(
            input_assoc.select().where(
                input_assoc.c.input_data_id == input_id,
                input_assoc.c.project_data_id != pdata_id,
            )
        ).all()
        # Rewire all project data outputs to input data
        conn.execute(
            input_assoc.update()
            .where(input_assoc.c.input_data_id == pdata_id)
            .values(input_data_id=input_id)
        )
        # Remove link between project data and its input
        conn.execute(
            input_assoc.delete().where(
                input_assoc.c.project_data_id == pdata_id
            )
        )
        if pdata_id == project_root_id:
            # Data is root of project => update to new project data
            conn.execute(
                project_root.update()
                .where(project_root.c.project_id == project_id)
                .values(project_root_data_id=input_id)
            )

        if len(other_outputs_of_input) == 0:
            # project data is the only output of its input data
            # We can merge them
            input_model = conn.execute(
                sa.select(
                    old_preference_model.c["id"],
                )
                .join(
                    project_data,
                    old_preference_model.c.data_generator_id
                    == project_data.c.id,
                )
                .where(
                    old_preference_model.c.data_generator_id == input_id,
                    old_preference_model.c.id
                    == project_data.c.active_model_id,
                )
            ).first()
            # Make input data active model dissolve adjacent
            conn.execute(
                old_preference_model.update()
                .where(old_preference_model.c.id == input_model[0])
                .values(
                    keep_overlap=keep_overlap,
                    dissolve_adjacent=dissolve_adjacent,
                )
            )
            # Move generated data from project data to input data
            conn.execute(
                project_data.update()
                .where(project_data.c.id == input_id)
                .values(data_id=data_id, last_update=last_update)
            )
        # Set project data active model to null
        # So to remove references to project_data
        conn.execute(
            project_data.update()
            .where(project_data.c.id == pdata_id)
            .values(active_model_id=None)
        )
        # Remove project_data models
        conn.execute(
            old_preference_model.delete().where(
                old_preference_model.c.data_generator_id == pdata_id
            )
        )
        # Remove project data
        conn.execute(
            project_data.delete().where(project_data.c.id == pdata_id)
        )
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    # Replace new preftype with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_preftype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN pref_type "
        "TYPE _preftype USING pref_type::text::_preftype"
    )
    new_preftype.drop(op.get_bind(), checkfirst=False)
    old_preftype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE preference_model ALTER COLUMN pref_type "
        "TYPE preftype USING pref_type::text::preftype"
    )
    tmp_preftype.drop(op.get_bind(), checkfirst=False)
