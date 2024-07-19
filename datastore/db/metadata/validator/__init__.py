import uuid
from datetime import date
from typing import Optional

from pydantic import BaseModel, ValidationError


class ClientData(BaseModel):
    client_email: str
    client_expertise: str


class SeedData(BaseModel):
    seed_id: int
    seed_family: str
    seed_genus: str
    seed_species: str


class ImageDataPictureSet(BaseModel):
    number_of_images: int


class AuditTrail(BaseModel):
    upload_date: date
    edited_by: str
    edit_date: date
    change_log: str
    access_log: str
    privacy_flag: bool


class Metadata(BaseModel):
    upload_date: date


class ImageData(BaseModel):
    format: str
    height: int
    width: int
    resolution: str
    source: str
    parent: str


class QualityCheck(BaseModel):
    image_checksum: str
    upload_check: bool
    valid_data: bool
    error_type: str
    quality_score: float


class UserData(BaseModel):
    description: str
    number_of_seeds: Optional[int] = None
    zoom: Optional[float] = None


class PictureSet(BaseModel):
    client_data: ClientData
    image_data: ImageDataPictureSet


class ProcessedPictureSet(BaseModel):
    image_data_picture_set: ImageDataPictureSet
    audit_trail: AuditTrail


class Picture(BaseModel):
    user_data: UserData


class ProcessedPicture(BaseModel):
    user_data: UserData
    metadata: Metadata
    image_data: ImageData
    quality_check: QualityCheck


class ClientFeedback(BaseModel):
    correctIdentification: bool
    historicalComparison: str


class AnalysisForm(BaseModel):
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
    weight_kg: float | None = None
    weight_lb: float | None = None
    density: float | None = None
    volume: float | None = None
    npk: str | None = None
    warranty: str | None = None
    cautions_en: list[str] | None = None
    instructions_en: list[str] | None = None
    micronutrients_en: list[str] | None = None
    organic_ingredients_en: list[str] | None = None
    inert_ingredients_en: list[str] | None = None
    specifications_en: list[str] | None = None
    first_aid_en: list[str] | None = None
    cautions_fr: list[str] | None = None
    instructions_fr: list[str] | None = None
    micronutrients_fr: list[str] | None = None
    organic_ingredients_fr: list[str] | None = None
    inert_ingredients_fr: list[str] | None = None
    specifications_fr: list[str] | None = None
    first_aid_fr: list[str] | None = None
    guaranteed_analysis: list[str] | None = None
    verified: bool = False


def is_valid_uuid(val):
    """
    This validates if a given string is a UUID
    """
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False
    except ValidationError:
        # This is a useless catch present to remove the lint error of unused Validation Error
        return False
