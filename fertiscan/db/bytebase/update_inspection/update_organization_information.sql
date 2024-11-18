
-- Function to upsert organization information
CREATE OR REPLACE FUNCTION "fertiscan_0.0.17".upsert_organization_info(input_org_info jsonb, label_info_id uuid)
RETURNS uuid AS $$
DECLARE
    record jsonb;
    address_str TEXT;
BEGIN

    -- loop each orgs in the input_org_info
    for record in SELECT * FROM jsonb_array_elements(input_org_info)
    loop
        if record->>'id' IS NULL THEN
            new_organization_info_located(
                record->>'name',
                record->>'address',
                record->>'website',
                record->>'phone_number',
                TRUE
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
                "edited" = (record->>'edited')::boolean
            WHERE "id" = record->>'id';
        end if;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
