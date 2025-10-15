path = "/home/connex"

import datetime 
import json
import sys

sys.path.append(f"{path}/library")
from SynapsisLibrary import packData, times
sys.path.append(f"{path}/project/database")
from query_project_db import SensorListDB, LogSensorDB, LogMonitoringDB, LogAlarmDB, LogToleranceAlarmDB, SystemServiceDB
sys.path.append(f"{path}/project/function")
from generalFunction import generalFunction
from httpProtocolFunction import httpProtocolFunction
from mqttProtocolFunction import mqttProtocolFunction
from serverFunction import serverFunction
from dbFunction import dbFunction
from sensorFunction import SensorFunction


class monitoringFunction():
    def logNotifMonitorData(condition, notifData, timestamp):
        timestampFirst = ''
        if condition == 'Normal':
            sensorPack = packData.sensorPack(notifData['normalSensorID'], notifData['normalSensorValue'], len(notifData['normalSensorID']))
            if len(notifData.get('normalSensorTimestamp', [])) > 0:
                timestampFirst = notifData['normalSensorTimestamp'][0]
            conditionNum = 1
        elif condition == 'Alarm Min':
            sensorPack = packData.sensorPack(notifData['minSensorID'], notifData['minSensorValue'], len(notifData['minSensorID']))
            if len(notifData.get('minSensorTimestamp', [])) > 0:
                timestampFirst = notifData['minSensorTimestamp'][0]
            conditionNum = 2
        elif condition == 'Alarm Max':
            sensorPack = packData.sensorPack(notifData['maxSensorID'], notifData['maxSensorValue'], len(notifData['maxSensorID']))
            if len(notifData.get('maxSensorTimestamp', [])) > 0:
                timestampFirst = notifData['maxSensorTimestamp'][0]
            conditionNum = 3
        elif condition == 'Alarm Error':
            sensorPack = packData.sensorPack(notifData['errorSensorID'], notifData['errorSensorValue'], len(notifData['errorSensorID']))
            if len(notifData.get('errorSensorTimestamp', [])) > 0:
                timestampFirst = notifData['errorSensorTimestamp'][0]
            conditionNum = 4
        else:
            return notifData
        if timestampFirst == '':
            timestampFirst = timestamp
        statusCode, statusBuffer, typeMonitor, attempt = "-", 3, conditionNum, 0
        LogMonitoringDB.insert(json.dumps(sensorPack), statusCode, statusBuffer, timestampFirst, typeMonitor, attempt)
        return notifData

    def sendAllSensorStatusLevel(notifData, dataSensor, timestamp):
        normalSensors, minSensors, maxSensors, errorSensors = [], [], [], []
        for i in range(dataSensor['numSensor']):
            sensorId = dataSensor['sensorId'][i]
            sensorValue = dataSensor['sensorValue'][i]
            condition = notifData['condition'][i]
            if condition in ['Normal', 'Alarm Inactive']:
                normalSensors.append({'id': sensorId, 'value': sensorValue, 'timestamp': timestamp})
            elif condition in ['Alarm Min', 'Alarm Min Tolerance']:
                minSensors.append({'id': sensorId, 'value': sensorValue, 'timestamp': timestamp})
            elif condition in ['Alarm Max', 'Alarm Max Tolerance']:
                maxSensors.append({'id': sensorId, 'value': sensorValue, 'timestamp': timestamp})
            elif condition in ['Alarm Error', 'Alarm Error Tolerance']:
                errorSensors.append({'id': sensorId, 'value': sensorValue, 'timestamp': timestamp})

        if len(normalSensors) > 0:
            notifData['normalSensorID'] = [s['id'] for s in normalSensors]
            notifData['normalSensorValue'] = [s['value'] for s in normalSensors]
            notifData['normalSensorTimestamp'] = [s['timestamp'] for s in normalSensors]
            notifData = monitoringFunction.logNotifMonitorData('Normal', notifData, timestamp)
            notifData['normalSensorID'], notifData['normalSensorValue'], notifData['normalSensorTimestamp'] = [], [], []

        if len(minSensors) > 0:
            notifData['minSensorID'] = [s['id'] for s in minSensors]
            notifData['minSensorValue'] = [s['value'] for s in minSensors]
            notifData['minSensorTimestamp'] = [s['timestamp'] for s in minSensors]
            notifData = monitoringFunction.logNotifMonitorData('Alarm Min', notifData, timestamp)
            notifData['minSensorID'], notifData['minSensorValue'], notifData['minSensorTimestamp'] = [], [], []

        if len(maxSensors) > 0:
            notifData['maxSensorID'] = [s['id'] for s in maxSensors]
            notifData['maxSensorValue'] = [s['value'] for s in maxSensors]
            notifData['maxSensorTimestamp'] = [s['timestamp'] for s in maxSensors]
            notifData = monitoringFunction.logNotifMonitorData('Alarm Max', notifData, timestamp)
            notifData['maxSensorID'], notifData['maxSensorValue'], notifData['maxSensorTimestamp'] = [], [], []

        if len(errorSensors) > 0:
            notifData['errorSensorID'] = [s['id'] for s in errorSensors]
            notifData['errorSensorValue'] = [s['value'] for s in errorSensors]
            notifData['errorSensorTimestamp'] = [s['timestamp'] for s in errorSensors]
            notifData = monitoringFunction.logNotifMonitorData('Alarm Error', notifData, timestamp)
            notifData['errorSensorID'], notifData['errorSensorValue'], notifData['errorSensorTimestamp'] = [], [], []

        return notifData
    def runMonitoring(num, intervalId, intervalData, globalVariable):
        projectData = generalFunction.getProjectSetting()
        timestamp = times.getDatetime()
        timestampUTC = times.convertToUTC(timestamp) 
        sensorData = SensorFunction.CollectDataSensorFunction.byRoutineMonitorInterval(intervalId[num])
        
        if sensorData['numSensor'] > 0:
            deviceSetting = dbFunction.getDeviceSetting()
            serverConfig = serverFunction.getServerConfig()
            # Pisahkan juga berdasarkan kondisi jika tersedia
            alarmNormalId, alarmNormalValue = [], []
            alarmMinId, alarmMinValue = [], []
            alarmMaxId, alarmMaxValue = [], []
            routineId, routineValue = [], []
            if 'sensorCondition' in sensorData:
                for x in range(sensorData['numSensor']):
                    if sensorData['sensorCondition'][x] != 'Alarm Inactive':
                        if sensorData['sensorCondition'][x] == 'Normal':
                            alarmNormalValue.append(sensorData['sensorValue'][x])
                            alarmNormalId.append(sensorData['sensorId'][x])
                        elif sensorData['sensorCondition'][x] == 'Alarm Min':
                            alarmMinValue.append(sensorData['sensorValue'][x])
                            alarmMinId.append(sensorData['sensorId'][x])
                        elif sensorData['sensorCondition'][x] == 'Alarm Max':
                            alarmMaxValue.append(sensorData['sensorValue'][x])
                            alarmMaxId.append(sensorData['sensorId'][x])
                    else:
                        routineId.append(sensorData['sensorId'][x])
                        routineValue.append(sensorData['sensorValue'][x])
            else:
                routineId = sensorData['sensorId']
                routineValue = sensorData['sensorValue']
            
            protocolMonitoring = projectData['protocol'] # 1: HTTP, 2: MQTT, 3: SNMP

            # Mode pengiriman alarm agar tidak duplikat dengan service sensor
            feature_setting = dbFunction.getFeatureSetting()
            alarm_mode = str(feature_setting.get('alarmMonitorMode', 'routine')).lower()
            colorLogService = ''

            # Bangun paket ROUTINE hanya berisi sensor non-aktif alarm
            if 'sensorCondition' in sensorData:
                routine_pack_ids = routineId
                routine_pack_values = routineValue
                routine_pack_size = len(routineId)
            else:
                routine_pack_ids = sensorData['sensorId']
                routine_pack_values = sensorData['sensorValue']
                routine_pack_size = sensorData['numSensor']
            dataPack = packData.dataPack(deviceSetting['uid'], routine_pack_ids, routine_pack_values, routine_pack_size, timestampUTC, 9)
        
            if str(protocolMonitoring) == "1":
                resultMonitoring = httpProtocolFunction.runPostMethod(serverConfig['http'], "receiver", dataPack)
        
                if resultMonitoring['state'] == "Success":               
                    statusBuffer, typeMonitor, attempt = 1, 9, 1
                    LogMonitoringDB.insert(json.dumps(dataPack['data']), resultMonitoring['state_code'], statusBuffer, timestamp, typeMonitor, attempt)
                    logService = f"{routine_pack_size} Sensors {resultMonitoring['state']} Routine Monitoring Interval ({intervalData[num]} Seconds)"
                    colorLogService = f"\033[92m{logService} at {timestamp}\033[00m"
        
                else:
                    statusBuffer, typeMonitor, attempt = 0, 9, 1
                    LogMonitoringDB.insert(json.dumps(dataPack['data']), resultMonitoring['state_code'], statusBuffer, timestamp, typeMonitor, attempt)
                    logService = f"{routine_pack_size} Sensors {resultMonitoring['state']} Routine Monitoring Interval ({intervalData[num]} Seconds) - {resultMonitoring['log']}"
                    colorLogService = f"\033[31m{logService} at {timestamp}\033[00m"

                # Kirim kategori Normal/Min/Max bersama routine hanya jika mode 'routine'
                if alarm_mode == 'routine':
                    if len(alarmNormalId) > 0:
                        alarmNormalPack = packData.dataPack(deviceSetting['uid'], alarmNormalId, alarmNormalValue, len(alarmNormalId), timestampUTC, 1)
                        httpProtocolFunction.runPostMethod(serverConfig['http'], 'receiver', alarmNormalPack)
                    if len(alarmMaxId) > 0:
                        alarmMaxPack = packData.dataPack(deviceSetting['uid'], alarmMaxId, alarmMaxValue, len(alarmMaxId), timestampUTC, 3)
                        httpProtocolFunction.runPostMethod(serverConfig['http'], 'receiver', alarmMaxPack)
                    if len(alarmMinId) > 0:
                        alarmMinPack = packData.dataPack(deviceSetting['uid'], alarmMinId, alarmMinValue, len(alarmMinId), timestampUTC, 2)
                        httpProtocolFunction.runPostMethod(serverConfig['http'], 'receiver', alarmMinPack)
        
            elif str(protocolMonitoring) == "2":
                resultMonitoring = mqttProtocolFunction.runPublish(serverConfig['mqtt'], "data", dataPack, globalVariable)
        
                if resultMonitoring['state'] == "Success":               
                    statusBuffer, typeMonitor, attempt = 1, 9, 1
                    LogMonitoringDB.insert(json.dumps(dataPack['data']), resultMonitoring['state_code'], statusBuffer, timestamp, typeMonitor, attempt)
                    logService = f"{sensorData['numSensor']} Sensors {resultMonitoring['state']} Routine Monitoring Interval ({intervalData[num]} Seconds)"
                    colorLogService = f"\033[92m{logService} at {timestamp}\033[00m"
        
                else:
                    statusBuffer, typeMonitor, attempt = 0, 9, 1
                    LogMonitoringDB.insert(json.dumps(dataPack['data']), resultMonitoring['state_code'], statusBuffer, timestamp, typeMonitor, attempt)
                    logService = f"{sensorData['numSensor']} Sensors {resultMonitoring['state']} Routine Monitoring Interval ({intervalData[num]} Seconds) - {resultMonitoring['log']}"
                    colorLogService = f"\033[31m{logService} at {timestamp}\033[00m"
        
            else:
                logService = f"{sensorData['numSensor']} Sensors Failed Routine Monitoring Interval ({intervalData[num]} Seconds) - Protocol N/A"
                colorLogService = f"\033[31m{logService} at {timestamp}\033[00m" 
        
            globalVariable["logger"].debug(f"{colorLogService}\n")   

            

        
        else:
            logService = f"No Sensor with Routine Monitoring Interval {intervalData[num]} Seconds"
            colorLogService = f"\033[31m{logService}\033[00m"
            globalVariable["logger"].debug(f"{colorLogService}\n")
            
        SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['serviceName'])  


    def runAlarm(num, alarmData, globalVariable):
        projectData = generalFunction.getProjectSetting()
        protocolMonitoring = projectData['protocol'] # 1: HTTP, 2: MQTT, 3: SNMP
        timestamp = times.getDatetime()
        deviceSetting = dbFunction.getDeviceSetting()
        serverConfig = serverFunction.getServerConfig()    
        tolerancePack = []
        idAlarmMonitorLog = alarmData[num]['id']
        sensorAlarmPack = json.loads(alarmData[num]['data'])
        sensorAlarmList = list(sensorAlarmPack.keys())
        timestampAlarm = alarmData[num]['timestamp'] 
        timestampAlarmUTC = times.convertToUTC(timestampAlarm)
        typeAlarm = alarmData[num]['tipe'] 
        
        ### CHECK TOLERANCE DATA ###
        tolerancePack = monitoringFunction.alarmMonitoringProcess.checkToleranceAlarmData(sensorAlarmList, timestampAlarm, tolerancePack)
        ### CHECK ROUTINE MONITOR & LOG DATA ###
        timestampAlarm = monitoringFunction.alarmMonitoringProcess.checkLogSensorRoutine(idAlarmMonitorLog, sensorAlarmList, typeAlarm, timestampAlarm) 
        
        ### SEND ALARM MONITORING DATA ###
        if str(protocolMonitoring) == "1":
            dataPackAlarm = {"node_id": deviceSetting['uid'], "data": sensorAlarmPack, "timestamp": str(timestampAlarmUTC), "status": str(typeAlarm)}
            attemptMonitoring = 1
            resultMonitoring = httpProtocolFunction.runPostMethod(serverConfig['http'], "receiver", dataPackAlarm)
        
            if resultMonitoring['state'] == "Success": 
                globalVariable["countAlarm"] += 1
                statusBuffer = 1
                LogMonitoringDB.updateAlarm(resultMonitoring['state_code'], statusBuffer, attemptMonitoring, idAlarmMonitorLog)
        
            else:
                statusBuffer = 0
                LogMonitoringDB.updateAlarm(resultMonitoring['state_code'], statusBuffer, attemptMonitoring, idAlarmMonitorLog)
        
        elif str(protocolMonitoring) == "2":
            dataPackAlarm = {"node_id": deviceSetting['uid'], "data": sensorAlarmPack, "timestamp": str(timestampAlarmUTC), "status": str(typeAlarm)}
            attemptMonitoring = 1
            resultMonitoring = mqttProtocolFunction.runPublish(serverConfig['mqtt'], "data", dataPackAlarm, globalVariable)
        
            if resultMonitoring['state'] == "Success": 
                globalVariable["countAlarm"] += 1
                statusBuffer = 1
                LogMonitoringDB.updateAlarm(str(resultMonitoring['state_code']), statusBuffer, attemptMonitoring, idAlarmMonitorLog)
        
            else:
                statusBuffer = 0
                LogMonitoringDB.updateAlarm(str(resultMonitoring['state_code']), statusBuffer, attemptMonitoring, idAlarmMonitorLog)
        
        else:
            resultMonitoring = {"state": "Failed", "log": "Protocol N/A", "state_code": "444", "payload": {}} 
            statusBuffer = 0
            
        ### SEND ALARM TOLERANCE MONITORING DATA ###
        if len(tolerancePack) > 0:
            threadTolerance = generalFunction.ThreadWithReturnValues(target=monitoringFunction.runAlarmTolerance, args=(deviceSetting, protocolMonitoring, serverConfig, 
                                                                                                                        tolerancePack, globalVariable))
            threadTolerance.start()
        ############################################
        
        if statusBuffer == 0:
            log = f"Status Code {resultMonitoring['state_code']}"       
            logService = f"Running {globalVariable['countAlarm']} of {len(alarmData)} Alarm Data | {log}"
        
        else:
            logService = f"Running {globalVariable['countAlarm']} of {len(alarmData)} Alarm Data"
        
        SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['serviceName'])
        resultAlarm = {"state": statusBuffer, "message": resultMonitoring}
        return resultAlarm


    def runAlarmTolerance(deviceSetting, protocolMonitoring, serverConfig, tolerancePack, globalVariable):
        for y in range(len(tolerancePack)):
            typeMonitoring, attemptMonitoring = 11, 1
            sensorTolerancePack = tolerancePack[y]['data']
            timestampTolerance = str(tolerancePack[y]['timestamp'])
            timestampToleranceUtc = times.convertToUTC(timestampTolerance)
        
            if str(protocolMonitoring) == "1":
                dataPackAlarmTolerance = {"node_id": deviceSetting['uid'], "data": sensorTolerancePack, "timestamp": str(timestampToleranceUtc), "status": str(typeMonitoring)}
                resultMonitoring = httpProtocolFunction.runPutMethod(serverConfig['http'], 'update', dataPackAlarmTolerance)

                if resultMonitoring['state'] == "Success":  
                    statusBuffer = 1
                    LogMonitoringDB.insert(json.dumps(sensorTolerancePack), resultMonitoring['state_code'], statusBuffer, timestampTolerance, typeMonitoring, attemptMonitoring) 

                else:
                    statusBuffer = 0 
                    LogMonitoringDB.insert(json.dumps(sensorTolerancePack), resultMonitoring['state_code'], statusBuffer, timestampTolerance, typeMonitoring, attemptMonitoring) 
                
            elif str(protocolMonitoring) == "2":
                dataPackAlarmTolerance = {"node_id": deviceSetting['uid'], "data": sensorTolerancePack, "timestamp": timestampToleranceUtc, "status": str(typeMonitoring)}
                resultMonitoring = mqttProtocolFunction.runPublish(serverConfig['mqtt'], "data", dataPackAlarmTolerance, globalVariable)
            
                if resultMonitoring['state'] == "Success": 
                    statusBuffer = 1
                    LogMonitoringDB.insert(json.dumps(sensorTolerancePack), resultMonitoring['state_code'], statusBuffer, timestampTolerance, typeMonitoring, attemptMonitoring)
            
                else:
                    statusBuffer = 0
                    LogMonitoringDB.insert(json.dumps(sensorTolerancePack), resultMonitoring['state_code'], statusBuffer, timestampTolerance, typeMonitoring, attemptMonitoring)
            
            else:
                pass       


    def runBuffer(num, bufferData, serverConfig, globalVariable):
        timestamp = times.getDatetime()
        deviceSetting = dbFunction.getDeviceSetting()
        typeData = bufferData[num]['tipe']
        
        if int(typeData) == 9 or int(typeData) == 10: state = '0'
        elif int(typeData) == 1: state = '5'
        elif int(typeData) == 2: state = '6'
        elif int(typeData) == 3: state = '7'
        elif int(typeData) == 4: state = '8'
        elif int(typeData) == 11: state = '11'
        else: state = '99'
            
        bufferTimestamp = bufferData[num]['timestamp']
        bufferTimestampUTC = times.convertToUTC(bufferTimestamp)
        dataPack = json.loads(bufferData[num]['data'])
        sensorIdList = list(dataPack.keys())
        sensorValueList = list(dataPack.values())
        numSensor = len(sensorIdList) 
        packedData = packData.dataPack(node_id=deviceSetting['uid'], id=sensorIdList, value=sensorValueList, size=numSensor, timestamp=bufferTimestampUTC, state=state)
        
        projectData = generalFunction.getProjectSetting()
        protocolMonitoring = projectData['protocol'] # 1: HTTP, 2: MQTT, 3: SNMP
        if str(protocolMonitoring) == "1":
        
            if state == '11':
                resultMonitoring = httpProtocolFunction.runPutMethod(serverConfig['http'], "update", packedData)
        
            else:
                resultMonitoring = httpProtocolFunction.runPostMethod(serverConfig['http'], "receiver", packedData)
        
            if resultMonitoring["state"] == "Success":
                globalVariable["countBuffer"] += 1
                LogMonitoringDB.updateBuffer(int(bufferData[num]['attempt']) + 1, bufferData[num]['id'])
                resultBuffer = 1
        
            else:
                LogMonitoringDB.updateAttempt(int(bufferData[num]['attempt']) + 1, bufferData[num]['id'])
                resultBuffer = 0
        
        elif str(protocolMonitoring) == "2":
            resultMonitoring = mqttProtocolFunction.runPublish(serverConfig['mqtt'], "data", packedData, globalVariable)
        
            if resultMonitoring["state"] == "Success":
                globalVariable["countBuffer"] += 1
                LogMonitoringDB.updateBuffer(int(bufferData[num]['attempt']) + 1, bufferData[num]['id'])
                resultBuffer = 1
        
            else:
                LogMonitoringDB.updateAttempt(int(bufferData[num]['attempt']) + 1, bufferData[num]['id'])
                resultBuffer = 0
        
        else:
            resultMonitoring = {"state": "Failed", "log": "Protocol N/A", "state_code": "444", "payload": {}} 
            resultBuffer = 0
        
        if resultBuffer == 0:
            log = f"Status Code {resultMonitoring['state_code']}"       
            logService = f"Running {globalVariable['countBuffer']} of {len(bufferData)} Buffer Data | {log}"
        
        else:
            logService = f"Running {globalVariable['countBuffer']} of {len(bufferData)} Buffer Data"
        
        SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['serviceName'])
        resultBuffer = {"state": resultBuffer, "message": resultMonitoring}
        return resultBuffer


    class alarmMonitoringProcess():
        def checkToleranceAlarmData(sensorAlarmList, timestampAlarm, tolerancePack):
            for x in range(len(sensorAlarmList)):
                checkAlarm = LogAlarmDB.selectBySensorFirstAlarmTime(sensorAlarmList[x], timestampAlarm)

                if len(checkAlarm) == 1:
                    alarmId = checkAlarm[0]["id"]
                    toleranceData = LogToleranceAlarmDB.selectByAlarm(alarmId)

                    if len(toleranceData) > 0:
                        for y in range(len(toleranceData)):
                            valueTolerance = toleranceData[y]["value"]
                            timestampTolerance = toleranceData[y]["timestamp"]
                            checkRoutine = LogMonitoringDB.selectRoutineByTimeOnly(timestampTolerance)

                            if len(checkRoutine) == 1:
                                sensorPackRoutine = json.loads(checkRoutine[0]["data"])
                                sensorListRoutine = list(sensorPackRoutine.keys())

                                for z in range(len(sensorListRoutine)):
                                    if sensorListRoutine[z] == sensorAlarmList[x]:
                                        sensorTolerancePack = packData.sensorPack([sensorAlarmList[x]], [valueTolerance], 1)

                                        tolerancePack.append({"data": sensorTolerancePack, "timestamp": timestampTolerance})
                            checkLog = LogSensorDB.selectRoutineBySensorTime(sensorAlarmList[x], timestampTolerance)
                            if len(checkLog) == 1:
                                idLog = checkLog[0]["id"]
                                LogSensorDB.updateValue(valueTolerance, idLog)    

                    LogAlarmDB.updateFlag(2, alarmId)       
            return tolerancePack       


        def checkLogSensorRoutine(idAlarmMonitorLog, sensorList, typeAlarm, timestampAlarm):
            check = 0
            timestampNew = timestampAlarm + datetime.timedelta(seconds=1)
            checkRoutine = LogMonitoringDB.selectRoutineByTimeOnly(timestampAlarm)
            if len(checkRoutine) == 1:
                check += 1
                sensorListRoutine = json.loads(checkRoutine[0]["data"])
                sensorListRoutine = list(sensorListRoutine.keys())
                
                for y in range(len(sensorList)):
                    for z in range(len(sensorListRoutine)):
                        if sensorList[y] == sensorListRoutine[z]:
                            LogMonitoringDB.updateTimestamp(timestampNew, idAlarmMonitorLog)
                            checkSensor = LogSensorDB.selectByAlarmSensorTime(sensorList[y], typeAlarm, timestampAlarm)
                            
                            if len(checkSensor) == 1:
                                LogSensorDB.updateTimestamp(timestampNew, checkSensor[0]["id"])    
                timestampAlarm = timestampAlarm + datetime.timedelta(seconds=1)
            
            if check == 0:
                check2 = 0
                
                for y in range(len(sensorList)):
                    checkSensor = LogSensorDB.selectRoutineBySensorTime(sensorList[y], timestampAlarm)
                    
                    if len(checkSensor) == 1:
                        checkAlarm = LogSensorDB.selectByAlarmSensorTime(sensorList[y], typeAlarm, timestampAlarm)
                        
                        if len(checkAlarm) == 1:
                            LogSensorDB.updateTimestamp(timestampNew, checkAlarm[0]["id"])
                            check2 += 1
                
                if check2 > 0:
                    LogMonitoringDB.updateTimestamp(timestampNew, idAlarmMonitorLog)
                    timestampAlarm = timestampAlarm + datetime.timedelta(seconds=1)


        def clearAlarmData():
            alarmData = LogAlarmDB.selectByFlag(2)
            for x in range(len(alarmData)):
                alarmId = alarmData[x]["id"]
                checkAlarm = SensorListDB.selectByAlarmId(alarmId)
                
                if len(checkAlarm) == 0:
                    LogAlarmDB.deleteById(alarmId)
                    LogToleranceAlarmDB.deleteByAlarmId(alarmId)


        def updateAlarmFlag():
            alarmData = LogAlarmDB.selectByFlag(1)
            for x in range(len(alarmData)):
                alarmId = alarmData[x]["id"]
                checkAlarm = SensorListDB.selectByAlarmId(alarmId)
                
                if len(checkAlarm) == 0: 
                    LogAlarmDB.updateFlag(2, alarmId)
