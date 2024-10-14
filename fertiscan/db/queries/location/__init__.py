from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_location(
    cursor: Cursor,
    name: str | None,
    address: str,
    region_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
):
    """
    Inserts a new location record into the database.

    Args:
        cursor: Database cursor object.
        name: Optional name of the location.
        address: Address of the location.
        region_id: Optional UUID or string of the associated region.
        owner_id: Optional UUID or string of the associated owner.

    Returns:
        The inserted location record as a dictionary, or None if failed.
    """
    query = SQL("""
        INSERT INTO location (name, address, region_id, owner_id)
        VALUES (%s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, address, region_id, owner_id))
        return new_cur.fetchone()


def read_location(cursor: Cursor, location_id: str | UUID):
    """
    Retrieves a location record by ID.

    Args:
        cursor: Database cursor object.
        location_id: UUID or string ID of the location.

    Returns:
        The location record as a dictionary, or None if not found.
    """
    query = SQL("SELECT * FROM location WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (location_id,))
        return new_cur.fetchone()


def read_all_locations(cursor: Cursor):
    """
    Retrieves all location records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all location records as dictionaries.
    """
    query = SQL("SELECT * FROM location;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_location(
    cursor: Cursor,
    location_id: str | UUID,
    name: str | None = None,
    address: str | None = None,
    region_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
):
    """
    Updates an existing location record by ID.

    Args:
        cursor: Database cursor object.
        location_id: UUID or string ID of the location.
        name: Optional new name of the location.
        address: Optional new address.
        region_id: Optional new region UUID.
        owner_id: Optional new owner UUID.

    Returns:
        The updated location record as a dictionary, or None if not found.
    """
    query = SQL("""
        UPDATE location
        SET name = COALESCE(%s, name),
            address = COALESCE(%s, address),
            region_id = COALESCE(%s, region_id),
            owner_id = COALESCE(%s, owner_id)
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, address, region_id, owner_id, location_id))
        return new_cur.fetchone()


def upsert_location(
    cursor: Cursor,
    address: str,
    location_id: str | UUID | None = None,
    name: str | None = None,
    region_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
) -> UUID:
    """
    Upserts a location based on the provided parameters.

    Args:
        cursor: Database cursor object.
        address: Address of the location. Cannot be None or Empty.
        location_id: UUID or string ID of the location. If None, a new location is created.
        name: Name of the location. Can be None.
        region_id: UUID or string ID of the associated region. Can be None.
        owner_id: UUID or string ID of the associated owner. Can be None.

    Returns:
        The UUID of the upserted location.
    """
    if not address:
        raise ValueError("Address cannot be empty or null or empty")

    query = SQL("SELECT upsert_location(%s, %s, %s, %s, %s);")
    cursor.execute(query, (location_id, name, address, region_id, owner_id))
    return cursor.fetchone()[0]


def delete_location(cursor: Cursor, location_id: str | UUID):
    """
    Deletes a location record by ID.

    Args:
        cursor: Database cursor object.
        location_id: UUID or string ID of the location.

    Returns:
        The deleted location record as a dictionary, or None if not found.
    """
    query = SQL("""
        DELETE FROM location
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (location_id,))
        return new_cur.fetchone()


def query_locations(
    cursor: Cursor,
    name: str | None = None,
    address: str | None = None,
    region_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
) -> list[dict]:
    """
    Queries locations based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        name: Optional name to filter locations.
        address: Optional address to filter locations.
        region_id: Optional region UUID to filter locations.
        owner_id: Optional owner UUID to filter locations.

    Returns:
        A list of location records matching the filter criteria, as dictionaries.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)
    if address is not None:
        conditions.append("address = %s")
        parameters.append(address)
    if region_id is not None:
        conditions.append("region_id = %s")
        parameters.append(region_id)
    if owner_id is not None:
        conditions.append("owner_id = %s")
        parameters.append(owner_id)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM location{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()


def get_full_location(cursor: Cursor, location_id: str | UUID):
    """
    This function get the full location details from the database.
    This includes the region and province info of the location.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - location_id (str): The UUID of the location.

    Returns:
    - dict: The location
    """
    query = """
        SELECT
            location.id,
            location.name,
            location.address,
            region.name as region_name,
            province.name as province_name
        FROM
            location
        LEFT JOIN
            region
        ON
            location.region_id = region.id
        LEFT JOIN
            province
        ON
            region.province_id = province.id
        WHERE
            location.id = %s
        """
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (location_id,))
        return new_cur.fetchone()
