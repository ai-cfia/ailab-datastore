# FertiScan DB Architecture

## Needs

- A User must be able to take a picture on the app and it must be saved in the
  blob Storage.

- A User can do an analysis of a label during its inspection and must confirm
  the digitalization of the label_information.

- A User must be able to store its inspection about fertilizers

- A User must be able to to a search about fertilizer with filters

- The application needs to register the structure of the Blob Storage used.

## FertiScan Operational Transaction Database Architecture

```mermaid
---
title: FertiScan Operational Transaction DB Structure
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
  users {
    uuid id PK
    string email
    timestamp registration_date
    timestamp updated_at
    uuid default_set_id FK
  }
  picture_set {
    uuid id PK
    json picture_set
    uuid owner_id FK
    date upload_date
    string name
  }
  picture {
    uuid id PK
    json picture
    int nb_obj
    uuid picture_set_id FK
    boolean verified
    timestamp upload_date
  }
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
  }
  fertilizer {
    uuid id PK
    string name "Unique"
    string registration_number
    timestamp upload_date
    timestamp update_at
    uuid latest_inspection_id FK
    uuid owner_id FK
  }
  organization {
    uuid id PK
    uuid information_id FK
    uuid main_location_id FK
  }
  organization_information{
    uuid id PK
    string name 
    string website
    string phone_number
    uuid location_id FK
    boolean edited
  }
  location {
    uuid id PK
    string name
    string address
    uuid region_id FK
    uuid owner_id FK
  }
  sample {
    uuid id PK
    uuid number
    date collection_date
    uuid location FK
  }
  province {
    int id PK
    string name "Unique"
  }
  region {
    uuid id PK
    int province_id FK
    string name
  }
  label_information {
    uuid id PK
    string lot_number
    string npk
    float n
    float p
    float k
    uuid company_info_id FK
    uuid manufacturer_info_id FK
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
  specification {
    uuid id PK
    float humidity
    float ph
    float solubility
    boolean edited
    uuid label_id FK
    enum language
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
  inspection ||--|| sample :has
  picture_set ||--|{picture : contains
  fertilizer ||--|| organization: responsable
  organization_information ||--|| location: Hosts
  location ||--|| region: defines
  region ||--|| province: apart
  inspection ||--|| fertilizer : about
  inspection }o--|| users :inspect
  inspection ||--o| picture_set :has
  inspection ||--|| label_information : defines
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|{ micronutrient: has
  label_information ||--|{ specification: has
  label_information ||--|{ sub_label: has
  label_information ||--o{ registration_number_information: has
  label_information ||--o| organization_information: company
  label_information ||--o| organization_information: manufacturer
  organization_information ||--|| organization: defines
  label_information ||--|{ metric: has
  sub_label }o--|| sub_type: defines
  users ||--o{ picture_set: owns
  metric }o--|| unit: defines

  micronutrient |o--|| element_compound: is
  guaranteed |o--|| element_compound: is

```

### FertiScan Operational Analytic Database Architecture

```mermaid
---
title: FertiScan Operational DB Structure
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

```
