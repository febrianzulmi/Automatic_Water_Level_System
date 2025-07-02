import json
import random
import sys
import string
from threading import Thread

import requests
import subprocess

sys.path.append('/home/connex/project/database')
from query_project_db import (SensorGroupDB, SensorListDB, SensorParameterGroupDB, SensorParameterListDB, EnvironmentDeviceDB, EnvironmentMasterSensorDB, 
                              EnvironmentMasterParameterDB, PowerDeviceDB, PowerMasterParameterDB, PowerMasterSensorDB, ActuatorListDB, ActuatorParameterListDB, 
                              ActuatorScheduleDB, ActuatorGroupDB, ActuatorParameterGroupDB, RtuParameterDB)


class generalFunction():
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
        

    class GenerateId():
        def generateIdNearon(flag, type):
            id = generalFunction.GenerateId.processGenerateId(flag, type)
            while True:
                if flag == "sensor":
                    if type == "sensor-group":
                        checkId = SensorGroupDB.selectOne(id)
                    elif type == "sensor-list":
                        checkId = SensorListDB.selectById(id)
                    elif type == "parameter-group":
                        checkId = SensorParameterGroupDB.selectOne(id)
                    elif type == "parameter-list":
                        checkId = SensorParameterListDB.selectById(id)
                
                elif flag == 'environment':
                    if type == 'device':
                        checkId = EnvironmentDeviceDB.selectById(id)
                    elif type == 'master-sensor':
                        checkId = EnvironmentMasterSensorDB.selectById(id)
                    elif type == 'master-parameter':
                        checkId = EnvironmentMasterParameterDB.selectById(id)

                elif flag == 'power':
                    if type == 'device':
                        checkId = PowerDeviceDB.selectById(id)
                    elif type == 'master-sensor':
                        checkId = PowerMasterSensorDB.selectById(id)
                    elif type == 'master-parameter':
                        checkId = PowerMasterParameterDB.selectById(id)

                elif flag == 'remote':
                    if type == 'device':
                        pass

                elif flag == 'actuator':
                    if type == "actuator-group":
                        checkId = ActuatorGroupDB.selectById(id)
                    elif type == "actuator-list":
                        checkId = ActuatorListDB.selectById(id)
                    elif type == "actuator-parameter-group":
                        checkId = ActuatorParameterGroupDB.selectById(id)
                    elif type == "actuator-parameter-list":
                        checkId = ActuatorParameterListDB.selectById(id)
                    elif type == "actuator-schedule":
                        checkId = ActuatorScheduleDB.selectById(id)
                
                elif flag == "rtu":
                    if type == "rtu-device":
                        checkId = RtuDeviceDB.selectById(id)
                        pass
                    elif type == "rtu-parameter":
                        checkId = RtuParameterDB.selectById(id)

                if len(checkId) == 0:
                    break
                else:
                    id = generalFunction.GenerateId.processGenerateId(flag, type)
            return id


        def processGenerateId(flag, type):
            id = ''
            if flag == "sensor":
                id = "P"
            elif flag == 'environment':
                id = 'E'
            elif flag == 'power':
                id = 'P'   
            elif flag == 'remote':
                id = 'R'
            elif flag == "actuator":
                id = 'P'
            elif flag == "rtu":
                id = "RTU"
            
            if type == "sensor-group":
                id += "GS"
            elif type == "sensor-list":
                id += "LS"
            elif type == "parameter-group":
                id += "PG"
            elif type == "parameter-list":
                id += "PL"
            elif type == 'device':
                id += 'ED'
            elif type == 'master-sensor':
                id += 'EMS'
            elif type == 'master-parameter':
                id += 'EMP'
            elif type == "actuator-group":
                id += "AG"
            elif type == "actuator-list":
                id += "AL"
            elif type == "actuator-parameter-group":
                id += "APG"
            elif type == "actuator-parameter-list":
                id += "APL"
            elif type == "actuator-schedule":
                id += "ALS"
            elif type == "rtu-device":
                id += "EXT"
            elif type == "rtu-parameter":
                id += "PRM"

            generate = generalFunction.getRandomID(5)
            id += '-' + str(generate)
            return id
    
    
    def getProjectSetting():
        port = generalFunction.getPortSetting()
        try:
            projectData = requests.get('http://localhost:' + port + '/api/project')
            projectData = projectData.text
            projectData = json.loads(projectData)
        except Exception as e:
            projectData = {'name': '', 'port' : None, 'gateway': 0, 'node': 0, 'protocol': 0}
        return projectData


    def getPortSetting():
        try:
            f = open("/home/connex/platform/ports.conf","r")
            port = f.read()
            f.close()
            port = port.replace("\n","")
        except:
            port = '80'
        return port


    def checkSession():
        port = generalFunction.getPortSetting()
        try:
            sessionData = requests.get('http://localhost:' + port + '/api/project/session')
            sessionData = sessionData.text
            sessionData = json.loads(sessionData)
        except Exception as e:
            sessionData = {'id': 0, 'username': '', 'level': 0, 'state': 0}
        return sessionData


    def getRandomID(length):
        id = ''.join([random.choice(string.ascii_uppercase + string.digits) for _ in range(length)])
        return id
    
    def checkUSBDevice(port):
        try:
            command = subprocess.check_output("ls -l /dev/serial/by-path/ | grep 0:1."+ str(port) + ":1", shell=True)
            command = command.decode("utf-8")
            command = command.replace("\n","")
            command = command.split(" ")
            data = []
            for x in range(len(command)):
                if "platform" in command[x]:
                    data.append(command[x])
                elif "ttyUSB" in command[x]:
                    usb = command[x]
                    usb = usb.replace("..","")
                    usb = usb.replace("/","")
                    data.append(usb)
        except Exception as e:
            data = ['N/A', 'N/A']
        return data
    
