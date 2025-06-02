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
    def runMonitoring(num, intervalId, intervalData, globalVariable):
        projectData = generalFunction.getProjectSetting()
        timestamp = times.getDatetime()
        timestampUTC = times.convertToUTC(timestamp) 
        sensorData = SensorFunction.CollectDataSensorFunction.byRoutineMonitorInterval(intervalId[num])
        
        if sensorData['numSensor'] > 0:
            deviceSetting = dbFunction.getDeviceSetting()
            serverConfig = serverFunction.getServerConfig()
            dataPack = packData.dataPack(deviceSetting['uid'], sensorData['sensorId'], sensorData['sensorValue'], sensorData['numSensor'], timestampUTC, 9) 
            protocolMonitoring = projectData['protocol'] # 1: HTTP, 2: MQTT, 3: SNMP
            colorLogService = ''
        
            if str(protocolMonitoring) == "1":
                resultMonitoring = httpProtocolFunction.runPostMethod(serverConfig['http'], "receiver", dataPack)
        
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
