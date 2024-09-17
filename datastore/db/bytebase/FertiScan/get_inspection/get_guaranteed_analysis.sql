CREATE OR REPLACE FUNCTION "fertiscan_0.0.14".get_guaranteed_analysis_json(
label_info_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
    result_json_title jsonb;
    title text;
    titre text;
    is_minimal boolean;
begin
	-- build Guaranteed_analysis nuntrients
    SELECT jsonb_build_object(
        'guaranteed_analysis', jsonb_build_object(
            'en', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(guaranteed.read_name, Null),
                    'value', COALESCE(guaranteed.value,Null),
                    'unit', COALESCE(guaranteed.unit,Null),
                    'edited', COALESCE(guaranteed.edited,Null)
                )
            ) FILTER (WHERE guaranteed.language = 'en'), '[]'::jsonb), 
            'fr', COALESCE(jsonb_agg(
                jsonb_build_object(
                    'name', COALESCE(guaranteed.read_name, Null),
                    'value', COALESCE(guaranteed.value,Null),
                    'unit', COALESCE(guaranteed.unit,Null),
                    'edited', COALESCE(guaranteed.edited,Null)
                )
            ) FILTER (WHERE guaranteed.language = 'fr'), '[]'::jsonb)
        )
    )
    INTO result_json
    FROM "fertiscan_0.0.13".guaranteed
    WHERE guaranteed.label_id = label_info_id;
    -- build Guaranteed_analysis title json
    SELECT jsonb_build_object(
     'guaranteed_analysis', jsonb_build_object(
 		'title', COALESCE(guaranteed_title, Null),
 		'titre', COALESCE(guaranteed_titre, Null), 
 		'is_minimal', COALESCE(title_is_minimal, Null)
 		)
 	)
    INTO
		result_json_title
    FROM "fertiscan_0.0.13".label_information 
    WHERE id = label_info_id;
   -- merge JSONs
   --We need to merge the JSON and cannot une json_set with a Null value since it is not supported in the current version of Postgres
   return  jsonb_build_object(
     'guaranteed_analysis', jsonb_build_object(
 		'title', COALESCE(result_json_title->'guaranteed_analysis'->'title', Null),
 		'titre', COALESCE(result_json_title->'guaranteed_analysis'->'titre', Null), 
 		'is_minimal', COALESCE(result_json_title->'guaranteed_analysis'->'is_minimal', Null),
 		'en', COALESCE(result_json->'guaranteed_analysis'->'en','[]'::jsonb),
 		'fr',COALESCE(result_json->'guaranteed_analysis'->'fr','[]'::jsonb)
 		)
 	);
END;
$function$;
