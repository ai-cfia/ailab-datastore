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
    timestamp update_time
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
  }
  sample{
    uuid id PK
    uuid number
    Date collection_date
    uuid location
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
    text warranty

    uuid weight FK
    uuid density FK
    uuid volume FK
    uuid specification_id FK    
    uuid first_aid_id FK
    uuid warranty_id FK
    uuid instruction_id FK
    uuid caution_id FK
    uuid metric_id FK
  }

  specification{
    uuid id PK
    float humidity
    float ph
    float solubility
    boolean edited
  }  
  first_aid{
    uuid id PK
    text first_aid_fr
    text first_aid_en
    boolean edited
  }
  warranty{
    uuid id PK
    text warranty_fr
    text warranty_en
    boolean edited
  }
  instruction{
    uuid id PK
    text instruction_fr
    text instruction_en
    boolean edited
  }
  caution{
    uuid id PK
    text caution_fr
    text caution_en
    boolean edited
  }
  metric{
    uuid id PK
    float value
    uuid unit_id
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
  }
  guaranteed{
    uuid id PK
    string read_name
    float value
    string unit
    int element_id FK
    boolean edited
  }
  ingredient{
    uuid id PK
    boolean organic
    string name
    boolean edited
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
  analysis ||--|| user :does
  analysis ||--o{ picture :has
  analysis ||--|| fertilizer :is about
  analysis ||--|| label_information : defines
  province ||--|| region: apart of
  region ||--|| location: defines
  responsable ||--|| location: located
  sample ||--|| location: taken
  label_information ||--|o metric: weight
  label_information ||--|o metric: density
  label_information ||--|o metric: volume
  label_information ||--|| caution: defines
  label_information ||--|| instruction: defines
  label_information ||--|| first_aid: defines
  label_information ||--|{ ingredient: has
  label_information ||--|{ guaranteed: has
  label_information ||--|| specification: defines
  label_information ||--|| warranty: defines
  label_information ||--|{ micronutrient: has
  
  metric ||--|| unit: defines
  micronutrient ||--|| element_compound: is
  guaranteed ||--|| element_compound: is

```
