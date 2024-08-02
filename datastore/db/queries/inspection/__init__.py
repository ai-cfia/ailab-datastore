"""
This module represent the function for the table inspection:

"""

import json
from uuid import UUID

from psycopg import Cursor, DatabaseError, Error, OperationalError
from psycopg.sql import SQL
from pydantic_core import ValidationError

from datastore.db.metadata.inspection import Inspection


class InspectionCreationError(Exception):
    pass


class InspectionUpdateError(Exception):
    pass


def new_inspection(cursor, user_id, picture_set_id, verified=False):
    """
    This function uploads a new inspection to the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.
    - picture_set_id (str): The UUID of the picture set.
    - verified (boolean, optional): The value if the inspection has been verified by the user. Default is False.

    Returns:
    - The UUID of the inspection.
    """

    try:
        query = """
            INSERT INTO inspection (
                inspector_id,
                picture_set_id,
                verified)
            VALUES 
                (%s, %s, %s)
            RETURNING 
                id
            """
        cursor.execute(query, (user_id, picture_set_id, verified))
        return cursor.fetchone()[0]
    except Exception:
        raise InspectionCreationError("Datastore inspection unhandeled error")


def new_inspection_with_label_info(cursor, user_id, picture_set_id, label_json):
    """
    This function calls the new_inspection function within the database and adds the label information to the inspection.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.
    - picture_set_id (str): The UUID of the picture set.
    - label_json (str): The label information in a json format.
    - verified (boolean, optional): The value if the inspection has been verified by the user. Default is False.

    Returns:
    - The json with ids of the inspection and the label information.
    """
    try:
        query = """
            SELECT new_inspection(%s, %s, %s)
            """
        cursor.execute(query, (user_id, picture_set_id, label_json))
        return cursor.fetchone()[0]
    except Exception as e:
        raise InspectionCreationError(e.__str__())


def is_inspection_verified(cursor, inspection_id):
    """
    This function checks if the inspection has been verified.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The value if the inspection has been verified.
    """

    try:
        query = """
            SELECT 
                verified
            FROM 
                inspection
            WHERE 
                id = %s
            """
        cursor.execute(query, (inspection_id,))
        return cursor.fetchone()[0]
    except Exception as e:
        raise Exception("Datastore inspection unhandeled error" + e.__str__())


def get_inspection(cursor, inspection_id):
    """
    This function gets the inspection from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The inspection.
    """

    try:
        query = """
            SELECT 
                verified,
                upload_date,
                updated_at,
                inspector_id,
                label_info_id,
                sample_id,
                picture_set_id,
                fertilizer_id
            FROM 
                inspection
            WHERE 
                id = %s
            """
        cursor.execute(query, (inspection_id,))
        return cursor.fetchone()
    except Exception as e:
        raise Exception("Datastore inspection unhandeled error" + e.__str__())
    
def get_all_user_unverified_inspection(cursor, user_id):
    """
    This function gets all the unverified inspection of a user from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.

    Returns:
    - The inspection.
    """

    try:
        query = """
            SELECT 
                inspection.id,
                inspection.upload_date,
                inspection.updated_at,
                inspection.sample_id,
                inspection.picture_set_id,
                label_info.id as label_info_id,
                label_info.product_name,
                label_info.company_info_id,
                label_info.manufacturer_info_id
            FROM 
                inspection
            LEFT JOIN 
                label_information as label_info
            ON
                inspection.label_info_id = label_information.id
            WHERE 
                inspector_id = %s AND verified = FALSE
            """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore inspection unhandeled error" + e.__str__())


def get_all_user_inspection(cursor, user_id):
    """
    This function gets all the inspection of a user from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.

    Returns:
    - The inspection.
    """

    try:
        query = """
            SELECT 
                id,
                verified,
                upload_date,
                updated_at,
                label_info_id,
                sample_id,
                picture_set_id,
                fertilizer_id
            FROM 
                inspection
            WHERE 
                inspector_id = %s
            """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore inspection unhandeled error" + e.__str__())

# Deprecated
def get_all_organization_inspection(cursor, org_id):
    """
    This function gets all the inspection of an organization from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - The inspection.
    """

    try:
        query = """
            SELECT 
                id,
                verified,
                upload_date,
                updated_at,
                inspector_id,
                label_info_id,
                sample_id,
                picture_set_id,
                fertilizer_id
            FROM 
                inspection
            WHERE 
                company_id = %s OR manufacturer_id = %s
            """
        cursor.execute(query, (org_id, org_id))
        return cursor.fetchall()
    except Exception as e:
        raise Exception("Datastore inspection unhandeled error" + e.__str__())


def update_inspection(
    cursor: Cursor,
    inspection_id: str | UUID,
    user_id: str | UUID,
    updated_data: Inspection,
) -> Inspection:
    """
    Update inspection data in the database.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str | UUID): UUID of the inspection to update.
    - user_id (str | UUID): UUID of the user performing the update.
    - updated_data (Inspection): Updated inspection data as an Inspection object.

    Returns:
    - Inspection: An Inspection object with updated inspection information.

    Raises:
    - InspectionUpdateError: Custom error for handling specific update issues.
    """
    try:
        updated_data_dict = updated_data.model_dump()

        # Prepare and execute the SQL function call
        query = SQL("SELECT update_inspection(%s, %s, %s)")
        cursor.execute(query, (inspection_id, user_id, json.dumps(updated_data_dict)))
        result = cursor.fetchone()

        if result is None:
            raise InspectionUpdateError(
                "Failed to update inspection. No data returned."
            )

        # Convert the JSON result back to an Inspection object
        return Inspection.model_validate(result[0])

    except (Error, DatabaseError, OperationalError) as e:
        raise InspectionUpdateError(f"Database error occurred: {str(e)}") from e
    except ValidationError as e:
        raise InspectionUpdateError(f"Validation failed: {str(e)}") from e
    except (ValueError, TypeError) as e:
        raise InspectionUpdateError(f"Invalid input: {str(e)}") from e
    except Exception as e:
        raise InspectionUpdateError(f"Unexpected error: {str(e)}") from e
