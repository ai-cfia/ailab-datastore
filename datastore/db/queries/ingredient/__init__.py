"""
This module represent the function for the Ingredient table
"""

class IngredientCreationError(Exception):
    pass

class IngredientNotFoundError(Exception):
    pass

def new_ingredient(cursor, name:str, value:float, read_unit:str, label_id, language:str, organic:bool, active:bool, edited=False):
    """
    This function creates a new ingredient in the database.
    """
    try:
        if language not in ["en", "fr"]:
            raise IngredientCreationError("Error: language must be either 'en' or 'fr'")
        query = """
            SELECT new_ingredient(%s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (name, value, read_unit, label_id, language, organic, active, edited))
        return cursor.fetchone()[0]
    except IngredientCreationError:
        raise 
    except Exception:
        raise IngredientCreationError("Error: could not create the ingredient")