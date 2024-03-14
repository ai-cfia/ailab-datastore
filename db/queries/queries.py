import psycopg
import os

NACHET_DB_URL = os.getenv("NACHET_DB_URL")

NACHET_SCHEMA = os.getenv("NACHET_SCHEMA")

def createConnection():
    return psycopg.connect(NACHET_DB_URL)

def createCursor(conn):
    return conn.cursor()

def createSearchPath(conn,cur):
    cur.execute(f"""SET search_path TO "{NACHET_SCHEMA}";""") 
    conn.commit()

def closeConnection(conn):
    conn.close()

def closeCursor(cur):
    cur.close()

def endQuery(conn,cursor):
    conn.commit()
    closeCursor(cursor)
    closeConnection(conn)

def queryDB(conn,cur,query):
    cur.execute(query)
    conn.commit()
    return cur

def queryParameterizedDB(conn,cur,query, params):
    cur.execute(query, params)
    conn.commit()
    return cur

def printResults(cur):
    for record in cur:
        print(record)