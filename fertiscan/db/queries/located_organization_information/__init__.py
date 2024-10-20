import json
from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row, tuple_row
from psycopg.sql import SQL


def create_located_organization_information(
    cursor: Cursor,
    name: str | None = None,
    address: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    edited: bool = False,
) -> UUID | None:
    """
    Inserts a new organization record with optional information.

    This function calls the `new_organization_info_located` database function to
    create a new organization record with the provided name, address, website,
    and phone number. At least one of these fields must be provided.

    Args:
        cursor (Cursor): The database cursor.
        name (str | None): The name of the organization. Optional.
        address (str | None): The address of the organization. Optional.
        website (str | None): The website URL of the organization. Optional.
        phone_number (str | None): The phone number of the organization. Optional.
        edited (bool): A flag indicating if the record has been edited. Defaults to False.

    Returns:
        UUID | None: The UUID of the new record, or None if the insertion fails.

    Raises:
        ValueError: If all input fields are None.
    """
    if all(v is None for v in (name, address, website, phone_number)):
        raise ValueError(
            "At least one of name, address, website, or phone_number must be provided."
        )

    query = SQL("SELECT new_organization_info_located(%s, %s, %s, %s, %s);")
    cursor.row_factory = tuple_row
    cursor.execute(query, (name, address, website, phone_number, edited))
    if result := cursor.fetchone():
        return result[0]


def read_located_organization_information(cursor: Cursor, id: str | UUID):
    """
    Retrieves a specific organization's information by ID.

    Args:
        cursor (Cursor): The database cursor.
        organization_id (str): The unique ID of the organization.

    Returns:
        dict | None: A dictionary with organization data or None if not found.
    """
    if not id:
        raise ValueError("Organization ID must be provided.")

    query = SQL("SELECT * FROM located_organization_information_view WHERE id = %s;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()


def read_all_located_organization_information(cursor: Cursor):
    """
    Retrieves all organization records from the view.

    Args:
        cursor (Cursor): The database cursor.

    Returns:
        list[dict]: A list of dictionaries representing all organizations.
    """
    query = SQL("SELECT * FROM located_organization_information_view;")
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query)
        return new_cur.fetchall()


def update_located_organization_information(
    cursor: Cursor,
    id: str | UUID,
    name: str | None = None,
    address: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    edited: bool = False,
):
    """
    Updates the information for a specific organization.

    Args:
        cursor (Cursor): The database cursor.
        id (str | UUID): The ID of the organization to update.
        name (str | None): Updated name. Optional.
        address (str | None): Updated address. Optional.
        website (str | None): Updated website. Optional.
        phone_number (str | None): Updated phone number. Optional.
        edited (bool): Whether the record has been edited. Default is False.

    Raises:
        ValueError: If the organization ID is not provided.
    """
    if not id:
        raise ValueError("Organization ID must be provided.")

    if all(v is None for v in (name, address, website, phone_number)):
        raise ValueError(
            "At least one of name, address, website, or phone_number must be provided."
        )

    return upsert_located_organization_information(
        cursor=cursor,
        id=id,
        name=name,
        address=address,
        website=website,
        phone_number=phone_number,
        edited=edited,
    )


def upsert_located_organization_information(
    cursor: Cursor,
    id: str | UUID | None = None,
    name: str | None = None,
    address: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
    edited: bool = False,
) -> UUID | None:
    """
    Inserts or updates organization data using the upsert pattern.

    If an ID is provided, it updates the corresponding record. If not, it creates a new one.

    Args:
        cursor (Cursor): The database cursor.
        id (str | UUID | None): The organization's ID. Optional.
        name (str | None): The name of the organization. Optional.
        address (str | None): The address. Optional.
        website (str | None): The website URL. Optional.
        phone_number (str | None): The phone number. Optional.
        edited (bool): Whether the record has been edited. Default is False.

    Returns:
        UUID | None: The UUID of the upserted record or None if unsuccessful.

    Raises:
        ValueError: If all input fields are None.
    """
    if all(v is None for v in (name, website, phone_number, address)):
        raise ValueError(
            "At least one of name, address, website, or phone_number must be provided."
        )

    if isinstance(id, UUID):
        id = str(id)

    input_org_info = {
        "id": id,
        "name": name,
        "website": website,
        "phone_number": phone_number,
        "address": address,
        "edited": edited,
    }

    query = SQL("SELECT upsert_organization_info(%s::jsonb);")
    cursor.row_factory = tuple_row
    cursor.execute(query, (json.dumps(input_org_info),))
    if result := cursor.fetchone():
        return result[0]


def query_located_organization_information(
    cursor: Cursor,
    name: str | None = None,
    address: str | None = None,
    website: str | None = None,
    phone_number: str | None = None,
):
    """
    Filters organization records based on optional criteria.

    Args:
        cursor (Cursor): The database cursor.
        name (str | None): Name filter. Optional.
        address (str | None): Address filter. Optional.
        website (str | None): Website filter. Optional.
        phone_number (str | None): Phone number filter. Optional.

    Returns:
        list[dict]: A list of dictionaries matching the criteria.
    """
    conditions = []
    parameters = []

    if name is not None:
        conditions.append("name = %s")
        parameters.append(name)
    if address is not None:
        conditions.append("address = %s")
        parameters.append(address)
    if website is not None:
        conditions.append("website = %s")
        parameters.append(website)
    if phone_number is not None:
        conditions.append("phone_number = %s")
        parameters.append(phone_number)

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
    query = SQL(f"SELECT * FROM located_organization_information_view{where_clause};")

    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, parameters)
        return new_cur.fetchall()


def delete_located_organization_information(cursor: Cursor, id: str | UUID):
    """
    Deletes an organization record by ID.

    Args:
        cursor (Cursor): The database cursor.
        id (str | UUID): The unique ID of the organization to delete.

    Returns:
        dict | None: A dictionary of the deleted record, or None if not found.

    Raises:
        ValueError: If the organization ID is not provided.
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
