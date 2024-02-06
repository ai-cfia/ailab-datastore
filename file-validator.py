from datetime import date
from pydantic import BaseModel
from typing import List
import yaml
import json

def fill_index_system(filename):
     if is_json_empty(filename):
        with open(filename, 'w') as json_file:
            json.dump(default_json_data, json_file, indent=2)

class ClientData(BaseModel):
    clientEmail: str
    clientExpertise: int

class SeedCharacteristics(BaseModel):
    color: str
    shape: str
    size: str
    texture: str
    pattern: str
    weight: float
    seedCount: int
    distinctFeatures: str

class SampleInformation(BaseModel):
    geoLocation: str
    region: str
    temperature: float
    humidity: float
    soil: str

class ClientFeedback(BaseModel):
    correctIdentification: bool
    historicalComparison: str

class SeedData(BaseModel):
    seedID: int
    seedFamily: str
    seedGenus: str
    seedSpecies: str
    seedCharacteristics: SeedCharacteristics
    sampleInformation: SampleInformation
    clientFeedback: ClientFeedback
    
class ImageData(BaseModel):
    numberOfImages: int
    seeds: list

class MetaData(BaseModel):
    uploadDate: date
    clientData: ClientData
    imageData: ImageData
    
class Data(BaseModel):
    primary_data: MetaData
    
# Load YAML template
with open('index-mockData.yaml', 'r') as file:
    yaml_data = yaml.safe_load(file)

# Validate and parse YAML data using Pydantic model
data = MetaData(**yaml_data)

# Serialize data to JSON
json_data = data.json()

print(json_data)