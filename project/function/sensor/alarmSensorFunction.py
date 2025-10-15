import json 
import sys
import time

sys.path.append('/home/connex/library')
from SynapsisLibrary import packData
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, LogSensorDB, LogAlarmDB, LogToleranceAlarmDB, LogMonitoringDB
sys.path.append("/home/connex/project/function")
from generalFunction import generalFunction
from notificationFunction import notificationFunction
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction


class alarmSensorFunction():
    def initiateAlarmSensor(data_sensor, sensor_setting, feature_setting):
        alarm_data = {'Normal':[], 'AlarmMin': [], 'AlarmMax':[], 'AlarmError':[], 'flag':[], 'condition':[]}
        alarm_data['NormalTime'], alarm_data['AlarmMinTime'], alarm_data['AlarmMaxTime'],  alarm_data['AlarmErrorTime'] = [], [], [], []
        alarm_data['totalNormal'], alarm_data['totalMin'], alarm_data['totalMax'], alarm_data['totalSensorError'] = 0, 0, 0, 0
        alarm_data['totalNormalTolerance'], alarm_data['totalMinTolerance'], alarm_data['totalMaxTolerance'], alarm_data['totalErrorTolerance'] = 0, 0, 0, 0 
        alarm_data['totalTolerance'], alarm_data['totalSensorInactive'], alarm_data['totalAlarmInactive'] = 0, 0, 0
        alarm_data['normalSensorID'], alarm_data['normalSensorValue'], alarm_data['normalSensorTimestamp'] = [], [], []
        alarm_data['errorSensorID'], alarm_data['errorSensorValue'], alarm_data['errorSensorTimestamp'] = [], [], []
        alarm_data['minSensorID'], alarm_data['minSensorValue'], alarm_data['minSensorTimestamp'] = [], [], []
        alarm_data['maxSensorID'], alarm_data['maxSensorValue'], alarm_data['maxSensorTimestamp'] = [], [], []
        alarm_data['firstAlarm'], alarm_data['lastAlarm'], alarm_data['alarmId'], alarm_data['alarmId2'] = [], [], [], []
        alarm_data['enterAlarm'], alarm_data['exitAlarm'], alarm_data['errorAlarm'] = sensor_setting['enterAlarm'], sensor_setting['exitAlarm'], sensor_setting['errorAlarm']
        alarm_data['timeAlarm'], alarm_data['timer'] = [], []
        alarm_data['feature_setting'] = feature_setting
        for x in range(data_sensor['numSensor']):
            alarm_data['timeAlarm'].append(time.time())
            normalCount, minCount, maxCount, errorCount = 0, 0, 0, 0
            normalTime, minTime, maxTime, errorTime = 0, 0, 0, 0
            if 'Tolerance' in data_sensor['sensorCondition'][x]:
                if data_sensor['sensorAlarmId'][x] != data_sensor['sensorLastAlarmId'][x]:
                    getLastAlarm = LogAlarmDB.selectById(data_sensor['sensorLastAlarmId'][x])
                    if len(getLastAlarm) == 1:
                        typeAlarm = getLastAlarm[0]['tipe']
                        if int(typeAlarm) == 1:
                            normalCount, normalTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                        elif int(typeAlarm) == 2:
                            minCount, minTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                        elif int(typeAlarm) == 3:
                            maxCount, maxTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                        elif int(typeAlarm) == 4:
                            errorCount, errorTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
            elif data_sensor['sensorCondition'][x] == 'Normal':
                normalTime, normalCount = data_sensor['sensorNotifTime'][x], data_sensor['sensorNotifCount'][x]
            elif data_sensor['sensorCondition'][x] == 'Alarm Min':
                minTime, minCount = data_sensor['sensorNotifTime'][x], data_sensor['sensorNotifCount'][x]
            elif data_sensor['sensorCondition'][x] == 'Alarm Max':
                maxTime, maxCount = data_sensor['sensorNotifTime'][x], data_sensor['sensorNotifCount'][x]
            elif data_sensor['sensorCondition'][x] == 'Alarm Error':
                errorTime, errorCount = data_sensor['sensorNotifTime'][x], data_sensor['sensorNotifCount'][x]
            alarm_data['Normal'].append(normalCount), alarm_data['AlarmMin'].append(minCount), alarm_data['AlarmMax'].append(maxCount), alarm_data['AlarmError'].append(errorCount)
            alarm_data['NormalTime'].append(normalTime), alarm_data['AlarmMinTime'].append(minTime), alarm_data['AlarmMaxTime'].append(maxTime), alarm_data['AlarmErrorTime'].append(errorTime)
            alarm_data['flag'].append(data_sensor['sensorNotifState'][x]), alarm_data['condition'].append(data_sensor['sensorCondition'][x])
            alarm_data['alarmId'].append(data_sensor['sensorAlarmId'][x]), alarm_data['alarmId2'].append(data_sensor['sensorLastAlarmId'][x])
            getAlarm = LogAlarmDB.selectById(data_sensor['sensorAlarmId'][x])
            if len(getAlarm) == 1:
                alarm_data['firstAlarm'].append(getAlarm[0]['first_alarm']), alarm_data['lastAlarm'].append(getAlarm[0]['last_alarm'])
            else:
                alarm_data['firstAlarm'].append(''), alarm_data['lastAlarm'].append('')
        return alarm_data
    
    def initiateSensor(x, notifData, dataSensor):
        notifData['timeAlarm'].append(time.time())
        normalCount, minCount, maxCount, errorCount = 0, 0, 0, 0
        normalTime, minTime, maxTime, errorTime = 0, 0, 0, 0
        if 'Tolerance' in dataSensor['sensorCondition'][x]:
            if dataSensor['sensorAlarmId'][x] != dataSensor['sensorLastAlarmId'][x]:
                getLastAlarm = LogAlarmDB.selectById(dataSensor['sensorLastAlarmId'][x])
                if len(getLastAlarm) == 1:
                    typeAlarm = getLastAlarm[0]['tipe']
                    if int(typeAlarm) == 1:
                        normalCount, normalTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                    elif int(typeAlarm) == 2:
                        minCount, minTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                    elif int(typeAlarm) == 3:
                        maxCount, maxTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
                    elif int(typeAlarm) == 4:
                        errorCount, errorTime = getLastAlarm[0]['count'], getLastAlarm[0]['count_time']
        elif dataSensor['sensorCondition'][x] == 'Normal':
            normalTime, normalCount = dataSensor['sensorNotifTime'][x], dataSensor['sensorNotifCount'][x]
        elif dataSensor['sensorCondition'][x] == 'Alarm Min':
            minTime, minCount = dataSensor['sensorNotifTime'][x], dataSensor['sensorNotifCount'][x]
        elif dataSensor['sensorCondition'][x] == 'Alarm Max':
            maxTime, maxCount = dataSensor['sensorNotifTime'][x], dataSensor['sensorNotifCount'][x]
        elif dataSensor['sensorCondition'][x] == 'Alarm Error':
            errorTime, errorCount = dataSensor['sensorNotifTime'][x], dataSensor['sensorNotifCount'][x]
        notifData['Normal'].append(normalCount), notifData['AlarmMin'].append(minCount), notifData['AlarmMax'].append(maxCount), notifData['AlarmError'].append(errorCount)
        notifData['NormalTime'].append(normalTime), notifData['AlarmMinTime'].append(minTime), notifData['AlarmMaxTime'].append(maxTime), notifData['AlarmErrorTime'].append(errorTime)
        notifData['flag'].append(dataSensor['sensorNotifState'][x]), notifData['condition'].append(dataSensor['sensorCondition'][x])
        notifData['alarmId'].append(dataSensor['sensorAlarmId'][x]), notifData['alarmId2'].append(dataSensor['sensorLastAlarmId'][x])
        getAlarm = LogAlarmDB.selectById(dataSensor['sensorAlarmId'][x])
        if len(getAlarm) == 1:
            notifData['firstAlarm'].append(getAlarm[0]['first_alarm']), notifData['lastAlarm'].append(getAlarm[0]['last_alarm'])
        else:
            notifData['firstAlarm'].append(''), notifData['lastAlarm'].append('')
        return notifData

    def updateLastValue(i, dataSensor, sensorValue, timestamp):
        log = SensorListDB.updateValue(sensorValue[i], timestamp, dataSensor['id'][i])
        baseOID = OidSensorFunction.getBaseOID(dataSensor['groupId'][i])     
        oid = str(baseOID) + "." + str(dataSensor['sensorOid'][i])
        oid_file = "/tmp/" + str(oid)
        if dataSensor['sensorDatatype'][i] == 0:
             oid_tipe = 'integer'
             oid_value = int(float(sensorValue[i])*100)
        else:
             oid_tipe = 'string'
             oid_value = sensorValue[i]    
        log = OidSensorFunction.writeSensorOidFile(oid_file, oid, oid_tipe, oid_value)

    def resetFlag(notifCount, notifTime, tolerance):
        if notifTime >= 1000000:
            notifTime = tolerance + 1
        if notifCount >= 10000:
            notifCount = 10
        return notifCount, notifTime

    def handleFlag(x, notifData):
        notifData['Normal'][x], notifData['NormalTime'][x] = alarmSensorFunction.resetFlag(notifData['Normal'][x], notifData['NormalTime'][x], notifData['exitAlarm'])
        notifData['AlarmMin'][x], notifData['AlarmMinTime'][x] = alarmSensorFunction.resetFlag(notifData['AlarmMin'][x], notifData['AlarmMinTime'][x], notifData['enterAlarm'])
        notifData['AlarmMax'][x], notifData['AlarmMaxTime'][x] = alarmSensorFunction.resetFlag(notifData['AlarmMax'][x], notifData['AlarmMaxTime'][x], notifData['enterAlarm'])
        notifData['AlarmError'][x], notifData['AlarmErrorTime'][x] = alarmSensorFunction.resetFlag(notifData['AlarmError'][x], notifData['AlarmErrorTime'][x], notifData['errorAlarm'])
        return notifData

    def handleStatusSensor(status, status2):
        if status != '':
            status = status + " | "
        status = status + status2
        return status

    def logNotifMonitorData(condition, notifData, timestamp):
        timestampFirst = ''
        if condition == 'Normal':
            sensorPack = packData.sensorPack(notifData['normalSensorID'], notifData['normalSensorValue'], len(notifData['normalSensorID']))
            if len(notifData['normalSensorTimestamp']) > 0:
                timestampFirst = notifData['normalSensorTimestamp'][0]
            conditionNum = 1
        elif condition == 'Alarm Min':
            sensorPack = packData.sensorPack(notifData['minSensorID'], notifData['minSensorValue'], len(notifData['minSensorID']))
            if len(notifData['minSensorTimestamp']) > 0:
                timestampFirst = notifData['minSensorTimestamp'][0]
            conditionNum = 2
        elif condition == 'Alarm Max':
            sensorPack = packData.sensorPack(notifData['maxSensorID'], notifData['maxSensorValue'], len(notifData['maxSensorID']))
            if len(notifData['maxSensorTimestamp']) > 0:
                timestampFirst = notifData['maxSensorTimestamp'][0]
            conditionNum = 3
        elif condition == 'Alarm Error':
            sensorPack = packData.sensorPack(notifData['errorSensorID'], notifData['errorSensorValue'], len(notifData['errorSensorID']))
            if len(notifData['errorSensorTimestamp']) > 0:
                timestampFirst = notifData['errorSensorTimestamp'][0]
            conditionNum = 4
        if timestampFirst == '':
            timestampFirst = timestamp
        statusCode, statusBuffer, typeMonitor, attempt = "-", 3, conditionNum, 0
        LogMonitoringDB.insert(json.dumps(sensorPack), statusCode, statusBuffer, timestampFirst, typeMonitor, attempt)
        return notifData

    def checkAlarm(dataSensor, sensorValue, sensorResult, notifData, method, timestamp):
        status, statusColored = '', ''

        if method == 'Serial':
            for x in range(dataSensor['numSensor']):
                notifData = alarmSensorFunction.logicNotif(x, sensorValue, sensorResult, notifData, dataSensor, timestamp)
            
        else:
            threadNotifs = []
            for x in range(dataSensor['numSensor']):
                threadNotif = generalFunction.ThreadWithReturnValues(target=alarmSensorFunction.logicNotif, args=(x, sensorValue, sensorResult, notifData, dataSensor, timestamp))
                threadNotif.start()
                threadNotifs.append(threadNotif)
            for y in range(len(threadNotifs)) :
                result = threadNotifs[y].join()
            notifData = result
             
        if notifData['totalTolerance'] > 0: 
            status = f"{str(notifData['totalTolerance'])} Sensors Alarm Tolerance"
            statusColored = f"\033[93m{status}\033[00m"
        
        if notifData['totalNormalTolerance'] > 0:
            status2 = f"{str(notifData['totalNormalTolerance'])} Sensors Normal Tolerance" 
            statusColored2 = f"\033[93m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
        
        if notifData['totalMinTolerance'] > 0: 
            status2 = f"{str(notifData['totalMinTolerance'])} Sensors Alarm Min Tolerance"
            statusColored2 = f"\033[93m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
        
        if notifData['totalMaxTolerance'] > 0: 
            status2 = f"{str(notifData['totalMaxTolerance'])} Sensors Alarm Max Tolerance"
            statusColored2 = f"\033[93m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
        
        if notifData['totalErrorTolerance'] > 0: 
            status2 = f"{str(notifData['totalErrorTolerance'])} Sensors Alarm Error Tolerance"
            statusColored2 = f"\033[93m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
            
        if notifData['totalNormal'] > 0:
            status2 = f"{str(notifData['totalNormal'])} Sensors Normal"
            statusColored2 = f"\033[32m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
            if len(notifData['normalSensorID']) > 0:
                notifData = alarmSensorFunction.logNotifMonitorData('Normal', notifData, timestamp)
                notifData['normalSensorID'], notifData['normalSensorValue'], notifData['normalSensorTimestamp'] = [], [], []
                
        if notifData['totalMin'] > 0:
            status2 = f"{str(notifData['totalMin'])} Sensors Alarm Min"
            statusColored2 = f"\033[91m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
            if len(notifData['minSensorID']) > 0:
                notifData = alarmSensorFunction.logNotifMonitorData('Alarm Min', notifData, timestamp)
                notifData['minSensorID'], notifData['minSensorValue'], notifData['minSensorTimestamp'] = [], [], []
                
        if notifData['totalMax'] > 0:
            status2 = f"{str(notifData['totalMax'])} Sensors Alarm Max"
            statusColored2 = f"\033[91m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
            if len(notifData['maxSensorID']) > 0:
                notifData = alarmSensorFunction.logNotifMonitorData('Alarm Max', notifData, timestamp)
                notifData['maxSensorID'], notifData['maxSensorValue'], notifData['maxSensorTimestamp'] = [], [], []
                
        if notifData['totalSensorError'] > 0:
            status2 = f"{str(notifData['totalSensorError'])} Sensors Alarm Error"
            statusColored2 = f"\033[31m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)
            if len(notifData['errorSensorID']) > 0:
                notifData = alarmSensorFunction.logNotifMonitorData('Alarm Error', notifData, timestamp)
                notifData['errorSensorID'], notifData['errorSensorValue'], notifData['errorSensorTimestamp'] = [], [], []
                
        if notifData['totalAlarmInactive'] > 0:
            status2 = f"{str(notifData['totalAlarmInactive'])} Sensors Alarm Inactive"
            statusColored2 = f"\033[34m{status2}\033[00m"
            status = alarmSensorFunction.handleStatusSensor(status, status2)
            statusColored = alarmSensorFunction.handleStatusSensor(statusColored, statusColored2)           
             
        summarySensor = {"log": status, "logColored": statusColored}                
        return notifData, summarySensor

    def logicNotif(i, sensorValue, sensorResult, notifData, dataSensor, timestamp):
        notifData = alarmSensorFunction.handleFlag(i, notifData)
        
        ########## ALARM ACTIVE ############
        if int(dataSensor['sensorAlarm'][i]) == 1:
            ########## SENSOR SUCCESS ##########
            if sensorResult['state'][i] == True:
                ########## DATATYPE INTEGER ##########
                if dataSensor['sensorDatatype'][i] == 0:
            
                    # Min & Max
                    if dataSensor['sensorAlarmType'][i] == 3:
                        if float(sensorValue[i]) < float(dataSensor['sensorMin'][i]):
                            ########## SENSOR MIN ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Alarm Min', 2, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR MIN ##########
                        elif float(sensorValue[i]) > float(dataSensor['sensorMax'][i]):
                            ########## SENSOR MAX ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Alarm Max', 3, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR MAX ##########
                        else:
                            ########## SENSOR NORMAL ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Normal', 1, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR NORMAL ##########

                    # Max Only
                    elif dataSensor['sensorAlarmType'][i] == 2:
                        if float(sensorValue[i]) > float(dataSensor['sensorMax'][i]):
                            ########## SENSOR MAX ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Alarm Max', 3, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR MAX ##########
                        else:
                            ########## SENSOR NORMAL ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Normal', 1, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR NORMAL ##########
                    
                    # Min Only
                    elif dataSensor['sensorAlarmType'][i] == 1:    
                        if float(sensorValue[i]) < float(dataSensor['sensorMin'][i]):
                            ########## SENSOR MIN ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Alarm Min', 2, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR MIN ##########
                        else:
                            ########## SENSOR NORMAL ##########
                            notifData = alarmSensorFunction.notifProcess(i, 'Normal', 1, sensorValue, notifData, dataSensor, timestamp)
                            ########## SENSOR NORMAL ##########

                    else:
                        ########## ALARM INACTIVE ##########
                        notifData = alarmSensorFunction.handleNotifInactive(i, notifData, dataSensor, sensorValue, timestamp)
                        ########## ALARM INACTIVE ##########
                ########## DATATYPE INTEGER ##########
                ########## DATATYPE STRING ###########
                else:   
                    notifData = alarmSensorFunction.notifProcess(i, 'Normal', 1, sensorValue, notifData, dataSensor, timestamp)
                ########## DATATYPE STRING ###########
            ########## SENSOR SUCCESS ##########
            ########## SENSOR ERROR ############
            else:
                notifData = alarmSensorFunction.notifProcess(i, 'Alarm Error', 4, sensorValue, notifData, dataSensor, timestamp)
            ########## SENSOR ERROR ############
        ########## ALARM ACTIVE ############
        ########## ALARM INACTIVE ##########
        else:
            notifData = alarmSensorFunction.handleNotifInactive(i, notifData, dataSensor, sensorValue, timestamp)
        ########## ALARM ACTIVE ############   
        return notifData

    def notifProcess(i, condition, conditionNumber, sensorValue, notifData, dataSensor, timestamp):      
        sensorTolerance = alarmSensorFunction.checkTolerance(conditionNumber, notifData)
        conditionHandle = condition.replace(" ","")
        ##### UPDATE ALARM COUNT & CONDITION #####
        secondTime = time.time()
        timers = round(secondTime - notifData['timeAlarm'][i],2)
        notifData[conditionHandle + 'Time'][i] = round(notifData[conditionHandle + 'Time'][i] + timers,2)
        notifData['timeAlarm'][i] = secondTime
        notifData[conditionHandle][i] += 1
        SensorListDB.updateNotifCount(notifData[conditionHandle][i], notifData[conditionHandle + 'Time'][i], dataSensor['sensorId'][i])
        ##### UPDATE ALARM COUNT & CONDITION #####
        if notifData[conditionHandle + 'Time'][i] >= sensorTolerance:
            alarmSensorFunction.updateLastValue(i, dataSensor, sensorValue, timestamp)
            notifData = alarmSensorFunction.handleNotifCondition(condition, notifData)
            notifData = alarmSensorFunction.handleResetOtherNotif(i, condition, notifData)
             
            ##### RESET FLAG ALARM #####)
            if notifData['condition'][i] != condition:                
                checkAlarm = LogAlarmDB.selectByIdType(conditionNumber, notifData['alarmId2'][i])
                if len(checkAlarm) == 0:
                    notifData['flag'][i] = 0
                    SensorListDB.updateNotifState(0, dataSensor['sensorId'][i])
            ##### RESET FLAG ALARM #####
             
            ##### ACTION ALARM #####
            if notifData['flag'][i] == 0:
                if int(notifData[conditionHandle][i]) == 1:
                    notifData = alarmSensorFunction.initiateAlarm(i, conditionNumber, sensorValue, notifData, dataSensor, timestamp)
                else:
                    LogToleranceAlarmDB.insert(sensorValue[i], timestamp, notifData['alarmId'][i])
                ##### CLEAR LAST ALARM #####
                checkLastAlarm = LogAlarmDB.selectByIdFlag(notifData['alarmId2'][i])

                if len(checkLastAlarm) == 1:
                    LogAlarmDB.deleteById(notifData['alarmId2'][i])
                    LogToleranceAlarmDB.deleteByAlarmId(notifData['alarmId2'][i])
                ##### CLEAR LAST ALARM #####
                notifData['flag'][i], notifData['condition'][i] = 1, condition
                notifData['lastAlarm'][i] = timestamp
                SensorListDB.updateNotifState(1, dataSensor['sensorId'][i]), SensorListDB.updateCondition(condition, dataSensor['sensorId'][i])
                LogAlarmDB.updateAlarm(notifData[conditionHandle][i], notifData[conditionHandle + 'Time'][i], sensorTolerance, notifData['lastAlarm'][i], 1, notifData['alarmId'][i])
                notifData = alarmSensorFunction.updateLastAlarmId(i, notifData['alarmId'][i], dataSensor['sensorId'][i], notifData)
                getAlarm = LogAlarmDB.selectById(notifData['alarmId'][i])
                if len(getAlarm) == 1:
                    value = getAlarm[0]['value']
                else:
                    value = sensorValue[i]
                if condition == 'Alarm Min':
                    alarmConfig = {'max': dataSensor['sensorMax'][i], 'min': dataSensor['sensorMin'][i], 'config': dataSensor['sensorAlarmType'][i]}
                elif condition == 'Alarm Max':
                    alarmConfig = {'max': dataSensor['sensorMax'][i], 'min': dataSensor['sensorMin'][i], 'config': dataSensor['sensorAlarmType'][i]}
                elif condition == 'Normal':
                    alarmConfig = {'max': dataSensor['sensorMax'][i], 'min': dataSensor['sensorMin'][i], 'config': dataSensor['sensorAlarmType'][i]}
                elif condition == 'Alarm Error':
                    alarmConfig = 'N/A'
                else:
                    alarmConfig = 'N/A'
                ##### SEND ALARM DATA & NOTIFICATION ####
                print(notifData['feature_setting'])
                if int(notifData['feature_setting']['notification']) == 1:
                    notificationFunction.generateNotificationSensor(dataSensor['sensorId'][i], dataSensor['sensorName'][i], value, alarmConfig, condition, dataSensor['sensorUnit'][i], notifData['firstAlarm'][i], notifData['feature_setting'])
                if int(notifData['feature_setting']['log']) == 1:
                    LogSensorDB.insert(dataSensor['id'][i], value, conditionNumber, notifData['firstAlarm'][i])
                # Kirim alarm monitoring hanya jika mode bukan 'routine'
                alarm_mode = str(notifData['feature_setting'].get('alarmMonitorMode', 'direct')).lower()
                if alarm_mode != 'routine' and int(notifData['feature_setting']['alarmMonitor']) == 1:
                    notifData = alarmSensorFunction.handlePackAlarmMonitoring(i, condition, notifData, value, dataSensor)
                ##### SEND ALARM DATA & NOTIFICATION ####
            else:
                if notifData['alarmId'][i] != notifData['alarmId2'][i]:
                    ##### CLEAR ALARM TOLERANCE #####
                    LogAlarmDB.deleteById(notifData['alarmId'][i])
                    LogToleranceAlarmDB.deleteByAlarmId(notifData['alarmId'][i])
                    notifData = alarmSensorFunction.updateFirstAlarmId(i, notifData['alarmId2'][i], dataSensor['sensorId'][i], notifData)
                    getAlarm = LogAlarmDB.selectById(notifData['alarmId'][i])
                    if len(getAlarm) == 1:
                        notifData['firstAlarm'][i] = getAlarm[0]['first_alarm']
                        notifData['lastAlarm'][i] = getAlarm[0]['last_alarm']
                    ##### CLEAR ALARM TOLERANCE #####
                notifData['flag'][i], notifData['condition'][i] = 2, condition
                SensorListDB.updateNotifState(2, dataSensor['sensorId'][i]), SensorListDB.updateCondition(condition, dataSensor['sensorId'][i])
                LogAlarmDB.updateCountAlarm(notifData[conditionHandle][i], notifData[conditionHandle + 'Time'][i], sensorTolerance, notifData['alarmId'][i])
            ##### ACTION ALARM #####
        else:
            if conditionNumber == 1: conditionTolerance = 'Normal Tolerance'
            elif conditionNumber == 2: conditionTolerance = 'Alarm Min Tolerance'
            elif conditionNumber == 3: conditionTolerance = 'Alarm Max Tolerance'
            elif conditionNumber == 4: conditionTolerance = 'Alarm Error Tolerance'
            else: conditionTolerance = 'Alarm Tolerance'
            notifData['condition'][i] = conditionTolerance
            SensorListDB.updateCondition(conditionTolerance, dataSensor['sensorId'][i])
            if int(notifData[conditionHandle][i]) == 1:
                notifData = alarmSensorFunction.initiateAlarm(i, conditionNumber, sensorValue, notifData, dataSensor, timestamp)
            LogAlarmDB.updateCountAlarm(notifData[conditionHandle][i], notifData[conditionHandle + 'Time'][i], sensorTolerance, notifData['alarmId'][i])
            if notifData[conditionHandle][i] > 1:
                LogToleranceAlarmDB.insert(sensorValue[i], timestamp, notifData['alarmId'][i])
            notifData = alarmSensorFunction.handleNotifCondition(notifData['condition'][i], notifData)
        return notifData

    def updateFirstAlarmId(i, alarmId, sensorId, notifData):
        notifData['alarmId'][i] = alarmId
        SensorListDB.updateAlarmId(alarmId, sensorId)
        return notifData

    def updateLastAlarmId(i, alarmId, sensorId, notifData):
        notifData['alarmId2'][i] = alarmId
        SensorListDB.updateLastAlarmId(alarmId, sensorId)
        return notifData

    def initiateAlarm(i, conditionNumber, sensorValue, notifData, dataSensor, timestamp):
        sensorTolerance = alarmSensorFunction.checkTolerance(conditionNumber, notifData)
        ##### START ALARM TOLERANCE #####
        getAlarmTolerance = LogAlarmDB.selectAlarmToleranceById(notifData['alarmId'][i])
        if len(getAlarmTolerance) == 1:
            LogAlarmDB.deleteById(notifData['alarmId'][i])
            LogToleranceAlarmDB.deleteByAlarmId(notifData['alarmId'][i])
        else:
            notifData = alarmSensorFunction.updateLastAlarmId(i, notifData['alarmId'][i], dataSensor['sensorId'][i], notifData)
        identity = ''
        if conditionNumber == 1:
            identity = 'NML'
        elif conditionNumber == 2:
            identity = 'MIN'
        elif conditionNumber == 3:
            identity = 'MAX'
        elif conditionNumber == 4:
            identity = 'ERR'
        alarmId = generalFunction.getRandomID(5)
        alarmId = identity + "-" + alarmId
        notifData = alarmSensorFunction.updateFirstAlarmId(i, alarmId, dataSensor['sensorId'][i], notifData)
        notifData['firstAlarm'][i] = timestamp
        LogAlarmDB.insert(alarmId, dataSensor['id'][i], sensorValue[i], conditionNumber, 0, 0, sensorTolerance, notifData['firstAlarm'][i])
        ##### START ALARM TOLERANCE #####
        return notifData

    def handleNotifInactive(i, notifData, dataSensor, sensorValue, timestamp):
        notifData['totalAlarmInactive'] += 1
        alarmId = [notifData['alarmId'][i], notifData['alarmId2'][i]]
        for x in range(len(alarmId)):
            getAlarm = LogAlarmDB.selectById(alarmId[x])
            if len(getAlarm) == 1:
                countTime, tolerance, flag = getAlarm[0]['count_time'], getAlarm[0]['tolerance'], getAlarm[0]['flag']
                if countTime < tolerance:
                    LogAlarmDB.deleteById(alarmId[x])
                    LogToleranceAlarmDB.deleteByAlarmId(alarmId[x])
                else:
                    if flag == 2:
                        LogAlarmDB.deleteById(alarmId[x])
                        LogToleranceAlarmDB.deleteByAlarmId(alarmId[x])
        notifData['firstAlarm'][i], notifData['lastAlarm'][i] = '', ''
        notifData = alarmSensorFunction.updateFirstAlarmId(i, '', dataSensor['sensorId'][i], notifData)
        notifData = alarmSensorFunction.updateLastAlarmId(i, '', dataSensor['sensorId'][i], notifData)
        SensorListDB.updateCondition("Alarm Inactive", dataSensor['sensorId'][i])
        SensorListDB.updateNotifState(0, dataSensor['sensorId'][i])
        SensorListDB.updateNotifCount(0, 0, dataSensor['sensorId'][i])
        notifData['Normal'][i], notifData['AlarmMin'][i], notifData['AlarmMax'][i], notifData['AlarmError'][i] = 0, 0, 0, 0
        notifData['NormalTime'][i], notifData['AlarmMinTime'][i], notifData['AlarmMaxTime'][i], notifData['AlarmErrorTime'][i] = 0, 0, 0, 0
        notifData['flag'][i], notifData['condition'][i]  = 0, 'Alarm Inactive'
        alarmSensorFunction.updateLastValue(i, dataSensor, sensorValue, timestamp)
        return notifData

    def checkTolerance(condition, notifData):
        if condition == 1 or condition == 'Normal':
            tolerance = notifData['exitAlarm']
        elif condition == 2 or condition == 'Alarm Min':
            tolerance = notifData['enterAlarm']
        elif condition == 3 or condition == 'Alarm Max':
            tolerance = notifData['enterAlarm']
        elif condition == 4 or condition == 'Alarm Error':
            tolerance = notifData['errorAlarm']
        else:
            tolerance = 0
        return tolerance

    def handleNotifCondition(condition, notifData):
        if condition == 'Normal': notifData['totalNormal'] += 1
        elif condition == 'Alarm Min': notifData['totalMin'] += 1
        elif condition == 'Alarm Max': notifData['totalMax'] += 1
        elif condition == 'Alarm Error': notifData['totalSensorError'] += 1
        elif condition == 'Normal Tolerance': notifData['totalNormalTolerance'] += 1
        elif condition == 'Alarm Min Tolerance': notifData['totalMinTolerance'] += 1
        elif condition == 'Alarm Max Tolerance': notifData['totalMaxTolerance'] += 1
        elif condition == 'Alarm Error Tolerance': notifData['totalErrorTolerance'] += 1
        elif condition == 'Alarm Tolerance': notifData['totalTolerance'] += 1
        return notifData

    def handleResetOtherNotif(i, condition, notifData):
        if condition == 'Normal':
            notifData['AlarmMin'][i], notifData['AlarmMax'][i], notifData['AlarmError'][i] = 0, 0, 0
            notifData['AlarmMinTime'][i], notifData['AlarmMaxTime'][i], notifData['AlarmErrorTime'][i] = 0, 0, 0
        elif condition == 'Alarm Min':
            notifData['Normal'][i], notifData['AlarmMax'][i], notifData['AlarmError'][i] = 0, 0, 0
            notifData['NormalTime'][i], notifData['AlarmMaxTime'][i], notifData['AlarmErrorTime'][i] = 0, 0, 0
        elif condition == 'Alarm Max':
            notifData['Normal'][i], notifData['AlarmMin'][i], notifData['AlarmError'][i] = 0, 0, 0
            notifData['NormalTime'][i], notifData['AlarmMinTime'][i], notifData['AlarmErrorTime'][i] = 0, 0, 0
        elif condition == 'Alarm Error':
            notifData['Normal'][i], notifData['AlarmMin'][i], notifData['AlarmMax'][i] = 0, 0, 0
            notifData['NormalTime'][i], notifData['AlarmMinTime'][i], notifData['AlarmMaxTime'][i] = 0, 0, 0
        return notifData

    def handlePackAlarmMonitoring(i, condition, notifData, value, dataSensor):
        if condition == 'Normal':
            notifData['normalSensorID'].append(dataSensor['sensorId'][i])
            notifData['normalSensorValue'].append(value)
            notifData['normalSensorTimestamp'].append(notifData['firstAlarm'][i])
        elif condition == 'Alarm Min':
            notifData['minSensorID'].append(dataSensor['sensorId'][i])
            notifData['minSensorValue'].append(value)
            notifData['minSensorTimestamp'].append(notifData['firstAlarm'][i])
        elif condition == 'Alarm Max':
            notifData['maxSensorID'].append(dataSensor['sensorId'][i])
            notifData['maxSensorValue'].append(value)
            notifData['maxSensorTimestamp'].append(notifData['firstAlarm'][i])
        elif condition == 'Alarm Error':
            notifData['errorSensorID'].append(dataSensor['sensorId'][i])
            notifData['errorSensorValue'].append(value)
            notifData['errorSensorTimestamp'].append(notifData['firstAlarm'][i])
        return notifData
