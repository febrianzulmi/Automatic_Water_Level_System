import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import sql
# sys.path.append('/home/connex/project/function')
# from generalFunction import generalFunction


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

class SensorListDB():
    # function yang baru menghilangkan kolom id di sensor_group
    # def select():
    #     connection = sql.connect(host, database, username, password)
    #     query = f"SELECT sensorListDB.*,  sensorGroupDB.id AS idGroup, sensorGroupDB.number, sensorGroupDB.name AS name_group, sensorGroupDB.intervals,  sensorGroupDB.unit, sensorGroupDB.frekuensi, sensorGroupDB.service_id, sensorGroupDB.enterAlarm, sensorGroupDB.exitAlarm, sensorGroupDB.errorAlarm FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id"
    #     fetchall = sql.selectNoInput(connection, query)
    #     return fetchall

    def select():
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT 
                sensorListDB.*,  
                sensorGroupDB.id AS idGroup, 
                sensorGroupDB.number, 
                sensorGroupDB.name AS name_group, 
                sensorGroupDB.intervals,  
                sensorGroupDB.unit, 
                sensorGroupDB.frekuensi, 
                sensorGroupDB.service_id, 
                sensorGroupDB.enterAlarm, 
                sensorGroupDB.exitAlarm, 
                sensorGroupDB.errorAlarm 
            FROM 
                sensorListDB 
            JOIN 
                sensorGroupDB 
            ON 
                sensorListDB.group_id = sensorGroupDB.id
            ORDER BY 
                sensorGroupDB.number ASC, 
                sensorListDB.oid ASC
        """
        fetchall = sql.selectNoInput(connection, query)
        return fetchall


    def selectByGroupFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT 
                sensorListDB.*, 
                sensorGroupDB.number, 
                sensorGroupDB.name AS name_group, 
                sensorGroupDB.intervals, 
                sensorGroupDB.unit AS unitInterval, 
                sensorGroupDB.frekuensi, 
                sensorGroupDB.service_id, 
                sensorGroupDB.enterAlarm, 
                sensorGroupDB.exitAlarm, 
                sensorGroupDB.errorAlarm 
            FROM 
                sensorListDB 
            JOIN 
                sensorGroupDB 
            ON 
                sensorListDB.group_id = sensorGroupDB.id 
            WHERE 
                sensorListDB.group_id = %s
            ORDER BY 
                sensorListDB.oid ASC
        """
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    
    def selectGroupByState(group_id, list_state, group_state):
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT
                sensorListDB.*,
                sensorGroupDB.number,
                sensorGroupDB.name AS name_group,
                sensorGroupDB.intervals,
                sensorGroupDB.unit as unitInterval,
                sensorGroupDB.frekuensi,
                sensorGroupDB.service_id,
                sensorGroupDB.enterAlarm,
                sensorGroupDB.exitAlarm,
                sensorGroupDB.errorAlarm
            FROM
                sensorListDB
            JOIN
                sensorGroupDB
            ON 
                sensorListDB.group_id=sensorGroupDB.id
            WHERE
                sensorListDB.group_id=%s and sensorListDB.state=%s and sensorGroupDB.state=%s
            ORDER BY 
                sensorListDB.oid ASC
            """
        value = (group_id, list_state, group_state)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall


    def selectByGroupNumberFull(group_id):
        connection = sql.connect(host, database, username, password)
        query = """
            SELECT 
                sensorListDB.*, 
                sensorGroupDB.number, 
                sensorGroupDB.name AS name_group, 
                sensorGroupDB.intervals, 
                sensorGroupDB.unit AS unitInterval, 
                sensorGroupDB.frekuensi, 
                sensorGroupDB.service_id, 
                sensorGroupDB.enterAlarm, 
                sensorGroupDB.exitAlarm, 
                sensorGroupDB.errorAlarm 
            FROM 
                sensorListDB 
            JOIN 
                sensorGroupDB 
            ON 
                sensorListDB.group_id = sensorGroupDB.id 
            WHERE 
                sensorGroupDB.number = %s
            ORDER BY 
                sensorListDB.oid ASC
        """
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectPriorityLog():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.*, sensorGroupDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.log=1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectPriorityMonitor():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.*, sensorGroupDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.monitor=1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectDailyLog():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.*, sensorGroupDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.log=2"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectDailyMonitor():
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.*, sensorGroupDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.monitor=2"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorListDB where sensor_id = %s"
        value = (sensor_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectValue(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value, timestamp FROM sensorListDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorListDB where id = %s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    

    def selectByAlarmId(alarmId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorListDB where alarmId1=%s or alarmId2=%s"
        value = (alarmId,alarmId)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectCalibrateById(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT calibrate, formula FROM sensorListDB where id=%s"
        value=(id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByGroup(id_group):
        connection = sql.connect(host, database, username, password)
        query = "SELECT id, sensor_id, name, oid_tipe FROM sensorListDB where group_id=%s ORDER BY oid ASC"
        value=(id_group,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    

    def selectByGroupOID(group, oid):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorListDB where group_id = %s and oid = %s"
        value = (group, oid)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByGroupState(group, state):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM sensorListDB where group_id = %s and state = %s ORDER BY oid ASC"
        value = (group, state)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectByRoutineMonitorInterval(routineMonitorIntervalId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.monitor=%s AND sensorListDB.state='1' AND sensorGroupDB.state='1'"
        value = (routineMonitorIntervalId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectByLogInterval(logIntervalId):
        connection = sql.connect(host, database, username, password)
        query = "SELECT sensorListDB.* FROM sensorListDB join sensorGroupDB on sensorListDB.group_id=sensorGroupDB.id where sensorListDB.log=%s AND sensorListDB.state='1' AND sensorGroupDB.state='1'"
        value = (logIntervalId,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall
    
    def selectMaxOidByGroup(group_id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT MAX(oid) AS max_oid FROM sensorListDB WHERE group_id = %s"
        value = (group_id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(id, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, state):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO sensorListDB (id, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, state) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (id, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, state)
        action = sql.execute(connection, query, value)
        return action
    
    def batchInsertSensors(extension_id, ports, port_config, deviceState, generalFunction):
        connection = sql.connect(host, database, username, password)
        query = """
            INSERT INTO sensorListDB 
            (id, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = []
        group_id = "PGS-DED30"

        oid_max_result = SensorListDB.selectMaxOidByGroup(group_id)
        oid = int(oid_max_result[0]["max_oid"]) if oid_max_result and oid_max_result[0]["max_oid"] else 0

        for port_number, port_type in enumerate(ports, start=1):
            if port_type in port_config:
                for sensor_suffix, sensor_name in port_config[port_type]:
                    id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                    sensor_id = f"{sensor_suffix}P{port_number}Ext{extension_id}"
                    name = f"{sensor_name} Port {port_number} Extension {extension_id}"
                    oid += 1
                    values.append((
                        id_sensor, sensor_id, oid, group_id, name, 0, 0, 0, 0, 0, deviceState
                    ))

        action = sql.executeMany(connection, query, values)
        return action
    
    def insertSyncronizerPowerExt(number, deviceState, total_port, generalFunction):
        connection = sql.connect(host, database, username, password)
        group_id = "PGS-44539"
        
        query = """
            INSERT INTO sensorListDB 
            (id, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = []
        oid_max_result = SensorListDB.selectMaxOidByGroup(group_id)
        oid = int(oid_max_result[0]["max_oid"]) if oid_max_result and oid_max_result[0]["max_oid"] else 0
        oid += 1
        sensor_id = F"acVoltageExt{number}"
        name = F"AC Voltage Extension {number}"
        id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
        values.append((id_sensor, sensor_id, oid, group_id, name, 0, 0, 0, 0, 0, deviceState))

        for i in range(1, total_port+1):
            oid += 1
            sensor_id = F"acCurrent{i}Ext{number}"
            name = F"AC Current {i} Extension {number}"
            id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
            values.append((id_sensor, sensor_id, oid, group_id, name, 0, 0, 0, 0, 0, deviceState))
        
        action = sql.executeMany(connection, query, values)
        return action



    def update(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set sensor_id=%s, oid=%s, group_id=%s, name=%s, calibrate=%s, formula=%s, oid_tipe=%s, monitor=%s, log=%s, alarm=%s, min=%s, max=%s, alarm_type=%s ,state=%s WHERE id=%s"
        value = (sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id)
        action = sql.execute(connection, query, value)
        return action

    def updateParam(name, alarm, sensor_max, sensor_min, unit, alarm_type, last_sync, sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set name=%s, alarm=%s, max=%s, min=%s, unit=%s, alarm_type=%s, last_sync=%s WHERE sensor_id=%s"
        value = (name, alarm, sensor_max, sensor_min, unit, alarm_type, last_sync, sensor_id)
        action = sql.execute(connection, query, value)
        return action
    

    def updateValue(value,timestamp,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set value=%s, timestamp=%s WHERE id=%s"
        value = (value,timestamp,id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateState(state, timestamp, sensor_id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set state=%s, timestamp=%s WHERE sensor_id=%s"
        value = (state, timestamp, sensor_id)
        action = sql.execute(connection, query, value)
        return action

    def updateAlarmId(alarmId, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set alarmId1=%s WHERE sensor_id=%s"
        value = (alarmId, id)
        action = sql.execute(connection, query, value)
        return action

    def updateLastAlarmId(alarmId, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set alarmId2=%s WHERE sensor_id=%s"
        value = (alarmId, id)
        action = sql.execute(connection, query, value)
        return action

    def updateCondition(condition, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set conditions=%s WHERE sensor_id=%s"
        value = (condition,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifState(notif_state, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set notif_state=%s WHERE sensor_id=%s"
        value = (notif_state,id)
        action = sql.execute(connection, query, value)
        return action

    def updateNotifCount(notif_count, notif_time, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set notif_count=%s, notif_time=%s WHERE sensor_id=%s"
        value = (notif_count, notif_time, id)
        action = sql.execute(connection, query, value)
        return action

    def updateResetAlarm(id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB set notif_state=0, notif_count= 0, notif_time=0, conditions='Alarm Inactive', alarmId1='', alarmId2='' WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
    
    def updateStateByMonitorId(state, monitor_id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB SET state = %s WHERE monitor = %s"
        value = (state, monitor_id)
        action = sql.execute(connection, query, value)
        return action
    
    def updateStateByLogId(state, log_id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE sensorListDB SET state = %s WHERE log = %s"
        value = (state, log_id)
        action = sql.execute(connection, query, value)
        return action

    def deleteOne(id_data):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM sensorListDB WHERE id=%s"
        value = (id_data,)
        action = sql.execute(connection, query, value)
        return action
    
    def batchDeleteSensors(extension_id, ports, port_config):
        connection = sql.connect(host, database, username, password)
        sensor_ids = []

        for port_number, port_type in enumerate(ports, start=1):
            if port_type in port_config:
                for sensor_suffix, _ in port_config[port_type]:
                    sensor_id = f"{sensor_suffix}P{port_number}Ext{extension_id}"
                    sensor_ids.append(sensor_id)

        query = "DELETE FROM sensorListDB WHERE sensor_id IN ({})".format(",".join(["%s"] * len(sensor_ids)))
        action = sql.execute(connection, query, tuple(sensor_ids))
        return action
    
    def deleteSyncronizerPowerExt(number, total_port):
        connection = sql.connect(host, database, username, password)

        sensor_ids = []
        sensor_id = F"acVoltageExt{number}"
        sensor_ids.append(sensor_id)

        for i in range(1, total_port+1):
            sensor_id = F"acCurrent{i}Ext{number}"
            sensor_ids.append(sensor_id)
        
        query = "DELETE FROM sensorListDB WHERE sensor_id IN ({})".format(",".join(["%s"] * len(sensor_ids)))
        action = sql.execute(connection, query, tuple(sensor_ids))
        return action