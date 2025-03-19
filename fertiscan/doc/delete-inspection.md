# Deleting an Inspection Record



## **Preconditions:**

- The inspection record must exist prior to the update.
- The InspectionController must of been fetch

## **Postconditions:**

- The inspection record is deleted along with the underlying table records.
- The pictures and folder are deleted from the Storage

### delete_inspection()

```mermaid

---
title: FertiScan Delete Inspection Sequence
---

sequenceDiagram
    participant Client
    participant IC as Inspection Controller
    box Query Module
    participant Qins as inspection
    end
    participant DB as DB
    participant AZ as Azure Storage

    Client->>IC: delete_inspection()

    IC ->> DB: verify parameters validity and user permissions
    
    IC ->> Qins: delete_inspection()
    Qins ->> DB: SELECT delete_inspection()
    DB->>DB: DELETE where id=inspection_id RETURNING *
    DB->>DB: trigger DELETE sample where id=deleted_inspection.sample_id
    DB->>DB: trigger cascade DELETE label_information where id=deleted_inspection.label_info_id
    DB->>DB: replace fertilizer.latest_inspection_id
    DB-->IC: return deleted inspection data
    create participant CC as Container Controller
    IC->>CC: get_container_controller(model.container_id)
    IC->>CC: delete_folder_permanently(model.folder_id)
    CC->>AZ: delete folder and pictures related to the inspection

    IC-->>Client: deleted inspection database dict

```

#### label_information Cascade

```mermaid

---
title: FertiScan DB table label_information Cascade Sequence
---

sequenceDiagram
    participant DB as DB
    participant LabelInfo as Label_Information
    participant Specification as Specification
    participant SubLabel as Sub_Label
    participant Micronutrient as Micronutrient
    participant Guaranteed as Guaranteed
    participant Ingredient as Ingredient
    participant Metric as Metric
    participant OrganizationInfo as Organization_Information

    DB->>LabelInfo: DELETE

    DB->>Specification: cascade DELETE where label_id=deleted_label_info.id
    DB->>SubLabel: cascade DELETE where label_id=deleted_label_info.id
    DB->>Micronutrient: cascade DELETE where label_id=deleted_label_info.id
    DB->>Guaranteed: cascade DELETE where label_id=deleted_label_info.id
    DB->>Ingredient: cascade DELETE where label_id=deleted_label_info.id
    DB->>Metric: cascade DELETE where label_id=deleted_label_info.id

    DB->>OrganizationInfo: trigger try DELETE where id=deleted_label_info.company_info_id
    DB->>OrganizationInfo: trigger try DELETE where id=deleted_label_info.manufacturer_info_id

```

### Output JSON Format (`DBInspection`)

```json
DBInspection = {
  "id": "uuid-of-deleted-inspection",
  "verified": false,
  "upload_date": "timestamp-of-upload",
  "updated_at": "timestamp-of-last-update",
  "inspector_id": "uuid-of-inspector",
  "label_info_id": "uuid-of-deleted-label-info",
  "sample_id": "uuid-of-deleted-sample",
  "picture_set_id": "uuid-of-picture-set",
  "fertilizer_id": "uuid-of-fertilizer"
}
```
