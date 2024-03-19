# Trusted user upload process

## Contexte
We have a set of trusted user that needs to have an easy way of uploading large
sets of data to both our picture storage and database.

## Prerequisites
- The user must be signed in
- The user Azure Storage Container's have been created
- The user the pictures validity passes all checks
- The Seed is already registered in the Database

## Sequence of the uploading process

``` mermaid  
sequenceDiagram;
  actor User
  box grey Ai-Lab services
  participant Frontend
  participant Backend
  participant MetaData
  end
  box grey Storage services
  participant PostgreSQL Database
  participant Azure Storage
  end

    User ->> Frontend: Upload session request
    Frontend -->> User: Show session form
    User -) Frontend: Fill form :<br> Seed selection, nb Seeds/Pic, Zoom
    User -) Frontend: Upload: session folder
    Frontend ->> Backend: Upload from trusted user request: <br> Seed info, nbSeeds/Pic, Zoom ,<br> Session Folder & User
    Backend -) Backend: Validate folder & file structure

    loop for each picture
      Backend -) Azure Storage: Upload: picture
      Backend -) Azure Storage: Retrieve picture link
    end

    Backend ->> MetaData: New Session request: <br> nbSeeds/Pic, Zoom, Seed info<br> PictureSet[picture,link] & User
    MetaData ->>PostreSQL Database: Inserts Session
    MetaData ->>PostreSQL Database: Insert Pictures
    alt no error
    MetaData -->> Backend: Return upload successful
    Backend -->> Frontend: Return upload successful
    Frontend -->> User: Upload successful
    end

``` 
