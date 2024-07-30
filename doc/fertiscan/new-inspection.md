# Inspection registration Documentation

## Context:
The User wants to digitalize a label picture on FertiScan. Therefore, the BE uses it's models to digitalize the content and sends over a JSON with all the information taken from the pictures. We need to parse the JSON, saves correctly the information into the DB linked to the pictures received.

## Prerequisites

- The user must be already registered

## Entity Used

``` mermaid

---
title: FertiScan DB Structure
---
erDiagram
  users{
    uuid id PK
    string email
    timestamp registration_date
    timestamp updated_at
    uuid default_set_id FK
  }
  picture_set{
    uuid id PK
    string name
    json picture_set
    uuid owner_id FK
    timestamp upload_date
  }
  picture{
    uuid id PK
    json picture
    boolean used_for_digitalization
    timestamp upload_date 
    uuid picture_set_id FK
    uuid parent_picture_id FK
  }
  inspection {
    uuid id PK
    boolean verified
    TIMESTAMP upload_date
    TIMESTAMP updated_at
    uuid inspector_id FK
    uuid label_info_id Fk
    uuid fertilizer_id FK
    uuid sample_id FK
    uuid company_id FK
    uuid manufacturer_id FK
    uuid picture_set_id FK
  }
  organization_information{
    uuid id PK
    string name 
    string website
    string phone_number
    uuid location_id FK
  }
  location{
    uuid id PK
    string address
    uuid organization_id FK
    uuid region_id FK
  }
  label_information{
    uuid id PK
    string lot_number
    string npk
    string registration_number
    float n
    float p
    float k
    uuid company_info_id FK
    uuid manufacturer_info_id FK
  }
  sub_label{
    uuid id PK
    text content_fr
    text content_en
    boolean edited
    uuid label_id FK
    uuid sub_type_id FK
  }
  sub_type{
    id uuid PK
    text type_fr "unique"
    text type_en "unique"
  }
  specification{
    id uuid PK
    float humidity
    float ph
    float solubility
    boolean edited
    uuid label_id FK
  }
  micronutrient{
    uuid id PK
    string read_name
    float value
    string unit
    boolean edited
    uuid label_id FK
    int element_id FK
  }
  guaranteed{
    uuid id PK
    string read_name
    float value
    string unit
    boolean edited
    int element_id FK
    uuid label_id FK
  }
  ingredient{
    uuid id PK
    boolean organic
    string name
    boolean edited
    uuid label_id FK
  }
  element_compound{
    int id PK
    string name_fr
    string name_en
    string symbol
  }
    metric{
    uuid id PK
    float value
    boolean edited
    ENUM metric_type 
    uuid unit_id FK
    uuid label_id FK
  }
  unit{
    uuid id PK
    string unit
    float to_si_unit
  }
  picture_set ||--|{picture : contains
  organization_information ||--|| location: Hosts
  inspection }|--|| users :inspect
  inspection ||--o| picture_set :has
  inspection ||--|| label_information : defines
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|{ micronutrient: has
  label_information ||--|{ specification: has
  label_information ||--|{ sub_label: has
  label_information ||--o| organization_information: company
  label_information ||--o| organization_information: manufacturer
  label_information ||--|{ metric: has
  sub_label }o--|| sub_type: defines
  users ||--o{ picture_set: owns
  metric }|--|| unit: defines

  micronutrient ||--|| element_compound: is
  guaranteed ||--|| element_compound: is

```

## Sequence of saving

```mermaid
sequenceDiagram
    title FertiScan Submit Form
    actor C as Client
    participant FE as Frontend
    participant BE as FertiScan
    participant DS as DataStore
    participant DB as Database
    participant blob as BLOB Storage

    C ->> FE: Upload pictures
    FE ->> BE: Analysis label (user_id,[pictures])
    BE ->> BE: Digitalize label(pictures)
    BE ->> DS: register_analysis(cursor,user_id,pictures,form.json)
    DS ->> DS: Manage pictures
    activate DS
    DS ->> DB: new_picture_set(user_id)
    DB --> DS: picture_set_id
    DB ->>blob: new_folder(picture_set_id)
    DS ->> DS: upload_pictures(user_id,pictures,picture_set_id,container_client)
    DS ->> DB: register all pictures
    DB --> DS: picture_ids
    DB ->> blob: container_client.upload_pictures(pictures,picture_set_id)
    deactivate DS
    DS ->> DS: formatted_form = build_inspection_import(form)
    DS ->> DB: new_inspection(user_id,picture_set_id,formatted_form.json)
    DB --> DS: formatted_form_with_ids

    DS --> BE: reworked_form_with_ids.json
    BE ->> FE: Display_result(reworked_form_with_ids.json)
    FE --> C: Build HTML page based on the received json for confirmation

```

## Sequence of updating

TODO
