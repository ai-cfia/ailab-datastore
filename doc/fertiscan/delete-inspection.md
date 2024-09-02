# Deleting an Inspection Record

## Sequence Diagram of the DB function

**Preconditions:**

- The inspection record must exist prior to the update.

**Postconditions:**

- The inspection record is deleted along with the underlying table records.

```mermaid
sequenceDiagram
    participant Client
    participant DB as DB
    participant Inspection as Inspection
    participant Sample as Sample
    participant LabelInfo as Label_Information

    Client->>DB: delete_inspection(inspection_id, inspector_id)

    DB->>Inspection: validate_inspection_ownership(inspection_id, inspector_id)
    DB->>Inspection: DELETE where id=inspection_id
    Inspection-->>DB: inspection_record

    DB->>Sample: trigger DELETE where id=deleted_inspection.sample_id

    DB->>LabelInfo: trigger DELETE where id=deleted_inspection.label_info_id

    DB-->>Client: inspection_record

```

```mermaid
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

```mermaid
sequenceDiagram
    participant DB as DB
    participant OrganizationInfo as Organization_Information
    participant Location as Location

    DB->>OrganizationInfo: DELETE
    OrganizationInfo->>Location: trigger DELETE where id=deleted_org_info.location_id

```

### Output JSON Format

```json
{
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

## Sequence diagram of fertiscan datastore python function

```mermaid
sequenceDiagram
    participant Client
    participant Datastore as Fertiscan Datastore
    participant DB as Database
    participant BlobStorage as Blob Storage

    Client->>Datastore: delete_inspection(inspection_id, user_id, container_client)

    Datastore->>DB: delete_inspection(cursor, inspection_id, user_id)
    DB-->>Datastore: deleted_inspection_record

    Datastore->>BlobStorage: delete_picture_set_permanently(cursor, user_id, deleted_inspection_record.picture_set_id, container_client)
    BlobStorage-->>Datastore: picture_set_deleted_confirmation

    Datastore-->>Client: deleted_inspection_record
```
