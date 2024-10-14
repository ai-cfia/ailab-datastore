import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

from fertiscan.db.models import GuaranteedAnalysis, Location, Province, Region
from fertiscan.db.queries import label, nutrients, organization
from fertiscan.db.queries.location import create_location
from fertiscan.db.queries.province import create_province
from fertiscan.db.queries.region import create_region

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateGuaranteedFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for guaranteed analysis
        with open("tests/fertiscan/inspection_export.json") as f:
            inspection_data = json.load(f)
        self.sample_guaranteed = json.dumps(inspection_data["guaranteed_analysis"])
        self.nb_guaranteed = len(inspection_data["guaranteed_analysis"]["en"]) + len(
            inspection_data["guaranteed_analysis"]["fr"]
        )
        self.updated_guaranteed = {
            "inspection": {
                "guaranteed_analysis": {
                    "en": [
                        {"name": "Total Nitrogen (N)", "value": 22, "unit": "%"},
                        {
                            "name": "Available Phosphate (P2O5)",
                            "value": 22,
                            "unit": "%",
                        },
                        {"name": "Soluble Potash (K2O)", "value": 22, "unit": "%"},
                    ],
                    "fr": [
                        {"name": "Total Nitrogen (N)", "value": 22, "unit": "%"},
                        {
                            "name": "Available Phosphate (P2O5)",
                            "value": 22,
                            "unit": "%",
                        },
                        {"name": "Soluble Potash (K2O)", "value": 22, "unit": "%"},
                    ],
                }
            }
        }

        # Insert test data to obtain a valid label_id
        self.province_name = "a-test-province"
        self.region_name = "test-region"
        self.name = "test-organization"
        self.website = "www.test.com"
        self.phone = "123456789"
        self.location_name = "test-location"
        self.location_address = "test-address"
        self.province = create_province(self.cursor, self.province_name)
        self.province = Province.model_validate(self.province)
        self.region = create_region(self.cursor, self.region_name, self.province.id)
        self.region = Region.model_validate(self.region)
        self.location = create_location(
            self.cursor, self.location_name, self.location_address, self.region.id
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

    def test_update_guaranteed(self):
        # Insert initial guaranteed analysis
        # TODO: write missing guaranteed functions
        self.cursor.execute(
            "SELECT update_guaranteed(%s, %s);",
            (self.label_id, self.sample_guaranteed),
        )

        # Verify that the data is correctly saved
        basic_data = nutrients.get_guaranteed_analysis_json(self.cursor, self.label_id)
        basic_data = GuaranteedAnalysis.model_validate(basic_data)
        self.assertEqual(
            len(basic_data.en) + len(basic_data.fr),
            self.nb_guaranteed,
            f"There should be {self.nb_guaranteed} guaranteed analysis records inserted",
        )

        # Update guaranteed analysis
        # TODO: write missing guaranteed functions
        self.cursor.execute(
            "SELECT update_guaranteed(%s, %s);",
            (self.label_id, json.dumps(self.updated_guaranteed)),
        )

        # Verify that the data is correctly updated
        updated_data = nutrients.get_guaranteed_analysis_json(
            self.cursor, self.label_id
        )
        updated_data = GuaranteedAnalysis.model_validate(updated_data)
        for value in updated_data.en:
            self.assertEqual(value.value, 22)


if __name__ == "__main__":
    unittest.main()
