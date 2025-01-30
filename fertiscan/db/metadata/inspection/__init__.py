"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects.
The metadata is generated in a json format and is used to store the metadata in the database.

"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import (
    UUID4,
    AliasChoices,
    BaseModel,
    Field,
    ValidationError,
    model_validator,
)

from fertiscan.db.metadata.errors import (
    BuildInspectionExportError,
    BuildInspectionImportError,
    MetadataError,
    NPKError,
)
from fertiscan.db.queries import (
    ingredient,
    inspection,
    label,
    metric,
    nutrients,
    organization,
    registration_number,
    sub_label,
)
from fertiscan.db.queries.errors import QueryError


class ValidatedModel(BaseModel):
    @model_validator(mode="before")
    def handle_none(cls, values):
        if values is None:
            return {}
        return values


class OrganizationInformation(ValidatedModel):
    id: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None


class Value(ValidatedModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    name: str | None = Field(None, validation_alias=AliasChoices("name", "nutrient"))
    edited: Optional[bool] = False


class Title(ValidatedModel):
    en: Optional[str] = None
    fr: Optional[str] = None


class GuaranteedAnalysis(ValidatedModel):
    title: Title | None = None
    is_minimal: Optional[bool] = False
    en: List[Value] = []
    fr: List[Value] = []


class ValuesObjects(ValidatedModel):
    en: List[Value] = []
    fr: List[Value] = []


class SubLabel(ValidatedModel):
    en: List[str] = []
    fr: List[str] = []


class Metric(ValidatedModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    edited: Optional[bool] = False


class Metrics(ValidatedModel):
    weight: Optional[List[Metric]] = []
    volume: Optional[Metric] = Metric()
    density: Optional[Metric] = Metric()


class RegistrationNumber(ValidatedModel):
    registration_number: str | None = None
    is_an_ingredient: bool | None = None
    edited: Optional[bool] = False


class ProductInformation(ValidatedModel):
    name: str | None = None
    label_id: str | None = None
    lot_number: str | None = None
    metrics: Metrics | None = Metrics()
    npk: str | None = None
    warranty: str | None = None
    n: float | None = None
    p: float | None = None
    k: float | None = None
    verified: Optional[bool] = False
    registration_numbers: List[RegistrationNumber] | None = []
    record_keeping: Optional[bool] = None


class Specification(ValidatedModel):
    humidity: float | None = None
    ph: float | None = None
    solubility: float | None = None
    edited: Optional[bool] = False


class Specifications(ValidatedModel):
    en: List[Specification]
    fr: List[Specification]


# Awkwardly named so to avoid name conflict this represents the inspection object in the database
# and not the inspection object used as a form on the application
class DBInspection(ValidatedModel):
    id: UUID4
    verified: bool = False
    upload_date: datetime | None = None
    updated_at: datetime | None = None
    inspector_id: UUID4 | None = None
    label_info_id: UUID4 | None = None
    sample_id: UUID4 | None = None
    picture_set_id: UUID4 | None = None
    inspection_comment: str | None = None


class Inspection(ValidatedModel):
    inspection_id: Optional[str] = None
    inspector_id: Optional[str] = None
    inspection_comment: Optional[str] = None
    verified: Optional[bool] = False
    company: Optional[OrganizationInformation] = OrganizationInformation()
    manufacturer: Optional[OrganizationInformation] = OrganizationInformation()
    product: ProductInformation
    cautions: SubLabel
    instructions: SubLabel
    guaranteed_analysis: GuaranteedAnalysis
    registration_numbers: Optional[List[RegistrationNumber]] = []
    ingredients: ValuesObjects


class RegistrationType(str, Enum):
    INGREDIENT = "ingredient_component"
    FERTILIZER = "fertilizer_product"


class PipelineRegistrationNumber(BaseModel):
    identifier: str | None = Field(None, pattern=r"^\d{7}[A-Z]$")
    type: RegistrationType | None = None


class PipelineGuaranteedAnalysis(BaseModel):
    title: str | None = None
    nutrients: list[Value] | None = []
    is_minimal: bool | None = None


class LabelData(BaseModel):
    organizations: list[OrganizationInformation] | None
    fertilizer_name: str | None = Field(
        ..., validation_alias=AliasChoices("fertilizer_name", "fertiliser_name")
    )
    registration_number: list[PipelineRegistrationNumber]
    lot_number: str | None
    weight: list[Metric] | None
    density: Metric | None
    volume: Metric | None
    npk: str | None
    guaranteed_analysis_en: PipelineGuaranteedAnalysis | None
    guaranteed_analysis_fr: PipelineGuaranteedAnalysis | None
    cautions_en: list[str] | None
    cautions_fr: list[str] | None
    instructions_en: list[str] | None
    instructions_fr: list[str] | None
    ingredients_en: list[Value] | None
    ingredients_fr: list[Value] | None


def build_inspection_import(analysis_form: dict, user_id) -> str:
    """
    This funtion build an inspection json object from the pipeline of digitalization analysis.
    This serves as the metadata for the inspection object in the database.

    Parameters:
    - analysis_form: (dict) The digitalization of the label.

    Returns:
    - The inspection db object in a string format.
    """
    try:
        labelData = LabelData.model_validate(analysis_form)

        npk = extract_npk(labelData.npk)

        company = labelData.organizations[0]
        manufacturer = labelData.organizations[1]

        metrics = Metrics(
            weight=labelData.weight, volume=labelData.volume, density=labelData.density
        )

        reg_numbers = [
            RegistrationNumber(
                registration_number=r.identifier,
                is_an_ingredient=(r.type == RegistrationType.INGREDIENT),
            )
            for r in labelData.registration_number
        ]

        # record keeping is set as null since the pipeline cant output a value yet
        product = ProductInformation(
            name=labelData.fertilizer_name,
            lot_number=labelData.lot_number,
            metrics=metrics,
            registration_numbers=reg_numbers,
            npk=labelData.npk,
            warranty=None,
            n=npk[0],
            p=npk[1],
            k=npk[2],
            verified=False,
            record_keeping=None,
        )

        cautions = SubLabel(
            en=labelData.cautions_en,
            fr=labelData.cautions_fr,
        )

        instructions = SubLabel(
            en=labelData.instructions_en,
            fr=labelData.instructions_fr,
        )

        # Commented and kept as reference for future implementation, but not used at the moment
        # micro_en: list[Value] = [
        #     Value(
        #         unit=nutrient.get("unit") or None,
        #         value=nutrient.get("value") or None,
        #         name=nutrient.get("nutrient"),
        #     )
        #     for nutrient in analysis_form.get("micronutrients_en", [])
        # ]
        # micro_fr: list[Value] = [
        #     Value(
        #         unit=nutrient.get("unit") or None,
        #         value=nutrient.get("value") or None,
        #         name=nutrient.get("nutrient"),
        #     )
        #     for nutrient in analysis_form.get("micronutrients_fr", [])
        # ]
        # micronutrients = ValuesObjects(en=micro_en, fr=micro_fr)

        ingredients = ValuesObjects(
            en=labelData.ingredients_en, fr=labelData.ingredients_fr
        )

        # specifications = Specifications(
        #     en=[
        #         Specification(**s)
        #         for s in analysis_form.get("specifications_en", [])
        #         if any(value is not None for _, value in s.items())
        #     ],
        #     fr=[
        #         Specification(**s)
        #         for s in analysis_form.get("specifications_fr", [])
        #         if any(value is not None for _, value in s.items())
        #     ],
        # )

        # first_aid = SubLabel(
        #     en=analysis_form.get("first_aid_en", []),
        #     fr=analysis_form.get("first_aid_fr", []),
        # )

        guaranteed = GuaranteedAnalysis(
            title=Title(
                en=labelData.guaranteed_analysis_en.title,
                fr=labelData.guaranteed_analysis_fr.title,
            ),
            is_minimal=labelData.guaranteed_analysis_en.is_minimal
            or labelData.guaranteed_analysis_fr.is_minimal,
            en=labelData.guaranteed_analysis_en.nutrients,
            fr=labelData.guaranteed_analysis_fr.nutrients,
        )

        inspection_formatted = Inspection(
            inspector_id=str(user_id),
            company=company,
            manufacturer=manufacturer,
            product=product,
            cautions=cautions,
            instructions=instructions,
            guaranteed_analysis=guaranteed,
            registration_numbers=reg_numbers,
            ingredients=ingredients,
        )
        Inspection(**inspection_formatted.model_dump())
        return inspection_formatted.model_dump_json()
    except MetadataError:
        raise
    except ValidationError as e:
        raise BuildInspectionImportError(f"Validation error: {e}") from e
    except Exception as e:
        raise BuildInspectionImportError(f"Unexpected error: {e}") from e


def build_inspection_export(cursor, inspection_id) -> str:
    """
    This funtion build an inspection json object from the database.
    """
    try:
        label_info_id = inspection.get_inspection(cursor, inspection_id)[
            inspection.LABEL_INFO_ID
        ]
        # get the label information
        product_info = label.get_label_information_json(cursor, label_info_id)
        product_info = ProductInformation(**product_info)

        # get metrics information
        metrics = metric.get_metrics_json(cursor, label_info_id)
        metrics = Metrics.model_validate(metrics)
        metrics.volume = metrics.volume or Metric()
        metrics.density = metrics.density or Metric()
        product_info.metrics = metrics

        # Retrieve the registration numbers
        reg_numbers = registration_number.get_registration_numbers_json(
            cursor, label_info_id
        )
        reg_number_model_list = []
        for reg_number in reg_numbers["registration_numbers"]:
            reg_number_model_list.append(RegistrationNumber.model_validate(reg_number))
        product_info.registration_numbers = reg_number_model_list

        # get the organizations information (Company and Manufacturer)
        org = organization.get_organizations_info_json(cursor, label_info_id)
        manufacturer = OrganizationInformation.model_validate(org.get("manufacturer"))
        company = OrganizationInformation.model_validate(org.get("company"))

        # Get all the sub labels
        sub_labels = sub_label.get_sub_label_json(cursor, label_info_id)
        cautions = SubLabel.model_validate(sub_labels.get("cautions"))
        instructions = SubLabel.model_validate(sub_labels.get("instructions"))

        # Get the guaranteed analysis
        guaranteed_analysis = nutrients.get_guaranteed_analysis_json(
            cursor, label_info_id
        )
        guaranteed_analysis = GuaranteedAnalysis.model_validate(guaranteed_analysis)

        # Get the ingredients but if the fertilizer is record keeping, the ingredients are not displayed
        if not product_info.record_keeping:
            ingredients = ingredient.get_ingredient_json(cursor, label_info_id)
        else:
            ingredients = ValuesObjects(en=[], fr=[])

        # Get the inspection information
        db_inspection = inspection.get_inspection_dict(cursor, inspection_id)
        db_inspection = DBInspection.model_validate(db_inspection)

        inspection_formatted = Inspection(
            inspection_id=str(inspection_id),
            inspector_id=str(db_inspection.inspector_id),
            inspection_comment=db_inspection.inspection_comment,
            cautions=cautions,
            company=company,
            guaranteed_analysis=guaranteed_analysis,
            instructions=instructions,
            manufacturer=manufacturer,
            product=product_info,
            verified=db_inspection.verified,
            registration_numbers=reg_number_model_list,
            ingredients=ingredients,
        )

        return inspection_formatted.model_dump_json()
    except QueryError as e:
        raise BuildInspectionExportError(f"Error fetching data: {e}") from e
    except Exception as e:
        raise BuildInspectionImportError(f"Unexpected error: {e}") from e


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
    try:
        if npk is None or npk == "" or len(npk) < 5:
            return [None, None, None]
        npk_formated = npk.replace("N", "-")
        npk_formated = npk_formated.replace("P", "-")
        npk_formated = npk_formated.replace("K", "-")
        npk_reformated = npk.split("-")
        for i in range(len(npk_reformated)):
            if not npk_reformated[i].isnumeric():
                NPKError(
                    "NPK values must be numeric. Issue with: "
                    + npk_reformated[i]
                    + "in the NPK string: "
                    + npk
                )
        return [
            float(npk_reformated[0]),
            float(npk_reformated[1]),
            float(npk_reformated[2]),
        ]
    except NPKError:
        raise
    except Exception as e:
        raise NPKError(f"Unexpected error: {e}") from e
