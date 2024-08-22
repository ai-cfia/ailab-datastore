CREATE OR REPLACE FUNCTION "fertiscan_0.0.11".new_metric_unit(
    value FLOAT,
    read_unit TEXT,
    label_id UUID,
    metric_type "fertiscan_0.0.11".metric_type
    )
RETURNS UUID 
LANGUAGE plpgsql
AS $function$
DECLARE
    unit_id UUID;
    record RECORD
    metric_id UUID;
BEGIN
	
       -- Check if the weight_unit exists in the unit table
	    SELECT id INTO unit_id FROM unit WHERE unit ILIKE read_unit;
	   
	   -- If unit_id is null, the unit does not exist
	    IF unit_id IS NULL THEN
	        -- Insert the new unit
	        INSERT INTO unit (unit, to_si_unit)
	        VALUES (read_unit, null) -- Adjust to_si_unit value as necessary
	        RETURNING id INTO unit_id;
	    END IF;
	   
	   	 -- Insert into metric for weight
	    INSERT INTO metric (value, unit_id, edited,metric_type_id,label_id)
	    VALUES (value_float, unit_id, FALSE,metric_type,label_id);
        RETURN metric_id;
    RETURN metric_id;
END;
$function$;