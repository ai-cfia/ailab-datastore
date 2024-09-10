CREATE OR REPLACE FUNCTION "fertiscan_0.0.12".get_guaranteed_analysis_json(
label_info_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    SELECT jsonb_build_object(
        'guaranteed_analysis', jsonb_build_object(
            'title', COALESCE(label_information.guaranteed_title, Null),
            'titre', COALESCE(label_information.guaranteed_titre,Null),
            'is_minimal', COALESCE(label_information.title_is_minimal,Null),
            'en', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(guaranteed.name, Null),
                    'value', COALESCE(guaranteed.value,Null),
                    'unit', COALESCE(guaranteed.unit,Null),
                    'edited', COALESCE(guaranteed.edited,Null)
                )
            ) FILTER (WHERE guaranteed.language = 'en'), '[]'::jsonb), 
            'fr', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(guaranteed.name, Null),
                    'value', COALESCE(guaranteed.value,Null),
                    'unit', COALESCE(guaranteed.unit,Null),
                    'edited', COALESCE(guaranteed.edited,Null)
                )
            ) FILTER (WHERE guaranteed.language = 'fr'), '[]'::jsonb)
        )
    )
    INTO result_json
    FROM guaranteed, label_information
    WHERE guaranteed.label_id = label_info_id AND label_information.id = label_info_id;
    RETURN result_json;

END;
$function$;
