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

class ServerSettingDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverSettingDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    

    def selectByServer(server):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM serverSettingDB WHERE server = %s"
        value = (server,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    
    def updateByName(domainAddress, ipAddress, port, user, passw, server):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE serverSettingDB SET domainAddress=%s, ipAddress=%s, port=%s, username=%s, password=%s WHERE server=%s"
        value = (domainAddress, ipAddress, port, user, passw, server)
        action = sql.execute(connection, query, value)
        return action
    
