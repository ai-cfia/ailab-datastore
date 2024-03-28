from datetime import date
from pydantic import BaseModel


class client_data(BaseModel):
    client_email: str
    client_expertise: str


class seed_data(BaseModel):
    seed_id: int
    seed_family: str
    seed_genus: str
    seed_species: str


class image_data_picture_set(BaseModel):
    number_of_images: int


class audit_trail(BaseModel):
    upload_date: date
    edited_by: str
    edit_date: date
    change_log: str
    access_log: str
    privacy_flag: bool


class metadata(BaseModel):
    upload_date: date


class image_data(BaseModel):
    format: str
    height: int
    width: int
    resolution: str
    source: str
    parent: str


class quality_check(BaseModel):
    image_checksum: str
    upload_check: bool
    valid_data: bool
    error_type: str
    quality_score: float


class user_data(BaseModel):
    description: str
    number_of_seeds: int
    zoom: float


class picture_set(BaseModel):
    client_data: client_data
    image_data: image_data


class Ppicture_set(BaseModel):
    image_data_picture_set: image_data_picture_set
    audit_trail: audit_trail


class Picture(BaseModel):
    user_data: user_data


class PPicture(BaseModel):
    user_data: user_data
    metadata: metadata
    image_data: image_data
    quality_check: quality_check


class ClientFeedback(BaseModel):
    correctIdentification: bool
    historicalComparison: str
