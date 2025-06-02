import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import sql


def openDB():
    with open('/home/connex/project/database/dbNearonProject.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class FeatureSettingDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT name, value FROM featureSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def toggle():
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM featureSettingDB WHERE name = 'log'"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def updateByName(name, value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE featureSettingDB SET value=%s WHERE name=%s"
        value = (value, name)
        action = sql.execute(connection, query, value)
        return action
    