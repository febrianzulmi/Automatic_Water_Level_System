from math import e
import datetime
import json
import os
import requests 
import random
import shutil
import subprocess 
import string, sys
from threading import Thread

from sql import *
from sql_connex import snmp
from query_project_db import LogNotifDB, SensorListDB


class ThreadWithReturnValues(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def generateIdSensorData(flag, type):
      id = processGenerateId(flag, type)
      while True:
         if flag == 'environment':
            if type == 'device':
               checkId = environmentDeviceDB.selectById(id)

            elif type == 'master-sensor':
               checkId = environmentMasterSensorDB.selectById(id)

            elif type == 'master-parameter':
               checkId = environmentMasterParameterDB.selectById(id)

         elif flag == 'power':
            if type == 'device':
               checkId = powerDeviceDB.selectById(id)

            elif type == 'master-sensor':
               checkId = powerMasterSensorDB.selectById(id)

            elif type == 'master-parameter':
               checkId = powerMasterParameterDB.selectById(id)

         elif flag == 'remote':
            if type == 'device':
               pass

         if len(checkId) == 0:
            break
         else:
            id = processGenerateId(flag, type)
      return id

def processGenerateId(flag, type):
      id = ''
      if flag == 'environment':
         id = 'E'
      elif flag == 'power':
         id = 'P'   
      elif flag == 'remote':
         id = 'R'   
      if type == 'device':
         id += 'ED'
      elif type == 'master-sensor':
         id += 'EMS'
      elif type == 'master-parameter':
         id += 'EMP'
      generate = getRandomID(5)
      id += '-' + str(generate)
      return id


def getPort():
    try:
       f = open("../../platform/ports.conf","r")
       port = f.read()
       f.close()
       port = port.replace("\n","")
    except:
       port = '80'
    return port

# Check Session New
def checkSession():
   port = getPort()
   try:
      sessionData = requests.get('http://localhost:' + port + '/api/project/session')
      sessionData = sessionData.text
      sessionData = json.loads(sessionData)
   except Exception as e:
      sessionData = {'id': 0, 'username': '', 'level': 0, 'state': 0}
   return sessionData

def getFormula():
   getData = calibrateFormula.select()
   formula = {}
   count = 0
   for item in getData :
      formula[count]={
         'id': item['id'],
         'name': item['name'],
         'sample': item['sample'],
         'koef_a': item['koef_a'],
         'koef_b': item['koef_b'],
         'calculate_time': item['calculate_time'].isoformat().replace('T',' ')            
      }
      count+=1
   return formula

# Get Data New
def getData():
   port = getPort()
   try:
      projectData = requests.get('http://localhost:' + port + '/api/project')
      projectData = projectData.text
      projectData = json.loads(projectData)
   except Exception as e:
      projectData = {'name': '', 'port' : None, 'gateway': 0, 'node': 0, 'protocol': 0}
   return projectData

# Get All Device Configuration Data
def getDeviceSetting():
   getData = deviceSettingDB.select()
   deviceSetting = {}
   if getData :
      for item in getData :
            item['updatedAt'] = item['updatedAt'].isoformat()
            if item['name'] in ['uid', 'name', 'version'] :
               deviceSetting[item['name']]= item['value']      
   else :
      deviceSetting = {'uid': '', 'name': '', 'version': ''}
   return deviceSetting

# New Function Get Connex Setting
def getConnexSetting():
   getData = connexSettingDB.select()
   feature_setting = {}
   if getData :
      for item in getData :     
         connexSetting[item['name']] = item['value']          
   return connexSetting

def getBaseOID(group_id):
   getData = params.selectByGroupParameter(group_id, 'parent_oid')
   if len(getData) == 1:
      baseOid = getData[0]['value']
   else :
      baseOid = 'Undefined'
   return baseOid

#New
def getSensorSetting(group_id):
    try:
      get = groups.selectOne(group_id)
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

#New
def getParameterGroupSensor(group_id):
   parameterData = params.selectByGroupSensor(group_id)
   if len(parameterData) > 0:
      result = {}
      for item in parameterData:
         result[item['parameter']] = item['value']
   else :
      result = {}
   return result

#New
def getParameterListSensor(group_id):
   parameterData = paramList.selectParameterListSensor(group_id)   
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

#New
def getParameterActuator(actuator_id):
    parameterData = actuator_param.selectByActuatorIdFull(actuator_id)
    if len(parameterData) > 0:
       result = {}
       for item in parameterData:
          result[item['parameter']] = item['value']
    else :
       result = {}
    return result

def getValueSensor(id):
    sensor_value = []
    for i in range(len(id)):
        values = sensor.selectById(id[i])
        value = '-'
        for i in values:
            value = i[8]
        sensor_value.append(value)
    return sensor_value

def checkDetailService(nama):
    detail =  subprocess.Popen("systemctl status " + nama + " | grep since", shell=True, stdout=subprocess.PIPE)
    (out, err) = detail.communicate()
    detail = out.decode('utf-8')
    detail = detail.replace('\n','')
    search1 = detail.find("since")
    search2 = detail.find("WIB")
    search3 = detail.find("ago")
    last_run = detail[search1+6:search2-1]
    since = detail[search2+5:search3]
    return last_run, since

def checkActiveService(nama):
    active =  subprocess.Popen(["systemctl", "is-active",  nama], stdout=subprocess.PIPE)
    (out, err) = active.communicate()
    active = out.decode('utf-8')
    active = active.replace('\n','')
    return active

def checkEnableService(nama):
    enable =  subprocess.Popen(["systemctl", "is-enabled",  nama], stdout=subprocess.PIPE)
    (outs, errs) = enable.communicate()
    enable = outs.decode('utf-8')
    enable = enable.replace('\n','')
    return enable

# New Get Service State
def getServiceState(serviceName):
   """Get Service State
   Return serviceStatus, serviceState, and serviceLastUpdated
   """
   getData = system.selectByName(serviceName)
   serviceData = {}

   if len(getData) > 0:      
      newData = getData[0]  
      serviceData.update({'state': newData['service']})
      serviceData.update({'log': newData['state']})
      serviceData.update({'last_update': newData['last_update']})
                  
   else :
      serviceData.update({'state': checkActiveService(serviceName)})
      serviceData.update({'log': '-'})
      serviceData.update({'last_update': '-'})
   return serviceData

# New Get Community SNMP
def getSnmpSetting(params):
   getData = snmp.selectByName(params)
   snmpData = {}
   if getData :
      snmpData = getData[0]
   else :
      snmpData = {}

   return snmpData

def oidWriteFile(oid_file, oid, oid_tipe, oid_value):
    try:
        f = open(str(oid_file), "w")
        f.write("." + str(oid) + ".0")
        f.write("\n")
        f.write(str(oid_tipe))
        f.write("\n")
        f.write(str(oid_value))
        f.write("\n")
        f.close()
        state = 1
    except Exception as e:
        state = 0
    return state

def createOID():
    def handleValue(oid_type):
        if oid_type == 0:
           values = '0'
        else:
           values = 'N/A'
        return values
    base = "/home/connex"
    path_snmp =  base + "/project/sensor/oid"
    os.system("sudo rm -r " + path_snmp)
    cek = os.path.exists(path_snmp)
    if cek == False:
       os.system("sudo mkdir " + path_snmp)
    if base != '':
       sensors  = SensorListDB.select()
       if sensors:
          shutil.copy(base + '/platform/storage/snmpd.conf.master', '/etc/snmp/snmpd.conf')
          files = open("/etc/snmp/snmpd.conf", "a")
          files.write("\n")
          for itemSensor in range(len(sensors)):
              id = sensors[itemSensor]['id']
              oid_sensor = sensors[itemSensor]['oid']
              base_oid = getBaseOID(sensors[itemSensor]['group_id'])
              oid = base_oid + "." + str(oid_sensor)
              oid_script = path_snmp + "/" + oid + ".sh"
              cek_script = os.path.exists(oid_script)
              if cek_script == False:
                 f = open(oid_script, "w")
                 f.write("#!/bin/bash\n")
                 f.write("cat /tmp/" + oid)
                 f.close()
              sensorByID = SensorListDB.selectById(id)
              if sensorByID:
                 for itemSensor in sensorByID:
                     value = sensorByID[0]['value']
                     oid_tipe = sensorByID[0]['oid_tipe']
                 if value == None:
                    value = handleValue(oid_tipe)
              else:
                 value = '0'
                 oid_tipe = 0
              if oid_tipe == 0:
                 oid_tipe = 'integer'
                 if value == 'N/A':
                    value = 0
                 oid_value = int(float(value)*100)
              else:
                 oid_tipe = 'string'
                 if value == 0:
                    value = 'N/A'
                 oid_value = value
              oid_file = "/tmp/" + str(oid)
              state = oidWriteFile(oid_file, oid, oid_tipe, oid_value)
              files.write("pass ." + oid + " /bin/sh " + oid_script + "\n")
          files.close()
          os.system("sudo systemctl snmpd status")

def generateOidAtBoot():
   dataSensor = getDataSensor.all()
   for i in range(dataSensor['numSensor']):
      serviceName = "sensor" + str(dataSensor['groupId'][i])
      serviceData = getServiceState(serviceName)
      base_oid = getBaseOID(dataSensor['groupId'][i])
      sensor_data = sensor.selectById(dataSensor['id'][i])
      last_oid = dataSensor['sensorOid'][i]
      oid_tipe = dataSensor['sensorDatatype'][i]
      if serviceData['state'] != "active":
         if 'state_sensor' != 'Success':
            if oid_tipe == 0:
               dataSensor['sensorValue'][i] = '0'
            else:
               dataSensor['sensorValue'][i] = 'N/A'
      oid = str(base_oid) + "." + str(last_oid)
      oid_file = "/tmp/" + str(oid)
      f = open(str(oid_file), "w")
      f.write("." + str(oid) + ".0")
      f.write("\n")
      if oid_tipe == 0:
         f.write("integer")
         value = int(float(dataSensor['sensorValue'][i])*100)
      else:
         f.write("string")
         value = dataSensor['sensorValue'][i]
      f.write("\n")
      f.write(str(value))
      f.write("\n")
      f.close()
      print("Sensor " + str(dataSensor['sensorName'][i]) + " (" + str(oid) + ") Updated with Value " + str(value))

class getDataSensor():
    def handleValueType(oid_type):
        if oid_type == 0:
           value = '0'
        else:
           value = 'N/A'
        return value

    def handleValueService(group_id, oid_type, value):
        serviceName = "sensor" + str(group_id)
        service, state_sensor, last_update = getServiceState(serviceName)
        service = "active"
        if service == "active":
           if 'Success' not in state_sensor:
              value = getDataSensor.handleValueType(oid_type)
        else:
           value = getDataSensor.handleValueType(oid_type)
        return value

    def handleValueDB(value, oid_type):
        if value == None:
           value = getDataSensor.handleValueType(oid_type)
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
        value = getDataSensor.handleValueDB(sensors[i]['value'], sensors[i]['oid_tipe'])
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
      dataSensor = getDataSensor.initiateSensor()
      if len(sensors) > 0:
         for i in range(len(sensors)):
            dataSensor = getDataSensor.assignSensor(i, sensors, dataSensor)
      dataSensor['numSensor'] = len(sensors)
      return dataSensor

    def all():
        sensors  = SensorListDB.select()
        dataSensor = getDataSensor.initiateSensor() # initial zero value
        if len(sensors) > 0:
           for i in range(len(sensors)):
               dataSensor = getDataSensor.assignSensor(i, sensors, dataSensor) # append value
        dataSensor['numSensor'] = len(sensors)
        return dataSensor
    
    def byRoutineMonitorInterval(routineMonitorIntervalId):
      sensors  = SensorListDB.selectByRoutineMonitorInterval(routineMonitorIntervalId)
      dataSensor = getDataSensor.initiateSensor()
      if len(sensors) > 0:
         for i in range(len(sensors)):
            dataSensor = getDataSensor.assignSensor(i, sensors, dataSensor)
      dataSensor['numSensor'] = len(sensors)
      return dataSensor

    def byLogInterval(logIntervalId):
      sensors  = SensorListDB.selectByLogInterval(logIntervalId)
      dataSensor = getDataSensor.initiateSensor()
      if len(sensors) > 0:
         for i in range(len(sensors)):
            dataSensor = getDataSensor.assignSensor(i, sensors, dataSensor)
      dataSensor['numSensor'] = len(sensors)
      return dataSensor

def calibrateSensor(dataSensor, value):
    calibrateValue = []
    for i in range(dataSensor['numSensor']):
        global values
        values = ''
        if str(dataSensor['sensorCalibration'][i]) == '0':
           coefA, coefB = 1, 0
           values = value[i]
        elif str(dataSensor['sensorCalibration'][i]) == '1':
           getFormula = calibrateFormula.selectById(dataSensor['sensorFormula'][i])
           for y in getFormula:
               coefA = float(y[3])
               coefB = float(y[4])
           values = (coefA*value[i]) + coefB
           values = round(values,2)
           if values < 0:
              values = 0.00
        calibrateValue.append(values)
    return calibrateValue

def createNotifSensor(id_sensor, name_sensor, value, config_alarm, type_alarm, unit, timestamp, connexSetting):
   settingData = getDeviceSetting()
   unix = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
   deviceName = settingData['name'] + " (" + settingData['uid'] + ")"
   if unit == None: unit = ""
   if unit == "#": unit = "%23"
   if unit == " ": unit = ""
   if "door" in name_sensor.lower():
      if str(value) == "1": value = "1 (Open)"
      elif str(value) == "0": value = "0 (Close)"
      else: "-1 (N/A)"
   elif "smoke" in name_sensor.lower():
      if str(value) == "1": value = "1 (Detect)"
      elif str(value) == "0": value = "0 (No Detect)" 
      else: value = "-1 (N/A)" 
   elif "water" in name_sensor.lower():
      if str(value) == "1": value = "1 (No Detect)"
      elif str(value) == "0": value = "0 (Detect)"
      else: value = "-1 (N/A)"   
   if unit != "":
      value = f"{value} {unit}"
   subjectNotification = 'Node {} Notification'.format(str(deviceName))
   emailMessage = f"Type Notification : <b><i>Sensor Alarm</i></b><br>" \
                  f"Sensor : <b><i>{name_sensor}</i></b><br>" \
                  f"Value : <b><i>{value}</i></b><br>"
   telegramMessage = f"<b>{subjectNotification} %23{str(unix)}</b><br><br>" \
                     f"Type Notification : <b><i>Sensor Alarm</i></b><br>" \
                     f"Sensor : <b><i>{name_sensor}</i></b><br>" \
                     f"Value : <b><i>{value}</i></b><br>"
   whatsappMessage = f"*{subjectNotification} %23{str(unix)}*<br><br>" \
                     f"Type Notification : *_Sensor Alarm_*<br>" \
                     f"Sensor : *_{name_sensor}_*<br>" \
                     f"Value : *_{value}_*<br>"
   webMessage = f"Sensor {name_sensor} (Node {deviceName}) values is {value}"

   if type_alarm == "Alarm Error":
      emailMessage += f"Condition : <b><i>Alarm Error</i></b><br>"
      telegramMessage += f"Condition : <b><i>Alarm Error</i></b><br>"
      whatsappMessage += f"Condition : *_Alarm Error_*<br>"
      webMessage += f" reach error condition at {str(timestamp)} GMT%2B7"

   else:
      limitMin, limitMax = str(config_alarm['min']), str(config_alarm['max'])
      if unit != "":
         limitMin = f"{limitMin} {unit}"
         limitMax = f"{limitMax} {unit}"
      
      if str(config_alarm['config']) == "3":
         emailMessage += f"Limit Min Value : <b><i>{limitMin}</i></b><br>" \
                         f"Limit Max Value : <b><i>{limitMax}</i></b><br>" \
                         f"Condition : <b><i>{type_alarm}</i></b><br>" \
                         f"Configuration Alarm : <b><i>Alarm Min & Alarm Max</i></b><br>" 
         telegramMessage += f"Limit Min Value : <b><i>{limitMin}</i></b><br>" \
                            f"Limit Max Value : <b><i>{limitMax}</i></b><br>" \
                            f"Condition : <b><i>{type_alarm}</i></b><br>" \
                            f"Configuration Alarm : <b><i>Alarm Min %26 Alarm Max</i></b><br>" 
         whatsappMessage += f"Limit Min Value : *_{limitMin}_*<br>" \
                            f"Limit Max Value : *_{limitMax}_*<br>" \
                            f"Condition : *_{type_alarm}_*<br>" \
                            f"Configuration Alarm : *_Alarm Min %26 Alarm Max_*<br>"
      elif str(config_alarm['config']) == "2":
         emailMessage += f"Limit Max Value : <b><i>{limitMax}</i></b><br>" \
                         f"Condition : <b><i>{type_alarm}</i></b><br>" \
                         f"Configuration Alarm : <b><i>Alarm Max Only</i></b><br>" 
         telegramMessage += f"Limit Max Value : <b><i>{limitMax}</i></b><br>" \
                            f"Condition : <b><i>{type_alarm}</i></b><br>" \
                            f"Configuration Alarm : <b><i>Alarm Max Only</i></b><br>" 
         whatsappMessage += f"Limit Max Value : *_{limitMax}_*<br>" \
                            f"Condition : *_{type_alarm}_*<br>" \
                            f"Configuration Alarm : *_Alarm Max Only_*<br>"
      elif str(config_alarm['config']) == "1":
         emailMessage += f"Limit Min Value : <b><i>{limitMin}</i></b><br>" \
                         f"Condition : <b><i>{type_alarm}</i></b><br>" \
                         f"Configuration Alarm : <b><i>Alarm Min Only</i></b><br>" 
         telegramMessage += f"Limit Min Value : <b><i>{limitMin}</i></b><br>" \
                            f"Condition : <b><i>{type_alarm}</i></b><br>" \
                            f"Configuration Alarm : <b><i>Alarm Min Only</i></b><br>" 
         whatsappMessage += f"Limit Min Value : *_{limitMin}_*<br>" \
                            f"Condition : *_{type_alarm}_*<br>" \
                            f"Configuration Alarm : *_Alarm Min Only_*<br>"
      if type_alarm == "Normal":
         webMessage += f" reach normal condition at {str(timestamp)} GMT%2B7"
      elif type_alarm == 'Alarm Min':
         webMessage += f" reach the lowest value limit {str(limitMin)} at {str(timestamp)} GMT%2B7"
      elif type_alarm == 'Alarm Max':
         webMessage += f" reach the highest value limit {str(limitMax)} at {str(timestamp)} GMT%2B7"
          
   emailMessage += f"Timestamp : <b><i>{str(timestamp)} GMT%2B7</i></b>"
   telegramMessage += f"Timestamp : <b><i>{str(timestamp)} GMT%2B7</i></b>"
   whatsappMessage += f"Timestamp : *_{str(timestamp)} GMT%2B7_*"
   if int(connexSetting['notificationSensorWeb']) == 1:
      LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Web", "-", webMessage, "Waiting", timestamp)
   if int(connexSetting['notificationSensorWA']) == 1:
      LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Whatsapp", "-", whatsappMessage, "Waiting", timestamp)
   if int(connexSetting['notificationSensorEmail']) == 1:
      LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Email", subjectNotification, emailMessage, "Waiting", timestamp)
   if int(connexSetting['notificationSensorTelegram']) == 1:
      LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Telegram", "-", telegramMessage, "Waiting", timestamp)

def createNotifNode(type, message, connexSetting):
    deviceSetting = getDeviceSetting()
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    unix = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    unix = int(unix.timestamp())
    deviceName = deviceSetting['name'] + " (" + deviceSetting['uid'] + ")"
    subjectNotification = 'Node {} Notification'.format(str(deviceName))
    if type == 'Power On':
       whatsappMessage = f"*{subjectNotification} %23{str(unix)}*<br><br>" \
                         f"Type Notification : *_Device Information_*<br>" \
                         f"Information : *_Power On_*<br>" \
                         f"Timestamp : *_{timestamp} GMT%2B7_*"
       emailMessage = f"Type Notification : <b><i>Device Information</i></b><br>" \
                      f"Information : <b><i>Power On</i></b><br>" \
                      f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
       telegramMessage = f"<b>{subjectNotification} %23{str(unix)}</b><br><br>" \
                         f"Type Notification : <b><i>Device Information</i></b><br>" \
                         f"Information : <b><i>Power On</i></b><br>" \
                         f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
       webMessage = f"Node {deviceSetting['name']} with Node ID {deviceSetting['uid']} is Power On at {timestamp} GMT%2B7"

    elif type == 'Service Error':
       whatsappMessage = f"*{subjectNotification} %23{str(unix)}*<br><br>" \
                         f"Type Notification : *_Service Warning_*<br>" \
                         f"Service : *_{message['service']}_*<br>" \
                         f"Error : *_{message['type']} ({message['message']} in Line {message['line']})_*<br>" \
                         f"Timestamp : *_{timestamp} GMT%2B7_*"
       emailMessage = f"<b>{subjectNotification} %23{str(unix)}</b><br><br>" \
                      f"Type Notification : <b><i>Service Warning</i></b><br>" \
                      f"Service : <b><i>{message['service']}</i></b><br>" \
                      f"Error : <b><i>{message['type']} ({message['message']} in Line {message['line']})</i></b><br>" \
                      f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
       telegramMessage = f"<b>{subjectNotification} %23{str(unix)}</b><br><br>" \
                         f"Type Notification : <b><i>Service Warning</i></b><br>" \
                         f"Service : <b><i>{message['service']}</i></b><br>" \
                         f"Error : <b><i>{message['type']} ({message['message']} in Line {message['line']})</i></b><br>" \
                         f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
       webMessage = f"Service {message['service']} (Node {deviceSetting['name']} with Node ID {deviceSetting['uid']} error {message['type']} ({message['message']}) in line {message['line']} at {timestamp} GMT%2B7"

    if int(connexSetting['notificationNodeWeb']) == 1:
       logNotif.insert("Device", "-", type, "Web","-", webMessage, "Waiting", timestamp)
    if int(connexSetting['notificationNodeTelegram']) == 1:
       logNotif.insert("Device", "-", type, "Telegram", "-", telegramMessage, "Waiting", timestamp)
    if int(connexSetting['notificationNodeWA']) == 1:
       logNotif.insert("Device", "-", type, "Whatsapp", "-", whatsappMessage, "Waiting", timestamp)
    if int(connexSetting['notificationNodeEmail']) == 1:
       logNotif.insert("Device", "-", type, "Email", subjectNotification, emailMessage, "Waiting", timestamp)

def createNotifActuator(id_act, state, value, timestamp, control):
    deviceSetting = getDeviceSetting()
    feature_setting = getConnexSetting()
    unix = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    unix = int(unix.timestamp())
    act_detail = actuator.selectById(id_act)
    for x in act_detail:
        actuator_name = x['name']
        actuator_id = x['actuator_id']
    if str(value) == '1':
       val = "ON"
    else:
       val = "OFF"
    if str(state) == '0':
       state = "Boot"
    elif str(state) == '1':
       state = "Server Remote"
    elif str(state) == '2':
       state = "Schedule"
    elif str(state) == '3':
       state = "Local Remote"

    subject = f"Node {deviceSetting['name']} - Actuator {actuator_name} Status Notification %23" \
              f"{str(unix)}"

    email_message = f"Trigger Control : <b><i>{state}</i></b><br>" \
                  f"Value : <b><i>{val}</i></b><br>" \
                  f"Control : <b><i>{control}</i></b><br>" \
                  f"Timestamp : <b><i>{timestamp} GMT%2B7</i><br>"

    wa_message = f"<b>{subject}</b><br><br>" \
               f"Trigger Control : <b>{state}</b><br>" \
               f"Value : <b>{val}</b><br>" \
               f"Control : <b>{control}</b><br>" \
               f"Timestamp : *_{timestamp} GMT%2B7_*<br>" 

    web_message = f"Node {deviceSetting['name']} - Actuator {actuator_name} is controlled by {state} with " \
                  f"value {val} and control {control} at {timestamp} GMT%2B7"


    tl_msg = f"<b>{subject}</b><br><br>" \
             f"Trigger Control : <b><i>{state}</i></b><br>" \
             f"Value : <b><i>{val}</i></b><br>" \
             f"Control : <b><i>{control}</i></b><br>" \
             f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b><br>" 

    if int(connexSetting['notificationActuatorWeb']) == 1:
       data = logNotif.insert("Actuator", actuator_name , state, "Web","-", web_message, "Waiting", timestamp)
    if int(connexSetting['notificationActuatorWA']) == 1:
      logNotif.insert("Actuator", actuator_name , state, "Whatsapp", "-", wa_message, "Waiting", timestamp)
    if int(connexSetting['notificationActuatorEmail']) == 1:
      logNotif.insert("Actuator", actuator_name , state, "Email", subject, email_message, "Waiting", timestamp)
    if int(connexSetting['notificationActuatorTelegram']) == 1:
       logNotif.insert("Actuator", actuator_name , state, "Telegram", "-", tl_msg, "Waiting", timestamp)

def serviceError(name, e):
    import sys, time, datetime
    exc_type, exc_value, exc_traceback = sys.exc_info()
    error_details = {
      'service' : name,
      'filename' : str(exc_traceback.tb_frame.f_code.co_filename),
      'line'  : str(exc_traceback.tb_lineno),
      'type'    : str(exc_type.__name__),
      'message' : str(e)
    }
    message = error_details['type'] + " (" + error_details['message'] + ")"
    timestamp = datetime.datetime.now()
    logError.insert(error_details['service'], message, error_details['filename'], error_details['line'], timestamp)
    system.updateStatusByName('Service Error - ' + message, timestamp, name)
    feature_setting = getConnexSetting()
    if int(connexSetting['notification']) == 1:
       createNotifNode("Service Error", error_details, connexSetting)
    print("Error : ", error_details)
    print("")
    time.sleep(10)

def getRandomID(length):
    import random, string
    id = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(length)])
    return id
