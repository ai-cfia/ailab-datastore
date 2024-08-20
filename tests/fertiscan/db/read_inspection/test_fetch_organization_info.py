import json
import os
import unittest

import psycopg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.getenv("FERTISCAN_DB_URL")
if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.getenv("FERTISCAN_SCHEMA_TESTING")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestFetchOrganizationInfoFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Manage transaction manually
        self.cursor = self.conn.cursor()

        # Set up test data for organization information (company)
        sample_company_info = {
            "name": "Test Company",
            "address": "123 Test Address",
            "website": "http://www.testcompany.com",
            "phone_number": "+1 800 555 0123",
        }
        self.cursor.execute(
            "SELECT upsert_organization_info(%s);", (json.dumps(sample_company_info),)
        )
        self.company_info_id = str(self.cursor.fetchone()[0])

        # Set up test data for organization information (manufacturer)
        sample_manufacturer_info = {
            "name": "Test Manufacturer",
            "address": "456 Test Manufacturer Address",
            "website": "http://www.testmanufacturer.com",
            "phone_number": "+1 800 555 0456",
        }
        self.cursor.execute(
            "SELECT upsert_organization_info(%s);",
            (json.dumps(sample_manufacturer_info),),
        )
        self.manufacturer_info_id = str(self.cursor.fetchone()[0])

    def tearDown(self):
        # Roll back any changes to leave the database state unchanged
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_fetch_company_info(self):
        # Execute the fetch_organization_info function for the company
        self.cursor.execute(
            "SELECT fetch_organization_info(%s);", (self.company_info_id,)
        )
        result = self.cursor.fetchone()[0]

        # Expected data
        expected_result = {
            "id": self.company_info_id,
            "name": "Test Company",
            "address": "123 Test Address",
            "website": "http://www.testcompany.com",
            "phone_number": "+1 800 555 0123",
        }

        # Validate the result
        self.assertIsNotNone(result, "Result should not be None")
        self.assertDictEqual(
            result, expected_result, "Company info should match the expected result"
        )

    def test_fetch_manufacturer_info(self):
        # Execute the fetch_organization_info function for the manufacturer
        self.cursor.execute(
            "SELECT fetch_organization_info(%s);", (self.manufacturer_info_id,)
        )
        result = self.cursor.fetchone()[0]

        # Expected data
        expected_result = {
            "id": self.manufacturer_info_id,
            "name": "Test Manufacturer",
            "address": "456 Test Manufacturer Address",
            "website": "http://www.testmanufacturer.com",
            "phone_number": "+1 800 555 0456",
        }

        # Validate the result
        self.assertIsNotNone(result, "Result should not be None")
        self.assertDictEqual(
            result,
            expected_result,
            "Manufacturer info should match the expected result",
        )

    def test_fetch_organization_info_empty(self):
        # Test with a non-existent organization_info_id
        non_existent_info_id = "00000000-0000-0000-0000-000000000000"
        self.cursor.execute(
            "SELECT fetch_organization_info(%s);", (non_existent_info_id,)
        )
        result = self.cursor.fetchone()[0]

        # Validate that the result is None when the organization is not found
        self.assertIsNone(
            result, "Result should be None when the organization is not found"
        )


if __name__ == "__main__":
    unittest.main()
