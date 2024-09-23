import re

from pydantic import BaseModel, Field, field_validator


def extract_first_number(string: str) -> str | None:
    if string is not None:
        match = re.search(r"\d+(\.\d+)?", string)
        if match:
            return match.group()
    return None


class NutrientValue(BaseModel):
    nutrient: str
    value: float | None = None
    unit: str | None = None

    @field_validator("value", mode="before", check_fields=False)
    def convert_value(cls, v):
        if isinstance(v, bool):
            return None
        elif isinstance(v, (int, float)):
            return str(v)
        elif isinstance(v, (str)):
            return extract_first_number(v)
        return None


class PipelineValue(BaseModel):
    value: float | None
    unit: str | None

    @field_validator("value", mode="before", check_fields=False)
    def convert_value(cls, v):
        if isinstance(v, bool):
            return None
        elif isinstance(v, (int, float)):
            return str(v)
        elif isinstance(v, (str)):
            return extract_first_number(v)
        return None


class PipelineGuaranteedAnalysis(BaseModel):
    title: str | None = None
    nutrients: list[NutrientValue] = []

    @field_validator(
        "nutrients",
        mode="before",
    )
    def replace_none_with_empty_list(cls, v):
        if v is None:
            v = []
        return v


class Specification(BaseModel):
    humidity: float | None = Field(..., alias="humidity")
    ph: float | None = Field(..., alias="ph")
    solubility: float | None

    @field_validator("humidity", "ph", "solubility", mode="before", check_fields=False)
    def convert_specification_values(cls, v):
        if isinstance(v, bool):
            return None
        elif isinstance(v, (int, float)):
            return str(v)
        elif isinstance(v, (str)):
            return extract_first_number(v)
        return None


class FertilizerInspection(BaseModel):
    company_name: str | None = None
    company_address: str | None = None
    company_website: str | None = None
    company_phone_number: str | None = None
    manufacturer_name: str | None = None
    manufacturer_address: str | None = None
    manufacturer_website: str | None = None
    manufacturer_phone_number: str | None = None
    fertiliser_name: str | None = None
    registration_number: str | None = None
    lot_number: str | None = None
    weight: list[PipelineValue] = []
    density: PipelineValue | None = None
    volume: PipelineValue | None = None
    npk: str | None = Field(None)
    guaranteed_analysis_en: PipelineGuaranteedAnalysis | None = None
    guaranteed_analysis_fr: PipelineGuaranteedAnalysis | None = None
    cautions_en: list[str] | None = None
    cautions_fr: list[str] | None = None
    instructions_en: list[str] = []
    instructions_fr: list[str] = []
    ingredients_en: list[NutrientValue] = []
    ingredients_fr: list[NutrientValue] = []

    @field_validator("npk", mode="before")
    def validate_npk(cls, v):
        if v is not None:
            pattern = re.compile(r"^\d+(\.\d+)?-\d+(\.\d+)?-\d+(\.\d+)?$")
            if not pattern.match(v):
                return None
        return v

    @field_validator(
        "cautions_en",
        "cautions_fr",
        "instructions_en",
        "instructions_fr",
        "weight",
        mode="before",
    )
    def replace_none_with_empty_list(cls, v):
        if v is None:
            v = []
        return v

    class Config:
        populate_by_name = True
