CREATE OR REPLACE FUNCTION "fertiscan_0.0.17".get_organizations_information_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_agg(jsonb_build_object(
        'organization',
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
    WHERE org.label_id = label_id
    RETURN result_json;
END;
$function$;
