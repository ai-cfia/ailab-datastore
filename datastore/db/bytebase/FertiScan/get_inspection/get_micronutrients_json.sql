
CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".get_micronutrient_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_build_object(
                'micronutrients', 
                jsonb_build_object(
                    'en', jsonb_agg(
                        jsonb_build_object(
                            'name', COALESCE(micronutrient.read_name,Null),
                            'unit', COALESCE(micronutrient.unit,Null),
                            'value', COALESCE(micronutrient.value,Null),
                            'edited', COALESCE(micronutrient.edited,Null)
                        )
                    ) FILTER (WHERE micronutrient.language = 'en'),
                    'fr', jsonb_agg(
                        jsonb_build_object(
                            'name', COALESCE(micronutrient.ph,Null),
                            'unit', COALESCE(micronutrient.humidity,Null),
                            'value', COALESCE(micronutrient.solubility,Null),
                            'edited', COALESCE(micronutrient.edited,Null)
                        )
                    ) FILTER (WHERE micronutrient.language = 'fr')
                )
           )
    INTO result_json
    FROM micronutrient
    WHERE micronutrient.label_id = label_id
    ORDER BY micronutrient.language;
    RETURN result_json;
END;
$function$;