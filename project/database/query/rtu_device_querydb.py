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

class RtuDeviceDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuDeviceDB ORDER BY number"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall


    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuDeviceDB WHERE id = %s"
        value = (id)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def selectByNumber(number):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuDeviceDB WHERE number = %s"
        value = (number,)
        action = sql.selectWithInput(connection, query, value)
        return action
    
    def selectBySlaveid(slave_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM rtuDeviceDB WHERE slave_id = %s"
        value = (slave_id,)
        action = sql.selectWithInput(connection, query, value)
        return action


    def insert(id, number, name, slave_id, state):
        connection = sql.connect(host, database, username, password)
        query = """INSERT INTO rtuDeviceDB 
                   (id, number, name, slave_id, state)
                   VALUES (%s, %s, %s, %s, %s)"""
        value = (id, number, name, slave_id, state)
        action = sql.execute(connection, query, value)
        return action


    def update(id, number, name, slave_id, state):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE rtuDeviceDB 
                   SET number=%s, name=%s, slave_id=%s, state=%s 
                   WHERE id=%s"""
        value = (number, name, slave_id, state, id)
        action = sql.execute(connection, query, value) 
        return action


    def updateById(id, name, custom_id, address, length, datatype, divider, type_sensor,
                   type_control, unit, monitoring, log, state):
        connection = sql.connect(host, database, username, password)
        query = """UPDATE rtuDeviceDB 
                   SET name=%s, custom_id=%s, address=%s, length=%s, datatype=%s, divider=%s, type=%s,
                   type_control=%s, unit=%s, monitoring=%s, log=%s, state=%s, updated_at=NOW()
                   WHERE id=%s"""
        value = (name, custom_id, address, length, datatype, divider, type_sensor,
                 type_control, unit, monitoring, log, state, id)
        action = sql.execute(connection, query, value)
        return action


    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM rtuDeviceDB WHERE id = %s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action