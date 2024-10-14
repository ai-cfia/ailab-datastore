import os
import unittest

import psycopg
from dotenv import load_dotenv

import fertiscan.db.queries.label as label
from fertiscan.db.models import Metric, Metrics
from fertiscan.db.queries import metric, organization

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateMetricsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for metrics using Pydantic models
        self.sample_metrics = Metrics(
            weight=[Metric(value=5, unit="kg"), Metric(value=11, unit="lb")],
            density=Metric(value=1.2, unit="g/cm³"),
            volume=Metric(value=20.8, unit="L"),
        )

        self.updated_metrics = Metrics(
            weight=[Metric(value=6, unit="kg"), Metric(value=13, unit="lb")],
            density=Metric(value=1.3, unit="g/cm³"),
            volume=Metric(value=25.0, unit="L"),
        )

        # Insert test data to obtain a valid label_id
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
        self.location_id = organization.new_location(
            self.cursor, self.location_name, self.location_address, self.region_id
        )
        self.company_info_id = organization.new_organization_info(
            self.cursor,
            self.name,
            self.website,
            self.phone,
            self.location_id,
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

    def test_update_metrics(self):
        # Insert initial metrics
        # TODO: write missing metrics functions
        self.cursor.execute(
            "SELECT update_metrics(%s, %s);",
            (self.label_id, self.sample_metrics.model_dump_json()),
        )

        # Verify that the data is correctly saved
        metrics = metric.get_metrics_json(self.cursor, self.label_id)
        metrics = Metrics.model_validate(metrics)
        self.assertDictEqual(
            metrics.model_dump(),
            self.sample_metrics.model_dump(),
            "Saved metrics should match the input",
        )

        # Update metrics using Pydantic model
        # TODO: write missing metrics functions
        self.cursor.execute(
            "SELECT update_metrics(%s, %s);",
            (self.label_id, self.updated_metrics.model_dump_json()),
        )

        # Verify that the data is correctly updated
        metrics = metric.get_metrics_json(self.cursor, self.label_id)
        metrics = Metrics.model_validate(metrics)
        self.assertDictEqual(
            metrics.model_dump(),
            self.updated_metrics.model_dump(),
            "Updated metrics should match the input",
        )


if __name__ == "__main__":
    unittest.main()
