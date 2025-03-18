# Inspection registration Documentation

## Context

The User wants to digitalize a label picture on FertiScan. Therefore, the BE
uses it's models to digitalize the content and sends over a JSON with all the
information taken from the pictures. We need to parse the JSON, extract its
information and transform it into the right format then save correctly the
information into the DB linked to the pictures received.

## Prerequisites

- The user must be already registered

## Entity Used

``` mermaid

---
title: FertiScan Inspection DB Structure
---

%%{init: {
  "theme": "default",
  "themeCSS": [
    ".er.relationshipLabel { fill: black; }", 
    ".er.relationshipLabelBox { fill: white; }", 
    ".er.entityBox { fill: lightgray; }",
    "[id^=entity-] .er.entityBox { fill: lightgreen;}",
    "[id^=entity-timedimension] .er.entityBox { fill: pink;} ",
    "[id^=entity-labeldimension] .er.entityBox { fill: pink;} ",
    "[id^=entity-inspectionfactual] .er.entityBox { fill: pink;} "
    ]
}}%%
erDiagram
    
  inspection {
    uuid id PK
    boolean verified
    timestamp upload_date
    timestamp updated_at
    uuid inspector_id FK
    uuid label_info_id FK
    uuid fertilizer_id FK
    uuid sample_id FK
    uuid picture_set_id FK
    uuid container_id FK
  }

organization_information{
    uuid id PK
    string name 
    string website
    string phone_number
    string address
    boolean edited
  }
  label_information {
    uuid id PK
    string lot_number
    string npk
    float n
    float p
    float k 
    string guaranteed_title_en
    string guaranteed_title_fr
    boolean title_is_minimal
    boolean record_keeping
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
  
  registration_number_information{
    uuid id PK
    string identifier
    string name
    boolean is_an_ingredient 
  }
  sub_label {
    uuid id PK
    text text_content_fr
    text text_content_en
    boolean edited
    uuid label_id FK
    uuid sub_type_id FK
  }
  sub_type {
    uuid id PK
    text type_fr "unique"
    text type_en "unique"
  }
  micronutrient{
    uuid id PK
    string read_name
    float value
    string unit
    boolean edited
    language language
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
    language language
  }
    
  element_compound{
    int id PK
    string name_fr
    string name_en
    string symbol
  }


  inspection_factual ||--o{ time_dimension : "References"
  inspection_factual ||--o{ label_dimension : "References"
  metric }o--|| unit: defines
  inspection ||--|| label_information : defines
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|{ micronutrient: has
  label_information ||--|{ sub_label: has
  label_information ||--o{ registration_number_information: has
  label_information ||--o{ organization_information: responsible
  label_information ||--|{ metric: has
  sub_label }o--|| sub_type: defines

  micronutrient |o--|| element_compound: is
  guaranteed |o--|| element_compound: is

```

## Sequence of saving

The sequence of saving an inspection comes in two steps

1. Uploading the pictures
2. Uploading the label data

```mermaid
sequenceDiagram
    title FertiScan Submit Form
    actor C as Client
    participant FE as Frontend
    participant BE as Backend
    participant FS as FertiScan.Inspection_Controller
    participant DS as DataStore.Container_Controller
    participant DB as Database
    participant blob as BLOB Storage

    C ->> FE: Upload pictures
    FE ->> BE: Analysis label (user_id,[pictures])
    BE ->> BE: Digitalize label(pictures)
    BE ->> DS: Save images
    DS ->> blob: Upload images in new folder
    DS --> BE: folder_id UUID
    
    BE ->> FS: register analysis
    DS ->> DS: formatted_form = build_inspection_import(form)
    DS ->> DB: new_inspection(user_id,picture_set_id,formatted_form.json)
    DB --> DS: formatted_form_with_ids.json

    DS --> BE: formatted_form_with_ids.json
    BE ->> FE: Display_result(reworked_form_with_ids.json)
    FE --> C: Build HTML page based on the received json for confirmation

```

### new_inspection()

```mermaid
sequenceDiagram

    participant User
    participant FS as Fertiscan
    participant data as metadata module
    box Query Module
    participant Qins as inspection
    participant organization
    participant Qlabel as label
    participant Qorg as organization
    participant Qm as metric
    participant Qi as ingredient
    participant Qga as nutrients
    participant Qsl as sub_label
    participant Qrg as registration_number
    participant Qf as fertilizer
    end
    participant DB as Database

    User->>FS: Call new_inspection() 
    activate FS

    FS ->>DB: Verify permissions and parameters received

    FS ->> data: build_inspection_import()
    data ->> data: extract & transform Inspection data into Inspection model
    data -->>FS: formatted inspection

    FS ->> Qlabel: new_label_information()
    Qlabel ->>DB: INSERT INTO label_information
    DB --> FS: label_information_id

    loop for each metrics
      FS ->> Qm: new_metric()
      Qm ->>DB: SELECT new_metric_unit()
    end

    loop for each ingredients
      FS ->> Qi: new_ingredient()
      Qi ->>DB: SELECT SELECT new_ingredient()
    end

    loop for each sub_label_type
      FS ->>DB: get sub_type id
      loop for each sub_label record
        FS ->> Qsl: new_sub_label()
        Qsl ->>DB: INSERT INTO sub_label
      end
    end

    loop for each guaranteed_analysis record
      FS ->> Qga: new_guaranteed_analysis()
      Qga ->>DB: INSERT INTO guaranteed
    end

    loop for each registration_number record
      FS ->> Qrg: new_registration_number()
      Qrg ->>DB: INSERT INTO registration_number_information
    end

    loop for each organization_information record
      FS ->> Qrg: new_organization_information()
      Qrg ->>DB: INSERT INTO organization_information
    end

    FS ->> Qins: new_inspection()
    Qins ->>DB: INSERT INTO inspection
    DB--> FS: inspection id

    FS --> FS: Add ids to Inspection model
    FS --> FS: Inspection.model_validate()

    FS ->>Qins: save_inspection_original_dataset()
    Qins ->> DB: UPDATE inspection_factual SET original_dataset

    create participant IC as InspectionController
    FS ->> IC: InspectionController(validated_inspection_model)
    FS-->User: InspectionController

    deactivate FS
```
