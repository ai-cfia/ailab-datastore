from datetime import date
from pydantic import BaseModel
from typing import List
import yaml
import json
import os
from azure.storage.blob import BlobServiceClient
from PIL import Image

def fill_index_system(filename):
     if is_json_empty(filename):
        with open(filename, 'w') as json_file:
            json.dump(default_json_data, json_file, indent=2)

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

class Index(BaseModel):
    clientData: ClientData
    imageData: ImageDataindex
    seedData: SeedData
    
class PIndex(BaseModel):
    clientData: ClientData
    imageData: ImageDataindex
    seedData: SeedData
    auditTrail: AuditTrail
    
class UserData(BaseModel):
    description: str
    numberOfSeeds: int
    zoom: float    
    
class Picture(BaseModel):
    userData: UserData 
    
class ClientFeedback(BaseModel):
    correctIdentification: bool
    historicalComparison: str
    
    
def is_yaml_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() == '.yaml'

def manualMetaDataImport():
    #ask name for the folder
    folderName = input("Folder Name: ")
    os.makedirs(folderName)
    #build index
    nbPic=buildIndex(folderName)
    #for each picture in field
    zoomlevel = input("Zoom level for this index: ")
    seedNumber = input("Number of seed for this index: ")
    for x in range(nbPic):
        buildPicture(folderName,zoomlevel,seedNumber)

def buildIndex(output:str):
    # Ask for the url in the console

    # # Retrieve some client info from the URL

    # Ask Data (I dont have access to the data url atm)
    clientEmail=input("clientEmail: ")
    clientExpertise= input("Expertise: ")
    clientData=ClientData(clientEmail=clientEmail,clientExpertise=clientExpertise)
    nb=input("numberOfImages: ")
    imageData=ImageDataindex(numberOfImages=nb)
    seedID=input("SeedID: ")
    family = input("Family: ")
    genus = input("Genus: ")
    species= input("Species: ")
    seedData=SeedData(seedID=seedID,seedFamily=family,seedGenus=genus,seedSpecies=species)
    
    index = Index(clientData=clientData,imageData=imageData,seedData=seedData)
    name = input("File created, name: ")
    
    #createJsonIndex(index=index,name=name,output=output)
    indexJson=index.dict()
    sysData=IndexProcessing(openIndexSystem())
    indexJson.update(sysData)
    print(indexJson)
    createJsonIndex(index=indexJson,name=name,output=output)
    return nb


def buildPicture(output:str,number:int,level):
    # Ask for the url in the console

    # # Retrieve some client info from the URL

    # Ask Data (I dont have access to the data url atm)
    desc= ""
    nb=number
    zoom=level
    userData = UserData(description=desc,numberOfSeeds=nb,zoom=zoom)
    
    pic = Picture(UserData=userData)
    name = input("File created, name: ")
    
    createJsonPicture(pic=pic,name=name,output=output)

#Create Json form Picture data model
def createJsonPicture(pic:Picture,name:str,output:str):
    data = pic.dict()
    filePath = f'{output}/{name}.json'
    with open(filePath,'w') as json_file:
        json.dump(data,json_file,indent=2)
    
# Create Json from Index data model
def createJsonIndex(index,name: str,output:str):
    #data=index.dict()
    data = PIndex(**index)
    filePath = f'{output}/{name}.json'
    with open(filePath,'w') as json_file:
        json.dump(index,json_file,indent=2)
    
    
    
def openIndex(path):
    if is_yaml_file(path):
        # Load YAML template
        with open(path, 'r') as file:
            yaml_data = yaml.safe_load(file)
    try: # Validate and parse YAML data using Pydantic model
        data = Index(**yaml_data)
    except Exception as error: # Errtor raised by Pydantic Validator
        print(error)
        
    else:
        json_data = data.json()
        print(json_data)
        return(json_data)
    
def openIndexSystem():
    with open('index-template-system.json','r') as file:
        sysData=json.load(file)
        #print(sysData)
    return sysData

def IndexProcessing(jsonData: str):
    today = date.today()
    editedBy = "Francois Werbrouck" #not permanent, will be changed once the mass import is over
    editDate = date.today()
    change=""
    access=""
    privacy=False
    return IndexSystemPopulating(jsonData,today,editedBy,editDate,change,access,privacy)
    
def PictureProcessing(jsonData:str):
     #ajouter structure 
     today=date.today()
     userID=""
     indexID=""
     parent=""
     source=input("Picture link: ")
     format=".tiff"
     height=""
     width=""
     resolution=""
     return ""   
    
def IndexSystemPopulating(data,date:date,editedBy,editDate:date,changes:str,access,privacy):
    #print(data)
    data["auditTrail"]["uploadDate"]=date.strftime("%Y-%m-%d")
    data["auditTrail"]["editedBy"]=editedBy
    data["auditTrail"]["editDate"]=editDate.strftime("%Y-%m-%d")
    data["auditTrail"]["changeLog"]=changes
    data["auditTrail"]["accessLog"]=access
    data["auditTrail"]["privacyFlag"]=privacy
    return data

def folderProcessing(storage_url):
    # Parse the storage URL
    account_url = storage_url.split('/')[2]
    container_name = storage_url.split('/')[3]
    
    # Create a blob service client
    blob_service_client = BlobServiceClient(account_url=account_url)

    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)

    # List blobs in the container
    blob_list = container_client.list_blobs()

    # Iterate through each blob
    for blob in blob_list:
        # Construct the blob URL
        blob_url = f"{storage_url}/{blob.name}"
        
        # Print file information
        print(f"File Name: {blob.name}")
        print(f"File URL: {blob_url}")

        # Download the blob to the local file path
        local_file_path = f"{local_download_path}/{blob.name}"
        print(f"Downloading to: {local_file_path}")
        
        # Create a blob client
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob.name)
        
        # Download the blob
        with open(local_file_path, "wb") as file:
            blob_data = blob_client.download_blob()
            blob_data.readinto(file)
        
        # Get image information
        with Image.open(local_file_path) as img:
            width, height = img.size
            img_format = img.format
        
        # Print image information
        print(f"Width: {width}")
        print(f"Height: {height}")
        print(f"Format: {img_format}")
        print("\n")
    
if __name__ == "__main__":
    #manualMetaDataImport()
    buildIndex("test")