"""
This module represent the function for the table metric and its children unit:

"""

from psycopg import Cursor
from uuid import UUID

from fertiscan.db.queries.errors import (
    MetricCreationError,
    MetricQueryError,
    MetricRetrievalError,
    MetricUpdateError,
    MetricDeleteError,
    UnitCreationError,
    UnitQueryError,
    handle_query_errors,
)


@handle_query_errors(MetricQueryError)
def is_a_metric(cursor, metric_id):
    """
    This function checks if the metric is in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - boolean: if the metric exists.
    """

    query = """
        SELECT EXISTS(
            SELECT 
                1 
            FROM 
                metric
            WHERE 
                id = %s
            )   
        """
    cursor.execute(query, (metric_id,))
    return cursor.fetchone()[0]


@handle_query_errors(MetricCreationError)
def new_metric(
    cursor: Cursor, value, read_unit, label_id, metric_type: str, edited=False
):
    """
    This function uploads a new metric to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - value (float): The value of the metric.
    - unit_id (str): The UUID of the unit.
    - edited (boolean, optional): The value if the metric has been edited by the user after confirmation. Default is False.

    Returns:
    - The UUID of the metric.
    """
    if metric_type.lower() not in ["density", "weight", "volume"]:
        raise MetricCreationError(
            f"Error: metric type:{metric_type} not valid. Metric type must be one of the following: 'density','weight','volume'"
        )
    query = """
        SELECT new_metric_unit(%s, %s, %s, %s, %s);
        """
    cursor.execute(
        query,
        (
            value,
            read_unit,
            label_id,
            metric_type.lower(),
            edited,
        ),
    )
    if result := cursor.fetchone():
        return result[0]
    raise MetricCreationError("Failed to create metric. No data returned.")


@handle_query_errors(MetricRetrievalError)
def get_metric(cursor: Cursor, metric_id):
    """
    This function gets the metric from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - The metric.
    """

    query = """
        SELECT
            value,
            unit_id,
            edited,
            metric_type
        FROM
            metric
        WHERE
            id = %s
        """
    cursor.execute(query, (metric_id,))
    return cursor.fetchone()


@handle_query_errors(MetricRetrievalError)
def get_metric_by_label(cursor: Cursor, label_id):
    """
    This function gets the metric from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - The metric.
    """

    query = """
        SELECT
            id,
            value,
            unit_id,
            edited,
            metric_type
        FROM
            metric
        WHERE
            label_id = %s
        ORDER BY
            metric_type
        """
    cursor.execute(query, (label_id,))
    return cursor.fetchall()


@handle_query_errors(MetricRetrievalError)
def get_metrics_json(cursor: Cursor, label_id) -> dict:
    """
    This function gets the metric from the database and returns it in json format.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - The metric in dict format.
    """
    query = """
        SELECT get_metrics_json(%s);
        """
    cursor.execute(query, (str(label_id),))
    if result := cursor.fetchone():
        return result[0]
    raise MetricRetrievalError(
        "Failed to retrieve metrics json. No data returned for: " + str(label_id)
    )


@handle_query_errors(MetricRetrievalError)
def get_full_metric(cursor: Cursor, metric_id):
    """
    This function gets the metric from the database with the unit.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - The metric with the unit.
    """

    query = """
        SELECT
            metric.id,
            metric.value,
            unit.unit,
            unit.to_si_unit,
            metric.edited,
            metric.metric_type,
            CONCAT(CAST(metric.value AS CHAR), ' ', unit.unit) AS full_metric
        FROM
            metric
        JOIN
            unit
        ON
            metric.unit_id = unit.id
        WHERE
            metric.id = %s
        """
    cursor.execute(query, (metric_id,))
    return cursor.fetchone()


@handle_query_errors(UnitCreationError)
def new_unit(cursor: Cursor, unit, to_si_unit):
    """
    This function uploads a new unit to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.
    - to_si_unit (float): The unit in SI units.

    Returns:
    - The UUID of the unit.
    """

    query = """
        INSERT INTO 
            unit(
                unit,
                to_si_unit
                )
        VALUES
            (%s, %s)
        RETURNING id
        """
    cursor.execute(
        query,
        (
            unit,
            to_si_unit,
        ),
    )
    if result := cursor.fetchone():
        return result[0]
    raise UnitCreationError("Failed to create unit. No data returned.")


@handle_query_errors(UnitQueryError)
def is_a_unit(cursor: Cursor, unit):
    """
    This function checks if the unit is in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.

    Returns:
    - boolean: if the unit exists.
    """

    query = """
        SELECT EXISTS(
            SELECT 
                1 
            FROM 
                unit
            WHERE 
                unit = %s
            )   
        """
    cursor.execute(query, (unit,))
    return cursor.fetchone()[0]


@handle_query_errors(UnitQueryError)
def get_unit_id(cursor: Cursor, unit):
    """
    This function gets the unit from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.

    Returns:
    - The UUID of the unit.
    """

    query = """
        SELECT
            id
        FROM
            unit
        WHERE
            unit = %s
        """
    cursor.execute(query, (unit,))
    if result := cursor.fetchone():
        return result[0]
    raise UnitQueryError("Failed to retrieve unit id. No data returned.")

@handle_query_errors(MetricDeleteError)
def delete_metric_by_type(cursor:Cursor, label_id:UUID, metric_type:str)->int:
    """
    This function deletes a metric from the database based on label_id and metric_type.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (UUID): The UUID of the label.
    - metric_type (str): The type of the metric.

    Returns:
    - number of deleted rows. (int)
    """
    query = """
        DELETE FROM
            metric
        WHERE
            label_id = %s AND
            metric_type = %s
        RETURNING ID;
        """
    cursor.execute(query, (label_id, metric_type))
    return cursor.rowcount
    
@handle_query_errors(MetricDeleteError)
def delete_metric(cursor:Cursor, label_id:UUID)->int:
    """
    This function deletes a metric from the database based on label_id and metric_type.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (UUID): The UUID of the label.
    
    Returns:
    - number of deleted rows. (int)
    """
    rowcount=0
    for type in ["density", "weight", "volume"]:
        rowcount += delete_metric_by_type(
            cursor=cursor,
            label_id=label_id,
            metric_type=type
        )
    return rowcount

@handle_query_errors(MetricUpdateError)
def upsert_metric(cursor: Cursor, label_id:UUID,metrics:dict):
    delete_metric(cursor=cursor,label_id=label_id)
    
    # Weight
    for record in metrics["weight"]:
        new_metric(
            cursor=cursor,
            value= record["value"],
            read_unit=record["unit"],
            label_id=label_id,
            metric_type='weight',
            edited=record["edited"]
        )
    # Density
    new_metric(
        cursor=cursor,
        value= metrics["density"]["value"],
        read_unit=metrics["density"]["unit"],
        label_id=label_id,
        metric_type='density',
        edited=metrics["density"]["edited"]
    )
    # Volume
    new_metric(
        cursor=cursor,
        value= metrics["volume"]["value"],
        read_unit=metrics["volume"]["unit"],
        label_id=label_id,
        metric_type='volume',
        edited=metrics["volume"]["edited"]
    )
    
