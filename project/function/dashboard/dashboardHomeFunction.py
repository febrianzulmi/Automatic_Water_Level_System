import datetime
import sys

sys.path.append('/connex/project/database')
from query_project_db import SystemServiceDB, SensorGroupDB, SensorListDB, ActuatorListDB, ActuatorGroupDB
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction
sys.path.append("/home/connex/project/function")
from dbFunction import dbFunction


class dashboardHome():
    def getDashboardInformation():
        dashboardData = {}
        serviceDataResult = dashboardHome.serviceDataInfo()
        dashboardData['nodeService'] = serviceDataResult['nodeService']
        dashboardData['sensorService'] = serviceDataResult['sensorService']
        dashboardData['actuatorService'] = serviceDataResult['actuatorService']
        dashboardData['sensorData'], dashboardData['sensorSummary'] = dashboardHome.sensorDataInfo(serviceDataResult['serviceData'])
        dashboardData['actuatorData'], dashboardData['actuatorSummary'] = dashboardHome.actuatorDataInfo(serviceDataResult['serviceData'])
        dashboardData['deviceSummary'] = dbFunction.getDeviceSetting()
        return dashboardData
    
    def serviceDataInfo():
        serviceData = SystemServiceDB.select()
        nodeService, sensorService, actuatorService = [], [], []

        if len(serviceData) > 0:
            x = 0
            while x < len(serviceData):
                if ("sensor" not in serviceData[x]["name"] and "dashboard" not in serviceData[x]["name"] and "actuator" not in serviceData[x]["name"] and 
                    "outback_api" not in serviceData[x]["name"] and "display" not in serviceData[x]["name"]):
                    serviceInfo = dashboardHome.serviceProcess(x, serviceData)
                    if serviceInfo:
                        nodeService.append(serviceInfo)
                elif "sensor" in serviceData[x]["name"]:
                    serviceInfo = dashboardHome.serviceProcess(x, serviceData)
                    if serviceInfo:
                        sensorService.append(serviceInfo)
                    else:
                        del serviceData[x]
                        continue
                elif "actuator" in serviceData[x]["name"]:
                    serviceInfo = dashboardHome.serviceProcess(x, serviceData)
                    if serviceInfo:
                        actuatorService.append(serviceInfo)

                x += 1 

        serviceDataResult = {
            "nodeService": nodeService,
            "sensorService": sensorService,
            "actuatorService": actuatorService,
            "serviceData": serviceData
        }

        return serviceDataResult
    
    def serviceProcess(x, serviceData):
        serviceName = '-'

        if serviceData[x]['name'] == 'nearon_routine':
            serviceName = 'Routine Monitoring'
        elif serviceData[x]['name'] == 'nearon_alarm':
            serviceName = 'Alarm Monitoring'
        elif serviceData[x]['name'] == 'nearon_buffer':
            serviceName = 'Buffer Monitoring'
        elif serviceData[x]['name'] == 'nearon_sync':
            serviceName = 'Synchronize'
        elif serviceData[x]['name'] == 'nearon_notif':
            serviceName = 'Notification'
        elif serviceData[x]['name'] == 'nearon_log':
            serviceName = 'Internal Log'
        elif serviceData[x]['name'] == 'nearon_auth':
            serviceName = 'Authentication'
        elif serviceData[x]['name'] == 'nearon_display':
            serviceName = 'Display'
        elif "sensor" in serviceData[x]['name']:
            groupId = serviceData[x]['name'].replace("sensor", "")
            group_id = SensorGroupDB.selectIsNumber(groupId)[0]["id"]
            groupData = SensorGroupDB.selectOneByState(group_id, "1")

            if not groupData:
                return None

            if len(groupData) == 1:
                serviceName = f"Sensor {groupData[0]['name']}"

        elif "actuator" in serviceData[x]['name']:
            number = serviceData[x]['name'].replace("actuator", "")
            actuatorData = ActuatorGroupDB.selectByNumber(number)
            if len(actuatorData) == 1:
                serviceName = f"Actuator {actuatorData[0]['name']}"
            else:
                serviceName = f"Actuator {number}"

        logTime = serviceData[x]["last_update"]
        log = serviceData[x]['state'] if serviceData[x]['state'] else "-"
        logTime = str(serviceData[x]['last_update']) if serviceData[x]['last_update'] else "-"

        serviceInfo = {
            'name': serviceName,
            'serviceName': serviceData[x]['name'],
            'log': log,
            'logTime': logTime,
            'state': serviceData[x]['service'],
            'autorun': serviceData[x]['enable']
        }

        return serviceInfo


    def actuatorDataInfo(serviceData):
        actuatorDataResult = []
        actuatorList = ActuatorListDB.selectFull()
        if len(actuatorList) > 0:
            for x in range(len(actuatorList)):
                actuatorData = {}
                serviceName = f"actuator{actuatorList[x]['actuator_group_number']}"
                serviceLog, serviceLogTime = '', ''
                serviceState, serviceAutorun = '', ''
                for y in range(len(serviceData)):
                    if serviceName == serviceData[y]['name']:
                        serviceState = serviceData[y]["service"]
                        serviceAutorun = serviceData[y]["enable"]
                        serviceLog = serviceData[y]["state"]
                        serviceLogTime = serviceData[y]["last_update"]
                        break
                actuatorData['serviceState'] = serviceState
                actuatorData['serviceAutorun'] = serviceAutorun 
                actuatorData['serviceLog'] = serviceLog 
                actuatorData['serviceLogTime'] = str(serviceLogTime)
                actuatorData['name'] = actuatorList[x]['name']
                if str(actuatorList[x]['server_value']) == '1': actuatorList[x]['server_value'] = 'Action'
                elif str(actuatorList[x]['server_value']) == '0': actuatorList[x]['server_value'] = 'No Action'

                if str(actuatorList[x]['last_server_value']) == '1': actuatorList[x]['last_server_value'] = 'Action'
                elif str(actuatorList[x]['last_server_value']) == '0': actuatorList[x]['last_server_value'] = 'No Action'

                if str(actuatorList[x]['last_action_value']) == '1': actuatorList[x]['last_action_value'] = 'Action'
                elif str(actuatorList[x]['last_action_value']) == '0': actuatorList[x]['last_action_value'] = 'No Action'

                if str(actuatorList[x]['last_action']) == '0': actuatorList[x]['last_action'] = 'Boot Sync'
                elif str(actuatorList[x]['last_action']) == '1': actuatorList[x]['last_action'] = 'Server'
                elif str(actuatorList[x]['last_action']) == '2': actuatorList[x]['last_action'] = 'Schedule'
                elif str(actuatorList[x]['last_action']) == '3': actuatorList[x]['last_action'] = 'Local'
                else: actuatorList[x]['last_action'] = 'N/A'

                
                if serviceState == 'active':
                    actuatorData['server_value'] = actuatorList[x]['server_value']
                    actuatorData['server_time'] = str(actuatorList[x]['server_sync_at'])
                    actuatorData['last_server_value'] = actuatorList[x]['last_server_value']
                    actuatorData['last_server_time'] = str(actuatorList[x]['last_server_sync_at'])
                    actuatorData['last_action_type'] = actuatorList[x]['last_action']
                    actuatorData['last_action_value'] = actuatorList[x]['last_action_value']
                    actuatorData['last_action_time'] = str(actuatorList[x]['last_action_at'])
                else:
                    actuatorData['server_value'] = "-"
                    actuatorData['server_time'] = "-"
                    actuatorData['last_server_value'] = "-"
                    actuatorData['last_server_time'] = "-"
                    actuatorData['last_action_type'] = "-"
                    actuatorData['last_action_value'] = "-"
                    actuatorData['last_action_time'] = "-"

                actuatorDataResult.append(actuatorData)
        actuatorSummary = {'totalActuator': len(actuatorList)}
        return actuatorDataResult, actuatorSummary

    def sensorDataInfo(serviceData):
        # groupSensor = SensorGroupDB.select()
        groupSensor = SensorGroupDB.selectByState("1")

        sensorDataResult = []
        countSensorActive, countSensor = 0, 0
        sensorNormal, sensorMin, sensorMax, sensorError, sensorAlarmInactive, sensorTolerance = 0, 0, 0, 0, 0, 0
        if len(groupSensor) > 0:
            for x in range(len(groupSensor)):
                groupSensorData = {}
                sensorService = 'sensor{}'.format(groupSensor[x]['number'])
                serviceState, serviceAutorun = '', ''
                for y in range(len(serviceData)):
                    if serviceData[y]["name"] ==  sensorService:
                        serviceState = serviceData[y]["service"]
                        serviceAutorun = serviceData[y]["enable"]
                        serviceLog = serviceData[y]["state"]
                        serviceLogTime = serviceData[y]["last_update"]
                        break
                groupSensorData['serviceState'] = serviceState
                groupSensorData['serviceAutorun'] = serviceAutorun 
                groupSensorData['serviceLog'] = serviceLog 
                groupSensorData['serviceLogTime'] = str(serviceLogTime)
                groupSensorData['groupName'] = "Sensor {}".format(groupSensor[x]['name'])
                groupSensorData['groupId'] = "{}".format(groupSensor[x]['id'])
                groupSensorData['sensorList'] = []   
                # sensorDatabase = SensorListDB.selectByGroupFull(groupSensor[x]['id'])   
                sensorDatabase = SensorListDB.selectGroupByState(groupSensor[x]['id'], "1", "1")
                for i in range(len(sensorDatabase)):
                    sensorData = {}
                    countSensor += 1
                    # if sensorDatabase[i]['state'] == '1':
                    #     countSensorActive += 1
                    sensorData['name'] = sensorDatabase[i]['name']
                    # baseOid = OidSensorFunction.getBaseOID(sensorDatabase[i]['group_id'])
                    baseOid = "1.3.6.1.4.1.19719"
                    sensorData['oid'] = f"{baseOid}.{groupSensor[x]['oid']}.{str(sensorDatabase[i]['oid'])}"
                    if sensorDatabase[i]['conditions'] == 'Normal':
                        sensorNormal += 1
                    elif sensorDatabase[i]['conditions'] == 'Alarm Min':
                        sensorMin += 1  
                    elif sensorDatabase[i]['conditions'] == 'Alarm Max':
                        sensorMax += 1  
                    elif sensorDatabase[i]['conditions'] == 'Alarm Error':
                        sensorError += 1            
                    elif sensorDatabase[i]['conditions'] == 'Alarm Inactive':
                        sensorAlarmInactive += 1      
                    else:
                        if 'Tolerance' in sensorDatabase[i]['conditions']:
                            sensorTolerance += 1  
                    if 'smoke' in sensorDatabase[i]['name'].lower():
                        if str(sensorDatabase[i]['value']) == '1': sensorDatabase[i]['value'] = 'Detect'
                        elif str(sensorDatabase[i]['value']) == '0': sensorDatabase[i]['value'] = 'No Detect'
                        else: sensorDatabase[i]['value'] = 'N/A'
                    if 'door' in sensorDatabase[i]['name'].lower():
                        if str(sensorDatabase[i]['value']) == '1': sensorDatabase[i]['value'] = 'Open'
                        elif str(sensorDatabase[i]['value']) == '0': sensorDatabase[i]['value'] = 'Close'
                        else: sensorDatabase[i]['value'] = 'N/A'
                    if 'water' in sensorDatabase[i]['name'].lower():
                        if str(sensorDatabase[i]['value']) == '1': sensorDatabase[i]['value'] = 'No Detect'
                        elif str(sensorDatabase[i]['value']) == '0': sensorDatabase[i]['value'] = 'Detect'
                        else: sensorDatabase[i]['value'] = 'N/A'
                    if 'stateac' in sensorDatabase[i]['sensor_id'].lower():
                        if str(sensorDatabase[i]['value']) == '1': sensorDatabase[i]['value'] = 'On'
                        elif str(sensorDatabase[i]['value']) == '0': sensorDatabase[i]['value'] = 'Off'
                        else: sensorDatabase[i]['value'] = 'N/A'     
                    if serviceState == 'active':
                        if sensorDatabase[i]['value'] == '' or sensorDatabase[i]['value'] == None:
                            sensorData['value'] = '-'
                            sensorData['valueAt'] = '-'
                        else:
                            sensorData['value'] = "{} {}".format(sensorDatabase[i]['value'], sensorDatabase[i]['unit'])  
                            sensorData['valueAt'] = str(sensorDatabase[i]['timestamp'])   
                        sensorData['condition'] = sensorDatabase[i]['conditions']     
                        timeNow = datetime.datetime.now()
                        diffTime = timeNow - sensorDatabase[i]['timestamp']
                        sensorData['diffTime'] = diffTime.seconds
                    else:
                        sensorData['value'] = '-'        
                        sensorData['valueAt'] = '-'
                        sensorData['condition'] = '-'
                    groupSensorData['sensorList'].append(sensorData)  
                sensorDataResult.append(groupSensorData)   
        sensorSummary = {}
        sensorSummary['totalSensor'] = countSensor    
        sensorSummary['totalAlarmNormal'], sensorSummary['totalAlarmInactive'], sensorSummary['totalAlarmTolerance'] = sensorNormal, sensorAlarmInactive, sensorTolerance 
        sensorSummary['totalAlarmMax'], sensorSummary['totalAlarmMin'], sensorSummary['totalAlarmError'] = sensorMax, sensorMin, sensorError       
        return sensorDataResult, sensorSummary 