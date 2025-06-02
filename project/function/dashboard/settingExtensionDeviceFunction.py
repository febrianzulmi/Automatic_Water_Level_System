import json
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import (EnvironmentDeviceDB, EnvironmentMasterParameterDB, EnvironmentMasterSensorDB, SensorListDB, PowerDeviceDB,
                                PowerMasterParameterDB, PowerMasterSensorDB)
sys.path.append('/home/connex/project/function')
from generalFunction import generalFunction

class settingExtensionDevice():
    class environmentExtension():
        class device():
            def calculatePorts(data):
                port_mapping = {
                    0: 'disable',
                    1: 'sht20',
                    2: 'smoke',
                    3: 'door',
                    4: 'water_leak'
                }
                results = []
                for item in data:
                    port_counts = {port_type: 0 for port_type in port_mapping.values()}
                    for key, value in item.items():
                        if key.startswith('port') and isinstance(value, int):
                            port_type = port_mapping.get(value, 'Unknown')
                            port_counts[port_type] += 1
                    results.append({
                        'id': item['id'],
                        'name': item['name'],
                        'port_counts': port_counts
                    })
                return results

            def syncronizer(extension_id=None, ports=None, deviceState=None, type=None, last_port=[], lastNumber=None):
                port_config = {
                    "1": [("temp", "Temperature"), ("humid", "Humidity")],  # sht20
                    "2": [("smoke", "Smoke Detector")],                    # smoke
                    "3": [("door", "Door State")],                         # door
                    "4": [("water", "Water Leak")]                         # water leak
                }

                if type == "insert":
                    return SensorListDB.batchInsertSensors(extension_id, ports, port_config, deviceState, generalFunction)
                elif type == "update":
                    SensorListDB.batchDeleteSensors(lastNumber, last_port, port_config)
                    return SensorListDB.batchInsertSensors(extension_id, ports, port_config, deviceState, generalFunction)
                elif type == "delete":
                    return SensorListDB.batchDeleteSensors(extension_id, ports, port_config)

                return "1"


            def insert(number, name, method, ipAddress, modbus_id, deviceState, time, ports):
                try:
                    checkNumber = EnvironmentDeviceDB.checkNumber(number)
                    checkName = EnvironmentDeviceDB.checkName(name)
                    checkIp = EnvironmentDeviceDB.checkIp(ipAddress)
                    checkModbus = EnvironmentDeviceDB.checkModbusId(modbus_id)
                    state = "0"

                    if len(checkNumber) > 0:
                        result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device number already use'}
                        return json.dumps(result)
                    elif len(checkName) > 0:
                        result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device name already use'}
                        return json.dumps(result)

                    if method == "0": # Network
                        if len(checkIp) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device IP already use'}
                            return json.dumps(result)
                        else:
                            idDevice = generalFunction.GenerateId.generateIdNearon('environment', 'device')
                            state = EnvironmentDeviceDB.insertNetwork(number, idDevice, name, ipAddress, method, state, time, ports)
                            state = settingExtensionDevice.environmentExtension.device.syncronizer(extension_id=number, ports=ports, deviceState=deviceState, type="insert")
                            result = {'state':state, 'message':f'{name} Extension Device Network Method Added successfully!'}
                            return json.dumps(result)

                    elif method == "1": # Modbus
                        if len(checkModbus) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device Modbus already use'}
                            return json.dumps(result)
                        else:
                            idDevice = generalFunction.GenerateId.generateIdNearon('environment', 'device')
                            state = EnvironmentDeviceDB.insertModbus(number, idDevice, name, modbus_id, method, state, time, ports)
                            state = settingExtensionDevice.environmentExtension.device.syncronizer(extension_id=number, ports=ports, deviceState=deviceState, type="insert")
                            result = {'state':state, 'message':f'{name} Extension Device Modbus Method Added successfully!'}
                            return json.dumps(result)
                    
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(number, idDevice, name, method, ipAddress, modbus_id, deviceState, lastNumber, lastName, lastIp, lastModbus, ports, last_port):
                try:
                    state = "0"
                    if lastNumber != number:
                        checkNumber = EnvironmentDeviceDB.checkNumber(number)
                        if len(checkNumber) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device number already use'}
                            return json.dumps(result)
                    elif lastName != name:
                        checkName = EnvironmentDeviceDB.checkName(name)
                        if len(checkName) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device name already use'}
                            return json.dumps(result)

                    if method == "0":
                        if lastIp != ipAddress:
                            checkIp = EnvironmentDeviceDB.checkIp(ipAddress)
                            if len(checkIp) > 0:
                                result = {'state':'0', 'message':f'Failed to Update {name} Extension Device. Device IP already use'}
                                return json.dumps(result)
                            
                        state = settingExtensionDevice.environmentExtension.device.syncronizer(number, ports, deviceState, "update", last_port, lastNumber)
                        state = EnvironmentDeviceDB.updateNetworkById(number, idDevice, name, ipAddress, method, deviceState, ports)
                        result = {'state':state, 'message':f'Update Successful! Your Modbus {name} Extension Device have been successfully updated.'}
                        return json.dumps(result)

                    elif method == "1":
                        if lastModbus != modbus_id:
                            checkModbus = EnvironmentDeviceDB.checkModbusId(modbus_id)
                            if len(checkModbus) > 0:
                                result = {'state':'0', 'message':f'Failed to Update {name} Extension Device. Device Modbus already use'}
                                return json.dumps(result)
                        
                        state = settingExtensionDevice.environmentExtension.device.syncronizer(number, ports, deviceState, "update", last_port, lastNumber)
                        state = EnvironmentDeviceDB.updateModbusById(number, idDevice, name, modbus_id, method, deviceState, ports)
                        result = {'state':state, 'message':f'Update Successful! Your Network {name} Extension Device have been successfully updated.'}
                        return json.dumps(result)
        
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, number, last_port, name):
                try:
                    state = EnvironmentDeviceDB.deleteById(idDevice)
                    state = settingExtensionDevice.environmentExtension.device.syncronizer(extension_id=number, ports=last_port, type="delete")
                    result = {'state':state, 'message':f'Delete Successful! Your {name} Extension Device have been successfully deleted.'}
                    return json.dumps(result)

                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
        
        class masterSensorData():
            def insert(name, sensorId, time): 
                try:
                    idDevice = generalFunction.GenerateId.generateIdNearon('environment', 'master-sensor')
                    state = EnvironmentMasterSensorDB.insert(idDevice, name, sensorId, time)
                    result = {'state':state, 'message':f'{name} Master Sensor Added successfully!'}
                    return json.dumps(result)
                
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Master Sensor. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(idDevice, name, sensorId):
                try:
                    state = EnvironmentMasterSensorDB.updateById(idDevice, name, sensorId)
                    result = {'state':state, 'message':f'Update Successful! Your {name} Master Sensor have been successfully updated.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, name):
                try:
                    state = EnvironmentMasterSensorDB.deleteById(idDevice)
                    result = {'state':state, 'message':f'Delete Successful! Your {name} Master Sensor have been successfully deleted.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            

        class masterParameterData():
            def insert(name, parameterCode, time): 
                try:
                    idDevice = generalFunction.GenerateId.generateIdNearon('environment', 'master-parameter')
                    state = EnvironmentMasterParameterDB.insert(idDevice, name, parameterCode, time)
                    result = {'state':state, 'message':f'{name} Master Parameter Added successfully!'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Master Sensor. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(idDevice, name, parameterCode):
                try:
                    state = EnvironmentMasterParameterDB.updateById(idDevice, name, parameterCode)
                    result = {'state':state, 'message':f'Update Successful! Your {name} Master Parameter have been successfully updated.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, name):
                try:
                    state = EnvironmentMasterParameterDB.deleteById(idDevice)
                    result = {'state':state, 'message':f'Delete Successful! Your {name} Master Parameter have been successfully deleted.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
    
    class powerExtension():
        class device():

            def syncronizer(last_number=None, number=None, type=None, deviceState=None, total_port=None):
                if type == "insert":
                    return SensorListDB.insertSyncronizerPowerExt(number, deviceState, total_port, generalFunction)
                elif type == "update":
                    SensorListDB.deleteSyncronizerPowerExt(last_number, total_port)
                    return SensorListDB.insertSyncronizerPowerExt(number, deviceState, total_port, generalFunction)
                elif type == "delete":
                    return SensorListDB.deleteSyncronizerPowerExt(number, total_port)

            def insert(number, name, ipAddress, deviceConnection, deviceState, time):
                try:
                    checkNumber = PowerDeviceDB.checkNumber(number)
                    checkName = PowerDeviceDB.checkName(name)
                    checkIp = PowerDeviceDB.checkIp(ipAddress)
                    if len(checkNumber) > 0:
                        result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device number already use'}
                        return json.dumps(result)
                    elif len(checkName) > 0:
                        result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device name already use'}
                        return json.dumps(result)
                    elif len(checkIp) > 0:
                        result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device IP already use'}
                        return json.dumps(result)

                    idDevice = generalFunction.GenerateId.generateIdNearon('power', 'device')
                    state = PowerDeviceDB.insert(number, idDevice, name, ipAddress, deviceConnection, deviceState, time)
                    syncronizer = settingExtensionDevice.powerExtension.device.syncronizer(number=number, type="insert", deviceState=deviceState, total_port=6)
                
                    if state == "1" and syncronizer == "1":
                        status = "1"
                    else:
                        status = "0"
                    result = {'state':status, 'message':f'{name} Extension Device Added successfully!'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(number, idDevice, name, ipAddress, deviceState, lastNumber, lastName, lastIp):
                try:
                    if lastNumber != number:
                        checkNumber = PowerDeviceDB.checkNumber(number)
                        if len(checkNumber) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device number already use'}
                            return json.dumps(result)
                    elif lastName != name:
                        checkName = PowerDeviceDB.checkName(name)
                        if len(checkName) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device name already use'}
                            return json.dumps(result)
                    elif lastIp != ipAddress:
                        checkIp = PowerDeviceDB.checkIp(ipAddress)
                        if len(checkIp) > 0:
                            result = {'state':'0', 'message':f'Failed to Add {name} Extension Device. Device IP already use'}
                            return json.dumps(result)

                    state = PowerDeviceDB.updateById(number, idDevice, name, ipAddress, deviceState)
                    syncronizer = settingExtensionDevice.powerExtension.device.syncronizer(last_number=lastNumber, number=number, type="update", deviceState=deviceState, total_port=6)
                    if state == "1" and syncronizer == "1":
                        status = "1"
                    else:
                        status = "0"
                    result = {'state':status, 'message':f'Update Successful! Your {name} Extension Device have been successfully updated.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, name, number):
                try:
                    state = PowerDeviceDB.deleteById(idDevice)
                    syncronizer = settingExtensionDevice.powerExtension.device.syncronizer(number=number, type="delete", total_port=6)

                    if state == "1" and syncronizer == "1":
                        status = "1"
                    else:
                        status = "0"
                    
                    result = {'state':status, 'message':f'Delete Successful! Your {name} Extension Device have been successfully deleted.'}
                    return json.dumps(result)

                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
        class masterSensorData():
            def insert(name, sensorId, time): 
                try:
                    idDevice = generalFunction.GenerateId.generateIdNearon('power', 'master-sensor')
                    state = PowerMasterSensorDB.insert(idDevice, name, sensorId, time)
                    result = {'state':state, 'message':f'{name} Master Sensor Added successfully!'}
                    return json.dumps(result)
                
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Master Sensor. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(idDevice, name, sensorId):
                try:
                    state = PowerMasterSensorDB.updateById(idDevice, name, sensorId)
                    result = {'state':state, 'message':f'Update Successful! Your {name} Master Sensor have been successfully updated.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, name):
                try:
                    state = PowerMasterSensorDB.deleteById(idDevice)
                    result = {'state':state, 'message':f'Delete Successful! Your {name} Master Sensor have been successfully deleted.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            

        class masterParameterData():
            def insert(name, parameterCode, time): 
                try:
                    idDevice = generalFunction.GenerateId.generateIdNearon('power', 'master-parameter')
                    state = PowerMasterParameterDB.insert(idDevice, name, parameterCode, time)
                    result = {'state':state, 'message':f'{name} Master Parameter Added successfully!'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':f'Failed to Add {name} Master Sensor. There is an issue - ' + str(e)}
                    return json.dumps(result)
            
            def update(idDevice, name, parameterCode):
                try:
                    state = PowerMasterParameterDB.updateById(idDevice, name, parameterCode)
                    result = {'state':state, 'message':f'Update Successful! Your {name} Master Parameter have been successfully updated.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)
            
            def delete(idDevice, name):
                try:
                    state = PowerMasterParameterDB.deleteById(idDevice)
                    result = {'state':state, 'message':f'Delete Successful! Your {name} Master Parameter have been successfully deleted.'}
                    return json.dumps(result)
                except Exception as e:
                    result = {'state':'0', 'message':'Delete Failed! Sorry, there was an issue - ' + str(e)}
                    return json.dumps(result)