
CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".get_sub_label_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    fr text[];
    en text[];
    result_json jsonb;
BEGIN
    SELECT jsonb_object_agg(
                sub_type.type_en, 
                jsonb_build_object(
                    'en', COALESCE(sub_label_data.texts_en, '[]'::jsonb),
                    'fr', COALESCE(sub_label_data.texts_fr, '[]'::jsonb)
                )
           )
    INTO result_json
    FROM sub_type
    JOIN (
        SELECT 
            sub_type_id,
            array_agg(sub_label.text_content_en ORDER BY sub_label.id) AS texts_en,
            array_agg(sub_label.text_content_fr ORDER BY sub_label.id) AS texts_fr
        FROM sub_label
        WHERE sub_label.label_id = label_id 
        GROUP BY sub_label.sub_type_id
    ) AS sub_label_data
    ON sub_type.id = sub_label_data.sub_type_id
    GROUP BY
        sub_type.type_en;

    RETURN result_json;
END;
$function$;