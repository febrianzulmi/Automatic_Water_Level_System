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

class RtuParameterDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuParameterDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall


    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuParameterDB WHERE id = %s"
        value = (id,)
        action = sql.selectWithInput(connection, query, value)
        return action


    def insert(id, name, custom_id, address, length, datatype, divider, type_sensor,
               type_control, unit, monitoring, log, state, created_at):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO rtuParameterDB 
                   (id, name, custom_id, address, length, datatype, divider, type,
                   type_control, unit, monitoring, log, state, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        value = (id, name, custom_id, address, length, datatype, divider, type_sensor,
                 type_control, unit, monitoring, log, state, created_at)
        action = sql.execute(connection, query, value)
        return action


    def update(id, name, custom_id, address, length, datatype, divider, type_sensor,
               type_control, unit, monitoring, log, state, updated_at):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE rtuParameterDB 
                   SET name=%s, custom_id=%s, address=%s, length=%s, datatype=%s, divider=%s, type=%s,
                   type_control=%s, unit=%s, monitoring=%s, log=%s, state=%s, updated_at=%s
                   WHERE id=%s"""
        value = (name, custom_id, address, length, datatype, divider, type_sensor,
                 type_control, unit, monitoring, log, state, updated_at, id)
        action = sql.execute(connection, query, value) 
        return action


    def updateById(id, name, custom_id, address, length, datatype, divider, type_sensor,
                   type_control, unit, monitoring, log, state):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE rtuParameterDB 
                   SET name=%s, custom_id=%s, address=%s, length=%s, datatype=%s, divider=%s, type=%s,
                   type_control=%s, unit=%s, monitoring=%s, log=%s, state=%s, updated_at=NOW()
                   WHERE id=%s"""
        value = (name, custom_id, address, length, datatype, divider, type_sensor,
                 type_control, unit, monitoring, log, state, id)
        action = sql.execute(connection, query, value)
        return action


    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM rtuParameterDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    