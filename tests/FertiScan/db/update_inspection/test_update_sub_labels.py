import json
import os
import unittest

import psycopg
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
        self.sample_sub_labels = json.dumps(
            {
                "instructions": {
                    "fr": [
                        "1. Dissoudre 50g dans 10L d'eau.",
                        "2. Appliquer toutes les 2 semaines.",
                        "3. Conserver dans un endroit frais et sec.",
                    ],
                    "en": [
                        "1. Dissolve 50g in 10L of water.",
                        "2. Apply every 2 weeks.",
                        "3. Store in a cool, dry place.",
                    ],
                },
                "cautions": {
                    "fr": [
                        "Tenir hors de portée des enfants.",
                        "Éviter le contact avec la peau et les yeux.",
                    ],
                    "en": [
                        "Keep out of reach of children.",
                        "Avoid contact with skin and eyes.",
                    ],
                },
                "first_aid": {
                    "fr": [
                        "En cas de contact avec les yeux, rincer immédiatement à grande eau et consulter un médecin."
                    ],
                    "en": [
                        "In case of contact with eyes, rinse immediately with plenty of water and seek medical advice."
                    ],
                },
                "warranty": {
                    "fr": ["Garantie limitée de 1 an."],
                    "en": ["Limited warranty of 1 year."],
                },
            }
        )

        self.updated_sub_labels = json.dumps(
            {
                "instructions": {
                    "fr": [
                        "1. Dissoudre 50g dans 10L d'eau.",
                        "2. Appliquer toutes les 2 semaines.",
                        "3. Conserver dans un endroit frais.",
                    ],
                    "en": [
                        "1. Dissolve 50g in 10L of water.",
                        "2. Apply every 2 weeks.",
                        "3. Store in a cool place.",
                    ],
                },
                "cautions": {
                    "fr": [
                        "Tenir hors de portée des enfants.",
                        "Éviter le contact avec la peau et les yeux.",
                    ],
                    "en": [
                        "Keep out of reach of children.",
                        "Avoid contact with skin and eyes.",
                    ],
                },
                "first_aid": {
                    "fr": ["En cas de contact avec les yeux, rincer immédiatement."],
                    "en": ["If in eyes, rinse immediately."],
                },
                "warranty": {
                    "fr": ["Garantie limitée de 2 ans."],
                    "en": ["Limited warranty of 2 years."],
                },
            }
        )

        # Insert test data to obtain a valid label_id and sub_type_id
        sub_types = [
            ("instructions", "instructions"),
            ("cautions", "cautions"),
            ("first_aid", "first_aid"),
            ("warranty", "warranty"),
        ]
        self.sub_type_ids = {}
        for type_en, type_fr in sub_types:
            self.cursor.execute(
                f'INSERT INTO "{DB_SCHEMA}".sub_type (type_en, type_fr) VALUES (%s, %s) RETURNING id;',
                (type_en, type_fr),
            )
            self.sub_type_ids[type_en] = self.cursor.fetchone()[0]

        sample_org_info = json.dumps(
            {
                "name": "Test Company",
                "address": "123 Test Address",
                "website": "http://www.testcompany.com",
                "phone_number": "+1 800 555 0123",
            }
        )
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_organization_info(%s);', (sample_org_info,)
        )
        self.company_info_id = self.cursor.fetchone()[0]

        sample_label_info = json.dumps(
            {
                "lot_number": "L123456789",
                "npk": "10-20-30",
                "registration_number": "R123456",
                "n": 10.0,
                "p": 20.0,
                "k": 30.0,
            }
        )
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".upsert_label_information(%s, %s, %s);',
            (sample_label_info, self.company_info_id, self.company_info_id),
        )
        self.label_id = self.cursor.fetchone()[0]

    def tearDown(self):
        # Rollback any changes to leave the database state as it was before the test
        self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def test_update_sub_labels(self):
        # Insert initial sub labels
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".update_sub_labels(%s, %s);',
            (self.label_id, self.sample_sub_labels),
        )

        # Verify that the data is correctly saved
        self.cursor.execute(
            f'SELECT text_content_fr, text_content_en FROM "{DB_SCHEMA}".sub_label WHERE label_id = %s;',
            (self.label_id,),
        )
        saved_data = self.cursor.fetchall()
        expected_data = [
            ("1. Dissoudre 50g dans 10L d'eau.", "1. Dissolve 50g in 10L of water."),
            ("2. Appliquer toutes les 2 semaines.", "2. Apply every 2 weeks."),
            (
                "3. Conserver dans un endroit frais et sec.",
                "3. Store in a cool, dry place.",
            ),
            ("Tenir hors de portée des enfants.", "Keep out of reach of children."),
            (
                "Éviter le contact avec la peau et les yeux.",
                "Avoid contact with skin and eyes.",
            ),
            (
                "En cas de contact avec les yeux, rincer immédiatement à grande eau et consulter un médecin.",
                "In case of contact with eyes, rinse immediately with plenty of water and seek medical advice.",
            ),
            ("Garantie limitée de 1 an.", "Limited warranty of 1 year."),
        ]
        self.assertEqual(
            len(saved_data), 7, "There should be seven sub label records inserted"
        )
        self.assertListEqual(
            saved_data, expected_data, "Saved data should match the expected values"
        )

        # Update sub labels
        self.cursor.execute(
            f'SELECT "{DB_SCHEMA}".update_sub_labels(%s, %s);',
            (self.label_id, self.updated_sub_labels),
        )

        # Verify that the data is correctly updated
        self.cursor.execute(
            f'SELECT text_content_fr, text_content_en FROM "{DB_SCHEMA}".sub_label WHERE label_id = %s;',
            (self.label_id,),
        )
        updated_data = self.cursor.fetchall()
        expected_updated_data = [
            ("1. Dissoudre 50g dans 10L d'eau.", "1. Dissolve 50g in 10L of water."),
            ("2. Appliquer toutes les 2 semaines.", "2. Apply every 2 weeks."),
            ("3. Conserver dans un endroit frais.", "3. Store in a cool place."),
            ("Tenir hors de portée des enfants.", "Keep out of reach of children."),
            (
                "Éviter le contact avec la peau et les yeux.",
                "Avoid contact with skin and eyes.",
            ),
            (
                "En cas de contact avec les yeux, rincer immédiatement.",
                "If in eyes, rinse immediately.",
            ),
            ("Garantie limitée de 2 ans.", "Limited warranty of 2 years."),
        ]
        self.assertEqual(
            len(updated_data), 7, "There should be seven sub label records after update"
        )
        self.assertListEqual(
            updated_data,
            expected_updated_data,
            "Updated data should match the new values",
        )


if __name__ == "__main__":
    unittest.main()
