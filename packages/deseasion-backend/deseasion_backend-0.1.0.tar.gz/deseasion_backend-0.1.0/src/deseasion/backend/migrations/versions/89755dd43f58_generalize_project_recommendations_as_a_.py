"""Generalize project recommendations as a processing model

Revision ID: 89755dd43f58
Revises: 339b5d6198df
Create Date: 2025-04-10 13:24:13.983551

"""

from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "89755dd43f58"
down_revision = "339b5d6198df"
branch_labels = None
depends_on = None


old_modeltype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    name="modeltype",
)
new_modeltype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    "zone_proposition",
    name="modeltype",
)
tmp_modeltype = sa.Enum(
    "categories_rule",
    "continuous_rule",
    "geo_buffer",
    "mrsort",
    "weighted_sum",
    "merge_overlap",
    "dissolve_adjacent",
    "zone_proposition",
    name="_modeltype",
)

old_task_type = sa.Enum(
    "process_project_data",
    "process_zone_proposition",
    "update_stream",
    name="projecttasktype",
)
new_task_type = sa.Enum(
    "process_project_data",
    "update_stream",
    name="projecttasktype",
)
tmp_task_type = sa.Enum(
    "process_project_data",
    "update_stream",
    name="_projecttasktype",
)

old_geodatatype = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "proposition_geo_data",
    name="geodatatype",
)
new_geodatatype = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "proposition_geo_data",
    "global_data",
    name="geodatatype",
)
tmp_geodatatype = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "proposition_geo_data",
    "global_data",
    name="_geodatatype",
)

base_data = sa.Table(
    "base_data",
    sa.MetaData(),
    sa.Column("type", new_geodatatype, nullable=True),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("properties_modified_at", sa.DateTime(), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column(
        "extent",
        Geometry(
            spatial_index=False, from_text="ST_GeomFromEWKT", name="geometry"
        ),
        nullable=True,
    ),
)

processing_model = sa.Table(
    "processing_model",
    sa.MetaData(),
    sa.Column(
        "model_type",
        new_modeltype,
        nullable=True,
    ),
    sa.Column("name", sa.String(), nullable=True),
    sa.Column("data_generator_id", sa.Integer(), nullable=False),
    sa.Column(
        "keep_overlap",
        sa.Enum("min", "max", "sum", "average", name="keepoverlap"),
        nullable=False,
    ),
    sa.Column("cut_to_extent", sa.Boolean(), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("radius", sa.BigInteger(), nullable=True),
    sa.Column("majority_threshold", sa.Float(), nullable=True),
    sa.Column("rule", sa.String(), nullable=True),
    sa.Column("geo_size", sa.Float(), nullable=True),
    sa.Column("iterations", sa.Integer(), nullable=True),
    sa.Column("duration", sa.Float(), nullable=True),
    sa.Column("size", sa.Integer(), nullable=True),
    sa.Column("mutation", sa.Float(), nullable=True),
    sa.Column("children", sa.Integer(), nullable=True),
    sa.Column("filter_clusters", sa.Boolean(), nullable=True),
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
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
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

zone_proposition = sa.Table(
    "zone_proposition",
    sa.MetaData(),
    sa.Column("data_id", sa.Integer(), nullable=True),
    sa.Column("project_id", sa.Integer(), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
)

project_task = sa.Table(
    "project_task",
    sa.MetaData(),
    sa.Column("task_id", sa.String(), nullable=True),
    sa.Column("started_at", sa.DateTime(), nullable=True),
    sa.Column("finished_at", sa.DateTime(), nullable=True),
    sa.Column("state", sa.String(), nullable=True),
    sa.Column("error_message", sa.String(), nullable=True),
    sa.Column(
        "type",
        sa.Enum(
            "process_project_data",
            "process_zone_proposition",
            name="projecttasktype",
        ),
        nullable=True,
    ),
    sa.Column(
        "params", postgresql.JSONB(astext_type=sa.Text()), nullable=True
    ),
    sa.Column("project_id", sa.Integer(), nullable=False),
    sa.Column("id", sa.Integer(), nullable=False),
)

project_root = sa.Table(
    "project_root",
    sa.MetaData(),
    sa.Column("project_id", sa.Integer(), nullable=False),
    sa.Column("project_root_data_id", sa.Integer(), nullable=True),
)


def upgrade():
    # Replace old modeltype with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_modeltype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE processing_model ALTER COLUMN model_type TYPE _modeltype"
        " USING model_type::text::_modeltype"
    )
    old_modeltype.drop(op.get_bind(), checkfirst=False)
    new_modeltype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE processing_model ALTER COLUMN model_type TYPE modeltype"
        " USING model_type::text::modeltype"
    )
    tmp_modeltype.drop(op.get_bind(), checkfirst=False)

    with op.batch_alter_table("processing_model", schema=None) as batch_op:
        batch_op.add_column(sa.Column("geo_size", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column("iterations", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("duration", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("size", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("mutation", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("children", sa.Integer(), nullable=True))
        batch_op.add_column(
            sa.Column("filter_clusters", sa.Boolean(), nullable=True)
        )

    # Replace all zone propositions/proposition geo data with zone proposition
    # project data
    conn = op.get_bind()

    # Initialize progress bar
    nb = conn.execute(
        sa.text("SELECT count(id) FROM zone_proposition")
    ).fetchone()[0]
    count = 0
    print("Migrating Project Recommendations")
    progress_bar(count, nb)

    zone_prop_res = conn.execute(
        sa.select(
            zone_proposition.c["data_id", "project_id"],
            base_data.c["name", "created_at", "modified_at"],
            project_root.c["project_root_data_id"],
        )
        .join(base_data, zone_proposition.c.data_id == base_data.c.id)
        .join(
            project_root,
            project_root.c.project_id == zone_proposition.c.project_id,
        )
    )
    now = datetime.now(timezone.utc)
    new_model_map = {}
    for (
        data_id,
        project_id,
        name,
        created_at,
        modified_at,
        root_id,
    ) in zone_prop_res:
        # Fetch project task that built recommendations
        task_params = conn.execute(
            sa.select(project_task.c["params"])
            .where(
                project_task.c.project_id == project_id,
                project_task.c.type == "process_zone_proposition",
                project_task.c.state == "SUCCESS",
            )
            .order_by(sa.desc(project_task.c.finished_at))
        ).fetchone()[0]
        if "iterations" not in task_params and "duration" not in task_params:
            task_params["iterations"] = 1
        if "ga_params" not in task_params:
            task_params["ga_params"] = {}
        task_params["ga_params"]["mutation"] = task_params["ga_params"].get(
            "mutation", 0.02
        )
        task_params["ga_params"]["children"] = task_params["ga_params"].get(
            "children", 60
        )
        task_params["ga_params"]["filter_clusters"] = task_params[
            "ga_params"
        ].get("filter_clusters", True)
        task_params["ga_params"]["size"] = task_params["ga_params"].get(
            "size", 80
        )
        # Create new project data for recommendations
        pdata_id = conn.execute(
            project_data.insert()
            .values(
                data_type="generator",
                project_id=project_id,
                name=name,
                created_at=created_at,
                modified_at=now,
                last_update=modified_at,
                data_id=data_id,
            )
            .returning(project_data.c["id"])
        ).fetchone()[0]
        # Create zone proposition processing model
        model_id = conn.execute(
            processing_model.insert()
            .values(
                model_type="zone_proposition",
                data_generator_id=pdata_id,
                keep_overlap="max",
                geo_size=task_params.get("geo_size", 0),
                iterations=task_params.get("iterations"),
                duration=task_params.get("duration"),
                **task_params["ga_params"],
            )
            .returning(processing_model.c["id"])
        ).fetchone()[0]
        # Use new model as active model for new project data
        conn.execute(
            project_data.update()
            .values(active_model_id=model_id)
            .where(project_data.c.id == pdata_id)
        )
        new_model_map[project_id] = model_id
        # Change type of proposition geo data as generated geo data
        conn.execute(
            base_data.update()
            .values(type="generated_geo_data")
            .where(base_data.c.id == data_id)
        )
        # Add Root as input of new project data
        conn.execute(
            input_assoc.insert().values(
                project_data_id=pdata_id, input_data_id=root_id
            )
        )
        count += 1
        progress_bar(count, nb)

    # Initialize progress bar
    nb = conn.execute(
        sa.text(
            "SELECT count(project_id) FROM project_task "
            "WHERE type = 'process_zone_proposition'"
        )
    ).fetchone()[0]
    count = 0
    print("Migrating Project Tasks")
    progress_bar(count, nb)

    recomm_task_res = conn.execute(
        sa.select(project_task.c["project_id"]).where(
            project_task.c.type == "process_zone_proposition"
        )
    )
    for (project_id,) in recomm_task_res:
        conn.execute(
            project_task.update()
            .values(
                type="process_project_data",
                params={"model_id": new_model_map.get(project_id)},
            )
            .where(
                project_task.c.project_id == project_id,
                project_task.c.type == "process_zone_proposition",
            )
        )
        count += 1
        progress_bar(count, nb)

    # Replace old geodatatype with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_geodatatype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE _geodatatype"
        " USING type::text::_geodatatype"
    )
    old_geodatatype.drop(op.get_bind(), checkfirst=False)
    new_geodatatype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE geodatatype"
        " USING type::text::geodatatype"
    )
    tmp_geodatatype.drop(op.get_bind(), checkfirst=False)

    # Replace old task type with new one
    tmp_task_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_task ALTER COLUMN type TYPE _projecttasktype"
        " USING type::text::_projecttasktype"
    )
    old_task_type.drop(op.get_bind(), checkfirst=False)
    new_task_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_task ALTER COLUMN type TYPE projecttasktype"
        " USING type::text::projecttasktype"
    )
    tmp_task_type.drop(op.get_bind(), checkfirst=False)

    op.drop_table("zone_proposition")


def downgrade():
    op.create_table(
        "zone_proposition",
        sa.Column("data_id", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column(
            "project_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["data_id"],
            ["base_data.id"],
            name="fk_zone_proposition_data_id_base_data",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["project.id"],
            name="fk_zone_proposition_project_id_project",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_zone_proposition"),
    )

    now = datetime.now(timezone.utc)
    conn = op.get_bind()
    nb = conn.execute(
        sa.text(
            "SELECT count(pm.id) FROM processing_model pm "
            "JOIN project_data pd ON pd.active_model_id = pm.id "
            "WHERE pm.model_type = 'zone_proposition'"
        )
    ).fetchone()[0]
    count = 0
    progress_bar(count, nb)
    active_zone_props = conn.execute(
        sa.select(
            processing_model.c["id", "data_generator_id"],
            project_data.c["data_id"],
        )
        .join(
            project_data,
            project_data.c.active_model_id == processing_model.c.id,
        )
        .where(processing_model.c.model_type == "zone_proposition")
    )
    # Iterate over all active zone proposition models
    for model_id, pdata_id, data_id in active_zone_props:
        # Get other-types of model of the project_data
        other_models = [
            mid
            for (mid,) in conn.execute(
                sa.select(processing_model.c["id"]).where(
                    processing_model.c.data_generator_id == pdata_id,
                    processing_model.c.id != model_id,
                    processing_model.c.model_type != "zone_proposition",
                )
            )
        ]
        if len(other_models) == 0:
            # Delete model and project data
            # First detach model from project data
            conn.execute(
                project_data.update()
                .values(active_model_id=None, data_id=None)
                .where(project_data.c.id == pdata_id)
            )
            # Delete model
            conn.execute(
                processing_model.delete().where(
                    processing_model.c.id == model_id
                )
            )
            # Remove refs to project data
            conn.execute(
                input_assoc.delete().where(
                    input_assoc.c.project_data_id == pdata_id
                )
            )
            conn.execute(
                input_assoc.delete().where(
                    input_assoc.c.input_data_id == pdata_id
                )
            )
            if data_id is not None:
                conn.execute(
                    sa.text(
                        "DELETE FROM geo_feature "
                        "WHERE id IN ("
                        "SELECT f.id FROM feature f "
                        f"WHERE f.data_id = {data_id})"
                    )
                )
                conn.execute(
                    sa.text(f"DELETE FROM feature WHERE data_id = {data_id}")
                )
                conn.execute(
                    sa.text(
                        "DELETE FROM data_value WHERE attribute_id IN"
                        "(SELECT a.id FROM data_attribute a "
                        f"WHERE a.data_id = {data_id})"
                    )
                )
                conn.execute(
                    sa.text(
                        f"DELETE FROM data_attribute WHERE data_id = {data_id}"
                    )
                )
                conn.execute(
                    base_data.delete().where(base_data.c.id == data_id)
                )
            # Delete project data
            conn.execute(
                project_data.delete().where(project_data.c.id == pdata_id)
            )
        else:
            # Replace active model with other model
            conn.execute(
                project_data.update()
                .values(active_model_id=other_models[0], modified_at=now)
                .where(project_data.c.id == pdata_id)
            )
        count += 1
        progress_bar(count, nb)

    # Remove all inactive zone proposition (all remainings are inactive now)
    op.execute(
        processing_model.delete().where(
            processing_model.c.model_type == "zone_proposition"
        )
    )

    with op.batch_alter_table("processing_model", schema=None) as batch_op:
        batch_op.drop_column("filter_clusters")
        batch_op.drop_column("children")
        batch_op.drop_column("mutation")
        batch_op.drop_column("size")
        batch_op.drop_column("duration")
        batch_op.drop_column("iterations")
        batch_op.drop_column("geo_size")

    # Replace new modeltype with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_modeltype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE processing_model ALTER COLUMN model_type "
        "TYPE _modeltype USING model_type::text::_modeltype"
    )
    new_modeltype.drop(op.get_bind(), checkfirst=False)
    old_modeltype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE processing_model ALTER COLUMN model_type "
        "TYPE modeltype USING model_type::text::modeltype"
    )
    tmp_modeltype.drop(op.get_bind(), checkfirst=False)

    # Replace new geodatatype with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_geodatatype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE _geodatatype"
        " USING type::text::_geodatatype"
    )
    new_geodatatype.drop(op.get_bind(), checkfirst=False)
    old_geodatatype.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE geodatatype"
        " USING type::text::geodatatype"
    )
    tmp_geodatatype.drop(op.get_bind(), checkfirst=False)

    # Replace new task type with old one
    tmp_task_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_task ALTER COLUMN type TYPE _projecttasktype"
        " USING type::text::_projecttasktype"
    )
    new_task_type.drop(op.get_bind(), checkfirst=False)
    old_task_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_task ALTER COLUMN type TYPE projecttasktype"
        " USING type::text::projecttasktype"
    )
    tmp_task_type.drop(op.get_bind(), checkfirst=False)
