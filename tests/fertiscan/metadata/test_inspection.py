import json
import os
import unittest

import datastore.db as db
import datastore.db.metadata.inspection as metadata
from datastore.db.metadata.inspection.pipeline_models import (
    FertilizerInspection,
    NutrientValue,
    PipelineGuaranteedAnalysis,
    PipelineValue,
)
from datastore.db.queries import (
    inspection,
    picture,
    user,
)

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


class TestTransformAnalysisToInspection(unittest.TestCase):
    def setUp(self):
        self.valid_analysis_form = FertilizerInspection(
            company_name="Test Company",
            company_address="123 Test St",
            company_website="http://test.com",
            company_phone_number="123456789",
            manufacturer_name="Test Manufacturer",
            manufacturer_address="456 Manufacturer St",
            manufacturer_website="http://manufacturer.com",
            manufacturer_phone_number="987654321",
            fertiliser_name="Test Fertilizer",
            registration_number="1234",
            lot_number="5678",
            weight=[PipelineValue(value=100, unit="kg")],
            density=PipelineValue(value=1.2, unit="g/cm3"),
            volume=PipelineValue(value=50, unit="L"),
            npk="10-20-30",
            cautions_en=["Keep away from children"],
            cautions_fr=["Tenir loin des enfants"],
            instructions_en=["Apply evenly"],
            instructions_fr=["Appliquer uniformément"],
            ingredients_en=[NutrientValue(nutrient="N", value=10, unit="%")],
            ingredients_fr=[NutrientValue(nutrient="P", value=20, unit="%")],
            guaranteed_analysis_en=PipelineGuaranteedAnalysis(
                title="Guaranteed Analysis",
                nutrients=[
                    NutrientValue(nutrient="Nitrogen", value=10, unit="%"),
                    NutrientValue(nutrient="Phosphorus", value=20, unit="%"),
                    NutrientValue(nutrient="Potassium", value=30, unit="%"),
                ],
            ),
            guaranteed_analysis_fr=PipelineGuaranteedAnalysis(
                title="Analyse Garantie",
                nutrients=[
                    NutrientValue(nutrient="Azote", value=10, unit="%"),
                    NutrientValue(nutrient="Phosphore", value=20, unit="%"),
                    NutrientValue(nutrient="Potassium", value=30, unit="%"),
                ],
            ),
        )

        self.partial_analysis_form = FertilizerInspection(
            company_name=None,
            company_address=None,
            company_website=None,
            company_phone_number=None,
            manufacturer_name=None,
            manufacturer_address=None,
            manufacturer_website=None,
            manufacturer_phone_number=None,
            fertiliser_name=None,
            registration_number=None,
            lot_number=None,
            weight=[],
            density=None,
            volume=None,
            npk=None,
            cautions_en=[],
            cautions_fr=[],
            instructions_en=[],
            instructions_fr=[],
            ingredients_en=[],
            ingredients_fr=[],
            guaranteed_analysis_en=None,
            guaranteed_analysis_fr=None,
        )

    def test_valid_transformation(self):
        inspection = metadata.transform_analysis_to_inspection(self.valid_analysis_form)
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.product.name, "Test Fertilizer")
        self.assertEqual(inspection.product.npk, "10-20-30")
        self.assertEqual(inspection.product.metrics.weight[0].value, 100)
        self.assertEqual(inspection.cautions.en[0], "Keep away from children")
        self.assertEqual(inspection.ingredients.en[0].name, "N")
        self.assertEqual(inspection.ingredients.fr[0].name, "P")
        self.assertIsNotNone(inspection.guaranteed_analysis)
        self.assertEqual(inspection.guaranteed_analysis.en[0].name, "Nitrogen")
        self.assertEqual(inspection.guaranteed_analysis.en[0].value, 10)
        self.assertEqual(inspection.guaranteed_analysis.fr[0].name, "Azote")
        self.assertEqual(inspection.guaranteed_analysis.fr[0].value, 10)

    def test_partial_transformation(self):
        inspection = metadata.transform_analysis_to_inspection(
            self.partial_analysis_form
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNone(inspection.company)
        self.assertIsNone(inspection.manufacturer)
        self.assertIsNone(inspection.product)
        self.assertEqual(inspection.cautions.en, [])
        self.assertIsNone(inspection.ingredients)
        self.assertIsNone(inspection.guaranteed_analysis)

    def test_missing_npk(self):
        analysis_form_no_npk = self.valid_analysis_form.model_copy(update={"npk": None})
        inspection = metadata.transform_analysis_to_inspection(analysis_form_no_npk)
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNone(inspection.product.npk)

    def test_empty_lists_in_analysis(self):
        analysis_form_empty_lists = self.valid_analysis_form.model_copy(
            update={"weight": [], "instructions_en": [], "cautions_fr": []}
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_empty_lists
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.product.metrics.weight, [])
        self.assertEqual(inspection.instructions.en, [])
        self.assertEqual(inspection.cautions.fr, [])

    def test_none_guaranteed_analysis(self):
        inspection = metadata.transform_analysis_to_inspection(
            self.valid_analysis_form.model_copy(
                update={"guaranteed_analysis_en": None, "guaranteed_analysis_fr": None}
            )
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNone(inspection.guaranteed_analysis)

    def test_company_but_no_manufacturer(self):
        analysis_form_no_manufacturer = self.valid_analysis_form.model_copy(
            update={
                "manufacturer_name": None,
                "manufacturer_address": None,
                "manufacturer_website": None,
                "manufacturer_phone_number": None,
            }
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_no_manufacturer
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.company)
        self.assertIsNone(inspection.manufacturer)

    def test_manufacturer_but_no_company(self):
        analysis_form_no_company = self.valid_analysis_form.model_copy(
            update={
                "company_name": None,
                "company_address": None,
                "company_website": None,
                "company_phone_number": None,
            }
        )
        inspection = metadata.transform_analysis_to_inspection(analysis_form_no_company)
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.manufacturer)
        self.assertIsNone(inspection.company)

    def test_partial_product_information(self):
        analysis_form_partial_product = self.valid_analysis_form.model_copy(
            update={
                "fertiliser_name": "Test Fertilizer",
                "registration_number": None,
                "lot_number": None,
            }
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_partial_product
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.product.name, "Test Fertilizer")
        self.assertIsNone(inspection.product.registration_number)
        self.assertIsNone(inspection.product.lot_number)

    def test_no_metrics(self):
        analysis_form_no_metrics = self.valid_analysis_form.model_copy(
            update={"weight": [], "density": None, "volume": None}
        )
        inspection = metadata.transform_analysis_to_inspection(analysis_form_no_metrics)
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.product.metrics.weight, [])
        self.assertIsNone(inspection.product.metrics.density)
        self.assertIsNone(inspection.product.metrics.volume)

    def test_some_metrics_but_not_all(self):
        analysis_form_some_metrics = self.valid_analysis_form.model_copy(
            update={
                "weight": [PipelineValue(value=100, unit="kg")],
                "density": None,
                "volume": None,
            }
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_some_metrics
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.product.metrics.weight[0].value, 100)
        self.assertIsNone(inspection.product.metrics.density)
        self.assertIsNone(inspection.product.metrics.volume)

    def test_partial_cautions_and_instructions(self):
        analysis_form_partial_cautions = self.valid_analysis_form.model_copy(
            update={
                "cautions_en": ["Keep away from children"],
                "cautions_fr": [],
                "instructions_en": [],
                "instructions_fr": ["Appliquer uniformément"],
            }
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_partial_cautions
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertEqual(inspection.cautions.en, ["Keep away from children"])
        self.assertEqual(inspection.cautions.fr, [])
        self.assertEqual(inspection.instructions.fr, ["Appliquer uniformément"])
        self.assertEqual(inspection.instructions.en, [])

    def test_only_english_ingredients(self):
        analysis_form_english_ingredients = self.valid_analysis_form.model_copy(
            update={"ingredients_fr": []}
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_english_ingredients
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.ingredients.en)
        self.assertEqual(inspection.ingredients.en[0].name, "N")
        self.assertEqual(inspection.ingredients.fr, [])

    def test_only_french_ingredients(self):
        analysis_form_french_ingredients = self.valid_analysis_form.model_copy(
            update={"ingredients_en": []}
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_french_ingredients
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.ingredients.fr)
        self.assertEqual(inspection.ingredients.fr[0].name, "P")
        self.assertEqual(inspection.ingredients.en, [])

    def test_only_english_guaranteed_analysis(self):
        analysis_form_english_guaranteed_analysis = self.valid_analysis_form.model_copy(
            update={"guaranteed_analysis_fr": None}
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_english_guaranteed_analysis
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.guaranteed_analysis)
        self.assertEqual(inspection.guaranteed_analysis.en[0].name, "Nitrogen")
        self.assertEqual(inspection.guaranteed_analysis.fr, [])

    def test_only_french_guaranteed_analysis(self):
        analysis_form_french_guaranteed_analysis = self.valid_analysis_form.model_copy(
            update={"guaranteed_analysis_en": None}
        )
        inspection = metadata.transform_analysis_to_inspection(
            analysis_form_french_guaranteed_analysis
        )
        self.assertIsInstance(inspection, metadata.InspectionV2)
        self.assertIsNotNone(inspection.guaranteed_analysis)
        self.assertEqual(inspection.guaranteed_analysis.fr[0].name, "Azote")
        self.assertEqual(inspection.guaranteed_analysis.en, [])
