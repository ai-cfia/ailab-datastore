import unittest
import datastore.bin.upload_picture_set as upload_picture_set
import datastore.db as db
import datastore.db.queries.user as user
import datastore.db.queries.seed as seed
import datastore.db.queries.picture as picture_query
import datastore.blob as blob
from PIL import Image
import base64
import io

class test_upload_picture_set(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db()
        self.cursor = db.cursor(self.con)
        db.create_search_path(self.con,self.cursor)
        
        self.email = "test@email"
        self.user_id = user.register_user(self.cursor, self.email)
    
        self.seed_name = "test_seed"
        self.seed_id = seed.new_seed(self.cursor, self.seed_name)

        self.image = Image.new('RGB', (1980, 1080),'blue')
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format='TIFF')
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode("utf8")
        
        self.pictures=[self.pic_encoded, self.pic_encoded]
        
        self.connection_string = "https://testfrancoiswerbrouck.blob.core.windows.net/test-import"
        user.link_container(self.cursor, self.user_id, self.connection_string)
        
    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)
        
    def test_upload_picture_set(self):
        """
        This test checks if the upload_picture_set function runs without issue
        """
        #TODO: check if the pictures are uploaded in the blob storage
        zoom_level = 1.0
        nb_seeds = 1
        picture_set_id=upload_picture_set.upload_picture_set(self.cursor, self.connection_string, self.pictures, self.user_id, self.seed_name, zoom_level, nb_seeds)
        self.assertTrue(True)
        self.assertTrue(picture_query.is_a_picture_set_id(self.cursor, picture_set_id))
        
        
    def test_non_existing_seed(self):
        """
        This test checks if the upload_picture_set function raises an exception when the seed does not exist
        """
        with self.assertRaises(seed.SeedNotFoundError):
            upload_picture_set.upload_picture_set(self.cursor, self.connection_string, self.pictures, self.user_id, "non_existing_seed", 1.0, 1)

    def test_non_existing_user(self):
        """
        This test checks if the upload_picture_set function raises an exception when the user does not exist
        """
        with self.assertRaises(user.UserNotFoundError):
            upload_picture_set.upload_picture_set(self.cursor, self.connection_string, self.pictures, 0, self.seed_name, 1.0, 1)

if __name__ == "__main__":
    unittest.main()