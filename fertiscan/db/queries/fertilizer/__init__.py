

from uuid import UUID
from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL

from fertiscan.db.queries.errors import (
    FertilizerUpsertError,
    FertilizerQueryError,
    handle_query_errors,
)

handle_query_errors(FertilizerUpsertError)
def upsert_fertilizer(cursor: Cursor, name: str, reg_number:str, org_owner_id:UUID,latest_inspection_id: UUID):
    """
    This function Inserts data for a Fertilizer based on its name.
    If a Fertilizer is already named as such we update the latest inspection FK.

    Parameters:
        cursor (Cursor): 
        name (str): 
        reg_number (str): 
        org_owner_id (UUID): 
        latest_inspection_id (UUID): 
    
    Returns:
        - Fertilizer id (uuid)
    """
    query = """
    INSERT INTO 
        fertilizer (
            name, 
            registration_number, 
            upload_date, 
            update_at, 
            main_contact_id, 
            latest_inspection_id)
    VALUES (
        %s,
        %s,
        CURRENT_TIMESTAMP,  -- Set upload date to current timestamp
        CURRENT_TIMESTAMP,  -- Set update date to current timestamp
        %s,
        %s
    )
    ON CONFLICT (name) DO UPDATE
    SET
        registration_number = EXCLUDED.registration_number,
        update_at = CURRENT_TIMESTAMP,  -- Update the update_at timestamp
        main_contact_id = EXCLUDED.main_contact_id,
        latest_inspection_id = EXCLUDED.latest_inspection_id
    RETURNING id;
    """
    cursor.execute(query,(name,reg_number,org_owner_id,latest_inspection_id,))
    return cursor.fetchone()[0]


def search_fertilizer(cursor: Cursor, fertilizer_name:str, registration_number: str, lower_bound_date: Date, upper_bound_date: Date, lot_number:str, org_ids:list[UUID]):
    """
    Find all inspections where the organization is listed as main contact.

    Parameters:
    - cursor (Cursor): Database cursor
    - org_ids (list[UUID]): List of organization IDs to search for

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
            f.id as fertilizer_id,
            f.name as fertilizer_name,
            f.registration_number as registration_number,
            f.main_contact_id as organization,
            o.name as organization_name,
            o.phone_number as organization_phone_number,
            o.address as organization_email,
            l.lot_number as lot_number,
            l.title_is_minimal as is_minimal_guaranteed_analysis,
            l.record_keeping as is_record_keeping
        FROM 
            fertilizer f
        JOIN 
            inspection i ON f.latest_inspection_id = i.id
        JOIN 
            organization o ON f.main_contact_id = o.id
        JOIN
            label_information l ON i.label_info_id = l.id
    """
    first = True
    # check if all parameters are not none
    if ((org_ids is None or len(org_ids) < 1) and 
        (fertilizer_name is None or fertilizer_name.strip() == "") and
        (registration_number is None or registration_number.strip() == "") and 
        (lower_bound_date is None) and
        (upper_bound_date is None) and
        (lot_number is None or lot_number.strip() == "")
    ):
        raise FertilizerQueryError("No search parameters provided, please provide at least one search parameter.")
    if org_ids is not None and len(org_ids) > 0:
        query += "WHERE o.id = ANY(%s)"
        if first:
            first = False
    if fertilizer_name is not None and fertilizer_name.strip() != "":
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "f.name = %s"
        first = False
    if registration_number is not None and registration_number.strip() != "":
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "f.registration_number = %s"
        first = False
    if lower_bound_date is not None:
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "i.upload_date >= %s"
        first = False
    if upper_bound_date is not None:
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "i.upload_date <= %s"
        first = False
    if lot_number is not None and lot_number.strip() != "":
        if first:
            query += "WHERE "
        else:
            query += "AND "
        query += "l.lot_number = %s"
        first = False
    query += ";"
    
    cursor.execute(query, (org_ids,))
    return cursor.fetchall()
