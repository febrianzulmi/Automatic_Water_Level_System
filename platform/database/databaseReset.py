import mysql.connector, json, sys, os
sys.path.append('/home/connex/library')
from SynapsisLibrary import *

def openDB():
    with open('/home/connex/platform/database/db.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

def openDBProject():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class resetDatabase():
    def deleteTable(table_name):
        try:
            connection = sql.connect(host, database, username, password)
            query = f"DROP TABLE IF EXISTS {table_name}"
            action = sql.execute(connection, query)
            connection.close()
            return True
        except Exception as e:
            print(f"Error deleting table {table_name}: {e}")
            return False
