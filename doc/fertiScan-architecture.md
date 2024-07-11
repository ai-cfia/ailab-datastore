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
    uuid picture_set_id FK
    uuid parent FK
    int nb_object
    boolean verified
    timestamp upload_date 
  }
  analysis {
    uuid id PK
    uuid user_id FK
    boolean verified
    uuid label_info fk
    TIMESTAMP upload_date
    TIMESTAMP updated_at
    uuid fertilizer_id
    uuid sample_id FK
    uuid company_id FK
    uuid manufacturer_id FK
    uuid picture_id
  }
  fertilizer{
    uuid id PK
    string name "Unique"
    string registration_number
    timestamp upload_date
    timestamp update_at
    uuid latest_analysis FK
    uuid respo_id FK
  }
  responsable{
    uuid id PK
    string name
    string website
    string phone_number
    uuid location_id
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
    uuid location FK
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
    uuid label_id FK
    boolean edited
    sub_type_id uuid FK
  }
  sub_type{
    id uuid FK
    text type_fr "unique"
    text type_en "unique"
  }
  metric{
    uuid id PK
    float value
    uuid unit_id FK
    boolean edited
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
    int element_id FK
    boolean edited
    label_id uuid FK
  }
  guaranteed{
    uuid id PK
    string read_name
    float value
    string unit
    int element_id FK
    boolean edited
    label_id uuid FK
  }
  ingredient{
    uuid id PK
    boolean organic
    string name
    boolean edited
    label_id uuid FK
  }
  element_compound{
    int id PK
    string name_fr
    string name_en
    string symbol
  }
  analysis ||--|| sample :has
  picture }o--|| picture_set: contains
  analysis ||--|| responsable :manage
  fertilizer ||--|| responsable: manage
  analysis ||--|| users :does
  analysis ||--o{ picture :has
  analysis ||--|| fertilizer : represent
  analysis ||--|| label_information : defines
  province ||--|| region: apart
  region ||--|| location: defines
  responsable ||--|| location: located
  sample ||--|| location: taken
  label_information ||--|o metric: weight
  label_information ||--|o metric: density
  label_information ||--|o metric: volume
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|{ micronutrient: has
  label_information ||--|{ sub_label: has
  sub_label }o--|| sub_type: defines
  
  metric ||--|| unit: defines
  micronutrient ||--|| element_compound: is
  guaranteed ||--|| element_compound: is

```
