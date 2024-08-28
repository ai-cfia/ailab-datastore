
CREATE OR REPLACE FUNCTION olap_guaranteed_creation()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        IF (NEW.id IS NOT NULL) AND (NEW.label_id IS NOT NULL) THEN
        -- Update the label_dimension table with the new guaranteed_analysis_id
		UPDATE "fertiscan_0.0.12"."label_dimension" 
		SET guaranteed_ids = array_append(guaranteed_ids, NEW.id)
		WHERE label_dimension.label_id = label_info_id;
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this guaranteed is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER guaranteed_creation
AFTER INSERT ON "fertiscan_0.0.12".guaranteed
FOR EACH ROW
EXECUTE FUNCTION olap_guaranteed_creation();

CREATE OR REPLACE FUNCTION olap_guaranteed_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        IF (OLD.id IS NOT NULL) AND (OLD.label_id IS NOT NULL) THEN
        -- Update the label_dimension table with the new guaranteed_analysis_id
        UPDATE "fertiscan_0.0.12"."label_dimension" 
        SET label_dimension.guaranteed_ids = array_remove(label_dimension.guaranteed_ids, OLD.id)
        WHERE label_dimension.label_id = label_info_id;
        ELSE
            -- Raise a warning if the condition is not met
            RAISE WARNING 'The OLAP dimension of this guaranteed is not updated because the condition is not met';
        END IF;
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER guaranteed_deletion
AFTER DELETE ON "fertiscan_0.0.12".guaranteed
FOR EACH ROW
EXECUTE FUNCTION olap_guaranteed_deletion();
