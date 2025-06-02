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

class CalibrateFormulaDB():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM calibrateFormulaDB"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM calibrateFormulaDB where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(name,sample):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO calibrateFormulaDB (name,sample) VALUES (%s,%s)"
        value = (name,sample)
        action = sql.execute(connection, query, value)
        return action

    def updateNameByFormula(name,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrateFormulaDB set name=%s WHERE id=%s"
        value = (name,id)
        action = sql.execute(connection, query, value)
        return action

    def updateSampleByFormula(sample,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrateFormulaDB set sample=%s WHERE id=%s"
        value = (sample,id)
        action = sql.execute(connection, query, value)
        return action

    def updateCoefByFormula(koef_a,koef_b,datetime,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE calibrateFormulaDB set koef_a=%s, koef_b=%s, calculate_time=%s WHERE id=%s"
        value = (koef_a,koef_b,datetime,id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM calibrateFormulaDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
