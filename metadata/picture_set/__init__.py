from pydantic import BaseModel
from datetime import date
from metadata import validator

def build_picture_set(user_id:str,nb_picture:int):
    """
    This function builds the picture_set needed to represent each folder (with pictures in it) of a container.
    
    Parameters:
    - user_id (str): The UUID of the user uploading.
    - nb_picture (int): The amount of picture present in the folder.

    Returns:
    - The picture_set in .
    """
    
    image_metadata=validator.image_data_picture_set(number_of_images=nb_picture)
    
    sysData=validator.audit_trail(
        upload_date=date.today(),
        edited_by=str(user_id),
        edit_date=date.today(),
        change_log="picture_set created",
        access_log="picture_set accessed",
        privacy_flag=False
        )
    
    picture_set_data = validator.Ppicture_set(image_data_picture_set=image_metadata,audit_trail=sysData)
    try:
        validator.Ppicture_set(**picture_set_data.model_dump())
    except:
        print("Error: picture_set not created")
        return None
    return picture_set_data.model_dump_json()   
    