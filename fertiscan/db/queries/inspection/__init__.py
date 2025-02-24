"""
This module represent the function for the table inspection:

"""

import json
from uuid import UUID
from datetime import date as Date

from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL

from fertiscan.db.queries.errors import (
    InspectionCreationError,
    InspectionDeleteError,
    InspectionNotFoundError,
    InspectionQueryError,
    InspectionRetrievalError,
    InspectionUpdateError,
    handle_query_errors,
)


@handle_query_errors(InspectionCreationError)
def new_inspection(cursor: Cursor, user_id, picture_set_id, label_id,container_id,verified=False):
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

    query = """
        INSERT INTO inspection (
            inspector_id,
            picture_set_id,
            verified,
            label_info_id,
            container_id
            )
        VALUES 
            (%s, %s, %s,%s,%s)
        RETURNING 
            id
        """
    cursor.execute(query, (user_id, picture_set_id, verified,label_id,container_id))
    if result := cursor.fetchone():
        return result[0]
    raise InspectionCreationError("Failed to create inspection. No data returned.")

def save_inspection_original_dataset(cursor: Cursor, inspection_id:UUID,og_data):
    query = """
        UPDATE 
            "fertiscan_0.1.1".inspection_factual
	    SET 
            original_dataset = %s
	    WHERE 
            inspection_factual."inspection_id" = %s;
    """
    cursor.execute(query,(og_data,inspection_id))

@handle_query_errors(InspectionCreationError)
def new_inspection_with_label_info(cursor: Cursor, user_id, picture_set_id, label_json):
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
    query = """
        SELECT new_inspection(%s, %s, %s)
        """
    cursor.execute(query, (user_id, picture_set_id, label_json))
    return cursor.fetchone()[0]


@handle_query_errors(InspectionQueryError)
def is_a_inspection_id(cursor: Cursor, inspection_id) -> bool:
    """
    This function checks if the inspection exists in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The value if the inspection exists.
    """

    query = """
        SELECT 
            EXISTS(
                SELECT 
                    1
                FROM 
                    inspection
                WHERE 
                    id = %s
            )
        """
    cursor.execute(query, (inspection_id,))
    return cursor.fetchone()[0]


@handle_query_errors(InspectionQueryError)
def is_inspection_verified(cursor: Cursor, inspection_id):
    """
    This function checks if the inspection has been verified.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The value if the inspection has been verified.
    """

    query = """
        SELECT 
            verified
        FROM 
            inspection
        WHERE 
            id = %s
        """
    cursor.execute(query, (inspection_id,))
    if result := cursor.fetchone():
        return result[0]
    raise InspectionNotFoundError(
        "Failed to check inspection verification status. No data returned."
    )


VERIFIED = 0
UPLOAD_DATE = 1
UPDATED_AT = 2
INSPECTOR_ID = 3
LABEL_INFO_ID = 4
SAMPLE_ID = 5
PICTURE_SET_ID = 6
FERTILIZER_ID = 7
INSPECTION_COMMENT = 8


@handle_query_errors(InspectionRetrievalError)
def get_inspection(cursor: Cursor, inspection_id):
    """
    This function gets the inspection from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The inspection.
    """

    query = """
        SELECT 
            verified,
            upload_date,
            updated_at,
            inspector_id,
            label_info_id,
            sample_id,
            picture_set_id,
            fertilizer_id,
            inspection_comment
        FROM 
            inspection
        WHERE 
            id = %s
        """
    cursor.execute(query, (inspection_id,))
    return cursor.fetchone()


@handle_query_errors(InspectionRetrievalError)
def get_inspection_dict(cursor: Cursor, inspection_id: str | UUID):
    """
    This function fetches the inspection by its ID from the database.

    Parameters:
    - cursor (Cursor): The database cursor.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The inspection as a dictionary, or None if no record is found.
    """
    with cursor.connection.cursor(row_factory=dict_row) as dict_cursor:
        query = SQL("SELECT * FROM inspection WHERE id = %s")
        dict_cursor.execute(query, (inspection_id,))
        return dict_cursor.fetchone()


@handle_query_errors(InspectionQueryError)
def get_inspection_original_dataset(cursor: Cursor, inspection_id):
    """
    This function gets the inspection from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The inspection.
    """

    query = """
        SELECT 
            original_dataset
        FROM 
            inspection_factial
        WHERE 
            inspection_id = %s
        """
    cursor.execute(query, (inspection_id,))
    return cursor.fetchone()


@handle_query_errors(InspectionQueryError)
def get_inspection_fk(cursor: Cursor, inspection_id):
    """
    This function gets the foreign keys of the inspection from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The foreign keys of the inspection.
    [
        label_info_id,
        inspector_id,
        picture_set_id,
        container_id,
        fertilizer_id,
        sample_id
    ]
    """

    query = """
        SELECT 
            inspection.label_info_id,
            inspection.inspector_id,
            inspection.picture_set_id,
            inspection.container_id,
            inspection.fertilizer_id,
            inspection.sample_id
        FROM 
            inspection
        WHERE 
            inspection.id = %s
        """
    cursor.execute(query, (inspection_id,))
    return cursor.fetchone()


@handle_query_errors(InspectionRetrievalError)
def get_all_user_inspection_filter_verified(cursor: Cursor, user_id, verified: bool):
    """
    This function gets all the unverified inspection of a user from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.

    Returns:
    - The inspection.
    """

    query = """
        SELECT 
            inspection.id as inspection_id,
            inspection.upload_date as upload_date,
            inspection.updated_at as updated_at,
            inspection.sample_id as sample_id,
            inspection.picture_set_id as picture_set_id,
            label_info.id as label_info_id,
            label_info.product_name as product_name,
            company_info.id as company_info_id,
            company_info.name as company_name,
            inspection.verified as verified
        FROM 
            inspection
        LEFT JOIN 
            label_information as label_info
        ON
            inspection.label_info_id = label_info.id
        LEFT JOIN
            organization_information as company_info
        ON
            label_info.id = company_info.label_id AND company_info.is_main_contact = TRUE
        WHERE 
            inspection.inspector_id = %s AND inspection.verified = %s
        """
    cursor.execute(query, (user_id, verified))
    return cursor.fetchall()


@handle_query_errors(InspectionRetrievalError)
def get_all_user_inspection(cursor: Cursor, user_id):
    """
    This function gets all the inspection of a user from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - user_id (str): The UUID of the user.

    Returns:
    - The inspection.
    """

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


# Deprecated
@handle_query_errors(InspectionRetrievalError)
def get_all_organization_inspection(cursor: Cursor, org_id):
    """
    This function gets all the inspection of an organization from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - org_id (str): The UUID of the organization.

    Returns:
    - The inspection.
    """

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

def update_inspection(
    cursor: Cursor,
    inspection_id: str | UUID,
    verified: bool,
    inspection_comment:str
):
    if verified:
        query = """
            UPDATE
                inspection
            SET
                verified = %s,
                updated_at = CURRENT_TIMESTAMP,
                inspection_comment = %s,
                verified_date = CURRENT_TIMESTAMP
            WHERE
                id = %s;
        """
    else:
            query = """
            UPDATE
                inspection
            SET
                verified = %s,
                updated_at = CURRENT_TIMESTAMP,
                inspection_comment = %s
            WHERE
                id = %s;
        """
    cursor.execute(query, (verified,inspection_comment,inspection_id))


@handle_query_errors(InspectionUpdateError)
def update_inspection_function(
    cursor: Cursor,
    inspection_id: str | UUID,
    user_id: str | UUID,
    updated_data_dict
) -> dict:
    """
    Update inspection data in the database.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str | UUID): UUID or string of the inspection to update.
    - user_id (str | UUID): UUID or string of the user performing the update.
    - updated_data_dict (dict): Dictionary containing the updated inspection data.

    Returns:
    - dict: A dictionary containing the updated inspection information.

    Raises:
    - InspectionUpdateError: Custom error for handling specific update issues.
    """
    # Prepare and execute the SQL function call
    query = SQL("SELECT update_inspection(%s, %s, %s)")
    cursor.execute(query, (inspection_id, user_id, updated_data_dict))

    if result := cursor.fetchone():
        return result[0]
    raise InspectionUpdateError("Failed to update inspection. No data returned.")


@handle_query_errors(InspectionDeleteError)
def delete_inspection(
    cursor: Cursor,
    inspection_id: str | UUID,
    user_id: str | UUID,
):
    """
    Delete an inspection from the database and return the deleted inspection record.

    Parameters:
    - cursor (Cursor): Database cursor for executing queries.
    - inspection_id (str | UUID): UUID of the inspection to delete.
    - user_id (str | UUID): UUID of the user performing the deletion.

    Returns:
    - DBInspection: A DBInspection object representing the deleted inspection.

    Raises:
    - InspectionDeleteError: Custom error for handling specific delete issues.
    """
    query = SQL("SELECT delete_inspection(%s, %s);")
    cursor.execute(query, (inspection_id, user_id))

    if result := cursor.fetchone():
        return result[0]
    raise InspectionDeleteError("Failed to delete inspection. No data returned.")


@handle_query_errors(InspectionQueryError)
def get_inspection_factual(cursor: Cursor, inspection_id):
    """
    This function gets the inspection from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - inspection_id (str): The UUID of the inspection.

    Returns:
    - The inspection.
    """
    if not is_a_inspection_id(cursor, inspection_id):
        raise InspectionNotFoundError(f"Inspection with id {inspection_id} not found")
    query = """
        SELECT 
            inspection_id,
            inspector_id,
            label_info_id,
            time_id,
            sample_id,
            company_id,
            manufacturer_id,
            picture_set_id
        FROM 
            inspection_factual
        WHERE 
            inspection_id = %s
        """
    cursor.execute(query, (inspection_id,))
    return cursor.fetchone()

def search_inspection(cursor: Cursor, fertilizer_name:str, lower_bound_date: Date, upper_bound_date: Date, lot_number:str, label_ids:list[UUID]) -> list:
    """
    Find all inspections where the organization is listed as main contact.

    Parameters:
    - cursor (Cursor): Database cursor
    - fertilizer_name (str): The name of the fertilizer
    - lower_bound_date (Date): The lower bound date of the inspection
    - upper_bound_date (Date): The upper bound date of the inspection
    - lot_number (str): The lot number of the fertilizer
    - label_ids (list[UUID]): The list of label IDs to search also search for regarless of other parameters
    
    Returns:
    - list: List of tuples containing inspection data
    """
    query = """
        SELECT 
            i.id as inspection_id,
            i.verified as verified,
            i.upload_date as upload_date,
            i.updated_at as last_updated_at,
            i.inspector_id as inspector_id,
            i.label_info_id as label_info_id,
            i.container_id as container_id,
            i.picture_set_id as foldeer_id,
            i.inspection_comment as inspection_comment,
            i.verified_date as verified_date,
            l.product_name as fertilizer_name,
            o.id as organization_info_id,
            o.name as organization_name,
            o.phone_number as organization_phone_number,
            o.address as organization_email,
            l.lot_number as lot_number,
            l.title_is_minimal as is_minimal_guaranteed_analysis,
            l.record_keeping as is_record_keeping,
            r.identifier as registration_number
        FROM 
            inspection i
        JOIN
            label_information l ON i.label_info_id = l.id
        JOIN
            organization_information o ON l.id = o.label_id AND o.is_main_contact = TRUE
        JOIN
            registration_number_information r ON l.id = r.label_id 
    """
    first = True
    params = ()
    # check if all parameters are not none
    if ((fertilizer_name is None or fertilizer_name.strip() == "") and
        (lower_bound_date is None) and
        (upper_bound_date is None) and
        (lot_number is None or lot_number.strip() == "") and
        (label_ids is None or len(label_ids) < 1)
    ):
        raise InspectionQueryError("No search parameters provided, please provide at least one search parameter.")
    if fertilizer_name is not None and fertilizer_name.strip() != "":
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "l.product_name = %s "
        first = False
        params += (fertilizer_name,)
    if lower_bound_date is not None:
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "i.upload_date >= %s "
        first = False
        params += (lower_bound_date,)
    if upper_bound_date is not None:
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "i.upload_date <= %s "
        first = False
        params += (upper_bound_date,)
    if lot_number is not None and lot_number.strip() != "":
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "l.lot_number = %s "
        first = False
        params += (lot_number,)
    if label_ids is not None and len(label_ids) > 0:
        if first:
            query += "WHERE " # This is a list for previous conditions that were met
        else:
            query += "OR "
        query += "l.id = ANY(%s) "
        first = False
        params += (label_ids,)
        
    # Aggregate the Registration Numbers
    query += """ 
        GROUP BY 
            i.id,
            i.verified,
            i.upload_date,
            i.updated_at,
            i.inspector_id,
            i.label_info_id,
            i.container_id,
            i.picture_set_id,
            i.inspection_comment,
            i.verified_date,
            l.product_name,
            o.id,
            o.name,
            o.phone_number,
            o.address,
            l.lot_number,
            l.title_is_minimal,
            l.record_keeping
        """
    query += ";"
    cursor.execute(query, params)
    return cursor.fetchall()

