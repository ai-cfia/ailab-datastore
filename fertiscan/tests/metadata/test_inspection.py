import json
import os
import unittest

import datastore.db.__init__ as db
import datastore.db.metadata.inspection as metadata
from datastore.db.queries import inspection, picture, user

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")


class test_inspection_export(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)

        with open("tests/fertiscan/analyse.json") as f:
            self.analyse = json.load(f)

        self.formatted_analysis = metadata.build_inspection_import(self.analyse)

        self.user_id = user.register_user(self.cursor, "test-email@email")

        self.picture_set_id = picture.new_picture_set(
            self.cursor, json.dumps({}), self.user_id
        )

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_perfect_inspection(self):
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])
        self.assertDictEqual(inspection_dict["product"], data["product"])
        self.assertDictEqual(inspection_dict["manufacturer"], data["manufacturer"])
        self.assertDictEqual(inspection_dict["company"], data["company"])
        self.assertDictEqual(inspection_dict["micronutrients"], data["micronutrients"])
        self.assertDictEqual(inspection_dict["ingredients"], data["ingredients"])
        self.assertDictEqual(inspection_dict["specifications"], data["specifications"])
        self.assertDictEqual(inspection_dict["first_aid"], data["first_aid"])
        self.assertListEqual(
            inspection_dict["guaranteed_analysis"], data["guaranteed_analysis"]
        )

    def test_no_manufacturer(self):
        self.analyse["manufacturer_name"] = None
        self.analyse["manufacturer_website"] = None
        self.analyse["manufacturer_phone_number"] = None
        self.analyse["manufacturer_address"] = None

        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])
        self.assertDictEqual(inspection_dict["company"], data["company"])
        self.assertIsNotNone(data["manufacturer"])
        self.assertIsNone(data["manufacturer"]["id"])
        self.assertIsNone(data["manufacturer"]["name"])
        self.assertIsNone(data["manufacturer"]["address"])
        self.assertIsNone(data["manufacturer"]["phone_number"])
        self.assertIsNone(data["manufacturer"]["website"])

    def test_no_volume(self):
        self.analyse["volume"] = None
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["product"]["metrics"]["volume"])
        self.assertIsNone(data["product"]["metrics"]["volume"]["unit"])
        self.assertIsNone(data["product"]["metrics"]["volume"]["value"])

        self.assertIsNotNone(data["product"]["metrics"]["density"])
        self.assertIsNotNone(data["product"]["metrics"]["density"]["unit"])

    def test_no_weight(self):
        self.analyse["weight"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["product"]["metrics"]["weight"])
        self.assertListEqual(data["product"]["metrics"]["weight"], [])

    def test_missing_sub_label(self):
        self.analyse["instructions_en"] = []
        self.analyse["instructions_fr"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["instructions"])
        self.assertIsNotNone(data["instructions"]["en"])
        self.assertIsNotNone(data["instructions"]["fr"])
        self.assertListEqual(data["instructions"]["fr"], [])
        self.assertListEqual(data["instructions"]["en"], [])

    def test_unequal_sub_label_lengths_and_order(self):
        expected_instructions_en = ["one", ""]
        expected_instructions_fr = ["un", "deux"]
        self.analyse["instructions_en"] = expected_instructions_en
        self.analyse["instructions_fr"] = expected_instructions_fr
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")

        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)

        self.assertIsNotNone(data["instructions"])
        self.assertIsNotNone(data["instructions"]["en"])
        self.assertIsNotNone(data["instructions"]["fr"])

        self.assertEqual(
            set(data["instructions"]["en"]),
            set(expected_instructions_en),
            "Instructions EN mismatch",
        )
        self.assertEqual(
            set(data["instructions"]["fr"]),
            set(expected_instructions_fr),
            "Instructions FR mismatch",
        )

    def test_missing_specification(self):
        self.analyse["specifications_en"] = []
        self.analyse["specifications_fr"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["specifications"])
        self.assertIsNotNone(data["specifications"]["en"])
        self.assertIsNotNone(data["specifications"]["fr"])
        self.assertListEqual(data["specifications"]["fr"], [])
        self.assertListEqual(data["specifications"]["en"], [])

    def test_missing_ingredients(self):
        self.analyse["ingredients_en"] = []
        self.analyse["ingredients_fr"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["ingredients"])
        self.assertIsNotNone(data["ingredients"]["en"])
        self.assertIsNotNone(data["ingredients"]["fr"])
        self.assertListEqual(data["ingredients"]["fr"], [])
        self.assertListEqual(data["ingredients"]["en"], [])

    def test_missing_micronutrients(self):
        self.analyse["micronutrients_en"] = []
        self.analyse["micronutrients_fr"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["micronutrients"])
        self.assertIsNotNone(data["micronutrients"]["en"])
        self.assertIsNotNone(data["micronutrients"]["fr"])
        self.assertListEqual(data["micronutrients"]["fr"], [])
        self.assertListEqual(data["micronutrients"]["en"], [])

    def test_missing_guaranteed_analysis(self):
        self.analyse["guaranteed_analysis"] = []
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # print(formatted_analysis)
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]

        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")
        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)
        self.assertIsNotNone(data["inspection_id"])
        self.assertEqual(inspection_dict["inspection_id"], data["inspection_id"])
        self.assertEqual(inspection_dict["verified"], data["verified"])

        self.assertIsNotNone(data["guaranteed_analysis"])
        self.assertListEqual(data["guaranteed_analysis"], [])

    def test_no_empty_specifications(self):
        # Set specifications with one empty and one valid specification
        self.analyse["specifications_en"] = [
            {"humidity": None, "ph": None, "solubility": None},
            {"humidity": 10.0, "ph": 7.0, "solubility": 5.0},
        ]
        self.analyse["specifications_fr"] = [
            {"humidity": None, "ph": None, "solubility": None},
            {"humidity": 15.0, "ph": 6.5, "solubility": 3.5},
        ]

        formatted_analysis = metadata.build_inspection_import(self.analyse)

        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]
        label_information_id = inspection_dict["product"]["label_id"]

        if inspection_id is None:
            self.fail("Inspection not created")

        data = metadata.build_inspection_export(
            self.cursor, str(inspection_id), label_information_id
        )
        data = json.loads(data)

        # Check that no empty specification (all fields None) is present
        for spec in data["specifications"]["en"]:
            self.assertFalse(
                all(value is None for value in spec.values()),
                "Empty specification found in 'en' list",
            )

        for spec in data["specifications"]["fr"]:
            self.assertFalse(
                all(value is None for value in spec.values()),
                "Empty specification found in 'fr' list",
            )

    def test_empty_sub_label(self):
        # Modify analyse data to have empty cautions_en and cautions_fr
        self.analyse["cautions_en"] = []
        self.analyse["cautions_fr"] = []

        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # Create inspection and get label information
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]
        label_id = inspection_dict["product"]["label_id"]

        # Get inspection data using the inspection_id and label_id
        inspection_data = metadata.build_inspection_export(
            self.cursor, inspection_id, label_id
        )
        inspection_data = json.loads(inspection_data)

        # Assert that cautions in both 'en' and 'fr' are empty
        self.assertIsNotNone(inspection_data["cautions"])
        self.assertEqual(inspection_data["cautions"]["en"], [])
        self.assertEqual(inspection_data["cautions"]["fr"], [])

    def test_null_in_middle_of_sub_label_en(self):
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # Convert the JSON string to a dictionary
        formatted_analysis_dict = json.loads(formatted_analysis)

        # Apply alterations to the dictionary
        formatted_analysis_dict["cautions"]["en"] = ["Warning 1", None, "Warning 2"]
        formatted_analysis_dict["cautions"]["fr"] = [
            "Avertissement 1",
            "Avertissement 2",
            "Avertissement 3",
        ]

        # Convert the dictionary back to a JSON string
        formatted_analysis = json.dumps(formatted_analysis_dict)

        # Create inspection and get label information
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]
        label_id = inspection_dict["product"]["label_id"]

        # Get inspection data using the inspection_id and label_id
        inspection_data = metadata.build_inspection_export(
            self.cursor, inspection_id, label_id
        )
        inspection_data = json.loads(inspection_data)

        # Assert that null in cautions_en is replaced by an empty string
        self.assertIsNotNone(inspection_data["cautions"])
        self.assertEqual(
            inspection_data["cautions"]["en"],
            [
                formatted_analysis_dict["cautions"]["en"][0],
                "",
                formatted_analysis_dict["cautions"]["en"][2],
            ],
        )
        self.assertEqual(
            inspection_data["cautions"]["fr"],
            formatted_analysis_dict["cautions"]["fr"],
        )

    def test_mismatched_sub_label_lengths_en_longer(self):
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # Convert the JSON string to a dictionary
        formatted_analysis_dict = json.loads(formatted_analysis)

        # Apply alterations: cautions_en longer than cautions_fr
        formatted_analysis_dict["cautions"]["en"] = [
            "Warning 1",
            "Warning 2",
            "Warning 3",
        ]
        formatted_analysis_dict["cautions"]["fr"] = ["Avertissement 1"]

        # Convert the dictionary back to a JSON string
        formatted_analysis = json.dumps(formatted_analysis_dict)

        # Create inspection and get label information
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]
        label_id = inspection_dict["product"]["label_id"]

        # Get inspection data using the inspection_id and label_id
        inspection_data = metadata.build_inspection_export(
            self.cursor, inspection_id, label_id
        )
        inspection_data = json.loads(inspection_data)

        # Assert that both cautions_en and cautions_fr are padded to the same length
        self.assertIsNotNone(inspection_data["cautions"])
        self.assertEqual(
            inspection_data["cautions"]["en"],
            formatted_analysis_dict["cautions"]["en"],
        )
        self.assertEqual(
            inspection_data["cautions"]["fr"],
            [formatted_analysis_dict["cautions"]["fr"][0], "", ""],
        )

    def test_mismatched_sub_label_lengths_fr_longer(self):
        formatted_analysis = metadata.build_inspection_import(self.analyse)

        # Convert the JSON string to a dictionary
        formatted_analysis_dict = json.loads(formatted_analysis)

        # Apply alterations: cautions_fr longer than cautions_en
        formatted_analysis_dict["cautions"]["en"] = ["Warning 1"]
        formatted_analysis_dict["cautions"]["fr"] = [
            "Avertissement 1",
            "Avertissement 2",
            "Avertissement 3",
        ]

        # Convert the dictionary back to a JSON string
        formatted_analysis = json.dumps(formatted_analysis_dict)

        # Create inspection and get label information
        inspection_dict = inspection.new_inspection_with_label_info(
            self.cursor, self.user_id, self.picture_set_id, formatted_analysis
        )
        inspection_id = inspection_dict["inspection_id"]
        label_id = inspection_dict["product"]["label_id"]

        # Get inspection data using the inspection_id and label_id
        inspection_data = metadata.build_inspection_export(
            self.cursor, inspection_id, label_id
        )
        inspection_data = json.loads(inspection_data)

        # Print the inspection data
        # Assert that both cautions_en and cautions_fr are padded to the same length
        self.assertIsNotNone(inspection_data["cautions"])
        self.assertEqual(
            inspection_data["cautions"]["en"],
            [formatted_analysis_dict["cautions"]["en"][0], "", ""],
        )
        self.assertEqual(
            inspection_data["cautions"]["fr"],
            formatted_analysis_dict["cautions"]["fr"],
        )
