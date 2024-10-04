# Inspection fetching documentation

## Context

The User want to visualize the digitalization of a label, whether it is verified
or not. Therefore, the BE needs to be able to fetch an inspection in json format
from the database with only its id .

## Prerequisites

- The inspection id must be of a valid inspection

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
  inspection {
    uuid inspector_id FK
    uuid label_info_id Fk
    uuid sample_id FK
    uuid company_id FK
    uuid manufacturer_id FK
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
  organization_information ||--|| location: Hosts
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
  metric }|--|| unit: defines

```

## Sequence of Getting the inspection

```mermaid
sequenceDiagram
    title FertiScan Get Inspection Form
    actor C as Client
    participant FE as Frontend
    participant BE as FertiScan
    participant DS as DataStore
    participant Metadata
    participant DB as Database

C -) FE: Select form to view
FE -) BE: get_inspection(inspection_id,user_id)
BE -) DS: get_full_inspection(cursor,inspection_id)
DS -) DB: is_inspection(inspection_id)?
DS --> DS: did we received fks?
DS -) DB: get_inspection_fks(inspection_id)
DB --> DS : label_id, user_id, ...
DS -) DS: check fks
DS -) Metadata: build_inspection_export(inspection_id,label_id)
activate Metadata
Note right of Metadata: Process detailed <br> under this graph
Metadata -->> DS: inspection_json
deactivate Metadata
DS -->> BE: inspection_json
BE -->> FE: inspection_json
FE -->> C: Display inspection

```

## Sequence of build_inspection_export

```mermaid
sequenceDiagram
    title FertiScan Get Inspection Form
    participant DS as DataStore
    participant M as Metadata
    participant P as Pydantic models
    participant DB as Database

DS -) M: build_inspection_export(inspection_id,label_id)
M -) M : inspection_json = {inspection_id: inspection_id}
M -) DB: get_label_info_json(label_id)
DB --> M: label_info_json
M -) DB: get_metrics_json(label_id)
DB --> M: metrics_json
M -) M : label_info_json.update(metrics_json)
M -->> P : ProductInfo(label_info_json)
M -) M : inspection_json.update(label_info_json)
M -) DB: get_sub_label_json(label_id)
DB --> M: sub_label_json
loop for each sub_label.keys()
    M-->>P: SubLabel(sub_label.get(keys))
end
M -) M : inspection_json.update(sub_label_json)

M -) DB: get_ingredients_json(label_id)
DB --> M: ingredient_json
M -->> P: ValuesObject(ingredient_json)
M -) M : inspection_json.update(ingredient_json)

M -) DB: get_nutrients_json(label_id)
DB --> M: nutrients_json
M --> P: ValuesObject(nutrients_json)
M -) M : inspection_json.update(nutrients_json)

M -) DB: get_guaranteed_analysis_json(label_id)
DB --> M: guaranteed_analysis_json
loop for each guaranteed_analysis entry
    M-->>P: Value(guaranteed_analysis_json[i])
end
M -) M : inspection_json.update(guaranteed_analysis_json)

M -) DB: get_specifications_json(label_id)
DB --> M: specification_json
M -->> P: Specifications(specification_json)
M -) M : inspection_json.update(specification_json)

M -) P: Inspection(inspection_json)

M --> DS: inspection_json.dump_model()

```
