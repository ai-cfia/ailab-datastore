"""
This module represent the function for the table micronutrient, guaranteed and its children element_compound:

"""

from psycopg import Cursor
from uuid import UUID

from fertiscan.db.queries.errors import (
    ElementCompoundCreationError,
    ElementCompoundNotFoundError,
    ElementCompoundQueryError,
    GuaranteedAnalysisCreationError,
    GuaranteedAnalysisRetrievalError,
    GuaranteedAnalysisDeleteError,
    GuaranteedAnalysisUpdateError,
    MicronutrientCreationError,
    MicronutrientRetrievalError,
    handle_query_errors,
)


@handle_query_errors(ElementCompoundCreationError)
def new_element(cursor: Cursor, number, name_fr, name_en, symbol):
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

    query = """
        INSERT INTO element_compound (number,name_fr,name_en,symbol)
        VALUES (%s,%s,%s,%s)
        RETURNING id
        """
    cursor.execute(query, (number, name_fr, name_en, symbol))
    if result := cursor.fetchone():
        return result[0]
    raise ElementCompoundCreationError("Failed to create element. No data returned.")


@handle_query_errors(ElementCompoundQueryError)
def get_element_id_full_search(cursor: Cursor, name):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the element.

    Returns:
    - str: The UUID of the element.
    """

    query = """
        SELECT id
        FROM element_compound
        WHERE name_fr ILIKE %s OR name_en ILIKE %s OR symbol = %s
        """
    cursor.execute(query, (name, name, name))
    if result := cursor.fetchone():
        return result[0]
    raise ElementCompoundNotFoundError(
        "Failed to retrieve element id. No data returned."
    )


@handle_query_errors(ElementCompoundQueryError)
def get_element_id_name(cursor: Cursor, name):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the element.

    Returns:
    - str: The UUID of the element.
    """

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
    if result := cursor.fetchone():
        return result[0]
    raise ElementCompoundNotFoundError(
        "Failed to retrieve element id. No data returned."
    )


@handle_query_errors(ElementCompoundQueryError)
def get_element_id_symbol(cursor: Cursor, symbol):
    """
    This function get the element in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - symbol (str): The symbol of the element.

    Returns:
    - str: The UUID of the element.
    """

    query = """
        SELECT 
            id
        FROM 
            element_compound
        WHERE 
            symbol ILIKE %s
        """
    cursor.execute(query, (symbol,))
    if result := cursor.fetchone():
        return result[0]
    raise ElementCompoundNotFoundError(
        "Failed to retrieve element id. No data returned."
    )


@handle_query_errors(MicronutrientCreationError)
def new_micronutrient(
    cursor: Cursor,
    read_name: str,
    value: float,
    unit: str,
    label_id,
    language: str,
    element_id: int,
    edited=False,
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

    if language.lower() not in ["fr", "en"]:
        raise MicronutrientCreationError("Language not supported")
    query = """
        SELECT new_micronutrient(%s, %s, %s, %s, %s,%s,%s);
        """
    cursor.execute(
        query, (read_name, value, unit, label_id, language, edited, element_id)
    )
    return cursor.fetchone()[0]


@handle_query_errors(MicronutrientRetrievalError)
def get_micronutrient(cursor: Cursor, micronutrient_id):
    """
    This function get the micronutrient in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - micronutrient_id (str): The UUID of the micronutrient.

    Returns:
    - str: The UUID of the micronutrient.
    """

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


@handle_query_errors(MicronutrientRetrievalError)
def get_micronutrient_json(cursor: Cursor, label_id) -> dict:
    """
    This function get the micronutrient in the database for a specific label.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - micronutrient (dict): The micronutrient.
    """
    query = """
        SELECT get_micronutrient_json(%s);
        """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        return result[0]
    raise MicronutrientRetrievalError(
        "Failed to retrieve micronutrient json. No data returned for: " + str(label_id)
    )


@handle_query_errors(MicronutrientRetrievalError)
def get_full_micronutrient(cursor: Cursor, micronutrient_id):
    """
    This function get the micronutrient in the database with the element.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - micronutrient_id (str): The UUID of the micronutrient.

    """

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
        LEFT JOIN 
            element_compound ec ON m.element_id = ec.id
        WHERE 
            m.id = %s
        """
    cursor.execute(query, (micronutrient_id,))
    return cursor.fetchone()


@handle_query_errors(MicronutrientRetrievalError)
def get_all_micronutrients(cursor: Cursor, label_id):
    """
    This function get all the micronutrients with the right label_id in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - str: The UUID of the micronutrient.
    """

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
        LEFT JOIN 
            element_compound ec ON m.element_id = ec.id
        WHERE 
            m.label_id = %s
        """
    cursor.execute(query, (label_id,))
    return cursor.fetchall()

def new_guaranteed_analysis(
    cursor: Cursor,
    read_name,
    value,
    unit,
    label_id,
    language: str,
    element_id: int = None,
    edited: bool = False, 
):
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
    if language.lower() not in ["fr", "en"]:
        raise GuaranteedAnalysisCreationError("Language not supported")
    if (
        (read_name is None or read_name == "")
        and (value is None or value == "")
        and (unit is None or unit == "")
    ):
        raise GuaranteedAnalysisCreationError("Read name and value cannot be empty")
    query = """
        INSERT INTO guaranteed (
            read_name, 
            value, 
            unit, 
            edited, 
            label_id, 
            element_id, 
            language)
	    VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id;
        """
    cursor.execute(
        query, (read_name, value, unit, edited,label_id, element_id, language)
    )
    if result := cursor.fetchone():
        return result[0]
    raise GuaranteedAnalysisCreationError(
        "Failed to create guaranteed analysis. No data returned."
    )


@handle_query_errors(GuaranteedAnalysisCreationError)
def new_guaranteed_analysis_function(
    cursor: Cursor,
    read_name,
    value,
    unit,
    label_id,
    language: str,
    element_id: int = None,
    edited: bool = False,
):
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

    if language.lower() not in ["fr", "en"]:
        raise GuaranteedAnalysisCreationError("Language not supported")
    if (
        (read_name is None or read_name == "")
        and (value is None or value == "")
        and (unit is None or unit == "")
    ):
        raise GuaranteedAnalysisCreationError("Read name and value cannot be empty")
    query = """
        SELECT new_guaranteed_analysis(%s, %s, %s, %s, %s, %s, %s);
        """
    cursor.execute(
        query, (read_name, value, unit, label_id, language, edited, element_id)
    )
    if result := cursor.fetchone():
        return result[0]
    raise GuaranteedAnalysisCreationError(
        "Failed to create guaranteed analysis. No data returned."
    )


@handle_query_errors(GuaranteedAnalysisRetrievalError)
def get_guaranteed(cursor: Cursor, guaranteed_id):
    """
    This function get the guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - guaranteed_id (str): The UUID of the guaranteed.

    Returns:
    - str: The UUID of the guaranteed.
    """

    query = """
        SELECT 
            read_name,
            value,
            unit,
            element_id,
            label_id,
            edited,
            language,
            CONCAT(CAST(read_name AS TEXT),' ',value,' ', unit) AS reading
        FROM 
            guaranteed
        WHERE 
            id = %s
        """
    cursor.execute(query, (guaranteed_id,))
    return cursor.fetchone()


@handle_query_errors(GuaranteedAnalysisRetrievalError)
def get_guaranteed_analysis_json(cursor: Cursor, label_id) -> dict:
    """
    This function get the guaranteed in the database for a specific label.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - guaranteed (dict): The guaranteed.
    """
    query = """
        SELECT get_guaranteed_analysis_json(%s);
        """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        if (data := result[0]) is None:
            return {"title": None, "is_minimal": False, "en": [], "fr": []}
        return data
    raise GuaranteedAnalysisRetrievalError(
        "Failed to retrieve guaranteed analysis json. No data returned for: "
        + str(label_id)
    )
@handle_query_errors(GuaranteedAnalysisDeleteError)
def delete_guaranteed_analysis(cursor:Cursor, label_id:UUID):
    """
    This function deletes guaranteed analysis records from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (UUID): The UUID of the label.

    Returns:
    - int: The number of rows deleted.
    """
    query = """
        DELETE FROM guaranteed
        WHERE label_id = %s
        RETURNING id;
        """
    cursor.execute(query, (label_id,))
    return cursor.rowcount

@handle_query_errors(GuaranteedAnalysisUpdateError)
def upsert_guaranteed_analysis(cursor:Cursor,label_id: UUID, GA:dict):
    """
    Replaces all entries for a label by deleting existing ones and inserting new ones.
    
    Parameters:
    - cursor: Database cursor
    - label_id: UUID of the label to update
    - GA: Dictionary containing the new values to insert
    """
    delete_guaranteed_analysis(
        cursor=cursor,
        label_id= label_id,
    )
    
    for record in GA["en"]:
        new_guaranteed_analysis(
            cursor=cursor,
            read_name=record["name"],
            value=record["value"],
            unit = record["unit"],
            label_id=label_id,
            language="en",
            element_id=None,
            edited= True
        ) 
    for record in GA["fr"]:
        new_guaranteed_analysis(
            cursor=cursor,
            read_name=record["name"],
            value=record["value"],
            unit = record["unit"],
            label_id=label_id,
            language="fr",
            element_id=None,
            edited= True
        ) 
    


@handle_query_errors(GuaranteedAnalysisRetrievalError)
def get_full_guaranteed(cursor: Cursor, guaranteed):
    """
    This function get the guaranteed in the database with the element.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - guaranteed (str): The UUID of the guaranteed.

    Returns:
    - str: The UUID of the guaranteed.
    """

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


@handle_query_errors(GuaranteedAnalysisRetrievalError)
def get_all_guaranteeds(cursor: Cursor, label_id):
    """
    This function get all the guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - str: The UUID of the guaranteed.
    """

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

@handle_query_errors(GuaranteedAnalysisRetrievalError)
def get_guaranteed_by_label(cursor:Cursor,label_id:UUID):
    """
    This function get all the guaranteed in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (str): The UUID of the label.

    Returns:
    - str: The UUID of the guaranteed.
    """

    query = """
        SELECT 
            g.id,
            g.read_name,
            g.value,
            g.unit,
            g.edited,
            CONCAT(CAST(g.read_name AS TEXT),' ',g.value,' ', g.unit) AS reading
        FROM 
            guaranteed g
        WHERE 
            g.label_id = %s;
        """
    cursor.execute(query, (label_id,))
    return cursor.fetchall()
