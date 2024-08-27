CREATE OR REPLACE FUNCTION "fertiscan_0.0.13".delete_organization_information(
    p_organization_information_id uuid
)
RETURNS void
LANGUAGE plpgsql
AS $$
DECLARE
    v_location_id uuid;
BEGIN
    -- Retrieve the associated location ID before deleting the organization
    SELECT location_id INTO v_location_id
    FROM "fertiscan_0.0.13".organization_information
    WHERE id = p_organization_information_id;

    -- Delete the organization information without handling exceptions
    DELETE FROM "fertiscan_0.0.13".organization_information
    WHERE id = p_organization_information_id;

    -- If the organization information was successfully deleted, delete the associated location
    IF v_location_id IS NOT NULL THEN
        BEGIN
            DELETE FROM "fertiscan_0.0.13".location
            WHERE id = v_location_id;
            RAISE NOTICE 'Location with ID % deleted successfully.', v_location_id;
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'Location with ID % could not be deleted due to associated records.', v_location_id;
        END;
    END IF;
END;
$$;


CREATE OR REPLACE FUNCTION "fertiscan_0.0.13".delete_inspection(
    p_inspection_id uuid,
    p_inspector_id uuid
)
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
    v_inspection_data jsonb;
    v_label_id uuid;
    v_sample_id uuid;
    v_company_id uuid;
    v_manufacturer_id uuid;
BEGIN
    -- Check if the inspector is the creator of the inspection
    IF NOT EXISTS (
        SELECT 1 
        FROM "fertiscan_0.0.13".inspection 
        WHERE id = p_inspection_id 
        AND inspector_id = p_inspector_id
    ) THEN
        RAISE EXCEPTION 'Inspector is not the creator of this inspection';
    END IF;

    -- Get the entire inspection data and extract relevant IDs
    SELECT 
        jsonb_build_object(
            'id', i.id,
            'label_info_id', i.label_info_id,
            'sample_id', i.sample_id,
            'picture_set_id', i.picture_set_id,
            'inspector_id', i.inspector_id,
            'verified', i.verified,
            'upload_date', i.upload_date,
            'updated_at', i.updated_at
        ),
        i.label_info_id,
        i.sample_id,
        li.company_info_id,
        li.manufacturer_info_id
    INTO 
        v_inspection_data,
        v_label_id,
        v_sample_id,
        v_company_id,
        v_manufacturer_id
    FROM 
        "fertiscan_0.0.13".inspection i
    JOIN 
        "fertiscan_0.0.13".label_information li 
    ON 
        i.label_info_id = li.id
    WHERE 
        i.id = p_inspection_id;
    
    -- Delete the label information (cascade deletes associated records)
    IF v_label_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.13".label_information
        WHERE id = v_label_id;
    ELSE
        RAISE EXCEPTION 'Label information not found for this inspection';
    END IF;

    -- Delete the sample if it exists
    IF v_sample_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.13".sample
        WHERE id = v_sample_id;
    END IF;

    -- Attempt to delete the company organization information
    BEGIN
        PERFORM "fertiscan_0.0.13".delete_organization_information(v_company_id);
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'Company organization information with ID % could not be deleted due to foreign key constraints.', v_company_id;
    END;

    -- Attempt to delete the manufacturer organization information
    BEGIN
        PERFORM "fertiscan_0.0.13".delete_organization_information(v_manufacturer_id);
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'Manufacturer organization information with ID % could not be deleted due to foreign key constraints.', v_manufacturer_id;
    END;

    -- Return the inspection data as JSON
    RETURN v_inspection_data;

END;
$$;
