from datetime import date
from pydantic import BaseModel
from typing import List
import yaml
import json
import os

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

class ImageDataindex(BaseModel):
    numberOfImages: int
    
class ImageDatapic(BaseModel):
    description: string
    numberOfSeeds: int
    zoom: float


class Index(BaseModel):
    clientData: ClientData
    imageData: ImageDataindex
    seedData: SeedData
    
    
def is_yaml_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() == '.yaml'


    
def openIndex(path):
    if is_yaml_file(path):
        # Load YAML template
        with open(path, 'r') as file:
            yaml_data = yaml.safe_load(file)
    try: # Validate and parse YAML data using Pydantic model
        data = Index(**yaml_data)
    except Exception as error: # Error raised by Pydantic Validator
        print(error)
        
    else:
        json_data = data.json()
        print(json_data)
        #return(json_data)

if __name__ == "__main__":
    file_path = input("Path:")
    openIndex(file_path)