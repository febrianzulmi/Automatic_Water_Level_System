import json 
import os 
import requests
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import RtuParameterDB
sys.path.append('/home/connex/project/function')
from generalFunction import generalFunction
sys.path.append("/home/connex/library")
from SynapsisLibrary import times


class SettingRtu():
    class Device():
        pass
    
    
    class Parameter():
        def insert(name, custom_id, address, length, datatype, divider, type_sensor, type_control, unit, monitoring, log, state):
            try:
                is_name = RtuParameterDB.selectByName(name)
                is_address = RtuParameterDB.selectByAddress(address)
                is_custom_id = RtuParameterDB.selectByCustomId(custom_id)
                if is_name :
                    result = {'state': '2', 'message': 'Duplicate RTU Parameter Name Founded!'}
                    return json.dumps(result)
                elif is_address:
                    result = {'state': '2', 'message': 'Duplicate RTU Parameter Address Founded!'}
                    return json.dumps(result)
                elif is_custom_id:
                    result = {'state': '2', 'message': 'Duplicate RTU Parameter Custom ID Founded!'}
                    return json.dumps(result)
                else :
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
                result = {'state': '0', 'message': f'Failed to Add Sensor Group {name}. There is an issue - {str(e)}'}
                return json.dumps(result)
    
        def update(name, custom_id, address, length, datatype, divider, type_sensor, type_control, unit, monitoring, log, state):
            pass

        def delete(id):
            pass
        