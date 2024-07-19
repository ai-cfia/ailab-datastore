"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

import json

from pydantic import ValidationError

from datastore.db.metadata.validator import AnalysisForm


class BuildInspectionValidationError(Exception):
    pass


def build_inspection_import(analysis_form: AnalysisForm):
    """
    Build an inspection JSON object from the digitalization analysis pipeline.
    This serves as the metadata for the inspection object in the database.

    Parameters:
    - analysis_form (AnalysisForm): The digitalization of the label.

    Returns:
    - str: The inspection database object in JSON string format.

    Raises:
    - BuildInspectionValidationError: If there is a validation error in the analysis form data.
    """
    try:
        npk = extract_npk(analysis_form.npk)
        output_json = {
            "company": {
                "name": analysis_form.company_name,
                "address": analysis_form.company_address,
                "website": analysis_form.company_website,
                "phone_number": analysis_form.company_phone_number,
            },
            "manufacturer": {
                "name": analysis_form.manufacturer_name,
                "address": analysis_form.manufacturer_address,
                "website": analysis_form.manufacturer_website,
                "phone_number": analysis_form.manufacturer_phone_number,
            },
            "product": {
                "name": analysis_form.fertiliser_name,
                "registration_number": analysis_form.registration_number,
                "lot_number": analysis_form.lot_number,
                "weight": {
                    "kg": analysis_form.weight_kg,
                    "lb": analysis_form.weight_lb,
                },
                "density": analysis_form.density,
                "volume": analysis_form.volume,
                "npk": analysis_form.npk,
                "n": npk[0],
                "p": npk[1],
                "k": npk[2],
                "warranty": analysis_form.warranty,
            },
            "cautions": {
                "en": analysis_form.cautions_en,
                "fr": analysis_form.cautions_fr,
            },
            "instructions": {
                "en": analysis_form.instructions_en,
                "fr": analysis_form.instructions_fr,
            },
            "micronutrients": {
                "en": analysis_form.micronutrients_en,
                "fr": analysis_form.micronutrients_fr,
            },
            "organic_ingredients": {
                "en": analysis_form.organic_ingredients_en,
                "fr": analysis_form.organic_ingredients_fr,
            },
            "inert_ingredients": {
                "en": analysis_form.inert_ingredients_en,
                "fr": analysis_form.inert_ingredients_fr,
            },
            "specifications": {
                "en": analysis_form.specifications_en,
                "fr": analysis_form.specifications_fr,
            },
            "first_aid": {
                "en": analysis_form.first_aid_en,
                "fr": analysis_form.first_aid_fr,
            },
            "guaranteed_analysis": analysis_form.guaranteed_analysis,
            "verified": analysis_form.verified,
        }
        return json.dumps(output_json)
    except ValidationError as e:
        raise BuildInspectionValidationError(f"Validation error: {e}")


def split_value_unit(value_unit: str) -> dict:
    """
    This function splits the value and unit from a string.
    The string must be in the format of "value unit".

    Parameters:
    - value_unit: (str) The string to split.

    Returns:
    - A dictionary containing the value and unit.
    """
    if value_unit is None or value_unit == "" or len(value_unit) < 2:
        return {"value": None, "unit": None}
    # loop through the string and split the value and unit
    for i in range(len(value_unit)):
        if not (
            value_unit[i].isnumeric() or value_unit[i] == "." or value_unit[i] == ","
        ):
            value = value_unit[:i]
            unit = value_unit[i:]
            break
    # trim the unit of any leading or trailing whitespaces
    unit = unit.strip()
    if unit == "":
        unit = None
    return {"value": value, "unit": unit}


def extract_npk(npk: str):
    """
    This function extracts the npk values from the string npk.
    The string must be in the format of "N-P-K".

    Parameters:
    - npk: (str) The string to split.

    Returns:
    - A list containing the npk values.
    """
    if npk is None or npk == "" or len(npk) < 5:
        return [None, None, None]
    npk = npk.split("-")
    return [float(npk[0]), float(npk[1]), float(npk[2])]
