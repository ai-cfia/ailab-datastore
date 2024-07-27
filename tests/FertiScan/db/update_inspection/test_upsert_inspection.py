import os
import unittest

import psycopg

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpsertInspectionFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Insert a user to act as the inspector
        self.cursor.execute(
            f'INSERT INTO "{DB_SCHEMA}".users (email) VALUES (%s) RETURNING id;',
            ("test_inspector@example.com",),
        )
        self.inspector_id = self.cursor.fetchone()[0]

        # Insert a label information record to link with inspection
        self.cursor.execute(
            f'INSERT INTO "{DB_SCHEMA}".label_information (lot_number, npk, registration_number, n, p, k) '
            f"VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;",
            ("L123456789", "10-20-30", "R123456", 10.0, 20.0, 30.0),
        )
        self.label_info_id = self.cursor.fetchone()[0]

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_insert_new_inspection_minimal_fields(self):
        # Insert a new inspection with minimal required fields
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_inspection(%s, %s, %s, %s, %s, %s);',
            (None, self.label_info_id, self.inspector_id, None, None, False),
        )
        inspection_id = self.cursor.fetchone()[0]

        # Verify that the inspection data is correctly saved
        self.cursor.execute(
            f'SELECT id, label_info_id, inspector_id, sample_id, picture_set_id, verified FROM "{DB_SCHEMA}".inspection WHERE id = %s;',
            (inspection_id,),
        )
        saved_inspection = self.cursor.fetchone()
        self.assertIsNotNone(saved_inspection, "Inspection record should be saved.")
        self.assertEqual(
            saved_inspection[1], self.label_info_id, "Label ID should match."
        )
        self.assertEqual(
            saved_inspection[2], self.inspector_id, "Inspector ID should match."
        )
        self.assertIsNone(saved_inspection[3], "Sample ID should be None.")
        self.assertIsNone(saved_inspection[4], "Picture Set ID should be None.")
        self.assertFalse(saved_inspection[5], "Verified should be False.")

    def test_update_existing_inspection(self):
        # Insert a new inspection first
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_inspection(%s, %s, %s, %s, %s, %s);',
            (None, self.label_info_id, self.inspector_id, None, None, False),
        )
        inspection_id = self.cursor.fetchone()[0]

        # Update the inspection record
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_inspection(%s, %s, %s, %s, %s, %s);',
            (inspection_id, self.label_info_id, self.inspector_id, None, None, True),
        )

        # Verify the data is updated
        self.cursor.execute(
            f'SELECT id, label_info_id, inspector_id, sample_id, picture_set_id, verified FROM "{DB_SCHEMA}".inspection WHERE id = %s;',
            (inspection_id,),
        )
        updated_inspection = self.cursor.fetchone()
        self.assertIsNotNone(
            updated_inspection, "Inspection record should still exist."
        )
        self.assertEqual(
            updated_inspection[5], True, "Verified status should be updated to True."
        )

    def test_upsert_with_null_values(self):
        # Test handling of null values in optional fields
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_inspection(%s, %s, %s, %s, %s, %s);',
            (None, self.label_info_id, self.inspector_id, None, None, True),
        )
        inspection_id = self.cursor.fetchone()[0]

        # Verify the data is correctly saved with nulls
        self.cursor.execute(
            f'SELECT id, sample_id, picture_set_id FROM "{DB_SCHEMA}".inspection WHERE id = %s;',
            (inspection_id,),
        )
        saved_inspection = self.cursor.fetchone()
        self.assertIsNotNone(saved_inspection, "Inspection record should be saved.")
        self.assertIsNone(saved_inspection[1], "Sample ID should be None.")
        self.assertIsNone(saved_inspection[2], "Picture Set ID should be None.")


if __name__ == "__main__":
    unittest.main()
