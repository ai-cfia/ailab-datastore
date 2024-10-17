"""
This module represent the function for the Specification table

"""

from psycopg import Cursor, sql

from fertiscan.db.queries.errors import (
    SpecificationCreationError,
    SpecificationNotFoundError,
    SpecificationQueryError,
    SpecificationRetrievalError,
    handle_query_errors,
)


@handle_query_errors(SpecificationCreationError)
def new_specification(
    cursor: Cursor,
    humidity,
    ph,
    solubility,
    label_id,
    language,
    edited=False,
):
    """
    This function creates a new specification in the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - humidity (float): The humidity of the product.
    - ph (float): The ph of the product.
    - solubility (float): The solubility of the product.
    - label_id (uuid): The UUID of the label_information.
    - edited (bool): The edited status of the specification.
    Returns:
    - The UUID of the new specification.
    """
    if language not in ["en", "fr"]:
        raise SpecificationCreationError("Error: language must be either 'en' or 'fr'")
    # query = sql.SQL("""
    #    SELECT {}.new_specification(%s, %s, %s, %s, %s, %s);
    # """).format(sql.Identifier(schema))
    query = sql.SQL("""
        SELECT new_specification(%s, %s, %s, %s, %s, %s);
    """)
    cursor.execute(query, (humidity, ph, solubility, language, label_id, edited))
    if result := cursor.fetchone():
        return result[0]
    raise SpecificationCreationError(
        "Failed to create Specification. No data returned."
    )


@handle_query_errors(SpecificationRetrievalError)
def get_specification(cursor: Cursor, specification_id):
    """
    This function gets the specification from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - specification_id (uuid): The UUID of the specification.
    Returns:
    - The specification.
    """
    query = """
        SELECT 
            humidity,
            ph,
            solubility,
            edited
        FROM 
            specification
        WHERE 
            id = %s
    """
    cursor.execute(query, (specification_id,))
    if result := cursor.fetchone():
        return result
    raise SpecificationNotFoundError("No record found for the given specification_id")


@handle_query_errors(SpecificationQueryError)
def has_specification(cursor: Cursor, label_id):
    """
    This function checks if a label has specification.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - True if the label has specification, False otherwise.
    """
    query = """
        SELECT
            EXISTS(
                SELECT 1
                FROM 
                    specification
                WHERE 
                    label_id = %s
            );
    """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        return result[0]
    raise SpecificationQueryError(
        "Failed to check if label has specification. No data returned."
    )


@handle_query_errors(SpecificationRetrievalError)
def get_specification_json(cursor: Cursor, label_id) -> dict:
    """
    This function gets the specification from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - specification_id (uuid): The UUID of the specification.
    Returns:
    - The specification.
    """
    if not has_specification(cursor, label_id):
        return {"specifications": {"en": [], "fr": []}}
    query = """
        SELECT get_specification_json(%s);
    """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchone():
        return result[0]
    raise SpecificationNotFoundError("No record found for the given specification_id")


@handle_query_errors(SpecificationRetrievalError)
def get_all_specifications(cursor: Cursor, label_id):
    """
    This function gets all the specifications from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - The specifications.
    """
    query = """
        SELECT 
            id,
            humidity,
            ph,
            solubility,
            edited,
            language
        FROM 
            specification
        WHERE 
            label_id = %s
    """
    cursor.execute(query, (label_id,))
    if result := cursor.fetchall():
        return result
    raise SpecificationNotFoundError("No record found for the given label_id")
