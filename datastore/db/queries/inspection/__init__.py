"""
This module represent the function for the table inspection:

"""

import json
import uuid

from psycopg import Cursor, DatabaseError, Error, OperationalError
from psycopg.sql import SQL


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
                company_id,
                manufacturer_id,
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
                company_id,
                manufacturer_id,
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
                company_id,
                manufacturer_id,
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
    cursor: Cursor, inspection_id: str, user_id: str, updated_data: dict
) -> dict:
    """
    Update inspection data in the database.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str): UUID of the inspection to update.
    - user_id (str): UUID of the user performing the update.
    - updated_data (dict): Dictionary containing updated inspection data.

    Returns:
    - dict: A JSON object with updated inspection information.

    Raises:
    - InspectionUpdateError: Custom error for handling specific update issues.
    """
    try:
        # Validate and convert input IDs
        inspection_uuid = uuid.UUID(inspection_id)
        user_uuid = uuid.UUID(user_id)

        # Ensure updated_data is a valid dictionary
        if not isinstance(updated_data, dict):
            raise ValueError("Invalid data format: updated_data must be a dictionary")

        # Prepare and execute the SQL function call
        query = SQL("""SELECT update_inspection(%s, %s, %s)""")
        cursor.execute(
            query, (inspection_uuid, user_uuid, json.dumps(updated_data))
        )
        result = cursor.fetchone()

        if result is None:
            raise InspectionUpdateError(
                "Failed to update inspection. No data returned."
            )

        return result[0]

    except (
        Error,
        DatabaseError,
        OperationalError,
    ) as db_err:
        raise InspectionUpdateError(
            f"Database error occurred: {str(db_err)}"
        ) from db_err
    except (ValueError, TypeError) as val_err:
        raise InspectionUpdateError(f"Invalid input: {str(val_err)}") from val_err
    except Exception as ex:
        raise InspectionUpdateError(f"Unexpected error: {str(ex)}") from ex
