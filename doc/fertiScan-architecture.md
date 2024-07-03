# FertiScan DB Architecture

This is the doc about the FertiScan Database Architecture

``` mermaid

---
title: FertiScan DB Structure
---
erDiagram
  user{
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
    uuid latest_Analyses FK
    uuid respo_id 
    uuid fertilizer_information FK
    uuid manufacturer_companie_id FK
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
  }
  warranty{
    uuid id PK
    text warranty_fr
    text warranty_en
  }
  instruction{
    uuid id PK
    text instruction_fr
    text instruction_en
  }
  caution{
    uuid id PK
    text caution_fr
    text caution_en
  }
  metric{
    uuid id PK
    float value
    uuid unit_id
  }
  unit{
    uuid id PK
    string unit
    float to_metric_unit
  }
  micronutrient{
    uuid id PK
    string read_name
    float value
    string unit
    int element_id FK
  }
  guaranteed{
    uuid id PK
    string read_name
    float value
    string unit
    int element_id FK
  }
  ingredient{
    uuid id PK
    boolean organic
    string name
  }
  element_compound{
    int id PK
    string name_fr
    string name_en
    string symbol
  }
  analysis ||--|| sample :test
  picture }o--|| picture_set: contains
  analysis ||--|| responsable :test
  analysis ||--|| user :test
  analysis ||--o{ picture :test
  analysis ||--|| fertilizer :test
  analysis ||--|| label_information :test
  province ||--|| region: test
  region ||--|| location: test
  responsable ||--|| location: test
  sample ||--|| location: test
  label_information ||--|| metric: test
  label_information ||--|| caution: test
  label_information ||--|| instruction: test
  label_information ||--|| first_aid: test
  label_information ||--|| ingredient: test
  label_information ||--|| guaranteed: test
  label_information ||--|| specification: test
  label_information ||--|| warranty: test
  label_information ||--|| micronutrient: test
  
  metric ||--|| unit: test
  micronutrient ||--|| element_compound: test
  guaranteed ||--|| element_compound: test


```