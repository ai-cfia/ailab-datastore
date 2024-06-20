# Inference

## Contexte

We have a process in place to requests our pipelines to perfom an inference on a
picture in our blob storage and register the result in the database. Therefore,
we would need a process to register the user's feedback of said inference

## Prerequisites

- The user must be signed in

- The user has a picture uploaded in the blob storage and with its metadata saved
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
        Frontend -) Backend: Inference result positive (user_id, boxes)
        Backend -) Datastore: new_perfect_inference_feeback(inference_id, user_id, boxes_id)
        Note over Backend, Datastore : Each box_id is an inference object in db
        alt if inference not already verified
                Datastore ->> Database: Set each object.valid = True & object.verified_id=object.top_id
        end
    else Annotated Inference
        Frontend -) Backend: Inference feedback (inference_feedback.json,user_id,inference_id)
        Backend ->> Datastore: new_correction_feedback(inference_feedback.json)
        alt inference not already verified
            Datastore -> Database: Get Inference_result(inference_id)
            loop each Boxes
                alt object not already verified
                    Datastore-)Database: update object.verified & object.valid
                end
            end
        end
    end

```

## Sequence of checking the corrected inference fields

``` mermaid

sequenceDiagram;
  actor User
  participant Datastore
  participant f as inference feedback
  participant Database
  
    User --> Datastore: gives 
    Datastore -->> f: has key "inferenceId"
    rect rgb(255, 170, 170)
    alt no "inferenceId" key 
           
        Datastore --x User: Error
    end
    end
    Datastore -->> f: has key "userId"
    rect rgb(255, 170, 170)
    alt no "userId" key    
        Datastore -x User: Error
    end
    end
    Datastore -) Database: is_a_user(user_id)
    rect rgb(255, 170, 170)
    alt not a registered user
        Datastore -x User: Error
    end
    end
    Datastore -) Database: is_inference_verified(inference_id)
    rect rgb(255, 170, 170)
    alt inference is verified
        Datastore --x User: Error
    end
    end
    loop for each box in "boxes"
        Datastore -->> f: get "boxId"
        Datastore -->> f: get "classId" (seed_id) & "label" (seed_name)
        rect rgb(250,150,250)
        note right of f: The box was created by the user
        alt no boxId
            Datastore -) Database: new_inference_object(inference_id,box_metadata)
            Database -->> Datastore: object_id
            Datastore -) Database: new_seed_object(object_id,seed_id)
            Database -->> Datastore: seed_object_id
            Datastore -) Database: set_inference_object_verified_id(object_id,seed_object_id)
        end
        end
        rect rgb(255,200,150)
        Note right of f: Finding the seed_id
        alt no seed_id
            alt no seed_name
                note right of Datastore: The box was deleted by the user and is not valid anymore.
            else 
                Datastore -) Database: is_seed_registered(seed_name)
                alt seed not registered
                note right of Datastore: The selected seed is not known in our database.
                    Datastore -) Database: new_seed(seed_name)
                    Database -->> Datastore: seed_id
                end
            end
        end
        end
        Datastore -) Database: is_object_verified(box_id)
        rect rgb(255, 170, 170)
        alt box is verified
            Datastore --x User: Error
        end
        end
        rect rgb(150,255,255)
        Note right of f: Checking box_metadata update
        Datastore -) Database: get_inference_object(box_id)
        Datastore -) Database: new_top_id = get_seed_object_id(seed_id,box_id)
        alt box_metadata has changed
            Datastore -) Database: set_object_box_metadata(box_id, box_metadata)
        end
        end
        rect rgb(150,255,200)
        Note right of f: Checking which guess <br> is the correct one
        alt new_top_id is None
        note right of Datastore: The seed selected was not part of the inference guesses
            Datastore -) Database: seed_object_id = new_seed_object(object_id,seed_id)
            Datastore -) Database: set_inference_object_verified_id(object_id,seed_object_id)
        else new_top_id != old_top_id
        note right of Datastore: The seed was not correctly identified but is within the inference guesses
            Datastore -) Database: set_inference_object_verified_id(object_id,new_top_id)
        else new_top_id == old_top_id
        note right of Datastore: The seed was correctly identified
            Datastore -) Database: set_inference_object_verified_id(object_id,old_top_id)
        end
        end
        Datastore -) Database: set_inference_object_valid(box_id,is_valid)
    end
    Datastore -) Database: verify_inference_status(inference_id,user_id)

```
