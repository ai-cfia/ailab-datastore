import unittest
import uuid
import datastore.db.metadata.picture_set as picture_set_data
import datastore.db.metadata.picture as picture_data
import io
from PIL import Image
from datetime import date
import base64
import json

PIC_LINK = "test.com"

PIC_PATH = "img/test_image.tiff"


class test_picture_functions(unittest.TestCase):
    def setUp(self):
        self.image = Image.new("RGB", (1980, 1080), "blue")
        self.image_byte_array = io.BytesIO()
        self.image.save(self.image_byte_array, format="TIFF")
        self.pic_encoded = base64.b64encode(self.image_byte_array.getvalue()).decode(
            "utf8"
        )
        self.link = PIC_LINK
        self.nb_seeds = 1
        self.zoom = 1.0

    def test_build_picture(self):
        """
        This test checks if the build_picture function returns a valid JSON object
        """
        picture = picture_data.build_picture(
            self.pic_encoded, self.link, self.nb_seeds, self.zoom
        )
        properties = picture_data.get_image_properties(self.pic_encoded)
        data = json.loads(picture)
        mock_picture = {
            "user_data": {
                "description": "",
                "number_of_seeds": 1,
                "zoom": 1.0,
            },
            "metadata": {
                "upload_date": str(date.today()),
            },
            "image_data": {
                "format": properties[2],
                "height": properties[1],
                "width": properties[0],
                "resolution": "",
                "source": PIC_LINK,
            },
            "quality_check": {
                "image_checksum": "",
                "upload_check": True,
                "valid_data": True,
                "error_type": "",
                "quality_score": 0.0,
            },
        }
        for key, value in mock_picture.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    self.assertEqual(
                        data[key][sub_key],
                        sub_value,
                        f"{sub_key} should be {sub_value}",
                    )

    def test_get_image_properties(self):
        """
        This test checks if the get_image_properties function returns the correct image properties
        """
        properties = picture_data.get_image_properties(self.pic_encoded)
        mock_properties = (1980, 1080, "TIFF")
        self.assertEqual(
            properties, mock_properties, "Image properties should be 1980x1080, TIFF"
        )


class test_picture_set_functions(unittest.TestCase):
    def setUp(self):
        self.nb_pictures = 1
        self.user_id = uuid.uuid4()

    def test_build_picture_set(self):
        """
        This test checks if the build_picture_set function returns a valid JSON object
        """
        picture_set = picture_set_data.build_picture_set(self.user_id, self.nb_pictures)
        data = json.loads(picture_set)
        self.assertEqual(data["image_data_picture_set"]["number_of_images"], 1)
        self.assertEqual(data["audit_trail"]["upload_date"], str(date.today()))
        self.assertEqual(data["audit_trail"]["edited_by"], str(self.user_id))
        self.assertEqual(data["audit_trail"]["edit_date"], str(date.today()))
        self.assertEqual(data["audit_trail"]["change_log"], "picture_set created")
        self.assertEqual(data["audit_trail"]["access_log"], "picture_set accessed")
        self.assertEqual(data["audit_trail"]["privacy_flag"], False)


if __name__ == "__main__":
    unittest.main()
