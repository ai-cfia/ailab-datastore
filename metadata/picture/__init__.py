
from datetime import date
from metadata import validator
from PIL import Image
import io
import base64

def build_picture(pic_encoded,link:str,nb_seeds:int,zoom:float,description:str=""):
    """
    This function builds the Picture metadata needed for the database.
    
    Parameters:
    - pic_encoded (str): The picture in a string format.
    - link (str): The link to the picture blob.
    - nb_seeds (int): The number of seeds in the picture.
    - zoom (float): The zoom level of the picture.
    """
    
    user_data = validator.user_data(
        description=description,
        number_of_seeds=nb_seeds,
        zoom=zoom
        )
    
    meta_data = validator.metadata(upload_date=date.today())
    
    pic_properties = get_image_properties(pic_encoded)
    
    image_metadata = validator.image_data(
        format=pic_properties[2],
        height=pic_properties[1],
        width=pic_properties[0],
        resolution="",
        source=link,
        parent=""
        )
    
    quality_check_metadata = validator.quality_check(
        image_checksum="",
        upload_check=True,
        valid_data=True,
        error_type="",
        quality_score=0.0
        )
    
    picture = validator.PPicture(user_data=user_data,
                      metadata=meta_data,
                      image_data=image_metadata,
                      quality_check=quality_check_metadata)
    try:
        validator.PPicture(**picture.model_dump())
    except:
        print("Error: Picture not created")
        return None
    return picture.model_dump_json()
        
def get_image_properties(pic_encoded: str):
    """
    Function to retrieve an image's properties.

    Parameters:
    - pic_encoded (str): The image in a string format.

    Returns:
    - The image's width, height and format as a tuple.
    """
    with Image.open(io.BytesIO(base64.b64decode(pic_encoded))) as img:
        width, height = img.size
        img_format = img.format
    return width, height, img_format