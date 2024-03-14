import psycopg
import os
from db.entities.index import Index

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
        
def getResults(cur):
    return cur.fetchall()

def getOneResult(cur):
    return cur.fetchone()
        
if __name__ == "__main__":
    conn = createConnection()
    cur = createCursor(conn)
    createSearchPath(conn,cur)
    query = "SELECT * from indexes Limit 1"
    params = ('6193f6c9-2ad7-460f-a320-799a48773889',)
    cur = queryDB(conn,cur,query)
    res = getResults(cur)
    printResults(cur)
    index = Index(res[0][0],res[0][1],res[0][2])
    endQuery(conn,cur)