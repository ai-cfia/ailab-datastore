from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_unit(cursor: Cursor, unit: str, to_si_unit: float | None = None):
    """
    Inserts a new unit record into the database.

    Args:
        cursor: Database cursor object.
        unit: The name of the unit.
        to_si_unit: Conversion factor to SI unit (optional).

    Returns:
        The inserted unit record as a dictionary, or None if failed.
    """
    if unit is None:
        raise ValueError("Unit must be provided.")

    query = SQL("""
        INSERT INTO unit (unit, to_si_unit)
        VALUES (%s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (unit, to_si_unit))
        return new_cur.fetchone()


def read_unit(cursor: Cursor, id: str | UUID):
    """
    Retrieves a unit record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the unit.

    Returns:
        The unit record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Unit ID must be provided.")

    query = SQL("SELECT * FROM unit WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_units(cursor: Cursor):
    """
    Retrieves all unit records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all unit records as dictionaries.
    """
    query = SQL("SELECT * FROM unit;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_unit(
    cursor: Cursor, id: str | UUID, unit: str, to_si_unit: float | None = None
):
    """
    Updates an existing unit record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the unit.
        unit: New name of the unit.
        to_si_unit: New conversion factor to SI unit (optional).

    Returns:
        The updated unit record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Unit ID must be provided.")

    if unit is None:
        raise ValueError("Unit must be provided.")

    query = SQL("""
        UPDATE unit
        SET unit = %s, to_si_unit = %s
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (unit, to_si_unit, id))
        return new_cur.fetchone()


def delete_unit(cursor: Cursor, id: str | UUID):
    """
    Deletes a unit record by ID.

    Args:
        cursor: Database cursor object.
        id: ID of the unit.

    Returns:
        The deleted unit record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Unit ID must be provided.")

    query = SQL("""
        DELETE FROM unit
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def query_units(
    cursor: Cursor, unit: str | None = None, to_si_unit: float | None = None
):
    """
    Queries units based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        unit: Optional name of the unit to filter units.
        to_si_unit: Optional conversion factor to filter units.

    Returns:
        A list of unit records matching the filter criteria as dictionaries.
    """
    conditions = []
    parameters = []

    if unit is not None:
        conditions.append("unit = %s")
        parameters.append(unit)

    if to_si_unit is not None:
        conditions.append("to_si_unit = %s")
        parameters.append(to_si_unit)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM unit{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()
