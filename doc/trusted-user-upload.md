# Trusted user upload process

## Contexte
We have a set of trusted user that needs to have an easy way of uploading large
sets of data to both our picture storage and database.

## Prerequisites
- The user must be signed in
- The user Azure Storage Container's have been created
- The user the pictures validity passes all checks
- The Seed is already registered in the Database

## Sequence of the uploading process

``` mermaid  
sequenceDiagram;
  actor User
  box grey Ai-Lab services
  participant Frontend
  participant Backend
  participant Datastore
  end
  box grey Storage services
  participant PostgreSQL Database
  participant Azure Storage
  end

    User ->> Frontend: Upload session request
    Frontend -->> User: Show session form
    User -) Frontend: Fill form :<br> Seed selection, nb Seeds/Pic, Zoom
    User -) Frontend: Upload: session folder
    Frontend ->> Backend: Upload from trusted user request: <br> Seed info, nbSeeds/Pic, Zoom ,<br> Session Folder & User
    Backend -) Datastore: db.connect_db()
    Datastore --> Backend : connection
    Backend -) Datastore: cursor(connection)
    Datastore --> Backend : cursor
    Backend -) Datastore: get_User(email,cursor)
    Datastore --> Backend : User
    Backend -) Datastore: get_user_container_client(user_uuid)
    Datastore --> Backend : container_client
    Backend -) Datastore: upload_picture_set (cursor, container_client, pictures, user_id, seed_name, zoom_level, nb_seeds)
    Datastore --> PostgreSQL Database: is_seed_registered(seed_name)
    Datastore --> PostgreSQL Database: is_a_user_id(user_id)
    Datastore -) PostgreSQL Database: get_container_url()
    Datastore ->> Datastore: build_picture_set()
    Datastore -) PostgreSQL Database: new_picture_set(user_id)
    Datastore -) Azure Storage: create_folder(picture_set_id)
    loop for each picture_encoded in pictures
      Datastore -) PostgreSQL Database: new_picture(seed_id,picture_set_id)
      Datastore -) Azure Storage: upload_image(picture_encoded)
      Datastore ->> Datastore: build_picture(picture_encoded,blob_url)
      Datastore -) PostgreSQL: update_picture_metadata(picture_id,picture)
    end

``` 
