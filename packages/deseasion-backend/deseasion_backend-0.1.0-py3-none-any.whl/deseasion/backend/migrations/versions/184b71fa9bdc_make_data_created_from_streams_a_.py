"""Make data created from streams a project data only

Revision ID: 184b71fa9bdc
Revises: c6bfa5794b5c
Create Date: 2025-02-26 15:30:07.436792

"""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry
from sqlalchemy.dialects import postgresql

from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "184b71fa9bdc"
down_revision = "c6bfa5794b5c"
branch_labels = None
depends_on = None


old_data_type = sa.Enum(
    "geo_data",
    "generator",
    "global_data",
    name="datatype",
)
new_data_type = sa.Enum(
    "geo_data",
    "generator",
    "global_data",
    "data_stream",
    name="datatype",
)
tmp_data_type = sa.Enum(
    "geo_data",
    "generator",
    "global_data",
    "data_stream",
    name="_datatype",
)

old_task_type = sa.Enum(
    "process_project_data",
    "process_zone_proposition",
    name="projecttasktype",
)
new_task_type = sa.Enum(
    "process_project_data",
    "process_zone_proposition",
    "update_stream",
    name="projecttasktype",
)
tmp_task_type = sa.Enum(
    "process_project_data",
    "process_zone_proposition",
    "update_stream",
    name="_projecttasktype",
)


base_data = sa.Table(
    "base_data",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum("geo_data", "generator", "global_data", name="datatype"),
        nullable=True,
    ),
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


old_geo_data = sa.Table(
    "geo_data",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum(
            "geo_data",
            "generated_geo_data",
            "proposition_geo_data",
            "global_data",
            name="geodatatype",
        ),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column(
        "extent",
        Geometry(
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
        ),
        nullable=True,
    ),
    sa.Column("properties_modified_at", sa.DateTime(), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("original_name", sa.String(), nullable=True),
    sa.Column("source_driver", sa.String(), nullable=True),
    sa.Column("upload_user_id", sa.Integer(), nullable=True),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column("stream_id", sa.Integer(), nullable=True),
    sa.Column("is_public", sa.Boolean(), nullable=False),
)

new_geo_data = sa.Table(
    "geo_data",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum(
            "geo_data",
            "generated_geo_data",
            "proposition_geo_data",
            "global_data",
            name="geodatatype",
        ),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column(
        "extent",
        Geometry(
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
        ),
        nullable=True,
    ),
    sa.Column("properties_modified_at", sa.DateTime(), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("original_name", sa.String(), nullable=True),
    sa.Column("source_driver", sa.String(), nullable=True),
    sa.Column("upload_user_id", sa.Integer(), nullable=True),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column("is_public", sa.Boolean(), nullable=False),
)

feature = sa.Table(
    "feature",
    sa.MetaData(),
    sa.Column("data_id", sa.Integer(), nullable=True),
    sa.Column(
        "explainability",
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column(
        "type",
        sa.Enum("feature", "geo_feature", name="featuretype"),
        nullable=True,
    ),
)

geo_feature = sa.Table(
    "geo_feature",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column(
        "geom",
        Geometry(
            spatial_index=False, from_text="ST_GeomFromEWKT", name="geometry"
        ),
        nullable=True,
    ),
)

attribute = sa.Table(
    "data_attribute",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum("quantitative", "nominal", "ordinal", name="attributetype"),
        nullable=True,
    ),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column(
        "statistics",
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    ),
    sa.Column("data_id", sa.Integer(), nullable=False),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("order", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
)

data_value = sa.Table(
    "data_value",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum("quantitative", "nominal", "ordinal", name="attributetype"),
        nullable=True,
    ),
    sa.Column("attribute_id", sa.Integer(), nullable=True),
    sa.Column("feature_id", sa.Integer(), nullable=True),
    sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
)

old_project_data = sa.Table(
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

new_project_data = sa.Table(
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
    sa.Column("stream_id", sa.Integer(), nullable=True),
    sa.Column(
        "classes",
        postgresql.ARRAY(sa.Float(), dimensions=2),
        nullable=True,
    ),
    sa.Column("start", sa.Float(), nullable=True),
    sa.Column("step", sa.Float(), nullable=True),
    sa.Column("stop", sa.Float(), nullable=True),
    sa.Column("resolution", sa.Float(), nullable=True),
)

input_assoc = sa.Table(
    "data_input_association",
    sa.MetaData(),
    sa.Column(
        "project_data_id",
        sa.Integer,
        nullable=False,
    ),
    sa.Column(
        "input_data_id",
        sa.Integer,
        nullable=False,
    ),
)

feature_input_assoc = sa.Table(
    "feature_input_association",
    sa.MetaData(),
    sa.Column(
        "feature_id",
        sa.Integer,
        nullable=False,
    ),
    sa.Column(
        "input_feature_id",
        sa.Integer,
        nullable=False,
    ),
)

project = sa.Table(
    "project",
    sa.MetaData(),
    sa.Column("is_template", sa.Boolean(), nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("manager_id", sa.Integer(), nullable=True),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column(
        "extent",
        Geometry(
            spatial_index=False,
            from_text="ST_GeomFromEWKT",
            name="geometry",
            nullable=False,
        ),
        nullable=False,
    ),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("is_public", sa.Boolean(), nullable=False),
)

stream_geo_data = sa.Table(
    "stream_geo_data",
    sa.MetaData(),
    sa.Column(
        "type", sa.Enum("wfs", "wms", name="streamdatatype"), nullable=True
    ),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("title", sa.String(), nullable=True),
    sa.Column("original_name", sa.String(), nullable=True),
    sa.Column("url", sa.String(), nullable=False),
    sa.Column("upload_user_id", sa.Integer(), nullable=True),
    sa.Column("description", sa.String(), nullable=True),
    sa.Column(
        "keywords",
        postgresql.ARRAY(sa.String(), dimensions=1),
        nullable=True,
    ),
    sa.Column("is_public", sa.Boolean(), nullable=False),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("modified_at", sa.DateTime(), nullable=True),
    sa.Column("id", sa.Integer(), nullable=False),
)

wms_geo_data = sa.Table(
    "wms_geo_data",
    sa.MetaData(),
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column(
        "classes",
        postgresql.ARRAY(sa.Float(), dimensions=2),
        nullable=True,
    ),
    sa.Column("layer", sa.String(), nullable=False),
    sa.Column("resolution", sa.Float(), nullable=True),
    sa.Column("version", sa.String(), nullable=True),
    sa.Column("start", sa.Float(), nullable=True),
    sa.Column("step", sa.Float(), nullable=True),
    sa.Column("stop", sa.Float(), nullable=True),
)

stream_permission = sa.Table(
    "stream_geo_data_permission",
    sa.MetaData(),
    sa.Column("object_id", sa.Integer(), nullable=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("id", sa.Integer(), nullable=False),
)

geo_data_permission = sa.Table(
    "geo_data_permission",
    sa.MetaData(),
    sa.Column("object_id", sa.Integer(), nullable=True),
    sa.Column("user_id", sa.Integer(), nullable=False),
    sa.Column("id", sa.Integer(), nullable=False),
)

default_value = sa.Table(
    "default_value",
    sa.MetaData(),
    sa.Column("attribute_id", sa.Integer(), nullable=False),
    sa.Column("model_id", sa.Integer(), nullable=False),
    sa.Column("value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
)

processing_model = sa.Table(
    "processing_model",
    sa.MetaData(),
    sa.Column(
        "model_type",
        sa.Enum(
            "categories_rule",
            "continuous_rule",
            "geo_buffer",
            "mrsort",
            "weighted_sum",
            "merge_overlap",
            "dissolve_adjacent",
            name="modeltype",
        ),
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
)

mr_sort_criterion = sa.Table(
    "mrsort_criterion",
    sa.MetaData(),
    sa.Column(
        "profiles",
        postgresql.ARRAY(sa.Float(), dimensions=1),
        nullable=True,
    ),
    sa.Column("weight", sa.Float(), nullable=True),
    sa.Column("maximize", sa.Boolean(), nullable=False),
    sa.Column("mrsort_id", sa.Integer(), nullable=False),
    sa.Column("attribute_id", sa.Integer(), nullable=False),
)

weighted_sum_operand = sa.Table(
    "weighted_sum_operand",
    sa.MetaData(),
    sa.Column("attribute_id", sa.Integer(), nullable=True),
    sa.Column("weight", sa.Float(), nullable=True),
    sa.Column("model_id", sa.Integer(), nullable=False),
    sa.Column("id", sa.Integer(), nullable=False),
)


def upgrade():
    # Replace old data type with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_data ALTER COLUMN data_type TYPE _datatype"
        " USING data_type::text::_datatype"
    )
    old_data_type.drop(op.get_bind(), checkfirst=False)
    new_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_data ALTER COLUMN data_type TYPE datatype"
        " USING data_type::text::datatype"
    )
    tmp_data_type.drop(op.get_bind(), checkfirst=False)

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

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("stream_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "classes",
                postgresql.ARRAY(sa.Float(), dimensions=2),
                nullable=True,
            )
        )
        batch_op.add_column(sa.Column("start", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("step", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("stop", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("resolution", sa.Float(), nullable=True))
        batch_op.create_foreign_key(
            batch_op.f("fk_project_data_stream_id_stream_geo_data"),
            "stream_geo_data",
            ["stream_id"],
            ["id"],
        )

    conn = op.get_bind()

    nb_migration_ops = conn.execute(
        sa.text(
            "SELECT count(p.id) FROM project_data AS p "
            "JOIN geo_data AS g ON g.id = p.data_id "
            "WHERE g.stream_id IS NOT NULL"
        )
    ).fetchone()[0]
    op_it = 0
    progress_bar(op_it, nb_migration_ops)

    # Replace all DataGeo created from stream by DataStream
    res = conn.execute(
        sa.select(
            new_project_data.c["id"],
            old_geo_data.c["stream_id", "id"],
            project.c["id", "manager_id"],
            stream_geo_data.c["is_public", "type"],
        )
        .join(old_geo_data, old_geo_data.c.id == new_project_data.c.data_id)
        .join(project, project.c.id == new_project_data.c.project_id)
        .join(
            stream_geo_data, stream_geo_data.c.id == old_geo_data.c.stream_id
        )
        .where(old_geo_data.c.stream_id != None)  # noqa: E711
    )
    geo_data_modified = []
    new_stream_perms = []
    for (
        p_data_id,
        stream_id,
        data_id,
        proj_id,
        manager_id,
        is_public,
        stream_type,
    ) in res:
        if stream_type == "wms":
            classes, start, step, stop, resolution = conn.execute(
                sa.select(
                    wms_geo_data.c[
                        "classes", "start", "step", "stop", "resolution"
                    ]
                ).where(wms_geo_data.c.id == stream_id)
            ).one()
        else:
            classes = None
            start = None
            step = None
            stop = None
            resolution = None

        # Replace DataGeo with DataStream instance (in place to keep refs)
        conn.execute(
            new_project_data.update()
            .where(new_project_data.c.id == p_data_id)
            .values(
                data_type="data_stream",
                stream_id=stream_id,
                classes=classes,
                start=start,
                step=step,
                stop=stop,
                resolution=resolution,
            )
        )
        if data_id in geo_data_modified:
            # geo_data used elsewhere => duplicate it
            data_sel = sa.select(
                base_data.c[
                    "type",
                    "name",
                    "extent",
                    "properties_modified_at",
                    "created_at",
                    "modified_at",
                ],
            ).where(base_data.c.id == data_id)
            new_data_id = conn.execute(
                base_data.insert()
                .from_select(
                    [
                        "type",
                        "name",
                        "extent",
                        "properties_modified_at",
                        "created_at",
                        "modified_at",
                    ],
                    data_sel,
                )
                .returning(base_data.c.id)
            ).one()[0]

            # Replace data_id in DataStream project data
            conn.execute(
                new_project_data.update()
                .where(new_project_data.c.id == p_data_id)
                .values(data_id=new_data_id)
            )

            # Duplicate attributes
            old_attrs = conn.execute(
                sa.select(
                    attribute.c["id", "type", "name", "statistics", "order"]
                ).where(attribute.c.data_id == data_id)
            )
            attributes_map = {}
            for attr_id, type, name, stats, order in old_attrs:
                attributes_map[attr_id] = conn.execute(
                    attribute.insert()
                    .values(
                        type=type,
                        data_id=new_data_id,
                        name=name,
                        statistics=stats,
                        order=order,
                    )
                    .returning(attribute.c.id)
                ).one()[0]
                # Update attribute links
                # Update links in default_value table
                model_ids = [
                    _row[0]
                    for _row in conn.execute(
                        sa.select(
                            default_value.c["model_id"],
                        )
                        .join(
                            processing_model,
                            processing_model.c.id == default_value.c.model_id,
                        )
                        .join(
                            new_project_data,
                            new_project_data.c.id
                            == processing_model.c.data_generator_id,
                        )
                        .join(
                            project,
                            project.c.id == new_project_data.c.project_id,
                        )
                        .where(project.c.id == proj_id)
                        .where(default_value.c.attribute_id == attr_id)
                    )
                ]
                conn.execute(
                    default_value.update()
                    .where(default_value.c.model_id.in_(model_ids))
                    .where(default_value.c.attribute_id == attr_id)
                    .values(attribute_id=attributes_map[attr_id])
                )
                # Update links in mr_sort_criterion
                mr_sort_ids = [
                    _row[0]
                    for _row in conn.execute(
                        sa.select(mr_sort_criterion.c["mrsort_id"])
                        .join(
                            processing_model,
                            processing_model.c.id
                            == mr_sort_criterion.c.mrsort_id,
                        )
                        .join(
                            new_project_data,
                            new_project_data.c.id
                            == processing_model.c.data_generator_id,
                        )
                        .join(
                            project,
                            project.c.id == new_project_data.c.project_id,
                        )
                        .where(project.c.id == proj_id)
                        .where(mr_sort_criterion.c.attribute_id == attr_id)
                    )
                ]
                conn.execute(
                    mr_sort_criterion.update()
                    .where(mr_sort_criterion.c.mrsort_id.in_(mr_sort_ids))
                    .where(mr_sort_criterion.c.attribute_id == attr_id)
                    .values(attribute_id=attributes_map[attr_id])
                )
                # Update links in weighted_sum_operand table
                model_ids = [
                    _row[0]
                    for _row in conn.execute(
                        sa.select(weighted_sum_operand.c["id"])
                        .join(
                            processing_model,
                            processing_model.c.id
                            == weighted_sum_operand.c.model_id,
                        )
                        .join(
                            new_project_data,
                            new_project_data.c.id
                            == processing_model.c.data_generator_id,
                        )
                        .join(
                            project,
                            project.c.id == new_project_data.c.project_id,
                        )
                        .where(project.c.id == proj_id)
                        .where(weighted_sum_operand.c.attribute_id == attr_id)
                    )
                ]
                conn.execute(
                    weighted_sum_operand.update()
                    .where(weighted_sum_operand.c.id.in_(model_ids))
                    .values(attribute_id=attributes_map[attr_id])
                )

            # Duplicate features as well
            orig_feats = conn.execute(
                sa.select(feature.c["id"], geo_feature.c["geom"])
                .join(geo_feature, geo_feature.c.id == feature.c.id)
                .where(feature.c.data_id == data_id)
            )
            for f_id, geom in orig_feats:
                # Duplicate feature
                new_f_id = conn.execute(
                    feature.insert()
                    .values(data_id=new_data_id, type="geo_feature")
                    .returning(feature.c["id"])
                ).one()[0]
                # Duplicate geometry
                conn.execute(
                    geo_feature.insert().values(id=new_f_id, geom=geom)
                )
                # Duplicate values
                old_values = conn.execute(
                    sa.select(
                        data_value.c["type", "attribute_id", "value"]
                    ).where(data_value.c.feature_id == f_id)
                )
                for type, attr_id, value in old_values:
                    conn.execute(
                        data_value.insert().values(
                            type=type,
                            attribute_id=attributes_map[attr_id],
                            feature_id=new_f_id,
                            value=value,
                        )
                    )

            # We also need to replace data and its nested fields in every
            # ref of the project
            # attributes used in processing models
        else:
            # Replace geo data type with 'generated_geo_data'
            conn.execute(
                base_data.update()
                .where(base_data.c.id == data_id)
                .values(type="generated_geo_data")
            )
            # Remove geo_data permissions
            # (generated geo data don't have permissions)
            conn.execute(
                geo_data_permission.delete().where(
                    geo_data_permission.c.object_id == data_id
                )
            )
            # Remove geo_data entry (generated_geo_data are not in this table!)
            conn.execute(
                old_geo_data.delete().where(old_geo_data.c.id == data_id)
            )
            geo_data_modified.append(data_id)
        if not is_public:
            # Make sure project manager can access stream
            # Handle when project manager can access version but not stream
            new_stream_perms.append((stream_id, manager_id))
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    # Make sure project manager can access streams in their project
    _new_stream_perms = set(new_stream_perms)
    res = conn.execute(sa.select(stream_permission.c["object_id", "user_id"]))
    _new_stream_perms -= {(r[0], r[1]) for r in res.all()}
    new_stream_perms = sorted(
        set(_new_stream_perms), key=new_stream_perms.index
    )
    for stream_id, user_id in new_stream_perms:
        conn.execute(
            stream_permission.insert().values(
                object_id=stream_id, user_id=user_id
            )
        )

    with op.batch_alter_table("geo_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_geo_data_stream_id_stream_geo_data", type_="foreignkey"
        )
        batch_op.drop_column("stream_id")


def downgrade():
    # Remove update_stream tasks
    op.execute(sa.text("DELETE FROM project_task WHERE type = update_stream"))

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

    with op.batch_alter_table("geo_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "stream_id", sa.INTEGER(), autoincrement=False, nullable=True
            )
        )
        batch_op.create_foreign_key(
            "fk_geo_data_stream_id_stream_geo_data",
            "stream_geo_data",
            ["stream_id"],
            ["id"],
        )

    conn = op.get_bind()
    nb_migration_ops = conn.execute(
        sa.text(
            "SELECT count(id) FROM project_data "
            "WHERE data_type = 'data_stream'"
        )
    ).fetchone()[0]
    op_it = 0
    progress_bar(op_it, nb_migration_ops)

    # Replace all DataStream by DataGeo with GeoData ref
    res = conn.execute(
        sa.select(
            new_project_data.c["id", "stream_id", "data_id"],
            project.c["manager_id"],
            stream_geo_data.c["upload_user_id", "name", "type"],
        )
        .join(project, project.c.id == new_project_data.c.project_id)
        .join(
            stream_geo_data,
            stream_geo_data.c.id == new_project_data.c.stream_id,
        )
        .where(new_project_data.c.data_type == "data_stream")  # noqa: E711
    )
    for (
        p_data_id,
        stream_id,
        data_id,
        manager_id,
        upload_user_id,
        name,
        s_type,
    ) in res:
        # Replace DataStream instance with DataGeo (in place to keep refs)
        conn.execute(
            new_project_data.update()
            .where(new_project_data.c.id == p_data_id)
            .values(data_type="geo_data")
        )
        # Replace geo data type with 'geo_data' and add stream ref
        conn.execute(
            base_data.update()
            .where(base_data.c.id == data_id)
            .values(type="geo_data")
        )
        conn.execute(
            old_geo_data.insert().values(
                id=data_id,
                stream_id=stream_id,
                upload_user_id=upload_user_id,
                original_name=name,
                source_driver=s_type,
                is_public=False,
            )
        )
        # Add access to geo data to stream upload user and DataStream manager
        conn.execute(
            geo_data_permission.insert().values(
                object_id=data_id, user_id=manager_id
            )
        )
        conn.execute(
            geo_data_permission.insert().values(
                object_id=data_id, user_id=upload_user_id
            )
        )
        op_it += 1
        progress_bar(op_it, nb_migration_ops)

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_project_data_stream_id_stream_geo_data"),
            type_="foreignkey",
        )
        batch_op.drop_column("resolution")
        batch_op.drop_column("stop")
        batch_op.drop_column("step")
        batch_op.drop_column("start")
        batch_op.drop_column("classes")
        batch_op.drop_column("stream_id")

    # Replace new data type with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_data ALTER COLUMN data_type TYPE _datatype"
        " USING data_type::text::_datatype"
    )
    new_data_type.drop(op.get_bind(), checkfirst=False)
    old_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE project_data ALTER COLUMN data_type TYPE datatype"
        " USING data_type::text::datatype"
    )
    tmp_data_type.drop(op.get_bind(), checkfirst=False)
