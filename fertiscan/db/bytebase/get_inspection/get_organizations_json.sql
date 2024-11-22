
--Unverified organization data
DROP IF EXISTS FUNCTION "fertiscan_0.0.18".get_organizations_information_json(label_id uuid);
CREATE OR REPLACE FUNCTION "fertiscan_0.0.18".get_organizations_information_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_agg(jsonb_build_object(
        'organizations',
        jsonb_build_object(
                'id',  COALESCE(org.id, Null),
                'name',  COALESCE(org.name, Null),
                'address',  COALESCE(org.address, Null),
                'phone_number',  COALESCE(org.phone_number, Null),
                'website',  COALESCE(org.website, Null),
                'edited',  COALESCE(org.edited, Null),
                'is_main_contact',  COALESCE(org.is_main_contact, Null)
        )
    ))
    INTO result_json
    FROM organization_information as org
    WHERE org.label_id = label_id;
    RETURN result_json;
END;
$function$;

-- verified organization 
DROP IF EXISTS FUNCTION "fertiscan_0.0.18".get_organizations_json();
CREATE OR REPLACE FUNCTION "fertiscan_0.0.18".get_organizations_json()
RETURNS jsonb
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_agg(jsonb_build_object(
        'organizations',
        jsonb_build_object(
                'id',  COALESCE(org.id, Null),
                'name',  COALESCE(org.name, Null),
                'address',  COALESCE(org.address, Null),
                'phone_number',  COALESCE(org.phone_number, Null),
                'website',  COALESCE(org.website, Null),
                'updated_at',  COALESCE(org.updated_at, Null),
        )
    ))
    INTO result_json
    FROM organization_information as org;
    RETURN result_json;
END;
