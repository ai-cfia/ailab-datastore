"""
This module represent the function for the sub table of label_information and the ingredient table:

    --sub table 1-1 label_information
    CREATE TABLE "fertiscan_0.0.6"."specification" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "humidity" float,
    "ph" float,
    "solubility" float,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."first_aid" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "first_aid_fr" text,
    "first_aid_en" text,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."warranty" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "warranty_fr" text,
    "warranty_en" text,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."instruction" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "instruction_fr" text,
    "instruction_en" text,
    "edited" boolean
    );

    CREATE TABLE "fertiscan_0.0.6"."caution" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "caution_fr" text,
    "caution_en" text,
    "edited" boolean
    );


    -- label_information 1-* ingredient
    CREATE TABLE "fertiscan_0.0.6"."ingredient" (
    "id" uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
    "organic" boolean NOT NULL,
    "name" text NOT NULL,
    "edited" boolean,
    "label_id" uuid REFERENCES "fertiscan_0.0.6".label_information(id)
    );


"""
class SpecificationCreationError(Exception):
    pass

def new_specification(cursor,humidity, ph, solubility, edited=False):
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
                specification (humidity, ph, solubility, edited)
            VALUES 
                (%s, %s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (humidity, ph, solubility, edited))
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

def new_first_aid(cursor,first_aid_fr, first_aid_en, edited=False):
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
                first_aid (first_aid_fr, first_aid_en, edited)
            VALUES 
                (%s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (first_aid_fr, first_aid_en, edited))
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

def new_warranty(cursor,warranty_fr, warranty_en, edited=False):
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
                warranty (warranty_fr, warranty_en, edited)
            VALUES 
                (%s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (warranty_fr, warranty_en, edited))
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

def new_instruction(cursor,instruction_fr, instruction_en, edited=False):
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
                instruction (instruction_fr, instruction_en, edited)
            VALUES 
                (%s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (instruction_fr, instruction_en, edited))
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

def new_caution(cursor,caution_fr, caution_en, edited=False):
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
                caution (caution_fr, caution_en, edited)
            VALUES 
                (%s, %s, %s)
            RETURNING 
                id
        """
        cursor.execute(query, (caution_fr, caution_en, edited))
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

def new_ingredient(cursor, name,label_id, organic:boolean ,edited:boolean=False ):
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
        """
        cursor.execute(query, (label_id,))
        res = cursor.fetchall()
        return res
    except Exception:
        raise IngredientNotFoundError("Error: could not get the ingredients")