# Inference

## Contexte

We have a process in place to requests our pipelines to perfom an inference on a
picture in our blob storage. Therefore, we would need a process to save the
inference result and also incorporate a a user validation

## Prerequisites

- The user must be signed in

- The user has picture uploaded in the blob storage and with its metadata saved
  within the DB.

``` mermaid

---
title: Nachet DB Structure for Inference
---
erDiagram
    seed{
        uuid id
        uuid object_type_id
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

  user ||--o{ inference: requests
  inference ||--|| picture: infers
  inference }o--|| pipeline: uses
  inference ||--o{ object: detects
  object ||--o{ seed_object: is
  seed_object }o--|| seed: is
  object }o--|| object_type: is 
```

## Sequence of saving the inference

``` mermaid

sequenceDiagram;
  actor User
  box grey Ai-Lab services
  participant Frontend
  participant Backend
  participant Datastore
  participant ML
  end
  box grey Storage services
  participant PostgreSQL Database
  participant Azure Storage
  end

    User ->> Frontend: Classify picture
    Frontend -) Backend: Classify_picture(picture_id)
    Backend -) Datastore: get_picture_url(picture_id)
    Datastore ->> Backend : picture_url
    Backend -) ML: inference_request(pipeline,picture)
    ML ->> Backend : inference.json
    Backend -) Datastore: register_inference_result(inference)
    Datastore ->> Datastore: trim_inference
    Datastore -) PostgreSQL Database: new_inference(trimmed_inference)
    Datastore ->> Datastore: Add {inference_id: uuid}
    loop each box 
        Datastore ->> Datastore: build_box_metadata(box_metadata)
        Datastore ->> PostgreSQL: new_inference_object(box_metadata)
        Datastore ->> Datastore: Add {box_id: uuid}
        loop each guess
            Datastore -) PostgreSQL: get_seed_id(seed_name)
            Datastore ->> PostgreSQL: new_seed_object(box_id,seed_id)
            Datastore ->> Datastore: Add {object_id: uuid}
        end
        Datastore  ->> PostgreSQL: set_inference_object_top_id(object_id, top_seed_object_id)
        Datastore ->> Backend: inference_with_id.json
    end


```
