import os
import traceback

from psycopg import connect

from datastore.db.metadata import picture_set

# Import the function as specified
from datastore.db.queries import picture, user
from fertiscan.db.queries import inspection

# Use the constants you provided
DB_CONNECTION_STRING = os.environ.get("FERTISCAN_DB_URL")
DB_SCHEMA = os.environ.get("FERTISCAN_SCHEMA_TESTING")


def test_new_ingredient():
    conn = None
    try:
        # Establish a connection to the database
        conn = connect(
            DB_CONNECTION_STRING, options=f"-c search_path={DB_SCHEMA},public"
        )
        cursor = conn.cursor()

        user_email = "testessr@email"
        user_id = user.register_user(cursor, user_email)
        folder_name = "test-folder"
        picture_s = picture_set.build_picture_set(user_id, 1)
        picture_set_id = picture.new_picture_set(
            cursor, picture_s, user_id, folder_name
        )

        inspection_id = inspection.new_inspection(
            cursor, user_id, picture_set_id, False
        )

        # Explicitly roll back to avoid saving the data
        conn.rollback()

    except Exception as e:
        if conn:
            conn.rollback()
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        if conn:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    test_new_ingredient()
