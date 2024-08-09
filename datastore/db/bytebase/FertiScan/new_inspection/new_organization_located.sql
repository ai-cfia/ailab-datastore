CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_organization_located(name,address,website,phone_number)
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    location_id uuid;
    record RECORD
    organization_id uuid;
BEGIN
	-- Check if organization location exists by address
    SELECT id INTO location_id
    FROM location
    WHERE address ILIKE address
    LIMIT 1;
   
	IF location_id IS NULL THEN 
        INSERT INTO location (address)
        VALUES (
            address
        )
        RETURNING id INTO location_id;
    END IF;   
	INSERT INTO organization_information (name,website,phone_number,location_id)
	VALUES (
	        name,
            website,
            phone_number,
            location_id
	)
	RETURNING id INTO organization_id;

    RETURN organization_id;
END;
$function$;