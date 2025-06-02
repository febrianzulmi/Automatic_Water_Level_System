import sys

sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SensorGroupDB, SensorParameterGroupDB, SensorParameterListDB
from sql_connex import snmp
sys.path.append("/home/connex/project/function")
from serviceProjectFunction import ServiceProjectFunction

class CollectDataSensorFunction():
    def handleValueType(oid_type):
        if oid_type == 0:
            value = '0'
        else:
            value = 'N/A'
        return value

    def handleValueService(group_id, oid_type, value):
        serviceName = "sensor" + str(group_id)
        service, state_sensor, last_update = ServiceProjectFunction.getServiceInfo(serviceName)
        service = "active"
        if service == "active":
            if 'Success' not in state_sensor:
                value = CollectDataSensorFunction.handleValueType(oid_type)
        else:
            value = CollectDataSensorFunction.handleValueType(oid_type)
        return value

    def handleValueDB(value, oid_type):
        if value == None:
            value = CollectDataSensorFunction.handleValueType(oid_type)
        return value

    def initiateSensor():
        dataSensor = {}
        dataSensor['id'], dataSensor['sensorId'], dataSensor['groupId'], dataSensor['sensorName'], dataSensor['sensorOid'] = [], [], [], [], []
        dataSensor['sensorValue'], dataSensor['sensorValueTime'], dataSensor['sensorAlarm'], dataSensor['sensorAlarmType'], dataSensor['sensorMin'] = [], [], [], [], []
        dataSensor['sensorMax'], dataSensor['sensorUnit'], dataSensor['sensorDatatype'], dataSensor['sensorCalibration'] = [], [], [], []
        dataSensor['sensorFormula'], dataSensor['sensorMonitor'], dataSensor['sensorLog'], dataSensor['sensorCondition'] = [], [], [], []
        dataSensor['sensorLastSync'], dataSensor['sensorNotifState'], dataSensor['sensorNotifCount'], dataSensor['sensorNotifTime'] = [], [], [], []
        dataSensor['sensorAlarmId'], dataSensor['sensorLastAlarmId'] = [], []
        return dataSensor

    def assignSensor(i, sensors, dataSensor):
        dataSensor['id'].append(sensors[i]['id'])
        dataSensor['sensorId'].append(sensors[i]['sensor_id'])
        dataSensor['groupId'].append(sensors[i]['group_id'])
        dataSensor['sensorOid'].append(sensors[i]['oid'])
        dataSensor['sensorName'].append(sensors[i]['name'])
        value = CollectDataSensorFunction.handleValueDB(sensors[i]['value'], sensors[i]['oid_tipe'])
        dataSensor['sensorValue'].append(value)
        dataSensor['sensorValueTime'].append(sensors[i]['timestamp'])
        dataSensor['sensorCalibration'].append(sensors[i]['calibrate'])
        dataSensor['sensorFormula'].append(sensors[i]['formula'])
        dataSensor['sensorAlarm'].append(sensors[i]['alarm'])
        dataSensor['sensorMax'].append(sensors[i]['max'])
        dataSensor['sensorMin'].append(sensors[i]['min'])
        dataSensor['sensorUnit'].append(sensors[i]['unit'])
        dataSensor['sensorDatatype'].append(sensors[i]['oid_tipe'])
        dataSensor['sensorMonitor'].append(sensors[i]['monitor'])
        dataSensor['sensorLog'].append(sensors[i]['log'])
        dataSensor['sensorAlarmType'].append(sensors[i]['alarm_type'])
        dataSensor['sensorLastSync'].append(sensors[i]['last_sync'])
        dataSensor['sensorCondition'].append(sensors[i]['conditions'])
        dataSensor['sensorNotifState'].append(sensors[i]['notif_state'])
        dataSensor['sensorNotifCount'].append(sensors[i]['notif_count'])
        dataSensor['sensorNotifTime'].append(sensors[i]['notif_time'])
        dataSensor['sensorAlarmId'].append(sensors[i]['alarmId1'])
        dataSensor['sensorLastAlarmId'].append(sensors[i]['alarmId2'])
        return dataSensor

    def byGroup(groupId):
        sensors  = SensorListDB.selectByGroupFull(groupId)
        dataSensor = CollectDataSensorFunction.initiateSensor()
        if len(sensors) > 0:
            for i in range(len(sensors)):
                dataSensor = CollectDataSensorFunction.assignSensor(i, sensors, dataSensor)
        dataSensor['numSensor'] = len(sensors)
        return dataSensor
    

    def byGroupState(group_id):
        sensors  = SensorListDB.selectGroupByState(group_id, "1", "1")
        dataSensor = CollectDataSensorFunction.initiateSensor()
        if len(sensors) > 0:
            for i in range(len(sensors)):
                dataSensor = CollectDataSensorFunction.assignSensor(i, sensors, dataSensor)
        dataSensor['numSensor'] = len(sensors)
        return dataSensor

    def all():
        sensors  = SensorListDB.select()
        dataSensor = CollectDataSensorFunction.initiateSensor() # initial zero value
        if len(sensors) > 0:
            for i in range(len(sensors)):
                dataSensor = CollectDataSensorFunction.assignSensor(i, sensors, dataSensor) # append value
        dataSensor['numSensor'] = len(sensors)
        return dataSensor

    def byRoutineMonitorInterval(routineMonitorIntervalId):
        sensors  = SensorListDB.selectByRoutineMonitorInterval(routineMonitorIntervalId)
        dataSensor = CollectDataSensorFunction.initiateSensor()
        if len(sensors) > 0:
            for i in range(len(sensors)):
                dataSensor = CollectDataSensorFunction.assignSensor(i, sensors, dataSensor)
        dataSensor['numSensor'] = len(sensors)
        return dataSensor

    def byLogInterval(logIntervalId):
        sensors  = SensorListDB.selectByLogInterval(logIntervalId)
        dataSensor = CollectDataSensorFunction.initiateSensor()
        if len(sensors) > 0:
            for i in range(len(sensors)):
                dataSensor = CollectDataSensorFunction.assignSensor(i, sensors, dataSensor)
        dataSensor['numSensor'] = len(sensors)
        return dataSensor

    def getSensorSetting(group_id):
        try:
            get = SensorGroupDB.selectOne(group_id)
            if len(get) > 0:
                for i in get:
                    interval = i['intervals']
                    unit = i['unit']
                    if unit == 1:
                        interval = interval
                    elif unit == 2:
                        interval = interval * 60
                    else:
                        interval = interval * 3600
                    frekuensi = i['frekuensi']
                    enterAlarm = i['enterAlarm']
                    exitAlarm = i['exitAlarm']
                    errorAlarm = i['errorAlarm']
            else:
                interval = 60 #in Seconds
                frekuensi = 1
                enterAlarm = 1
                exitAlarm = 1
                errorAlarm = 300
        except Exception as e:
            interval = 60 #in Seconds
            frekuensi = 1
            enterAlarm = 1
            exitAlarm = 1
            errorAlarm = 300
        sensorSetting = {'interval': interval, 'frekuensi': frekuensi, 'enterAlarm': enterAlarm, 'exitAlarm': exitAlarm, 'errorAlarm': errorAlarm}  
        return sensorSetting

    def getParameterGroupSensor(group_id):
        parameterData = SensorParameterGroupDB.selectByGroupSensor(group_id)
        if len(parameterData) > 0:
            result = {}
            for item in parameterData:
                result[item['parameter']] = item['value']
        else :
            result = {}
        return result

    def getParameterListSensor(group_id):
        parameterData = SensorParameterListDB.selectParameterListSensor(group_id)   
        if len(parameterData) > 0:
            result = {}
            for item in parameterData:
                sensor_id = item['sensor_id']
                parameter = item['parameter']
                value = item['value']
                if sensor_id not in result:
                    result[sensor_id] = {}
                result[sensor_id][parameter] = value
        else :
            result = {}   
        return result