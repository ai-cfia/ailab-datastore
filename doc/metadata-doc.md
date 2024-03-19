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
    DB[(Database)] 
    blob[(Blob)]
    FE(Frontend)
    BE(Backend)
    file[/Folder/]
    classDef foo stroke:#f00

    file --> FE
    FE-->BE
    subgraph dbProcess [New Process]
    MD(MetaData):::hidden
    end
    BE -- TODO --- MD
    MD -- TODO --> DB
    BE ---> blob

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
This workflow showcase the 2 options that a user will face to upload data. The
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

 We are currently working on such process, which will be added to the  backend
 part of nachet once it is finished.

``` mermaid  
---
title: Nachet folder upload
---
flowchart LR;
    DB[(Database)] 
    blob[(Blob)]
    FE(Frontend)
    BE(Backend)
    file[/Folder/]
    classDef foo stroke:#f00

    file --> FE
    FE-->BE
    subgraph dbProcess [New Process]
    MD(MetaData):::hidden
    end
    BE -- TODO --- MD
    MD -- TODO --> DB
    BE ---> blob

    style dbProcess stroke:#f00,stroke-width:2px
``` 

## [Deployment mass import](deployment-mass-import.md)

## [Trusted User Upload](trusted-user-upload.md)

### Queries 
> :warning: This needs to be reworked. After discussions, we are not taking for
> this approach 

To communicate with the database and perform the request, we will need to build
a structure representing the schema.

```mermaid
  classDiagram
      class User {
          <<PK>> uuid id
          string email
          User(email) User
          getUser(id) User
          isUser(email) bool
          registerUser() uuid
          update()
          getAllSessions(id) List~Session~ 
          getAllPictures(id) List~Pictures~
      }

      class Session {
          <<PK>> uuid id
          json session
          <<FK>> uuid ownerID
          getSession(id) Session
          update()
          getSeed() Seed
          getNbPicture int
          getAllPictures(id) List~Pictures~       
      }

      class Picture {
          <<PK>> uuid id
          json picture
          <<FK>>
          <<FK>> uuid sessionID
          <<FK>> uuid parentID
          getPicture(id)
          update()
          getParent(id)
          getUrlSource() string
      }
      class PictureSeed {
        json pictureSeed
        getSeed() Seed
        getNbSeeds() int
        getZoom() float
        getUrlSas() string

      }
      class Seed{
        <<PK>> uuid id
        string name
        getAllPictures() List~Pictures~
        getAllSessions() List~Session~
      }

      class Search{
        uuid userID
        uuid sessionID
        uuid pictureID
        uuid seedID
        float zoom
        nbSeed int
        date startDate
        date endDate
      }
      Picture <|-- PictureSeed
```
### Requests (Backend)

Nachet backend will need the following requests to be able to handle the new
process.

*Note the name of the requests are subject to change and are currently meant to
be explicit about the purpose of the call*

#### User requests

| Name                | Parameters | Description |
| ------------------- | ----------- | ----------- |
| isUserRegister      | uuid | Is this user uuid stored in the database |
| getUserID           | user email | Retrieve the uuid of the current user |
| userRegister        | user email | This will serve as creating an instance of the user in the DB. I assume this will also be used as a way to create the containers if the user is an expert and has the responsibility to upload a data set for testing the models |

#### Seed requests

| Name                | Parameters | Description |
| ------------------- | ----------- | ----------- |
| getAllSeedsName     | None | Returns a list of all the seeds name |
| getSeedID           | seed name | Returns the ID (if there's an existing seed under the given name) |
| CreateSeed          | seed name | If the seed name is not already in the DB, we inserts the seed into it |

#### Upload requests

| Name                | Parameters | Description |
| ------------------- | ----------- | ----------- |
| New Session  | nbSeeds/Pic, Zoom, Seed info, PictureSet[(picture,link)] & User info | This request has the goal of inserting a session in the DB based on the User and the Session info. It also has the responsability of inserting all the pictures with their info into the DB. |
#### Validation Errors
> :warning: This is deprecated

Here's a list of the errors that can be returned turing the validation of the
upload 

| Name                | Description |
| ------------------- | ----------- |
| Wrong structure     | This type of error indicates the folder uploaded by the user doesn't follow the required structure. |
| Missing Session       | An Session is missing which means the whole folder of picture couldn't be processed. This might stop the upload process as a whole. |
| Session content       | A specific Session either has missing fields or unexpected values. |
| Unexpected file     | Based on the value given by the user within the session, there are more files present in the subfolder than expected. |
| Missing file        | Based on the value given by the user within the session, there are less picture files than expected. |
| `<picture.yml>` content | This error indicates there's an issue with one of the data fields in the file called 'picture.yml'. *(If the number of seeds and zoom field are not removed from picture.yaml)* |
### Files Structure

We aim to have a standard file structure to enable the use of a script to manage
the importation of files into the system. This statarized structure will allow
us to keep track  of the users uploads, the metadata feedback. By providing a
default structure for the files, we can run scripts through those files and
efficiently add/edit data within. Moreover, this approach will facilitate the
population of a database with the collected information enabling us to have a
better insight on our models actual performance. 

#### Folder

Lets begin by examinating the overall struture of the folder that a typical user
will be expected to upload. We require that users pack their entire upload into
a singular folder. Within the project folder, multiple subfolder will be present
to enforce an overall structure for the project, while allowing futur addition.
The project folder should adhere to the following structure:
```
project/
│
└───pictures/
│   └───session1/
│   |  │   1.tiff
│   |  │   2.tiff
│   |  |   ...
│   |  └─────────────
│   └───session2/
│      |   ...
│      └─────────────
└──────────────────
```
#### Files (.yaml)
##### [Session.yaml](session.yaml)

The session is an most important file. It will allow us to have all the
knowledge about the user and dataset uploaded.


##### [picture.yaml](picture.yaml)

Each picture should have their .yaml conterpart. This will allow us to run
scripts into the session folder and monitor each picture easily.

*Note: 'picture' in this exemple is replacing the picture number or name of the
.tiff file*
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
    string container  
  }
  sessions{
    uuid id PK
    json session
    uuid ownerID FK
  }
  pictures{
    uuid id PK
    json picture
    uuid sessionID FK
    uuid parent FK
  }
  feedbacks{
    int ID PK
    json feedback
  }
  seeds{
    uuid id PK
    string name
    json information
  }

  users ||--|{ sessions: uploads
  sessions ||--o{pictures: contains
  pictures ||--o{pictures: cropped
  pictures ||--||seeds: has

```
## Blob Storage

Finally the picture uploaded by the users will need to be stored in a blob
storage. Therefore we are using a Azure blob Storage account which currently
contains a list of containers either for the users upload or our Data scientists
training sets. The current structure needs to be revised and a standarized
structure needs to pe applied for the futur of Nachet. 

```
Storage account
│     
│
└───container 
│   └───folder/
│   |  │   1.tiff
│   |  │   2.tiff
│   |  |   ...
│   |  └─────────────
│   └───folder/
│      |   ...
│      └─────────────
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