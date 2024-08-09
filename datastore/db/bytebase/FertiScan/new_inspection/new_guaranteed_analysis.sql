CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_location(
name TEXT,
value FLOAT,
unit TEXT,
label_id UUID
)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    guaranteed_id uuid;
    record RECORD
    _id uuid;
BEGIN
	INSERT INTO guaranteed (read_name, value, unit, edited, label_id)
	VALUES (
		name,
	    value,
	    unit,
		FALSE,
		label_id
    ) RETURNING id INTO guaranteed_id;
    RETURN guaranteed_id;
END;
$function$;