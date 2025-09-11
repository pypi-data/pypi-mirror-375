"""Split disjointed geometries.

Revision ID: a212e7950484
Revises: 184b71fa9bdc
Create Date: 2025-03-20 17:13:00.000000

"""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry, WKBElement, shape
from sqlalchemy.dialects import postgresql

from deseasion.backend.services.geo_data_loading_service import (
    split_multi_geometry,
)
from deseasion.backend.services.utils import progress_bar

# revision identifiers, used by Alembic.
revision = "a212e7950484"
down_revision = "184b71fa9bdc"
branch_labels = None
depends_on = None


feature = sa.Table(
    "feature",
    sa.MetaData(),
    sa.Column(
        "type",
        sa.Enum("feature", "geo_feature", name="featuretype"),
        nullable=True,
    ),
    sa.Column("data_id", sa.Integer(), nullable=True),
    sa.Column(
        "explainability",
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
    ),
    sa.Column("id", sa.Integer(), nullable=False),
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


feature_input_assoc = sa.Table(
    "feature_input_association",
    sa.MetaData(),
    sa.Column(
        "feature_id",
        sa.Integer,
    ),
    sa.Column(
        "input_feature_id",
        sa.Integer,
    ),
)


def upgrade():
    conn = op.get_bind()
    # Get all geo features with non-polygon geometry
    nb = conn.execute(
        sa.text(
            "SELECT count(id) FROM geo_feature "
            "WHERE ST_GeometryType(geom) != 'ST_Polygon'"
        )
    ).fetchone()[0]
    res = conn.execute(
        sa.text(
            "SELECT f.id, g.geom, f.data_id, f.explainability "
            "FROM geo_feature AS g JOIN feature AS f ON f.id = g.id "
            "WHERE ST_GeometryType(g.geom) != 'ST_Polygon'"
        )
    )
    i = 0
    progress_bar(i, nb)
    for id, geom, data_id, explain in res:
        # Split disjoint geometry
        geoms = split_multi_geometry(shape.to_shape(WKBElement(geom)))
        # Update old geometry with first single part
        geom1 = next(geoms)
        conn.execute(
            geo_feature.update()
            .values(geom=shape.from_shape(geom1, srid=4326))
            .where(geo_feature.c.id == id)
        )
        # Insert a new geo feature for each other simple geometry
        for simple_geom in geoms:
            new_id = conn.execute(
                feature.insert()
                .values(
                    data_id=data_id, explainability=explain, type="geo_feature"
                )
                .returning(feature.c.id)
            ).first()[0]
            conn.execute(
                geo_feature.insert().values(
                    id=new_id, geom=shape.from_shape(simple_geom, srid=4326)
                )
            )
            # Duplicate each data value for new feature
            sel = sa.select(
                data_value.c["type", "attribute_id", "value"],
                sa.bindparam("feature_id", new_id),
            ).where(data_value.c.feature_id == id)
            conn.execute(
                data_value.insert().from_select(
                    ["type", "attribute_id", "value", "feature_id"], sel
                )
            )
            # Add input features of old feature
            sel = sa.select(
                feature_input_assoc.c["input_feature_id"],
                sa.bindparam("feature_id", new_id),
            ).where(feature_input_assoc.c.feature_id == id)
            conn.execute(
                feature_input_assoc.insert().from_select(
                    ["input_feature_id", "feature_id"], sel
                )
            )
            # Add new feature as input of features having old feature as input
            # Old feature was union of new features
            sel = sa.select(
                feature_input_assoc.c["feature_id"],
                sa.bindparam("input_feature_id", new_id),
            ).where(feature_input_assoc.c.input_feature_id == id)
            conn.execute(
                feature_input_assoc.insert().from_select(
                    ["feature_id", "input_feature_id"], sel
                )
            )
        i += 1
        progress_bar(i, nb)


def downgrade():
    pass
