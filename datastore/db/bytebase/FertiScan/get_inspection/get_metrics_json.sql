CREATE OR REPLACE FUNCTION "fertiscan_0.0.12".get_metrics_json(
label_id uuid)
RETURNS jsonb 
LANGUAGE plpgsql
AS $function$
DECLARE
    result_json jsonb;
BEGIN
    WITH metric_data AS (
        SELECT 
            metric.metric_type,
            metric.value,
            unit.unit,
            metric.edited
        FROM 
            metric
        JOIN 
            unit ON metric.unit_id = unit.id
        WHERE 
            metric.label_id = label_id 
        ORDER BY 
            metric.metric_type
    ),
    weight_data AS (
        SELECT 
            jsonb_agg(
                jsonb_build_object(
                    'unit', COALESCE(unit, Null),
                    'value', COALESCE(value, Null)
                )
            ) AS weight
        FROM 
            metric_data
        WHERE 
            metric_type = 'weight'
    )
    SELECT jsonb_build_object(
                'metrics',
                jsonb_build_object(
                    'volume', (
                        SELECT 
                            jsonb_build_object(
                                'unit', COALESCE(unit, Null),
                                'value', COALESCE(value, Null)
                            )
                        FROM 
                            metric_data
                        WHERE 
                            metric_type = 'volume'
                        LIMIT 1
                    ),
                    'weight', (
                        SELECT 
                            weight
                        FROM 
                            weight_data
                    ),
                    'density', (
                        SELECT 
                            jsonb_build_object(
                                'unit', COALESCE(unit, Null),
                                'value', COALESCE(value, Null)
                            )
                        FROM 
                            metric_data
                        WHERE 
                            metric_type = 'density'
                        LIMIT 1
                    )
                )
           )
    INTO result_json;

    RETURN result_json;
END;
$function$;
