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

class ActuatorScheduleDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT actuatorScheduleDB.*, actuatorListDB.name FROM actuatorScheduleDB join actuatorListDB on actuatorScheduleDB.actuator_list_id=actuatorListDB.id"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByActuatorId(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorScheduleDB where actuator_list_id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByActuatorListFull(id):
        connection = sql.connect(host, database, username, password)
        query = """SELECT actuatorScheduleDB.*, actuatorListDB.name FROM actuatorScheduleDB JOIN actuatorListDB ON actuatorScheduleDB.actuator_list_id = actuatorListDB.id 
                    WHERE actuatorScheduleDB.actuator_list_id = %s"""
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorScheduleDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectBySchedule(id, day, time, value):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorScheduleDB where actuator_list_id=%s and day=%s and time=%s and value=%s"
        value = (id, day, time, value)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, actuator_list_id, day, time, value):
        connection = sql.connect(host, database, username, password)
        query = "INSERT actuatorScheduleDB (id, actuator_list_id, day, time, value) VALUES (%s, %s, %s, %s, %s)"
        value = (id, actuator_list_id, day, time, value)
        action = sql.execute(connection, query, value)
        return action

    def updateSchedule(id, day, time, value, id_sch):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorScheduleDB set actuator_list_id=%s, day=%s, time=%s, value=%s WHERE id=%s"
        value = (id, day, time, value, id_sch)
        action = sql.execute(connection, query, value)
        return action

    def updateState(state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorScheduleDB set state=%s WHERE id=%s"
        value = (state,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteById(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorScheduleDB WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByActId(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorScheduleDB WHERE actuator_list_id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
