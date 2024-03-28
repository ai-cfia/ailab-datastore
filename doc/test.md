# Test suites
- **Requirements**:
    - io
    - base64
    - PIL/Images
    - Nachet-metadata-format/metadata
        - ./picture_set
        - ./picture
## User

Prerequisites:
-  DB connection
- user email

### test_register_user
- Register the user
- Check if it returns a valid UUID

### test_is_user_registered
- Check user is not already registered
- Registers the user
- Check if the user has been created

### test_get_user_id
- Registers the user
- Check if the returns uuid is equal to the uuid found by email

## Seed
Prerequisites:
- DB connection
- seed name
### test_new_seed
- Creates a seed
- Check if the return value is a valid UUID

### test_get_all_seeds_names
- Creates a seed
- Check the return seed list is not empty
- Check if the new seeds is into the seed list

### test_get_seed_id
- Creates a seed
- Check if the returned UUID is equal to the UUID found by name

## Picture
Prerequisites:
- DB connection
- seed name
- Seed added in DB
- user email
- User added in DB
- User_uuid
- encoded picture file in a string format
- picture_set in a string format (metadata)
- picture in a string format (metadata)

### test_new_picture_set
- Creates a new picture_set entry
- Check the return value is a valid UUID

### test_new_picture_set
- Create a new picture_set entry
- Check if the returned value is a valid UUID

### test_new_picture
- Create a new picture_set entry
- Create a new picture entry
- Check if the returned value is a valid UUID

### test_get_picture_set
- Creates new picture_set entry and obtain its UUID
- Retrieve picture_set with it's UUID
- Check the returned metadata is not empty

### test_get_picture
- Creates new picture_set entry
- Creates new picture entry and obtain its UUID
- Retrieve the picture
- Check the returned metadata is not empty