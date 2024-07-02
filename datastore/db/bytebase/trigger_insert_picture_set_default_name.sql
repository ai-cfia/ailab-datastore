CREATE OR REPLACE FUNCTION "nachet_0.0.11".picture_set_default_name() 
RETURNS TRIGGER 
LANGUAGE plpgsql 
AS $$
  BEGIN
    IF NEW.name IS NULL THEN
        NEW.name := NEW.id::text;
    END IF;
    RETURN NEW;
  END;
$$;

CREATE TRIGGER picture_set_default_name_trigger 
BEFORE INSERT ON "nachet_0.0.11".picture_set
FOR EACH ROW 
WHEN (NEW.name IS NULL)
EXECUTE FUNCTION "nachet_0.0.11".picture_set_default_name();