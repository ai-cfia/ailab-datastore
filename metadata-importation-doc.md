
## Workflow: Metadata upload to Azure cloud 
``` mermaid  
            sequenceDiagram
                
                actor User
                actor Dev
                participant Azure Portal
                participant Azure Storage Explorer
                participant Azure Storage
                alt New User
                    User->>Dev: Storage subscription key request 
                    Note right of User: Email
                    Dev->>Azure Portal: Create Storage Blob
                    Azure Portal-)Azure Storage: Create()
                    Dev->>Azure Storage: Retrieve Key
                    Dev->>User: Send back subscription key
                    Note left of Dev: Email
                    User-)Azure Storage Explorer: SubscribeToStorage(key)
                end
                loop for each file
                    User-)Azure Storage Explorer: Upload(file)
                    Azure Storage Explorer-) Azure Storage: Save(file)
                end
                
``` 
## Sequence of Processing metadata for model

``` mermaid  
            sequenceDiagram

                actor Dev
                participant Azure Portal
                participant Notebook
                participant Azure Storage

                Dev->>Azure Storage: Check files structure
                alt Wrong structure
                    Dev->>Azure Portal: Create Alt. Azure Storage
                    Azure Portal-)Azure Storage: Create(Alt)
                    Dev-)Azure Storage: Copy files into Alt. Storage
                    Dev-)Azure Storage: Rework structure + Edit files/folders
                    Dev-)Azure Storage: Replace  Storage content with Alt. Storage content
                end
                Dev->>Azure Storage: Retrieve extraction code
                Dev->>Notebook: Edit parameters of extraction code commands
                
                Dev-) Notebook: Run extraction code
                Note left of Notebook: output source needs to be specified
                Notebook -) Azure Storage: Processing files into metadata
                Dev->> Azure Storage: Use files to train the model
``` 

### Legend
|Element|Description|
|-------|-----------|
| User | Anyone wanting to upload data. |
| Dev | AI-Lab Team. |
| Azure Portal | Interface managing Azure's services|
| Azure Storage | Interface storing data in the cloud. |
| Azure Storage Explorer | Application with GUI offering a user friendly access to a Azure Storage without granting full acess To the Azure Services. |
| NoteBook | Azure Service enabling to run code with Azure Storage structure|
| Files | All files shouldd follow the file structure present in the README.md |


## Observation

- The process of the user requesting the Subscription Access Key and obtaining it is not really efficient. The Dev hav to manually create Storage space, the key is sent by email and no information links the user to the storage space. It would be interesting to have a SOP (standard operating procedure)
  
- Alot of time can be spent on wrong file structure. We need to implement our file structure at the source (User). We also need more doc or SOP on how to deal with wrongfully structured file set.