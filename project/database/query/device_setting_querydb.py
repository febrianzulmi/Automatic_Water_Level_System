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

class DeviceSettingDB():       
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM deviceSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def insert(deviceUID, deviceName, deviceVersion):
        data = [deviceUID, deviceName, deviceVersion]
        column = ['uid', 'name', 'version']
        for i in range(3):
            connection = sql.connect(host, database, username, password)
            query = "INSERT INTO deviceSettingDB (name, value) VALUES (%s, %s)"
            value = (column[(i)], data[(i)])
            action = sql.execute(connection, query, value)
        return action

    def update(deviceUID, deviceName, deviceVersion):
        data = [deviceUID, deviceName, deviceVersion]
        for i in range(1,4):
            connection = sql.connect(host, database, username, password)
            query = "UPDATE deviceSettingDB SET value = %s WHERE id = %s"
            value = (data[(i-1)], i)
            action = sql.execute(connection, query, value)
        return action
    
    def updateByName(name, value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE deviceSettingDB SET value=%s WHERE name=%s"
        value = (value, name)
        action = sql.execute(connection, query, value)
        return action
