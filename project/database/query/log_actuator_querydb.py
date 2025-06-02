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

class LogActuatorDB():
    def selectAll():
        connection = sql.connect(host, database, username, password)
        query = "SELECT logActuatorDB.*, actuatorListDB.actuator_custom_id, actuatorListDB.name FROM logActuatorDB JOIN actuatorListDB ON logActuatorDB.actuator_list_id=actuatorListDB.id ORDER BY logActuatorDB.action_at DESC"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "SELECT logActuatorDB.*, actuatorListDB.actuator_custom_id, actuatorListDB.name FROM logActuatorDB JOIN actuatorListDB ON logActuatorDB.actuator_list_id=actuatorListDB.id WHERE logActuatorDB.action_at BETWEEN %s AND %s ORDER by logActuatorDB.action_at DESC"
        value = (datetime1,datetime2)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(actuator_list_id,value,action,action_at):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logActuatorDB (actuator_list_id,value,action,action_at) VALUES (%s, %s, %s, %s)"
        value = (actuator_list_id,value,action,action_at)
        action = sql.execute(connection, query, value)
        return action

    def updateAll(actuator_list_id,value,action,action_at,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logActuatorDB set actuator_list_id=%s, value=%s, action=%s, action_at=%s WHERE id=%s"
        value = (actuator_list_id,value,action,action_at,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifWhatsapp(id_log):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logActuatorDB set notif_wa=1 WHERE id=%s"
        value = (id_log,)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifEmail(id_log):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE logActuatorDB set notif_email=1 WHERE id=%s"
        value = (id_log,)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logActuatorDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action

    def deleteByTime(datetime1,datetime2):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logActuatorDB WHERE action_at BETWEEN %s AND %s"
        value = (datetime1,datetime2)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logActuatorDB"
        action = sql.execute(connection, query)
        return action
