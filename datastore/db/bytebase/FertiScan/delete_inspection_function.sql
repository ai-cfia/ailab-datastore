CREATE OR REPLACE FUNCTION "fertiscan_0.0.12".delete_organization_information(
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
    FROM "fertiscan_0.0.12".organization_information
    WHERE id = p_organization_information_id;

    -- Attempt to delete the organization information
    IF p_organization_information_id IS NOT NULL THEN
        BEGIN
            DELETE FROM "fertiscan_0.0.12".organization_information
            WHERE id = p_organization_information_id;
            RAISE NOTICE 'Organization information with ID % deleted successfully.', p_organization_information_id;
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'Organization information with ID % could not be deleted due to associated records.', p_organization_information_id;
        END;
    END IF;

    -- If the organization information was successfully deleted, delete the associated location
    IF v_location_id IS NOT NULL THEN
        BEGIN
            DELETE FROM "fertiscan_0.0.12".location
            WHERE id = v_location_id;
            RAISE NOTICE 'Location with ID % deleted successfully.', v_location_id;
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'Location with ID % could not be deleted due to associated records.', v_location_id;
        END;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION "fertiscan_0.0.12".delete_inspection(
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
        FROM "fertiscan_0.0.12".inspection 
        WHERE id = p_inspection_id 
        AND inspector_id = p_inspector_id
    ) THEN
        RAISE EXCEPTION 'Inspector is not the creator of this inspection';
    END IF;

    -- Get the entire inspection data and extract relevant IDs
    SELECT jsonb_build_object(
        'id', id,
        'label_info_id', label_info_id,
        'sample_id', sample_id,
        'picture_set_id', picture_set_id,
        'inspector_id', inspector_id,
        'verified', verified,
        'upload_date', upload_date,
        'updated_at', updated_at
    ) INTO v_inspection_data,
    label_info_id INTO v_label_id,
    sample_id INTO v_sample_id,
    company_info_id INTO v_company_id,
    manufacturer_info_id INTO v_manufacturer_id
    FROM "fertiscan_0.0.12".inspection
    JOIN "fertiscan_0.0.12".label_information ON label_info_id = "fertiscan_0.0.12".label_information.id
    WHERE "fertiscan_0.0.12".inspection.id = p_inspection_id;

    -- Delete the label information (cascade deletes associated records)
    IF v_label_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.12".label_information
        WHERE id = v_label_id;
    ELSE
        RAISE EXCEPTION 'Label information not found for this inspection';
    END IF;

    -- Delete the sample if it exists
    IF v_sample_id IS NOT NULL THEN
        DELETE FROM "fertiscan_0.0.12".sample
        WHERE id = v_sample_id;
    END IF;

    -- Attempt to delete the company organization information
    PERFORM "fertiscan_0.0.12".delete_organization_information(v_company_id);

    -- Attempt to delete the manufacturer organization information
    PERFORM "fertiscan_0.0.12".delete_organization_information(v_manufacturer_id);

    -- Return the inspection data as JSON
    RETURN v_inspection_data;

END;
$$;
