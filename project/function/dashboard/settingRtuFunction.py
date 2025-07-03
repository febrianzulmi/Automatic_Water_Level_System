import json 
import os 
import requests
import sys

sys.path.append("/home/connex/project/database")
from query_project_db import (RtuParameterDB, RtuDeviceDB)
sys.path.append("/home/connex/project/function")
from generalFunction import generalFunction
sys.path.append("/home/connex/library")
from SynapsisLibrary import times


class SettingRtu():
    class Device():
        def insert(number, name, slave_id, state):
            try:
                check_number = RtuDeviceDB.selectByNumber(number)
                check_slaveid = RtuDeviceDB.selectBySlaveid(slave_id)
                
                if len(check_number) != 0:
                    result = {'state': '2', 'message': f'{number} All Ready Exist'}
                    return json.dumps(result)
                
                elif len(check_slaveid) != 0:
                    result = {'state': '2', 'message': f'{slave_id} All Ready Exist'}
                    return json.dumps(result)
                
                else:
                    if not state: state = "0"
                    
                    device_id = generalFunction.GenerateId.generateIdNearon("rtu", "rtu-device")
                    state = RtuDeviceDB.insert(device_id, number, name, slave_id, state)
                    
                    result = {'state': state, 'message': 'RTU Device Added successfully!'}
                    return json.dumps(result)
                
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Add RTU device {name}. There is an issue - {str(e)}'}
                return json.dumps(result)
                    
                    
        def update(device_id, number, name, slave_id, state):
            try:
                check_number = RtuDeviceDB.selectByNumber(number)
                check_slaveid = RtuDeviceDB.selectBySlaveid(slave_id)
                
                if len(check_number) != 0:
                    result = {'state': '2', 'message': f'{number} All Ready Exist'}
                    return json.dumps(result)
                
                elif len(check_slaveid) != 0:
                    result = {'state': '2', 'message': f'{slave_id} All Ready Exist'}
                    return json.dumps(result)
                
                else:
                    if not state: state = "0"
                    
                    status = RtuDeviceDB.update(device_id, number, name, slave_id, state)
                    
                    result = {'state': status, 'message': 'RTU Device Updated successfully!'}
                    return json.dumps(result)
                
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Updated RTU device {name}. There is an issue - {str(e)}'}
                return json.dumps(result)
        
        def delete():
            pass
    
    class Parameter():
        def insert(name, custom_id, address, length, datatype, divider, type_sensor, type_control, unit, monitoring, log, state):
            try:
                is_name = RtuParameterDB.selectByName(name)
                is_address = RtuParameterDB.selectByAddress(address)
                is_custom_id = RtuParameterDB.selectByCustomId(custom_id)
                
                if len(is_name) != 0:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Name Found!"}
                    return json.dumps(result)
                
                elif len(is_address) != 0:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Address Found!"}
                    return json.dumps(result)
                
                elif len(is_custom_id) != 0:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Custom ID Found!"}
                    return json.dumps(result)
                
                else:
                    if not state: state = "0"
                    
                    rtu_parameter_id = generalFunction.GenerateId.generateIdNearon("rtu", "rtu-parameter")
                    state = RtuParameterDB.insert(rtu_parameter_id, name, custom_id, address, length, datatype, divider, 
                                                  type_sensor, type_control, unit, monitoring, log, state)
                    
                    
                    # if str(state) == '1':
                    #     serviceId = SensorFunction.serviceSensor.createSensorFile(number)
                    #     SensorGroupDB.updateService(serviceId, sensor_group_id)
                    #     result = {'state': state, 'message': 'Sensor Group Added successfully!'}
                    #     return json.dumps(result)
                    # else:
                    #     result = {"state": state, "message": f"Failed Add Sensor Group {name}. There was an issue - failed add database"}
                    
                    result = {'state': state, 'message': 'Sensor Group Added successfully!'}
                    return json.dumps(result)
                
            except Exception as e:
                result = {"state": "0", "message": f"Failed to Add RTU Parameter {name}. There is an issue - {str(e)}"}
                return json.dumps(result)
    
        def update(id, name, custom_id, address, length, datatype, divider, type_sensor, type_control, 
                   unit, monitoring, log, state, last_name, last_custom_id, last_address):
            try:
                is_name = RtuParameterDB.selectByName(name)
                is_address = RtuParameterDB.selectByAddress(address)
                is_custom_id = RtuParameterDB.selectByCustomId(custom_id)
                
                if len(is_name) != 0 and last_name != name:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Name Found!"}
                    return json.dumps(result)
                
                elif len(is_address) != 0 and last_address != address:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Address Found!"}
                    return json.dumps(result)
                
                elif len(is_custom_id) != 0 and last_custom_id != custom_id:
                    result = {"state": "2", "message": "Duplicate RTU Parameter Custom ID Found!"}
                    return json.dumps(result)
                    
                else:
                    state = RtuParameterDB.updateById(id, name, custom_id, address, length, datatype, divider, type_sensor,
                                                      type_control, unit, monitoring, log, state)

                    if str(state) == '1':
                        result = {"state": state, "message": "RTU Parameter Updated successfully!"}
                        return json.dumps(result)
                    
                    else:
                        result = {"state": state, "message": f"Failed to Update RTU Parameter {name}. There was an issue - failed update database"}
                        return json.dumps(result)
                
            except Exception as e:
                result = {"state": "0", "message": f"Failed to Update RTU Parameter {name}. There is an issue - {str(e)}"}
                return json.dumps(result)

        def delete(id, name):
            try:
                state = RtuParameterDB.deleteById(id)
                result = {"state": state, "message": f"RTU Parameter {name} has been deleted!"}
            except Exception as e:
                result = {"state": "0", "message": f"RTU Parameter {name} failed to delete, there was an issue - {e}"}
            return json.dumps(result)
        