# Manage folders

## Executive summary

A user is able to have a preview of his blob storage container in the Nachet
application. He can have many folders in his container and pictures in it. Since
we have the database, those folders are related to the picture_set table and
each pictures is also saved in the database. Here is the schema of actual
database.

``` mermaid
---
title: Extract from Nachet DB Structure 
---
erDiagram
  picture_set{
    uuid id PK
    json picture_set
    uuid owner_id FK
    timestamp upload_date
  }
  picture{
    uuid id PK
    json picture
    uuid picture_set_id FK
    uuid parent FK
    int nb_object
    boolean verified
    timestamp upload_date 
  }
inference{
    uuid id PK
    json inference 
    uuid picture_id FK
    uuid user_id FK
    timestamp upload_date
  }
  picture_seed{
    uuid id PK
    uuid picture_id FK
    uuid seed_id FK
    timestamp upload_date
  }
  picture_set ||--o{picture: contains
  picture ||--o{picture: cropped
  picture |o--o{picture_seed: has
  picture_seed }o--o| seed: has
  inference ||--o{ object: detects
  object ||--o{ seed_object: is
  seed_object }o--|| seed: is
  inference ||--|| picture: infers

```

From the nachet application, a user can create and delete folders, so the blob
storage and the database must be correctly updated.

When a folder is created, it takes on a name and is created as a picture_set in
the database and as a folder in the blob storage container of the user.

There are more issues when the user wants to delete a folder. If the folder
contains validated pictures, it may be useful for training purpose, because it
means there is a valid inference associate with each seed on the picture. The
same applies to pictures imported in batches, which have been downloaded for
training purposes. Our solution is to request confirmation from the user, who
can decide to delete pictures from his container but let us save them, or he can
delete everything anyway, for example if there has been a missed click.

Users have asked to be able to access the pictures of folders in the directory
section on frontend. We want them to be able to see each pictures name. Then a
user can select a folder this will get all pictures and their inferences.

## Prerequisites

- The user must be signed in and have an Azure Storage Container
- The backend need to have a connection with the datastore

## Sequence Diagram

### Delete use case

```mermaid
sequenceDiagram
    participant User
    participant FE
    participant BE
    participant DS

    User->>FE: Delete Folder
    rect rgb(200, 50, 50)
      FE->>BE: /delete-request
    end
    rect rgb(200, 50, 50)
          BE->>DS: Check if there are validated inferences or pictures from a batch import
note left of DS: Check for picture_seed entities linked to picture id<br> since a verified inference and a batch upload has those
    end
    alt picture_seed exist
        DS-->>BE: Validated inference status or pictures from batch import
        BE->>FE: True : Request user confirmation
        rect rgb(200, 50, 50)
            FE->>User: Ask to keep data for training
note left of FE : "Some of those pictures were validated or upload via the batch import.<br>Do you want us to keep them for training ? <br>If yes, your folder will be deleted but we'll keep the validated pictures.<br>If no, everything will be deleted and unrecoverable.
        end
        alt No
            User ->>FE: delete all
            rect rgb(200, 50, 50)
                FE-->BE:  /delete-permanently
            end
            BE->>DS: delete picture_set
        else YES
            User ->>FE: Keep them
            rect rgb(200, 50, 50)
                FE-->BE: /delete-with-archive
            end
            rect rgb(200, 50, 50)
                BE->>DS: archive data for validated inferences and batch import in picture_set
                    note left of DS: "Pictures are moved in different container <br> DB entities updated" 
                BE->>DS: delete picture_set
                   note left of DS: "Folder and all the files left are deleted, <br>related pictures, inference are deleted." 
            end
       else CANCEL
            User ->>FE: cancel : nothing happens
       end
    else no picture_seed exist
        DS-->>BE: No pictures with validated inference status or from batch import
        BE-->>FE: False: confirmation to delete the folder
        rect rgb(200, 50, 50)
            FE->>User: Ask confirmation
note left of FE : "Are you sure ? Everything in this folder will be deleted and unrecoverable"
        end
        alt Yes
            User ->>FE: delete all
            rect rgb(200, 50, 50)
                FE-->BE:  /delete-permanently
            end
            BE->>DS: delete picture_set
        else CANCEL
            User ->>FE: cancel : nothing happens
        
        end
    end

```

### Get folder content user case

```mermaid
sequenceDiagram
    participant User
    participant FE as Frontend
    participant BE as Backend
    participant DS as Datastore

    User->>FE: ApplicationStart()
        FE-->>BE:  /directories
            BE->>DS: get_picture_sets_info(user_id)
                loop for each picture set
                    DS-->DS: get_pictures(user_id, picture_set_id)
                end
            DS-->>BE: List of picture_set with pictures data
        BE-->>FE: Response : List of picture_set with pictures name
    User->>FE: Select Folder
        FE->>BE: /get-folder-content
            BE->>DS: get_pictures_inferences(user_id, picture_set_id)
                DS-->DS: get_pictures_with_inferencse(user_id, picture_set_id)
            DS-->>BE: Return pictures with inferences
            BE->>DS: get_pictures_blobs(user_id, picture_set_id)
                DS-->DS: get_blobs(user_id, picture_set_id)
            DS-->>BE: Return pictures blobs
        BE-->>BE: cache pictures and inferences
        BE-->>FE: Response : True
    FE-->>User: Display folder content (list of pictures)
    User->>FE: Select Picture
        FE->>BE: /get-picture
            BE->>BE: get_picture_from_cache(user_id, picture_id)
        BE-->>FE: Response : Picture with hash and inference
    FE-->>User: Display picture with inference if exist


```
