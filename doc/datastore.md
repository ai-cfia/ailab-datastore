# Datastore

Welcome to the Nachet Datastore - the integral data management layer of the
Nachet solution serving a dual function role. As a central repository, it
efficiently manages multimedia storage in the blob storage server while
concurrently ensuring accurate metadata registration into a database server. 

## Robust Multimedia Storage 

The essential function of our Datastore is to manage the multimedia storage
effectively within the blob storage server. With support for a variety of media
formats and efficient indexing techniques, the smooth retrieval and access of
data are assured. 

```Structure

Storage account:
│     
│  Container:
└───user-8367cc4e-1b61-42c2-a061-ca8662aeac37
|   | Folder:
│   └───fb20146f-df2f-403f-a56f-f02a48092167/
|   |  |   fb20146f-df2f-403f-a56f-f02a48092167.json
│   |  │   f9b0ef75-6276-4ffc-a71c-975bc842063c.tiff
│   |  │   68e16a78-24bd-4b8c-91b6-75e6b84c40d8.tiff
│   |  |   ...
│   |  └─────────────
|   | Folder:
│   └───a6bc9da0-b1d0-42e5-8c41-696b86271d55/
│      |   ...
│      └─────────────
|   Container:
└───user-...
|   └── ...
└──────────────────

```

## Efficient Metadata Registration

Coupled with managing multimedia storage, the Nachet Datastore also seamlessly registers metadata into a database server. This double-edged approach ensures not just efficient storage, but also the organization and easy accessibility of your valuable data. 



##

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
    integer permission_id
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
  picture_seed{
    uuid id PK
    uuid picture_id FK
    uuid seed_id FK
    timestamp upload_date
  }
  seed{
    uuid id PK
    string name
    json information
    uuid object_type_id
    timestamp upload_date
  }
  object_type{
    integer id PK
    text name 
  }
  inference{
    uuid id PK
    json inference 
    uuid picture_id FK
    uuid user_id FK
    timestamp upload_date
  }
  model{
    uuid id PK
    text name
    text endpoint_name
    integer task_id FK
    uuid active_version FK
  }
  model_version{
    uuid id PK
    uuid model_id FK
    json data
    text version
    timestamp upload_date 
  }
  object{
    uuid id PK
    json box_metadata
    uuid inference_id FK
    integer type_id
    uuid verified_id
    boolean valid
    uuid top_inference FK
    timestamp upload_date
    timestamp updated_at
  }
  seed_object{
    uuid id PK
    uuid seed_id FK 
    uuid object_id FK
  }
  pipeline{
    uuid id PK
    text name
    boolean active
    boolean is_default
    json data
  }
  pipeline_model{
    uuid id PK
    uuid pipeline_id FK
    uuid model_id FK
  }
  pipeline_default{
    uuid id PK
    uuid pipeline_id FK
    uuid user_id FK
    timestamp update_date
  }
  group{
    uuid id PK
    text name
    int permission_id FK
    uuid owner_id FK
    timestamp upload_date
  }
  permission{
    int id
    text name
  }
  user_group{
    uuid id
    uuid user_id
    uuid group_id
    timestamp upload_date

  }
  group_container{
    uuid id
    uuid group_id
    uuid container_id
    timestamp upload_date
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
  picture |o--o{picture_seed: has
  picture_seed }o--o| seed: has
  object_type ||--|| seed: is
  user ||--o{ inference: requests
  inference ||--|| picture: infers
  inference }o--|| pipeline: uses
  inference ||--o{ object: detects
  object ||--o{ seed_object: is
  seed_object }o--|| seed: is
  object }o--|| object_type: is 
  user ||--||pipeline_default: select
  pipeline_default }o--||pipeline: is
  pipeline }o--o{ pipeline_model: uses
  model }o--o{ pipeline_model: uses
  model_version ||--o{ model: has
  user }o--o{ user_group: apart
  user_group }o--o{group: represent
  permission ||--|| user: has
  permission ||--|| group: has
  group }o--o{group_container: has
  container }o--o{group_container: represent
  container ||--o{picture_set: contains

```