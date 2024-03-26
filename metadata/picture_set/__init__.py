from pydantic import BaseModel
from datetime import date


class image_data(BaseModel):
    numberOfImages: int

class audit_trail(BaseModel):
    upload_date: date
    edited_by: str
    edit_date: date
    change_log: str
    access_log: str
    privacy_flag: bool

class picture_set(BaseModel):
    image_data: image_data
    audit_trail: audit_trail

def build_picture_set(userID:str,nbPicture:int):
    """
    This function builds the picture_set needed to represent each folder (with pictures in it) of a container.
    
    Parameters:
    - userID (str): The UUID of the user uploading.
    - nbPicture (int): The amount of picture present in the folder.

    Returns:
    - The picture_set in .
    """
    
    image_data=image_data(numberOfImages=nbPicture)
    
    sysData=audit_trail(
        upload_date=date.today(),
        edited_by=userID,
        edit_date=date.today(),
        change_log="picture_set created",
        access_log="picture_set accessed",
        privacy_flag=False
        )
    
    picture_set = picture_set(image_data=image_data,audit_trail=sysData)
    try:
        picture_set(**picture_set.dict())
    except:
        print("Error: picture_set not created")
        return None
    return picture_set
    
    