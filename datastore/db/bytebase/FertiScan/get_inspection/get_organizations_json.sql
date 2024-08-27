CREATE OR REPLACE FUNCTION "fertiscan_0.0.12".get_organizations_information_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_agg(jsonb_build_object(
        CASE 
            WHEN org.id = label_info.manufacturer_info_id THEN 'manufacturer'
            WHEN org.id = label_info.company_info_id THEN 'company'
            ELSE 'organization'
        end, 
            jsonb_build_object(
                'id',  COALESCE(org.id, Null),
                'name',  COALESCE(org.name, Null),
                'address',  COALESCE(location.address, Null),
                'phone_number',  COALESCE(org.phone_number, Null),
                'website',  COALESCE(org.website, Null)
            )
    ))
    INTO result_json
    FROM organization_information as org
    JOIN (
        SELECT 
            company_info_id,
            manufacturer_info_id
        FROM 
            label_information
        WHERE 
            id = label_id
        LIMIT 1
    ) AS label_info
    ON org.id = label_info.company_info_id OR org.id = label_info.manufacturer_info_id
    JOIN (
        SELECT
            id,
            address
        FROM
            location
    ) AS location
    ON org.location_id = location.id;
    RETURN result_json;
END;
$function$;
