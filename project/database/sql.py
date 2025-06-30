import mysql.connector
import json
import sys
import random
import string

sys.path.append('/home/connex/library')
from SynapsisLibrary import *


def openDB():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = "synapsis_project"
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class resetDatabaseProject():
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
