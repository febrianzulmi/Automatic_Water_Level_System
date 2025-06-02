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

class IntervalRoutineLogDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = """SELECT id, (CAST(`interval` AS UNSIGNED) * CASE unit WHEN '1' THEN 1 WHEN '2' THEN 60 WHEN '3' THEN 3600 END) AS total_seconds,
            `interval`, unit, createdAt, updatedAt, state FROM intervalRoutineLogDB ORDER BY total_seconds ASC;"""
        fetchall = sql.selectNoInput(connection, query)
        return fetchall
    
    def selectEnable():
        connection = sql.connect(host, database, username, password)
        query = """SELECT id, (CAST(`interval` AS UNSIGNED) * CASE unit WHEN '1' THEN 1 WHEN '2' THEN 60 WHEN '3' THEN 3600 END) AS total_seconds,
                `interval`, unit, createdAt, updatedAt, state FROM intervalRoutineLogDB WHERE state ='1' ORDER BY total_seconds ASC;"""
        fetch = sql.selectNoInput(connection, query)
        return fetch

    def selectByIntervalAndUnit(interval, unit, state):
        connection = sql.connect(host, database, username, password)
        query = "SELECT `interval`, unit FROM intervalRoutineLogDB WHERE `interval`=%s AND unit=%s AND state=%s"
        value = (interval, unit, state)
        action = sql.selectWithInput(connection, query, value)
        return action
    

    def insert(interval, unit, state):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO intervalRoutineLogDB (`interval`, unit, state) VALUES (%s, %s, %s)"
        value = (interval, unit, state)
        action = sql.execute(connection, query, value)
        return action
    

    def deleteOne(idVal):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM intervalRoutineLogDB WHERE id=%s"
        value = (idVal,)
        action = sql.execute(connection, query, value)
        return action
    
    
    def update(interval, unit, state, idVal):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE intervalRoutineLogDB SET `interval`=%s, unit=%s, state=%s WHERE id=%s"
        value = (interval, unit, state, idVal)
        action = sql.execute(connection, query, value)
        return action
    