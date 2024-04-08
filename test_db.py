"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""

import unittest
import uuid
from PIL import Image
import io
import base64
import datastore.db.queries.user as user
import datastore.db.queries.seed as seed
import datastore.db.queries.picture as picture
import datastore.db.metadata.picture_set as picture_set_data
import datastore.db.metadata.picture as picture_data
import datastore.db.metadata.validator as validator
import datastore.db.__init__ as db




# --------------------  USER FUNCTIONS --------------------
class test_user_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = self.con.cursor()
        self.email = "test@email.gouv.ca"

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

        user_id = user.register_user(self.cursor, self.email)

        self.assertTrue(validator.is_valid_uuid(user_id), "The user_id is not a valid UUID")

    def test_get_user_id(self):
        """
        This test checks if the get_user_id function returns the correct UUID
        """
        user_id = user.register_user(self.cursor, self.email)
        uuid = user.get_user_id(self.cursor, self.email)

        self.assertTrue(validator.is_valid_uuid(user_id), f"The user_id={user_id} is not a valid UUID")
        self.assertTrue(validator.is_valid_uuid(uuid), f"The returned UUID={uuid} is not a valid UUID")
        self.assertEqual(
            user_id, uuid, "The returned UUID is not the same as the registered UUID"
        )

    def test_get_user_id_not_registered(self):
        """
        This test checks if the get_user_id function raises an exception when the user is not registered
        """
        with self.assertRaises(user.UserNotFoundError):
            user.get_user_id(self.cursor, self.email)

    def test_register_user(self):
        """
        This test checks if the register_user function returns a valid UUID
        """
        user_id = user.register_user(self.cursor, self.email)

        self.assertTrue(validator.is_valid_uuid(user_id), "The user_id is not a valid UUID")



# --------------------  SEED FUNCTIONS --------------------


class test_seed_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)
        self.seed_name = "test"

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_get_all_seeds_names(self):
        """
        This test checks if the get_all_seeds_names function returns a list of seeds
        with at least the one seed we added
        """
        seed.new_seed(self.cursor, self.seed_name)
        seeds = seed.get_all_seeds_names(self.cursor)

        self.assertNotEqual(len(seeds), 0)
        self.assertIn((self.seed_name,), seeds)


    def test_get_seed_id(self):
        """
        This test checks if the get_seed_id function returns the correct UUID
        """
        seed_uuid = seed.new_seed(self.cursor, self.seed_name)
        fetch_id = seed.get_seed_id(self.cursor, self.seed_name)

        self.assertTrue(validator.is_valid_uuid(fetch_id))
        self.assertEqual(seed_uuid, fetch_id)
        
    def test_get_nonexistant_seed_id(self):
        """
        This test checks if the get_seed_id function raises an exception when the seed does not exist
        """
        with self.assertRaises(seed.SeedNotFoundError):
            seed.get_seed_id(self.cursor, "nonexistant_seed")


    def test_new_seed(self):
        """
        This test checks if the new_seed function returns a valid UUID
        """
        seed_id = seed.new_seed(self.cursor, self.seed_name)

        self.assertTrue(validator.is_valid_uuid(seed_id))



# --------------------  PICTURE FUNCTIONS --------------------
class test_pictures_functions(unittest.TestCase):
    def setUp(self):
        # prepare the connection and cursor
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)

        # prepare the seed
        self.seed_name = "test seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)

        # prepare the user
        self.user_id =user.register_user(self.cursor, "test@email")

        # prepare the picture_set and picture
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode(
            "utf8"
        )
        self.picture_set = picture_set_data.build_picture_set(self.user_id, 1)
        self.picture = picture_data.build_picture(
            self.pic_encoded, self.seed_name, 1, 1.0
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_picture_set(self):
        """
        This test checks if the new_picture_set function returns a valid UUID
        """
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        self.assertTrue(
            validator.is_valid_uuid(picture_set_id), "The picture_set_id is not a valid UUID"
        )


    def test_new_picture(self):
        """
        This test checks if the new_picture function returns a valid UUID
        """
        # prepare the picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )

        # create the new picture in the db
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, self.seed_id
        )

        self.assertTrue(validator.is_valid_uuid(picture_id), "The picture_id is not a valid UUID")

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
            self.cursor, self.picture_set, self.user_id
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
            self.cursor, self.picture_set, self.user_id
        )

        # prepare picture
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, self.seed_id
        )

        # test the function
        picture_data = picture.get_picture(self.cursor, picture_id)

        self.assertIsNotNone(picture_data, "The picture_data is None")
        self.assertNotEqual(len(picture_data), 0, "The picture_data is empty")



if __name__ == "__main__":
    unittest.main()
