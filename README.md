# ailab-datastore

## Overview

This monorepo contains the code for the AI Lab Datastore project. The project
aims to provide a data store with metadata for images and other data types
related to different projects. The datastore folder contains common code for
projects used by Nachet and Fertiscan projects.

## Nachet

Capturing attributes associated to the images is essential for proper model
training.

### image format

* .npy for nachet-batch
* .tiff for nachet-interactive

We define metadata related to the file.

### csv vs yaml vs json file

These are machine readable file formats that are popular:

* [csv](https://en.wikipedia.org/wiki/Comma-separated_values): often as an
  export of spreadsheet, each row is a single piece of data with columnar
* [json](https://www.json.org/): json is a standard for modern API dataformat,
  it defines a dictionary of keys and values with datatypes matching Javascript
  datatypes but now supported in most languages
* [yaml](https://yaml.org/): YAML is a human-friendly data serialization
  language for all programming languages

Although originally proposing JSON, we will use YAML instead as it is easier to
edit for users.

### on-disk directory/file structure

* name/
  * index.yaml
    * projectName:
    * submitterName:
    * acquisition setup information
      * categorization of the images
  * pictures/
    * session1/
      * index.yaml  
      * 1.tiff
      * 1.yaml
        * microscope metadata

### import utility

Python script that reads from on-disk directory structure and converts it to
database

* yaml metadata is inherited recursively and properties are inherited
* some of the properties can be directly read from the source image
* some draft information might be filled in by the model
* some of the metadata is filled in the user

### mapping to relational model nachet-db

(TODO: ERD (Entity-Relationship Diagram) here)

attributes are both from the yaml metadata and the images themselves metadata
and file (timestamps)

entities

* picture with metadata column
* project
* submitter
