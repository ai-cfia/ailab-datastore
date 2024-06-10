import datastore.db.queries.seed as seed
import datastore.db.queries.user as user
import datastore.db.metadata.picture_set as picture_set_metadata
import datastore.db.metadata.picture as picture_metadata
import datastore.db.queries.picture as picture_query
from datastore.blob import azure_storage_api as blob
import datastore
import asyncio
import json


class AlreadyExistingFolderError(Exception):
    pass


class UploadError(Exception):
    pass


def upload_picture_set(
    cursor,
    container_client,
    pictures,
    user_id: str,
    seed_name: str,
    zoom_level: float,
    nb_seeds: int,
    **kwargs,
):
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
        kwargs: additional arguments
    """
    try:
        if not seed.is_seed_registered(cursor=cursor, seed_name=seed_name):
            raise seed.SeedNotFoundError(
                f"Seed not found based on the given name: {seed_name}"
            )
        seed_id = seed.get_seed_id(cursor=cursor, seed_name=seed_name)

        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        picture_set = picture_set_metadata.build_picture_set(user_id, len(pictures))
        picture_set_id = picture_query.new_picture_set(
            cursor=cursor, picture_set=picture_set, user_id=user_id
        )

        folder_created = asyncio.run(
            blob.create_folder(container_client, str(picture_set_id))
        )
        print(folder_created)
        if not folder_created:
            raise AlreadyExistingFolderError(f"Folder already exists: {picture_set_id}")
        folder_url = container_client.url + "/" + str(picture_set_id)
        picture_uploaded = []
        for picture_encoded in pictures:

            # Create picture instance in DB
            empty_picture = json.dumps([])
            picture_id = picture_query.new_picture(
                cursor=cursor,
                picture=empty_picture,
                picture_set_id=picture_set_id,
                seed_id=seed_id,
            )
            # Upload picture to Azure and retrieve link
            asyncio.run(
                blob.upload_image(
                    container_client, picture_set_id, picture_encoded, picture_id
                )
            )
            picture_link = folder_url + "/" + str(picture_id)
            picture_uploaded.append(picture_link)
            # Create picture metadata and update DB instance (with link to Azure blob)
            picture = picture_metadata.build_picture(
                pic_encoded=picture_encoded,
                link=picture_link,
                nb_seeds=nb_seeds,
                zoom=zoom_level,
                description="upload_picture_set script",
            )
            picture_query.update_picture_metadata(
                cursor=cursor, picture_id=picture_id, metadata=picture
            )

        return picture_set_id
    except (seed.SeedNotFoundError) as e:
        raise e
    except user.UserNotFoundError as e:
        raise e
    except AlreadyExistingFolderError as e:
        raise e
    except Exception:
        if folder_url is not None:
            #arg = f""""picture_set_uuid":'{picture_set_id}'"""
            #blobs = asyncio.run(blob.get_blobs_from_tag(container_client, arg))
            blobs = container_client.list_blobs()
            container_client.delete_blobs(blobs)
        raise UploadError("An error occured during the upload of the picture set")

async def create_picture_set(cursor, container_client, nb_pictures:int, user_id: str):
    try:

        if not user.is_a_user_id(cursor=cursor, user_id=user_id):
            raise user.UserNotFoundError(
                f"User not found based on the given id: {user_id}"
            )

        picture_set = picture_set_metadata.build_picture_set(user_id, nb_pictures)
        picture_set_id = picture_query.new_picture_set(
            cursor=cursor, picture_set=picture_set, user_id=user_id
        )

        folder_created = asyncio.run(
            blob.create_folder(container_client, str(picture_set_id))
        )
        if not folder_created:
            raise AlreadyExistingFolderError(f"Folder already exists: {picture_set_id}")
        
        return picture_set_id
    except (seed.SeedNotFoundError) as e:
        raise e
    except user.UserNotFoundError as e:
        raise e
    except AlreadyExistingFolderError as e:
        raise e
    except Exception:
        raise UploadError("An error occured during the upload of the picture set")

async def upload_pictures(cursor, user_id, picture_set_id, container_client, pictures, seed_name: str, zoom_level: float, nb_seeds: int) :
    try:
        
        if not seed.is_seed_registered(cursor=cursor, seed_name=seed_name):
            raise seed.SeedNotFoundError(
                f"Seed not found based on the given name: {seed_name}"
            )
        seed_id = seed.get_seed_id(cursor=cursor, seed_name=seed_name)
            
        for picture_encoded in pictures:
            datastore.upload_picture(cursor, user_id, picture_encoded, container_client, picture_set_id, seed_id, nb_seeds, zoom_level)
        
        return picture_set_id
    except (seed.SeedNotFoundError) as e:
        raise e
    except user.UserNotFoundError as e:
        raise e
    except AlreadyExistingFolderError as e:
        raise e
    except Exception:
        raise UploadError("An error occured during the upload of the picture set")
if __name__ == "__main__":
    upload_picture_set()
