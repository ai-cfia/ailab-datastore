# Search Inspection Documentation

## Context

The User wants to be able to search within the datasets of existing inspection based on the following parameters:

- Fertilizer Name
- Registration number
- Lot number
- A timeframe (lower and upper bounds dates)
- Organization information (the entity responsable for the product)
    - Name
    - Phone number
    - Address

## Rules

We need to establish rules regarding our search. 

### String matching

- The search must allow for a case insensitive search, meaning the capitalisation of words must not be considered. Meaning if you search "ABC in the following dataset

**Dataset**
| ID  | Name |
|-----|------|
| 1   | ABC  |
| 2   | abc  |

**Results**
| ID  | Name |
|-----|------|
| 1   | ABC  |
| 2   | abc  |

- The results must be an exact match to the parameter given, meaning if you search "**ABC**" in the following dataset

**Dataset**
| ID  | Name |
|-----|------|
| 1   | **ABC**  |
| 2   | **ABC**D |
| 3   | **AB**   |
| 4   | abc  |

**Results**
| ID  | Name |
|-----|------|
| 1   | **ABC**  |
| 4   | abc  |

### Multiple Parameters

- For an entry with multiple parameters being evaluated, all parameters are evaluated using a logical "**AND**" therefor they mist all be a match for the entry to be returned as a result. Meaning if you search (**ABC**,**XYZ**) in the following dataset

**Dataset**
| ID  | first name |  Last name |
|-----|------|----| 
| 1   | **ABC**  | **XYZ** |
| 2   | **ABC**  | IJK |
| 3   | DEF  | **XYZ** |
| 4   | DEF  | IJK |

**Results**
| ID  | first name |  Last name |
|-----|------|----| 
| 1   | **ABC**  | **XYZ** |


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
  inspection {
    uuid id PK
    boolean verified
    TIMESTAMP upload_date
    TIMESTAMP updated_at
    uuid inspector_id FK
    uuid label_info_id Fk
    uuid fertilizer_id FK
    uuid picture_set_id FK
  }
  organization_information{
    uuid id PK
    string name 
    string website
    string phone_number
    string address
  }
  label_information{
    uuid id PK
    string name
    string lot_number
  }
    
  registration_number_information{
    uuid id PK
    string identifier
  }

  inspection ||--|| label_information : defines
  label_information ||--o| organization_information: company
  label_information ||--o|registration_number_information: defines
```

## Datastore Signature
``` python
def search_inspection(
    cursor:Cursor,
    fertilizer_name:str,
    reg_number:str,
    lot_number:str,
    inspector_name:str,
    date_of_inspection:str,
    organization_name:str,
    organization_address:str,
    organization_phone:str,
):
```

## Sequence of searching

```mermaid
sequenceDiagram
    title FertiScan Submit Form
    Actor User
    participant FS as FertiScan-Datastore
    participant Q as Query module
    participant DB as Database
    
    User ->> FS: search_inspection()
    FS ->> Q: search_organisation(<br> organization_name,<br>organization_address,<br>organization_phone)
    Q --) Q: build query with parameters
    Q->>DB: fetch query results 
    Q -->>FS: list of organisation information
    FS --)FS: append list of label_ids to fetch

    FS ->> Q: search_registration_number(<br>registration_number)
    Q --) Q: build query with parameters
    Q->>DB: fetch query results 
    Q -->>FS: list of registration number information
    FS --)FS: append list of label_ids to fetch
    
    FS ->> Q: search_inspection(<br>fertilizer_name,<br> lower_bound_date,<br>upper_bound_date,<br>lot_number,<br>label_ids)
    Q --) Q: build query with parameters
    Q->>DB: fetch query results 
    Q ->>FS: list of inspection resume
    FS-->User: list of inspection resume

```
