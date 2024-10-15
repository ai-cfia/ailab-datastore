import os
import unittest
import uuid

import datastore.db as db
from datastore.db.metadata import validator
from fertiscan.db.models import CompanyManufacturer, OrganizationInformation
from fertiscan.db.queries import label
from fertiscan.db.queries.organization_information import (
    create_organization_information,
)

DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
if DB_CONNECTION_STRING is None or DB_CONNECTION_STRING == "":
    raise ValueError("FERTISCAN_DB_URL is not set")

DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")
if DB_SCHEMA is None or DB_SCHEMA == "":
    raise ValueError("FERTISCAN_SCHEMA_TESTING is not set")

# ------------ label ------------


class test_label(unittest.TestCase):
    def setUp(self):
        self.con = db.connect_db(DB_CONNECTION_STRING, DB_SCHEMA)
        self.cursor = self.con.cursor()
        db.create_search_path(self.con, self.cursor, DB_SCHEMA)
        self.product_name = "product_name"
        self.lot_number = "lot_number"
        self.npk = "npk"
        self.registration_number = "registration_number"
        self.n = 10.0
        self.p = 20.0
        self.k = 30.0
        self.guaranteed_analysis_title_en = "guaranteed_analysis"
        self.guaranteed_analysis_title_fr = "analyse_garantie"
        self.guaranteed_is_minimal = False
        self.company_info_id = None
        self.manufacturer_info_id = None

    def tearDown(self):
        self.con.rollback()
        db.end_query(self.con, self.cursor)

    def test_new_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            self.company_info_id,
            self.manufacturer_info_id,
        )
        self.assertTrue(validator.is_valid_uuid(label_information_id))

    def test_get_label_information(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            self.company_info_id,
            self.manufacturer_info_id,
        )
        label_data = label.get_label_information(self.cursor, label_information_id)

        self.assertEqual(label_data[0], label_information_id)
        self.assertEqual(label_data[1], self.product_name)
        self.assertEqual(label_data[2], self.lot_number)
        self.assertEqual(label_data[3], self.npk)
        self.assertEqual(label_data[4], self.registration_number)
        self.assertEqual(label_data[5], self.n)
        self.assertEqual(label_data[6], self.p)
        self.assertEqual(label_data[7], self.k)
        self.assertEqual(label_data[8], self.guaranteed_analysis_title_en)
        self.assertEqual(label_data[9], self.guaranteed_analysis_title_fr)
        self.assertEqual(label_data[10], self.guaranteed_is_minimal)
        self.assertIsNone(label_data[11])
        self.assertIsNone(label_data[12])

    def test_get_label_information_json(self):
        label_information_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            None,
            None,
        )
        label_data = label.get_label_information_json(self.cursor, label_information_id)
        self.assertEqual(label_data["label_id"], str(label_information_id))
        self.assertEqual(label_data["name"], self.product_name)
        self.assertEqual(label_data["lot_number"], self.lot_number)
        self.assertEqual(label_data["npk"], self.npk)
        self.assertEqual(label_data["registration_number"], self.registration_number)
        self.assertEqual(label_data["n"], self.n)
        self.assertEqual(label_data["p"], self.p)
        self.assertEqual(label_data["k"], self.k)

    def test_get_label_information_json_wrong_label_id(self):
        with self.assertRaises(label.LabelInformationNotFoundError):
            label.get_label_information_json(self.cursor, str(uuid.uuid4()))

    def test_get_company_and_manufacturer_json(self):
        # Create company and manufacturer
        company = create_organization_information(self.cursor, name="company_name")
        company = OrganizationInformation.model_validate(company)
        manufacturer = create_organization_information(
            self.cursor, name="manufacturer_name"
        )
        manufacturer = OrganizationInformation.model_validate(manufacturer)

        # Create label
        label_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            company.id,
            manufacturer.id,
        )

        # Get company and manufacturer
        company_manufacturer = label.get_company_manufacturer_json(
            self.cursor, label_id
        )
        company_manufacturer = CompanyManufacturer.model_validate(company_manufacturer)

        # Verify that the company and manufacturer are correctly retrieved
        self.assertIsNotNone(company_manufacturer.company)
        self.assertEqual(str(company_manufacturer.company.id), str(company.id))
        self.assertEqual(company_manufacturer.company.name, company.name)
        self.assertEqual(
            str(company_manufacturer.manufacturer.id), str(manufacturer.id)
        )
        self.assertIsNotNone(company_manufacturer.manufacturer)
        self.assertEqual(company_manufacturer.manufacturer.name, manufacturer.name)

    def test_get_company_and_manufacturer_no_data(self):
        # Create label
        label_id = label.new_label_information(
            self.cursor,
            self.product_name,
            self.lot_number,
            self.npk,
            self.registration_number,
            self.n,
            self.p,
            self.k,
            self.guaranteed_analysis_title_en,
            self.guaranteed_analysis_title_fr,
            self.guaranteed_is_minimal,
            None,
            None,
        )

        # Get company and manufacturer
        company_manufacturer = label.get_company_manufacturer_json(
            self.cursor, label_id
        )
        company_manufacturer = CompanyManufacturer.model_validate(company_manufacturer)

        # Verify that the company and manufacturer are correctly retrieved
        self.assertIsNone(company_manufacturer.company.id)
        self.assertIsNone(company_manufacturer.company.name)
        self.assertIsNone(company_manufacturer.company.address)
        self.assertIsNone(company_manufacturer.company.website)
        self.assertIsNone(company_manufacturer.company.phone_number)
        self.assertIsNone(company_manufacturer.manufacturer.id)
        self.assertIsNone(company_manufacturer.manufacturer.name)
        self.assertIsNone(company_manufacturer.manufacturer.address)
        self.assertIsNone(company_manufacturer.manufacturer.website)
        self.assertIsNone(company_manufacturer.manufacturer.phone_number)
