-- To avoid potential schema drift issues
SET search_path TO "fertiscan_0.0.15";

-- Trigger function to handle after organization_information delete for location deletion
CREATE OR REPLACE FUNCTION "fertiscan_0.0.15".after_org_info_delete_location_trig()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.location_id IS NOT NULL THEN
        BEGIN
            DELETE FROM "fertiscan_0.0.15".location
            WHERE id = OLD.location_id;
        EXCEPTION WHEN foreign_key_violation THEN
            RAISE NOTICE 'Location % is still referenced by another record and cannot be deleted.', OLD.location_id;
        END;
    END IF;

    RETURN NULL;
END;
$$;

-- Trigger definition on organization_information table for location deletion
DROP TRIGGER IF EXISTS after_organization_information_delete_location ON "fertiscan_0.0.15".organization_information;
CREATE TRIGGER after_organization_information_delete_location
AFTER DELETE ON "fertiscan_0.0.15".organization_information
FOR EACH ROW
EXECUTE FUNCTION "fertiscan_0.0.15".after_org_info_delete_location_trig();

-- Function to delete an inspection and related data
CREATE OR REPLACE FUNCTION "fertiscan_0.0.15".delete_inspection(
    p_inspection_id uuid,
    p_inspector_id uuid
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    inspection_record jsonb;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM "fertiscan_0.0.15".inspection 
        WHERE id = p_inspection_id 
        AND inspector_id = p_inspector_id
    ) THEN
        RAISE EXCEPTION 'Inspector % is not the creator of inspection %', p_inspector_id, p_inspection_id;
    END IF;

    -- Delete the inspection record and retrieve it
    WITH deleted_inspection AS (
        DELETE FROM "fertiscan_0.0.15".inspection
        WHERE id = p_inspection_id
        RETURNING *
    )
    SELECT row_to_json(deleted_inspection) 
    INTO inspection_record
    FROM deleted_inspection;

    -- Return the deleted inspection record
    RETURN inspection_record;
END;
$$;

-- Combined trigger function to handle after inspection delete for sample and label_information deletion
CREATE OR REPLACE FUNCTION "fertiscan_0.0.15".after_insp_delete_cleanup_trig()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF OLD.sample_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.15".sample
        WHERE id = OLD.sample_id;
    END IF;

    IF OLD.label_info_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.15".label_information
        WHERE id = OLD.label_info_id;
    END IF;

    RETURN NULL;
END;
$$;

-- Trigger definition on inspection table for combined cleanup (sample and label_information deletion)
DROP TRIGGER IF EXISTS after_inspection_delete_cleanup ON "fertiscan_0.0.15".inspection;
CREATE TRIGGER after_inspection_delete_cleanup
AFTER DELETE ON "fertiscan_0.0.15".inspection
FOR EACH ROW
EXECUTE FUNCTION "fertiscan_0.0.15".after_insp_delete_cleanup_trig();

-- Trigger function to handle after label_information delete for organization_information deletion
CREATE OR REPLACE FUNCTION "fertiscan_0.0.15".after_label_info_delete_org_info_trig()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    BEGIN
        DELETE FROM "fertiscan_0.0.15".organization_information
        WHERE id = OLD.company_info_id;
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'Company organization_information with ID % could not be deleted due to foreign key constraints.', OLD.company_info_id;
    END;

    BEGIN
        DELETE FROM "fertiscan_0.0.15".organization_information
        WHERE id = OLD.manufacturer_info_id;
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'Manufacturer organization_information with ID % could not be deleted due to foreign key constraints.', OLD.manufacturer_info_id;
    END;

    RETURN NULL;
END;
$$;

-- Trigger definition on label_information table for organization_information deletion
DROP TRIGGER IF EXISTS after_label_information_delete_organization_information ON "fertiscan_0.0.15".label_information;
CREATE TRIGGER after_label_information_delete_organization_information
AFTER DELETE ON "fertiscan_0.0.15".label_information
FOR EACH ROW
EXECUTE FUNCTION "fertiscan_0.0.15".after_label_info_delete_org_info_trig();
