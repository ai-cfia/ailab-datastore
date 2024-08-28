
CREATE OR REPLACE FUNCTION olap_sub_label_creation()
RETURNS TRIGGER AS $$
DECLARE
    type_str TEXT;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        IF (NEW.id IS NOT NULL) AND (NEW.label_id IS NOT NULL) AND (NEW.sub_type_id IS NOT NULL) THEN
        -- FIND THE SUB_TYPE TO GET THE COLUMN IDENTIFIER
        SELECT sub_type.type_en INTO type_str FROM "fertiscan_0.0.12".sub_type WHERE sub_type.id = NEW.sub_type_id;
        
        EXECUTE format('UPDATE "fertiscan_0.0.12".label_dimension 
					SET %I = array_append(%I, %L) 
					WHERE label_id = %L;',
					type_str, type_str, NEW.id, NEW.label_id);
			
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sub_label_creation
AFTER INSERT ON "fertiscan_0.0.12".sub_label
FOR EACH ROW
EXECUTE FUNCTION olap_sub_label_creation();

CREATE OR REPLACE FUNCTION olap_sub_label_deletion()
RETURNS TRIGGER AS $$
DECLARE
    type_str TEXT;
BEGIN
    IF (TG_OP = 'DELETE') THEN
        IF (OLD.id IS NOT NULL) AND (OLD.label_id IS NOT NULL) AND (OLD.sub_type_id IS NOT NULL) THEN
        -- FIND THE SUB_TYPE TO GET THE COLUMN IDENTIFIER
        SELECT sub_type.type_en INTO type_str FROM "fertiscan_0.0.12".sub_type WHERE sub_type.id = OLD.sub_type_id;
        type_str = type_str || '_ids';
        EXECUTE format('UPDATE "fertiscan_0.0.12".label_dimension 
                    SET %I = array_remove(%I, %L) 
                    WHERE label_id = %L;',
                    type_str, type_str, OLD.id, OLD.label_id);
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this sub_label is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sub_label_deletion
AFTER DELETE ON "fertiscan_0.0.12".sub_label
FOR EACH ROW
EXECUTE FUNCTION olap_sub_label_deletion();
