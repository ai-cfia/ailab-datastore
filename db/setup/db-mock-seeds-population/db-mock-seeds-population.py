import psycopg
import os

NACHET_DB_URL = os.getenv("NACHET_DB_URL")

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")


def populate_seeds():
    # Connect to your PostgreSQL database with the DB URL
    conn = psycopg.connect(NACHET_DB_URL)
    # Create a cursor object
    cur = conn.cursor()
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

    cur.execute(f"""SET search_path TO "{NACHET_SCHEMA}";""")
    conn.commit()

    # Query to insert a seed
    query = "INSERT INTO seeds (name) VALUES (%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s),(%s,(%s),(%s),(%s),(%s),(%s),(%s)"

    cur.execute(query, seeds)

    conn.commit()

    cur.close()
    conn.close()


if __name__ == "main":
    populate_seeds()
