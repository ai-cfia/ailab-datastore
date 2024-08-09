"""
This module represent the function for the table micronutrient, guaranteed and its children element_compound:

"""


class ElementCreationError(Exception):
    pass


class ElementNotFoundError(Exception):
    pass


class MicronutrientCreationError(Exception):
    pass


class MicronutrientNotFoundError(Exception):
    pass


class GuaranteedCreationError(Exception):
    pass


class GuaranteedNotFoundError(Exception):
    pass


def new_element(cursor, number, name_fr, name_en, symbol):
    """
    This function add a new element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - number (int): The number of the element.
    - name_fr (str): The name of the element in French.
    - name_en (str): The name of the element in English.
    - symbol (str): The symbol of the element.

    Returns:
    - str: The UUID of the element.
    """

    try:
        query = """
            INSERT INTO element_compound (number,name_fr,name_en,symbol)
            VALUES (%s,%s,%s,%s)
            RETURNING id
            """
        cursor.execute(query, (number, name_fr, name_en, symbol))
        return cursor.fetchone()[0]
    except Exception:
        raise ElementCreationError


def get_element_id_full_search(cursor, name):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the element.

    Returns:
    - str: The UUID of the element.
    """

    try:
        query = """
            SELECT id
            FROM element_compound
            WHERE name_fr ILIKE %s OR name_en ILIKE %s OR symbol = %s
            """
        cursor.execute(query, (name, name, name))
        return cursor.fetchone()[0]
    except Exception:
        raise ElementNotFoundError


def get_element_id_name(cursor, name):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the element.

    Returns:
    - str: The UUID of the element.
    """

    try:
        query = """
            SELECT 
                id
            FROM 
                element_compound
            WHERE 
                name_fr = %s OR 
                name_en = %s
            """
        cursor.execute(query, (name, name))
        return cursor.fetchone()[0]
    except Exception:
        raise ElementNotFoundError


def get_element_id_symbol(cursor, symbol):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - symbol (str): The symbol of the element.

    Returns:
    - str: The UUID of the element.
    """

    try:
        query = """
            SELECT 
                id
            FROM 
                element_compound
            WHERE 
                symbol ILIKE %s
            """
        cursor.execute(query, (symbol,))
        return cursor.fetchone()[0]
    except Exception:
        raise ElementNotFoundError


def new_micronutrient(
    cursor, read_name:str, value:float, unit:str,  label_id,language:str, edited=False
):
    """
    This function add a new micronutrient in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - read_name (str): The name of the micronutrient.
    - value (float): The value of the micronutrient.
    - unit (str): The unit of the micronutrient.
    - element_id (int): The element of the micronutrient.
    - label_id (str): The label of the micronutrient.

    Returns:
    - str: The UUID of the micronutrient.
    """

    try:
        if language.lower() not in ['fr','en']:
            raise MicronutrientCreationError('Language not supported')
        query = """
            SELECT new_micronutrient(%s, %s, %s, %s, %s, %s,%s);
            """
        cursor.execute(query, (read_name, value, unit, label_id, language,edited))
        return cursor.fetchone()[0]
    except Exception:
        raise MicronutrientCreationError


def get_micronutrient(cursor, micronutrient_id):
    """
    This function get the micronutrient in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - micronutrient_id (str): The UUID of the micronutrient.

    Returns:
    - str: The UUID of the micronutrient.
    """

    try:
        query = """
            SELECT 
                read_name,
                value,
                unit,
                element_id,
                edited,
                language,
                CONCAT(CAST(read_name AS TEXT),' ',value,' ', unit) AS reading
            FROM 
                micronutrient
            WHERE 
                id = %s
            """
        cursor.execute(query, (micronutrient_id,))
        return cursor.fetchone()
    except Exception:
        raise MicronutrientNotFoundError


def get_full_micronutrient(cursor, micronutrient_id):
    """
    This function get the micronutrient in the database with the element.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - micronutrient_id (str): The UUID of the micronutrient.

    """

    try:
        query = """
            SELECT 
                m.read_name,
                m.value,
                m.unit,
                ec.name_fr,
                ec.name_en,
                ec.symbol,
                m.edited,
                m.language,
                CONCAT(CAST(m.read_name AS TEXT),' ',m.value,' ', m.unit) AS reading
            FROM 
                micronutrient m
            JOIN 
                element_compound ec ON m.element_id = ec.id
            WHERE 
                m.id = %s
            """
        cursor.execute(query, (micronutrient_id,))
        return cursor.fetchone()
    except Exception:
        raise MicronutrientNotFoundError


def get_all_micronutrients(cursor, label_id):
    """
    This function get all the micronutrients in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - str: The UUID of the micronutrient.
    """

    try:
        query = """
            SELECT 
                m.id,
                m.read_name,
                m.value,
                m.unit,
                ec.name_fr,
                ec.name_en,
                ec.symbol,
                m.edited,
                m.language,
                CONCAT(CAST(m.read_name AS TEXT),' ',m.value,' ', m.unit) AS reading
            FROM 
                micronutrient m
            JOIN 
                element_compound ec ON m.element_id = ec.id
            WHERE 
                m.label_id = %s
            """
        cursor.execute(query, (label_id,))
        return cursor.fetchall()
    except Exception:
        raise MicronutrientNotFoundError


def new_guaranteed_analysis(cursor, read_name, value, unit, label_id,edited:bool=False, element_id:int=None):
    """
    This function add a new guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - read_name (str): The name of the guaranteed.
    - value (float): The value of the guaranteed.
    - unit (str): The unit of the guaranteed.
    - element_id (int): The element of the guaranteed.
    - label_id (str): The label of the guaranteed.

    Returns:
    - str: The UUID of the guaranteed.
    """

    try:
        query = """
            SELECT new_guaranteed_analysis(%s, %s, %s, %s, %s, %s);
            """
        cursor.execute(query, (read_name, value, unit, label_id, edited, element_id))
        return cursor.fetchone()[0]
    except Exception:
        raise GuaranteedCreationError


def get_guaranteed(cursor, guaranteed_id):
    """
    This function get the guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - guaranteed_id (str): The UUID of the guaranteed.

    Returns:
    - str: The UUID of the guaranteed.
    """

    try:
        query = """
            SELECT 
                read_name,
                value,
                unit,
                element_id,
                label_id,
                edited,
                CONCAT(CAST(read_name AS TEXT),' ',value,' ', unit) AS reading
            FROM 
                guaranteed
            WHERE 
                id = %s
            """
        cursor.execute(query, (guaranteed_id,))
        return cursor.fetchone()
    except Exception:
        raise GuaranteedNotFoundError


def get_full_guaranteed(cursor, guaranteed):
    """
    This function get the guaranteed in the database with the element.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - guaranteed (str): The UUID of the guaranteed.

    Returns:
    - str: The UUID of the guaranteed.
    """

    try:
        query = """
            SELECT 
                g.read_name,
                g.value,
                g.unit,
                ec.name_fr,
                ec.name_en,
                ec.symbol,
                g.edited,
                CONCAT(CAST(g.read_name AS TEXT),' ',g.value,' ', g.unit) AS reading
            FROM 
                guaranteed g
            JOIN 
                element_compound ec ON g.element_id = ec.id
            WHERE 
                g.id = %s
            """
        cursor.execute(query, (guaranteed,))
        return cursor.fetchone()
    except Exception:
        raise GuaranteedNotFoundError


def get_all_guaranteeds(cursor, label_id):
    """
    This function get all the guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - str: The UUID of the guaranteed.
    """

    try:
        query = """
            SELECT 
                g.id,
                g.read_name,
                g.value,
                g.unit,
                ec.name_fr,
                ec.name_en,
                ec.symbol,
                g.edited,
                CONCAT(CAST(g.read_name AS TEXT),' ',g.value,' ', g.unit) AS reading
            FROM 
                guaranteed g
            JOIN 
                element_compound ec ON g.element_id = ec.id
            WHERE 
                g.label_id = %s
            """
        cursor.execute(query, (label_id,))
        return cursor.fetchall()
    except Exception:
        raise GuaranteedNotFoundError
