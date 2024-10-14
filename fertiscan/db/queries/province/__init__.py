from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_province(cursor: Cursor, name: str):
    """
    Inserts a new province record into the database.

    Args:
        cursor: Database cursor object.
        name: Name of the province.

    Returns:
        The inserted province record as a dictionary, or None if failed.
    """
    query = SQL("""
        INSERT INTO province (name)
        VALUES (%s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name,))
        return new_cur.fetchone()


def read_province(cursor: Cursor, province_id: int):
    """
    Retrieves a province record by ID.

    Args:
        cursor: Database cursor object.
        province_id: ID of the province.

    Returns:
        The province record as a dictionary, or None if not found.
    """
    query = SQL("SELECT * FROM province WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (province_id,))
        return new_cur.fetchone()


def read_all_provinces(cursor: Cursor):
    """
    Retrieves all province records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all province records as dictionaries.
    """
    query = SQL("SELECT * FROM province;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_province(cursor: Cursor, province_id: int, name: str):
    """
    Updates an existing province record by ID.

    Args:
        cursor: Database cursor object.
        province_id: ID of the province.
        name: New name of the province.

    Returns:
        The updated province record as a dictionary, or None if not found.
    """
    query = SQL("""
        UPDATE province
        SET name = %s
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, province_id))
        return new_cur.fetchone()


def delete_province(cursor: Cursor, province_id: int):
    """
    Deletes a province record by ID.

    Args:
        cursor: Database cursor object.
        province_id: ID of the province.

    Returns:
        The deleted province record as a dictionary, or None if not found.
    """
    query = SQL("""
        DELETE FROM province
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (province_id,))
        return new_cur.fetchone()


def query_provinces(cursor: Cursor, name: str | None = None):
    """
    Queries provinces based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        name: Optional name to filter provinces.

    Returns:
        A list of province records matching the filter criteria as dictionaries.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM province{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()
