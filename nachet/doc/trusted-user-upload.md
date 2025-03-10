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
    Backend -) Datastore: get_container_controller(user.model.containers[i].id)
    Datastore --> Backend : container_controller
    Backend -) Datastore: upload_pictures_known (cursor, container_controller, pictures, user_id, seed_id, zoom_level, nb_seeds)
    Datastore -) Azure Storage: container_controller.upload_pictures(picture_set_id)
    loop for each ID in picture_ids
      Datastore -) PostgreSQL Database: new_picture_seed(seed_id,picture_set_id)
    end

```

``` mermaid

---
title: Nachet DB Structure
---
erDiagram
  user{
    uuid id PK
    string email
    timestamp registration_date
    timestamp updated_at
    integer role_id
  }
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
  role{
    int id
    text name
  }
  container{
    uuid id PK
    uuid owner_id FK
    boolean public
    timestamp creation_date
    timestamp updated_at
  }

  user ||--|{ picture_set: uploads
  picture_set ||--o{picture: contains
  picture ||--o{picture: cropped
  role ||--|| user: has
  container ||--o{picture_set: contains
  user ||--o{container: own

```
