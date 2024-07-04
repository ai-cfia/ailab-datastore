CREATE OR REPLACE FUNCTION verified_inference() RETURNS TRIGGER LANGUAGE plpgsql AS $$
  BEGIN
    IF NEW.verified = true THEN
        INSERT INTO picture_seed (picture_id, seed_id)
          SELECT 
            New.picture_id, 
            so.seed_id  
          FROM object obj 
            LEFT JOIN seed_obj so 
              ON so.id = obj.verified_id  
          WHERE obj.inference_id = NEW.id and obj.verified_id is not null;
    END IF;
    RETURN NEW;
  END;
$$;

CREATE TRIGGER verified_inference_trigger 
AFTER UPDATE ON inference
FOR EACH ROW 
WHEN (NEW.verified = true)
EXECUTE FUNCTION verified_inference();
