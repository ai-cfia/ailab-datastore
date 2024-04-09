import datastore.db.queries.seed as seed
import datastore.db.queries.user as user
import datastore.db.metadata.picture_set as picture_set_metadata
import datastore.db.metadata.picture as picture_metadata
import datastore.db.queries.picture as picture_query
from datastore.blob import azure_storage_api as blob

class AlreadyExistingFolderError(Exception):  
    pass

def upload_picture_set(cursor, connection_string:str, pictures, user_id:str, seed_name:str, zoom_level:float, nb_seeds:int):
    """
    Upload a set of pictures to the Azure storage account and the database.

    Args:
        cursor (obj): cursor object to interact with the database
        connection_string (str): URL to connect to the Azure storage account
        pictures (str): list picture in a string format 
        user_id (str): uuid of the user
        seed_name (str): name of the seed
        zoom_level (float): zoom level of the picture
        nb_seeds (int): number of seeds in the picture
    """
    
    if not seed.is_seed_registered(cursor=cursor, seed_name=seed_name):
        raise seed.SeedNotFoundError(f"Seed not found based on the given name: {seed_name}")
    
    if not user.is_a_user_id(cursor=cursor, user_id=user_id):
        raise user.UserNotFoundError(f"User not found based on the given id: {user_id}")
    
    connection_string = user.get_container_url(cursor=cursor, user_id=user_id)
    container_client = blob.mount_container(connection_string,user_id,False,"user")
    
    picture_set = picture_set_metadata.build_picture_set(user_id, len(pictures))
    picture_set_id= picture_query.new_picture_set(cursor=cursor, picture_set=picture_set, user_id=user_id)
    
    if not blob.create_folder(container_client, picture_set_id):
        raise AlreadyExistingFolderError(f"Folder already exists: {picture_set_id}")
    folder_url= connection_string + "/" + str(picture_set_id)
    
    for picture_encoded in pictures:
        
        # Create picture instance in DB
        picture_id=picture_query.new_picture(cursor=cursor, picture="", picture_set_id=picture_set_id, seed_id=seed_id)
        # Upload picture to Azure and retrieve link
        blob.upload_image(container_client, picture_set_id, picture_encoded, picture_id)
        picture_link = folder_url +  "/" + str(picture_id)
        
        # Create picture metadata and update DB instance (with link to Azure blob)
        picture = picture_metadata.build_picture(pic_encoded=picture_encoded,link= picture_link,nb_seeds=nb_seeds,zoom=zoom_level, description="upload_picture_set script")
        picture_query.update_picture_metadata(cursor=cursor, picture_id=picture_id, picture=picture)
        
    return picture_set_id

if __name__ == "__main__":
    upload_picture_set()