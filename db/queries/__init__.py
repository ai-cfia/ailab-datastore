"""
Module for database queries
This module is seperated into the objects that are being queried
"""

def query_db(conn,cur,query):
    cur.execute(query)
    conn.commit()
    return cur

def query_parameterized_db(conn,cur,query, params):
    cur.execute(query, params)
    conn.commit()
    return cur

def print_results(res):
    for record in res:
        print(record)
        
def get_results(cur):
    return cur.fetchall()

def get_one_result(cur):
    return cur.fetchone()