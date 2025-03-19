# Inference

## Contexte

We have a process in place to requests our pipelines to perfom an inference on a
picture in our blob storage. Therefore, we would need a process to save the
inference result.

## Prerequisites

- The user must be signed in

- The user has already uploaded a picture in the blob storage with a Container Controller.

### Database

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

- `object` represents object identified on the picture. There should be a box
  created on the picture by the model to frame the object.
- `seed_object` represent the guess of what the model think is the object

## Sequence of saving the inference

``` mermaid

sequenceDiagram;
  actor User
  participant FE as Frontend
  participant BE as Backend
  participant DS as Datastore
  box query module
    participant inf as inference
    participant seed as seed
  end
  participant CC as Container Controller
  participant ML as Pipeline

  box grey Storage services
    participant DB as PostgreSQL Database
    participant AZ as Azure Storage
  end

    User ->>FE: Classify picture
    FE -) BE: Classify_picture(picture_id)
    BE -) CC: picture_url = model.Folders.path + "/" + str(picture_id)
    BE -) CC: get_picture_blob()
    CC-) AZ: download_blob()
    AZ -->BE: picture in BLOB format
    BE -) ML: inference_request(pipeline,picture)
    ML ->> BE : inference.json
    
    BE -) DS: register_inference_result(inference, picture_id)
    
    DS ->> DS: format inference
    DS ->> DB: get_pipeline_id if not given as parameters

    DS->>inf: new_inference()
    inf-)DB:INSERT INTO inference

    loop for each box
    
        DS->>inf: new_inference_object()
        inf-)DB:INSERT INTO object

        loop for each inference guess

            DS ->>DS: verify if it is the top guess
            DS ->> seed: get_seed_id()
            seed -) DB: SELECT seed WHERE name ILIKE

            DS ->> inf: new_seed_object()
            inf-)DB: INSERT INTO seed_obj
        end

        DS ->>inf: set_inference_object_top_id(top_inference_guess_id)
        
    end
    
    DS->>DS: Inference.model_validate(formatted_inference_with_ids)
    DS-->BE: inference_model (dict)
    BE-->FE: inference_model
    FE-->User: Display inference results

```
