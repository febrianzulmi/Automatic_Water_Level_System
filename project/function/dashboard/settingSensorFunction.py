import json 
import os 
import requests
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import SensorGroupDB, SensorListDB, SensorParameterGroupDB, SensorParameterListDB, SensorPortConfigDB, SystemServiceDB
sys.path.append('/home/connex/project/function')
from sensorFunction import SensorFunction
from serviceProjectFunction import ServiceProjectFunction
from generalFunction import generalFunction
from rtuFunction import RtuFunction
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction
sys.path.append("/home/connex/library")
from SynapsisLibrary import times


class settingSensor():
    class group():
        def insert(number, oid_group, name, intervals, unit, frekuensi, enterAlarm, exitAlarm, errorAlarm):
            try:
                isNull = SensorGroupDB.selectByName(name)
                isNumber = SensorGroupDB.selectIsNumber(number)
                isOid = SensorGroupDB.selectIsOid(oid_group)
                if isNull :
                    result = {'state': '2', 'message': 'Duplicate Sensor Group Name Founded!'}
                    return json.dumps(result)
                elif isNumber:
                    result = {'state': '2', 'message': 'Duplicate Sensor Group Number Founded!'}
                    return json.dumps(result)
                elif isOid:
                    result = {'state': '2', 'message': 'Duplicate Sensor Group Oid Founded!'}
                    return json.dumps(result)
                else :
                    sensor_group_id = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-group")
                    state = SensorGroupDB.insert(sensor_group_id, number, oid_group, name, intervals, unit, frekuensi, 0, enterAlarm, exitAlarm, errorAlarm)
                    if name.lower() == "rtu":
                        RtuFunction.createSensorList()
                    if str(state) == '1':
                        serviceId = SensorFunction.serviceSensor.createSensorFile(number)
                        SensorGroupDB.updateService(serviceId, sensor_group_id)
                        result = {'state': state, 'message': 'Sensor Group Added successfully!'}
                        return json.dumps(result)
                    else:
                        result = {"state": state, "message": f"Failed Add Sensor Group {name}. There was an issue - failed add database"}
                
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Add Sensor Group {name}. There is an issue - {str(e)}'}
                return json.dumps(result)
    
        def update(number, oid, name, interval, unit, frekuensi, service_id, id, enterAlarm, exitAlarm, errorAlarm, stateSensor, last_number, last_name, last_oid_group):
            try:

                if last_name != name:
                    isName = SensorGroupDB.selectByName(name)
                    if isName :
                        result = {'state': '2', 'message': 'Duplicate Sensor Group Name Founded!'}
                        return json.dumps(result)

                elif last_number != number:
                    isNumber = SensorGroupDB.selectIsNumber(number)
                    if isNumber:
                        result = {'state': '2', 'message': 'Duplicate Sensor Group Number Founded!'}
                        return json.dumps(result)

                if last_oid_group != oid:
                    isOid = SensorGroupDB.selectIsOid(oid)
                    if isOid:
                        result = {'state': '2', 'message': 'Duplicate Sensor Group Oid Founded!'}
                        return json.dumps(result)
                
                state = SensorGroupDB.update(number, oid, name, interval, unit, frekuensi, service_id, id, enterAlarm, exitAlarm, errorAlarm, stateSensor)
                
                if last_name.lower() != "rtu" and name.lower() == "rtu":
                    sensordetail = SensorListDB.selectByGroup(id)
                    if sensordetail:
                        SensorListDB.deleteByGroupId(id)
                    RtuFunction.createSensorList()

                elif last_name.lower() == "rtu" and name.lower() != "rtu":
                    SensorListDB.deleteByGroupId(id)

                print("masuk iff 3")

                if str(state) == "1":
                    if last_number != number:
                        SensorFunction.serviceSensor.renameSensorFile(last_number, number, service_id)
                        SystemServiceDB.deleteByName(F"sensor{last_number}")
                        ServiceProjectFunction.actionService("stop", "disable", F"sensor{last_number}")
                    if str(stateSensor) == "1":
                        service = ServiceProjectFunction.actionService("start", "enable", F"sensor{number}")
                    elif str(stateSensor) == "0":
                        service = ServiceProjectFunction.actionService("stop", "disable", F"sensor{number}")
                    result = {"state": state, "message": f"Success Update Sensor Group {name}"}
                else:
                    result = {"state": state, "message": f"Failed Update Sensor Group {name}. There was an issue - failed update database"}
            except Exception as e:
                result = {"state": "0", "message": f"Failed Update Sensor Group {name}. There was an issue - {e}"}
            return json.dumps(result)
        
        def delete(id, number, nameSensorGroup, serviceId, port):
            try:
                state_group = SensorGroupDB.deleteOne(id)
                if str(state_group) == "1":
                    SensorFunction.serviceSensor.deleteSensorFile(number, serviceId)
                    SystemServiceDB.deleteByName(F"sensor{number}")
                    result = {'state': '1', 'message': 'Sensor Group Deleted successfully!'}
                else:
                    result = {"state": "0", "message": f"Failed Add Sensor Group {nameSensorGroup}. There was an issue - failed delete database"}
                    
            except Exception as e:
                result = {'state': '0', 'message': f'Failed to Add Sensor Group {nameSensorGroup}. There is an issue - {str(e)}'}
            return json.dumps(result)
        
    class list():
        def insert(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log):
            try:
                id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                state = SensorListDB.insert(id_sensor, sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, "1")
                OidSensorFunction.createSensorOid()
                result = {'state':state, 'message':f'Sensor List Added successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed to Add Sensor List. There is an issue - ' + str(e)}
            return json.dumps(result)
        
        def update(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id):      
            try:
                state = SensorListDB.update(sensor_id, oid, group_id, name, calibrate, formula, oid_tipe, monitor, log, alarm, min, max, alarm_type, stateSensorList, id)
                OidSensorFunction.createSensorOid()
                result = {'state':state, 'message':'Update Successful! Your Sensor List have been successfully updated.'}
            except Exception as e:
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
            return json.dumps(result)
        
        def delete(id, name):
            try:
                state = SensorListDB.deleteOne(id)
                OidSensorFunction.createSensorOid()
                result = {'state':state, 'message':f'Sensor List {name} deleted successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':f'Failed Delete Sensor List {name} - {e}'}
            return json.dumps(result)
        
    class parameterGroup():
        def insert(group_id, name, parameter, value):
            try:
                id_param_group = generalFunction.GenerateId.generateIdNearon("sensor", "parameter-group")
                state = SensorParameterGroupDB.insert(id_param_group, group_id, name, parameter, value)
                result = {'state':state, 'message':f'Sensor Parameter Group {name} Added successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':f'Failed to Add Sensor Parameter Group {name}. There is an issue - ' + str(e)}
            return json.dumps(result)
        
        def update(group_id, name, parameter, value, id):
            try:
                state = SensorParameterGroupDB.update(group_id, name, parameter, value, id)
                result = {'state':state, 'message':f'Update Successful! Your Sensor Parameter Group {name} have been successfully updated.'}
            except Exception as e:
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
            return json.dumps(result)
        
        def delete(id, name):
            try:
                state = SensorParameterGroupDB.deleteOne(id)
                result = {'state':state, 'message':f'Parameter Group {name} Deleted Successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':f'Failed Delete Parameter Group {name} - {e}'}
            return json.dumps(result)
    
    class parameterList():
        def insert(sensorID, name, parameter, value):
            try:
                id_param_list = generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list")
                state = SensorParameterListDB.insert(id_param_list, sensorID, name, parameter, value)
                result = {'state': state, 'message': 'Sensor Parameter List Added successfully!'}
            except Exception as e :
                result = {'state': '0', 'message': f'Failed Delete Sensor List - {e}'}
            return json.dumps(result)
        
        def update(sensorID, name, parameter, value, id):
            try:
                state = SensorParameterListDB.update(sensorID, name, parameter, value, id)
                result = {'state': state, 'message': 'Update Successful! Your Sensor Parameter List have been successfully updated.'}
            except Exception as e :
                result = {'state': '0', 'message': f'Update Failed! Sorry, there was an issue - {e}'}
            return json.dumps(result)
        
        def delete(id):
            try:
                state = SensorParameterListDB.deleteOne(id)
                result = {'state': state, 'message': 'Sensor Parameter List has been deleted!'}
            except Exception as e:
                result = {'state': '0', 'message': f'Sensor Parameter List failed to delete, there was an issue - {e}'}
            return json.dumps(result)
    

    class PortConfig():
        def update(ports):
            try:
                timestamp = times.getDatetime()
                for i in range(1, 7):
                    mappings = {
                        "0": {"disable": F""},
                        "1": {"temp": F"temp_p{i}", "humid": F"humid_p{i}"},
                        "2": {"smoke": F"smoke_p{i}"},
                        "3": {"door": F"door_p{i}"}
                    }
                    port = F"port_{i}"
                    check_modbus_id = SensorPortConfigDB.checkModbusId(ports[port]["modbusId"], str(i))
                    check_digital_pin = SensorPortConfigDB.checkDigitalPin(ports[port]["digitalPin"], str(i))

                    if len(check_modbus_id) > 0:
                        result = {'state': '0', 'message': f'Failed to Update Port {i}. Modbus ID already Use'}
                        return json.dumps(result)
                    if len(check_digital_pin) > 0:
                        result = {'state': '0', 'message': f'Failed to Update Port {i}. Digital Pin already Use'}
                        return json.dumps(result)
                    
                    state_port = SensorPortConfigDB.updateById(ports[port]["typePort"], ports[port]["modbusId"], ports[port]["digitalPin"], str(i))
                    parsed_lastP = mappings.get(ports[port]["lastPort"])
                    for key in parsed_lastP:
                        if key == "disable":
                            break
                        state_sensor_list = SensorListDB.updateState("0", timestamp, parsed_lastP[key])
                    
                    parsed_newP = mappings.get(ports[port]["typePort"])
                    for key in parsed_newP:
                        if key == "disable":
                            break
                        state_sensor_list = SensorListDB.updateState("1", timestamp, parsed_newP[key])
                
                if state_port == "1" and state_sensor_list == "1":
                    result = {'state': '1', 'message': f'Succes Update Sensor Port Config'}
                    return json.dumps(result)
                else:
                    result = {'state': '0', 'message': f'Sensor Port Config Failed to Update'}
                    return json.dumps(result)

            except Exception as e:
                result = {'state': '0', 'message': f'Sensor Port Config Failed to Update, there was an issue - {e}'}
                return json.dumps(result)
