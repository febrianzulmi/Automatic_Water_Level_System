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


class ActuatorParameterGroupDB():
    # New Query
    def checkExistingParam(actuator_group_id, param):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorParameterGroupDB WHERE actuator_group_id=%s AND parameter=%s"
        value = (actuator_group_id, param)
        fetchall = sql.selectWithInput(connection, query, value)
        isExist = len(fetchall)
        return isExist
    
    def selectFull():
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterGroupDB.id, actuatorParameterGroupDB.actuator_group_id, actuatorParameterGroupDB.name as name_parameter, actuatorParameterGroupDB.parameter, 
                actuatorParameterGroupDB.value, actuatorGroupDB.number, actuatorGroupDB.name, actuatorGroupDB.intervals, actuatorGroupDB.unit FROM actuatorParameterGroupDB 
                join actuatorGroupDB on actuatorParameterGroupDB.actuator_group_id=actuatorGroupDB.id"""
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorParameterGroupDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByActuatorGroupFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterGroupDB.id, actuatorParameterGroupDB.actuator_group_id, actuatorParameterGroupDB.name as name_parameter, actuatorParameterGroupDB.parameter, 
                actuatorParameterGroupDB.value, actuatorGroupDB.number, actuatorGroupDB.name, actuatorGroupDB.intervals, actuatorGroupDB.unit FROM actuatorParameterGroupDB join 
                actuatorGroupDB on actuatorParameterGroupDB.actuator_group_id=actuatorGroupDB.id where actuatorParameterGroupDB.actuator_group_id=%s"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByActuatorGroupNumberFull(number):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterGroupDB.id, actuatorParameterGroupDB.actuator_group_id, actuatorParameterGroupDB.name as name_parameter, actuatorParameterGroupDB.parameter, 
                actuatorParameterGroupDB.value, actuatorGroupDB.number, actuatorGroupDB.name, actuatorGroupDB.intervals, actuatorGroupDB.unit FROM actuatorParameterGroupDB join 
                actuatorGroupDB on actuatorParameterGroupDB.actuator_group_id=actuatorGroupDB.id where actuatorGroupDB.number=%s"""
        value = (number,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, actuator_group_id, name, param, value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuatorParameterGroupDB (id, actuator_group_id, name, parameter, value) VALUES (%s, %s, %s, %s, %s)"
        value = (id, actuator_group_id, name, param, value)
        action = sql.execute(connection, query, value)
        return action

    def update(actuator_group_id,name,param,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorParameterGroupDB set actuator_group_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (actuator_group_id,name,param,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorParameterGroupDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteByActuatorGroup(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorParameterGroupDB WHERE actuator_group_id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    