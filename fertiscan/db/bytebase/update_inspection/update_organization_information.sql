
-- Function to upsert organization information
DROP FUNCTION IF EXISTS "fertiscan_0.0.17".upsert_organization_info(jsonb, uuid);
CREATE OR REPLACE FUNCTION "fertiscan_0.0.17".upsert_organization_info(input_org_info jsonb, label_info_id uuid)
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
        -- UPDATE THE LOCATION
            address_str := input_org_info->>'address';

            -- CHECK IF ADRESS IS NULL
            IF address_str IS NULL or COALESCE(address_str,'')='' THEN
                RAISE WARNING 'Address should not be null';
            ELSE 
                -- Check if organization location exists by address
                SELECT id INTO location_id
                FROM location
                WHERE location.address ILIKE address_str
                LIMIT 1;
                    -- Use upsert_location to insert or update the location
                location_id := upsert_location(location_id, address_str);
            END IF;
        -- UPDATE THE ORGANIZATION INFORMATION
            UPDATE organization_information SET
                "name" = record->>'name',
                "website" = record->>'website',
                "phone_number" = record->>'phone_number',
                "location_id" = location_id,
                "edited" = (record->>'edited')::boolean,
                "is_main_contact" = (record->>'is_main_contact')::boolean
            WHERE "id" = record->>'id';
        end if;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
