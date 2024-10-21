import json
import os
import unittest
import uuid

import psycopg
from dotenv import load_dotenv

from datastore.db.queries import user
from fertiscan.db.queries import (
    guaranteed,
    ingredient,
    inspection,
    label,
    metric,
    nutrients,
    specification,
    sub_label,
)
from fertiscan.db.queries.fertilizer import query_fertilizers
from fertiscan.db.queries.organization_information import read_organization_information

load_dotenv()

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

INPUT_JSON_PATH = "tests/fertiscan/inspection.json"


class TestDeleteInspectionFunction(unittest.TestCase):
    def setUp(self):
        # Set up database connection and cursor
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False
        self.cursor = self.conn.cursor()

        # Insert an inspector user into the users table and retrieve the inspector_id
        self.inspector_id = user.register_user(self.cursor, "inspector@example.com")

        # Load the JSON data for creating a new inspection
        with open(INPUT_JSON_PATH, "r") as file:
            create_input_json = json.load(file)

        create_input_json_str = json.dumps(create_input_json)

        # Create initial inspection data using the new_inspection function
        inspection_data = inspection.new_inspection_with_label_info(
            self.cursor, self.inspector_id, None, create_input_json_str
        )

        self.inspection_id = inspection_data["inspection_id"]
        self.label_info_id = inspection_data["product"]["label_id"]
        self.company_info_id = inspection_data["company"]["id"]
        self.manufacturer_info_id = inspection_data["manufacturer"]["id"]

        # Update the inspection to verified true
        inspection_data["verified"] = True
        inspection.update_inspection(
            self.cursor, self.inspection_id, self.inspector_id, inspection_data
        )

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_delete_inspection_success(self):
        # Call the delete_inspection function and get the returned inspection record
        deleted_inspection = inspection.delete_inspection(
            self.cursor, self.inspection_id, self.inspector_id
        )

        # Validate that the returned inspection record matches the expected data
        self.assertIsNotNone(
            deleted_inspection, "Deleted inspection should be returned."
        )
        self.assertEqual(
            deleted_inspection["id"],
            str(self.inspection_id),
            "Inspection ID should match.",
        )
        self.assertEqual(
            deleted_inspection["inspector_id"],
            str(self.inspector_id),
            "Inspector ID should match.",
        )

        # Verify that the inspection record was deleted
        self.assertIsNone(
            inspection.get_inspection(self.cursor, self.inspection_id),
            "Inspection should not be found after deletion.",
        )

        # Verify that the related sample was deleted
        # TODO: samples not yet handled

        # Verify that related fertilizer information was deleted
        fertilizers = query_fertilizers(
            cursor=self.cursor, latest_inspection_id=self.inspection_id
        )
        self.assertListEqual(fertilizers, [])

        # Verify that the label information was deleted
        self.assertIsNone(
            label.get_label_information(self.cursor, self.label_info_id),
            "Label information should not be found after deletion.",
        )

        # Verify that the related metrics were deleted
        self.assertListEqual(
            metric.query_metrics(self.cursor, label_id=self.label_info_id),
            [],
            "Metrics should not be found after deletion.",
        )

        # Verify that the related specifications were deleted
        self.assertDictEqual(
            specification.get_specification_json(self.cursor, self.label_info_id),
            {"specifications": {"fr": [], "en": []}},
            "Specifications should not be found after deletion.",
        )

        # Verify that the related sub-labels were deleted
        self.assertFalse(
            sub_label.has_sub_label(self.cursor, self.label_info_id),
            "Sub-labels should not be found after deletion.",
        )

        # Verify that the related micronutrients were deleted
        self.assertListEqual(
            nutrients.get_all_micronutrients(self.cursor, self.label_info_id),
            [],
            "Micronutrients should be deleted.",
        )

        # Verify that the related guaranteed records were deleted
        self.assertListEqual(
            guaranteed.query_guaranteed(self.cursor, label_id=self.label_info_id),
            [],
            "Guaranteed records should be deleted.",
        )

        # Verify that the related ingredients were deleted
        self.assertDictEqual(
            ingredient.get_ingredient_json(self.cursor, self.label_info_id),
            {"ingredients": {"en": [], "fr": []}},
            "Ingredients should not be found after deletion.",
        )

    def test_delete_inspection_with_linked_manufacturer(self):
        # Attempt to delete the inspection, which should raise a notice but not fail
        inspection.delete_inspection(self.cursor, self.inspection_id, self.inspector_id)

        # Ensure that the inspection and label were deleted
        self.assertIsNone(
            inspection.get_inspection(self.cursor, self.inspection_id),
            "Inspection should not be found after deletion.",
        )

        self.assertIsNone(
            label.get_label_information(self.cursor, self.label_info_id),
            "Label information should not be found after deletion.",
        )

        # Ensure that the manufacturer info was not deleted due to foreign key constraints
        self.assertIsNotNone(
            read_organization_information(self.cursor, self.manufacturer_info_id),
            "Manufacturer info should not be found after deletion.",
        )

        # Ensure that the company info related to the deleted inspection is deleted
        self.assertIsNone(
            read_organization_information(self.cursor, self.company_info_id),
            "Company info should not be found after deletion.",
        )

    def test_delete_inspection_unauthorized(self):
        # Generate a random UUID to simulate an unauthorized inspector
        unauthorized_inspector_id = str(uuid.uuid4())

        # Attempt to delete the inspection with a different inspector
        with self.assertRaises(inspection.InspectionDeleteError) as context:
            inspection.delete_inspection(
                self.cursor, self.inspection_id, unauthorized_inspector_id
            )

        # Check that the exception message indicates unauthorized access
        self.assertIn(
            f"Inspector {unauthorized_inspector_id} is not the creator of inspection {self.inspection_id}",
            str(context.exception),
        )


if __name__ == "__main__":
    unittest.main()
