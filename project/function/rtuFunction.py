import json 
import sys

sys.path.append("/home/connex/project/database")
from query_project_db import (RtuParameterDB, RtuDeviceDB, SensorListDB,
                              SensorGroupDB, SensorParameterListDB,
                              ActuatorListDB, ActuatorGroupDB, ActuatorParameterListDB)
sys.path.append("/home/connex/project/function")
from generalFunction import generalFunction
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction

class RtuFunction:
    def createSensorandActuatorList():       
        rtu_device = RtuDeviceDB.select()
        rtu_parameter = RtuParameterDB.select()
        sensor_group_id = SensorGroupDB.selectByName("RTU")[0]["id"]
        actuator_group_id = ActuatorGroupDB.selectByName("RTU")[0]["id"]
        SensorListDB.deleteByGroupId(sensor_group_id)
        ActuatorListDB.deleteByGroupId(actuator_group_id)

        oid_number = 1

        for item_device in range(len(rtu_device)):
            for item_parameter in range(len(rtu_parameter)):
                if rtu_parameter[item_parameter]["type"] == 0 or rtu_parameter[item_parameter]["type"] == 2:
                    id_sensor = generalFunction.GenerateId.generateIdNearon("sensor", "sensor-list")
                    sensor_name = f"{rtu_parameter[item_parameter]['name']} {rtu_device[item_device]['name']}"
                    sensor_custom_id = f"{rtu_parameter[item_parameter]['custom_id']}Rtu{rtu_device[item_device]['number']}"
                    state_sensor = '1' if (rtu_device[item_device]['state'] == '1' and rtu_parameter[item_parameter]['state'] == '1') else '0'
                    datatype = rtu_parameter[item_parameter]["datatype"]
                    monitoring = rtu_parameter[item_parameter]["monitoring"]
                    log = rtu_parameter[item_parameter]["log"]
                    unit = rtu_parameter[item_parameter]["unit"]
                    
                    SensorListDB.insert(id_sensor, sensor_custom_id, oid_number, sensor_group_id, sensor_name, "0", "0", 
                                        datatype, monitoring, log, state_sensor)
                    SensorListDB.updateUnitById(id_sensor, unit)
                    oid_number += 1

                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                id_sensor, "Address", "address", rtu_parameter[item_parameter]["address"])
                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                id_sensor, "Length", "length", rtu_parameter[item_parameter]["length"])
                    SensorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("sensor", "parameter-list"), 
                                                id_sensor, "Divider", "divider", rtu_parameter[item_parameter]["divider"])
                
                if rtu_parameter[item_parameter]["type"] == 1 or rtu_parameter[item_parameter]["type"] == 2:
                    id_actuator = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-list")
                    actuator_name = f"{rtu_parameter[item_parameter]['name']} {rtu_device[item_device]['name']}"
                    actuator_custom_id = f"{rtu_parameter[item_parameter]['custom_id']}Rtu{rtu_device[item_device]['number']}"
                    type_actuator = int(rtu_parameter[item_parameter]['type_control']) - 1

                    ActuatorListDB.insert(id_actuator, actuator_group_id, actuator_name, actuator_custom_id, type_actuator)

                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                    id_actuator, "Address", "address", rtu_parameter[item_parameter]["address"])
                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                    id_actuator, "Length", "length", rtu_parameter[item_parameter]["length"])
                    ActuatorParameterListDB.insert(generalFunction.GenerateId.generateIdNearon("actuator", "actuator-parameter-list"),
                                                    id_actuator, "Divider", "divider", rtu_parameter[item_parameter]["divider"])
        
        OidSensorFunction.createSensorOid()