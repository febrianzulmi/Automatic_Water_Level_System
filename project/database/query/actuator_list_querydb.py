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


class ActuatorListDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorListDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectFull():
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorGroupDB.name as actuator_group_name, actuatorGroupDB.number as actuator_group_number, actuatorListDB.* FROM actuatorListDB join 
                actuatorGroupDB on actuatorListDB.actuator_group_id=actuatorGroupDB.id ORDER by actuatorGroupDB.number ASC, actuatorListDB.created_at ASC"""
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByActId(actuator_custom_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorListDB where actuator_custom_id = %s"
        value = (actuator_custom_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorListDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByActuatorGroupFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorGroupDB.name as actuator_group_name, actuatorListDB.* FROM actuatorListDB join actuatorGroupDB on actuatorListDB.actuator_group_id=actuatorGroupDB.id
                where actuatorListDB.actuator_group_id=%s ORDER by actuatorGroupDB.number ASC"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByActuatorGroupNumberFull(number):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorGroupDB.name as actuator_group_name, actuatorListDB.* FROM actuatorListDB join actuatorGroupDB on actuatorListDB.actuator_group_id=actuatorGroupDB.id
                where actuatorGroupDB.number=%s ORDER by actuatorGroupDB.number ASC"""
        value = (number,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, actuator_group_id, name, actuator_custom_id, type_actuator):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuatorListDB (id, actuator_group_id, name, actuator_custom_id, type_actuator) VALUES (%s, %s, %s, %s, %s)"
        value = (id, actuator_group_id, name, actuator_custom_id, type_actuator)
        action = sql.execute(connection, query, value)
        return action

    def update(actuator_group_id, name, actuator_custom_id, type_actuator, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorListDB set actuator_group_id = %s, name = %s, actuator_custom_id=%s, type_actuator=%s WHERE id=%s"
        value = (actuator_group_id, name, actuator_custom_id, type_actuator, id)
        action = sql.execute(connection, query, value)
        return action

    def updateParam(name, value, timestamp, schedule, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorListDB set name=%s, server_value=%s, server_sync_at=%s, schedule=%s WHERE id=%s"
        value = (name, value, timestamp, schedule, id)
        action = sql.execute(connection, query, value)
        return action

    def updateStatus(status,times,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorListDB set status=%s, last_time=%s WHERE id=%s"
        value = (status,times,id)
        action = sql.execute(connection, query, value)
        return action

    def updateAction(value,action,times,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorListDB set last_action_value=%s, last_action=%s, last_action_at=%s WHERE id=%s"
        value = (value,action,times,id)
        action = sql.execute(connection, query, value)
        return action

    def updateLastServer(value,times,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorListDB set last_server_value=%s, last_server_sync_at=%s WHERE id=%s"
        value = (value,times,id)
        action = sql.execute(connection, query, value)
        return action    

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorListDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
