"""
This module contains the function to generate the metadata necessary to interact with the database and the other layers of Fertiscan for all the inspection related objects.
The metadata is generated in a json format and is used to store the metadata in the database.

"""

from pydantic import ValidationError

from fertiscan.db.models import (
    DBInspection,
    GuaranteedAnalysis,
    Inspection,
    Metric,
    Metrics,
    OrganizationInformation,
    ProductInformation,
    SubLabel,
    Title,
    Value,
)
from fertiscan.db.queries import (
    ingredient,
    inspection,
    label,
    metric,
    nutrients,
    organization,
    specification,
    sub_label,
)


class MissingKeyError(Exception):
    pass


class NPKError(Exception):
    pass


class MetadataFormattingError(Exception):
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
            "cautions_en",
            "instructions_en",
            "cautions_fr",
            "instructions_fr",
            "guaranteed_analysis_fr",
            "guaranteed_analysis_en",
        ]
        missing_keys = []
        for key in requiered_keys:
            if key not in analysis_form:
                missing_keys.append(key)
        if len(missing_keys) > 0:
            raise MissingKeyError(missing_keys)

        npk = extract_npk(analysis_form.get("npk"))

        company = OrganizationInformation(
            name=analysis_form.get("company_name"),
            address=analysis_form.get("company_address"),
            website=analysis_form.get("company_website"),
            phone_number=analysis_form.get("company_phone_number"),
        )
        manufacturer = OrganizationInformation(
            name=analysis_form.get("manufacturer_name"),
            address=analysis_form.get("manufacturer_address"),
            website=analysis_form.get("manufacturer_website"),
            phone_number=analysis_form.get("manufacturer_phone_number"),
        )

        weights: list[Metric] = [
            Metric(
                unit=weight.get("unit"),
                value=weight.get("value"),
            )
            for weight in analysis_form.get("weight", [])
        ]

        volume_obj = Metric()
        if volume := analysis_form.get("volume"):
            volume_obj = Metric(unit=volume.get("unit"), value=volume.get("value"))

        density_obj = Metric()
        if density := analysis_form.get("density"):
            density_obj = Metric(unit=density.get("unit"), value=density.get("value"))

        metrics = Metrics(weight=weights, volume=volume_obj, density=density_obj)

        product = ProductInformation(
            name=analysis_form.get("fertiliser_name"),
            registration_number=analysis_form.get("registration_number"),
            lot_number=analysis_form.get("lot_number"),
            metrics=metrics,
            npk=analysis_form.get("npk"),
            warranty=analysis_form.get("warranty"),
            n=npk[0],
            p=npk[1],
            k=npk[2],
            verified=False,
        )

        cautions = SubLabel(
            en=analysis_form.get("cautions_en", []),
            fr=analysis_form.get("cautions_fr", []),
        )

        instructions = SubLabel(
            en=analysis_form.get("instructions_en", []),
            fr=analysis_form.get("instructions_fr", []),
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

        # ingredients_en: list[Value] = [
        #     Value(
        #         unit=ingredient.get("unit") or None,
        #         value=ingredient.get("value") or None,
        #         name=ingredient.get("nutrient"),
        #     )
        #     for ingredient in analysis_form.get("ingredients_en", [])
        # ]
        # ingredients_fr: list[Value] = [
        #     Value(
        #         unit=ingredient.get("unit") or None,
        #         value=ingredient.get("value") or None,
        #         name=ingredient.get("nutrient"),
        #     )
        #     for ingredient in analysis_form.get("ingredients_fr", [])
        # ]
        # ingredients = ValuesObjects(en=ingredients_en, fr=ingredients_fr)

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

        guaranteed_fr: list[Value] = [
            Value(
                unit=item.get("unit") or None,
                value=item.get("value") or None,
                name=item.get("nutrient"),
            )
            for item in analysis_form.get("guaranteed_analysis_fr", []).get(
                "nutrients", []
            )
        ]

        guaranteed_en: list[Value] = [
            Value(
                unit=item.get("unit") or None,
                value=item.get("value") or None,
                name=item.get("nutrient"),
            )
            for item in analysis_form.get("guaranteed_analysis_en", []).get(
                "nutrients", []
            )
        ]

        guaranteed = GuaranteedAnalysis(
            title=Title(
                en=analysis_form.get("guaranteed_analysis_en", {}).get("title"),
                fr=analysis_form.get("guaranteed_analysis_fr", {}).get("title"),
            ),
            # is_minimal=analysis_form.get("guaranteed_analysis_is_minimal"),
            is_minimal=None,  # Not processed yet by the pipeline
            en=guaranteed_en,
            fr=guaranteed_fr,
        )

        inspection_formatted = Inspection(
            company=company,
            manufacturer=manufacturer,
            product=product,
            cautions=cautions,
            instructions=instructions,
            guaranteed_analysis=guaranteed,
        )
        Inspection(**inspection_formatted.model_dump())
    except MissingKeyError as e:
        raise MissingKeyError("Missing keys:" + str(e))
    except ValidationError as e:
        print(analysis_form.get("cautions_en", []))
        print(analysis_form.get("cautions_fr", []))
        raise MetadataFormattingError(
            "Error InspectionCreationError not created: " + str(e)
        ) from None
    # print(inspection_formatted.model_dump_json())
    return inspection_formatted.model_dump_json()


def build_inspection_export(cursor, inspection_id, label_info_id) -> str:
    """
    This funtion build an inspection json object from the database.
    """
    try:
        # get the label information
        product_info = label.get_label_information_json(cursor, label_info_id)
        product_info = ProductInformation(**product_info)

        # get metrics information
        metrics = metric.get_metrics_json(cursor, label_info_id)
        metrics = Metrics.model_validate(metrics)
        metrics.volume = metrics.volume or Metric()
        metrics.density = metrics.density or Metric()
        product_info.metrics = metrics

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

        # Get the inspection information
        db_inspection = inspection.get_inspection_dict(cursor, inspection_id)
        db_inspection = DBInspection.model_validate(db_inspection)

        inspection_formatted = Inspection(
            inspection_id=str(inspection_id),
            inspection_comment=db_inspection.inspection_comment,
            cautions=cautions,
            company=company,
            guaranteed_analysis=guaranteed_analysis,
            instructions=instructions,
            manufacturer=manufacturer,
            product=product_info,
            verified=db_inspection.verified,
        )

        return inspection_formatted.model_dump_json()
    except (
        label.LabelInformationNotFoundError
        or metric.MetricNotFoundError
        or organization.OrganizationNotFoundError
        or sub_label.SubLabelNotFoundError
        or ingredient.IngredientNotFoundError
        or nutrients.MicronutrientNotFoundError
        or nutrients.GuaranteedNotFoundError
        or specification.SpecificationNotFoundError
    ):
        raise
    except Exception as e:
        raise MetadataFormattingError(
            "Error Inspection Form not created: " + str(e)
        ) from e


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
