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

class SystemServiceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM systemServiceDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    
    def insert(name,service,enable,last_run,since):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO systemServiceDB (name,service,enable,state,last_run,since) VALUES (%s, %s, %s, %s, %s, %s)"
        value = (name,service,enable,'-',last_run,since)
        action = sql.execute(connection, query, value)
        return action
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM systemServiceDB where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def updateStatusByName(state,times,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set state=%s, last_update=%s WHERE name=%s"
        value = (state,times,name)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceStateById(state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set state=%s WHERE id=%s"
        value = (state, id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceBootById(boot, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set enable=%s WHERE id=%s"
        value = (boot, id)
        action = sql.execute(connection, query, value)
        return action

    def updateStatusByName(state,times,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set state=%s, last_update=%s WHERE name=%s"
        value = (state,times,name)
        action = sql.execute(connection, query, value)
        return action
    
    def updateServiceByName(service,enable,last_run,since,name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set service=%s, enable=%s, last_run=%s, since=%s WHERE name=%s"
        value = (service,enable,last_run,since,name)
        action = sql.execute(connection, query, value)
        return action
    
    def updateName(last_name, last_update, name):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE systemServiceDB set name=%s, last_update=%s WHERE name=%s"
        value = (name, last_update, last_name)
        action = sql.execute(connection, query, value)
        return action

    def deleteByName(name):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM systemServiceDB WHERE name=%s"
        value = (name,)
        action = sql.execute(connection, query, value)
        return action
