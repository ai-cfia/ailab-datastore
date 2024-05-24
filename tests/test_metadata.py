import unittest
import uuid
import datastore.db.metadata.picture_set as picture_set_data
import datastore.db.metadata.picture as picture_data
import datastore.db.metadata.inference as inference
import datastore.db.metadata.machine_learning as ml_data
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

class test_inference_functions(unittest.TestCase):
    def setUp(self):
        self.filename="test.jpg"
        self.overlapping=False
        self.overlapping_indices=0
        self.total_boxes=1
        with open('tests/inference_example.json') as f:
            self.inference_exemple = json.load(f)
        self.filename=self.inference_exemple["filename"]
        self.labelOccurrence=self.inference_exemple["labelOccurrence"]
        self.total_boxes=self.inference_exemple["totalBoxes"]
        self.boxes=self.inference_exemple["boxes"]

    def test_build_inference_import(self):
        """
        This test checks if the build_inference_import function returns a valid JSON object
        """
        mock_inference = {
            "filename": self.filename,
            "labelOccurrence": self.labelOccurrence,
            "totalBoxes": self.total_boxes,
        }
        inference_tested = inference.build_inference_import(self.inference_exemple)
        inference_tested = json.loads(inference_tested)
        self.assertGreaterEqual(len(mock_inference), len(inference_tested), "The inference returned has too many keys")
        for key, value in mock_inference.items():
            self.assertTrue( key in inference_tested, f"{key} should be in the inference object")
            self.assertEqual(
                inference_tested[key],
                value,
                f"{key} should be {value}",
            )

    def test_build_object_import(self):
        """
        This test checks if the build_object_import function returns a valid JSON object
        """
        object =self.boxes[0]
        object_tested = inference.build_object_import(object)
        data = json.loads(object_tested)
        mock_object = {
            "box": {
                "topX": 0.0,
                "topY": 0.0,
                "bottomX": 0.0,
                "bottomY": 0.0
            },
            "color": "#ff0",
        }
        for key, value in mock_object.items():
            self.assertEqual(
                data[key],
                value,
                f"{key} should be {value}",
            )
            
class test_machine_learning_functions(unittest.TestCase):
    def setUp(self):
        with open("tests/ml_structure_exemple.json", "r") as file:
            self.ml_structure = json.load(file)
            self.model_name="that_model_name"
            self.model_id="48efe646-5210-4761-908e-a06f95f0c344"
            self.model_endpoint="https://that-model.inference.ml.com/score"
            self.task="classification"
            self.version=5
            self.data={
                "creation_date":"2024-01-01",
                "created_by":"Avery GoodDataScientist",
                "Accuracy": 0.6908
            }
            self.mock_model={
                "task": "classification",
                "endpoint": "https://that-model.inference.ml.com/score",
                "api_key": "SeCRetKeys",
                "content_type": "application/json",
                "deployment_platform": "azure",
                "endpoint_name": "that-model-endpoint",
                "model_name": "that_model_name",
                "model_id":"48efe646-5210-4761-908e-a06f95f0c344",
                "created_by": "Avery GoodDataScientist",
                "creation_date": "2024-01-01",
                "version": 5,
                "description": "Model Description",
                "job_name": "Job Name",
                "dataset_description": "Dataset Description",
                "Accuracy": 0.6908
            }
            self.pipeline_name="First Pipeline"
            self.pipeline_id="48efe646-5210-4761-908e-a06f95f0c344"
            self.pipeline_default=True
            self.model_ids=["that_model_name", "other_model_name"]
            self.mock_pipeline={
                "models": ["that_model_name", "other_model_name"],
                "pipeline_id": "48efe646-5210-4761-908e-a06f95f0c344",
                "pipeline_name": "First Pipeline",
                "created_by": "Avery GoodDataScientist",
                "creation_date": "2024-01-01",
                "version": 1,
                "description": "Pipeline Description",
                "job_name": "Job Name",
                "dataset_description": "Dataset Description",
                "Accuracy": 0.6908,
                "default": True
            }

    def test_build_model_import(self):
        """
        This test checks if the build_model_import function returns a valid JSON object
        """
        model = self.ml_structure["models"][0]
        model_import = ml_data.build_model_import(model)
        model_data = json.loads(model_import)
        self.assertLessEqual(len(model_data),len(self.mock_model), "The returned model data should have more key than expected")
        for key in model_data:
            self.assertEqual(self.mock_model[key], model_data[key], f"{key} should be {self.mock_model[key]}")

    def test_missing_key_build_model_import(self):
        """
        This test checks if the build_model_import function raises an error when a key is missing
        """
        model = self.ml_structure["models"][0]
        model.pop("api_key")
        self.assertRaises(ml_data.MissingKeyError, ml_data.build_model_import, model)

    def test_build_model_export(self):
        """
        This test checks if the build_model_export function returns a valid JSON object
        """
        model_export = ml_data.build_model_export(self.data,self.model_id,self.model_name,self.model_endpoint,self.task,self.version)
        self.assertLessEqual(len(model_export),len(self.mock_model), "The returned model data should have more key than expected")
        for key in model_export:
            self.assertTrue(key in self.mock_model, f"The key:{key} was not expected")
            self.assertEqual(self.mock_model[key], model_export[key], f"{key} should be {self.mock_model[key]}")

    def test_build_pipeline_import(self):
        """
        This test checks if the build_pipeline_import function returns a valid JSON object
        """
        pipeline = self.ml_structure["pipelines"][0]
        pipeline_import = ml_data.build_pipeline_import(pipeline)
        pipeline_data = json.loads(pipeline_import)
        self.assertLessEqual(len(pipeline_data),len(self.mock_pipeline), "The returned pipeline data should have more key than expected")
        for key in pipeline_data:
            self.assertEqual(pipeline_data[key], self.mock_pipeline[key], f"The pipeline data for the key:{key} should be {self.mock_pipeline[key]}")

    def test_missing_key_build_pipeline_import(self):
        """
        This test checks if the build_pipeline_import function raises an error when a key is missing
        """
        pipeline = self.ml_structure["pipelines"][0]
        pipeline.pop("models")
        self.assertRaises(ml_data.MissingKeyError, ml_data.build_pipeline_import, pipeline)

    def test_build_pipeline_export(self):
        """
        This test checks if the build_pipeline_export function returns a valid JSON object
        """
        pipeline_export = ml_data.build_pipeline_export(self.data,self.pipeline_name,self.pipeline_id,self.pipeline_default,self.model_ids)
        self.assertLessEqual(len(pipeline_export),len(self.mock_pipeline), "The returned pipeline data should have more key than expected")
        for key in pipeline_export:
            self.assertTrue(key in self.mock_pipeline, f"The key:{key} was not expected")
            self.assertEqual(self.mock_pipeline[key], pipeline_export[key], f"{key} should be {self.mock_pipeline[key]}")

if __name__ == "__main__":
    unittest.main()
