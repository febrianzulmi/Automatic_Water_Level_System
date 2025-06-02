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


class ActuatorGroupDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorGroupDB ORDER BY number"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorGroupDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByNumber(number):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorGroupDB where number = %s"
        value = (number,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM actuatorGroupDB where name = %s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, number, name, interval, unit):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO actuatorGroupDB (id, number, name, intervals, unit) VALUES (%s, %s, %s, %s, %s)"
        value = (id, number, name, interval, unit)
        action = sql.execute(connection, query, value)
        return action

    def update(number, name, interval, unit, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorGroupDB set number = %s, name = %s, intervals=%s, unit=%s WHERE id=%s"
        value = (number, name, interval, unit, id)
        action = sql.execute(connection, query, value)
        return action

    def updateService(service_id, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE actuatorGroupDB set service_id=%s WHERE id=%s"
        value = (service_id,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM actuatorGroupDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
