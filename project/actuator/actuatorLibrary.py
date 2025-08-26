import json
import re
import sys
import time
import RPi.GPIO as GPIO
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import requests
import minimalmodbus
import serial

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
                                divider = float(parameter_list[actuator_data[x]["actuator_custom_id"]]["divider"])
                                if address > 40000:
                                    result = rtu_object.write_register(address=address-40001, value=int(int(actuator_run["value"][x]) * divider), unit=slave_id)
                                else:
                                    result = rtu_object.write_coil(address=address-1, value=int(int(actuator_run["value"][x]) * divider), unit=slave_id)
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


def read_water_level_safety():
    """
    Baca water level untuk safety check
    Returns: water level dalam cm, atau None jika error
    """
    try:
        # Konfigurasi water level sensor
        SERIAL_PORT = '/dev/ttyUSB0'
        DEVICE_ID = 1
        BAUD_RATE = 9600
        WATER_LEVEL_UNIT = 'cm'
        
        # Setup minimalmodbus
        instrument = minimalmodbus.Instrument(SERIAL_PORT, DEVICE_ID)
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.baudrate = BAUD_RATE
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 2.0
        instrument.close_port_after_each_call = True
        instrument.clear_buffers_before_each_transaction = True
        
        # Baca register 4 (water level)
        result = instrument.read_registers(4, 1, 3)
        water_level = result[0]
        
        # Konversi ke cm jika perlu
        if WATER_LEVEL_UNIT == 'mm':
            water_level = water_level / 10
            
        return water_level
        
    except Exception as e:
        print(f"⚠️  Water level safety check error: {e}")
        return None


def check_water_level_safety(actuator_custom_id):
    """
    Cek water level safety untuk pompa
    Returns: True jika aman, False jika perlu dimatikan
    """
    # Hanya cek untuk water pump
    if "water" in actuator_custom_id.lower() or "pump" in actuator_custom_id.lower():
        water_level = read_water_level_safety()
        
        if water_level is not None:
            # Safety threshold: 10 cm
            SAFETY_THRESHOLD = 10
            
            if water_level >= SAFETY_THRESHOLD:
                print(f"🚨 SAFETY ALERT: Water level {water_level:.1f} cm ≥ {SAFETY_THRESHOLD} cm")
                print(f"🔴 Pompa {actuator_custom_id} akan dimatikan untuk keamanan")
                return False  # Perlu dimatikan
            else:
                print(f"✅ Water level aman: {water_level:.1f} cm < {SAFETY_THRESHOLD} cm")
                return True  # Aman
        else:
            print(f"⚠️  Tidak bisa membaca water level untuk {actuator_custom_id}")
            return True  # Biarkan berjalan jika tidak bisa baca sensor
    
    return True  # Bukan pompa, biarkan berjalan


def start_water_level_monitoring(actuator_custom_id, pin):
    """
    Start monitoring water level saat pompa aktif
    """
    import threading
    import time
    
    def monitor_water_level():
        print(f"🚰 Memulai monitoring water level untuk {actuator_custom_id}")
        while True:
            try:
                water_level = read_water_level_safety()
                if water_level is not None:
                    SAFETY_THRESHOLD = 10
                    if water_level >= SAFETY_THRESHOLD:
                        print(f"🚨 SAFETY TRIGGER: Water level {water_level:.1f} cm ≥ {SAFETY_THRESHOLD} cm")
                        print(f"🔴 Matikan pompa {actuator_custom_id} via GPIO pin {pin}")
                        
                        # Matikan pompa via GPIO
                        GPIO.setmode(GPIO.BCM)
                        GPIO.setup(pin, GPIO.OUT)
                        GPIO.output(pin, GPIO.LOW)
                        
                        print(f"✅ Pompa {actuator_custom_id} berhasil dimatikan untuk keamanan")
                        break  # Stop monitoring
                    else:
                        print(f"✅ Water level aman: {water_level:.1f} cm")
                else:
                    print(f"⚠️  Tidak bisa membaca water level")
                
                time.sleep(5)  # Cek setiap 5 detik
                
            except Exception as e:
                print(f"❌ Error monitoring water level: {e}")
                time.sleep(5)
    
    # Start monitoring dalam thread terpisah
    monitor_thread = threading.Thread(target=monitor_water_level, daemon=True)
    monitor_thread.start()
    print(f"🔄 Monitoring thread started untuk {actuator_custom_id}")


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

class ActuatorGPIO():
    def run(global_variable, actuator_run, actuator_data):
        parameter_list = ActuatorFunction.getParameterListActuator(global_variable["number"])
        result_action = {"state": [], "value": [], "summary": "", "message": []}
        
        if len(actuator_data) > 0:
            try:
                # Setup GPIO mode
                GPIO.setmode(GPIO.BCM)
                GPIO.setwarnings(False)
                
                success_run = 0
                for x in range(len(actuator_data)):
                    try:
                        if actuator_run["action"][x] == True:
                            actuator_custom_id = actuator_data[x]["actuator_custom_id"]
                            pin = int(parameter_list[actuator_data[x]["actuator_custom_id"]]["pin"])
                            value = int(actuator_run["value"][x])
                            
                            # Safety check untuk water pump
                            if value == 1:  # Jika akan mengaktifkan pompa
                                if not check_water_level_safety(actuator_custom_id):
                                    # Water level tinggi, paksa matikan pompa
                                    print(f"🚨 EMERGENCY SHUTDOWN: Pompa {actuator_custom_id} dimatikan paksa")
                                    value = 0  # Paksa matikan
                                    result_action["message"].append("Emergency Shutdown - Water Level High")
                                else:
                                    # Start monitoring water level jika pompa akan diaktifkan
                                    if "water" in actuator_custom_id.lower() or "pump" in actuator_custom_id.lower():
                                        start_water_level_monitoring(actuator_custom_id, pin)
                                    result_action["message"].append("Success")
                            else:
                                result_action["message"].append("Success")
                            
                            # Setup pin as output
                            GPIO.setup(pin, GPIO.OUT)
                            
                            # Set pin value (0 for OFF, 1 for ON)
                            GPIO.output(pin, value)
                            
                            result_state, result_value = True, value
                            success_run += 1
                        else:
                            result_state, result_value = False, None
                            result_action["message"].append("Skip Run")
                    except Exception as e:
                        result_state, result_value = False, None
                        result_action["message"].append(str(e))
                    result_action["state"].append(result_state)
                    result_action["value"].append(result_value)
                
                result_action["summary"] = f"Success Run {success_run} of {actuator_run['count']} Actuator from {len(actuator_data)} Actuator"
                
            except Exception as e:
                result_action["state"].append(False)
                result_action["value"].append(None)
                result_action["message"].append(f"GPIO Error: {str(e)}")
                result_action["summary"] = f"GPIO Error: {str(e)}"
        else:
            result_action["summary"] = "No Actuator Data"
        
        return result_action
