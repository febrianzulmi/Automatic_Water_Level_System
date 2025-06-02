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

class ServerHttpAuthDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpAuthDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverHttpAuthDB where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateValueByName(value, name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverHttpAuthDB set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

    def deleteValueByName(name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverHttpAuthDB SET value = '' WHERE name = %s"
        value = (name,)
        action = sql.execute(connection, query, value)
        return action
    
