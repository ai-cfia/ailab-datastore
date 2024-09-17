CREATE OR REPLACE FUNCTION "fertiscan_0.0.14".get_guaranteed_analysis_json(
label_info_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_build_object(
            'guaranteed_analysis', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(guaranteed.read_name,Null),
                    'unit', COALESCE(guaranteed.unit,Null),
                    'value', COALESCE(guaranteed.value,Null),
                    'edited', COALESCE(guaranteed.edited,Null)
                )
            )
        ,NULL))
    INTO result_json
    FROM guaranteed
    WHERE guaranteed.label_id = label_info_id;
    RETURN result_json;
END;
$function$;
