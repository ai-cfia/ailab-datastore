CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".get_ingredients_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    record RECORD
    result_json jsonb;
BEGIN
    SELECT jsonb_build_object(
        'ingredients', jsonb_build_object(
            'en',jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(ingredient.name, Null),
                    'value', COALESCE(ingredient.value,Null),
                    'unit', COALESCE(ingredient.unit,Null),
                    'edited', COALESCE(ingredient.edited,Null)
                )
            ) FILTER (WHERE ingredient.language = 'en'), 
            'fr', jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(ingredient.name, Null),
                    'value', COALESCE(ingredient.value,Null),
                    'unit', COALESCE(ingredient.unit,Null),
                    'edited', COALESCE(ingredient.edited,Null)
                )
            ) FILTER (WHERE ingredient.language = 'fr')
        )
    )
    INTO result_json
    FROM ingredient
    WHERE ingredient.label_id = label_id
    ORDER BY ingredient.language;
    RETURN result_json;
END;
$function$;