import json
import os
import unittest

from dotenv import load_dotenv

import datastore.db as db
import datastore.db.queries.label as label
import datastore.db.queries.sub_label as sub_label
from datastore.db.metadata import validator

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")

if not DB_CONNECTION_STRING:
    raise ValueError("FERTISCAN_DB_URL is not set")
if not DB_SCHEMA:
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateSubLabelsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the database and set schema
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        # Setup label and sub-label information
        self.label_id = label.new_label_information(
            self.cursor,
            "product_name",
            "lot_number",
            "npk",
            "registration_number",
            10.0,
            20.0,
            30.0,
            "warranty",
            None,
            None,
        )
        self.type_fr = "test-type-fr"
        self.type_en = "test-type-en"
        self.sub_type_id = sub_label.new_sub_type(
            self.cursor, self.type_fr, self.type_en
        )

        # Text for sub-labels
        self.text_fr = "text_fr"
        self.text_en = "text_en"
        self.updated_text_fr = "updated_text_fr"
        self.updated_text_en = "updated_text_en"

        # Updated sub-labels JSON structure
        self.updated_sub_labels = json.dumps(
            {self.type_en: {"fr": [self.updated_text_fr], "en": [self.updated_text_en]}}
        )

    def tearDown(self):
        # Rollback changes and close connection
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_insert_and_update_sub_label(self):
        # Insert a sub-label
        sub_label_id = sub_label.new_sub_label(
            self.cursor,
            self.text_fr,
            self.text_en,
            self.label_id,
            self.sub_type_id,
            False,
        )
        self.assertTrue(validator.is_valid_uuid(sub_label_id))

        # Update sub-labels
        self.cursor.execute(
            "SELECT update_sub_labels(%s, %s);",
            (self.label_id, self.updated_sub_labels),
        )

        # Verify the updated sub-label
        self.cursor.execute(
            "SELECT text_content_fr, text_content_en FROM sub_label WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        self.assertEqual(updated_data, [(self.updated_text_fr, self.updated_text_en)])


if __name__ == "__main__":
    unittest.main()
