from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row, tuple_row
from psycopg.sql import SQL

from fertiscan.db.models import Metrics


class MetricCreationError(Exception):
    pass


class MetricNotFoundError(Exception):
    pass


def create_metric(
    cursor: Cursor,
    value: float | None = None,
    edited: bool | None = None,
    unit_id: str | UUID | None = None,
    metric_type: str | None = None,
    label_id: str | UUID | None = None,
):
    """
    Inserts a new metric record into the database.

    Args:
        cursor: Database cursor object.
        value: The value of the metric (optional).
        edited: Whether the metric is edited (optional).
        unit_id: The ID of the unit associated with the metric (optional).
        metric_type: The type of the metric (optional).
        label_id: The ID of the label information (optional).

    Returns:
        The inserted metric record as a dictionary, or None if failed.
    """
    query = SQL("""
        INSERT INTO metric (value, edited, unit_id, metric_type, label_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (value, edited, unit_id, metric_type, label_id))
        return new_cur.fetchone()


def read_metric(cursor: Cursor, id: str | UUID):
    """
    Retrieves a metric record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the metric.

    Returns:
        The metric record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Metric ID must be provided.")

    query = SQL("SELECT * FROM metric WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_metrics(cursor: Cursor):
    """
    Retrieves all metric records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all metric records as dictionaries.
    """
    query = SQL("SELECT * FROM metric;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_metric(
    cursor: Cursor,
    id: str | UUID,
    value: float | None = None,
    edited: bool | None = None,
    unit_id: str | UUID | None = None,
    metric_type: str | None = None,
    label_id: str | UUID | None = None,
):
    """
    Updates an existing metric record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the metric.
        value: New value of the metric (optional).
        edited: New edited status (optional).
        unit_id: New unit ID associated with the metric (optional).
        metric_type: New type of the metric (optional).
        label_id: New label information ID (optional).

    Returns:
        The updated metric record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Metric ID must be provided.")

    query = SQL("""
        UPDATE metric
        SET value = %s, edited = %s, unit_id = %s, metric_type = %s, label_id = %s
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (value, edited, unit_id, metric_type, label_id, id))
        return new_cur.fetchone()


def delete_metric(cursor: Cursor, id: str | UUID):
    """
    Deletes a metric record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the metric.

    Returns:
        The deleted metric record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Metric ID must be provided.")

    query = SQL("""
        DELETE FROM metric
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def query_metrics(
    cursor: Cursor,
    value_from: float | None = None,
    value_to: float | None = None,
    edited: bool | None = None,
    unit_id: str | UUID | None = None,
    metric_type: str | None = None,
    label_id: str | UUID | None = None,
) -> list[dict]:
    """
    Queries metrics based on optional filter criteria, including a range of values.

    Args:
        cursor: Database cursor object.
        value_from: Start of the value range (inclusive).
        value_to: End of the value range (inclusive).
        edited: Optional edited status to filter metrics.
        unit_id: Optional unit ID to filter metrics.
        metric_type: Optional metric type to filter metrics.
        label_id: Optional label ID to filter metrics.

    Returns:
        A list of metric records matching the filter criteria, as dictionaries.
    """
    conditions = []
    parameters = []

    if value_from is not None:
        conditions.append("value >= %s")
        parameters.append(value_from)
    if value_to is not None:
        conditions.append("value <= %s")
        parameters.append(value_to)

    if edited is not None:
        conditions.append("edited = %s")
        parameters.append(edited)
    if unit_id is not None:
        conditions.append("unit_id = %s")
        parameters.append(unit_id)
    if metric_type is not None:
        conditions.append("metric_type = %s")
        parameters.append(metric_type)
    if label_id is not None:
        conditions.append("label_id = %s")
        parameters.append(label_id)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM metric{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()


def read_full_metric(cursor: Cursor, id: str | UUID):
    """
    Retrieves full metric details from the database using the full_metric_view.

    Args:
        cursor (Cursor): The database cursor used to execute the query.
        id (str | UUID): The UUID or string ID of the metric record.

    Returns:
        dict | None: The metric record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Metric ID must be provided.")

    query = SQL("SELECT * FROM full_metric_view WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


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
    metric = cursor.fetchone()
    if metric is None:
        raise MetricNotFoundError(
            "Error: could not get the metric for label: " + str(label_id)
        )
    return metric[0]


def update_metrics(cursor: Cursor, label_id: str | UUID, metrics: dict | Metrics):
    """
    Updates the metrics for a specific label in the database.

    Parameters:
    - cursor (Cursor): The database cursor used to execute the query.
    - label_id (str | UUID): The UUID or string ID of the label whose metrics
      need to be updated.
    - metrics (dict | Metrics): The metrics data, either as a dictionary or a
      Metrics instance. This data contains the updated metrics information
      to be stored.

    """
    if not isinstance(metrics, Metrics):
        metrics = Metrics.model_validate(metrics)

    cursor.row_factory = tuple_row
    cursor.execute(
        "SELECT update_metrics(%s, %s);",
        (label_id, metrics.model_dump_json()),
    )
