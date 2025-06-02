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

class ServerMqttDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverMqttDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    

    def selectByParameter(parameter):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverMqttDB WHERE parameter = %s"
        value = (parameter,)
        action = sql.selectWithInput(connection, query, value)
        return action
    

    def insert(name, parameter, api):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO serverMqttDB (name, parameter, data) VALUES (%s, %s, %s)"
        value = (name, parameter, api)
        action = sql.execute(connection, query, value)
        return action
    

    def update(name, parameter, topic, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverMqttDB SET name=%s, parameter=%s, data=%s WHERE id=%s"
        value = (name, parameter, topic, id)
        action = sql.execute(connection, query, value)
        return action
    
    
    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM serverMqttDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    
