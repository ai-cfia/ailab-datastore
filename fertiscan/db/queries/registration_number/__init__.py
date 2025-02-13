"""
This module represent the function for the registration_number_information table

"""

from psycopg import Cursor, sql
from uuid import UUID

from fertiscan.db.queries.errors import (
    RegistrationNumberCreationError,
    RegistrationNumberNotFoundError,
    RegistrationNumberQueryError,
    RegistrationNumberRetrievalError,
    handle_query_errors,
)


@handle_query_errors(RegistrationNumberCreationError)
def new_registration_number(
    cursor: Cursor,
    registration_number,
    label_id: UUID,
    is_an_ingredient: bool,
    read_name: str = None,
    edited=False,
):
    """
    This function creates a new registration_number in the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - registration_number (str): The registration number of the product.
    - label_id (uuid): The UUID of the label_information.
    - is_an_ingredient (bool): The status of the registration number.
    - edited (bool): The edited status of the registration number.
    Returns:
    - The UUID of the new registration number.
    """
    query = sql.SQL(
        """
        SELECT new_registration_number(%s, %s, %s, %s, %s);
    """
    )
    cursor.execute(
        query, (registration_number, label_id, is_an_ingredient, read_name, edited)
    )
    if result := cursor.fetchone():
        return result[0]
    raise RegistrationNumberCreationError(
        "Failed to create Registration Number. No data returned."
    )


@handle_query_errors(RegistrationNumberRetrievalError)
def get_registration_numbers_json(cursor: Cursor, label_id: UUID):
    """
    This function gets the registration numbers from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - The registration numbers of the label.
    """
    query = sql.SQL(
        """
        SELECT get_registration_numbers_json(%s);
    """
    )
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        return result[0]
    raise RegistrationNumberRetrievalError(
        "Failed to get Registration Numbers with the given label_id. No data returned."
    )


@handle_query_errors(RegistrationNumberQueryError)
def update_registration_number(
    cursor: Cursor,
    registration_numbers,
    label_id: UUID,
):
    """
    This function updates the registration number in the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - registration_number_id (uuid): The UUID of the registration number.
    - registration_number (str): The registration number of the product.
    - is_an_ingredient (bool): The status of the registration number.
    - edited (bool): The edited status of the registration number.
    Returns:
    - The UUID of the updated registration number.
    """
    query = sql.SQL(
        """
        SELECT update_registration_number(%s, %s);
    """
    )
    cursor.execute(
        query,
        (
            label_id,
            registration_numbers,
        ),
    )
    if result := cursor.fetchone():
        return result[0]
    raise RegistrationNumberQueryError(
        "Failed to update Registration Number. No data returned."
    )


def get_registration_numbers_from_label(cursor: Cursor, label_id: UUID):
    """
    This function gets the registration numbers from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - The registration numbers of the label.
    """
    query = sql.SQL(
        """
        SELECT 
            identifier,
            is_an_ingredient,
            name,
            edited
        FROM registration_number_information
        WHERE label_id = %s;
    """
    )
    cursor.execute(query, (label_id,))
    result = cursor.fetchall()
    if result:
        return result
    raise RegistrationNumberNotFoundError(
        f"Failed to get Registration Numbers with the given label_id {label_id}. No data returned."
    )

def delete_registration_numbers(cursor: Cursor, label_id : UUID):
    """
    This function deletes the registration numbers from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    """
    query = sql.SQL(
        """
        DELETE FROM registration_number_information
        WHERE label_id = %s;
    """
    )
    cursor.execute(query, (label_id,))
    if cursor.rowcount == 0:
        raise RegistrationNumberQueryError(
            f"Failed to delete Registration Numbers with the given label_id {label_id}. No rows affected."
        )
    else:
        return cursor.rowcount
    
def upsert_registration_numbers(cursor: Cursor, label_id: UUID, reg_numbers:dict):
    """
    Replaces all entries for a label by deleting existing ones and inserting new ones.
    
    Parameters:
    - cursor: Database cursor
    - label_id: UUID of the label to update
    - reg_numbers: Dictionary containing the new values to insert
    """
    delete_registration_numbers(cursor=cursor,label_id=label_id)
    
    for record in reg_numbers:
        new_registration_number(
            cursor=cursor,
            registration_number=record.registration_number,
            label_id=label_id,
            is_an_ingredient=record.is_an_ingredient,
            read_name=None,
            edited=True
        )
