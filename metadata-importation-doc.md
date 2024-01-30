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
                Azure Storage Explorer-) Azure Storage: Send(file)
            end
            
``` 