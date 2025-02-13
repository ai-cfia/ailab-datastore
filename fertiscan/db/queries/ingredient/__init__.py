from psycopg import Cursor, Error
from uuid import UUID

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

def delete_ingredient_label(cursor:Cursor, label_id:UUID):
    query = """
        DELETE FROM ingredient
        WHERE label_id = %s;
    """
    try:
        cursor.execute(query, (label_id,))
    except Error as db_error:
        raise IngredientQueryError(f"Database error: {db_error}") from db_error
    except Exception as e:
        raise IngredientQueryError(f"Unexpected error: {e}") from e

def upsert_ingredient(cursor: Cursor,label_id:UUID,ingredients:dict):
    delete_ingredient_label(cursor=cursor,label_id=label_id)
    for ingredient_en in ingredients["en"]:
        new_ingredient(
            cursor=cursor,
            name=ingredient_en["name"],
            value=ingredient_en["value"],
            read_unit=ingredient_en["unit"],
            label_id=label_id,
            language="en",
            organic=None,
            active=None,
            edited=True)
    for ingredient_fr in ingredients["fr"]:
        new_ingredient(
            cursor=cursor,
            name=ingredient_fr["name"],
            value=ingredient_fr["value"],
            read_unit=ingredient_fr["unit"],
            label_id=label_id,
            language="fr",
            organic=None,
            active=None,
            edited=True)
