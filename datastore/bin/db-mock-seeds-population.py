import db.queries
import os
import db as db

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")


def populate_seeds():
    # Connect to your PostgreSQL database with the DB URL
    conn = db.connect_db()
    # Create a cursor object
    cur = db.cursor(connection=conn)
    db.create_search_path(connection=conn, cur=cur)
    
    seeds = (
        "Brassica napus",
        "Brassica juncea",
        "Cirsium arvense",
        "Cirsium vulgare",
        "Carduus nutans",
        "Bromus secalinus",
        "Bromus hordeaceus",
        "Bromus japonicus",
        "Lolium temulentum",
        "Solanum carolinense",
        "Solanum nigrum",
        "Solanum rostratum",
        "Ambrosia artemisiifolia",
        "Ambrosia trifida",
        "Ambrosia psilostachya",
    )

    # Query to insert a seed
    query = "INSERT INTO seeds (name) VALUES (%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s,(%s),(%s),(%s),(%s),(%s),(%s)"

    db.queries.query_parameterized_db(cur, query, seeds)

    db.end_query(connection=conn, cursor=cur)


if __name__ == "main":
    populate_seeds()
