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


class ActuatorParameterListDB():
    # New Query
    def checkExistingParam(actuator_list_id, param):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorParameterListDB WHERE actuator_list_id=%s AND parameter=%s"
        value = (actuator_list_id, param)
        fetchall = sql.selectWithInput(connection, query, value)
        isExist = len(fetchall)
        return isExist
    
    def selectFull():
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterListDB.id, actuatorParameterListDB.actuator_list_id, actuatorParameterListDB.name as name_parameter, actuatorParameterListDB.parameter, 
                actuatorParameterListDB.value, actuatorListDB.actuator_custom_id, actuatorListDB.name, actuatorListDB.server_value, actuatorListDB.last_server_value, 
                actuatorListDB.last_server_sync_at, actuatorListDB.last_action, actuatorListDB.last_action_value, actuatorListDB.last_action_at FROM actuatorParameterListDB 
                join actuatorListDB on actuatorParameterListDB.actuator_list_id=actuatorListDB.id"""
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorParameterListDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByActuatorListFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterListDB.id, actuatorParameterListDB.actuator_list_id, actuatorParameterListDB.name as name_parameter, actuatorParameterListDB.parameter, 
                actuatorParameterListDB.value, actuatorListDB.actuator_custom_id, actuatorListDB.name, actuatorListDB.server_value, actuatorListDB.last_server_value, 
                actuatorListDB.last_server_sync_at, actuatorListDB.last_action, actuatorListDB.last_action_value, actuatorListDB.last_action_at FROM actuatorParameterListDB 
                join actuatorListDB on actuatorParameterListDB.actuator_list_id=actuatorListDB.id where actuatorParameterListDB.actuator_list_id=%s"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByActuatorGroupNumberFull(number):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterListDB.id, actuatorParameterListDB.actuator_list_id, actuatorParameterListDB.name as name_parameter, actuatorParameterListDB.parameter, 
                actuatorParameterListDB.value, actuatorListDB.actuator_custom_id, actuatorListDB.name, actuatorListDB.server_value, actuatorListDB.last_server_value, 
                actuatorListDB.last_server_sync_at, actuatorListDB.last_action, actuatorListDB.last_action_value, actuatorListDB.last_action_at,  actuatorGroupDB.name as group_name, 
                actuatorGroupDB.number as group_number FROM actuatorParameterListDB join actuatorListDB on actuatorParameterListDB.actuator_list_id=actuatorListDB.id 
                join actuatorGroupDB on actuatorGroupDB.id=actuatorListDB.actuator_group_id where actuatorGroupDB.number=%s"""
        value = (number,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByActuatorGroupFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorParameterListDB.id, actuatorParameterListDB.actuator_list_id, actuatorParameterListDB.name as name_parameter, actuatorParameterListDB.parameter, 
                actuatorParameterListDB.value, actuatorListDB.actuator_custom_id, actuatorListDB.name, actuatorListDB.server_value, actuatorListDB.last_server_value, 
                actuatorListDB.last_server_sync_at, actuatorListDB.last_action, actuatorListDB.last_action_value, actuatorListDB.last_action_at FROM actuatorParameterListDB 
                join actuatorListDB on actuatorParameterListDB.actuator_list_id=actuatorListDB.id where actuatorListDB.actuator_group_id=%s"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id,actuator_list_id,name,param,value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuatorParameterListDB (id,actuator_list_id,name,parameter,value) VALUES (%s, %s, %s, %s, %s)"
        value = (id,actuator_list_id,name,param,value)
        action = sql.execute(connection, query, value)
        return action

    def update(actuator_list_id,name,param,value,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorParameterListDB set actuator_list_id=%s, name=%s, parameter=%s, value=%s WHERE id=%s"
        value = (actuator_list_id,name,param,value,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorParameterListDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def deleteByActId(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorParameterListDB WHERE actuator_list_id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    