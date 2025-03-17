# Inspection fetching documentation

## Context

The User want to visualize the digitalization of a label, whether it is verified
or not. Therefore, the BE needs to be able to fetch an inspection in json format
from the database with only its id .

## Prerequisites

- The inspection id must be of a valid inspection

## Post Condition

- The User receive an InspectionController allowing them to vizualize the model attribute

## Entity Used

``` mermaid
---
title: FertiScan Inspection DB Structure
---
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

## Sequence of Getting the inspection

```mermaid
sequenceDiagram
    title FertiScan Get Inspection Form
    actor C as Client
    participant F as Fertiscan
    participant data as metadata.inspection

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


C ->> F: get_inspection(cursor,inspection_id)
activate F
F ->> DB: Validate inspection_id exists
F ->> data: build_inspection_export()
activate data

data ->>Qins: get_inspection()
Qins ->> DB: SELECT inspection

data ->>Qins: get_inspection()
Qins ->> DB: SELECT inspection
DB -->>data: label_information_id

data ->>Qlabel: get_label_information_json()
Qlabel ->> DB: SELECT get_label_info_json()
DB -->>data: dict
data ->>data: ProductInformation(**product_info)

data ->>Qm: get_metrics_json()
Qm ->> DB: SELECT get_metrics_json()
DB -->>data: dict
data ->>data: Metrics.model_validate()

data ->>Qrg: get_registration_numbers_json()
Qrg ->> DB: SELECT get_registration_numbers_json()
DB -->>data: dict
data ->>data: RegistrationNumber.model_validate()

data ->>Qorg: get_organizations_info_json()
Qorg ->> DB: SELECT get_organizations_info_json()
DB -->>data: dict
data ->>data: OrganizationInformation.model_validate()

data ->>Qsl: get_sub_label_json()
Qsl ->> DB: SELECT get_sub_label_json()
DB -->>data: dict
data ->>data: SubLabel.model_validate()

data ->>Qga: get_guaranteed_analysis_json()
Qga ->> DB: SELECT get_guaranteed_analysis_json()
DB -->>data: dict
data ->>data: GuaranteedAnalysis.model_validate()

alt if not record_keeping

data ->>Qi: get_ingredient_json()
Qi ->> DB: SELECT get_ingredient_json()
DB -->>data: dict
data ->>data: ValuesObjects.model_validate()
end 

data->>data: Inspection()
data-->F:inspection model
deactivate data
create Participant IC as Inspection Controller
F ->>IC: InspectionController(inspection_model)
F -->C: Inspection Controller
deactivate F

```
