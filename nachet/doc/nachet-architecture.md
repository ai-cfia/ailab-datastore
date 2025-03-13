# Database Architecture
  
## Needs

- A User must be able to take a picture on the app and it must be saved in the
  blob Storage.

- A User can upload a batch on pictures.

- A User can classify a picture with a selected pipeline which returns an
  inference that needs to be saved.
  
- A User can verify an inference by confirming the positive result, select the
  right seed from the topN result set (technically it shouldn't be the first
  one) or select a seed that isn't part of the topN.

- The application needs to save a list of known seeds.

- The application needs to save a list of all the Machine Learning versions.

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
    boolean manual_detection
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
  container{
    uuid id PK
    uuid owner_id FK
    boolean public
    timestamp creation_date
    timestamp updated_at
  }

  container ||--o{ picture_set: contain
  user ||--|{ picture_set: uploads
  picture_set ||--o{picture: contains
  picture ||--o{picture: cropped
  picture |o--o{picture_seed: has
  picture_seed }o--o| seed: has
  object_type ||--|| seed: is
  user ||--o{ inference: requests
  inference ||--|| picture: infers
  inference ||--o{ object: detects
  object ||--o{ seed_object: is
  seed_object }o--|| seed: is
  object }o--|| object_type: is 

  inference }o--|| pipeline: uses
  pipeline_default }o--||pipeline: is
  pipeline }o--o{ pipeline_model: uses
  model }o--o{ pipeline_model: uses
  model_version ||--o{ model: has
  user ||--||pipeline_default: select

  user ||--|{ picture_set: uploads
  picture_set ||--o{picture: contains
  picture ||--o{picture: cropped
  picture |o--o{picture_seed: has
  picture_seed }o--o| seed: has
  

```

  For more detail on the container, groups and user relationship use the
  [Datastore Architecture](../../datastore/doc/datastore.md)
