import json 
import sys

sys.path.append("/home/connex/project/database")
from query_project_db import (RtuParameterDB, RtuDeviceDB, SensorListDB, SensorGroupDB, SensorParameterListDB, 
                              ActuatorListDB, ActuatorGroupDB, ActuatorParameterListDB)
sys.path.append("/home/connex/project/function")
from generalFunction import generalFunction
from rtuFunction import RtuFunction


class SettingRtu():
    class Device():
        def insert(number, name, slave_id, state):
            try:
                check_number = RtuDeviceDB.selectByNumber(number)
                check_slaveid = RtuDeviceDB.selectBySlaveid(slave_id)
                
                if len(check_number) != 0:
                    result = {'state': '2', 'message': f'RTU Device Number {number} All Ready Exist'}
                    return json.dumps(result)
                
                elif len(check_slaveid) != 0:
                    result = {'state': '2', 'message': f'RTU Device Slave Id {slave_id} All Ready Exist'}
                    return json.dumps(result)
                
                else:
                    if not state: state = "0"
                    
                    device_id = generalFunction.GenerateId.generateIdNearon("rtu", "rtu-device")
                    status = RtuDeviceDB.insert(device_id, number, name, slave_id, state)

                    if str(status) == '1':
                        ####################################### Sync Sensor and Actuator #######################################
                        rtu_parameter = RtuParameterDB.select()
                        sensor_group_id = SensorGroupDB.selectByName("RTU")[0]["id"]
                        actuator_group_id = ActuatorGroupDB.selectByName("RTU")[0]["id"]
                        oid_number = len(SensorListDB.selectByGroupFull(sensor_group_id)) + 1
                        
                        for item_parameter in range(len(rtu_parameter)):
                            name_data = f"{rtu_parameter[item_parameter]['name']} - {name}"
                            custom_id_data = f"{rtu_parameter[item_parameter]['custom_id']}Rtu{number}"
                            state_data = '1' if (rtu_parameter[item_parameter]['state'] == '1' and state == '1') else '0'

                            if int(rtu_parameter[item_parameter]['type']) == 0 or int(rtu_parameter[item_parameter]['type']) == 2:
                                id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                                datatype = rtu_parameter[item_parameter]['datatype']
                                monitoring = rtu_parameter[item_parameter]['monitoring']
                                log = rtu_parameter[item_parameter]['log']
                                unit = rtu_parameter[item_parameter]['unit']
                                address = rtu_parameter[item_parameter]['address']
                                length = rtu_parameter[item_parameter]['length']
                                divider = rtu_parameter[item_parameter]['divider']
                                
                                SensorListDB.insert(id_sensor, custom_id_data, oid_number, sensor_group_id, name_data, "0", "0", 
                                                    datatype, monitoring, log, state_data)
                                SensorListDB.updateUnitById(id_sensor, unit)
                                oid_number += 1

                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Address", "address", address)
                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Length", "length", length)
                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Divider", "divider", divider)


                            if int(rtu_parameter[item_parameter]['type']) == 1 or int(rtu_parameter[item_parameter]['type']) == 2:
                                id_actuator = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-list")
                                type_actuator = int(rtu_parameter[item_parameter]['type_control']) - 1
                                address = rtu_parameter[item_parameter]['address']
                                length = rtu_parameter[item_parameter]['length']
                                divider = rtu_parameter[item_parameter]['divider']

                                ActuatorListDB.insert(id_actuator, actuator_group_id, name_data, custom_id_data, type_actuator, state_data)

                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Address", "address", address)
                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Length", "length", length)
                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Divider", "divider", divider)

                        RtuFunction.rearrangeSensorandActuatorList()
                        ####################################### Sync Sensor and Actuator #######################################
                        
                        result = {"state": status, "message": "RTU Device Added successfully!"}
                        return json.dumps(result)

                    else:
                        result = {"state": status, "message": f"Failed to Add RTU Device {name}. There was an issue - failed add database"}
                        return json.dumps(result)
                
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Add RTU Device {name}. There was an issue - {str(e)}'}
                return json.dumps(result)
                    
                    
        def update(device_id, number, name, slave_id, state, last_number, last_slaveid):
            try:
                check_number = RtuDeviceDB.selectByNumber(number)
                check_slaveid = RtuDeviceDB.selectBySlaveid(slave_id)
                
                if len(check_number) != 0 and last_number != number:
                    result = {'state': '2', 'message': f'RTU Device Number {number} Already Exist'}
                    return json.dumps(result)
                
                elif len(check_slaveid) != 0 and last_slaveid != slave_id:
                    result = {'state': '2', 'message': f'RTU Device Slave Id {slave_id} Already Exist'}
                    return json.dumps(result)
                
                else:
                    if not state: state = "0"

                    status = RtuDeviceDB.update(device_id, number, name, slave_id, state)

                    if str(status) == '1':
                        ####################################### Sync Sensor and Actuator #######################################
                        rtu_parameter = RtuParameterDB.select()
                        sensor_group_id = SensorGroupDB.selectByName("RTU")[0]["id"]
                        actuator_group_id = ActuatorGroupDB.selectByName("RTU")[0]["id"]
                        sensor_list = SensorListDB.selectByGroupFull(sensor_group_id)
                        actuator_list = ActuatorListDB.selectByActuatorGroupFull(actuator_group_id)
                        oid_number = len(sensor_list) + 1

                        for item_parameter in range(len(rtu_parameter)):
                            name_data = f"{rtu_parameter[item_parameter]['name']} - {name}"
                            custom_id_data = f"{rtu_parameter[item_parameter]['custom_id']}Rtu{number}"
                            last_custom_id_data = f"{rtu_parameter[item_parameter]['custom_id']}Rtu{last_number}"
                            state_data = '1' if (rtu_parameter[item_parameter]['state'] == '1' and state == '1') else '0'
                            
                            if int(rtu_parameter[item_parameter]['type']) == 0 or int(rtu_parameter[item_parameter]['type']) == 2:
                                datatype = rtu_parameter[item_parameter]['datatype']
                                monitoring = rtu_parameter[item_parameter]['monitoring']
                                log = rtu_parameter[item_parameter]['log']
                                unit = rtu_parameter[item_parameter]['unit']
                                address = rtu_parameter[item_parameter]['address']
                                length = rtu_parameter[item_parameter]['length']
                                divider = rtu_parameter[item_parameter]['divider']

                                for item_sensor in range(len(sensor_list)):
                                    if custom_id_data == sensor_list[item_sensor]["sensor_id"] or last_custom_id_data == sensor_list[item_sensor]["sensor_id"]:                                  
                                        SensorListDB.update(custom_id_data, sensor_list[item_sensor]["oid"], sensor_group_id, 
                                                            name_data, sensor_list[item_sensor]["calibrate"], sensor_list[item_sensor]["formula"],
                                                            datatype, monitoring, log, sensor_list[item_sensor]["alarm"], sensor_list[item_sensor]["min"], 
                                                            sensor_list[item_sensor]["max"], sensor_list[item_sensor]["alarm_type"], state_data, sensor_list[item_sensor]["id"])
                                        SensorListDB.updateUnitById(sensor_list[item_sensor]["id"], unit)

                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Address", "address", address,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "address")[0]["id"])
                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Length", "length", length,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "length")[0]["id"])
                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Divider", "divider", divider,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "divider")[0]["id"])
                                        
                            if int(rtu_parameter[item_parameter]['type']) == 1 or int(rtu_parameter[item_parameter]['type']) == 2:
                                type_actuator = int(rtu_parameter[item_parameter]['type_control']) - 1
                                address = rtu_parameter[item_parameter]['address']
                                length = rtu_parameter[item_parameter]['length']
                                divider = rtu_parameter[item_parameter]['divider']

                                for item_actuator in range(len(actuator_list)):
                                    if custom_id_data == actuator_list[item_actuator]["actuator_custom_id"] or last_custom_id_data == actuator_list[item_actuator]["actuator_custom_id"]:
                                        ActuatorListDB.update(actuator_group_id, name_data, custom_id_data, type_actuator, state_data, actuator_list[item_actuator]["id"])

                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Address", "address", address,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "address")[0]["id"])
                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Length", "length", length,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "length")[0]["id"])
                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Divider", "divider", divider,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "divider")[0]["id"])
                            
                        RtuFunction.rearrangeSensorandActuatorList()
                        ####################################### Sync Sensor and Actuator #######################################
                        result = {"state": status, "message": "RTU Device Updated successfully!"}
                        return json.dumps(result)
                    
                    else:
                        result = {"state": status, "message": f"Failed to Update RTU Device {name}. There was an issue - failed update database"}
                        return json.dumps(result)
                
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Update RTU device {name}. There was an issue - {str(e)}'}
                return json.dumps(result)
        
        def delete(id, name):
            try:
                status = RtuDeviceDB.deleteById(id)
                if str(status) == '1':
                        ####################################### Sync Sensor and Actuator #######################################
                        rtu_parameter = RtuParameterDB.select()
                        for item_parameter in range(len(rtu_parameter)):
                            fullname = f"{rtu_parameter[item_parameter]['name']} - {name}"
                            SensorListDB.deleteByName(fullname)
                            ActuatorListDB.deleteByName(fullname)
                        
                        RtuFunction.rearrangeSensorandActuatorList()
                        ####################################### Sync Sensor and Actuator #######################################

                        result = {"state": status, "message": f"RTU Device {name} has been deleted!"}
                        return json.dumps(result)

                else:
                    result = {"state": status, "message": f"Failed to Delete RTU Device {name}. There was an issue - failed delete database"}
                    return json.dumps(result)
            
            except Exception as e:
                result = {"state": "0", "message": f"RTU Device {name} failed to delete, there was an issue - {e}"}
                return json.dumps(result)
        
    
    class Parameter():
        def insert(name, custom_id, address, length, datatype, divider, type_parameter, type_control, unit, monitoring, log, state):
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

                    if type_parameter == 0 :
                        type_control = 0
                
                    elif type_parameter == 1:
                        monitoring = 0
                        log = 0
                        unit = '#'
                        datatype = 0
                    
                    rtu_parameter_id = generalFunction.GenerateId.generateIdNearon("rtu", "rtu-parameter")
                    status = RtuParameterDB.insert(rtu_parameter_id, name, custom_id, address, length, datatype, divider, 
                                                    type_parameter, type_control, unit, monitoring, log, state)
                    
                    if str(status) == '1':
                        ####################################### Sync Sensor and Actuator #######################################
                        rtu_device = RtuDeviceDB.select()
                        sensor_group_id = SensorGroupDB.selectByName("RTU")[0]["id"]
                        actuator_group_id = ActuatorGroupDB.selectByName("RTU")[0]["id"]
                        oid_number = len(SensorListDB.selectByGroupFull(sensor_group_id)) + 1
                        
                        for item_device in range(len(rtu_device)):
                            name_data = f"{name} - {rtu_device[item_device]['name']}"
                            custom_id_data = f"{custom_id}Rtu{rtu_device[item_device]['number']}"
                            state_data = '1' if (rtu_device[item_device]['state'] == '1' and state == '1') else '0'

                            if int(type_parameter) == 0 or int(type_parameter) == 2:
                                id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                                
                                SensorListDB.insert(id_sensor, custom_id_data, oid_number, sensor_group_id, name_data, "0", "0", 
                                                    datatype, monitoring, log, state_data)
                                SensorListDB.updateUnitById(id_sensor, unit)
                                oid_number += 1

                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Address", "address", address)
                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Length", "length", length)
                                SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                            id_sensor, "Divider", "divider", divider)
                            

                            if int(type_parameter) == 1 or int(type_parameter) == 2:
                                id_actuator = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-list")
                                type_actuator = int(type_control) - 1

                                ActuatorListDB.insert(id_actuator, actuator_group_id, name_data, custom_id_data, type_actuator, state_data)

                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Address", "address", address)
                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Length", "length", length)
                                ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                id_actuator, "Divider", "divider", divider)
                        
                        RtuFunction.rearrangeSensorandActuatorList()
                        ####################################### Sync Sensor and Actuator #######################################

                        result = {"state": status, "message": "RTU Parameter Added successfully!"}
                        return json.dumps(result)
                    
                    else:
                        result = {"state": status, "message": f"Failed to Add RTU Parameter {name}. There was an issue - failed add database"}
                        return json.dumps(result)
                
            except Exception as e:
                result = {"state": "0", "message": f"Failed to Add RTU Parameter {name}. There was an issue - {str(e)}"}
                return json.dumps(result)
    
        def update(id, name, custom_id, address, length, datatype, divider, type_parameter, type_control, 
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
                    if str(type_parameter) == '0' :
                        type_control = 0
                
                    elif str(type_parameter) == '1':
                        monitoring = 0
                        log = 0
                        unit = '#'
                        datatype = 0

                    status = RtuParameterDB.updateById(id, name, custom_id, address, length, datatype, divider,
                                                        type_parameter, type_control, unit, monitoring, log, state)

                    if str(status) == '1':
                        ####################################### Sync Sensor and Actuator #######################################
                        rtu_device = RtuDeviceDB.select()
                        sensor_group_id = SensorGroupDB.selectByName("RTU")[0]["id"]
                        actuator_group_id = ActuatorGroupDB.selectByName("RTU")[0]["id"]
                        sensor_list = SensorListDB.selectByGroupFull(sensor_group_id)
                        actuator_list = ActuatorListDB.selectByActuatorGroupFull(actuator_group_id)
                        oid_number = len(sensor_list) + 1

                        for item_device in range(len(rtu_device)):
                            name_data = f"{name} - {rtu_device[item_device]['name']}"
                            custom_id_data = f"{custom_id}Rtu{rtu_device[item_device]['number']}"
                            last_custom_id_data = f"{last_custom_id}Rtu{rtu_device[item_device]['number']}"
                            state_data = '1' if (rtu_device[item_device]['state'] == '1' and state == '1') else '0'

                            if int(type_parameter) == 0 or int(type_parameter) == 2:
                                if int(type_parameter) == 0:
                                   ActuatorListDB.deleteByName(name_data)

                                sensor_exist = False
                                
                                for item_sensor in range(len(sensor_list)):
                                    if custom_id_data == sensor_list[item_sensor]["sensor_id"] or last_custom_id_data == sensor_list[item_sensor]["sensor_id"]:
                                        SensorListDB.update(custom_id_data, sensor_list[item_sensor]["oid"], sensor_group_id, 
                                                            name_data, sensor_list[item_sensor]["calibrate"], sensor_list[item_sensor]["formula"],
                                                            datatype, monitoring, log, sensor_list[item_sensor]["alarm"], sensor_list[item_sensor]["min"], 
                                                            sensor_list[item_sensor]["max"], sensor_list[item_sensor]["alarm_type"], state_data, sensor_list[item_sensor]["id"])
                                        SensorListDB.updateUnitById(sensor_list[item_sensor]["id"], unit)

                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Address", "address", address,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "address")[0]["id"])
                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Length", "length", length,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "length")[0]["id"])
                                        SensorParameterListDB.update(sensor_list[item_sensor]["id"], "Divider", "divider", divider,
                                                                     SensorParameterListDB.selectBySensorParameter(sensor_list[item_sensor]["id"], "divider")[0]["id"])
                                        
                                        sensor_exist = True
                                    
                                if not sensor_exist:
                                    id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                            
                                    SensorListDB.insert(id_sensor, custom_id_data, oid_number, sensor_group_id, name_data, "0", "0", 
                                                        datatype, monitoring, log, state_data)
                                    SensorListDB.updateUnitById(id_sensor, unit)

                                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                                id_sensor, "Address", "address", address)
                                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                                id_sensor, "Length", "length", length)
                                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                                id_sensor, "Divider", "divider", divider)

                                        
                            if int(type_parameter) == 1 or int(type_parameter) == 2:
                                type_actuator = int(type_control) - 1

                                if int(type_parameter) == 1:
                                    SensorListDB.deleteByName(name_data)

                                actuator_exist = False
                                
                                for item_actuator in range(len(actuator_list)):
                                    if custom_id_data == actuator_list[item_actuator]["actuator_custom_id"] or last_custom_id_data == actuator_list[item_actuator]["actuator_custom_id"]:
                                        ActuatorListDB.update(actuator_group_id, name_data, custom_id_data, type_actuator, state_data, actuator_list[item_actuator]["id"])

                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Address", "address", address,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "address")[0]["id"])
                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Length", "length", length,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "length")[0]["id"])
                                        ActuatorParameterListDB.update(actuator_list[item_actuator]["id"], "Divider", "divider", divider,
                                                                       ActuatorParameterListDB.selectByActuatorParameter(actuator_list[item_actuator]["id"], "divider")[0]["id"])
                                        
                                        actuator_exist = True

                                if not actuator_exist:
                                    id_actuator = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-list")

                                    ActuatorListDB.insert(id_actuator, actuator_group_id, name_data, custom_id_data, type_actuator, state_data)

                                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                    id_actuator, "Address", "address", address)
                                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                    id_actuator, "Length", "length", length)
                                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                                    id_actuator, "Divider", "divider", divider)

                            
                        RtuFunction.rearrangeSensorandActuatorList()
                        ####################################### Sync Sensor and Actuator #######################################

                        result = {"state": status, "message": "RTU Parameter Updated successfully!"}
                        return json.dumps(result)
                    
                    else:
                        result = {"state": status, "message": f"Failed to Update RTU Parameter {name}. There was an issue - failed update database"}
                        return json.dumps(result)
                
            except Exception as e:
                result = {"state": "0", "message": f"Failed to Update RTU Parameter {name}. There was an issue - {str(e)}"}
                return json.dumps(result)

        def delete(id, name):
            try:
                status = RtuParameterDB.deleteById(id)
                
                if str(status) == '1':
                    ####################################### Sync Sensor and Actuator #######################################
                    rtu_device = RtuDeviceDB.select()
                    for item_device in range(len(rtu_device)):
                        fullname = f"{name} - {rtu_device[item_device]['name']}"
                        SensorListDB.deleteByName(fullname)
                        ActuatorListDB.deleteByName(fullname)
                    
                    RtuFunction.rearrangeSensorandActuatorList()
                    ####################################### Sync Sensor and Actuator #######################################

                    result = {"state": status, "message": f"RTU Parameter {name} has been deleted!"}
                    return json.dumps(result)

                else:
                    result = {"state": status, "message": f"Failed to Delete RTU Parameter {name}. There was an issue - failed delete database"}
                    return json.dumps(result)

            except Exception as e:
                result = {"state": "0", "message": f"RTU Parameter {name} failed to delete, there was an issue - {e}"}
                return json.dumps(result)
        