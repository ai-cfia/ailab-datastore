import unittest

from psycopg import Error as PsycopgError

from fertiscan.db.queries.errors import QueryError, handle_query_errors


class TestHandleQueryErrors(unittest.TestCase):
    # Test to ensure the decorated function runs successfully without errors
    def test_successful_function_execution(self):
        @handle_query_errors()
        def successful_function():
            return "Success"

        self.assertEqual(successful_function(), "Success")

    # Test to verify that QueryError and its subclasses are raised as-is
    def test_query_error_propagation(self):
        class CustomQueryError(QueryError):
            pass

        @handle_query_errors()
        def function_raises_query_error():
            raise CustomQueryError("Test query error")

        with self.assertRaises(CustomQueryError):
            function_raises_query_error()

    # Test to ensure that psycopg DB errors are caught and raised as QueryError
    def test_db_error_handling(self):
        @handle_query_errors()
        def function_raises_db_error():
            raise PsycopgError("DB error")

        with self.assertRaises(QueryError) as cm:
            function_raises_db_error()

        self.assertIn("Database error: DB error", str(cm.exception))

    # Test to ensure any unexpected exceptions are caught and raised as QueryError
    def test_unexpected_error_handling(self):
        @handle_query_errors()
        def function_raises_unexpected_error():
            raise ValueError("Some value error")

        with self.assertRaises(QueryError) as cm:
            function_raises_unexpected_error()

        self.assertIn("Unexpected error: Some value error", str(cm.exception))

    # Test to check custom error class handling in the decorator
    def test_custom_error_cls(self):
        class CustomError(Exception):
            pass

        @handle_query_errors(error_cls=CustomError)
        def function_raises_db_error():
            raise PsycopgError("DB error")

        with self.assertRaises(CustomError) as cm:
            function_raises_db_error()

        self.assertIn("Database error: DB error", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
