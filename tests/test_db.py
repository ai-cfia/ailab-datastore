"""
This is a test script for the database packages.
It tests the functions in the user, seed and picture modules.
"""

import base64
import io
import json
import os
import unittest
import uuid
from unittest.mock import MagicMock

from PIL import Image

import datastore.db.__init__ as db
from datastore import Role, Permission
from datastore.db.metadata import picture_set as picture_set_data
from datastore.db.metadata import validator
from datastore.db.queries import picture, user, group, container

DB_CONNECTION_STRING = os.environ.get("NACHET_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("NACHET_DB_URL_TESTING is not set")

DB_SCHEMA = os.environ.get("NACHET_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("NACHET_SCHEMA_TESTING is not set")


# --------------------  USER FUNCTIONS --------------------
class test_user_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.email = "test@email.gouv.ca"
        self.role_id = Role.INSPECTOR.value

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_is_user_registered(self):
        """
        This test checks if the is_user_registered function returns the correct value
        for a user that is not yet registered and one that is.
        """

        self.assertFalse(
            user.is_user_registered(self.cursor, self.email),
            "The user should not already be registered",
        )

        user_id = user.register_user(self.cursor, self.email, self.role_id)

        self.assertTrue(
            validator.is_valid_uuid(user_id), "The user_id is not a valid UUID"
        )

    def test_is_user_registered_error(self):
        """
        This test checks if the is_user_registered function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.is_user_registered(mock_cursor, self.email)

    def test_is_a_user_id(self):
        """
        This test checks if the is_a_user_id function returns the correct value
        for a user that is not yet registered and one that is.
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)

        self.assertTrue(
            user.is_a_user_id(self.cursor, user_id),
            "The user_id should be registered",
        )

        self.assertFalse(
            user.is_a_user_id(self.cursor, str(uuid.uuid4())),
            "The user_id should not be registered",
        )

    def test_is_a_user_id_error(self):
        """
        This test checks if the is_a_user_id function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.is_a_user_id(mock_cursor, user_id)

    def test_get_user_id(self):
        """
        This test checks if the get_user_id function returns the correct UUID
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)
        uuid = user.get_user_id(self.cursor, self.email)

        self.assertTrue(
            validator.is_valid_uuid(user_id),
            f"The user_id={user_id} is not a valid UUID",
        )
        self.assertTrue(
            validator.is_valid_uuid(uuid),
            f"The returned UUID={uuid} is not a valid UUID",
        )
        self.assertEqual(
            user_id, uuid, "The returned UUID is not the same as the registered UUID"
        )

    def test_get_user_id_not_registered(self):
        """
        This test checks if the get_user_id function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.get_user_id(self.cursor, self.email)

    def test_get_user_id_error(self):
        """
        This test checks if the get_user_id function raises an exception when the connection fails
        """
        user.register_user(self.cursor, self.email, self.role_id)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.get_user_id(mock_cursor, self.email)

    def test_register_user(self):
        """
        This test checks if the register_user function returns a valid UUID
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)

        self.assertTrue(
            validator.is_valid_uuid(user_id), "The user_id is not a valid UUID"
        )

    def test_register_user_error(self):
        """
        This test checks if the register_user function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(user.UserCreationError):
            user.register_user(mock_cursor, self.email, self.role_id)

    # def test_link_container(self):
    #     """
    #     This test checks if the link_container function links the container to the user
    #     """
    #     user_id = user.register_user(self.cursor, self.email,self.role_id)
    #     container_url = "https://container.com"
    #     user.link_container(self.cursor, user_id, container_url)
    #     fetched_url = user.get_container_url(self.cursor, user_id)
    #     self.assertEqual(container_url, fetched_url)

    def test_link_container_not_registered(self):
        """
        This test checks if the link_container function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.link_container(self.cursor, str(uuid.uuid4()), "https://container.com")

    def test_link_container_error(self):
        """
        This test checks if the link_container function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.link_container(mock_cursor, user_id, "https://container.com")

    # def test_get_container_url(self):
    #     """
    #     This test checks if the get_container_url function returns the correct container url
    #     """
    #     user_id = user.register_user(self.cursor, self.email,self.role_id)
    #     container_url = "https://container.com"
    #     user.link_container(self.cursor, user_id, container_url)

    #     fetched_url = user.get_container_url(self.cursor, user_id)

    #     self.assertEqual(container_url, fetched_url)

    def test_get_container_url_not_registered(self):
        """
        This test checks if the get_container_url function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.get_container_url(self.cursor, str(uuid.uuid4()))

    # def test_get_container_url_not_linked(self):
    #     """
    #     This test checks if the get_container_url function raises an exception when the container is not linked
    #     """
    #     user_id = user.register_user(self.cursor, self.email,self.role_id)
    #     with self.assertRaises(user.ContainerNotSetError):
    #         user.get_container_url(self.cursor, user_id)

    def test_get_container_url_error(self):
        """
        This test checks if the get_container_url function raises an exception when the connection fails
        """
        user_id = user.register_user(self.cursor, self.email, self.role_id)
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            user.get_container_url(mock_cursor, user_id)


class test_group_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.email = "test-gouv.ca"
        self.role_id = Role.TEAM_LEADER.value

        self.user_id = user.register_user(self.cursor, self.email, self.role_id)

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_create_group(self):
        """
        This test checks if the create_group function returns a valid UUID
        """
        group_name = "test_group"
        group_id = group.create_group(self.cursor, group_name, self.user_id)

        group_id_fetched = group.get_group_by_name(self.cursor, group_name)

        self.assertTrue(
            validator.is_valid_uuid(group_id), "The group_id is not a valid UUID"
        )
        self.assertEqual(
            str(group_id),
            str(group_id_fetched[0][0]),
            "The group_id is not the same as the fetched group_id",
        )

    def test_add_user_to_group(self):
        """
        This test checks if the add_member function adds a member to a group
        """
        group_name = "test_group"
        group_id = group.create_group(self.cursor, group_name, self.user_id)

        group.add_user_to_group(
            self.cursor, self.user_id, group_id, self.user_id, Permission.OWNER.value
        )

        self.assertTrue(group.is_user_in_group(self.cursor, self.user_id, group_id))

    def test_remove_user_from_group(self):
        """
        This test checks if the remove_member function removes a member from a group
        """
        group_name = "test_group"
        group_id = group.create_group(self.cursor, group_name, self.user_id)

        group.add_user_to_group(
            self.cursor, self.user_id, group_id, self.user_id, Permission.OWNER.value
        )

        self.assertTrue(group.is_user_in_group(self.cursor, self.user_id, group_id))

        group.remove_user_from_group(self.cursor, self.user_id, group_id)

        self.assertFalse(group.is_user_in_group(self.cursor, self.user_id, group_id))


# --------------------  PICTURE FUNCTIONS --------------------
class test_pictures_functions(unittest.TestCase):
    def setUp(self):
        # prepare the connection and cursor
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = db.cursor(self.con)
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        # prepare the user
        self.role_id = Role.INSPECTOR.value
        self.user_id = user.register_user(self.cursor, "test@email", self.role_id)

        # prepare the picture_set and picture
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode(
            "utf8"
        )
        self.nb_seed = 1
        self.picture_set = picture_set_data.build_picture_set_metadata(self.user_id, 1)
        picture_properties = picture_set_data.get_image_properties(
            pic_encoded=self.pic_encoded
        )
        self.image_link = "www.link.com"
        self.picture = picture_set_data.PictureMetadata(
            picture_id=None,
            link=self.image_link,
            upload_date=None,
            privacy_flag=False,
            description=None,
            name=None,
            nb_object=self.nb_seed,
            properties=picture_properties,
        ).model_dump_json()
        self.folder_name = "test_folder"

        self.container_id = container.create_container(
            self.cursor, "test_container", self.user_id, False, "test-user"
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_picture_set(self):
        """
        This test checks if the new_picture_set function returns a valid UUID
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            self.container_id,
            None,
        )

        self.assertTrue(
            validator.is_valid_uuid(picture_set_id),
            "The picture_set_id is not a valid UUID",
        )

        self.assertEqual(
            picture.get_picture_set_name(self.cursor, picture_set_id),
            self.folder_name,
            "The folder name is not test_folder",
        )

    def test_new_picture_set_error(self):
        """
        This test checks if the new_picture_set function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(picture.PictureSetCreationError):
            picture.new_picture_set(
                mock_cursor,
                self.picture_set,
                self.user_id,
                None,
                self.container_id,
                None,
            )

    def test_get_inexisting_picture_set(self):
        """
        This test checks if the get_picture_set function raises an exception when the picture_set does not exist
        """
        with self.assertRaises(picture.PictureSetNotFoundError):
            picture.get_picture_set(self.cursor, str(uuid.uuid4()))

    def test_get_picture_set(self):
        """
        This test checks if the get_picture_set function returns an object
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id, None, self.container_id, None
        )
        # test the function
        picture_set = picture.get_picture_set(self.cursor, picture_set_id)

        self.assertIsNotNone(picture_set, "The picture_set is None")
        self.assertNotEqual(len(picture_set), 0, "The picture_set is empty")

    def test_get_inexisting_picture(self):
        """
        This test checks if the get_picture function raises an exception when the picture does not exist
        """
        with self.assertRaises(picture.PictureNotFoundError):
            picture.get_picture(self.cursor, str(uuid.uuid4()))

    def test_get_picture(self):
        """
        This test checks if the get_picture function returns an object
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            container_id=self.container_id,
        )

        # prepare picture
        picture_id = picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )

        # test the function
        picture_data = picture.get_picture(self.cursor, picture_id)

        self.assertIsNotNone(picture_data, "The picture_data is None")
        self.assertNotEqual(len(picture_data), 0, "The picture_data is empty")

    def test_update_picture_metadata(self):
        """
        This test checks if the update_picture_metadata function updates the metadata
        """
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            container_id=self.container_id,
        )

        # prepare picture
        picture_id = picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )
        pic_properties = picture_set_data.get_image_properties(self.pic_encoded)
        new_picture = picture_set_data.PictureMetadata(
            name="test", link="test.com", nb_object=3, properties=pic_properties
        ).model_dump_json()
        picture_metadata = picture.get_picture(self.cursor, picture_id)
        # update the metadata
        picture.update_picture_metadata(self.cursor, picture_id, new_picture, 6)
        new_picture = json.loads(new_picture)
        # get the updated metadata
        new_picture_metadata = picture.get_picture(self.cursor, picture_id)
        self.assertNotEqual(
            new_picture["name"],
            picture_metadata["name"]
        )
        self.assertEqual(
            new_picture_metadata["name"],
            new_picture["name"],
            "The metadata was not updated correctly",
        )

    def test_update_picture_metadata_error(self):
        """
        This test checks if the update_picture_metadata function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Connection error")
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(picture.PictureUpdateError):
            picture.update_picture_metadata(
                mock_cursor, uuid.uuid4(), self.picture, self.nb_seed
            )

    def test_is_a_picture_set_id(self):
        """
        This test checks if the is_a_picture_set_id function returns the correct value
        for a picture_set that is not yet registered and one that is.
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            container_id=self.container_id,
        )

        self.assertTrue(
            picture.is_a_picture_set_id(self.cursor, picture_set_id),
            "The picture_set_id should be registered",
        )

        self.assertFalse(
            picture.is_a_picture_set_id(self.cursor, str(uuid.uuid4())),
            "The picture_set_id should not be registered",
        )

    def test_is_a_picture_set_id_error(self):
        """
        This test checks if the is_a_picture_set_id function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            picture.is_a_picture_set_id(mock_cursor, uuid.uuid4())

    def test_get_picture_set_name(self):
        """
        This test checks if the get_picture_set_name function returns the correct name of the picture_set
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            self.container_id,
            None,
        )
        name = picture.get_picture_set_name(self.cursor, picture_set_id)
        self.assertEqual(name, self.folder_name, "The folder name is not test_folder")

    def test_get_picture_set_name_error(self):
        """
        This test checks if the get_picture_set_name function raises an exception when the connection fails
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")
        with self.assertRaises(Exception):
            picture.get_picture_set_name(mock_cursor, picture_set_id)

    def test_get_user_picture_sets(self):
        """
        This test checks if the get_user_picture_sets function returns all picture_sets of the user
        """
        picture_set_id1 = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )
        picture_set_id2 = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name + "2",
            container_id=self.container_id,
            parent_id=None,
        )

        picture_sets = picture.get_user_picture_sets(self.cursor, self.user_id)
        self.assertEqual(
            len(picture_sets), 2, "The number of picture_sets is not the expected one"
        )
        self.assertIn(
            (picture_set_id1, self.folder_name),
            picture_sets,
            "The first picture_set is not in the list of picture_sets",
        )
        self.assertIn(
            (picture_set_id2, self.folder_name + "2"),
            picture_sets,
            "The second picture_set is not in the list of picture_sets",
        )

    def test_get_user_picture_sets_error(self):
        """
        This test checks if the get_user_picture_sets function raises an exception when the connection fails
        """
        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("Connection error")

        with self.assertRaises(picture.GetPictureSetError):
            picture.get_user_picture_sets(mock_cursor, self.user_id)

    def test_get_user_picture_sets_user_error(self):
        """
        This test checks if the get_user_picture_sets function raises an exception when the user do not exist
        """
        with self.assertRaises(picture.GetPictureSetError):
            picture.get_user_picture_sets(self.cursor, str(uuid.uuid4()))

    def test_count_pictures(self):
        """
        This test checks if the count_pictures function returns the correct number of pictures
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )
        picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )

        count = picture.count_pictures(self.cursor, picture_set_id)
        self.assertEqual(count, 2, "The number of pictures is not the expected one")

    def test_count_pictures_error(self):
        """
        This test checks if the count_pictures function raises an exception when the connection fails
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )

        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = Exception("Connection error")

        with self.assertRaises(picture.PictureSetNotFoundError):
            picture.count_pictures(mock_cursor, picture_set_id)

    def test_get_picture_set_pictures(self):
        """
        This test checks if the get_picture_set_pictures function returns the correct pictures
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        self.assertEqual(
            len(picture.get_picture_set_pictures(self.cursor, picture_set_id)),
            0,
            "The number of pictures is not the expected one",
        )

        pictureId1 = picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )
        pictureId2 = picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )

        pictures = picture.get_picture_set_pictures(self.cursor, picture_set_id)
        self.assertEqual(
            len(pictures), 2, "The number of pictures is not the expected one"
        )
        self.assertEqual(
            pictures[0][0], pictureId1, "The first picture is not the expected one"
        )
        self.assertEqual(
            pictures[1][0], pictureId2, "The second picture is not the expected one"
        )

    def test_get_picture_set_pictures_error(self):
        """
        This test checks if the get_picture_set_pictures function raises an error if connection fails
        """
        picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, picture_set_id, self.nb_seed
        )

        mock_cursor = MagicMock()
        mock_cursor.fetchall.side_effect = Exception("Connection error")

        with self.assertRaises(Exception):
            picture.get_picture_set_pictures(mock_cursor, picture_set_id)

    def test_change_picture_set_id(self):
        old_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, old_picture_set_id, self.nb_seed
        )
        picture.new_picture_unknown(
            self.cursor, self.picture, old_picture_set_id, self.nb_seed
        )

        new_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )
        old_picture_set = picture.get_picture_set_pictures(
            self.cursor, old_picture_set_id
        )
        self.assertEqual(
            len(old_picture_set), 2, "The number of pictures is not the expected one"
        )
        new_picture_set = picture.get_picture_set_pictures(
            self.cursor, new_picture_set_id
        )
        self.assertEqual(
            len(new_picture_set), 0, "The number of pictures is not the expected one"
        )

        picture.change_picture_set_id(
            self.cursor,
            str(self.user_id),
            str(old_picture_set_id),
            str(new_picture_set_id),
        )

        old_picture_set = picture.get_picture_set_pictures(
            self.cursor, old_picture_set_id
        )
        self.assertEqual(
            len(old_picture_set), 0, "The number of pictures is not the expected one"
        )
        new_picture_set = picture.get_picture_set_pictures(
            self.cursor, new_picture_set_id
        )
        self.assertEqual(
            len(new_picture_set), 2, "The number of pictures is not the expected one"
        )

    def test_change_picture_set_id_error(self):
        old_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, old_picture_set_id, self.nb_seed
        )

        new_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Connection error")

        with self.assertRaises(picture.PictureUpdateError):
            picture.change_picture_set_id(
                mock_cursor, self.user_id, old_picture_set_id, new_picture_set_id
            )

    def test_change_picture_set_id_user_error(self):
        old_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        picture.new_picture_unknown(
            self.cursor, self.picture, old_picture_set_id, self.nb_seed
        )

        new_picture_set_id = picture.new_picture_set(
            self.cursor,
            self.picture_set,
            self.user_id,
            self.folder_name,
            container_id=self.container_id,
            parent_id=None,
        )

        with self.assertRaises(picture.PictureUpdateError):
            picture.change_picture_set_id(
                self.cursor, str(uuid.uuid4()), old_picture_set_id, new_picture_set_id
            )


if __name__ == "__main__":
    unittest.main()
