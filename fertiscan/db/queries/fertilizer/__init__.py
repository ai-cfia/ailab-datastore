from datetime import datetime
from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row, tuple_row
from psycopg.sql import SQL

# TODO: properly handle exceptions


def create_fertilizer(
    cursor: Cursor,
    name: str,
    registration_number: str | None = None,
    latest_inspection_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
):
    """
    Inserts a new fertilizer record into the database.

    Args:
        cursor: Database cursor object.
        name: Name of the fertilizer.
        registration_number: Optional registration number.
        latest_inspection_id: Optional UUID or string of the latest inspection.
        owner_id: Optional UUID or string of the owner.

    Returns:
        The inserted fertilizer record as a dictionary, or None if failed.
    """
    query = SQL("""
        INSERT INTO fertilizer (name, registration_number, latest_inspection_id, owner_id)
        VALUES (%s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(
            query, (name, registration_number, latest_inspection_id, owner_id)
        )
        return new_cur.fetchone()


def read_fertilizer(cursor: Cursor, fertilizer_id: str | UUID):
    """
    Retrieves a fertilizer record by ID.

    Args:
        cursor: Database cursor object.
        fertilizer_id: UUID or string ID of the fertilizer.

    Returns:
        The fertilizer record as a dictionary, or None if not found.
    """
    query = SQL("SELECT * FROM fertilizer WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (fertilizer_id,))
        return new_cur.fetchone()


def read_all_fertilizers(cursor: Cursor):
    """
    Retrieves all fertilizer records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all fertilizer records as dictionaries.
    """
    query = SQL("SELECT * FROM fertilizer;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_fertilizer(
    cursor: Cursor,
    fertilizer_id: str | UUID,
    name: str | None = None,
    registration_number: str | None = None,
    latest_inspection_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
):
    """
    Updates an existing fertilizer record by ID.

    Args:
        cursor: Database cursor object.
        fertilizer_id: UUID or string ID of the fertilizer.
        name: Optional new name of the fertilizer.
        registration_number: Optional new registration number.
        latest_inspection_id: Optional new inspection ID.
        owner_id: Optional new owner ID.

    Returns:
        The updated fertilizer record as a dictionary, or None if not found.
    """
    query = SQL("""
        UPDATE fertilizer
        SET name = COALESCE(%s, name),
            registration_number = COALESCE(%s, registration_number),
            latest_inspection_id = COALESCE(%s, latest_inspection_id),
            owner_id = COALESCE(%s, owner_id),
            update_at = CURRENT_TIMESTAMP
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(
            query,
            (name, registration_number, latest_inspection_id, owner_id, fertilizer_id),
        )
        return new_cur.fetchone()


def upsert_fertilizer(
    cursor: Cursor,
    name: str,
    registration_number: str | None = None,
    latest_inspection_id: str | UUID | None = None,
    owner_id: str | UUID | None = None,
):
    """
    Inserts a new fertilizer record or updates an existing one based on the fertilizer name.

    Args:
        cursor: Database cursor object.
        name: Name of the fertilizer. Used to identify the record for upsert.
        registration_number: Optional registration number of the fertilizer.
        latest_inspection_id: Optional UUID of the latest inspection.
        owner_id: Optional UUID of the owner.

    Returns:
        The UUID of the upserted fertilizer.
    """
    if not name:
        raise ValueError("Name cannot be null or empty")

    query = SQL("SELECT upsert_fertilizer(%s, %s, %s, %s);")
    cursor.row_factory = tuple_row
    cursor.execute(query, (name, registration_number, owner_id, latest_inspection_id))
    return cursor.fetchone()


def delete_fertilizer(cursor: Cursor, fertilizer_id: str | UUID):
    """
    Deletes a fertilizer record by ID.

    Args:
        cursor: Database cursor object.
        fertilizer_id: UUID or string ID of the fertilizer.

    Returns:
        The deleted fertilizer record as a dictionary, or None if not found.
    """
    query = SQL("""
        DELETE FROM fertilizer
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (fertilizer_id,))
        return new_cur.fetchone()


def query_fertilizers(
    cursor: Cursor,
    name: str | None = None,
    registration_number: str | None = None,
    owner_id: str | UUID | None = None,
    latest_inspection_id: str | UUID | None = None,
    upload_date_from: str | datetime | None = None,
    upload_date_to: str | datetime | None = None,
    update_at_from: str | datetime | None = None,
    update_at_to: str | datetime | None = None,
) -> list[dict]:
    """
    Queries fertilizers based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        name: Optional name to filter fertilizers.
        registration_number: Optional registration number.
        owner_id: Optional owner UUID (as string or UUID object).
        latest_inspection_id: Optional inspection UUID (as string or UUID object).
        upload_date_from: Start of the upload date range.
        upload_date_to: End of the upload date range.
        update_at_from: Start of the update date range.
        update_at_to: End of the update date range.

    Returns:
        A list of fertilizer records matching the filter criteria, as dictionaries.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)
    if registration_number is not None:
        conditions.append("registration_number = %s")
        parameters.append(registration_number)
    if owner_id is not None:
        conditions.append("owner_id = %s")
        parameters.append(owner_id)
    if latest_inspection_id is not None:
        conditions.append("latest_inspection_id = %s")
        parameters.append(latest_inspection_id)
    if upload_date_from is not None:
        conditions.append("upload_date >= %s")
        parameters.append(upload_date_from)
    if upload_date_to is not None:
        conditions.append("upload_date <= %s")
        parameters.append(upload_date_to)
    if update_at_from is not None:
        conditions.append("update_at >= %s")
        parameters.append(update_at_from)
    if update_at_to is not None:
        conditions.append("update_at <= %s")
        parameters.append(update_at_to)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM fertilizer{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()
