"""
This module represent the function for the table micronutrient, guaranteed and its children element_compound:

    CREATE TABLE "fertiscan_0.0.6"."label_information" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "lot_number" text,
    "npk" text,
    "registration_number" text,
    "n" float,
    "p" float,
    "k" float,
    "weight" uuid REFERENCES "fertiscan_0.0.6".metric(id),
    "density" uuid REFERENCES "fertiscan_0.0.6".metric(id),
    "volume" uuid REFERENCES "fertiscan_0.0.6".metric(id),
    );

"""

def new_label_information(cursor, lot_number, npk, registration_number, n, p, k, weight, density, volume):
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
    - weight (uuid): The weight of the label_information.
    - density (uuid): The density of the label_information.
    - volume (uuid): The volume of the label_information.

    Returns:
    - str: The UUID of the label_information
    """
    try:
        query = """
            INSERT INTO 
                label_information (
                    lot_number, 
                    npk, 
                    registration_number, 
                    n, 
                    p, 
                    k 
                    )
            VALUES 
                (%s, %s, %s, %s, %s, %s)
            RETURNING 
                id
            """
        cursor.execute(query, (lot_number, npk, registration_number, n, p, k,))
        return cursor.fetchone()[0]
    except Exception as e:
        raise e

def new_label_information_complete(cursor,lot_number, npk, registration_number, n, p, k, weight, density, volume):
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
                lot_number, 
                npk, 
                registration_number, 
                n, 
                p, 
                k, 
                weight, 
                density, 
                volume
            FROM 
                label_information
            WHERE 
                id = %s
            """
        cursor.execute(query, (label_information_id,))
        return cursor.fetchone()
    except Exception as e:
        raise e