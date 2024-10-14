import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

import fertiscan.db.queries.label as label
import fertiscan.db.queries.sub_label as sub_label
from fertiscan.db.models import Inspection, Location, SubLabel
from fertiscan.db.queries import organization
from fertiscan.db.queries.location import create_location

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


TEST_INPUT_JSON_PATH = "tests/fertiscan/inspection_export.json"


class TestUpdateSubLabelsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Load and validate the inspection data from the JSON file using the Inspection model
        with open(TEST_INPUT_JSON_PATH) as f:
            inspection_data = json.load(f)
        inspection_data = Inspection.model_validate(inspection_data)

        # Set up test data for sub labels using the SubLabel Pydantic model
        self.sample_sub_labels = {
            "instructions": inspection_data.instructions.model_dump(),
            "cautions": inspection_data.cautions.model_dump(),
        }

        # Calculate the number of sub-labels for the initial insertion
        self.nb_sub_labels = len(inspection_data.instructions.en) + len(
            inspection_data.cautions.en
        )

        # Set up updated sub labels using the SubLabel Pydantic model
        self.updated_sub_labels = {
            "instructions": SubLabel(
                en=[
                    "1. Dissolve 50g in 10L of water.",
                    "2. Apply every 2 weeks.",
                    "3. Store in a cool place.",
                    "4. Test instruction.",
                    "5. Test instruction.",
                ],
                fr=[
                    "1. Dissoudre 50g dans 10L d'eau.",
                    "2. Appliquer toutes les 2 semaines.",
                    "3. Conserver dans un endroit frais.",
                    "4. Test instruction.",
                    "5. Test instruction.",
                ],
            ).model_dump(),
            "cautions": SubLabel(
                en=[
                    "Keep out of reach of children.",
                    "Avoid contact with skin and eyes.",
                    "If in eyes, rinse immediately.",
                    "Limited warranty of 1 year.",
                    "Test caution.",
                ],
                fr=[
                    "Tenir hors de portée des enfants.",
                    "Éviter le contact avec la peau et les yeux.",
                    "En cas de contact avec les yeux, rincer immédiatement.",
                    "Garantie limitée de 1 an.",
                    "Test caution.",
                ],
            ).model_dump(),
        }
        self.nb_updated = 10

        # Set up organization information
        self.province_name = "a-test-province"
        self.region_name = "test-region"
        self.name = "test-organization"
        self.website = "www.test.com"
        self.phone = "123456789"
        self.location_name = "test-location"
        self.location_address = "test-address"
        self.province_id = organization.new_province(self.cursor, self.province_name)
        self.region_id = organization.new_region(
            self.cursor, self.region_name, self.province_id
        )
        self.location = create_location(
            self.cursor, self.location_name, self.location_address, self.region_id
        )
        self.location = Location.model_validate(self.location)
        self.company_info_id = organization.new_organization_info(
            self.cursor,
            self.name,
            self.website,
            self.phone,
            self.location.id,
        )

        self.label_id = label.new_label_information(
            self.cursor,
            "test-label",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            self.company_info_id,
            self.company_info_id,
        )

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_update_sub_labels(self):
        # Insert initial sub labels
        # TODO: write missing sub_label functions
        self.cursor.execute(
            "SELECT update_sub_labels(%s, %s);",
            (self.label_id, json.dumps(self.sample_sub_labels)),
        )

        saved_sub_labels = sub_label.get_sub_label_json(self.cursor, self.label_id)
        for k, v in saved_sub_labels.items():
            self.assertDictEqual(v, self.sample_sub_labels[k])
            for lang, arr in v.items():
                self.assertCountEqual(arr, self.sample_sub_labels[k][lang])

        # Update sub labels
        # TODO: write missing sub_label functions
        self.cursor.execute(
            "SELECT update_sub_labels(%s, %s);",
            (self.label_id, json.dumps(self.updated_sub_labels)),
        )

        # Verify that the data is correctly updated
        updated_sub_labels = sub_label.get_sub_label_json(self.cursor, self.label_id)
        for k, v in updated_sub_labels.items():
            for lang, arr in v.items():
                self.assertCountEqual(arr, self.updated_sub_labels[k][lang])

    def test_update_sub_labels_with_mismatched_arrays(self):
        # Load the sub-labels from sample data
        instructions = self.sample_sub_labels["instructions"]

        # Remove the last item from 'fr' array
        instructions["fr"] = instructions["fr"][:-1]

        # Create mismatched sub-labels JSON, where 'fr' is shorter
        mismatched_sub_labels = json.dumps({"instructions": instructions})

        try:
            # Attempt to update the sub-labels in the database
            # TODO: write missing sub_label functions
            self.cursor.execute(
                "SELECT update_sub_labels(%s, %s);",
                (self.label_id, mismatched_sub_labels),
            )
        except Exception as e:
            self.fail(f"update_sub_labels raised an unexpected exception: {e}")

        # Retrieve the saved sub-label data from the database
        saved_data = sub_label.get_sub_label_json(self.cursor, self.label_id)
        saved_instructions = saved_data["instructions"]

        # Check that the 'fr' array was padded with an empty string
        self.assertEqual(
            len(saved_instructions["fr"]),
            len(
                instructions["en"]
            ),  # 'fr' should be padded to match the length of 'en'
            f"Mismatch in length of 'fr' array: expected {len(instructions['en'])}, got {len(saved_instructions['fr'])}.",
        )

        # Assert that the content in 'fr' is correctly padded with an empty string
        self.assertEqual(
            saved_instructions["fr"],
            instructions["fr"]
            + [""],  # Expecting the missing value replaced by an empty string
            f"Mismatch in 'fr' content: expected {instructions['fr'] + ['']}, got {saved_instructions['fr']}.",
        )

        # Assert that the 'en' array was not modified
        self.assertEqual(
            saved_instructions["en"],
            instructions["en"],
            f"Mismatch in 'en' content: expected {instructions['en']}, got {saved_instructions['en']}.",
        )

    def test_update_sub_labels_with_empty_arrays(self):
        # Test with empty 'fr' and 'en' arrays
        empty_sub_labels = json.dumps({"instructions": {"fr": [], "en": []}})

        try:
            # Execute the function with empty sub labels
            # TODO: write missing sub_label functions
            self.cursor.execute(
                "SELECT update_sub_labels(%s, %s);", (self.label_id, empty_sub_labels)
            )
        except Exception as e:
            self.fail(f"update_sub_labels raised an exception with empty arrays: {e}")

        # Verify that no new data was inserted
        saved_data_empty = sub_label.get_all_sub_label(self.cursor, self.label_id)
        self.assertListEqual(
            saved_data_empty,
            [],
            "No sub label records should be inserted when arrays are empty",
        )


if __name__ == "__main__":
    unittest.main()
