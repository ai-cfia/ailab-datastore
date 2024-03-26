from datetime import date
import sys
import uuid
import json
import os
import psycopg
from PIL import Image
import db as db

# This script is used to import the missing metadata from an Azure container to the database


# Constants
container_URL = ""
seed_id = ""
path = ""


def json_deletion(picture_folder):
    """
    Function to delete all the .json files in the specified folder in case of a bad importation.

    Parameters:
    - picture_folder (str): The path to the folder.
    """
    # Get a list of files in the directory
    files = [
        f
        for f in os.listdir(picture_folder)
        if os.path.isfile(os.path.join(picture_folder, f))
    ]
    # Iterate over the list of filepaths & remove each file.
    for file in files:
        try:
            os.remove(file)
        except OSError as e:
            print("Error: %s : %s" % (file, e.strerror))


def manual_metadata_import(picture_folder: str):
    """
    Template function to do the importation process of the metadata from the Azure container to the database.
    The user is prompted to input the client email, the zoom level and the number of seeds for the picture_set.
    The container needs to be downloaded locally before running this function.

    Parameters:
    - picture_folder (str): Relative path to the folder we want to import.
    """

    # Manually define the picture folder
    # picture_folder = ""  # manually inputted before each import sequence

    # Input the client email to identify the user or register him if needed
    # client_email = input("client_email: ")
    client_email = "test@email"
    user_id = get_user_id(client_email)
    if user_id is None:
        print("Error: could not retrieve the user_id")
        return
    # #build picture_set
    nb_pic = build_picture_set(picture_folder, user_id)

    # upload picture_set to database
    picture_set_id = upload_picture_set_db(f"{picture_folder}/picture_set.json", user_id=user_id)
    # picture_set_id=1
    print("picture_set_id : " + str(picture_set_id))

    # for each picture in field
    zoom_level = input("Zoom level for this picture_set: ")
    seed_number = input("Number of seed for this picture_set: ")

    # Get a list of files in the directory
    files = [
        f
        for f in os.listdir(picture_folder)
        if os.path.isfile(os.path.join(picture_folder, f))
    ]
    i = 0
    # Loop through each file in the folder
    for filename in files:
        if filename.endswith(".tiff") or filename.endswith(".tif"):
            build_picture(picture_folder, seed_number, zoom_level, filename)
            pic_path = f'{picture_folder}/{filename.removesuffix(".tiff")}.json'
            # upload picture to database
            uploadPictureDB(pic_path, picture_set_id, seed_id=seed_id)
            i = i + 1

    if i != nb_pic:
        print("Error: number of pictures processed does not match the picture_set")
        print("Number of picture processed: " + str(i))
        print("Number of picture in picture_set: " + str(nb_pic))
    else:
        print("importation of " + picture_folder + "/ complete")
        print("Number of picture processed: " + str(i))


def get_user_id(email: str):
    """
    Function to retrieve the user_id from the database based on the email.
    If the email is not already registered, it registers the email and returns the user_id.

    Parameters:
    - email (str): The email of the user.

    Returns:
    - The user_id of the user.
    """
    try:
        # Connect to your PostgreSQL database
        conn = psycopg.connect(os.getenv("NACHET_DB_URL"))
        # Create a cursor object
        cur = conn.cursor()
        db.create_search_path(conn, cur)
        # Check if the email is already registered
        cur.execute(f"SELECT Exists(SELECT 1 FROM users WHERE email='{email}')")
        if cur.fetchone()[0]:  # Already registered
            cur.execute(f"SELECT id FROM users WHERE email='{email}'")
            res = cur.fetchone()[0]
        else:  # Not registered -> Creates new user
            cur.execute(f"INSERT INTO users (id,email) VALUES (,'{email}')")
            cur.execute(f"SELECT id FROM users WHERE email='{email}'")
            res = cur.fetchone()[0]
    except (Exception, psycopg.DatabaseError) as error:
        print(error)
        res = None
    finally:
        cur.close()
        conn.close()
    return res


def build_picture_set(output: str, client_id):
    """
    This function builds the picture_set needed to represent each folder (with pictures in it) of a container.
    It prompts the user to input the expertise of the client and the number of images in the folder.

    Parameters:
    - output (str): The path to the folder.
    - client_id (str): The UUID of the client.

    Returns:
    - The number of pictures in the folder that are supposed to be processed.
    """

    # client_email = input("client_email: ")
    client_email = "test@email"

    # client_expertise = input("Expertise: ")
    client_expertise = "Developer"

    # Create the picture_set metadata (sub part) normally filled by the user
    client_data = validator.client_data(
        client_email=client_email, client_expertise=client_expertise
    )
    print(output)
    nb = len([f for f in os.listdir(output) if os.path.isfile(os.path.join(output, f))])
    image_data = validator.image_data_picture_set(numberOfImages=nb)

    # ATM===> I dont have access to the seed_id db
    # seed_id = input("seed_id: ")

    # family = input("Family: ")
    # genus = input("Genus: ")
    # species = input("Species: ")
    family = ""
    genus = ""
    species = ""
    seed_data = validator.seed_data(
        seed_id=seed_id, seed_family=family, seed_genus=genus, seed_species=species
    )

    # Create the picture_set object
    picture_set = validator.picture_set(client_data=client_data, image_data=image_data)

    print("File created, name: " + output + "/picture_set.json")
    picture_set_jsons = picture_set.dict()

    # Creating picture_set metadata collected from the system
    sysData = picture_set_processing(open_picture_set_system())

    # Append the system data to the picture_set
    picture_set_jsons.update(sysData)

    # Create the picture_set file
    create_json_picture_set(picture_set=picture_set_jsons, name="picture_set", output=output)
    return nb


def build_picture(output: str, number: int, zoom, name: str):
    """
    This function builds the picture metadata file (.json) for each picture in the folder.

    Parameters:
    - output (str): The path to the folder.
    - number (int): The number of seeds in the picture.
    - zoom (float): The zoom level of the picture.
    - name (str): The name of the picture.

    Returns:
    None
    """

    desc = "This image was uploaded before the creation of the database and was apart of the first importation batch."
    nb = number
    user_data = validator.user_data(description=desc, number_of_seeds=nb, zoom=zoom)

    # Create the Picture object with the user data
    pic = validator.Picture(user_data=user_data)
    pic_json = pic.dict()
    print("File created, name: " + name)
    picture_path = f"{output}/{name}"

    # Creating picture metadata collected from the system
    picData = picture_processing(open_picture_system(), picture_path)
    pic_json.update(picData)
    create_json_picture(pic=pic_json, name=name, output=output)


def picture_set_processing(json_data: str):
    """
    Function to create the system picture_set metadata.

    Parameters:
    - json_data (str): The JSON data of the picture_set.

    Returns:
    - The system picture_set object populated with the metadata.
    """
    today = date.today()
    edited_by = "Francois Werbrouck"  # not permanent, will be changed once the mass import is over
    edited_date = date.today()
    change = ""
    access = ""
    privacy = False
    return picture_set_system_populating(
        json_data, today, edited_by, edited_date, change, access, privacy
    )


def picture_processing(json_data: str, picture_path: str):
    """
    Function to create the system picture metadata.

    Parameters:
    - json_data (str): The JSON data of the picture.
    - user_id (str): The UUID of the user.
    - picture_set_id (str): The ID of the picture_set.
    - picture_path (str): The path to the picture.

    Returns:
    - The system picture object populated with the metadata.
    """
    today = date.today()
    # user_id
    # picture_set_id
    info = get_image_properties(picture_path)
    parent = ""
    # source = container_URL + picture_path.removesuffix("test")
    source = container_URL + picture_path
    format = info[2]
    height = info[1]
    width = info[0]
    resolution = ""
    return picture_system_populating(
        json_data,
        today,
        format,
        height,
        width,
        resolution,
        source,
        parent,
    )


def picture_set_system_populating(
    data, date: date, edited_by, edited_date: date, changes: str, access, privacy
):
    """
    Function to populate the picture_set metadata file provided.

    Parameters:
    - data (str): The JSON data template of the picture_set.
    - date (date): The date of the upload
    - edited_by (str): The name of the person who edited the file
    - edited_date (date): The date of the last edit
    - changes (str): The changes made to the file
    - access (str): The access log

    Returns:
    - The picture_set metadata object populated with the metadata.
    """
    # print(data)
    data["auditTrail"]["uploadDate"] = date.strftime("%Y-%m-%d")
    data["auditTrail"]["edited_by"] = edited_by
    data["auditTrail"]["edited_date"] = edited_date.strftime("%Y-%m-%d")
    data["auditTrail"]["changeLog"] = changes
    data["auditTrail"]["accessLog"] = access
    data["auditTrail"]["privacyFlag"] = privacy
    return data


def picture_system_populating(
    data,
    date: date,
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
    - user_id (str): The UUID of the user
    - picture_set_id (str): The ID of the picture_set
    - format (str): The format of the picture
    - height (int): The height of the picture
    - width (int): The width of the picture
    - resolution (str): The resolution of the picture
    - source (str): The source of the picture
    - parent (str): The parent of the picture

    Returns:
    - The Picture metadata object populated with the metadata.
    """
    data["info"]["uploadDate"] = date.strftime("%Y-%m-%d")
    data["image_data"]["height"] = height
    data["image_data"]["width"] = width
    data["image_data"]["format"] = format
    data["image_data"]["source"] = source
    data["image_data"]["parent"] = parent
    data["image_data"]["resolution"] = resolution

    data["qualityCheck"]["imageChecksum"] = ""
    data["qualityCheck"]["uploadCheck"] = True
    data["qualityCheck"]["validData"] = True
    data["qualityCheck"]["errorType"] = ""
    data["qualityCheck"]["dataQualityScore"] = 1.0

    return data


def get_image_properties(path: str):
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


# Function to open the system picture_set metadata template file
# Returns an empty system picture_set metadata object
def open_picture_set_system():
    """
    Function to open the system picture_set metadata template file.

    Returns:
    - An empty system picture_set metadata object.
    """
    with open("picture_set-template-system.json", "r") as file:
        sysData = json.load(file)
        # print(sysData)
    return sysData


def open_picture_system():
    """
    Function to open the system picture metadata template file.

    Returns:
    - An empty system picture metadata object.
    """
    with open("picture-template-system.json", "r") as file:
        sysData = json.load(file)
        # print(sysData)
    return sysData


def create_json_picture_set(picture_set, name: str, output: str):
    """
    Create .json from picture_set data model to the specified output.

    Parameters:
    - picture_set (dict): The picture_set data model.
    - name (str): The name of the file.
    - output (str): The path to the folder.

    Returns:
    None
    """
    data = validator.Ppicture_set(**picture_set)
    filePath = f"{output}/{name}.json"
    with open(filePath, "w") as json_file:
        json.dump(picture_set, json_file, indent=2)


def create_json_picture(pic, name: str, output: str):
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


def upload_picture_set_db(path: str, user_id: str):
    """
    Upload the picture_set.json file located at the specified path to the database.

    Parameters:
    - path (str): The path to the picture_set file.
    - user_id (str): The ID of the user.

    Returns:
    - The ID of the picture_set.
    """
    try:
        # Connect to your PostgreSQL database
        conn = psycopg.connect(os.getenv("NACHET_DB_URL"))

        # Create a cursor object
        cur = conn.cursor()

        db.create_search_path(conn, cur)

        # Open the file
        with open(path, "r") as file:
            data = file.read()

        # Build picture_set_id
        picture_set_id = uuid.uuid4()

        # Execute the INSERT statement
        # print(user_id)
        query = "INSERT INTO picture_sets (id,picture_set, owner_id) VALUES (%s,%s, %s)"
        params = (
            picture_set_id,
            data,
            user_id,
        )
        cur.execute(query, params)
        conn.commit()
    except:
        print("Error: could not upload the picture_set to the database")
        picture_set_id = None
    # Retrieve the picture_set id
    # cur.execute("SELECT id FROM picture_sets ORDER BY id DESC LIMIT 1")
    finally:
        cur.close()
        conn.close()
    return picture_set_id


def uploadPictureDB(path: str, picture_set_id: str, seed_id: str):
    """
    Uploads the picture file located at the specified path to the database.

    Parameters:
    - path (str): The path to the picture file.
    - user_id (str): The ID of the user.
    - picture_set_id (str): The ID of the picture_set.

    Returns:
    None
    """
    try:
        # Connect to your PostgreSQL howatabase
        conn = psycopg.connect(os.getenv("NACHET_DB_URL"))

        # Create a cursor object
        cur = conn.cursor()

        db.create_search_path(conn, cur)
        # Open the file
        with open(path, "r") as file:
            data = file.read()

        # Generate picture_id
        picture_id = uuid.uuid4()

        # Execute the INSERT statement
        params = (
            picture_id,
            data,
            picture_set_id,
        )
        query = "INSERT INTO pictures (id,picture, picture_set_id) VALUES (%s,%s, %s)"
        cur.execute(query, params)
        conn.commit()

        id = uuid.uuid4()

        # Create a Picture - Seed relationship
        param = (
            id,
            seed_id,
            picture_id,
        )
        query = "INSERT INTO seedpicture (id,seed_id,picture_id) VALUES (%s,%s,%s)"
        cur.execute(query, param)
        conn.commit()
    except:
        print("Error: could not upload the picture to the database")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    manual_metadata_import(*sys.argv[1:])
