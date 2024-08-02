"""
This module represent the function for the table label_information
"""


def new_label_information(
    cursor,name, lot_number, npk, registration_number, n, p, k, company_info_id, manufacturer_info_id
):
    """
    This function create a new label_information in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - lot_number (str): The lot number of the label_information.
    - npk (str): The npk of the label_information.
    - registration_number (str): The registration number of the label_information.
    - n (float): The n of the label_information.
    - p (float): The p of the label_information.
    - k (float): The k of the label_information.
    - company_info_id (str): The UUID of the company.
    - manufacturer_info_id (str): The UUID of the manufacturer.

    Returns:
    - str: The UUID of the label_information
    """
    try:
        query = """
            INSERT INTO 
                label_information (
                    product_name,
                    lot_number, 
                    npk, 
                    registration_number, 
                    n, 
                    p, 
                    k,
                    company_info_id,
                    manufacturer_info_id
                    )
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s,%s,%s)
            RETURNING 
                id
            """
        cursor.execute(
            query,
            (
                name,
                lot_number,
                npk,
                registration_number,
                n,
                p,
                k,
                company_info_id,
                manufacturer_info_id,
            ),
        )
        return cursor.fetchone()[0]
    except Exception as e:
        raise e


def new_label_information_complete(
    cursor, lot_number, npk, registration_number, n, p, k, weight, density, volume
):
    ##TODO: Implement this function
    return None


def get_label_information(cursor, label_information_id):
    """
    This function get a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_information_id (str): The UUID of the label_information.

    Returns:
    - dict: The label_information
    """
    try:
        query = """
            SELECT 
                product_name,
                lot_number, 
                npk, 
                registration_number, 
                n, 
                p, 
                k, 
                company_info_id,
                manufacturer_info_id
            FROM 
                label_information
            WHERE 
                id = %s
            """
        cursor.execute(query, (label_information_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e
