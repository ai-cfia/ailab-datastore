import unittest
import uuid
import metadata.picture_set as picture_set_data
import metadata.picture as picture_data
import metadata.validator as validator
import io
from PIL import Image
from datetime import date
import base64
import json
from pydantic import BaseModel

PIC_LINK = 'test.com'

PIC_PATH = 'test_image.tiff'

class test_picture_functions(unittest.TestCase):
    def setUp(self):
        self.image = Image.new('RGB', (1980, 1080),'blue')
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format='TIFF')
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode("utf8")
        self.link = PIC_LINK
        self.nb_seeds = 1
        self.zoom = 1.0
    
    def test_build_picture(self):
        picture = picture_data.build_picture(self.pic_encoded, self.link, self.nb_seeds, self.zoom)
        properties = picture_data.get_image_properties(self.pic_encoded)
        data = json.loads(picture)
        self.assertEqual(data["user_data"]["description"], "")
        self.assertEqual(data["user_data"]["number_of_seeds"], 1)
        self.assertEqual(data["user_data"]["zoom"], 1.0)
        self.assertEqual(data["metadata"]["upload_date"], str(date.today()))
        self.assertEqual(data["image_data"]["format"], properties[2])
        self.assertEqual(data["image_data"]["height"], properties[1])
        self.assertEqual(data["image_data"]["width"], properties[0])
        self.assertEqual(data["image_data"]["resolution"], "")
        self.assertEqual(data["image_data"]["source"], PIC_LINK)
        self.assertEqual(data["quality_check"]["image_checksum"], "")
        self.assertEqual(data["quality_check"]["uploadCheck"], True)
        self.assertEqual(data["quality_check"]["validData"], True)
        self.assertEqual(data["quality_check"]["errorType"], "")
        self.assertEqual(data["quality_check"]["dataQualityScore"], 0.0)
        
    def test_get_image_properties(self):
        properties = picture_data.get_image_properties(self.pic_encoded)
        self.assertEqual(properties[0], 1980)
        self.assertEqual(properties[1], 1080)
        self.assertEqual(properties[2], "TIFF")

class test_picture_set_functions(unittest.TestCase):
    def setUp(self):   
        self.nb_pictures = 1
        self.user_id = uuid.uuid4()
        
    def test_build_picture_set(self):
        picture_set = picture_set_data.build_picture_set(self.user_id, self.nb_pictures)
        data = json.loads(picture_set)
        self.assertEqual(data["image_data"]["numberOfImages"], 1)
        self.assertEqual(data["audit_trail"]["upload_date"], str(date.today()))
        self.assertEqual(data["audit_trail"]["edited_by"], str(self.user_id))
        self.assertEqual(data["audit_trail"]["edit_date"], str(date.today()))
        self.assertEqual(data["audit_trail"]["change_log"], "picture_set created")
        self.assertEqual(data["audit_trail"]["access_log"], "picture_set accessed")
        self.assertEqual(data["audit_trail"]["privacy_flag"], False)
        
if __name__ == "__main__":
    unittest.main()
