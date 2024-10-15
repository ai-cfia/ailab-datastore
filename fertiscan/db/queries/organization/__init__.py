"""
This module represent the function for the table organization and its children tables: [location, region, province]


"""

from uuid import UUID

from psycopg import Cursor
from psycopg.rows import dict_row


class OrganizationCreationError(Exception):
    pass


class OrganizationNotFoundError(Exception):
    pass


class OrganizationUpdateError(Exception):
    pass


def create_organization(cursor, information_id, location_id=None):
    """
    This function create a new organization in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.

    Returns:
    - str: The UUID of the organization
    """
    try:
        if location_id is None:
            query = """
                SELECT 
                    location_id
                FROM
                    organization_information
                WHERE
                    id = %s
                """
            cursor.execute(query, (information_id,))
            location_id = cursor.fetchone()[0]
        query = """
            INSERT INTO 
                organization (
                    information_id,
                    main_location_id 
                    )
            VALUES 
                (%s, %s)
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                information_id,
                location_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise OrganizationCreationError(
            "Datastore organization unhandeled error" + e.__str__()
        )


def update_organization(cursor, organization_id, information_id, location_id):
    """
    This function update a organization in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - organization_id (str): The UUID of the organization.
    - name (str): The name of the organization.
    - website (str): The website of the organization.
    - phone_number (str): The phone number of the organization.
    - location_id (str): The UUID of the location.

    Returns:
    - str: The UUID of the organization
    """
    try:
        query = """
            UPDATE 
                organization
            SET 
                information_id = COALESCE(%s,information_id),
                main_location_id = COALESCE(%s,main_location_id)
            WHERE 
                id = %s
            """
        cursor.execute(
            query,
            (
                information_id,
                location_id,
                organization_id,
            ),
        )
        return organization_id
    except Exception as e:
        raise OrganizationUpdateError(
            "Datastore organization unhandeled error" + e.__str__()
        )


def read_organization(cursor, organization_id):
    """
    This function get a organization from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - organization_id (str): The UUID of the organization.

    Returns:
    - dict: The organization
    """
    try:
        query = """
            SELECT 
                information_id,
                main_location_id 
            FROM 
                organization
            WHERE 
                id = %s
            """
        cursor.execute(query, (organization_id,))
        res = cursor.fetchone()
        if res is None:
            raise OrganizationNotFoundError
        return res
    except OrganizationNotFoundError:
        raise OrganizationNotFoundError(
            "organization not found with organization_id: " + organization_id
        )
    except Exception as e:
        raise Exception("Datastore organization unhandeled error" + e.__str__())


def read_full_organization(cursor: Cursor, id: str | UUID):
    """
    Retrieve full organization details from the database using the organization view.

    Parameters:
    - cursor (Cursor): The database cursor.
    - organization_id (str | UUID): The ID of the organization to retrieve.

    Returns:
    - dict | None: A dictionary with organization details or None if not found.
    """
    query = "SELECT * FROM full_organization_view WHERE id = %s"
    with cursor.connection.cursor(row_factory=dict_row) as new_cur:
        new_cur.execute(query, (id,))
        return new_cur.fetchone()
