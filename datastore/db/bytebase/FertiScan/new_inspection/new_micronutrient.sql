CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_micronutrient(
name TEXT,
value FLOAT,
unit TEXT,
label_id UUID,
language "fertiscan_0.0.11".language
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    micronutrient_id uuid;
    record RECORD
    _id uuid;
BEGIN
	INSERT INTO micronutrient (read_name, value, unit, edited, label_id,language)
	VALUES (
		name,
	    value,
	    unit,
		FALSE,
		label_id,
		language
	)
    RETURNING id INTO micronutrient_id;
    RETURN micronutrient_id;
END;
$function$;