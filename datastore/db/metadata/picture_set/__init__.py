""" 
This module contains the function to build the picture_set metadata needed for the database.
"""
from datetime import date
from datastore.db.metadata import validator


class PictureSetCreationError(Exception):
    pass


def build_picture_set_metadata(user_id: str, nb_picture: int):
    """
    This function builds the picture_set_metadata needed to represent each folder (with pictures in it) of a container.

    Parameters:
    - user_id (str): The UUID of the user uploading.
    - nb_picture (int): The amount of picture present in the folder.

    Returns:
    - The picture_set in a string dict format.
    """

    image_metadata = validator.ImageDataPictureSet(number_of_images=nb_picture)

    sysData = validator.AuditTrail(
        upload_date=date.today(),
        edited_by=str(user_id),
        edit_date=date.today(),
        change_log="picture_set created",
        access_log="picture_set accessed",
        privacy_flag=False,
    )

    picture_set_data = validator.ProcessedPictureSet(
        image_data_picture_set=image_metadata, audit_trail=sysData
    )
    try:
        validator.ProcessedPictureSet(**picture_set_data.model_dump())
    except validator.ValidationError as e:
        raise PictureSetCreationError("Error picture_set not created:"+ str(e)) from None
    return picture_set_data.model_dump_json()
