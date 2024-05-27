# Deployment mass import

## Contexte

We have a set of already existing picture in our Blob storage. We would like to
save the metadata of our files into the DB.

## Prerequisites

- The folder path must be accessible

- The Azure Storage container must be specified in the file

- The SeedId must be specified in the file

## Sequence of the uploading process

``` mermaid  
sequenceDiagram;
  actor dev
  box grey deployment-mass-import.py
  participant manualMetaDataImport
  participant buildIndex
  participant buildPicture
  end
  participant Database
  
  dev ->> manualMetaDataImport: gives Path
  manualMetaDataImport -) manualMsetaDataImport: set clientEmail=test@dev
  manualMetaDataImport -) Database: getUserID(email)
  Database -->> manualMetaDataImport: userID : UUID
  manualMetaDataImport ->> buildIndex: gives path,ClientID 
  buildIndex -) buildIndex: Create Index.json
  buildIndex -) buildIndex: Insert into Index.json user metadata
  buildIndex -) buildIndex: append Index.json with system metadata
  manualMetaDataImport -) Database: uploadIndexDB(path+/index.json",userID)
  Database -->> manualMetaDataImport: indexID : UUID
  manualMetaDataImport -) dev: input: nbSeeds/pic & zoom
  dev ->> manualMetaDataImport: nbSeeds/pic : int <br> zoom : float
  loop each picture in path
     manualMetaDataImport -) buildPicture: gives picture, nbSeeds, zoom, indexID, picName, userID
    buildPicture -) buildPicture: Create picName.json
    buildPicture -) buildPicture: Insert into picName.json user metadata
    buildPicture -) buildPicture: append picName.json with system metadata
     manualMetaDataImport -) Database: uploadPicture(picName.Json path, userID, indexID)
  end
  manualMetaDataImport -->> dev: Importation completed
```

``` mermaid

---
title: Nachet DB Structure
---
erDiagram
  picture_set{
    uuid id PK
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
  picture_seed{
    uuid id PK
    uuid picture_id FK
    uuid seed_id FK
    timestamp upload_date
  }
  seed{
    uuid id PK
    string name
    json information
    uuid object_type_id
    timestamp upload_date
  }
  container{
    uuid id PK
    uuid owner_id FK
    boolean public
    timestamp creation_date
    timestamp updated_at
  }

  picture_set ||--o{picture: contains
  picture ||--o{picture: cropped
  picture |o--o{picture_seed: has
  picture_seed }o--o| seed: has

  container ||--o{picture_set: contains

```