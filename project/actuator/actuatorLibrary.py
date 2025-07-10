import json
import re
import sys
import time

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import requests

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, RtuDeviceDB
sys.path.append("/home/connex/project/function")
from actuatorFunction import ActuatorFunction
from generalFunction import generalFunction

class ActuatorRTU():
    def run(global_variable, actuator_run, actuator_data):
        parameter_group = ActuatorFunction.getParameterGroupActuator(global_variable["number"])
        parameter_list = ActuatorFunction.getParameterListActuator(global_variable["number"])
        result_action = {"state": [], "value": [], "summary": "", "message": []}
        if len(actuator_data) > 0:
            port = generalFunction.checkUSBDevice(parameter_group["port"])
            port = port[1]
            if port != "N/A": 
                port = f"/dev/{port}"
                try:
                    rtu_object = ModbusClient(method="rtu", port=port, baudrate=int(parameter_group["baudrate"]), parity='N', stopbits=1, bytesize=8)
                except Exception as e:
                    rtu_object = None
                if rtu_object != None:
                    success_run = 0
                    for x in range(len(actuator_data)):
                        try:
                            if actuator_run["action"][x] == True:
                                actuator_custom_id = actuator_data[x]["actuator_custom_id"]
                                rtu_number = actuator_custom_id[actuator_custom_id.lower().find("rtu") + 3:]
                                slave_id = int(RtuDeviceDB.selectByNumber(rtu_number)[0]["slave_id"])
                                address = int(parameter_list[actuator_data[x]["actuator_custom_id"]]["address"])
                                divider = int(parameter_list[actuator_data[x]["actuator_custom_id"]]["divider"])
                                if address > 40000:
                                    result = rtu_object.write_register(address=address-40001, value=int(actuator_run["value"][x]) * divider, unit=slave_id)
                                else:
                                    result = rtu_object.write_coil(address=address-1, value=int(actuator_run["value"][x]) * divider, unit=slave_id)
                                if result.isError() == False:
                                    result_state, result_value = True, result.value
                                    result_action["message"].append("Success")
                                    success_run += 1
                                else:
                                    result_state, result_value = False, None
                                    result_action["message"].append(result.message)
                            else:
                                result_state, result_value= False, None
                                result_action["message"].append("Skip Run")
                        except Exception as e:
                            result_state, result_value = False, None
                            result_action["message"].append(str(e))
                        result_action["state"].append(result_state)
                        result_action["value"].append(result_value)
                    result_action["summary"] = f"Success Run {success_run} of {actuator_run['count']} Actuator from {len(actuator_data)} Actuator"
                else:
                    result_action["state"].append(False)
                    result_action["value"].append(None)
                    result_action["message"].append("RTU Device Not Found")
                    result_action["summary"] = "RTU Device Not Found"    
            else:
                result_action["state"].append(False)
                result_action["value"].append(None)
                result_action["message"].append("Port N/A")
                result_action["summary"] = "Port N/A"
        else:
            result_action["summary"] = "No Actuator Data"
        # print(result_action)
        return result_action


def actuatorAC(actuator_custom_id, value):
   def sendCommand(actuator_custom_id, value, swing, temp, url_ac):
      headers = {"content-type": "application/json"} 
      data_json = json.dumps({'ac':str(actuator_custom_id), 'state':str(value), 'swing':swing, 'temp':str(temp)})
      send = requests.post(url=url_ac, data=data_json, headers=headers, timeout=10)
      state = send.status_code
      return send.json(), state  
      
   status, num = None, 0 
   actuator_custom_id = actuator_custom_id.replace("remote","")
   parameterActuator = ActuatorFunction.getParameterListActuator(actuator_custom_id)  
   try:   
      url_ac = f"http://{parameterActuator['ip']}{parameterActuator['endpoint']}"
      response_state = None
      while num < 1:
         num += 1
         timestamp = times.getDatetime()
         send, state = sendCommand(actuator_custom_id, value, parameterActuator['swing'], parameterActuator['temperature'], url_ac)
         if state == 200:
            response_state = send['data']['state']  # Mengakses state dari respons JSON
            SensorListDB.updateValue(response_state, timestamp, "stateAc" + str(actuator_custom_id))
            status = "Action Success"
         else:
            status = "Action Error"
         time.sleep(1) 
         
   except Exception as e:
      num = 1          
      state = 404
      status = f"Action Failed - {str(e)}"

   status = str(status) + " | " + str(num) + "x Action"   
   return status
