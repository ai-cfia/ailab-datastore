CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".get_specification_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_build_object(
        'specifications', jsonb_build_object(
            'en',jsonb_agg(
                jsonb_build_object(
                    'ph', COALESCE(specification.ph, Null),
                    'humidity', COALESCE(specification.humidity,Null),
                    'solubility', COALESCE(specification.solubility,Null),
                    'edited', COALESCE(specification.edited,Null)
                )
            ) FILTER (WHERE specification.language = 'en'), 
            'fr', jsonb_agg(
                jsonb_build_object(
                    'ph', COALESCE(specification.ph,Null),
                    'humidity', COALESCE(specification.humidity,Null),
                    'solubility', COALESCE(specification.solubility,Null),
                    'edited', COALESCE(specification.edited,Null)
                )
            ) FILTER (WHERE specification.language = 'fr')
        )
    )
    INTO result_json
    FROM specification
    WHERE specification.label_id = label_id;
    RETURN result_json;
END;
$function$;
