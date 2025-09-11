/**
 * Dissolve adjacent geometries if they have the same attributes.
 * 
 * Warning: the function deletes the old features before inserting the new ones.
 */
CREATE OR REPLACE FUNCTION dissolve_adjacent (data_id int) RETURNS void AS $$
BEGIN
    -- Use a temporary table to store the attributes
    CREATE TEMP TABLE temp_dissolve AS
    WITH merge AS (
        SELECT g.geom AS geom, json_object_agg(v.attribute_id, v.value) AS props
        FROM feature f INNER JOIN geo_feature g ON f.id = g.id
        INNER JOIN data_value v ON f.id = v.feature_id
        WHERE f.data_id = data_id
        GROUP BY f.id
    )
    -- Dissolve the adjacent geometries based on their attributes
    SELECT ST_SetSRID(ST_UnaryUnion(d.geom), 4326) AS geom, d.props AS props
    FROM (
        SELECT UNNEST(ST_ClusterIntersecting(m.geom)) AS geom, m.props::jsonb AS props
        FROM merge m
        GROUP BY m.props::jsonb
    ) AS d;

    -- Delete old features
    WITH delf AS (
        DELETE FROM feature f WHERE f.data_id = data_id
        RETURNING f.id
    )
    DELETE FROM geo_feature WHERE id IN (SELECT * FROM delf);

    -- Insert the new dissolved features
    WITH ins AS (
        INSERT INTO feature (data_id)
        SELECT geom, data_id
        FROM temp_dissolve
        RETURNING id, geom
    )
    INSERT INTO geo_feature (id, geom)
    SELECT id, geom FROM ins;
    INSERT INTO data_value (attribute_id, value, feature_id, type)
    SELECT d.key, d.value, ins.id, a.type
    FROM ins INNER JOIN (
        SELECT t.geom, j.key::int, j.value
        FROM temp_dissolve t, jsonb_each(t.props) j
    ) AS d ON ins.geom = d.geom
    INNER JOIN data_attribute a ON d.key = a.id;

    -- Delete the temporary table
    DROP TABLE temp_dissolve;
END;
$$ LANGUAGE plpgsql;
