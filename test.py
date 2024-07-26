import datastore.FertiScan as FertiScan
import datastore
import datastore.db.__init__ as db
import os
import json

if __name__ == "__main__":
    analysis_json = json.loads('tests/analyse.json')

    con = db.connect_db(FertiScan.FERTISCAN_DB_URL)
    cursor = con.cursor()
    db.create_search_path(con, cursor, FertiScan.FERTISCAN_SCHEMA)

    user_email = 'test@email'
    datastore.new_user(cursor, user_email)

    user_id = datastore.get_user_id(cursor, user_email)
    container_client = datastore.get_user_container_client(user_id, 'test-user')

    analysis = FertiScan.register_analysis(cursor, container_client, user_id, analysis_json)

    print(analysis)