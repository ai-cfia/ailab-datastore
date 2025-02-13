"""
This module represent the function for the sub table of label_information

"""

from psycopg import Cursor
from uuid import UUID

from fertiscan.db.queries.errors import (
    SubLabelCreationError,
    SubLabelNotFoundError,
    SubLabelQueryError,
    SubLabelRetrievalError,
    SubLabelDeleteError,
    SubLabelUpdateError,
    SubTypeCreationError,
    SubTypeQueryError,
    handle_query_errors,
)


@handle_query_errors(SubLabelCreationError)
def new_sub_label(
    cursor: Cursor, text_fr, text_en, label_id, sub_type_id, edited=False
):
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
    query = """
        SELECT new_sub_label(%s, %s, %s, %s, %s);
    """
    cursor.execute(query, (text_fr, text_en, label_id, sub_type_id, edited))
    if result := cursor.fetchone():
        return result[0]
    raise SubLabelCreationError("Failed to create SubLabel. No data returned.")


@handle_query_errors(SubLabelRetrievalError)
def get_sub_label(cursor: Cursor, sub_label_id):
    """
    This function gets the sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - sub_label_id (uuid): The UUID of the sub label.

    Returns:
    - The sub label entity.
    """
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


@handle_query_errors(SubLabelQueryError)
def has_sub_label(cursor: Cursor, label_id):
    """
    This function checks if a label has sub label.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - True if the label has sub label, False otherwise.
    """
    query = """
        SELECT 
            Exists(
                SELECT 1
                FROM
                    sub_label
                WHERE
                    label_id = %s
                Limit 1
            );
    """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        return result[0]
    raise SubLabelQueryError(
        "Failed to check if label has sub label. No data returned."
    )


@handle_query_errors(SubLabelRetrievalError)
def get_sub_label_json(cursor: Cursor, label_id) -> dict:
    """
    This function gets all the sub label for a label in a json format.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - The sub label in dict format.
    """
    if not has_sub_label(cursor, label_id):
        return {
            "cautions": {"en": [], "fr": []},
            "instructions": {"en": [], "fr": []},
            "first_aid": {"en": [], "fr": []},
        }
    query = """
        SELECT get_sub_label_json(%s);
        """
    cursor.execute(query, (str(label_id),))
    if result := cursor.fetchone():
        return result[0]
    raise SubLabelNotFoundError("No sub label found for label_id: " + str(label_id))


@handle_query_errors(SubLabelRetrievalError)
def get_full_sub_label(cursor: Cursor, sub_label_id):
    """
    This function gets the full sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - sub_label_id (uuid): The UUID of the sub label.

    Returns:
    - The full sub label entity.
    """
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


@handle_query_errors(SubLabelRetrievalError)
def get_all_sub_label(cursor: Cursor, label_id):
    """
    This function gets all the sub label from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of sub label entity.
    """
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


@handle_query_errors(SubLabelUpdateError)
def update_sub_label(cursor: Cursor, sub_label_id, text_fr, text_en, edited=True):
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

handle_query_errors(SubLabelUpdateError)
def upsert_sub_label(cursor: Cursor, label_id: UUID, inspection_dict: dict):
    """
    Replaces all entries for a label by deleting existing ones and inserting new ones.
    
    Parameters:
    - cursor: Database cursor
    - label_id: UUID of the label to update
    - inspection_dict: Dictionary containing the new values to insert
    """
    # get the all the active sub_types
    sub_types = get_sub_types(cursor=cursor)

    delete_sub_label(cursor=cursor, label_id=label_id)

    for id, sub_type in sub_types:
        sub_label = inspection_dict[sub_type]
        fr_list = sub_label["fr"]
        en_list = sub_label["en"]
        max_length = max(len(fr_list), len(en_list))
        for i in range(0, max_length):
            if i >= len(fr_list):
                fr = None
                en = en_list[i]
            elif i >= len(en_list):
                fr = fr_list[i]
                en = None
            else:
                fr = fr_list[i]
                en = en_list[i]
            new_sub_label(
                cursor=cursor,
                text_fr=fr,
                text_en=en,
                label_id=label_id,
                sub_type_id=id,
                edited=True,
            )


handle_query_errors(SubLabelDeleteError)
def delete_sub_label(cursor: Cursor, label_id: UUID):
    """
    This function deletes all sub labels associated with a given label_id.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - None
    """
    query = """
        DELETE FROM 
            sub_label
        WHERE 
            label_id = %s
        RETURNING ID;
    """
    cursor.execute(query, (label_id,))
    return cursor.rowcount


@handle_query_errors(SubTypeCreationError)
def new_sub_type(cursor: Cursor, type_fr, type_en):
    """
    This function creates a new sub type in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - type_fr (str): The type in french.
    - type_en (str): The type in english.

    Returns:
    - The UUID of the new sub type.
    """
    query = """
        INSERT INTO 
            sub_type (type_fr, type_en)
        VALUES 
            (%s, %s)
        RETURNING 
            id
    """
    cursor.execute(query, (type_fr, type_en))
    if result := cursor.fetchone():
        return result[0]
    raise SubTypeCreationError("Failed to create SubType. No data returned.")


@handle_query_errors(SubTypeQueryError)
def get_sub_type_id(cursor: Cursor, type_name):
    """
    This function gets the sub type from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - type_name (str): The name of the sub type.

    Returns:
    - The UUID of the sub type.
    """
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
    if result := cursor.fetchone():
        return result[0]
    raise SubTypeQueryError("Failed to get the sub type id. No data returned.")


def get_sub_types(cursor: Cursor) -> list:
    """
    This function fetches all sub types names from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.

    Returns:
    - A list of Tuple of sub type names and ids (id,name_en).
    """
    query = """
        SELECT 
            id, type_en
        FROM 
            sub_type
    """
    cursor.execute(query)
    return cursor.fetchall()
