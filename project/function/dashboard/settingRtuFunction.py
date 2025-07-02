import json 
import os 
import requests
import sys

sys.path.append("/home/connex/project/database")
from query_project_db import RtuParameterDB
sys.path.append("/home/connex/project/function")
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

                    if str(state) == '1':
                        result = {"state": state, "message": "RTU Parameter Added successfully!"}
                        return json.dumps(result)
                    
                    else:
                        result = {"state": state, "message": f"Failed to Add RTU Parameter {name}. There was an issue - failed add database"}
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
        