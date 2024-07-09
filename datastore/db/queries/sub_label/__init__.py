"""
This module represent the function for the sub table of label_information

"""
class SpecificationCreationError(Exception):
    pass
class SpecificationNotFoundError(Exception):
    pass
class FirstAidCreationError(Exception):
    pass
class FirstAidNotFoundError(Exception):
    pass
class WarrantyCreationError(Exception):
    pass
class WarrantyNotFoundError(Exception):
    pass
class InstructionCreationError(Exception):
    pass
class InstructionNotFoundError(Exception):
    pass
class CautionCreationError(Exception):
    pass
class CautionNotFoundError(Exception):
    pass
class IngredientCreationError(Exception):
    pass
class IngredientNotFoundError(Exception):
    pass

def new_specification(cursor,humidity, ph, solubility,label_id, edited=False):
    """
    This function creates a new specification in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - humidity (float): The humidity of the product.
    - ph (float): The ph of the product.
    - solubility (float): The solubility of the product.
    - edited (bool): The edited status of the specification.

    Returns:
    - The UUID of the new specification.
    """
    try:
        query = """
            INSERT INTO 
                specification (humidity, ph, solubility, edited,label_id)
            VALUES 
                (%s, %s, %s, %s,%s)
            RETURNING 
                id
        """
        cursor.execute(query, (humidity, ph, solubility, edited,label_id,))
        return cursor.fetchone()[0]
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
        return cursor.fetchone()
    except Exception:
        raise SpecificationNotFoundError("Error: could not get the specification")

def get_all_specifications(cursor, label_id):
    """
    This function gets all the specifications of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of specifications.
    """
    try:
        query = """
            SELECT 
                id, 
                humidity, 
                ph, 
                solubility, 
                edited
            FROM 
                specification
            WHERE 
                label_id = %s
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise SpecificationNotFoundError("Error: could not get the specifications")

def new_first_aid(cursor,first_aid_fr, first_aid_en,label_id, edited=False):
    """
    This function creates a new first aid in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - first_aid_fr (str): The first aid in french.
    - first_aid_en (str): The first aid in english.
    - edited (bool): The edited status of the first aid.

    Returns:
    - The UUID of the new first aid.
    """
    try:
        query = """
            INSERT INTO 
                first_aid (first_aid_fr, first_aid_en, edited,label_id)
            VALUES 
                (%s, %s, %s,%s)
            RETURNING 
                id
        """
        cursor.execute(query, (first_aid_fr, first_aid_en, edited,label_id))
        return cursor.fetchone()[0]
    except Exception:
        raise FirstAidCreationError("Error: could not create the first aid")

def get_first_aid(cursor, first_aid_id):
    """
    This function gets the first aid from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - first_aid_id (uuid): The UUID of the first aid.

    Returns:
    - The first_aid entity.
    """
    try:
        query = """
            SELECT 
                first_aid_fr,
                first_aid_en,
                edited
            FROM 
                first_aid
            WHERE 
                id = %s
        """
        cursor.execute(query, (first_aid_id,))
        return cursor.fetchone()
    except Exception:
        raise FirstAidNotFoundError("Error: could not get the first aid")

def get_all_first_aids(cursor, label_id):
    """
    This function gets all the first aids of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of first aids.
    """
    try:
        query = """
            SELECT 
                id, 
                first_aid_fr, 
                first_aid_en, 
                edited
            FROM 
                first_aid
            WHERE 
                label_id = %s
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise FirstAidNotFoundError("Error: could not get the first aids")

def new_warranty(cursor,warranty_fr, warranty_en,label_id, edited=False):
    """
    This function creates a new warranty in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - warranty_fr (str): The warranty in french.
    - warranty_en (str): The warranty in english.
    - edited (bool): The edited status of the warranty.

    Returns:
    - The UUID of the new warranty.
    """
    try:
        query = """
            INSERT INTO 
                warranty (warranty_fr, warranty_en, edited,label_id)
            VALUES 
                (%s, %s, %s,%s)
            RETURNING 
                id
        """
        cursor.execute(query, (warranty_fr, warranty_en, edited,label_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise WarrantyCreationError("Error: could not create the warranty")

def get_warranty(cursor, warranty_id):
    """
    This function gets the warranty from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - warranty_id (uuid): The UUID of the warranty.

    Returns:
    - The warranty entity.
    """
    try:
        query = """
            SELECT 
                warranty_fr,
                warranty_en,
                edited
            FROM 
                warranty
            WHERE 
                id = %s
        """
        cursor.execute(query, (warranty_id,))
        return cursor.fetchone()
    except Exception:
        raise WarrantyNotFoundError("Error: could not get the first aid")

def get_all_warranties(cursor, label_id):
    """
    This function gets all the warranties of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of warranties.
    """
    try:
        query = """
            SELECT 
                id, 
                warranty_fr, 
                warranty_en, 
                edited
            FROM 
                warranty
            WHERE 
                label_id = %s
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise WarrantyNotFoundError("Error: could not get the warranties")

def new_instruction(cursor,instruction_fr, instruction_en,label_id, edited=False):
    """
    This function creates a new instruction in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - instruction_fr (str): The instruction in french.
    - instruction_en (str): The instruction in english.
    - edited (bool): The edited status of the instruction.

    Returns:
    - The UUID of the new instruction.
    """
    try:
        query = """
            INSERT INTO 
                instruction (instruction_fr, instruction_en, edited,label_id)
            VALUES 
                (%s, %s, %s,%s)
            RETURNING 
                id
        """
        cursor.execute(query, (instruction_fr, instruction_en, edited,label_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise InstructionCreationError("Error: could not create the instruction")

def get_instruction(cursor, instruction_id):
    """
    This function gets the instruction from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - instruction_id (uuid): The UUID of the instruction.

    Returns:
    - The instruction entity.
    """
    try:
        query = """
            SELECT 
                instruction_fr,
                instruction_en,
                edited
            FROM 
                instruction
            WHERE 
                id = %s
        """
        cursor.execute(query, (instruction_id,))
        return cursor.fetchone()
    except Exception:
        raise InstructionNotFoundError("Error: could not get the instruction")

def get_all_instructions(cursor, label_id):
    """
    This function gets all the instructions of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of instructions.
    """
    try:
        query = """
            SELECT 
                id, 
                instruction_fr, 
                instruction_en, 
                edited
            FROM 
                instruction
            WHERE 
                label_id = %s
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise InstructionNotFoundError("Error: could not get the instructions")

def new_caution(cursor,caution_fr, caution_en,label_id, edited=False):
    """
    This function creates a new caution in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - caution_fr (str): The caution in french.
    - caution_en (str): The caution in english.
    - edited (bool): The edited status of the caution.

    Returns:
    - The UUID of the new caution.
    """
    try:
        query = """
            INSERT INTO 
                caution (caution_fr, caution_en, edited,label_id)
            VALUES 
                (%s, %s, %s,%s)
            RETURNING 
                id
        """
        cursor.execute(query, (caution_fr, caution_en, edited,label_id,))
        return cursor.fetchone()[0]
    except Exception:
        raise CautionCreationError("Error: could not create the caution")

def get_caution(cursor, caution_id):
    """
    This function gets the caution from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - caution_id (uuid): The UUID of the caution.

    Returns:
    - The caution entity.
    """
    try:
        query = """
            SELECT 
                caution_fr,
                caution_en,
                edited
            FROM 
                caution
            WHERE 
                id = %s
        """
        cursor.execute(query, (caution_id,))
        return cursor.fetchone()
    except Exception:
        raise CautionNotFoundError("Error: could not get the caution")

def get_all_cautions(cursor, label_id):
    """
    This function gets all the cautions of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of cautions.
    """
    try:
        query = """
            SELECT 
                id, 
                caution_fr, 
                caution_en, 
                edited
            FROM 
                caution
            WHERE 
                label_id = %s
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise CautionNotFoundError("Error: could not get the cautions")

def new_ingredient(cursor, name,label_id, organic:bool ,edited:bool=False ):
    """
    This function creates a new ingredient in the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - name (str): The name of the ingredient.
    - label_id (uuid): The UUID of the label_information.
    - organic (bool): The organic status of the ingredient.
    - edited (bool): The edited status of the ingredient.

    Returns:
    - The UUID of the new ingredient.
    """
    try:
        query = """
            INSERT INTO 
                ingredient (name, label_id, organic, edited)
            VALUES 
                (%s, %s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (name, label_id, organic, edited))
        return cursor.fetchone()[0]
    except Exception:
        raise IngredientCreationError("Error: could not create the ingredient")

def get_ingredient(cursor, ingredient_id):
    """
    This function gets the ingredient from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - ingredient_id (uuid): The UUID of the ingredient.

    Returns:
    - The ingredient entity.
    """
    try:
        query = """
            SELECT 
                name,
                organic,
                edited
            FROM 
                ingredient
            WHERE 
                id = %s
        """
        cursor.execute(query, (ingredient_id,))
        return cursor.fetchone()
    except Exception:
        raise IngredientNotFoundError("Error: could not get the ingredient")

def get_all_ingredients(cursor, label_id):
    """
    This function gets all the ingredients of a label_information from the database.

    Parameters:
    - cursor (cursor): The cursor of the database.
    - label_id (uuid): The UUID of the label_information.

    Returns:
    - The list of ingredients.
    """
    try:
        query = """
            SELECT 
                id, 
                name,
                organic,
                edited
            FROM 
                ingredient
            WHERE 
                label_id = %s
            ORDER BY
                organic ASC
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise IngredientNotFoundError("Error: could not get the ingredients")
