"""Make streams base data

Revision ID: bb99ff70c7bf
Revises: 163a9f52cac3
Create Date: 2025-06-25 17:03:17.087567

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "bb99ff70c7bf"
down_revision = "163a9f52cac3"
branch_labels = None
depends_on = None


old_data_type = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "global_data",
    name="geodatatype",
)
new_data_type = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "global_data",
    "wfs",
    "wms",
    name="geodatatype",
)
tmp_data_type = sa.Enum(
    "geo_data",
    "generated_geo_data",
    "global_data",
    "wfs",
    "wms",
    name="_geodatatype",
)
stream_type = sa.Enum(
    "wfs",
    "wms",
    name="streamdatatype",
)


def upgrade():
    # Replace old data type with new one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE _geodatatype"
        " USING type::text::_geodatatype"
    )
    old_data_type.drop(op.get_bind(), checkfirst=False)
    new_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE geodatatype"
        " USING type::text::geodatatype"
    )
    tmp_data_type.drop(op.get_bind(), checkfirst=False)

    op.create_table(
        "base_data_permission",
        sa.Column("object_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["base_data.id"],
            name=op.f("fk_base_data_permission_object_id_base_data"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk_base_data_permission_user_id_user"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_base_data_permission")),
    )
    with op.batch_alter_table("base_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("original_name", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("description", sa.String(), nullable=True)
        )
        # Make it non-nullable afterwards (necessary to create column)
        batch_op.add_column(
            sa.Column("is_public", sa.Boolean(), nullable=True)
        )

    # Move stored streams in temporary tables
    op.execute(
        sa.text(
            """
CREATE TEMPORARY TABLE temp_wfs_objects AS
SELECT s.id, s.name, s.title, s.original_name, s.url,
s.upload_user_id, s.description, s.keywords, s.created_at,
s.modified_at, s.is_public, w.feature_type, w.version,
0 as new_id
FROM stream_geo_data s JOIN wfs_geo_data w ON s.id = w.id
"""
        )
    )
    op.execute(
        sa.text(
            "CREATE TEMPORARY TABLE temp_wms_objects AS "
            "SELECT s.id, s.name, s.title, s.original_name, s.url, "
            "s.upload_user_id, s.description, s.keywords, s.created_at, "
            "s.modified_at, s.is_public, w.layer, w.version, w.classes, "
            "w.start, w.step, w.stop, w.resolution, 0 as new_id "
            "FROM stream_geo_data s JOIN wms_geo_data w ON s.id = w.id"
        )
    )

    # Clear stream tables
    op.execute(sa.text("DELETE FROM wfs_geo_data"))
    op.execute(sa.text("DELETE FROM wms_geo_data"))

    with op.batch_alter_table("wfs_geo_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("upload_user_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("url", sa.String(), nullable=False))
        batch_op.add_column(
            sa.Column(
                "keywords",
                postgresql.ARRAY(sa.String(), dimensions=1),
                nullable=True,
            )
        )
        batch_op.drop_constraint(
            "fk_wfs_geo_data_id_stream_geo_data", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_wfs_geo_data_upload_user_id_user"),
            "user",
            ["upload_user_id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_wfs_geo_data_id_base_data"),
            "base_data",
            ["id"],
            ["id"],
        )

    with op.batch_alter_table("wms_geo_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("upload_user_id", sa.Integer(), nullable=True)
        )
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("url", sa.String(), nullable=False))
        batch_op.add_column(
            sa.Column(
                "keywords",
                postgresql.ARRAY(sa.String(), dimensions=1),
                nullable=True,
            )
        )
        batch_op.drop_constraint(
            "fk_wms_geo_data_id_stream_geo_data", type_="foreignkey"
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_wms_geo_data_id_base_data"),
            "base_data",
            ["id"],
            ["id"],
        )
        batch_op.create_foreign_key(
            batch_op.f("fk_wms_geo_data_upload_user_id_user"),
            "user",
            ["upload_user_id"],
            ["id"],
        )

    # Insert WFS streams into base_data and store id in temp_wfs_objects.new_id
    op.execute(
        sa.text(
            """
WITH numbered_source AS (
    SELECT
        id AS temp_id,
        name,
        original_name,
        description,
        created_at,
        modified_at,
        is_public,
        ROW_NUMBER() OVER () AS rn
    FROM temp_wfs_objects
),
inserted AS (
    INSERT INTO base_data (
        type, name, original_name, description, created_at, modified_at, is_public
    )
    SELECT
        'wfs', name, original_name, description, created_at, modified_at, is_public
    FROM numbered_source
    RETURNING id
),
numbered_inserted AS (
    SELECT
        id AS new_id,
        ROW_NUMBER() OVER () AS rn
    FROM inserted
)
UPDATE temp_wfs_objects t
SET new_id = ni.new_id
FROM numbered_source s
JOIN numbered_inserted ni ON s.rn = ni.rn
WHERE t.id = s.temp_id;
"""  # noqa: E501
        )
    )
    # Insert WFS stream parts in wfs_geo_data
    op.execute(
        sa.text(
            """
INSERT INTO wfs_geo_data (id, title, url, keywords, version, feature_type)
SELECT new_id, title, url, keywords, version, feature_type FROM temp_wfs_objects
"""  # noqa: E501
        )
    )

    # Insert WMS streams into base_data and store id in temp_wms_objects.new_id
    op.execute(
        sa.text(
            """
WITH numbered_source AS (
    SELECT
        id AS temp_id,
        name,
        original_name,
        description,
        created_at,
        modified_at,
        is_public,
        ROW_NUMBER() OVER () AS rn
    FROM temp_wms_objects
),
inserted AS (
    INSERT INTO base_data (
        type, name, original_name, description, created_at, modified_at, is_public
    )
    SELECT
        'wfs', name, original_name, description, created_at, modified_at, is_public
    FROM numbered_source
    RETURNING id
),
numbered_inserted AS (
    SELECT
        id AS new_id,
        ROW_NUMBER() OVER () AS rn
    FROM inserted
)
UPDATE temp_wms_objects t
SET new_id = ni.new_id
FROM numbered_source s
JOIN numbered_inserted ni ON s.rn = ni.rn
WHERE t.id = s.temp_id;
"""  # noqa: E501
        )
    )
    # Insert WMS stream parts in wms_geo_data
    op.execute(
        sa.text(
            """
INSERT INTO wms_geo_data (id, title, url, keywords, version, classes,
start, step, stop, layer, resolution)
SELECT new_id, title, url, keywords, version, classes,
start, step, stop, layer, resolution
FROM temp_wms_objects
"""
        )
    )

    # Move migrated geo_data fields values to base_data
    op.execute(
        sa.text(
            """
UPDATE base_data
SET
    description = other_table.description,
    original_name = other_table.original_name,
    is_public = other_table.is_public
FROM (
    SELECT id, description, original_name, is_public
    FROM geo_data
) AS other_table
WHERE other_table.id = base_data.id
"""
        )
    )
    # Move migrated global_data fields values to base_data
    op.execute(
        sa.text(
            """
UPDATE base_data
SET
    description = other_table.description,
    is_public = other_table.is_public
FROM (
    SELECT id, description, is_public
    FROM global_data
) AS other_table
WHERE other_table.id = base_data.id
"""
        )
    )
    # Set is_public to false for generated_geo_data
    op.execute(
        sa.text(
            """
UPDATE base_data
SET
    is_public = false
WHERE base_data.type = 'generated_geo_data'
"""
        )
    )
    op.alter_column("base_data", "is_public", nullable=False)
    with op.batch_alter_table("geo_data", schema=None) as batch_op:
        batch_op.drop_column("description")
        batch_op.drop_column("is_public")
        batch_op.drop_column("original_name")

    with op.batch_alter_table("global_data", schema=None) as batch_op:
        batch_op.drop_column("description")
        batch_op.drop_column("is_public")

    # Add WFS stream permissions
    op.execute(
        sa.text(
            """
INSERT INTO base_data_permission (object_id, user_id)
SELECT w.new_id, p.user_id FROM stream_geo_data_permission p
JOIN temp_wfs_objects w ON p.object_id = w.id
"""
        )
    )
    # Add WMS stream permissions
    op.execute(
        sa.text(
            """
INSERT INTO base_data_permission (object_id, user_id)
SELECT w.new_id, p.user_id FROM stream_geo_data_permission p
JOIN temp_wms_objects w ON p.object_id = w.id
"""
        )
    )
    # Add geo data permissions
    op.execute(
        sa.text(
            """
INSERT INTO base_data_permission (object_id, user_id)
SELECT object_id, user_id FROM geo_data_permission
"""
        )
    )
    # Add global data permissions
    op.execute(
        sa.text(
            """
INSERT INTO base_data_permission (object_id, user_id)
SELECT object_id, user_id FROM global_data_permission
"""
        )
    )
    op.drop_table("stream_geo_data_permission")
    op.drop_table("geo_data_permission")
    op.drop_table("global_data_permission")

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_project_data_stream_id_stream_geo_data", type_="foreignkey"
        )
    # Modify data stream in project data to reference base data (stream ids)
    op.execute(
        sa.text(
            """
UPDATE project_data
SET
    stream_id = other.new_id
FROM (
    SELECT 'wfs' AS type, id, new_id FROM temp_wfs_objects UNION
    SELECT 'wms' AS type, id, new_id FROM temp_wms_objects
) AS other
WHERE project_data.stream_id = other.id
"""
        )
    )
    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_project_data_stream_id_base_data"),
            "base_data",
            ["stream_id"],
            ["id"],
        )

    op.drop_table("stream_geo_data")
    stream_type.drop(op.get_bind(), checkfirst=False)


def downgrade():
    op.create_table(
        "stream_geo_data",
        sa.Column(
            "type",
            postgresql.ENUM("wfs", "wms", name="streamdatatype"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "original_name", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column("url", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "upload_user_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "description", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "keywords",
            postgresql.ARRAY(sa.VARCHAR()),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "is_public", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "modified_at",
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('stream_geo_data_id_seq'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["upload_user_id"],
            ["user.id"],
            name="fk_stream_geo_data_upload_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_stream_geo_data"),
        postgresql_ignore_search_path=False,
    )

    # Move stored streams in temporary tables
    op.execute(
        sa.text(
            "CREATE TEMPORARY TABLE temp_wfs_objects AS "
            "SELECT d.id, d.name, w.title, d.original_name, w.url, "
            "w.upload_user_id, d.description, w.keywords, d.created_at, "
            "d.modified_at, d.is_public, w.feature_type, w.version, "
            "0 as new_id "
            "FROM base_data d JOIN wfs_geo_data w ON d.id = w.id "
        )
    )
    op.execute(
        sa.text(
            "CREATE TEMPORARY TABLE temp_wms_objects AS "
            "SELECT d.id, d.name, w.title, d.original_name, w.url, "
            "w.upload_user_id, d.description, w.keywords, d.created_at, "
            "d.modified_at, d.is_public, w.layer, w.version, w.classes, "
            "w.start, w.step, w.stop, w.resolution, 0 as new_id "
            "FROM base_data d JOIN wms_geo_data w ON d.id = w.id"
        )
    )

    # Clear stream tables
    op.execute(sa.text("DELETE FROM wfs_geo_data"))
    op.execute(sa.text("DELETE FROM wms_geo_data"))

    with op.batch_alter_table("wms_geo_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_wms_geo_data_upload_user_id_user"),
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            batch_op.f("fk_wms_geo_data_id_base_data"), type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_wms_geo_data_id_stream_geo_data",
            "stream_geo_data",
            ["id"],
            ["id"],
        )
        batch_op.drop_column("keywords")
        batch_op.drop_column("url")
        batch_op.drop_column("title")
        batch_op.drop_column("upload_user_id")

    with op.batch_alter_table("wfs_geo_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_wfs_geo_data_id_base_data"), type_="foreignkey"
        )
        batch_op.drop_constraint(
            batch_op.f("fk_wfs_geo_data_upload_user_id_user"),
            type_="foreignkey",
        )
        batch_op.create_foreign_key(
            "fk_wfs_geo_data_id_stream_geo_data",
            "stream_geo_data",
            ["id"],
            ["id"],
        )
        batch_op.drop_column("keywords")
        batch_op.drop_column("url")
        batch_op.drop_column("title")
        batch_op.drop_column("upload_user_id")

    # Insert WFS streams into base_data and store id in temp_wfs_objects.new_id
    op.execute(
        sa.text(
            """
WITH numbered_source AS (
    SELECT
        id AS temp_id,
        name,
        title,
        original_name,
        description,
        created_at,
        modified_at,
        is_public,
        url,
        upload_user_id,
        keywords,
        ROW_NUMBER() OVER () AS rn
    FROM temp_wfs_objects
),
inserted AS (
    INSERT INTO stream_geo_data (
        type, name, title, original_name, description, created_at, modified_at,
        is_public, url, upload_user_id, keywords
    )
    SELECT
        'wfs', name, title, original_name, description, created_at, modified_at,
        is_public, url, upload_user_id, keywords
    FROM numbered_source
    RETURNING id
),
numbered_inserted AS (
    SELECT
        id AS new_id,
        ROW_NUMBER() OVER () AS rn
    FROM inserted
)
UPDATE temp_wfs_objects t
SET new_id = ni.new_id
FROM numbered_source s
JOIN numbered_inserted ni ON s.rn = ni.rn
WHERE t.id = s.temp_id;
"""  # noqa: E501
        )
    )
    # Insert WFS stream parts in wfs_geo_data
    op.execute(
        sa.text(
            """
INSERT INTO wfs_geo_data (id, feature_type, version)
SELECT new_id, feature_type, version FROM temp_wfs_objects
"""  # noqa: E501
        )
    )

    # Insert WMS streams into base_data and store id in temp_wfs_objects.new_id
    op.execute(
        sa.text(
            """
WITH numbered_source AS (
    SELECT
        id AS temp_id,
        name,
        title,
        original_name,
        description,
        created_at,
        modified_at,
        is_public,
        url,
        upload_user_id,
        keywords,
        ROW_NUMBER() OVER () AS rn
    FROM temp_wms_objects
),
inserted AS (
    INSERT INTO stream_geo_data (
        type, name, title, original_name, description, created_at, modified_at,
        is_public, url, upload_user_id, keywords
    )
    SELECT
        'wfs', name, title, original_name, description, created_at, modified_at,
        is_public, url, upload_user_id, keywords
    FROM numbered_source
    RETURNING id
),
numbered_inserted AS (
    SELECT
        id AS new_id,
        ROW_NUMBER() OVER () AS rn
    FROM inserted
)
UPDATE temp_wms_objects t
SET new_id = ni.new_id
FROM numbered_source s
JOIN numbered_inserted ni ON s.rn = ni.rn
WHERE t.id = s.temp_id;
"""  # noqa: E501
        )
    )
    # Insert WMS stream parts in wms_geo_data
    op.execute(
        sa.text(
            """
INSERT INTO wms_geo_data (id, version, classes,
start, step, stop, layer, resolution)
SELECT new_id, version, classes,
start, step, stop, layer, resolution
FROM temp_wms_objects
"""
        )
    )

    with op.batch_alter_table("global_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_public", sa.BOOLEAN(), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "description", sa.VARCHAR(), autoincrement=False, nullable=True
            )
        )

    with op.batch_alter_table("geo_data", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "original_name",
                sa.VARCHAR(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.add_column(
            sa.Column(
                "is_public", sa.BOOLEAN(), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "description", sa.VARCHAR(), autoincrement=False, nullable=True
            )
        )

    # Move migrated geo_data fields values back from base_data
    op.execute(
        sa.text(
            """
UPDATE geo_data
SET
    description = other_table.description,
    original_name = other_table.original_name,
    is_public = other_table.is_public
FROM (
    SELECT id, description, original_name, is_public
    FROM base_data
) AS other_table
WHERE other_table.id = geo_data.id
"""
        )
    )
    # Move migrated global_data fields values back from base_data
    op.execute(
        sa.text(
            """
UPDATE global_data
SET
    description = other_table.description,
    is_public = other_table.is_public
FROM (
    SELECT id, description, is_public
    FROM base_data
) AS other_table
WHERE other_table.id = global_data.id
"""
        )
    )

    op.alter_column("geo_data", "is_public", nullable=False)
    op.alter_column("global_data", "is_public", nullable=False)
    with op.batch_alter_table("base_data", schema=None) as batch_op:
        batch_op.drop_column("is_public")
        batch_op.drop_column("description")
        batch_op.drop_column("original_name")

    op.create_table(
        "geo_data_permission",
        sa.Column(
            "object_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "user_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["geo_data.id"],
            name="fk_geo_data_permission_object_id_geo_data",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_geo_data_permission_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_geo_data_permission"),
    )
    op.create_table(
        "global_data_permission",
        sa.Column(
            "object_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "user_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["global_data.id"],
            name="fk_global_data_permission_object_id_global_data",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_global_data_permission_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_global_data_permission"),
    )
    op.create_table(
        "stream_geo_data_permission",
        sa.Column(
            "object_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "user_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.ForeignKeyConstraint(
            ["object_id"],
            ["stream_geo_data.id"],
            name="fk_stream_geo_data_permission_object_id_stream_geo_data",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name="fk_stream_geo_data_permission_user_id_user",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_stream_geo_data_permission"),
    )

    # Add WFS stream permissions
    op.execute(
        sa.text(
            """
INSERT INTO stream_geo_data_permission (object_id, user_id)
SELECT w.new_id, p.user_id FROM base_data_permission p
JOIN temp_wfs_objects w ON p.object_id = w.id
"""
        )
    )
    # Add WMS stream permissions
    op.execute(
        sa.text(
            """
INSERT INTO stream_geo_data_permission (object_id, user_id)
SELECT w.new_id, p.user_id FROM base_data_permission p
JOIN temp_wms_objects w ON p.object_id = w.id
"""
        )
    )
    # Add geo data permissions
    op.execute(
        sa.text(
            """
INSERT INTO geo_data_permission (object_id, user_id)
SELECT object_id, user_id FROM base_data_permission
JOIN base_data ON base_data.id = base_data_permission.object_id
WHERE base_data.type = 'geo_data'
"""
        )
    )
    # Add global data permissions
    op.execute(
        sa.text(
            """
INSERT INTO global_data_permission (object_id, user_id)
SELECT object_id, user_id FROM base_data_permission
JOIN base_data ON base_data.id = base_data_permission.object_id
WHERE base_data.type = 'global_data'
"""
        )
    )

    op.drop_table("base_data_permission")

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_project_data_stream_id_base_data"),
            type_="foreignkey",
        )

    # Modify data stream in project data to reference stream geo data
    op.execute(
        sa.text(
            """
UPDATE project_data
SET
    stream_id = other.new_id
FROM (
    SELECT 'wfs' AS type, id, new_id FROM temp_wfs_objects UNION
    SELECT 'wms' AS type, id, new_id FROM temp_wms_objects
) AS other
WHERE project_data.stream_id = other.id
"""
        )
    )

    with op.batch_alter_table("project_data", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_project_data_stream_id_stream_geo_data",
            "stream_geo_data",
            ["stream_id"],
            ["id"],
        )

    # Delete stream from base_data table
    op.execute(sa.text("DELETE FROM base_data WHERE type IN ('wfs', 'wms')"))
    # Replace new data type with old one
    # https://stackoverflow.com/questions/14845203/altering-an-enum-field-using-alembic  # noqa: E501
    tmp_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE _geodatatype"
        " USING type::text::_geodatatype"
    )
    new_data_type.drop(op.get_bind(), checkfirst=False)
    old_data_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE base_data ALTER COLUMN type TYPE geodatatype"
        " USING type::text::geodatatype"
    )
    tmp_data_type.drop(op.get_bind(), checkfirst=False)
