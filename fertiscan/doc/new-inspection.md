# Inspection registration Documentation

## Context

The User wants to digitalize a label picture on FertiScan. Therefore, the BE
uses it's models to digitalize the content and sends over a JSON with all the
information taken from the pictures. We need to parse the JSON, saves correctly
the information into the DB linked to the pictures received.

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

  fertilizer {
    uuid id PK
    string name "Unique"
    string registration_number
    timestamp upload_date
    timestamp update_at
    uuid latest_inspection_id FK
    uuid owner_id FK
  }organization_information{
    uuid id PK
    string name 
    string website
    string phone_number
    string address
    boolean edited
  }
  organization {
    uuid id PK
    uuid information_id FK
    uuid main_location_id FK
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
  sample {
    id uuid
    json data
  }
  




 

  inspection_factual {
    uuid inspection_id PK
    uuid inspector_id
    uuid label_info_id
    uuid time_id FK
    uuid sample_id
    uuid company_id
    uuid manufacturer_id
    uuid picture_set_id
    timestamp inspection_date
    json original_dataset
  }
  label_dimension {
    uuid label_id PK
    uuid company_info_id
    uuid company_location_id
    uuid manufacturer_info_id
    uuid manufacturer_location_id
    uuid[] instructions_ids "DEFAULT '{}'"
    uuid[] cautions_ids "DEFAULT '{}'"
    uuid[] first_aid_ids "DEFAULT '{}'"
    uuid[] warranties_ids "DEFAULT '{}'"
    uuid[] specification_ids "DEFAULT '{}'"
    uuid[] ingredient_ids "DEFAULT '{}'"
    uuid[] micronutrient_ids "DEFAULT '{}'"
    uuid[] guaranteed_ids "DEFAULT '{}'"
    uuid[] weight_ids "DEFAULT '{}'"
    uuid[] volume_ids "DEFAULT '{}'"
    uuid[] density_ids "DEFAULT '{}'"
  }
  time_dimension {
    uuid id PK
    date date_value
    int year
    int month
    int day
    text month_name
    text day_name
  }

  inspection_factual ||--o{ time_dimension : "References"
  inspection_factual ||--o{ label_dimension : "References"
  metric }o--|| unit: defines
  inspection ||--|| sample :"has"
  fertilizer ||--|| organization: responsible
  organization ||--||organization_information : defines
  inspection ||--|| fertilizer : about
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
  
    participant DB as Database
    participant Function as new_inspection()
    participant olap as OLAP dimension

    links olap: {"Inspection_Factual": "","Label_Dimension": "","Time_Dimension": ""}

    User->>DB: Call new_inspection()
    DB ->> Function: 
    activate Function

    Note over Function: Process Company Information
    Function->>DB: Call new_organization_info_located for Company
    DB-->>Function: Return company_id
    Function->>Function: Update input_json with company_id

    Note over Function: Process Manufacturer Information
    Function->>DB: Call new_organization_info_located for Manufacturer
    DB-->>Function: Return manufacturer_id
    Function->>Function: Update input_json with manufacturer_id

    Note over Function: Process Label Information
    Function->>DB: Call new_label_information
    DB -) olap: TRIGGER: Create new label_dimension
    DB-->>Function: Return label_info_id
    Function->>Function: Update input_json with label_info_id

    Note over Function: Process Weight Metrics
    loop For each weight record
        Function->>DB: Call new_metric_unit for Weight
        DB -) olap: TRIGGER: UPDATE label_dimension append weight_ids
        DB-->>Function: Return weight_id
    end

    Note over Function: Process Density Metric
    Function->>DB: Call new_metric_unit for Density
    DB -) olap: TRIGGER: UPDATE label_dimension append density_ids
    DB-->>Function: Return density_id

    Note over Function: Process Volume Metric
    Function->>DB: Call new_metric_unit for Volume
    DB -) olap: TRIGGER: UPDATE label_dimension append volume_ids
    DB-->>Function: Return volume_id

    Note over Function: Process Specifications
    loop For each specification record
        Function->>DB: Call new_specification
        DB -) olap: TRIGGER: UPDATE label_dimension append specification_ids
        DB-->>Function: Return specification_id
    end

    Note over Function: Process Ingredients
    loop For each ingredient record
        Function->>DB: Call new_ingredient
        DB -) olap: TRIGGER: UPDATE label_dimension append ingredient_ids
        DB-->>Function: Return ingredient_id
    end

    Note over Function: Process Sub Labels
    loop For each sub label record
        Function->>DB: Call new_sub_label
        DB -) olap: TRIGGER: UPDATE label_dimension append child_label_ids child_label = sub_label_type
        DB-->>Function: Return sub_label_id
    end

    Note over Function: Process Micronutrients
    loop For each micronutrient record
        Function->>DB: Call new_micronutrient
        DB -) olap: TRIGGER: UPDATE label_dimension append micronutrients_ids
        DB-->>Function: Return micronutrient_id
    end

    Note over Function: Process Guaranteed Analysis
    loop For each guaranteed analysis record
        Function->>DB: Call new_guaranteed_analysis
        DB -) olap: TRIGGER: UPDATE label_dimension append guaranteed_ids
        DB-->>Function: Return guaranteed_analysis_id
    end

    Note over Function: Insert Inspection
    Function->>DB: Insert into inspection
    DB-->>Function: Return inspection_id_value
    Function->>Function: Update input_json with inspection_id_value

    DB->>olap: TRIGGER: update inspection_factual SET original_dataset = input_json

    Function-->>User: Return input_json
    deactivate Function
```
