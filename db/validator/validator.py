from datetime import date
from pydantic import BaseModel


class ClientData(BaseModel):
    clientEmail: str
    clientExpertise: str


class SeedData(BaseModel):
    seedID: int
    seedFamily: str
    seedGenus: str
    seedSpecies: str


class ImageDataindex(BaseModel):
    numberOfImages: int


class AuditTrail(BaseModel):
    uploadDate: date
    editedBy: str
    editDate: date
    changeLog: str
    accessLog: str
    privacyFlag: bool


class Info(BaseModel):
    userID: int
    uploadDate: date
    indexID: int


class ImageData(BaseModel):
    format: str
    height: int
    width: int
    resolution: str
    source: str
    parent: str


class QualityCheck(BaseModel):
    imageChecksum: str
    uploadCheck: bool
    validData: bool
    errorType: str
    dataQualityScore: float


class UserData(BaseModel):
    description: str
    numberOfSeeds: int
    zoom: float


class Index(BaseModel):
    clientData: ClientData
    imageData: ImageDataindex
    seedData: SeedData


class PIndex(BaseModel):
    clientData: ClientData
    imageData: ImageDataindex
    seedData: SeedData
    auditTrail: AuditTrail


class Picture(BaseModel):
    userData: UserData


class PPicture(BaseModel):
    userData: UserData
    info: Info
    imageData: ImageData
    qualityCheck: QualityCheck


class ClientFeedback(BaseModel):
    correctIdentification: bool
    historicalComparison: str
