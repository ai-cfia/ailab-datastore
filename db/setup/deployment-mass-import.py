from datetime import date
import uuid
import json
import os
import psycopg
from PIL import Image
import db.queries.queries as queries
import validator as validator

# File: nachetDb-1.0.0/mass-import.py
# This script is used to import the missing metadata from an Azure container to the database


# Constants
container_URL = ""
seedID = ""
path = ""


def jsonDeletion(picturefolder):
    """
    Function to delete all the .json files in the specified folder in case of a bad importation.

    Parameters:
    - picturefolder (str): The path to the folder.
    """
    # Get a list of files in the directory
    files = [
        f
        for f in os.listdir(picturefolder)
        if os.path.isfile(os.path.join(picturefolder, f))
    ]
    # Iterate over the list of filepaths & remove each file.
    for file in files:
        try:
            os.remove(file)
        except OSError as e:
            print("Error: %s : %s" % (file, e.strerror))


def manualMetaDataImport(picturefolder: str):
    """
    Template function to do the importation process of the metadata from the Azure container to the database.
    The user is prompted to input the client email, the zoom level and the number of seeds for the index.
    The container needs to be downloaded locally before running this function.

    Parameters:
    - picturefolder (str): Relative path to the folder we want to import.
    """

    # Manually define the picture folder
    # picturefolder = ""  # manually inputted before each import sequence

    # Input the client email to identify the user or register him if needed
    # clientEmail = input("clientEmail: ")
    clientEmail = "test@dev"
    userID = getUserID(clientEmail)

    # #build index
    nbPic = buildIndex(picturefolder, userID)

    # upload index to database
    indexID = uploadIndexDB(f"{picturefolder}/index.json", userID=userID)
    # indexID=1
    print("indexID : " + str(indexID))

    # for each picture in field
    # zoomlevel = input("Zoom level for this index: ")
    zoomlevel = 0
    seedNumber = input("Number of seed for this index: ")

    # Get a list of files in the directory
    files = [
        f
        for f in os.listdir(picturefolder)
        if os.path.isfile(os.path.join(picturefolder, f))
    ]
    i = 0
    # Loop through each file in the folder
    for filename in files:
        if filename.endswith(".tiff") or filename.endswith(".tif"):
            buildPicture(
                picturefolder, seedNumber, zoomlevel, indexID, filename, userID
            )
            picPath = f'{picturefolder}/{filename.removesuffix(".tiff")}.json'
            # upload picture to database
            uploadPictureDB(picPath, userID, indexID)
            i = i + 1

    if i != nbPic:
        print("Error: number of pictures processed does not match the index")
        print("Number of picture processed: " + str(i))
        print("Number of picture in index: " + str(nbPic))
    else:
        print("importation of " + picturefolder + "/ complete")
        print("Number of picture processed: " + str(i))


# Function to retrieve the userID from the database based on the email
# Returns the userID if the email is already registered, else it registers the email and returns the userID
def getUserID(email: str):
    """
    Function to retrieve the userID from the database based on the email.
    If the email is not already registered, it registers the email and returns the userID.

    Parameters:
    - email (str): The email of the user.

    Returns:
    - The userID of the user.
    """
    # Connect to your PostgreSQL database
    conn = psycopg.connect(os.getenv("NACHET_DB_URL"))
    # Create a cursor object
    cur = conn.cursor()
    queries.createSearchPath(conn, cur)
    # Check if the email is already registered
    cur.execute(f"SELECT Exists(SELECT 1 FROM users WHERE email='{email}')")
    if cur.fetchone()[0]:  # Already registered
        cur.execute(f"SELECT id FROM users WHERE email='{email}'")
        res = cur.fetchone()[0]
    else:  # Not registered -> Creates new user
        cur.execute(f"INSERT INTO users (id,email) VALUES (,'{email}')")
        cur.execute(f"SELECT id FROM users WHERE email='{email}'")
        res = cur.fetchone()[0]
    cur.close()
    conn.close()
    return res


# Function to build the index metadata file
def buildIndex(output: str, clientID):
    """
    This function builds the index needed to represent each folder (with pictures in it) of a container.
    It prompts the user to input the expertise of the client and the number of images in the folder.

    Parameters:
    - output (str): The path to the folder.
    - clientID (str): The UUID of the client.

    Returns:
    - The number of pictures in the folder that are supposed to be processed.
    """

    # clientEmail = input("clientEmail: ")
    clientEmail = "test@email"

    # clientExpertise = input("Expertise: ")
    clientExpertise = "Developer"

    # Create the index metadata (sub part) normally filled by the user
    clientData = validator.ClientData(clientEmail=clientEmail, clientExpertise=clientExpertise)
    print(output)
    nb = len([f for f in os.listdir(output) if os.path.isfile(os.path.join(output, f))])
    imageData = validator.ImageDataindex(numberOfImages=nb)

    # ATM===> I dont have access to the seedID db
    # seedID = input("SeedID: ")

    # family = input("Family: ")
    # genus = input("Genus: ")
    # species = input("Species: ")
    family = ""
    genus = ""
    species = ""
    seedData = validator.SeedData(
        seedID=seedID, seedFamily=family, seedGenus=genus, seedSpecies=species
    )

    # Create the Index object
    index = validator.Index(clientData=clientData, imageData=imageData, seedData=seedData)
    
    print("File created, name: " + output + "/index.json")
    indexJson = index.dict()

    # Creating index metadata collected from the system
    sysData = IndexProcessing(openIndexSystem())

    # Append the system data to the index
    indexJson.update(sysData)

    # Create the index file
    createJsonIndex(index=indexJson, name="index", output=output)
    return nb


def buildPicture(output: str, number: int, zoom, indexID: int, name: str, userID: str):
    """
    This function builds the picture metadata file (.json) for each picture in the folder.

    Parameters:
    - output (str): The path to the folder.
    - number (int): The number of seeds in the picture.
    - zoom (float): The zoom level of the picture.
    - indexID (uuid): The ID of the index.
    - name (str): The name of the picture.
    - userID (str): The UUID of the user.

    Returns:
    None
    """

    desc = "This image was uploaded before the creation of the database and was apart of the first importation batch."
    nb = number
    userData = validator.UserData(description=desc, numberOfSeeds=nb, zoom=zoom)

    # Create the Picture object with the user data
    pic = validator.Picture(userData=userData)
    picJson = pic.dict()
    print("File created, name: " + name)
    picturePath = f"{output}/{name}"

    # Creating picture metadata collected from the system
    picData = PictureProcessing(openPictureSystem(), userID, indexID, picturePath)
    picJson.update(picData)
    createJsonPicture(pic=picJson, name=name, output=output)


def IndexProcessing(jsonData: str):
    """
    Function to create the system index metadata.

    Parameters:
    - jsonData (str): The JSON data of the index.

    Returns:
    - The system index object populated with the metadata.
    """
    today = date.today()
    editedBy = "Francois Werbrouck"  # not permanent, will be changed once the mass import is over
    editDate = date.today()
    change = ""
    access = ""
    privacy = False
    return IndexSystemPopulating(
        jsonData, today, editedBy, editDate, change, access, privacy
    )


# Function to create the system picture metadata
# Returns the system picture object populated with the metadata
def PictureProcessing(jsonData: str, userID: str, indexID: int, picturePath: str):
    """
    Function to create the system picture metadata.

    Parameters:
    - jsonData (str): The JSON data of the picture.
    - userID (str): The UUID of the user.
    - indexID (str): The ID of the index.
    - picturePath (str): The path to the picture.

    Returns:
    - The system picture object populated with the metadata.
    """
    today = date.today()
    # userID
    # indexID
    info = getImageProperties(picturePath)
    parent = ""
    source = container_URL + picturePath.removesuffix("test")
    format = info[2]
    height = info[1]
    width = info[0]
    resolution = ""
    return PictureSystemPopulating(
        jsonData,
        today,
        str(userID),
        str(indexID),
        format,
        height,
        width,
        resolution,
        source,
        parent,
    )


# Function to populate the index metadata file provided
# Returns the index metadata object populated with the metadata
def IndexSystemPopulating(
    data, date: date, editedBy, editDate: date, changes: str, access, privacy
):
    """
    Function to populate the index metadata file provided.

    Parameters:
    - data (str): The JSON data template of the index.
    - date (date): The date of the upload
    - editedBy (str): The name of the person who edited the file
    - editDate (date): The date of the last edit
    - changes (str): The changes made to the file
    - access (str): The access log

    Returns:
    - The index metadata object populated with the metadata.
    """
    # print(data)
    data["auditTrail"]["uploadDate"] = date.strftime("%Y-%m-%d")
    data["auditTrail"]["editedBy"] = editedBy
    data["auditTrail"]["editDate"] = editDate.strftime("%Y-%m-%d")
    data["auditTrail"]["changeLog"] = changes
    data["auditTrail"]["accessLog"] = access
    data["auditTrail"]["privacyFlag"] = privacy
    return data


# Function to populate the picture metadata file provided
# Returns the picture metadata object populated with the metadata
def PictureSystemPopulating(
    data,
    date: date,
    userID: str,
    indexID: str,
    format: str,
    height: int,
    width: int,
    resolution: str,
    source: str,
    parent: str,
):
    """
    Function to populate the Picture metadata file provided.

    Parameters:
    - data (str): The JSON data template of the Picture.
    - date (date): The date of the upload
    - userID (str): The UUID of the user
    - indexID (str): The ID of the index
    - format (str): The format of the picture
    - height (int): The height of the picture
    - width (int): The width of the picture
    - resolution (str): The resolution of the picture
    - source (str): The source of the picture
    - parent (str): The parent of the picture

    Returns:
    - The Picture metadata object populated with the metadata.
    """
    data["info"]["userID"] = userID
    data["info"]["uploadDate"] = date.strftime("%Y-%m-%d")
    data["info"]["indexID"] = indexID
    data["imageData"]["height"] = height
    data["imageData"]["width"] = width
    data["imageData"]["format"] = format
    data["imageData"]["source"] = source
    data["imageData"]["parent"] = parent
    data["imageData"]["resolution"] = resolution

    data["qualityCheck"]["imageChecksum"] = ""
    data["qualityCheck"]["uploadCheck"] = True
    data["qualityCheck"]["validData"] = True
    data["qualityCheck"]["errorType"] = ""
    data["qualityCheck"]["dataQualityScore"] = 1.0

    return data


def getImageProperties(path: str):
    """
    Function to retrieve an image's properties.

    Parameters:
    - path (str): The path to the image.

    Returns:
    - The image's width, height and format as a tuple.
    """
    with Image.open(path) as img:
        width, height = img.size
        img_format = img.format
    return width, height, img_format


# Function to open the system index metadata template file
# Returns an empty system index metadata object
def openIndexSystem():
    """
    Function to open the system index metadata template file.

    Returns:
    - An empty system index metadata object.
    """
    with open("index-template-system.json", "r") as file:
        sysData = json.load(file)
        # print(sysData)
    return sysData


# Function to open the system picture metadata template file
# Returns an empty system picture metadata object
def openPictureSystem():
    """
    Function to open the system picture metadata template file.

    Returns:
    - An empty system picture metadata object.
    """
    with open("picture-template-system.json", "r") as file:
        sysData = json.load(file)
        # print(sysData)
    return sysData


# Create .json from Index data model
def createJsonIndex(index, name: str, output: str):
    """
    Create .json from index data model to the specified output.

    Parameters:
    - index (dict): The index data model.
    - name (str): The name of the file.
    - output (str): The path to the folder.

    Returns:
    None
    """
    data = validator.PIndex(**index)
    filePath = f"{output}/{name}.json"
    with open(filePath, "w") as json_file:
        json.dump(index, json_file, indent=2)


# Create .json form Picture data model
def createJsonPicture(pic, name: str, output: str):
    """
    Create .json from picture data model to the specified output.

    Parameters:
    - pic (dict): The picture data model.
    - name (str): The name of the file.
    - output (str): The path to the folder.

    Returns:
    None
    """
    data = validator.PPicture(**pic)
    extension = name.split(".")[-1]
    filename = name.removesuffix("." + extension)
    filePath = f"{output}/{filename}.json"
    with open(filePath, "w") as json_file:
        json.dump(pic, json_file, indent=2)


# Function to upload the index file located @path to the database
# RETURNS the indexID of the uploaded index
def uploadIndexDB(path: str, userID: str):
    """
    Upload the index.json file located at the specified path to the database.

    Parameters:
    - path (str): The path to the index file.
    - userID (str): The ID of the user.

    Returns:
    - The ID of the index.
    """

    # Connect to your PostgreSQL database
    conn = psycopg.connect(os.getenv("NACHET_DB_URL"))

    # Create a cursor object
    cur = conn.cursor()

    queries.createSearchPath(conn, cur)

    # Open the file
    with open(path, "r") as file:
        data = file.read()

    # Build indexID
    indexID = uuid.uuid4()

    # Execute the INSERT statement
    # print(userID)
    cur.execute(
        "INSERT INTO indexes (id,index, ownerID) VALUES (%s,%s, %s)",
        (indexID, data, userID),
    )
    conn.commit()

    # Retrieve the index id
    cur.execute("SELECT id FROM indexes ORDER BY id DESC LIMIT 1")

    cur.close()
    conn.close()
    return indexID


def uploadPictureDB(path: str, userID: str, indexID: str):
    """
    Uploads the picture file located at the specified path to the database.

    Parameters:
    - path (str): The path to the picture file.
    - userID (str): The ID of the user.
    - indexID (str): The ID of the index.

    Returns:
    None
    """
    # Connect to your PostgreSQL howatabase
    conn = psycopg.connect(os.getenv("NACHET_DB_URL"))

    # Create a cursor object
    cur = conn.cursor()

    queries.createSearchPath(conn, cur)
    # Open the file
    with open(path, "r") as file:
        data = file.read()

    # Generate pictureID
    pictureID = uuid.uuid4()

    # Execute the INSERT statement
    cur.execute(
        "INSERT INTO pictures (id,picture, indexID) VALUES (%s,%s, %s)",
        (pictureID, data, indexID),
    )
    conn.commit()

    cur.close()
    conn.close()


if __name__ == "__main__":
    manualMetaDataImport(path)
