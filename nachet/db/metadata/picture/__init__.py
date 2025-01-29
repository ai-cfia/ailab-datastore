""" 
This module contains the function to build the picture metadata needed for the database.
"""

from datetime import date
from datastore.db.metadata import validator



class PictureCreationError(Exception):
    pass


def build_picture(
    pic_encoded, link: str, nb_seeds: int, zoom: float, description: str = ""
):
    """
    This function builds the Picture metadata needed for the database.

    Parameters:
    - pic_encoded (str): The picture in a string format.
    - link (str): The link to the picture blob.
    - nb_seeds (int): The number of seeds in the picture.
    - zoom (float): The zoom level of the picture.

    Returns:
    - The picture metadata in a string dict format.
    """

    user_data = validator.UserData(
        description=description, number_of_seeds=nb_seeds, zoom=zoom
    )

    meta_data = validator.Metadata(upload_date=date.today())
    #TODO : Fix
    #pic_properties = get_image_properties(pic_encoded)
    pic_properties = [None,None,None]
    image_metadata = validator.ImageData(
        format=pic_properties[2],
        height=pic_properties[1],
        width=pic_properties[0],
        resolution="",
        source=link,
        parent="",
    )

    quality_check_metadata = validator.QualityCheck(
        image_checksum="",
        upload_check=True,
        valid_data=True,
        error_type="",
        quality_score=0.0,
    )

    picture = validator.ProcessedPicture(
        user_data=user_data,
        metadata=meta_data,
        image_data=image_metadata,
        quality_check=quality_check_metadata,
    )
    try:
        validator.ProcessedPicture(**picture.model_dump())
    except validator.ValidationError as e:
        raise PictureCreationError("Error, Picture not created:" + str(e)) from None
    return picture.model_dump_json()
