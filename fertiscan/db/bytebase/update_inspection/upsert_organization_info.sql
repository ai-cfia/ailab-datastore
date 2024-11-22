
-- Function to upsert organization information
DROP FUNCTION IF EXISTS "fertiscan_0.0.18".upsert_organization_info(jsonb, uuid);
CREATE OR REPLACE FUNCTION "fertiscan_0.0.18".upsert_organization_info(input_org_info jsonb, label_info_id uuid)
RETURNS void AS $$
DECLARE
    record jsonb;
    address_str TEXT;
    location_id uuid;
BEGIN

    -- loop each orgs in the input_org_info
    for record in SELECT * FROM jsonb_array_elements(input_org_info)
    loop
        if record->>'id' IS NULL THEN
            PERFORM new_organization_info_located(
                record->>'name',
                record->>'address',
                record->>'website',
                record->>'phone_number',
                TRUE,
                label_info_id,
                (record->>'is_main_contact')::boolean
            );
        else
        -- UPDATE THE ORGANIZATION INFORMATION
            UPDATE organization_information SET
                "name" = record->>'name',
                "website" = record->>'website',
                "phone_number" = record->>'phone_number',
                "address" = address_str,
                "edited" = (record->>'edited')::boolean,
                "is_main_contact" = (record->>'is_main_contact')::boolean
            WHERE "id" = record->>'id';
        end if;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
