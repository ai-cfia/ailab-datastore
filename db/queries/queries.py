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
    print(f'SET search_path TO {NACHET_SCHEMA}') 
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

def printResults(res):
    for record in res:
        print(record)
        
def getResults(cur):
    return cur.fetchall()

def getOneResult(cur):
    return cur.fetchone()

if __name__ == "__main__":
    conn = createConnection()
    cur = createCursor(conn)
    createSearchPath(conn,cur)
    query = "SELECT * FROM seeds order by seeds.name"
    cur = queryDB(conn,cur,query)
    res = getResults(cur)
    printResults(res)
    endQuery(conn,cur)