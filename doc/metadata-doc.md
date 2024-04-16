# Metadata importation

## Context

The following documentation provide an overview of the metadata importation
process for the Nachet pipeline. We outline each steps of the workflow,
illustrating how data progresses until it becomes usable by our models.
Additionally, the upcoming process are showcased with the expected files
structure. 

``` mermaid

---
title: Nachet data upload
---
flowchart LR;
    FE(Frontend)
    BE(Backend)
    file[/Folder/]
    classDef foo stroke:#f00

    file --> FE
    FE-->BE
    subgraph dbProcess [New Process]
    MD(Datastore)
    DB[(Database)] 
    blob[(Blob)]
    end
    BE -- TODO --- MD
    MD --> DB
    MD --> blob

```

As shown above, we are currently working on a process to validate the files
uploaded to the cloud. However, since Nachet is still a work in progress, here's
the current workflow for our user to upload their images for the models.

## Workflow: Metadata upload to Azure cloud (Currently)

``` mermaid  

sequenceDiagram;
  actor User
  actor DataScientist
  participant Azure Portal
  participant Azure Storage Explorer
  
  alt New User
      User->>DataScientist: Storage subscription key request 
      Note right of User: Email
      DataScientist->>Azure Portal: Create Storage Blob
      create participant Azure Storage
      Azure Portal-)Azure Storage: Create()
      DataScientist->>Azure Storage: Retrieve Key
      DataScientist->>User: Send back subscription key
      Note left of DataScientist: Email
      User-)Azure Storage Explorer: SubscribeToStorage(key)
  end
  loop for each project Folder
      User-)Azure Storage Explorer: Upload(Folder)
      Azure Storage Explorer-) Azure Storage: Save(folder)
  end
  
```

This workflow showcase the two options that a user will face to upload data. The
first one being he's a first time user. Therefore, the current process for a
first time user is to contact the AI-Lab team and subscribe to the Blob storage
with a given subscription key.

## Sequence of processing metadata for model (Currently)

``` mermaid

sequenceDiagram;
  actor DataScientist
  participant Azure Portal
  participant Notebook
  participant Azure Storage
  DataScientist->>Azure Storage: Check files structure
  alt Wrong structure
      DataScientist->>Azure Portal: Create Alt. Azure Storage
      Azure Portal-)Azure Storage: Create(Alt)
      create participant Azure Storage Alt
      DataScientist-)Azure Storage Alt: Copy files
      DataScientist-)Azure Storage Alt: Rework structure + Edit files/folders
      DataScientist-)Azure Storage Alt: Replace Storage content with Alt. Storage content
      destroy Azure Storage Alt 
      Azure Storage Alt -) Azure Storage: Export files
  end
  DataScientist->>Azure Storage: Retrieve extraction code
  DataScientist->>Notebook: Edit parameters of extraction code commands
  
  DataScientist-) Notebook: Run extraction code
  Note left of Notebook: output source needs to be specified
  Notebook -) Azure Storage: Processing files into metadata
  DataScientist->> Azure Storage: Use files to train the model

```

This sequence illustrate the manual task done by our team to maintain the
storage of user's data.

### Legend

| Element                | Description                                                                                                                |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| User                   | Anyone wanting to upload data.                                                                                             |
| DataScientist          | Member of the AI-Lab Team.                                                                                                 |
| Azure Portal           | Interface managing Azure's services                                                                                        |
| Azure Storage          | Interface storing data in the cloud.                                                                                       |
| Azure Storage Explorer | Application with GUI offering a user friendly access to a Azure Storage without granting full acess To the Azure Services. |
| NoteBook               | Azure Service enabling to run code with Azure Storage structure                                                            |
| Folder                 | All project folder should follow the files structure presented bellow.                                                     |

## Development

As explained in the context we aim to implement an architecture for user
uploads. This approach would allow to us add a data structure validator using
[Pydantic](https://docs.pydantic.dev/latest/). By implementing a validator, we
will be able to remove all manual metadata maintenance. Once the validation
process is complete, the upload process will come into play, enabling the
distribution of the files between the BLOB storage and a PostgreSQL database. 

 We are currently working on such process, which will be handled by the  backend
 part of nachet once it is finished.

``` mermaid

---
title: Nachet folder upload
---
flowchart LR;
    FE(Frontend)
    BE(Backend)
    file[/Folder/]
    classDef foo stroke:#f00

    file --> FE
    FE-->BE
    subgraph dbProcess [New Process]
    MD(Datastore)
    DB[(Database)]
    blob[(Blob)]
    end
    BE -- TODO --- MD
    MD --> DB
    MD --> blob

    style dbProcess stroke:#f00,stroke-width:2px

```

## Finished processes:

### [Deployment mass import](deployment-mass-import.md)

### [Trusted User Upload](trusted-user-upload.md)

## Database

We plan on storing the metadata of the user's files in a postgreSQL Database.
The database should have the following structure: 

``` mermaid

---
title: Nachet DB Structure
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
    json picture_set
    uuid owner_id FK
    timestamp upload_date
  }
  pictures{
    uuid id PK
    json picture
    uuid picture_set_id FK
    uuid parent FK
  }
  picture_seed{
    uuid id PK
    uuid picture_id FK
    uuid seed_id FK
    timestamp upload_date
  }
  seeds{
    uuid id PK
    string name
    json information
    timestamp upload_date
  }

  users ||--|{ picture_set: uploads
  picture_set ||--o{pictures: contains
  pictures ||--o{pictures: cropped
  pictures |o--o{picture_seed: has
  picture_seed }o--o| seeds: has

```

## Blob Storage

Finally the picture uploaded by the users will need to be stored in a blob
storage. Therefore we are using a Azure blob Storage account which currently
contains a list of containers used either for the users upload or our Data
scientists training sets. The current structure uses a tier in the container's name. 

```
Storage account:
│     
│  Container:
└───user-8367cc4e-1b61-42c2-a061-ca8662aeac37
|   | Folder:
│   └───fb20146f-df2f-403f-a56f-f02a48092167/
│   |  │   f9b0ef75-6276-4ffc-a71c-975bc842063c.tiff
│   |  │   68e16a78-24bd-4b8c-91b6-75e6b84c40d8.tiff
│   |  |   ...
│   |  └─────────────
|   | Folder:
│   └───a6bc9da0-b1d0-42e5-8c41-696b86271d55/
│      |   ...
│      └─────────────
|   Container:
└───user-...
|   └── ...
└──────────────────
```

## Consequences

  Implementing this structure and introducing the new backend features in Nachet
  will result in the following impact:
- **Automation of file structure maintenance:** This process will autonomously
  manage the file structure, eliminating the need for manual maintenance and
  reducing workload for the AI-Lab team.

- **Streamlined subscription key management:** The new feature will eliminate
  the need for email communication between users and the AI-Lab team for
  subscription keys. The system may automatically create and connect to the
  appropriate BLOB storage without user intervention. Consequently, manual
  creation of storage by the AI-Lab team will be unnecessary, and all keys will
  be securely stored in the database.

- **Enhanced security:** The removal of email exchanges between users and the
  development team represents a substantial improvement in security protocols.

- **Improved model tracking and training:** Storing user metadata will enable
  more effective tracking of model performance and facilitate better training
  strategies.

- **Automated metadata enrichment:** The process will enable the automatic
  addition of additional information to metadata, enhancing the depth of
  insights available.
  
Overall, this new feature will empowers the AI-Lab team to have better control
over the content fed to the models and ensures improved tool maintenance
capabilities in the future.