
CREATE OR REPLACE FUNCTION olap_label_information_creation()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        IF (NEW.id IS NOT NULL) THEN
        INSERT INTO "fertiscan_0.0.12"."label_dimension" (
            label_id, company_info_id, manufacturer_info_id
        ) VALUES (
            NEW.id, NEW.company_info_id, NEW.manufacturer_info_id
        );
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this label_information is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS label_information_creation ON "fertiscan_0.0.12".label_information;
CREATE TRIGGER label_information_creation
AFTER INSERT ON "fertiscan_0.0.12".label_information
FOR EACH ROW
EXECUTE FUNCTION olap_label_information_creation();

CREATE OR REPLACE FUNCTION olap_label_information_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        IF (OLD.id IS NOT NULL) THEN
        DELETE FROM "fertiscan_0.0.12"."label_dimension" 
        WHERE label_id = OLD.id;
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this label_information is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS label_information_deletion ON "fertiscan_0.0.12".label_information;
CREATE TRIGGER label_information_deletion
AFTER DELETE ON "fertiscan_0.0.12".label_information
FOR EACH ROW
EXECUTE FUNCTION olap_label_information_deletion();
