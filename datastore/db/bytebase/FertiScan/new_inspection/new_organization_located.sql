
CREATE OR REPLACE FUNCTION "fertiscan_0.0.14".new_organization_info_located(
    name TEXT,
    address_str TEXT,
    website TEXT,
    phone_number TEXT,
    edited BOOLEAN = FALSE
    )
RETURNS uuid 
LANGUAGE plpgsql
AS $function$
DECLARE
    location_id uuid;
    record RECORD;
    organization_id uuid;
BEGIN
-- CHECK IF ANY OF THE INPUTS ARE NOT NULL
IF COALESCE(name, address_str, website, phone_number,'') = '' THEN
    RAISE EXCEPTION 'ALL of the input parameters are null';
END IF;
    -- CHECK IF ADRESS IS NULL
    IF address_str IS NULL THEN
        RAISE WARNING 'Address cannot be null';
    ELSE 
        -- Check if organization location exists by address
        SELECT id INTO location_id
        FROM location
        WHERE location.address ILIKE address_str
        LIMIT 1;
    
        IF location_id IS NULL THEN 
            INSERT INTO location (address)
            VALUES (
                address_str
            )
            RETURNING id INTO location_id;
        END IF;
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
