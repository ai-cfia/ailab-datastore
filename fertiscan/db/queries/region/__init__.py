from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_region(cursor: Cursor, name: str, province_id: int) -> dict | None:
    """
    Inserts a new region record into the database.

    Args:
        cursor: Database cursor object.
        name: Name of the region.
        province_id: ID of the associated province.

    Returns:
        The inserted region record as a dictionary, or None if failed.
    """
    query = SQL("""
        INSERT INTO region (name, province_id)
        VALUES (%s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, province_id))
        return new_cur.fetchone()


def read_region(cursor: Cursor, region_id: UUID) -> dict | None:
    """
    Retrieves a region record by ID.

    Args:
        cursor: Database cursor object.
        region_id: UUID of the region.

    Returns:
        The region record as a dictionary, or None if not found.
    """
    query = SQL("SELECT * FROM region WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (region_id,))
        return new_cur.fetchone()


def read_all_regions(cursor: Cursor) -> list[dict]:
    """
    Retrieves all region records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all region records as dictionaries.
    """
    query = SQL("SELECT * FROM region;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_region(
    cursor: Cursor,
    region_id: UUID,
    name: str | None = None,
    province_id: int | None = None,
) -> dict | None:
    """
    Updates an existing region record by ID.

    Args:
        cursor: Database cursor object.
        region_id: UUID of the region.
        name: Optional new name of the region.
        province_id: Optional new province ID.

    Returns:
        The updated region record as a dictionary, or None if not found.
    """
    query = SQL("""
        UPDATE region
        SET name = COALESCE(%s, name),
            province_id = COALESCE(%s, province_id)
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, province_id, region_id))
        return new_cur.fetchone()


def delete_region(cursor: Cursor, region_id: UUID) -> dict | None:
    """
    Deletes a region record by ID.

    Args:
        cursor: Database cursor object.
        region_id: UUID of the region.

    Returns:
        The deleted region record as a dictionary, or None if not found.
    """
    query = SQL("""
        DELETE FROM region
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (region_id,))
        return new_cur.fetchone()


def query_regions(
    cursor: Cursor, name: str | None = None, province_id: int | None = None
) -> list[dict]:
    """
    Queries regions based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        name: Optional name to filter regions.
        province_id: Optional province ID to filter regions.

    Returns:
        A list of region records matching the filter criteria as dictionaries.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)
    if province_id is not None:
        conditions.append("province_id = %s")
        parameters.append(province_id)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM region{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()


def get_full_region(cursor: Cursor, region_id: UUID) -> dict | None:
    """
    Retrieves the full region details, including associated province info.

    Args:
        cursor: Database cursor object.
        region_id: UUID of the region.

    Returns:
        A dictionary with the full region details, or None if not found.
    """
    query = """
        SELECT
            region.id,
            region.name,
            province.id AS province_id,
            province.name AS province_name
        FROM
            region
        LEFT JOIN
            province
        ON
            region.province_id = province.id
        WHERE
            region.id = %s;
    """
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (region_id,))
        return new_cur.fetchone()
