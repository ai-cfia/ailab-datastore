from datetime import datetime
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, model_validator


class ValidatedModel(BaseModel):
    @model_validator(mode="before")
    def handle_none(cls, values):
        if values is None:
            return {}
        return values


class LocatedOrganizationInformation(ValidatedModel):
    id: str | UUID4 | None = None
    name: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    phone_number: Optional[str] = None


class OrganizationInformation(ValidatedModel):
    id: UUID4
    name: str | None = None
    website: str | None = None
    phone_number: str | None = None
    location_id: UUID4 | None = None
    edited: bool | None = False


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
    company: Optional[LocatedOrganizationInformation] = LocatedOrganizationInformation()
    manufacturer: Optional[LocatedOrganizationInformation] = (
        LocatedOrganizationInformation()
    )
    product: ProductInformation
    cautions: SubLabel
    instructions: SubLabel
    guaranteed_analysis: GuaranteedAnalysis


class Fertilizer(ValidatedModel):
    id: UUID4
    name: str | None = None
    registration_number: str | None = Field(None, pattern=r"^\d{7}[A-Z]$")
    upload_date: datetime
    update_at: datetime
    latest_inspection_id: UUID4 | None
    owner_id: UUID4 | None


class Location(ValidatedModel):
    id: UUID4
    name: str | None = None
    address: str
    region_id: UUID4 | None
    owner_id: UUID4 | None


class Region(ValidatedModel):
    id: UUID4
    name: str
    province_id: int | None = None


class Province(ValidatedModel):
    id: int | None = None
    name: str


class FullLocation(ValidatedModel):
    id: UUID4
    name: str | None = None
    address: str
    owner_id: UUID4 | None = None
    region_id: UUID4 | None = None
    region_name: str | None = None
    province_id: int | None = None
    province_name: str | None = None


class FullRegion(ValidatedModel):
    id: UUID4
    name: str
    province_name: str | None = None


class CompanyManufacturer(ValidatedModel):
    company: LocatedOrganizationInformation | None = LocatedOrganizationInformation()
    manufacturer: LocatedOrganizationInformation | None = (
        LocatedOrganizationInformation()
    )


class FullOrganization(ValidatedModel):
    id: UUID4
    name: str | None = None
    website: str | None = None
    phone_number: str | None = None
    location_id: UUID4 | None = None
    location_name: str | None = None
    location_address: str | None = None
    region_id: UUID4 | None = None
    region_name: str | None = None
    province_id: int | None = None
    province_name: str | None = None


class Guaranteed(ValidatedModel):
    id: UUID4
    read_name: str | None = None
    value: float | None = None
    unit: str | None = None
    language: str | None = None
    element_id: int | None = None
    label_id: UUID4 | None = None
    edited: bool = False
    created_at: datetime | None = None


class FullGuaranteed(ValidatedModel):
    id: UUID4
    read_name: str | None = None
    value: float | None = None
    unit: str | None = None
    element_name_fr: str | None = None
    element_name_en: str | None = None
    element_symbol: str | None = None
    edited: bool = False
    reading: str | None = None


class ElementCompound(ValidatedModel):
    id: int
    number: int
    name_fr: str
    name_en: str
    symbol: str


class Unit(ValidatedModel):
    id: UUID4
    unit: str
    to_si_unit: float | None = None


class DBMetric(ValidatedModel):
    id: UUID4
    value: float | None = None
    unit_id: UUID4 | None = None
    edited: bool | None = None
    metric_type: str | None = None
    label_id: UUID4 | None = None


class FullMetric(ValidatedModel):
    id: UUID4
    value: float | None = None
    unit: str | None = None
    to_si_unit: float | None = None
    edited: bool | None = None
    metric_type: str | None = None
    label_id: UUID4 | None = None
    full_metric: str | None = None
