from psycopg import Cursor, Error

"""
This module represent the function for the Ingredient table
"""


class IngredientQueryError(Exception):
    pass


class IngredientCreationError(IngredientQueryError):
    pass


class IngredientRetrievalError(IngredientQueryError):
    pass


def new_ingredient(
    cursor: Cursor,
    name: str,
    value: float,
    read_unit: str,
    label_id,
    language: str,
    organic: bool,
    active: bool,
    edited=False,
):
    """
    This function creates a new ingredient in the database.
    """
    try:
        if language not in ["en", "fr"]:
            raise IngredientCreationError("Error: language must be either 'en' or 'fr'")
        query = """
            SELECT new_ingredient(%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(
            query, (name, value, read_unit, label_id, language, organic, active, edited)
        )
        return cursor.fetchone()[0]
    except IngredientCreationError:
        raise
    except Error as db_error:
        raise IngredientCreationError(f"Database error: {db_error}") from db_error
    except Exception as e:
        raise IngredientCreationError(f"Unexpected error: {e}") from e


def get_ingredient_json(cursor: Cursor, label_id) -> dict:
    """
    This function gets the ingredient JSON from the database.
    """
    try:
        query = """
            SELECT get_ingredients_json(%s);
        """
        cursor.execute(query, (label_id,))
        result = cursor.fetchone()
        if result is None:
            raise IngredientRetrievalError("Error: ingredient not found")
        return result[0]

    except IngredientRetrievalError:
        raise
    except Error as db_error:
        raise IngredientCreationError(f"Database error: {db_error}") from db_error
    except Exception as e:
        raise IngredientCreationError(f"Unexpected error: {e}") from e
