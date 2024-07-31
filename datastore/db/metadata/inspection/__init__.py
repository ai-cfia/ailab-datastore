"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects. 
The metadata is generated in a json format and is used to store the metadata in the database.

"""

from typing import List
from pydantic import BaseModel, ValidationError
from typing import Optional

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
    value: Optional[float] = None
    unit: Optional[str] = None
    name: str

class ValuesObjects(BaseModel):
    en: List[Value]
    fr: List[Value]

class SubLabel(BaseModel):
    en: List[str]
    fr: List[str]
    
class Metric(BaseModel):
    value: float
    unit: str

class Metrics(BaseModel):
    weight: List[Metric]
    volume: Metric
    density: Metric

class ProductInformation(BaseModel):
    name: str
    registration_number: str
    lot_number: str
    metrics: Metrics
    npk: str
    warranty: str
    n: float
    p: float
    k: float
    verified: bool


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
    micronutrients: ValuesObjects
    ingredients: ValuesObjects
    specifications: Specifications
    first_aid: SubLabel
    guaranteed_analysis: List[Value]


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
            "ingredients_en",
            "specifications_en",
            "first_aid_en",
            "cautions_fr",
            "instructions_fr",
            "micronutrients_fr",
            "ingredients_fr",
            "specifications_fr",
            "first_aid_fr",
            "guaranteed_analysis"
        ]
        missing_keys = []
        for key in requiered_keys:
            if key not in analysis_form:
                missing_keys.append(key)
        if len(missing_keys) > 0:
            raise MissingKeyError(missing_keys)
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
        weights : List[Metric] = []
        for i in range(len(analysis_form["weight"])):
            weights.append(Metric(unit=analysis_form["weight"][i]["unit"], value=analysis_form["weight"][i]["value"]))
        metrics = Metrics(
            weight=weights,
            volume=Metric(unit=analysis_form["volume"]["unit"], value=analysis_form["volume"]["value"]),
            density=Metric(unit=analysis_form["density"]["unit"], value=analysis_form["density"]["value"])
        )
        product = ProductInformation(
            name=analysis_form["fertiliser_name"],
            registration_number=analysis_form["registration_number"],
            lot_number=analysis_form["lot_number"],
            metrics=metrics,
            npk=analysis_form["npk"],
            warranty=analysis_form["warranty"],
            n=npk[0],
            p=npk[1],
            k=npk[2],
            verified=False
        )

        cautions = SubLabel(
            en=analysis_form["cautions_en"],
            fr=analysis_form["cautions_fr"]
        )

        instructions = SubLabel(
            en=analysis_form["instructions_en"],
            fr=analysis_form["instructions_fr"]
        )
        micro_en: List[Value] = []
        micro_fr: List[Value] = []
        for i in range(len(analysis_form["micronutrients_en"])):
                micro_en.append(Value(unit= None if analysis_form["micronutrients_en"][i]["unit"] == "" else analysis_form["micronutrients_en"][i]["unit"], value = None if analysis_form["micronutrients_fr"][i]["value"] == "" else analysis_form["micronutrients_fr"][i]["value"], name=analysis_form["micronutrients_en"][i]["nutrient"]))
        for i in range(len(analysis_form["micronutrients_fr"])):
                micro_fr.append(Value(unit= None if analysis_form["micronutrients_fr"][i]["unit"] == "" else analysis_form["micronutrients_fr"][i]["unit"], value = None if analysis_form["micronutrients_fr"][i]["value"] == "" else analysis_form["micronutrients_fr"][i]["value"], name=analysis_form["micronutrients_fr"][i]["nutrient"]))
        micronutrients = ValuesObjects(
            en=micro_en,
            fr=micro_fr
        )
        ingredients_en : List[Value] = []
        ingredients_fr : List[Value] = []
        for i in range(len(analysis_form["ingredients_en"])):
            ingredients_en.append(Value(unit=None if analysis_form["ingredients_en"][i]["unit"] == "" else analysis_form["ingredients_en"][i]["unit"], value=None if analysis_form["ingredients_en"][i]["value"] == "" else analysis_form["ingredients_en"][i]["value"], name=analysis_form["ingredients_en"][i]["nutrient"]))
        for i in range(len(analysis_form["ingredients_fr"])):
            ingredients_fr.append(Value(unit=None if analysis_form["ingredients_fr"][i]["unit"] == "" else analysis_form["ingredients_fr"][i]["unit"], value=None if analysis_form["ingredients_fr"][i]["value"] == "" else analysis_form["ingredients_fr"][i]["value"], name=analysis_form["ingredients_fr"][i]["nutrient"]))
        ingredients = ValuesObjects(
            en=ingredients_en,
            fr=ingredients_fr
        )

        specifications = Specifications(
            en=extract_specifications(analysis_form["specifications_en"]),
            fr=extract_specifications(analysis_form["specifications_fr"])
        )

        first_aid = SubLabel(
            en=analysis_form["first_aid_en"],
            fr=analysis_form["first_aid_fr"]
        )

        guaranteed : List[Value] = []
        for i in range(len(analysis_form["guaranteed_analysis"])):
            guaranteed.append(Value(unit=None if analysis_form["guaranteed_analysis"][i]["unit"] == "" else analysis_form["guaranteed_analysis"][i]["unit"], value=None if analysis_form["guaranteed_analysis"][i]["value"] == "" else analysis_form["guaranteed_analysis"][i]["value"], name=analysis_form["guaranteed_analysis"][i]["nutrient"]))


        inspection_formatted = Inspection(
            company=company,
            manufacturer=manufacturer,
            product=product,
            cautions=cautions,
            instructions=instructions,
            micronutrients=micronutrients,
            ingredients=ingredients,
            specifications=specifications,
            first_aid=first_aid,
            guaranteed_analysis=guaranteed
        )
        Inspection(**inspection_formatted.model_dump())
    except MissingKeyError as e:
        raise MissingKeyError(f"Missing keys: {e}")
    except ValidationError as e:
        raise MetadataFormattingError("Error InspectionCreationError not created: "+ str(e)) from None
    # print(inspection_formatted.model_dump_json())
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
        res = Specification(humidity=specification["humidity"], ph=specification["ph"], solubility=specification["solubility"])
        output.append(res)
    return output
