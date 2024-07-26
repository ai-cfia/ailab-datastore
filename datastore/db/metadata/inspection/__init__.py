"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

import json
from typing import List
from pydantic import BaseModel, ValidationError

class MissingKeyError(Exception):
    pass

class NPKError(Exception):
    pass

class MetadataFormattingError(Exception):
    pass

class OrganizationInformation(BaseModel):
    name: str
    address: str
    website: str
    phone_number: str
    
class Value(BaseModel):
    value: float
    unit: str
    name: str

class ValuesObjects(BaseModel):
    en: List[Value]
    fr: List[Value]

class SubLabel(BaseModel):
    en: List[str]
    fr: List[str]

class ProductInformation(BaseModel):
    name: str
    registration_number: str
    lot_number: str
    weight: Value
    density: Value
    volume: Value
    npk: str
    warranty: str
    n: float
    p: float
    k: float

class Specification(BaseModel):
    humidity: float
    ph: float
    solubility: float

class Specifications(BaseModel):
    en: List[Specification]
    fr: List[Specification]

class Inspection(BaseModel):
    company: OrganizationInformation
    manufacturer: OrganizationInformation
    product: ProductInformation
    cautions: SubLabel
    instructions: SubLabel
    micronutrients: SubLabel
    organic_ingredients: ValuesObjects
    inert_ingredients: ValuesObjects
    specifications: Specifications
    first_aid: SubLabel
    guaranteed_analysis: ValuesObjects


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
        #data = json.loads(analysis_form)
        npk = extract_npk(analysis_form.get("npk"))
        company = OrganizationInformation(
            name=analysis_form.get("company_name"),
            address=analysis_form["company_address"],
            website=analysis_form["company_website"],
            phone_number=analysis_form["company_phone_number"]
        )
        manufacturer = OrganizationInformation(
            name=analysis_form["manufacturer_name"],
            address=analysis_form["manufacturer_address"],
            website=analysis_form["manufacturer_website"],
            phone_number=analysis_form["manufacturer_phone_number"]
        )
        product = ProductInformation(
            name=analysis_form["fertiliser_name"],
            registration_number=analysis_form["registration_number"],
            lot_number=analysis_form["lot_number"],
            weight=split_value_unit(analysis_form["weight"]),
            density=split_value_unit(analysis_form["density"]),
            volume=split_value_unit(analysis_form["volume"]),
            npk=analysis_form["npk"],
            warranty=analysis_form["warranty"],
            n=npk[0],
            p=npk[1],
            k=npk[2]
        )

        cautions = SubLabel(
            en=analysis_form["cautions_en"],
            fr=analysis_form["cautions_fr"]
        )

        instructions = SubLabel(
            en=analysis_form["instructions_en"],
            fr=analysis_form["instructions_fr"]
        )

        micronutrients = SubLabel(
            en=analysis_form["micronutrients_en"],
            fr=analysis_form["micronutrients_fr"]
        )

        organic_ingredients = ValuesObjects(
            en=analysis_form["organic_ingredients_en"],
            fr=analysis_form["organic_ingredients_fr"]
        )

        inert_ingredients = ValuesObjects(
            en=analysis_form["inert_ingredients_en"],
            fr=analysis_form["inert_ingredients_fr"]
        )

        specifications = Specifications(
            en=extract_specifications(analysis_form["specifications_en"]),
            fr=extract_specifications(analysis_form["specifications_fr"])
        )

        first_aid = SubLabel(
            en=analysis_form["first_aid_en"],
            fr=analysis_form["first_aid_fr"]
        )

        guaranteed_analysis = ValuesObjects(
            en=analysis_form["guaranteed_analysis"],
            fr=analysis_form["guaranteed_analysis"]
        )

        inspection_formatted = Inspection(
            company=company,
            manufacturer=manufacturer,
            product=product,
            cautions=cautions,
            instructions=instructions,
            micronutrients=micronutrients,
            organic_ingredients=organic_ingredients,
            inert_ingredients=inert_ingredients,
            specifications=specifications,
            first_aid=first_aid,
            guaranteed_analysis=guaranteed_analysis
        )
        Inspection(**inspection_formatted.model_dump())
    except MissingKeyError as e:
        raise MissingKeyError(f"Missing key: {e}")
    except ValidationError as e:
        raise MetadataFormattingError("Error InspectionCreationError not created:"+ str(e)) from None
    return inspection_formatted.model_dump_json()


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
    npk_formated=npk.replace("N","-")
    npk_formated=npk_formated.replace("P","-")
    npk_formated=npk_formated.replace("K","-")
    npk_reformated = npk.split("-")
    for i in range(len(npk_reformated)):
        if not npk_reformated[i].isnumeric():
            NPKError("NPK values must be numeric. Issue with: "+npk_reformated[i] + "in the NPK string: "+npk)
    return [float(npk_reformated[0]),float(npk_reformated[1]),float(npk_reformated[2])]

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