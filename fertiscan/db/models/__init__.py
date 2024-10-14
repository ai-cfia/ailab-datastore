from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, model_validator


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
    name: Optional[str] = None
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


class ProductInformation(ValidatedModel):
    name: str | None = None
    label_id: str | None = None
    registration_number: str | None = None
    lot_number: str | None = None
    metrics: Metrics | None = Metrics()
    npk: str | None = None
    warranty: str | None = None
    n: float | None = None
    p: float | None = None
    k: float | None = None


class Specification(ValidatedModel):
    humidity: float | None = None
    ph: float | None = None
    solubility: float | None = None
    edited: Optional[bool] = False


class Specifications(ValidatedModel):
    en: List[Specification]
    fr: List[Specification]


# Awkwardly named so to avoid name conflict
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
    inspection_comment: Optional[str] = None
    verified: Optional[bool] = False
    company: Optional[OrganizationInformation] = OrganizationInformation()
    manufacturer: Optional[OrganizationInformation] = OrganizationInformation()
    product: ProductInformation
    cautions: SubLabel
    instructions: SubLabel
    guaranteed_analysis: GuaranteedAnalysis


class Fertilizer(BaseModel):
    id: UUID4
    name: str | None = None
    registration_number: str | None = Field(None, pattern=r"^\d{7}[A-Z]$")
    upload_date: datetime
    update_at: datetime
    latest_inspection_id: UUID4 | None
    owner_id: UUID4 | None
