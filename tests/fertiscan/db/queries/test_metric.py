import os
import unittest
import uuid

from dotenv import load_dotenv
from psycopg import Connection, connect

from fertiscan.db.models import DBMetric, FullMetric, Metric, Metrics, Unit
from fertiscan.db.queries.label import new_label_information
from fertiscan.db.queries.metric import (
    create_metric,
    delete_metric,
    get_metrics_json,
    query_metrics,
    read_all_metrics,
    read_full_metric,
    read_metric,
    update_metric,
    update_metrics,
)
from fertiscan.db.queries.unit import create_unit

load_dotenv()

TEST_DB_CONNECTION_STRING = os.environ["FERTISCAN_DB_URL"]
TEST_DB_SCHEMA = os.environ["FERTISCAN_SCHEMA_TESTING"]


class TestCreateMetric(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conn: Connection = connect(
            TEST_DB_CONNECTION_STRING, options=f"-c search_path={TEST_DB_SCHEMA},public"
        )
        cls.conn.autocommit = False

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def setUp(self):
        self.cursor = self.conn.cursor()
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

        unit_name = f"unit-{uuid.uuid4().hex[:5]}"
        to_si_unit = 1.0
        self.unit = create_unit(self.cursor, unit_name, to_si_unit)
        self.unit = Unit.model_validate(self.unit)

        self.label_id = new_label_information(
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

    def tearDown(self):
        self.conn.rollback()
        self.cursor.close()

    def test_create_metric_success(self):
        value = 10.5
        edited = True
        metric_type = "volume"

        # Attempt to create the metric
        metric = create_metric(
            self.cursor, value, edited, self.unit.id, metric_type, self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Check if the returned record matches the input
        self.assertIsNotNone(metric)
        self.assertEqual(metric.value, value)
        self.assertEqual(metric.edited, edited)
        self.assertEqual(metric.unit_id, self.unit.id)
        self.assertEqual(metric.metric_type, metric_type)
        self.assertEqual(metric.label_id, self.label_id)

    def test_create_metric_missing_value(self):
        edited = True
        metric_type = "volume"

        # Attempt to create a metric with a missing value
        metric = create_metric(
            self.cursor, None, edited, self.unit.id, metric_type, self.label_id
        )
        self.assertIsNotNone(metric)

    def test_create_metric_missing_optional_fields(self):
        value = 20.0

        # Attempt to create a metric with only the value field
        metric = create_metric(self.cursor, value)
        metric = DBMetric.model_validate(metric)

        # Check if the returned record has the expected value and defaults
        self.assertIsNotNone(metric)
        self.assertEqual(metric.value, value)
        self.assertFalse(metric.edited)
        self.assertIsNone(metric.unit_id)
        self.assertIsNone(metric.metric_type)
        self.assertIsNone(metric.label_id)

    def test_create_metric_invalid_unit_id(self):
        value = 10.5
        edited = True
        unit_id = "invalid-uuid"  # Invalid UUID
        metric_type = "type1"
        label_id = str(uuid.uuid4())

        # Expect an exception due to invalid UUID format
        with self.assertRaises(Exception):
            create_metric(self.cursor, value, edited, unit_id, metric_type, label_id)

    def test_read_metric_success(self):
        value = 10.5
        edited = True
        metric_type = "volume"

        # Create a metric to read
        metric = create_metric(
            self.cursor, value, edited, self.unit.id, metric_type, self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Attempt to read the created metric
        read_metric_result = read_metric(self.cursor, metric.id)
        read_metric_result = DBMetric.model_validate(read_metric_result)

        # Check if the read record matches the created one
        self.assertIsNotNone(read_metric_result)
        self.assertEqual(read_metric_result, metric)

    def test_read_metric_not_found(self):
        # Attempt to read a metric with a non-existent ID
        result = read_metric(self.cursor, str(uuid.uuid4()))

        # Check that the result is None
        self.assertIsNone(result)

    def test_read_metric_invalid_id(self):
        # Attempt to read a metric with an invalid ID (None)
        with self.assertRaises(ValueError):
            read_metric(self.cursor, None)

    def test_read_all_metrics(self):
        # Create a few metrics
        metric1 = create_metric(
            self.cursor, 10.5, True, self.unit.id, "volume", self.label_id
        )
        metric1 = DBMetric.model_validate(metric1)

        metric2 = create_metric(
            self.cursor, 20.0, False, self.unit.id, "weight", self.label_id
        )
        metric2 = DBMetric.model_validate(metric2)

        # Read all metrics
        metrics = read_all_metrics(self.cursor)
        validated_metrics = [DBMetric.model_validate(m) for m in metrics]

        # Check if the created metrics are in the results
        self.assertIn(metric1, validated_metrics)
        self.assertIn(metric2, validated_metrics)

    def test_update_metric_success(self):
        # Create a metric to update
        metric = create_metric(
            self.cursor, 10.5, True, self.unit.id, "volume", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # New values for the metric
        new_value = 15.0
        new_edited = False
        new_metric_type = "weight"

        # Attempt to update the metric
        updated_metric = update_metric(
            self.cursor,
            metric.id,
            new_value,
            new_edited,
            self.unit.id,
            new_metric_type,
            self.label_id,
        )
        updated_metric = DBMetric.model_validate(updated_metric)

        # Check if the updated metric matches the new values
        self.assertIsNotNone(updated_metric)
        self.assertEqual(updated_metric.id, metric.id)
        self.assertEqual(updated_metric.value, new_value)
        self.assertEqual(updated_metric.edited, new_edited)
        self.assertEqual(updated_metric.unit_id, self.unit.id)
        self.assertEqual(updated_metric.metric_type, new_metric_type)
        self.assertEqual(updated_metric.label_id, self.label_id)

    def test_update_metric_not_found(self):
        # Attempt to update a metric with a non-existent ID
        updated_metric = update_metric(
            self.cursor,
            str(uuid.uuid4()),
            15.0,
            False,
            self.unit.id,
            "weight",
            self.label_id,
        )

        # Check that the result is None
        self.assertIsNone(updated_metric)

    def test_update_metric_invalid_id(self):
        # Attempt to update a metric with an invalid ID (None)
        with self.assertRaises(ValueError):
            update_metric(
                self.cursor,
                None,
                15.0,
                False,
                self.unit.id,
                "weight",
                self.label_id,
            )

    def test_delete_metric_success(self):
        # Create a metric to delete
        metric = create_metric(
            self.cursor, 10.5, True, self.unit.id, "volume", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Attempt to delete the created metric
        deleted_metric = delete_metric(self.cursor, metric.id)
        deleted_metric = DBMetric.model_validate(deleted_metric)

        # Check if the deleted metric matches the created one
        self.assertIsNotNone(deleted_metric)
        self.assertEqual(deleted_metric, metric)

        # Ensure the metric no longer exists
        self.assertIsNone(read_metric(self.cursor, metric.id))

    def test_delete_metric_not_found(self):
        # Attempt to delete a metric with a non-existent ID
        result = delete_metric(self.cursor, str(uuid.uuid4()))

        # Ensure the result is None, indicating no deletion occurred
        self.assertIsNone(result)

    def test_delete_metric_invalid_id(self):
        # Attempt to delete a metric with an invalid ID (None)
        with self.assertRaises(ValueError):
            delete_metric(self.cursor, None)

    def test_query_metrics_by_value_range(self):
        # Create metrics with different values
        metric1 = create_metric(
            self.cursor, 5.0, True, self.unit.id, "volume", self.label_id
        )
        metric1 = DBMetric.model_validate(metric1)

        metric2 = create_metric(
            self.cursor, 15.0, False, self.unit.id, "weight", self.label_id
        )
        metric2 = DBMetric.model_validate(metric2)

        metric3 = create_metric(
            self.cursor, 25.0, True, self.unit.id, "density", self.label_id
        )
        metric3 = DBMetric.model_validate(metric3)

        # Query by value range
        results = query_metrics(self.cursor, value_from=10.0, value_to=20.0)
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if metric2 is in the results, but not metric1 or metric3
        self.assertIn(metric2, validated_results)
        self.assertNotIn(metric1, validated_results)
        self.assertNotIn(metric3, validated_results)

    def test_query_metrics_by_edited(self):
        # Create metrics with different edited statuses
        metric1 = create_metric(
            self.cursor, 10.0, True, self.unit.id, "volume", self.label_id
        )
        metric1 = DBMetric.model_validate(metric1)

        metric2 = create_metric(
            self.cursor, 20.0, False, self.unit.id, "weight", self.label_id
        )
        metric2 = DBMetric.model_validate(metric2)

        # Query by edited status
        results = query_metrics(self.cursor, edited=True)
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if metric1 is in the results, but not metric2
        self.assertIn(metric1, validated_results)
        self.assertNotIn(metric2, validated_results)

    def test_query_metrics_by_unit_id(self):
        # Create a metric to query by unit ID
        metric = create_metric(
            self.cursor, 30.0, False, self.unit.id, "density", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Query by unit ID
        results = query_metrics(self.cursor, unit_id=self.unit.id)
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if the created metric is in the results
        self.assertIn(metric, validated_results)

    def test_query_metrics_by_metric_type(self):
        # Create a metric to query by metric type
        metric = create_metric(
            self.cursor, 40.0, False, self.unit.id, "weight", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Query by metric type
        results = query_metrics(self.cursor, metric_type="weight")
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if the created metric is in the results
        self.assertIn(metric, validated_results)

    def test_query_metrics_by_label_id(self):
        # Create a metric to query by label ID
        metric = create_metric(
            self.cursor, 50.0, True, self.unit.id, "volume", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Query by label ID
        results = query_metrics(self.cursor, label_id=self.label_id)
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if the created metric is in the results
        self.assertIn(metric, validated_results)

    def test_query_metrics_by_multiple_fields(self):
        # Create a metric to query by multiple fields
        metric = create_metric(
            self.cursor, 60.0, True, self.unit.id, "density", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Query by multiple fields
        results = query_metrics(
            self.cursor,
            value_from=50.0,
            value_to=70.0,
            edited=True,
            unit_id=self.unit.id,
            metric_type="density",
            label_id=self.label_id,
        )
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if the created metric is in the results
        self.assertIn(metric, validated_results)

    def test_query_metrics_no_filters(self):
        # Create a metric to query with no filters
        metric = create_metric(
            self.cursor, 70.0, False, self.unit.id, "volume", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Query with no filters (should return all metrics)
        results = query_metrics(self.cursor)
        validated_results = [DBMetric.model_validate(m) for m in results]

        # Check if the created metric is in the results
        self.assertIn(metric, validated_results)

    def test_read_full_metric_success(self):
        # Create a metric to read
        metric = create_metric(
            self.cursor, 15.0, True, self.unit.id, "weight", self.label_id
        )
        metric = DBMetric.model_validate(metric)

        # Attempt to read the full metric details
        full_metric_result = read_full_metric(self.cursor, metric.id)
        full_metric_result = FullMetric.model_validate(full_metric_result)

        # Check if the full metric details match the created metric
        self.assertIsNotNone(full_metric_result)
        self.assertEqual(full_metric_result.id, metric.id)
        self.assertEqual(full_metric_result.value, metric.value)
        self.assertEqual(full_metric_result.unit, self.unit.unit)
        self.assertEqual(full_metric_result.to_si_unit, self.unit.to_si_unit)
        self.assertEqual(full_metric_result.edited, metric.edited)
        self.assertEqual(full_metric_result.metric_type, metric.metric_type)
        self.assertEqual(full_metric_result.label_id, metric.label_id)

    def test_read_full_metric_not_found(self):
        # Attempt to read a full metric with a non-existent ID
        result = read_full_metric(self.cursor, str(uuid.uuid4()))

        # Ensure the result is None
        self.assertIsNone(result)

    def test_read_full_metric_invalid_id(self):
        # Attempt to read a full metric with an invalid ID (None)
        with self.assertRaises(ValueError):
            read_full_metric(self.cursor, None)

    def test_update_metrics(self):
        label_id = new_label_information(
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

        created_input = Metrics(
            weight=[Metric(value=5, unit="kg"), Metric(value=11, unit="lb")],
            density=Metric(value=1.2, unit="g/cm³"),
            volume=Metric(value=20.8, unit="L"),
        )

        updated_input = Metrics(
            weight=[Metric(value=6, unit="kg"), Metric(value=13, unit="lb")],
            density=Metric(value=1.3, unit="g/cm³"),
            volume=Metric(value=25.0, unit="L"),
        )

        # Insert initial metrics
        update_metrics(self.cursor, label_id, created_input)

        # Verify that the data is correctly saved
        created_output = get_metrics_json(self.cursor, label_id)
        created_output = Metrics.model_validate(created_output)
        self.assertEqual(created_output, created_input)

        # Update metrics using Pydantic model
        update_metrics(self.cursor, label_id, updated_input)

        # Verify that the data is correctly updated
        updated_output = get_metrics_json(self.cursor, label_id)
        updated_output = Metrics.model_validate(updated_output)
        self.assertEqual(updated_input, updated_output)


if __name__ == "__main__":
    unittest.main()
