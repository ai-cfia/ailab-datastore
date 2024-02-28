from datetime import date
from pydantic import BaseModel
from typing import List
import yaml
import json
import os
import psycopg
from azure.storage.blob import BlobServiceClient
from azure.core import paging
from PIL import Image

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
    

# def is_json_empty(filename):
#     with open(filename) as json_file:
#         data = json.load(json_file)
#         return len(data) == 0

# def fill_index_system(filename):
#     if is_json_empty(filename):
#         with open(filename, 'w') as json_file:
#             json.dump(default_json_data, json_file, indent=2)
    
# def is_yaml_file(file_path):
#     _, file_extension = os.path.splitext(file_path)
#     return file_extension.lower() == '.yaml'

container_URL="https://seedgroup.blob.core.windows.net/sas1706-tagarno-exp2-3-15species"

  
    
if __name__ == "__main__":
    print("test")
