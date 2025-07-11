import json
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import ActuatorListDB, ActuatorGroupDB, ActuatorParameterListDB, ActuatorParameterGroupDB, ActuatorScheduleDB, SystemServiceDB
sys.path.append('/home/connex/project/function')
from generalFunction import generalFunction
from actuatorFunction import ActuatorFunction
from rtuFunction import RtuFunction


class SettingActuator():
    class Group():
        def insert(number, name, interval, unit):
            try:
                is_number_exist = ActuatorGroupDB.selectByNumber(number)
                if is_number_exist:
                    result = {"state": "2", "message": f"Actuator Group with number {number} is already exist!"}
                    return json.dumps(result)
                id = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-group")
                state = ActuatorGroupDB.insert(id, number, name, interval, unit, '0')

                if name.lower() == "rtu":
                    RtuFunction.createActuatorList()

                if str(state) == '1':
                    service_id = ActuatorFunction.ServiceActuator.createActuatorFile(number)
                    ActuatorGroupDB.updateService(service_id, id)
                    result = {"state": state, "message": f"Success Add Actuator Group {name}"}
                else:
                    result = {"state": state, "message": f"Failed Add Actuator Group {name}. There was an issue - failed add database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Add Actuator Group {name}. There was an issue - {e}"}
            return json.dumps(result)
        
        def update(number, name, interval, unit, id, last_number, last_name, service_id, state_group):
            try:
                is_number_exist = ActuatorGroupDB.selectByNumber(number)
                if is_number_exist and number != last_number:
                    result = {"state": "2", "message": f"Actuator Group with number {number} is already exist!"}
                    return json.dumps(result)
                state = ActuatorGroupDB.update(number, name, interval, unit, state_group, id)
                if last_name.lower() != "rtu" and name.lower() == "rtu":
                    sensordetail = ActuatorListDB.selectByActuatorGroupFull(id)
                    if sensordetail:
                        ActuatorListDB.deleteByGroupId(id)
                    RtuFunction.createActuatorList()
                
                elif last_name.lower() == "rtu" and name.lower() != "rtu":
                    ActuatorListDB.deleteByGroupId(id)

                if str(state) == '1':
                    if number != last_number:
                        service_id = ActuatorFunction.ServiceActuator.renameActuatorFile(last_number, number, service_id)
                        SystemServiceDB.deleteByName(F"actuator{last_number}")
                    result = {"state": state, "message": f"Success Update Actuator Group {name}"}
                else:
                    result = {"state": state, "message": f"Failed Update Actuator Group {name}. There was an issue - failed update database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Update Actuator Group {name}. There was an issue - {e}"}
            return json.dumps(result)
        
        def delete(id, name, number, service_id):
            try:
                state = ActuatorGroupDB.deleteOne(id)
                if str(state) == '1':
                    ActuatorFunction.ServiceActuator.deleteActuatorFile(number, service_id)
                    SystemServiceDB.deleteByName(F"actuator{number}")
                    result = {"state": state, "message": f"Success Delete Actuator Group {name}"}
                else:
                    result = {"state": state, "message": f"Failed Delete Actuator Group {name}. There was an issue - failed delete database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Delete Actuator Group {name}. There was an issue - {e}"}
            return json.dumps(result) 
        
    class List():
        def insert(actuator_group_id, name, actuator_custom_id, type_actuator):
            try:
                is_actuator_id_exist = ActuatorListDB.selectByActId(actuator_custom_id)
                if is_actuator_id_exist:
                    result = {"state": "2", "message": f"Actuator List with Custom ID {actuator_custom_id} is already exist!"}
                    return json.dumps(result)
                id = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-list")
                state = ActuatorListDB.insert(id, actuator_group_id, name, actuator_custom_id, type_actuator, '0')
                if str(state) == '1':
                    result = {"state": state, "message": f"Success Add Actuator List {name}"}
                else:
                    result = {"state": state, "message": f"Failed Add Actuator List {name}. There was an issue - failed add database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Add Actuator List {name}. There was an issue - {e}"}
            return json.dumps(result)
        
        def update(actuator_group_id, name, actuator_custom_id, type_actuator, id, last_actuator_custom_id, state_actuator):
            try:
                is_number_exist = ActuatorListDB.selectByActId(actuator_custom_id)
                if is_number_exist and actuator_custom_id != last_actuator_custom_id:
                    result = {"state": "2", "message": f"Actuator List with Custom ID {actuator_custom_id} is already exist!"}
                    return json.dumps(result)
                state = ActuatorListDB.update(actuator_group_id, name, actuator_custom_id, type_actuator, state_actuator, id)
                if str(state) == '1':
                    result = {"state": state, "message": f"Success Update Actuator List {name}"}
                else:
                    result = {"state": state, "message": f"Failed Update Actuator List {name}. There was an issue - failed update database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Update Actuator List {name}. There was an issue - {e}"}
            return json.dumps(result)
        
        def delete(id, name):
            try:
                state = ActuatorListDB.deleteOne(id)
                if str(state) == '1':
                    result = {"state": state, "message": f"Success Delete Actuator List {name}"}
                else:
                    result = {"state": state, "message": f"Failed Delete Actuator List {name}. There was an issue - failed delete database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Delete Actuator List {name}. There was an issue - {e}"}
            return json.dumps(result) 
    
    class ParameterGroup():
        def insert(actuator_group_id, name, param, value):
            check_param = ActuatorParameterGroupDB.checkExistingParam(actuator_group_id, param)
            if check_param == 0:
                try:
                    id = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-group")
                    state = ActuatorParameterGroupDB.insert(id, actuator_group_id, name, param, value)
                    result = {"state": state, "message": f"Success Add Actuator Parameter Group {name}"}
                except Exception as e:
                    result = {"state": "0", "message": f"Failed Add Actuator Parameter Group {name}. There was an issue - {e}"}
            else:
                result = {"state": "2", "message": f"Failed Add Actuator Parameter Group {name}. There was an issue - duplicate parameter detected"}
            return json.dumps(result)
        
        def update(actuator_group_id, name, parameter, value, last_actuator_group_id, last_parameter, id):
            if parameter != last_parameter or actuator_group_id != last_actuator_group_id: 
                check_param = ActuatorParameterGroupDB.checkExistingParam(actuator_group_id, parameter)
            else: check_param = 0
            if check_param == 0:
                try:
                    state = ActuatorParameterGroupDB.update(actuator_group_id, name, parameter, value, id)
                    result = {"state": state, "message": f"Success Update Actuator Parameter Group {name}"}
                except Exception as e:
                    result = {"state": "0", "message": f"Failed Update Actuator Parameter Group {name}. There was an issue - {e}"}
            else:
                result = {"state": "2", "message": f"Failed Update Actuator Parameter Group {name}. There was an issue - duplicate parameter detected"}
            return json.dumps(result)
        
        def delete(id, name):
            try:
                state = ActuatorParameterGroupDB.deleteOne(id)
                result = {"state": state, "message": f"Success Delete Actuator Parameter Group {name}"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Delete Parameter Group {name} - {e}"}
            return json.dumps(result) 

    
    class ParameterList():
        def insert(actuator_list_id, name, param, value):
            check_param = ActuatorParameterListDB.checkExistingParam(actuator_list_id, param)
            if check_param == 0:
                try:
                    id = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list")
                    state = ActuatorParameterListDB.insert(id, actuator_list_id, name, param, value)
                    result = {"state": state, "message": f"Success Add Actuator Parameter List {name}"}
                except Exception as e:
                    result = {"state": "0", "message": f"Failed Add Actuator Parameter List {name}. There was an issue - {e}"}
            else:
                result = {"state": "2", "message": f"Failed Add Actuator Parameter List {name}. There was an issue - duplicate parameter detected"}
            return json.dumps(result)
        
        def update(actuator_list_id, name, parameter, value, last_actuator_list_id, last_parameter, id):
            if parameter != last_parameter or actuator_list_id != last_actuator_list_id: 
                check_param = ActuatorParameterListDB.checkExistingParam(actuator_list_id, parameter)
            else: check_param = 0
            if check_param == 0:
                try:
                    state = ActuatorParameterListDB.update(actuator_list_id, name, parameter, value, id)
                    result = {"state": state, "message": f"Success Update Actuator Parameter List {name}"}
                except Exception as e:
                    result = {"state": "0", "message": f"Failed Update Actuator Parameter List {name}. There was an issue - {e}"}
            else:
                result = {"state": "2", "message": f"Failed Update Actuator Parameter List {name}. There was an issue - duplicate parameter detected"}
            return json.dumps(result)
        
        def delete(id, name):
            try:
                state = ActuatorParameterListDB.deleteOne(id)
                result = {"state": state, "message": f"Success Delete Actuator Parameter List {name}"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Delete Parameter List {name} - {e}"}
            return json.dumps(result) 
