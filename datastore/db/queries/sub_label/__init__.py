"""
This module represent the function for the sub table of label_information

"""


class SubLabelCreationError(Exception):
    pass


class SubLabelNotFoundError(Exception):
    pass


class SubTypeCreationError(Exception):
    pass


class SubTypeNotFoundError(Exception):
    pass


def new_sub_label(cursor, text_fr, text_en, label_id, sub_type_id, edited=False):
    """
    This function creates a new sub label in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - text_fr (str): The text in french.
    - text_en (str): The text in english.
    - label_id (uuid): The UUID of the label_information.
    - sub_type_id (uuid): The UUID of the sub_type.
    - edited (bool): The edited status of the sub label.

    Returns:
    - The UUID of the new sub label.
    """
    try:
        query = """
            SELECT new_sub_label(%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (text_fr, text_en, label_id, edited, sub_type_id))
        return cursor.fetchone()[0]
    except Exception:
        raise SubLabelCreationError("Error: could not create the sub label")


def get_sub_label(cursor, sub_label_id):
    """
    This function gets the sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - sub_label_id (uuid): The UUID of the sub label.

    Returns:
    - The sub label entity.
    """
    try:
        query = """
            SELECT 
                text_content_fr,
                text_content_en,
                edited,
                label_id,
                sub_type_id
            FROM 
                sub_label
            WHERE 
                id = %s
        """
        cursor.execute(query, (sub_label_id,))
        return cursor.fetchone()
    except Exception:
        raise SubLabelNotFoundError("Error: could not get the sub label")


def get_full_sub_label(cursor, sub_label_id):
    """
    This function gets the full sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - sub_label_id (uuid): The UUID of the sub label.

    Returns:
    - The full sub label entity.
    """
    try:
        query = """
            SELECT 
                sub_label.id,
                sub_label.text_content_fr,
                sub_label.text_content_en,
                sub_label.edited,
                sub_type.type_fr,
                sub_type.type_en
            FROM 
                sub_label
            JOIN 
                sub_type
            ON 
                sub_label.sub_type_id = sub_type.id
            WHERE 
                sub_label.id = %s
        """
        cursor.execute(query, (sub_label_id,))
        return cursor.fetchone()
    except Exception:
        raise SubLabelNotFoundError("Error: could not get the full sub label")


def get_all_sub_label(cursor, label_id):
    """
    This function gets all the sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of sub label entity.
    """
    try:
        query = """
            SELECT 
                sub_label.id,
                sub_label.text_content_fr,
                sub_label.text_content_en,
                sub_label.edited,
                sub_type.type_fr,
                sub_type.type_en
            FROM 
                sub_label
            JOIN
                sub_type
            ON
                sub_label.sub_type_id = sub_type.id
            WHERE 
                label_id = %s
            ORDER BY
                sub_type.type_en
        """
        cursor.execute(query, (label_id,))
        return cursor.fetchall()
    except Exception:
        raise SubLabelNotFoundError("Error: could not get the sub label")


def update_sub_label(cursor, sub_label_id, text_fr, text_en, edited=True):
    """
    This function updates the sub label in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - sub_label_id (uuid): The UUID of the sub label.
    - text_fr (str): The text in french.
    - text_en (str): The text in english.
    - edited (bool): The edited status of the sub label.

    Returns:
    - None
    """
    try:
        query = """
            UPDATE 
                sub_label
            SET 
                text_content_fr = %s,
                text_content_en = %s,
                edited = %s
            WHERE 
                id = %s
        """
        cursor.execute(query, (text_fr, text_en, edited, sub_label_id))
    except Exception:
        raise SubLabelNotFoundError("Error: could not update the sub label")


def new_sub_type(cursor, type_fr, type_en):
    """
    This function creates a new sub type in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - type_fr (str): The type in french.
    - type_en (str): The type in english.

    Returns:
    - The UUID of the new sub type.
    """
    try:
        query = """
            INSERT INTO 
                sub_type (type_fr, type_en)
            VALUES 
                (%s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (type_fr, type_en))
        return cursor.fetchone()[0]
    except Exception:
        raise SubTypeCreationError("Error: could not create the sub type")


def get_sub_type_id(cursor, type_name):
    """
    This function gets the sub type from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - type_name (str): The name of the sub type.

    Returns:
    - The UUID of the sub type.
    """
    try:
        query = """
            SELECT 
                id
            FROM 
                sub_type
            WHERE 
                type_fr ILIKE %s OR type_en ILIKE %s
        """
        cursor.execute(
            query,
            (
                type_name,
                type_name,
            ),
        )
        return cursor.fetchone()[0]
    except Exception:
        raise SubTypeNotFoundError("Error: could not get the sub type")
