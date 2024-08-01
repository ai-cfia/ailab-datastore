"""
This module represent the function for the table inspection:
    
"""


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
    cursor,
    inspection_id,
    verified=None,
    label_info_id=None,
    sample_id=None,
    picture_set_id=None,
    fertilizer_id=None,
):
    """
    This function updates the inspection in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.
    - verified (boolean, optional): The value if the inspection has been verified by the user. Default is None.
    - label_info_id (str, optional): The UUID of the label information. Default is None.
    - sample_id (str, optional): The UUID of the sample. Default is None.
    - picture_set_id (str, optional): The UUID of the picture set. Default is None.
    - fertilizer_id (str, optional): The UUID of the fertilizer. Default is None.

    Returns:
    - The UUID of the inspection.
    """

    try:
        query = """
            UPDATE inspection
            SET 
                verified = COALESCE(%s, verified),
                label_info_id = COALESCE(%s, label_info_id),
                sample_id = COALESCE(%s, sample_id),
                picture_set_id = COALESCE(%s, picture_set_id),
                fertilizer_id = COALESCE(%s, fertilizer_id),
                updated_at = CURRENT_TIMESTAMP
            WHERE 
                id = %s
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                verified,
                label_info_id,
                sample_id,
                picture_set_id,
                fertilizer_id,
                inspection_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise InspectionUpdateError(e.__str__())
