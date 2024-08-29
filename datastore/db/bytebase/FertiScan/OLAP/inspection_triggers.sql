
CREATE OR REPLACE FUNCTION olap_inspection_creation()
RETURNS TRIGGER AS $$
DECLARE
    time_id UUID;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        IF (NEW.id IS NOT NULL) AND (NEW.label_info_id IS NOT NULL) THEN
        	-- Time Dimension
            INSERT INTO "fertiscan_0.0.12".time_dimension (
                date_value, year,month,day) 
            VALUES (
                CURRENT_DATE,
                EXTRACT(YEAR FROM CURRENT_DATE),
                EXTRACT(MONTH FROM CURRENT_DATE),
                EXTRACT(DAY FROM CURRENT_DATE)	
            ) RETURNING id INTO time_id;
            -- Create the Inspection_factual entry
            INSERT INTO "fertiscan_0.0.12".inspection_factual (
                inspection_id, inspector_id, label_info_id, time_id, sample_id, company_id, manufacturer_id, picture_set_id
            ) VALUES (
                NEW.id,
                NEW.user_id,
                NEW.label_info_id,
                time_id,
                NULL, -- NOT handled yet
                NULL, -- IS not defined yet
                NULL, -- IS not defined yet
                NEW.picture_set_id
            );
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this inspection is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS inspection_creation ON "fertiscan_0.0.12".inspection;
CREATE TRIGGER inspection_creation
AFTER INSERT ON "fertiscan_0.0.12".inspection
FOR EACH ROW
EXECUTE FUNCTION olap_inspection_creation();

CREATE OR REPLACE FUNCTION olap_inspection_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        IF (OLD.id IS NOT NULL) THEN
        DELETE FROM "fertiscan_0.0.12".inspection_factual 
        WHERE inspection_id = OLD.id;
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this inspection is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS inspection_deletion ON "fertiscan_0.0.12".inspection;
CREATE TRIGGER inspection_deletion
AFTER DELETE ON "fertiscan_0.0.12".inspection
FOR EACH ROW
EXECUTE FUNCTION olap_inspection_deletion();
