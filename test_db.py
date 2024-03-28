import unittest
import uuid
from PIL import Image
import io
import base64
import db.queries.user as user
import db.queries.seed as seed
import db.queries.picture as picture
import metadata.picture_set as picture_set_data
import metadata.picture as picture_data
import db.queries.__init__ as queries
import db.__init__ as db

"""
This is a test script for the database packages. 
It tests the functions in the user, seed and picture modules.
"""


def is_valid_uuid(val):
    """
    This validates if a given string is a UUID
    """
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


# --------------------  USER FUNCTIONS --------------------
class test_user_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = self.con.cursor()
        self.email = "test@email.gouv.ca"

    def tearDown(self):
        db.end_query(self.con, self.cursor)

    def test_is_user_registered(self):
        """
        This test checks if the is_user_registered function returns the correct value
        for a user that is registered and one that is not.
        """
        # self.cursor.fetchone.return_value = None
        self.assertFalse(user.is_user_registered(self.cursor, self.email))

        user.register_user(self.cursor, self.email)

        self.assertTrue(user.is_user_registered(self.cursor, self.email))
        self.con.rollback()

    def test_get_user_id(self):
        user.register_user(self.cursor, self.email)
        uuid = user.get_user_id(self.cursor, self.email)
        self.assertTrue(is_valid_uuid(uuid))
        self.con.rollback()

    def test_register_user(self):
        user.register_user(self.cursor, self.email)
        self.assertTrue(user.is_user_registered(self.cursor, self.email))
        self.con.rollback()


# --------------------  SEED FUNCTIONS --------------------


class test_seed_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = self.con.cursor()
        self.seed_name = "test"

    def tearDown(self):
        db.end_query(self.con, self.cursor)

    def test_get_all_seeds_names(self):
        seeds = seed.get_all_seeds_names(self.cursor)
        self.assertNotEqual(len(seeds), 0)
        self.con.rollback()

    def test_get_seed_id(self):
        seed.new_seed(self.cursor, self.seed_name)
        seed_id = seed.get_seed_id(self.cursor, self.seed_name)
        self.assertTrue(is_valid_uuid(seed_id))
        self.con.rollback()

    def test_new_seed(self):
        seed.new_seed(self.cursor, self.seed_name)
        seeds = seed.get_all_seeds_names(self.cursor)
        self.assertIn((self.seed_name,), seeds)
        self.con.rollback()


# --------------------  PICTURE FUNCTIONS --------------------
class test_pictures_functions(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = self.con.cursor()
        # prepare the seed
        self.seed_name = "test seed"
        # prepare the user
        user.register_user(self.cursor, "test@email")
        self.user_id = user.get_user_id(self.cursor, "test@email")
        # prepare the picture_set and picture
        self.image = Image.new('RGB', (1980, 1080),'blue')
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format='TIFF')
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode("utf8")
        self.picture_set = picture_set_data.build_picture_set(self.user_id, 1)
        self.picture = picture_data.build_picture(self.pic_encoded, self.seed_name, 1, 1.0)

    def tearDown(self):
        db.end_query(self.con, self.cursor)

    def test_new_picture_set(self):
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )
        self.assertTrue(is_valid_uuid(picture_set_id))
        self.con.rollback()

    def test_new_picture(self):
        seed.new_seed(self.cursor, self.seed_name)
        seed_id = seed.get_seed_id(self.cursor, self.seed_name)
        # prepare the picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )
        # create the new picture in the db
        picture_id = picture.new_picture(
            self.cursor, self.picture, picture_set_id, seed_id
        )
        self.assertTrue(is_valid_uuid(picture_id))
        self.con.rollback()

    def test_get_picture_set(self):
        # prepare picture_set
        picture_set_id = picture.new_picture_set(
            self.cursor, self.picture_set, self.user_id
        )
        # test the function
        picture_set = picture.get_picture_set(self.cursor, picture_set_id)
        self.assertIsNotNone(picture_set)
        self.assertNotEqual(len(picture_set), 0)
        self.con.rollback()


if __name__ == "__main__":
    unittest.main()
