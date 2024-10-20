from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL


def create_organization_information(
    cursor: Cursor,
    name: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    location_id: str | None = None,
):
    """
    Inserts a new organization_information record into the database.

    Args:
        cursor: Database cursor object.
        name: Optional; Name of the organization.
        website: Optional; Website of the organization.
        phone_number: Optional; Phone number of the organization.
        location_id: Optional; Location ID associated with the organization.

    Returns:
        The inserted organization_information record as a dictionary, or None if insertion failed.
    """

    if all(v is None for v in (name, website, phone_number)):
        raise ValueError(
            "At least one of name, website, or phone_number must be provided"
        )

    query = SQL("""
        INSERT INTO organization_information 
        (name, website, phone_number, location_id)
        VALUES (%s, %s, %s, %s)
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (name, website, phone_number, location_id))
        return new_cur.fetchone()


def read_organization_information(cursor: Cursor, id: str):
    """
    Retrieves an organization_information record by ID.

    Args:
        cursor: Database cursor object.
        id: The ID of the organization to retrieve.

    Returns:
        The organization_information record as a dictionary, or None if not found.
    """

    if not id:
        raise ValueError("Organization ID must be provided.")

    query = SQL("SELECT * FROM organization_information WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_organization_information(cursor: Cursor):
    """
    Retrieves all organization_information records from the database.

    Args:
        cursor: Database cursor object.

    Returns:
        A list of all organization_information records as dictionaries.
    """
    query = SQL("SELECT * FROM organization_information;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_organization_information(
    cursor: Cursor,
    id: str | UUID,
    name: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    location_id: str | UUID | None = None,
    edited: bool | None = None,
):
    """
    Updates an existing organization information record by ID.

    Args:
        cursor: Database cursor object.
        id: UUID or string ID of the organization.
        name: Optional new name of the organization.
        website: Optional new website URL.
        phone_number: Optional new phone number.
        location_id: Optional new location ID.
        edited: Optional flag indicating if the organization was edited.

    Returns:
        The updated organization record as a dictionary, or None if not found.
    """

    if id is None:
        raise ValueError("Organization ID must be provided.")

    if all(v is None for v in (name, website, phone_number)):
        raise ValueError(
            "At least one of name, website, or phone_number must be provided."
        )

    query = SQL("""
        UPDATE organization_information
        SET name = COALESCE(%s, name),
            website = COALESCE(%s, website),
            phone_number = COALESCE(%s, phone_number),
            location_id = COALESCE(%s, location_id),
            edited = COALESCE(%s, edited)
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(
            query,
            (name, website, phone_number, location_id, edited, id),
        )
        return new_cur.fetchone()


def delete_organization_information(cursor: Cursor, id: str):
    """
    Deletes an organization_information record by ID.

    Args:
        cursor: Database cursor object.
        id: The ID of the organization to delete.

    Returns:
        The deleted organization_information record as a dictionary, or None if not found.
    """
    if not id:
        raise ValueError("Organization ID must be provided.")

    query = SQL("""
        DELETE FROM organization_information 
        WHERE id = %s
        RETURNING *;
    """)
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def query_organization_information(
    cursor: Cursor,
    name: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    location_id: str | UUID | None = None,
    edited: bool | None = None,
) -> list[dict]:
    """
    Queries organization information based on optional filter criteria.

    Args:
        cursor: Database cursor object.
        name: Optional name to filter organizations.
        website: Optional website URL.
        phone_number: Optional phone number.
        location_id: Optional location UUID (as string or UUID object).
        edited: Optional flag to filter edited organizations.

    Returns:
        A list of organization records matching the filter criteria, as dictionaries.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)
    if website is not None:
        conditions.append("website = %s")
        parameters.append(website)
    if phone_number is not None:
        conditions.append("phone_number = %s")
        parameters.append(phone_number)
    if location_id is not None:
        conditions.append("location_id = %s")
        parameters.append(location_id)
    if edited is not None:
        conditions.append("edited = %s")
        parameters.append(edited)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM organization_information{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()
