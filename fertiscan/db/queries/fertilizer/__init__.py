

from uuid import UUID
from psycopg import Cursor
from psycopg.rows import dict_row
from psycopg.sql import SQL

from fertiscan.db.queries.errors import (
    FertilizerUpsertError,
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
