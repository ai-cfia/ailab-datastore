from psycopg import Cursor, Error
from uuid import UUID

"""
This module represent the function for the Ingredient table
"""

from fertiscan.db.queries.errors import (
    IngredientNotFoundError,
    IngredientCreationError,
    IngredientDeleteError,
    IngredientQueryError,
    handle_query_errors
)

handle_query_errors(IngredientCreationError)
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
    if language not in ["en", "fr"]:
        raise IngredientCreationError("Error: language must be either 'en' or 'fr'")
    if name is None and value is None and read_unit is None:
        raise IngredientCreationError("Error: All minimal inputs [name,value,read_unit] are Null")
    query = """
        SELECT new_ingredient(%s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(
        query, (name, value, read_unit, label_id, language, organic, active, edited)
    )
    return cursor.fetchone()[0]

handle_query_errors(IngredientNotFoundError)
def get_ingredient_json(cursor: Cursor, label_id) -> dict:
    """
    This function gets the ingredient JSON from the database.
    """
    query = """
        SELECT get_ingredients_json(%s);
    """
    cursor.execute(query, (label_id,))
    result = cursor.fetchone()
    if result is None:
        raise IngredientNotFoundError("Error: ingredient not found")
    return result[0]

handle_query_errors(IngredientNotFoundError)
def get_ingredient_label(cursor:Cursor,label_id:UUID):
    """
    This function gets the ingredient JSON from the database.
    """
    query = """
        SELECT 
            id,
            name,
            value,
            unit,
            edited,
            organic,
            active,
            language
        FROM
            ingredient
        WHERE
            label_id = %s;
    """
    cursor.execute(query, (label_id,))
    result = cursor.fetchall()
    return result

handle_query_errors(IngredientDeleteError)
def delete_ingredient_label(cursor:Cursor, label_id:UUID):
    query = """
        DELETE FROM ingredient
        WHERE label_id = %s
        RETURNING id;
    """
    cursor.execute(query, (label_id,))
    return cursor.rowcount

handle_query_errors(IngredientQueryError)
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
