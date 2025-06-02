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

class LogToleranceAlarmDB():
    def selectByAlarm(alarmId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * from logToleranceAlarmDB where alarmId=%s"
        value = (alarmId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(value, timestamp, alarmId):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO logToleranceAlarmDB (value, timestamp, alarmId) VALUES (%s, %s, %s)"
        value = (value, timestamp, alarmId)
        action = sql.execute(connection, query, value)
        return action

    def deleteByAlarmId(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logToleranceAlarmDB WHERE alarmId=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def deleteAll():
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM logToleranceAlarmDB"
        action = sql.execute(connection, query)
        connection = sql.connect(host, database, username, password)
        query = "TRUNCATE TABLE logToleranceAlarmDB"
        action = sql.executeOnly(connection, query)
        return action