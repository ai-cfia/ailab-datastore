from datetime import date
from pydantic import BaseModel
import uuid

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
    number_of_seeds: int
    zoom: float


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

def is_valid_uuid(val):
    """
    This validates if a given string is a UUID
    """
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False