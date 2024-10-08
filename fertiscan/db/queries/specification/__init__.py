"""
This module represent the function for the Specification table

"""
from psycopg import sql


class SpecificationCreationError(Exception):
    pass


class SpecificationNotFoundError(Exception):
    pass


def new_specification(
    cursor,
    humidity,
    ph,
    solubility,
    label_id,
    language,
    edited=False,
    schema="public",
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
    try:
        if language not in ["en", "fr"]:
            raise SpecificationCreationError(
                "Error: language must be either 'en' or 'fr'"
            )
        #query = sql.SQL("""
        #    SELECT {}.new_specification(%s, %s, %s, %s, %s, %s);
        #""").format(sql.Identifier(schema))
        query=sql.SQL("""
            SELECT new_specification(%s, %s, %s, %s, %s, %s);
        """)
        cursor.execute(query, (humidity, ph, solubility, language, label_id, edited))
        return cursor.fetchone()[0]
    except SpecificationCreationError:
        raise
    except Exception:
        raise SpecificationCreationError("Error: could not create the specification")


def get_specification(cursor, specification_id):
    """
    This function gets the specification from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - specification_id (uuid): The UUID of the specification.
    Returns:
    - The specification.
    """
    try:
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
        result = cursor.fetchone()

        if result is None:
            raise SpecificationNotFoundError(
                "No record found for the given specification_id"
            )
        return result
    except Exception:
        raise SpecificationNotFoundError("Error: could not get the specification")


def has_specification(cursor, label_id):
    """
    This function checks if a label has specification.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - True if the label has specification, False otherwise.
    """
    try:
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
        return cursor.fetchone()[0]
    except Exception:
        raise SpecificationNotFoundError(
            "Error: could not check if the label has specification"
        )


def get_specification_json(cursor, label_id) -> dict:
    """
    This function gets the specification from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - specification_id (uuid): The UUID of the specification.
    Returns:
    - The specification.
    """
    try:
        if not has_specification(cursor, label_id):
            return {"specifications": {"en": [], "fr": []}}
        query = """
            SELECT get_specification_json(%s);
        """
        cursor.execute(query, (label_id,))
        result = cursor.fetchone()

        if result is None:
            raise SpecificationNotFoundError(
                "No record found for the given specification_id"
            )
        specification = result[0]
        return specification
    except SpecificationNotFoundError:
        raise
    except Exception:
        raise


def get_all_specifications(cursor, label_id):
    """
    This function gets all the specifications from the database.
    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.
    Returns:
    - The specifications.
    """
    try:
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
        result = cursor.fetchall()
        if result is None or len(result) == 0:
            raise SpecificationNotFoundError(
                "No record found for the given specification_id"
            )
        return result
    except Exception:
        raise SpecificationNotFoundError(
            "Error: could not get the specifications with the label_id= " + label_id
        )
