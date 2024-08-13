"""
This module represent the function for the table metric and its children unit:

"""


class MetricCreationError(Exception):
    pass


class MetricNotFoundError(Exception):
    pass


class UnitCreationError(Exception):
    pass


class UnitNotFoundError(Exception):
    pass


def is_a_metric(cursor, metric_id):
    """
    This function checks if the metric is in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - boolean: if the metric exists.
    """

    try:
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
    except Exception:
        return False


def new_metric(cursor, value, read_unit, label_id, metric_type:str,edited=False):
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

    try:
        if metric_type.lower() not in ["density","weight","volume"]:
            raise MetricCreationError(f"Error: metric type:{metric_type} not valid. Metric type must be one of the following: 'density','weight','volume'")
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
        return cursor.fetchone()[0]
    except Exception:
        raise MetricCreationError("Error: metric not uploaded")


def get_metric(cursor, metric_id):
    """
    This function gets the metric from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - The metric.
    """

    try:
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
    except Exception:
        raise MetricNotFoundError("Error: metric not found")

def get_metric_by_label(cursor, label_id):
    """
    This function gets the metric from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - The metric.
    """

    try:
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
    except Exception:
        raise MetricNotFoundError("Error: metric not found")
    
def get_metrics_json(cursor, label_id) -> dict:
    """
    This function gets the metric from the database and returns it in json format.
    
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - The metric in dict format.
    """
    try:
        query = """
            SELECT get_metrics_json(%s);
            """
        cursor.execute(query, (str(label_id),))
        metric = cursor.fetchone()
        if metric is None:
            raise MetricNotFoundError("Error: could not get the metric for label: " + str(label_id))
        return metric
    except MetricNotFoundError as e:
        raise e
    except Exception:
        raise e


def get_full_metric(cursor, metric_id):
    """
    This function gets the metric from the database with the unit.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - metric_id (str): The UUID of the metric.

    Returns:
    - The metric with the unit.
    """

    try:
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
    except Exception:
        raise MetricNotFoundError("Error: metric not found")


def new_unit(cursor, unit, to_si_unit):
    """
    This function uploads a new unit to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.
    - to_si_unit (float): The unit in SI units.

    Returns:
    - The UUID of the unit.
    """

    try:
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
        return cursor.fetchone()[0]
    except Exception:
        raise UnitCreationError("Error: unit not uploaded")


def is_a_unit(cursor, unit):
    """
    This function checks if the unit is in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.

    Returns:
    - boolean: if the unit exists.
    """

    try:
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
    except Exception:
        return False


def get_unit_id(cursor, unit):
    """
    This function gets the unit from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - unit (str): The unit.

    Returns:
    - The UUID of the unit.
    """

    try:
        query = """
            SELECT
                id
            FROM
                unit
            WHERE
                unit = %s
            """
        cursor.execute(query, (unit,))
        return cursor.fetchone()[0]
    except Exception:
        raise UnitNotFoundError("Error: unit not found")
