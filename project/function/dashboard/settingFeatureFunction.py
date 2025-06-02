import json 
import os
import sys
import threading

sys.path.append('/home/connex/project/database')
from query_project_db import FeatureSettingDB, IntervalRoutineMonitorDB, IntervalRoutineLogDB, SystemServiceDB, LogToleranceAlarmDB, LogAlarmDB, SensorListDB
sys.path.append("/home/connex/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction


class settingFeature():
    class systemService():
        def command(action, name):
            os.system(f"sudo systemctl {action} {name}")

        def runAll(action, service):
            try:    
                allService = SystemServiceDB.select()
                if len(allService) > 0 :
                    action_threads = []
                    for num in range(len(allService)):
                        check = 0
                        serviceName = allService[num]['name']
                        if service == 'all':
                            if serviceName != 'outback_api' and serviceName != 'dashboard':
                                check = 1
                        elif service == 'node':
                            if 'sensor' not in serviceName and 'actuator' not in serviceName:
                                check = 1
                        elif service == 'sensor':
                            if 'sensor' in serviceName:
                                check = 1
                        elif service == 'actuator':
                            if 'actuator' in serviceName:
                                check = 1
                        # elif service == 'network':
                        #     if 'routine' in serviceName or 'buffer' in serviceName or 'alarm' in serviceName or 'sync' in serviceName or 'notif' in serviceName:
                        #         check = 1
                        if check == 1:
                            action_thread = threading.Thread(target = settingFeature.systemService.command, args = [action, serviceName])
                            action_thread.start()
                            action_threads.append(action_thread)
                    for x in action_threads:
                        x.join()
                if service == 'all':        
                    result = {'state': '1', 'message': f'Success to {action} all service'}   
                else:
                    result = {'state': '1', 'message': f'Success to {action} all {service} service'}               
            except Exception as e:
                if service == 'all':     
                    result = {'state': '0', 'message': f'Failed to {action} all service - ' + str(e)}   
                else:
                    result = {'state': '0', 'message': f'Failed to {action} all {service} service - ' + str(e)}   
            return json.dumps(result)            

    class systemAlarm():  
        def resetOnly():
            try:
                dataSensor = CollectDataSensorFunction.all()
                if dataSensor['numSensor'] > 0:
                    for x in range(dataSensor['numSensor']):
                     SensorListDB.updateResetAlarm(dataSensor['id'][x])
                LogToleranceAlarmDB.deleteAll()
                LogAlarmDB.deleteAll()
                result = {'state':'1', 'message':'Success to Reset Alarm Sensor Only'}      
            except Exception as e:
                result = {'state':'0', 'message':'Failed to Reset Alarm Sensor Only - ' + str(e)}   
            return json.dumps(result) 

        def resetWithRestart():
            try:
                settingFeature.systemService.runAll('stop', 'sensor')
                dataSensor = CollectDataSensorFunction.all()
                if dataSensor['numSensor'] > 0:
                    for x in range(dataSensor['numSensor']):
                        SensorListDB.updateResetAlarm(dataSensor['id'][x])
                    LogToleranceAlarmDB.deleteAll()
                    LogAlarmDB.deleteAll()
                    settingFeature.systemService.runAll('start', 'sensor') 
                result = {'state':'1', 'message':'Success to Reset Alarm Sensor with Restart Service'}      
            except Exception as e:
                result = {'state':'0', 'message':'Failed to Reset Alarm Sensor with Restart Service - ' + str(e)}   
            return json.dumps(result)      

    class internalLog():
        def update(log, duration_log, duration_state, backup_monthly):   
            try :
                state = FeatureSettingDB.updateByName('log', log)
                FeatureSettingDB.updateByName('durationStorageLog', duration_log)
                FeatureSettingDB.updateByName('durationStorageLogState', duration_state)
                FeatureSettingDB.updateByName('backupMonthlyLog', backup_monthly)

                toggle = settingFeature.internalLog.checkToggle()
                if toggle['value'] == '1':
                    result = {'state':'1', 'message':'Internal Log Enabled Successfully! The internal log feature has been successfully enabled.'}
                elif toggle['value'] == '0':
                    result = {'state':'1', 'message':'Internal Log Disabled Successfully! The internal log feature has been successfully disabled.'}
            except :
                result = {'state':'0', 'message':'Failed to Enable Internal Log!'}
            return json.dumps(result)
        
        def checkToggle():
            getData = FeatureSettingDB.toggle()
            toggleVal = getData[0]
            return toggleVal     
        
        def addRoutineInterval(interval, unit, state):
            try :
                isExists = IntervalRoutineLogDB.selectByIntervalAndUnit(interval, unit, state)
                if isExists :
                    result = {'state':'2', 'message':'Duplicate Data Detected! Sorry, there is already existing.'}
                else :
                    state = IntervalRoutineLogDB.insert(interval, unit, state)
                    result = {'state':state, 'message':'interval internal log added successfully!'}
            except Exception as e:
                    result = {'state':'0', 'message':'Failed to add interval internal log - ' + str(e)}
            return json.dumps(result)

        def updateRoutineInterval(interval, unit, state, idVal):
            try :
                isExists = IntervalRoutineLogDB.selectByIntervalAndUnit(interval, unit, state)
                if isExists :
                    result = {'state':'2', 'message':'Duplicate Data Detected! Sorry, there is already existing.'}
                else :
                    state = IntervalRoutineLogDB.update(interval, unit, state, idVal)
                    result = {'state':state, 'message':'Update Successfully! Your interval internal log have been successfully updated.'}
            except :
                result = {'state':'0', 'message':'Update Failed! there was an issue updating your interval internal log.'}
            return json.dumps(result)

        def deleteRoutineInterval(idVal):
            try :
                state_log = IntervalRoutineLogDB.deleteOne(idVal)
                state_sensor = SensorListDB.updateStateByLogId("0", idVal)
                if state_log == "1" and state_sensor == "1":
                    state = "1"
                else:
                    state = "0"
                result = {'state':state, 'message':'interval internal log deleted successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed delete interval internal log  - ' + str(e)}
            return json.dumps(result)

    class notification():
        # Function for update data notif setting
        def update(notification, notificationInterval, notificationUnit, notifNodeWeb, notifNodeWA, notifNodeEmail, notifNodeTelegram, notifSensorWeb, 
                               notifSensorWA, notifSensorEmail, notifSensorTelegram, notifActuatorWeb, notifActuatorWA, notifActuatorEmail, notifActuatorTelegram):
            nameSetting = ['notification', 'notificationInterval', 'notificationUnit', 'notificationNodeWeb', 'notificationNodeWA', 'notificationNodeEmail', 
                           'notificationNodeTelegram', 'notificationSensorWeb', 'notificationSensorWA', 'notificationSensorEmail', 'notificationSensorTelegram', 
                           'notificationActuatorWeb', 'notificationActuatorWA', 'notificationActuatorEmail', 'notificationActuatorTelegram']
            try :
                notifNodeWeb = notifNodeWeb if notifNodeWeb is not None else 0
                notifNodeWA = notifNodeWA if notifNodeWA is not None else 0
                notifNodeEmail = notifNodeEmail if notifNodeEmail is not None else 0
                notifNodeTelegram = notifNodeTelegram if notifNodeTelegram is not None else 0
                notifSensorWeb = notifSensorWeb if notifSensorWeb is not None else 0
                notifSensorWA = notifSensorWA if notifSensorWA is not None else 0
                notifSensorEmail = notifSensorEmail if notifSensorEmail is not None else 0
                notifSensorTelegram = notifSensorTelegram if notifSensorTelegram is not None else 0
                notifActuatorWeb = notifActuatorWeb if notifActuatorWeb is not None else 0
                notifActuatorWA = notifActuatorWA if notifActuatorWA is not None else 0
                notifActuatorEmail = notifActuatorEmail if notifActuatorEmail is not None else 0
                notifActuatorTelegram = notifActuatorTelegram if notifActuatorTelegram is not None else 0

                value = [notification, notificationInterval, notificationUnit, notifNodeWeb, notifNodeWA, notifNodeEmail, notifNodeTelegram, notifSensorWeb, 
                         notifSensorWA, notifSensorEmail, notifSensorTelegram, notifActuatorWeb, notifActuatorWA, notifActuatorEmail, notifActuatorTelegram]
                for num in range(len(nameSetting)):  
                    FeatureSettingDB.updateByName(nameSetting[num], value[num])
                result = {'state':'1', 'message':'Update Successfully! Your feature notification setting have been successfully updated.'} 
            except :
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue updating your feature notification setting.'}
            return json.dumps(result)

    class synchronize():
        # Function for update data sync setting
        def update(synchronize, synchronizeInterval, synchronizeUnit, syncNode, syncSensor, syncActuator):
            nameSetting = ['synchronize', 'synchronizeInterval', 'synchronizeUnit', 'syncNode', 'syncSensor', 'syncActuator']
            try : 
                syncNode = syncNode if syncNode is not None else 0
                syncSensor = syncSensor if syncSensor is not None else 0
                syncActuator = syncActuator if syncActuator is not None else 0
                
                value = [synchronize, synchronizeInterval, synchronizeUnit, syncNode, syncSensor, syncActuator]
                for num in range(len(nameSetting)):  
                    FeatureSettingDB.updateByName(nameSetting[num], value[num])
                result = {'state':'1', 'message':'Update Successful! Your feature synchronize setting have been successfully updated.'} 
            except :
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue updating - ' + str(e)}
            return json.dumps(result) 

    class monitoring():
        # Function for update data monitoring setting
        def update(routineMonitor, bufferMonitor, bufferMonitorInterval, bufferMonitorUnit, alarmMonitor, alarmMonitorUnit, alarmMonitorInterval):
            nameSetting = ['routineMonitor', 'bufferMonitor', 'bufferMonitorInterval', 'bufferMonitorUnit', 'alarmMonitor', 'alarmMonitorUnit', 'alarmMonitorInterval']
            value = [routineMonitor, bufferMonitor, bufferMonitorInterval, bufferMonitorUnit, alarmMonitor, alarmMonitorUnit, alarmMonitorInterval]
            try:
                for num in range(len(nameSetting)):  
                    FeatureSettingDB.updateByName(nameSetting[num], value[num])
                result = {'state':'1', 'message':'Update Successful! Your feature monitoring setting have been successfully updated.'} 
            except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue updating - ' + str(e)}     
            return json.dumps(result)
        
        # Function for add value routine monitoring
        def addRoutineInterval(interval, unit, routineState):
            try:
                isExists = IntervalRoutineMonitorDB.selectByIntervalAndUnit(interval, unit, routineState)
                if isExists:
                    result = {'state':'2', 'message':'Duplicate Data Detected! Sorry, there is already existing.'} 
                else :
                    state = IntervalRoutineMonitorDB.insert(interval, unit, routineState)
                    if state :
                        result = {'state':state, 'message':'routine monitoring interval added successfully!'} 
                    else :
                        result = {'state':'0', 'message':'Failed to add routine monitoring interval - error insert in database'}
            except Exception as e:
                    result = {'state':'0', 'message':'Failed to add routine monitoring interval - ' + str(e)} 
            return json.dumps(result)
        
        def updateRoutineInterval(interval, unit, routineState, idVal):
            try :
                isExists = IntervalRoutineMonitorDB.selectByIntervalAndUnit(interval, unit, routineState)
                if isExists:
                    result = {'state':'2', 'message':'Duplicate Data Detected! Sorry, there is already existing.'} 
                else :
                    state = IntervalRoutineMonitorDB.update(interval, unit, routineState, idVal)
                    result = {'state':state, 'message':'Update Successful! Your interval monitoring have been successfully updated.'} 
            except :
                result = {'state':'0', 'message':'Update Failed! there is this problem - ' + str(e)}
            return json.dumps(result)
        
        def deleteRoutineInterval(idVal):
            try:
                state_routine = IntervalRoutineMonitorDB.deleteOne(idVal)
                state_sensor = SensorListDB.updateStateByMonitorId("0", idVal)
                if state_routine == "1" and state_sensor == "1":
                    state = "1"
                else:
                    state = "0"
                result = {'state':state, 'message':'monitoring interval deleted successfully!'} 
            except Exception as e:
                result = {'state':'0', 'message':'Failed delete monitoring interval - ' + str(e)}
            return json.dumps(result)
