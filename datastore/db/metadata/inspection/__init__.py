"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

import json

class MissingKeyError(Exception):
    pass


def build_inspection_import(analysis_form: dict) -> str:
    """
    This funtion build an inspection json object from the pipeline of digitalization analysis.
    This serves as the metadata for the inspection object in the database.

    Parameters:
    - analysis_form: (dict) The digitalization of the label.

    Returns:
    - The inspection db object in a string format.
    """
    try:
        requiered_keys = [
            "company_name",
            "company_address",
            "company_website",
            "company_phone_number",
            "manufacturer_name",
            "manufacturer_address",
            "manufacturer_website",
            "manufacturer_phone_number",
            "fertiliser_name",
            "registration_number",
            "lot_number",
            "weight",
            "density",
            "volume",
            "npk",
            "warranty",
            "cautions_en",
            "instructions_en",
            "micronutrients_en",
            "organic_ingredients_en",
            "inert_ingredients_en",
            "specifications_en",
            "first_aid_en",
            "cautions_fr",
            "instructions_fr",
            "micronutrients_fr",
            "organic_ingredients_fr",
            "inert_ingredients_fr",
            "specifications_fr",
            "first_aid_fr",
            "guaranteed_analysis"
        ]
        for key in requiered_keys:
            if key not in analysis_form:
                raise MissingKeyError(key)
        npk = extract_npk(analysis_form.get("npk"))
        output_json = {
        "company": {
            "name": analysis_form.get("company_name"),
            "address": analysis_form.get("company_address"),
            "website": analysis_form.get("company_website"),
            "phone_number": analysis_form.get("company_phone_number")
        },
        "manufacturer": {
            "name": analysis_form.get("manufacturer_name"),
            "address": analysis_form.get("manufacturer_address"),
            "website": analysis_form.get("manufacturer_website"),
            "phone_number": analysis_form.get("manufacturer_phone_number")
        },
        "product": {
            "name": analysis_form.get("fertiliser_name"),
            "registration_number": analysis_form.get("registration_number"),
            "lot_number": analysis_form.get("lot_number"),
            "weight": {
                "kg": analysis_form.get("weight_kg"),
                "lb": analysis_form.get("weight_lb")
            },
            "density": analysis_form.get("density"),
            "volume": analysis_form.get("volume"),
            "npk": analysis_form.get("npk"),
            "n":npk[0],
            "p":npk[1],
            "k":npk[2],
            "warranty": analysis_form.get("warranty")
        },
        "cautions": {
            "en": analysis_form.get("cautions_en", []),
            "fr": analysis_form.get("cautions_fr", [])
        },
        "instructions": {
            "en": analysis_form.get("instructions_en", []),
            "fr": analysis_form.get("instructions_fr", [])
        },
        "micronutrients": {
            "en": analysis_form.get("micronutrients_en", []),
            "fr": analysis_form.get("micronutrients_fr", [])
        },
        "organic_ingredients": {
            "en": analysis_form.get("organic_ingredients_en", []),
            "fr": analysis_form.get("organic_ingredients_fr", [])
        },
        "inert_ingredients": {
            "en": analysis_form.get("inert_ingredients_en", []),
            "fr": analysis_form.get("inert_ingredients_fr", [])
        },
        "specifications": {
            "en": analysis_form.get("specifications_en", []),
            "fr": analysis_form.get("specifications_fr", [])
        },
        "first_aid": {
            "en": analysis_form.get("first_aid_en", []),
            "fr": analysis_form.get("first_aid_fr", [])
        },
        "guaranteed_analysis": analysis_form.get("guaranteed_analysis", [])
    }
        return (json.dumps(output_json))
    except MissingKeyError as e:
        raise MissingKeyError(f"Missing key: {e}")

def split_value_unit(value_unit: str) -> dict:
    """
    This function splits the value and unit from a string.
    The string must be in the format of "value unit".

    Parameters:
    - value_unit: (str) The string to split.

    Returns:
    - A dictionary containing the value and unit.
    """
    if value_unit is None or value_unit == "" or len(value_unit)<2:
        return {
        "value": None,
        "unit": None
    }
    # loop through the string and split the value and unit
    for i in range(len(value_unit)):
        if not (value_unit[i].isnumeric() or value_unit[i] == "." or value_unit[i] == ","):
            value = value_unit[:i]
            unit = value_unit[i:]
            break
    # trim the unit of any leading or trailing whitespaces
    unit = unit.strip()
    if unit == "":
        unit = None
    return {
        "value": value,
        "unit": unit
    }
def extract_npk(npk:str):
    """
    This function extracts the npk values from the string npk.
    The string must be in the format of "N-P-K".

    Parameters:
    - npk: (str) The string to split.

    Returns:
    - A list containing the npk values.
    """
    if npk is None or npk == "" or len(npk)<5:
        return [None,None,None]
    npk = npk.split("-")
    return [float(npk[0]),float(npk[1]),float(npk[2])]

def extract_specifications(specifications: list) -> list:
    """
    This function extracts the specifications from the list of strings.
    The strings must be in the format of "value unit".

    Parameters:
    - specifications: (list) The list of strings to split.

    Returns:
    - A list containing the specifications.
    """
    output = []
    if specifications is None or specifications == []:
        return output
    for specification in specifications:
        print(specification)
        res = {}
        res["humidity"] = float(specification["humidity"])
        res["ph"] = float(specification["ph"])
        res["solubility"] = float(specification["solubility"])
        output.append(res)
    return output
