/**
 * Trigger to correct the invalid geometries before an INSERT or an UPDATE.
 */
CREATE OR REPLACE FUNCTION feature_make_valid() RETURNS trigger AS $feature_make_valid$
BEGIN
    IF ST_IsValid(NEW.geom) = 'f' THEN
        NEW.geom := ST_MakeValid(NEW.geom);
    END IF;
    RETURN NEW;
END;
$feature_make_valid$ LANGUAGE plpgsql;

CREATE TRIGGER feature_make_valid BEFORE INSERT OR UPDATE ON geo_feature
    FOR EACH ROW EXECUTE PROCEDURE feature_make_valid();
