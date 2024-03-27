from pydantic import BaseModel
from datetime import date
from PIL import Image

class metadata(BaseModel):
    upload_date: date

class user_data(BaseModel):
    description: str
    number_of_seeds: int
    zoom: float
    
class image_data(BaseModel):
    format: str
    height: int
    width: int
    resolution: str
    source: str
    parent: str
    
class quality_check(BaseModel):
    image_checksum: str
    uploadCheck: bool
    validData: bool
    errorType: str
    dataQualityScore: float
    
class Picture(BaseModel):
    user_data: user_data
    metadata: metadata
    image_data: image_data
    quality_check: quality_check


def build_picture(pic,link:str,nb_seeds:int,zoom:float,description:str=""):
    """
    This function builds the Picture metadata needed for the database.
    
    Parameters:
    - pic (str): The picture in a string format.
    - link (str): The link to the picture blob.
    - nb_seeds (int): The number of seeds in the picture.
    - zoom (float): The zoom level of the picture.
    """
    
    user_metadata = user_data(
        description=description,
        number_of_seeds=nb_seeds,
        zoom=zoom
        )
    
    meta_data = metadata(upload_date=date.today())
    
    #This will cause an error.
    # TODO : Create a function to rebuild the picture.tiff from a string
    pic_properties = get_image_properties(pic)
    
    image_metadata = image_data(
        format=pic_properties[2],
        height=pic_properties[1],
        width=pic_properties[0],
        resolution="",
        source=link,
        parent=""
        )
    
    quality_check_metadata = quality_check(
        image_checksum="",
        uploadCheck=True,
        validData=True,
        errorType="",
        dataQualityScore=0.0
        )
    
    picture = Picture(user_data=user_metadata,
                      metadata=meta_data,
                      image_data=image_metadata,
                      quality_check=quality_check_metadata)
    try:
        Picture(**picture.model_dump())
    except:
        print("Error: Picture not created")
        return None
    return picture.model_dump_json()
        
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