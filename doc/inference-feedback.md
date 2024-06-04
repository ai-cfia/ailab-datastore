# Inference

## Contexte

We have a process in place to requests our pipelines to perfom an inference on a
picture in our blob storage and register the result in the database. Therefor,
we would need a process to register the user's feedback of said inference

## Prerequisites

- The user must be signed in

- The user has picture uploaded in the blob storage and with its metadata saved
  within the DB.

- The inference result has been saved into the DB.

``` mermaid

---
title: Nachet Architecture for Inference
---
erDiagram
    seed{
        uuid id
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
        boolean verified
        boolean modified
        uuid top_guess FK
        timestamp upload_date
        timestamp updated_at
    }
    seed_object{
        uuid id PK
        uuid seed_id FK 
        uuid object_id FK
        float score
    }

  user ||--o{ inference: requests
  inference ||--|| picture: infers
  inference }o--|| pipeline: creates
  inference ||--o{ object: detects
  object ||--o{ seed_object: is
  seed_object }o--|| seed: is
```

## Sequence of saving the inference feedback

``` mermaid

sequenceDiagram;
  actor User
  participant Frontend
  participant Backend
  participant Datastore
  participant Database
  

    User ->> Frontend: Validate inference
    alt Perfect Inference
    Frontend -) Backend: Inference result positive (user_id,inference_id)
    Backend -) Datastore: Inference result positive (user_id,inference_id)
    Datastore ->> Database: Set each object.verified = True & object.modified=False
    else Annotated Inference
    Frontend -) Backend: Inference feedback (inference_feedback.json,user_id,inference_id)
    Backend ->> Datastore: Inference feedback (inference_feedback.json, user_id, inference_id)
    Datastore -> Database: Get Inference_result(inference_id)
        loop each Boxes
            alt box has an id value
                alt inference_feedback.box.verified= False
                    Datastore --> Datastore: Next box & flag_all_box_verified=False
                else
                    Datastore -) Database: Set object.verified=True & object.verified_by=user_id
                    Datastore -) Datastore: Compare label & box coordinate
                    alt label value empty
                        Datastore -) Database: Set object.top_inference=Null
                        Datastore -) Database: Set object.modified=False                   
                    else label or box coordinate are changed & not empty
                        Datastore -) Database: Update object.top_inference & object.box_metadata
                        Note over Datastore,Database: if the top label is not part of the seed_object guesses, <br>we will need to create a new instance of seed_object.
                        Datastore -) Database: Set object.modified=true
                    else label and box haven't changed
                        Datastore -) Database: Set object.modified=False
                    end
                end
            else box has no id value
                Datastore -) Database: Create new object and seed_object
            end
        end
        alt if flag_all_box_verified=True
            Datastore -) Database: Set Inference.verified=true
        end
    end
    


```
