CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_specification(
humidity FLOAT,
ph FLOAT,
solubility FLOAT,
language "fertiscan_0.0.11".language,
label_id UUID
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    specification_id uuid;
    record RECORD
    _id uuid;
BEGIN
	INSERT INTO specification (humidity, ph, solubility, edited,LANGUAGE,label_id)
			VALUES (
				humidity,
				ph,
				solubility,
				FALSE,
				language,
				label_id
			)
            RETURNING id INTO specification_id;
    RETURN specification_id;
END;
$function$;