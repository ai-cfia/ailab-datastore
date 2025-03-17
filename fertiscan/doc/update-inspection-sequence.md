# Updating an Inspection Record

## Sequence Diagram

**Preconditions:**

- The inspection record must exist prior to the update.
- The inspection controller needs to be fetched and used to call `update_inspection()`

**Postconditions:**

- Records for organizations, labels, metrics, ingredients,
  micronutrients, guaranteed analysis, sub-labels, and fertilizers are created
  or updated.
- The existing inspection record is updated with the latest information.
- An updated version of the model is returned

```mermaid
sequenceDiagram
    participant Client
    participant IC as Fertiscan.Inspection_Controller

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
    participant fertilizer as fertilizer
    end
    participant DB as Database

    Client->>+IC: update_inspection(cursor, user_id, updated_data: dict | Inspection)

    IC->>DB: Validate user permissions & inspection state

    IC->> Qins: update_inspection()
    Qins-->>IC: updated_at timestamp

    Qins->>DB: UPDATE inspection SET verified, comment

    IC->> Qlabel: update_label_info()

    Qlabel->>DB: UPDATE label_information WHERE updated_data.product.label_id = label_id

    IC ->> Qorg : delete_absent_organisation_information_from_label()
    loop For each organization
        alt organization_information exists
            IC->>Qorg: update_organization_info()
            Qorg->>DB: UPDATE organisation_information WHERE ID = updated_data.organizations[i].org.id
        else new organization input from user
            IC->>Qorg:new_organization_information: new_organization_information()
            Qorg->>DB: INSERT INTO organisation_information
        end
    end

    IC ->> Qm: upsert_metric()
    Qm ->>DB: DELETE metric WHERE label_id
    Qm ->>DB: INSERT INTO metric

    IC ->>Qi: upsert_ingredient()
    Qi ->>DB: DELETE ingredient WHERE label_id
    Qi ->>DB: INSERT INTO ingredient

    IC ->>Qga: upsert_guaranteed_analysis()
    Qga ->>DB: DELETE guaranteed WHERE label_id
    Qga ->>DB: INSERT INTO guaranteed

    IC ->>Qsl: upsert_sub_label()
    Qsl ->>DB: SELECT sub_type
    Qsl ->>DB: DELETE sub_label WHERE label_id
    Qsl ->>DB: INSERT INTO sub_label

    IC ->>Qrg: update_registration_number()
    Qrg ->>DB: DELETE registration_number WHERE label_id
    Qrg ->>DB: INSERT INTO registration_number

    alt verified is true

        IC->>IC: Find if there is a registration number<br> for this fertilizer

        IC->>IC: upsert_organization(main_org_data)
        IC->>Qorg: SELECT id FROM organization WHERE name ILIKE main_org_name
        Qorg->>DB: organization_id

        IC->>fertilizer: upsert_fertilizer()
        fertilizer->>DB: INSERT INTO fertilizer ON CONFLICT (name) DO UPDATE RETURNING id;

    end
    IC -->>Client: updated_data with updated ids and timestamp

```

## Triggers to update

These triggers need to be updated to have the OLAP layer fully working. However, this layer is not a necessity to the application and its development as been paused

```mermaid

sequenceDiagram

participant c as Client
participant db as Database

box lightgreen OLTP
participant cli as label_children_Table
participant in as inspection_Table
end

links cli: {"instruction": "","caution": "","first_aid": "","warrantie": "","specification": "","ingredient": "","micronutrients": "","guaranteed_analysis": "","metrics": "","organization_information": ""}
    
box pink OLAP
participant ld as label_Dimension
participant if as inspection_Factual
end 
c ->> db: update label_id children
db ->> cli: call update f() of table
activate cli
cli -) cli: delete old record
cli -) ld: TRIGGER: remove OLD.child_label_id where label_id=label_info_id
cli -) cli: insert new record
cli -) ld: TRIGGER: add NEW.child_label_id where label_id=label_info_id
deactivate cli

c ->> db: update inspection <br>(NEW.verified=True)
db ->> in: UPDATE inspection
activate in
in -) if: TRIGGER: update company_id & manufacturer_id
activate if
if -) if: TRIGGER: protect original_data <br>(NEW.original_dataset = OLD.original_dataset)
deactivate if

deactivate in


```
