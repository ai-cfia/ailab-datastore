from queries import queries
from entities.index.index import Index

if __name__ == "__main__":
    conn = queries.createConnection()
    cur = queries.createCursor(conn)
    queries.createSearchPath(conn,cur)
    query = "SELECT * from indexes Limit 1"
    cur = queries.queryDB(conn,cur,query)
    res = queries.getResults(cur)
    queries.printResults(cur)
    #index = Index(res[0][0],res[0][1],res[0][2])
    queries.endQuery(conn,cur)