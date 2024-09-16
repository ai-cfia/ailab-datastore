import json
import os
import unittest

import psycopg
import datastore.db.queries.label as label
import datastore.db.queries.sub_label as sub_label
from dotenv import load_dotenv

load_dotenv()

# Fetch database connection URL and schema from environment variables
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class TestUpdateSubLabelsFunction(unittest.TestCase):
    def setUp(self):
        # Connect to the PostgreSQL database with the specified schema
        self.conn = psycopg.connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        self.conn.autocommit = False  # Ensure transaction is managed manually
        self.cursor = self.conn.cursor()

        # Set up test data for sub labels
        with open("tests/fertiscan/inspection_export.json") as f:
            inspection_data = json.load(f)
        self.sample_sub_labels = json.dumps(
            {
                "instructions": inspection_data["instructions"],
                "cautions": inspection_data["cautions"],
            }
        )
        self.nb_sub_labels = len(inspection_data["instructions"]["en"]) + len(
            inspection_data["cautions"]["en"]
        )
        # self.updated_sub_labels = self.sample_sub_labels

        self.updated_sub_labels = json.dumps(
            {
                "instructions": {
                    "fr": [
                        "1. Dissoudre 50g dans 10L d'eau.",
                        "2. Appliquer toutes les 2 semaines.",
                        "3. Conserver dans un endroit frais.",
                        "4. Test instruction.",
                        "5. Test instruction.",
                    ],
                    "en": [
                        "1. Dissolve 50g in 10L of water.",
                        "2. Apply every 2 weeks.",
                        "3. Store in a cool place.",
                        "4. Test instruction.",
                        "5. Test instruction.",
                    ],
                },
                "cautions": {
                    "fr": [
                        "Tenir hors de portée des enfants.",
                        "Éviter le contact avec la peau et les yeux.",
                        "En cas de contact avec les yeux, rincer immédiatement.",
                        "Garantie limitée de 1 an.",
                        "Test caution.",
                    ],
                    "en": [
                        "Keep out of reach of children.",
                        "Avoid contact with skin and eyes.",
                        "If in eyes, rinse immediately.",
                        "Limited warranty of 1 year.",
                        "Test caution.",
                    ],
                },
            }
        )
        self.nb_updated = 10

        sample_org_info = json.dumps(
            {
                "name": "Test Company",
                "address": "123 Test Address",
                "website": "http://www.testcompany.com",
                "phone_number": "+1 800 555 0123",
            }
        )
        self.cursor.execute("SELECT upsert_organization_info(%s);", (sample_org_info,))
        self.company_info_id = self.cursor.fetchone()[0]

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
        self.cursor.execute(
            "SELECT update_sub_labels(%s, %s);",
            (self.label_id, self.sample_sub_labels),
        )

        saved_data = sub_label.get_sub_label_json(self.cursor, self.label_id)
        nb_sub_labels = len(saved_data["instructions"]["en"]) + len(
            saved_data["cautions"]["en"]
        )

        self.assertEqual(
            nb_sub_labels,
            self.nb_sub_labels,
            f"There should be {self.nb_sub_labels} sub label records inserted",
        )

        # Update sub labels
        self.cursor.execute(
            "SELECT update_sub_labels(%s, %s);",
            (self.label_id, self.updated_sub_labels),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            "SELECT text_content_fr, text_content_en FROM sub_label WHERE label_id = %s;",
            (self.label_id,),
        )
        updated_data = sub_label.get_sub_label_json(self.cursor, self.label_id)
        nb_updated = len(updated_data["instructions"]["en"]) + len(
            updated_data["cautions"]["en"]
        )

        self.assertEqual(
            nb_updated,
            self.nb_updated,
            f"There should be {self.nb_sub_labels} sub label records inserted",
        )


if __name__ == "__main__":
    unittest.main()
