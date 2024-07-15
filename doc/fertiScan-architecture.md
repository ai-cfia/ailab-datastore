# FertiScan DB Architecture

This is the doc about the FertiScan Database Architecture

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
    uuid label_info fk
    uuid fertilizer_id FK
    uuid sample_id FK
    uuid company_id FK
    uuid manufacturer_id FK
    uuid picture_set_id FK
  }
  fertilizer{
    uuid id PK
    string name "Unique"
    string registration_number
    timestamp upload_date
    timestamp update_at
    uuid latest_inspection_id FK
    uuid owner_id FK
  }
  organization{
    uuid id PK
    string name "unique"
    string website
    string phone_number
    uuid main_location_id FK
  }
  organization_location{
    uuid id PK
    uuid location_id FK
    uuid organization_id FK
  }
  location{
    uuid id PK
    string address
    region_id uuid FK
  }
  sample{
    uuid id PK
    uuid number
    Date collection_date
  }
  province{
    int id PK
    string name "Unique"
  }
  region{
    uuid id PK
    int province_id FK
    string name
  }
  label_information{
    uuid id PK
    string lot_number
    string npk
    string registration_number
    float n
    float p
    float k

    uuid weight_id FK
    uuid density_id FK
    uuid volume_id FK
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
  metric{
    uuid id PK
    float value
    boolean edited
    uuid unit_id FK
  }
  unit{
    uuid id PK
    string unit
    float to_si_unit
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
  inspection ||--|| sample :has
  picture_set ||--|{picture : contains
  inspection ||--o| organization: manufacturer
  inspection ||--o| organization: company
  fertilizer ||--|| organization: responsable
  inspection ||--|| users :inspect
  inspection ||--o| picture_set :has
  inspection ||--|| fertilizer : about
  inspection ||--|| label_information : defines
  region ||--|| location: defines
  region ||--|| province: apart
  organization ||--|{ organization_location: has
  location ||--|| organization_location: defines
  label_information ||--|o metric: weight
  label_information ||--|o metric: density
  label_information ||--|o metric: volume
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|{ micronutrient: has
  label_information ||--|{ specification: has
  label_information ||--|{ sub_label: has
  sub_label }o--|| sub_type: defines
  
  metric ||--|| unit: defines
  micronutrient ||--|| element_compound: is
  guaranteed ||--|| element_compound: is

```