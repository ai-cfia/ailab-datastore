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
title: FertiScan DB Structure
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
    
    DS ->> DB: new_picture_set(user_id)
    activate DS
    DB --> DS: picture_set_id
    DS ->>blob: new_folder(picture_set_id)
    DS ->> DS: upload_pictures(user_id,pictures,picture_set_id,container_client)
    DS ->> DB: register all pictures
    DB --> DS: picture_ids
    DS ->> blob: container_client.upload_pictures(pictures,picture_set_id)
    deactivate DS
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