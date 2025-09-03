
from math import sqrt
import re
import sys
import time
import os
import glob
import subprocess
import math
import numpy as np

from gpiozero import MCP3008
import minimalmodbus
import psutil
import puresnmp
from pythonping import ping
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import requests
import RPi.GPIO as GPIO
import serial

# Add ADS1115 import for water quality sensors
try:
    import Adafruit_ADS1x15.ADS1x15 as ADS1x15
    ADS1115_AVAILABLE = True
except ImportError:
    ADS1115_AVAILABLE = False
    print("Warning: Adafruit_ADS1x15 not available. Water quality sensors will not work.")

sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SensorGroupDB, EnvironmentDeviceDB, PowerDeviceDB,  SensorPortConfigDB, RtuDeviceDB, LogSensorDB
sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append("/home/connex/project/function")
from serviceProjectFunction import ServiceProjectFunction
from generalFunction import generalFunction
sys.path.append("/home/connex/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction

from icecream import ic


def handleSensorValue(dataSensor):
    sensorValue, sensorState = [], []
    for x in range(dataSensor['numSensor']):
        if dataSensor['sensorDatatype'][x] == 1:
            sensorValue.append('N/A')
            sensorState.append(True)
        else:
            sensorValue.append(0.00)
            sensorState.append(True)
    return sensorValue, sensorState

class Environment:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.active_ports = SensorPortConfigDB.selectByActivePort()
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(self.dataSensor)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)


    class SensorHandler:
        def readSHT20(self, port):
            try:
                instrument = minimalmodbus.Instrument(self.parameterGroupSensor['portSerial'], int(port["modbus_id"]))
                instrument.mode = minimalmodbus.MODE_RTU
                instrument.serial.baudrate = 9600
                instrument.serial.bytesize = 8
                instrument.serial.parity = serial.PARITY_NONE
                instrument.serial.stopbits = 1
                instrument.serial.timeout = 0.2
                instrument.close_port_after_each_call = True
                instrument.clear_buffers_before_each_transaction = True
                result = instrument.read_registers(1, 2, 4)
                temp = result[0] / 10
                humid = result[1] / 10
                return {"value": [temp, humid], "state": True, "port": port["name"], "message": "Success Sampling SHT20 Sensor"}
            except Exception as e:
                port['name'] = port['name'].replace("port_", "Port ")
                return {"value": [0.00, 0.00], "state": False, "port": port["name"], "message": F"Error SHT20 {port['name']} {e}"}


        def readSmoke(self, port):
            pin = int(port["digital_pin"])
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                smoke = GPIO.input(pin)
                return {"value": smoke, "state": True, "port": port["name"], "message": "Success Sampling Smoke Sensor"}
            except Exception as e:
                port['name'] = port['name'].replace("port_", "Port ")
                return {"value": -1, "state": False, "port": port["name"], "message": F"Error Smoke {port['name']} {e}"}


        def readDoor(self, port):
            pin = int(port["digital_pin"])
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                door = GPIO.input(pin)
                return {"value": door, "state": True, "port": port["name"], "message": "Success Sampling Door Sensor"}
            except Exception as e:
                port['name'] = port['name'].replace("port_", "Port ")
                return {"value": -1, "state": False, "port": port["name"], "message": F"Error Door {port['name']} {e}"}


        def readWaterLevel(self, port):
            try:
                instrument = minimalmodbus.Instrument(self.parameterGroupSensor['portSerial'], int(port["modbus_id"]))
                instrument.mode = minimalmodbus.MODE_RTU
                instrument.serial.baudrate = 9600
                instrument.serial.bytesize = 8
                instrument.serial.parity = serial.PARITY_NONE
                instrument.serial.stopbits = 1
                instrument.serial.timeout = 0.2
                instrument.close_port_after_each_call = True
                instrument.clear_buffers_before_each_transaction = True
                result = instrument.read_registers(4, 1, 3)  # Read register 4 with function code 03
                water_level = result[0]  
                return {"value": water_level, "state": True, "port": port["name"], "message": "Success Sampling Water Level Sensor"}
            except Exception as e:
                port['name'] = port['name'].replace("port_", "Port ")
                return {"value": 0.00, "state": False, "port": port["name"], "message": F"Error Water Level {port['name']} {e}"}
    def main(self):
        self.groupData = SensorGroupDB.selectOne(self.groupId)

        if self.dataSensor['numSensor'] > 0:
            self.handler_mapping = {
                "1": Environment.SensorHandler.readSHT20,
                "2": Environment.SensorHandler.readSmoke,
                "3": Environment.SensorHandler.readDoor,
                "4": Environment.SensorHandler.readWaterLevel,
            }

            results = []
            state = []
            success_count = 0
            failed_count = 0
            error_messages = []

            for port in self.active_ports:
                port_type = port["type"]
                if port_type in self.handler_mapping:
                    result = self.handler_mapping[port_type](self, port)

                    if port_type == "1":  # SHT20
                        results.extend(result["value"])
                        state.extend([result["state"], result["state"]])
                    else:
                        results.append(result["value"])
                        state.append(result["state"])

                    if result["state"] == True:
                        success_count += len(result["value"]) if isinstance(result["value"], list) else 1
                    else:
                        failed_count += len(result["value"]) if isinstance(result["value"], list) else 1
                        error_messages.append(result["message"])

            self.sensorValue = results
            self.sensorState = state

            if failed_count == 0:
                sensorMessage = f"{success_count} Sensors Success Sampling"
            else:
                error_details = ", ".join(error_messages)
                if failed_count == self.dataSensor['numSensor']:
                    sensorMessage = f"{failed_count} Sensors Failed Sampling ({error_details})"
                else:
                    sensorMessage = f"{self.dataSensor['numSensor']-failed_count} of {self.dataSensor['numSensor']} Sensors Success Sampling | {error_details}"

            sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
            return sensorResult

        else:
            self.sensorState = []
            self.sensorValue = []
            sensorMessage = f"No List Sensors Registered on Group Sensor {str(self.groupData[0]['name'])}"
            sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
            return sensorResult


class Power:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(self.dataSensor)
        
        self.pinClk = 21
        self.pinMiso = 19
        self.pinMosi = 20
        self.pinCs = 18


    def readVoltInternal(self):
        parameterListSensorInternal = CollectDataSensorFunction.getParameterListSensor(7)
        mcp3008Internal = self.getMCP3008(channel=int(parameterListSensorInternal['nearonVolt']['pin']))
        adcInputConnexVoltage = mcp3008Internal.voltage
        voltInternal = round((adcInputConnexVoltage) * float(parameterListSensorInternal['nearonVolt']['offset']), 2) 
        return voltInternal


    def getMCP3008(self, channel):
        return MCP3008(clock_pin=self.pinClk, mosi_pin=self.pinMosi,
                        miso_pin=self.pinMiso, select_pin=self.pinCs, channel=channel)


    class ZMPT101B:
        def __init__(self, parent, channel, parameterGroupSensor):
            self.parent = parent
            self.channel = channel
            self.parameterGroupSensor = parameterGroupSensor
            self.period = 1.0 / 50.0
            self.adcScale = 1023.0
            self.vRef = 3.3
            self.offset = 1
            
            self.sensitivityVolt = int(self.parameterGroupSensor['sensitivityVoltage'])


        def setSensitivity(self, value):
            self.sensitivity = value


        def getZeroPoint(self):
            Vsum = 0
            measurements_count = 0
            t_start = time.time()

            while time.time() - t_start < self.period:
                Vsum += self.parent.getMCP3008(channel=self.channel).value * self.adcScale
                measurements_count += 1

            return Vsum / measurements_count


        def getRmsVoltage(self, loopCount):
            reading_voltage = 0.0
            for _ in range(loopCount):
                zero_point = self.getZeroPoint()
                Vnow = 0
                Vsum = 0
                measurements_count = 0

                while measurements_count < 100:
                    Vnow = (self.parent.getMCP3008(channel=self.channel).value * self.adcScale) - zero_point
                    Vsum += (Vnow ** 2)
                    measurements_count += 1

                self.setSensitivity(self.sensitivityVolt)
                reading_voltage += sqrt(Vsum / measurements_count) / self.adcScale * self.vRef * self.sensitivityVolt
            return (reading_voltage / loopCount) + self.offset


    class ACS712:
        def __init__(self, parent, channel, parameterGroup):
            self.parent = parent
            self.channel = channel
            self.parameterGroupSensor = parameterGroup
            self.adcScale = 1023.0
            self.vRef = 3.3
            self.zeroPoint = 766
            self.frequency = 50.0

            self.sensitivityCurr = float(self.parameterGroupSensor['sensitivityCurrent'])

        def set_sensitivity(self, sensitivity):
            self.sensitivityCurr = sensitivity
        

        def readCurrent(self):
            period = 1.0 / self.frequency
            t_start = time.time()
            Isum = 0
            measurements_count = 0
            while time.time() - t_start < period:
                Inow = self.parent.getMCP3008(channel=self.channel).value * self.adcScale - self.zeroPoint
                Isum += Inow**2
                measurements_count += 1
            Irms = sqrt(Isum / measurements_count) / self.adcScale * self.vRef / self.sensitivityCurr
            return Irms


    def handleValue(self, value):
        if value == None or value <= 0.50:
            value = 0.00
        else:
            value = round(value, 2)
        return value


    def main(self, globalVariable):
        if self.dataSensor['numSensor'] > 0:
            results = []
            state = []
            success_count = 0
            failed_count = 0
            error_messages = []

            try:
                voltInternal = self.readVoltInternal()
                SensorListDB.updateValue(voltInternal, times.now(), 42)
            except Exception as e:
                voltInternal = 0.00
                error_messages.append(f"Internal Voltage Error: {str(e)}")
            
            port_index = 0  
            for index, sensor_id in enumerate(self.dataSensor["sensorId"]):
                sensor_name = self.dataSensor["sensorName"][index]
                sensor_pin = int(self.parameterListSensor[sensor_id]["pin"])
                

                try:
                    if sensor_id == "acVoltage":
                        voltage_sensor = self.ZMPT101B(self, sensor_pin, self.parameterGroupSensor)
                        voltage_value = round(voltage_sensor.getRmsVoltage(10), 2)
                        results.append(voltage_value)
                        state.append(True)
                        success_count += 1
                        port_index = 0
                    elif sensor_id.startswith("acCurrent"):
                        port_index += 1
                        if globalVariable[f"calibratePort{port_index}"] == 0:
                            ac_current = self.ACS712(self, sensor_pin, self.parameterGroupSensor)
                            globalVariable[f"acsPort{port_index}"] = ac_current
                            globalVariable[f"calibratePort{port_index}"] = 1

                        ac_current_value = round(globalVariable[f"acsPort{port_index}"].readCurrent(), 2)
                        ac_current_value = self.handleValue(ac_current_value)
                        results.append(ac_current_value)
                        state.append(True)
                        success_count += 1

                except Exception as e:
                    results.append(0.00)
                    state.append(False)
                    failed_count += 1
                    error_messages.append(f"{sensor_name} Error : {str(e)}")

            self.sensorValue = results
            self.sensorState = state

            if failed_count == 0:
                sensorMessage = f"{success_count} Sensors Success Sampling"
            else:
                error_details = ", ".join(error_messages)
                if failed_count == self.dataSensor['numSensor']:
                    sensorMessage = f"{failed_count} Sensors Failed Sampling ({error_details})"
                else:
                    sensorMessage = f"{self.dataSensor['numSensor'] - failed_count} of {self.dataSensor['numSensor']} Sensors Success Sampling | {error_details}"

            sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
            return sensorResult
        
        else:
            self.sensorState = [False] * len(self.dataSensor["sensorId"])
            self.sensorValue = [0.00] * len(self.dataSensor["sensorId"])
            sensorMessage = 'No List Sensors Registered on Group Sensor ' + str(self.groupData[0]['name'])
            sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
            return sensorResult

class ACLoadOutput():
    def main(groupId, dataSensor):
        groupId = groupId
        dataSensor = dataSensor
        groupData = SensorGroupDB.selectOne(groupId)
        parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(groupId)
        parameterListSensor = CollectDataSensorFunction.getParameterListSensor(groupId)
        sensorValue, sensorState = handleSensorValue(dataSensor)
        ads1 = ADS1x15.ADS1115(address=0x48, busnum=1)
        ads2 = ADS1x15.ADS1115(address=0x49, busnum=1)
        acLoadOutput = {'acLoadOutput1': {}, 'acLoadOutput2': {}, 'acLoadOutput3': {}, 'acLoadOutput4': {}, 'acLoadOutput5': {}, 'acLoadOutput6': {}, 'acLoadOutput7': {}, 'acLoadOutput8': {}}
        samples = []
        num_samples = 50  

        # Debug: Print available keys in parameterListSensor
        print(f"Available keys in parameterListSensor: {list(parameterListSensor.keys())}")
        
        # Debug: Print the actual data structure
        for key, value in parameterListSensor.items():
            print(f"Key: '{key}', Value: {value}")
        
        # Clean parameterListSensor keys by removing any whitespace characters
        cleaned_parameterListSensor = {}
        for key, value in parameterListSensor.items():
            cleaned_key = key.strip()  # Remove leading/trailing whitespace including tabs
            cleaned_parameterListSensor[cleaned_key] = value
        
        for i in range(1, 9):
            load_key = f'acLoadOutput{i}'
            sensor_key = f'acLoadCurrent{i}'
            
            # Check if sensor_key exists in cleaned parameterListSensor
            if sensor_key not in cleaned_parameterListSensor:
                print(f"Warning: {sensor_key} not found in parameterListSensor")
                acLoadOutput[load_key] = {
                    'specification': 6.0,  # Default value
                    'port': 0,  # Default value
                    'status': 'on'  # Default value
                }
            else:
                try:
                    # Debug: Print the sensor data structure
                    # print(f"Processing {sensor_key}: {cleaned_parameterListSensor[sensor_key]}")
                    
                    # Safely extract values with defaults
                    sensor_data = cleaned_parameterListSensor[sensor_key]
                    
                    # Try to get specification, default to 5.0 if not available or invalid
                    try:
                        spec_value = sensor_data.get('specification', '5.0')
                        if isinstance(spec_value, str) and spec_value.lower() in ['on', 'off']:
                            specification = 5.0  # Default if status value is in specification field
                        else:
                            specification = float(spec_value)
                    except (ValueError, TypeError):
                        specification = 5.0
                    
                    # Try to get port, default to 0 if not available or invalid
                    try:
                        port_value = sensor_data.get('port', '0')
                        port = int(port_value)
                    except (ValueError, TypeError):
                        port = 0
                    
                    # Try to get status, default to 'on' if not available
                    status = str(sensor_data.get('status', 'on'))
                    
                    acLoadOutput[load_key] = {
                        'specification': specification,
                        'port': port,
                        'status': status
                    }
                    
                    # print(f"Parsed {load_key}: spec={specification}, port={port}, status={status}")
                    
                except Exception as e:
                    print(f"Error parsing {sensor_key}: {e}")
                    acLoadOutput[load_key] = {
                        'specification': 5.0,  # Default value
                        'port': 0,  # Default value
                        'status': 'on'  # Default value
                    }

        sensorMessage = ''
        if dataSensor['numSensor'] > 0:
            try:
                acLoadCurrents = []
                for i in range(1, 9):
                    samples = []
                    load_key = f'acLoadOutput{i}'
                    if acLoadOutput[load_key]['status'] == 'on':
                        ads_used = ads1 if i <= 4 else ads2
                        port = acLoadOutput[load_key]['port']
                        sensitivity = acLoadOutput[load_key]['specification']
                        if sensitivity == 5:
                            sensitivity = sensitivity + 1.5

                        elif sensitivity == 10:
                            sensitivity = sensitivity + 3

                        for _ in range(num_samples):
                            voltage = ACLoadOutput.read_voltage(ads_used, int(port))
                            samples.append(voltage)
                            time.sleep(0.001)
                        mean_voltage = np.mean(samples)
                        centered_samples = [v - mean_voltage for v in samples]
                        rms_voltage = ACLoadOutput.calculate_rms(centered_samples)
                        acLoadCurrent = round(float(rms_voltage * sensitivity), 2)
                        if mean_voltage <= 1:
                            acLoadCurrent = 0.00
                            
                    else:
                        acLoadCurrent = 0.0

                    acLoadCurrents.append(acLoadCurrent)
                sensorValue = acLoadCurrents
                sensorMessage = f"{dataSensor['numSensor']} Sensors Success Sampling"
            
            except Exception as e:
                sensorState = [False] * 8
                sensorMessage = f"{dataSensor['numSensor']} Sensors Failed Sampling - {str(e)}"

        else:
            sensorMessage = f"No List Sensors Registered on Group Sensor {groupData[0]['name']}"

        return {"value": sensorValue, "message": sensorMessage, "state": sensorState}

    @staticmethod
    def read_voltage(ads, channel):
        # Gain 1 corresponds to ±4.096V range
        raw = ads.read_adc(channel, gain=1)
        
        # Convert raw ADC value to voltage manually
        # For ADS1115 with gain=1, the voltage range is ±4.096V
        # ADS1115 is 16-bit, so range is -32768 to 32767
        voltage = (raw / 32767.0) * 4.096
        
        return voltage

    @staticmethod
    def calculate_rms(values):
        squares = [v**2 for v in values]
        mean = np.mean(squares)
        return np.sqrt(mean)

class EnvironmentExt:
    def __init__(self, group_id, data_sensor):
        self.data_sensor = data_sensor
        self.group_id = group_id
        self.endpoint = CollectDataSensorFunction.getParameterGroupSensor(self.group_id)['endpoint']
        self.modbus_port = CollectDataSensorFunction.getParameterGroupSensor(self.group_id)['modbus_port']
        self.sensor_list = self.data_sensor["sensorId"]
        self.devices = EnvironmentDeviceDB.selectByNumberOrderd()
        self.port_num = 8

        self.client = ModbusClient(method='rtu', port=self.modbus_port, baudrate=9600, timeout=3)
        self.client.connect()

        self.sensor_value = [0.0 if "temp" in sensor.lower() or "humid" in sensor.lower() else -1 for sensor in self.sensor_list]
        self.sensor_state = [False] * len(self.sensor_list)
        self.sensor_message = ""
        self.sync_message = []
        self.unsync_message = []
        self.error_message = []
        self.error_devices = set() 

        self.sensor_index_map = {sensor.lower(): idx for idx, sensor in enumerate(self.sensor_list)}

        self.deffault_values = {
            "temp": 0.00,
            "humid": 0.00,
            "smoke": -1,
            "door": -1,
            "water": -1,
        }
        self.default_state = False

    def fetchNetworkData(self, ip):
        url = f"http://{ip}{self.endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response


    def fetchModbusData(self, slave_id, start_register, count):
        result = self.client.read_holding_registers(start_register, count, unit=slave_id)
        if result.isError():
            print(f"Error Register {start_register}")
        else:
            return result.registers


    def parsePortData(self, method, port_type, values, state):
        def roundValue(val):
            try:
                return round(float(val), 2)
            except (ValueError, TypeError):
                return val
        
        if method == "0":  # Network Method
            mappings = {
                "sht20": {"temp": roundValue(values.get("temp", 0.00)), "humid": roundValue(values.get("humid", 0.00))},
                "smoke": {"smoke": values.get("smoke", -1)},
                "door": {"door": values.get("door", -1)},
                "waterleak": {"water": values.get("waterleak", -1)},
            }
            parsed_data = mappings.get(port_type, {"state": False, "undefined": "N/A"})
            parsed_data["state"] = state
            return parsed_data
        else:
            mappings_modbus = {
                "sht20": {"temp": roundValue(values[0] / 10.0), "humid": roundValue(values[1] / 10.0)},  # SHT20
                "smoke": {"smoke": values[2]},  # Smoke Sensor
                "door": {"door": values[3]},  # Door Sensor
                "water": {"water": values[4]},  # Water Leak Sensor
            }
            port_type_mapping = {
                1: "sht20",
                2: "smoke",
                3: "door",
                4: "water",
            }
            mappings_state = {
                1: "Success",
                2: "Error Tolerance",
                3: "Error",
                99: "Disable"
            }
            
            sensor_type = port_type_mapping.get(port_type, "Undefined")
            parsed_data = mappings_modbus.get(sensor_type, {"state": False, "undefined": "N/A"})
            parsed_data["state"] = mappings_state.get(state, "Disable")
            return parsed_data


    def parseResult(self, results):
        processed_sensors = set()

        for device_result in results:
            device_number = device_result.get("device", 0)
            ports = device_result.get("ports", {})

            for port, port_data in sorted(ports.items()):
                # port_type = port_data.get("type", "Undefined")
                port_state = port_data.get("state", "Disable")

                for sensor_key in ["temp", "humid", "smoke", "door", "water"]:
                    
                    if sensor_key in port_data:
                        sensor_name = f"{sensor_key}p{port[-1]}ext{device_number}"
                        idx = self.sensor_index_map.get(sensor_name.lower())

                        if idx is not None and sensor_name.lower() not in processed_sensors:
                            processed_sensors.add(sensor_name.lower())
                            self.sensor_value[idx] = port_data.get(sensor_key, self.deffault_values[sensor_key])
                            self.sensor_state[idx] = True if port_state == "Success" else False
                            
                            if port_state == "Success" and sensor_name not in self.sync_message:
                                self.sync_message.append(sensor_name)
                                
                            elif port_state == "Error" and sensor_name not in self.error_message:
                                self.error_message.append({sensor_name: "Port Error"})

                            elif port_state == "Error Tolerance" and sensor_name not in self.error_message:
                                self.error_message.append({sensor_name: "Port Error Tolerance"})

                            elif port_state == "Disable" and sensor_name not in self.unsync_message:
                                self.unsync_message.append({sensor_name: "Unsync"})

        for sensor in self.sensor_list:
            sensor_lower = sensor.lower()

            device_number_match = [int(x) for x in sensor_lower.split("ext")[-1] if x.isdigit()]
            if device_number_match:
                device_number = device_number_match[0]

                if device_number in self.error_devices and sensor_lower not in processed_sensors:
                    processed_sensors.add(sensor_lower)

                    if not any(sensor in err for err in self.error_message):
                        self.error_message.append({sensor: "Device Offline"})
                    continue

            if (
                sensor_lower not in processed_sensors
                and sensor_lower not in self.unsync_message
                and not any(sensor in err for err in self.error_message)
            ):
                self.unsync_message.append({sensor: "Unsynchronize"})


    def handleError(self, sensor_list):
        for sensor in sensor_list:
            sensor_lower = sensor.lower()

            if any(sensor_lower in msg for msg in self.sync_message + self.unsync_message + self.error_message):
                continue

            idx = self.sensor_index_map.get(sensor_lower)
            if idx is not None:
                if "temp" in sensor.lower() or "humid" in sensor.lower():
                    self.sensor_value[idx] = self.deffault_values["temp" if "temp" in sensor.lower() else "humid"]
                elif "smoke" in sensor.lower():
                    self.sensor_value[idx] = self.deffault_values["smoke"]
                elif "door" in sensor.lower():
                    self.sensor_value[idx] = self.deffault_values["door"]
                elif "water" in sensor.lower():
                    self.sensor_value[idx] = self.deffault_values["water"]

                self.sensor_state[idx] = self.default_state
                self.error_message.append({sensor: "Device Offline"})


    def main(self):
        if self.data_sensor['numSensor'] > 0:
            results = []

            for i, device in enumerate(self.devices):
                if int(device["state"]) == 1:
                    try:
                        number, method, modbus_id, ip, name = device['number'], device["method"], device["modbus_id"], device["ip"], device["name"]

                        if method == "0": # Network Method
                            data = self.fetchNetworkData(ip)
                            if data.status_code == 200:
                                data_json = data.json()
                                if data_json.get("status") == "Success":
                                    ports = data_json.get("data", {})
                                    device_result = {"device": number, "name": name, "ip": ip, "ports": {}}

                                    for port, port_data in ports.items():
                                        device_result["ports"][port] = self.parsePortData(
                                            method, port_data.get("type", "Disable"), port_data.get("value", {}), port_data.get("state", "Disable")
                                        )
                                    results.append(device_result)
                                else:
                                    raise ValueError(f"Error State Message ({data_json.get('status')})")
                            else:
                                raise ValueError(f"HTTP Error: {data.status_code}")
                    
                        else: # Modbus Method
                            device_result = {"device": number, "name": name, "modus_slave": modbus_id, "ports": {}}
                            start_register = 200
                            total_registers = self.port_num * 5 

                            sensor_data = self.fetchModbusData(int(modbus_id), start_register, total_registers)
                            type_sensor = self.fetchModbusData(int(modbus_id), 100, self.port_num)
                            state_sensor = self.fetchModbusData(int(modbus_id), 300, self.port_num)


                            for port in range(self.port_num):
                                if sensor_data and type_sensor and state_sensor:
                                    base_index = port * 5

                                    temp = sensor_data[base_index]
                                    humid = sensor_data[base_index + 1]
                                    smoke = sensor_data[base_index + 2]
                                    door = sensor_data[base_index + 3]
                                    water_leak = sensor_data[base_index + 4]

                                    sensor_ports = [temp, humid, smoke, door, water_leak]
                                    device_result["ports"][F"port{port+1}"] = self.parsePortData(
                                        method, type_sensor[port], sensor_ports, state_sensor[port]
                                    )

                            results.append(device_result)
                    except Exception:
                        self.error_devices.add(device['number'])
                        device_sensors = [
                            sensor for sensor in self.sensor_list if f"ext{device['number']}" in sensor.lower()
                        ]
                        self.handleError(device_sensors)
            
            self.parseResult(results)
            total_sensor = self.data_sensor['numSensor']
            success_sensors = int(total_sensor) - int(len(self.unsync_message)) - int(len(self.error_message))
            if success_sensors == 0:
                summary = f"{total_sensor - success_sensors} Sensors Failed Sampling"
            else:
                summary = f"{success_sensors} of {total_sensor} Sensors Success Sampling"
                
            def formatPorts(port_list):
                formatted_ports = []
                for port in port_list:
                    if "humid" not in port:
                        port = port.replace('water', '').replace('temp', '').replace('humid', '').replace('smoke', '').replace('door', '')
                        formatted_ports.append(f"Port {port[1]} Ext {port[-1]}")
                return ", ".join(formatted_ports)

            if self.unsync_message:
                summary += f" | {len(self.unsync_message)} Port Error Unsynchronize ("
                for x in range(len(self.unsync_message)):
                    port, key_json = '', ''
                    for key in self.unsync_message[x].keys():
                        key_json = key
                        key = key.replace('water', '').replace('temp', '').replace('humid', '').replace('smoke', '').replace('door', '')
                        port = f"Port {key[1]} Ext {key[-1]}"
                    if 'humid' not in key_json: summary += f"{port}"
                    if x + 1 != len(self.unsync_message):
                        if 'temp' not in key_json: summary += ", "
                summary += ")"

            if self.error_message:
                port_device_offline, port_error = [], []
                for x in range(len(self.error_message)):
                    for key in self.error_message[x].keys():
                        if self.error_message[x][key] == 'Device Offline' and 'humid' not in key: port_device_offline.append(key)
                        elif self.error_message[x][key] == 'Port Error' and 'humid' not in key: port_error.append(key)
                if port_device_offline:
                    summary += f" - {len(port_device_offline)} Port Error Device Offline ({formatPorts(port_device_offline)})"
                if port_error:
                    summary += f" - {len(port_error)} Port Error Sampling ({formatPorts(port_error)})"

            self.sensor_message = summary
            sensor_result = {
                "value": self.sensor_value,
                "message": self.sensor_message,
                "state": self.sensor_state,
            }
            return sensor_result


class PowerExt:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.endpoint = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)['endpoint']
        self.sensorList = self.dataSensor["sensorId"]
        self.devices = PowerDeviceDB.selectByNumberOrderd()

        self.sensorState = [False] * len(self.sensorList)
        self.sensorValue = [0.0  for sensor in self.sensorList]
        self.success_message = []
        self.error_messages = []
        self.sensor_message = ""

    def handle(self, value):
        if value == None:
            value = 0.00
        else:
            value = round(value, 2)
        return value
    
    def fetch_data(self, ip):
        url = f"http://{ip}{self.endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response
    
    def parse_port_data(self, device, data):

        for i in range(len(self.sensorList)):
            for key, item in data.items():
                if "voltage" in self.sensorList[i].lower() and "voltage" in key.lower():
                    if F"{key}Ext{device}".lower() in self.sensorList[i].lower():
                        self.sensorValue[i] = item
                        self.sensorState[i] = True
                        self.success_message.append(self.sensorList[i])

                elif "current" in self.sensorList[i].lower() and "current" in key.lower():
                    for current_name, current_value in data[key].items():
                        port_current = F"{key}{current_name[-1]}Ext{device}"
                        if port_current.lower() in self.sensorList[i].lower():
                            self.sensorValue[i] = current_value
                            self.sensorState[i] = True
                            self.success_message.append(self.sensorList[i])


    def handle_error(self, device):
        for i in range(len(self.sensorList)):
            if F"Ext{device}".lower() in self.sensorList[i].lower():
                self.error_messages.append(F"{self.sensorList[i]}")


    def main(self):
        if self.dataSensor['numSensor'] > 0:

            for i, device in enumerate(self.devices):
                if int(device["state"]) == 1:
                    try:
                        number, ip, name = device['number'], device["ip"], device["name"]
                        data = self.fetch_data(ip)
                        if data.status_code == 200:
                            data_json = data.json()
                            if data_json.get("status") == "Success":
                                power = data_json.get("data", {})
                                self.parse_port_data(number, power)
                            else:
                                raise ValueError(f"Error State Message ({data_json.get('status')})")
                        else:
                            raise ValueError(f"HTTP Error: {data.status_code}")
                    except Exception as e:
                        self.handle_error(device['number'])
        
        else:
            for i, device in enumerate(self.devices):
                self.handle_error(device['number'])
        
        if self.success_message:
            summary = f"{len(self.success_message)} of {len(self.sensorList)} Sensors Success Sampling"
        else:
                summary = f"{len(self.success_message)} of {len(self.sensorList)} Sensors Failed Sampling"
            
        if self.error_messages:
            summary += F" - {len(self.error_messages)} Port Error Device Offline ({self.error_messages})"
        
        self.sensor_message = summary

        sensor_result = {
            "value": self.sensorValue,
            "message": self.sensor_message,
            "state": self.sensorState,
            }
        return sensor_result


class RemoteIRExt:
    def __init__(self, groupId, dataSensor):
        self.dataSensor = dataSensor
        self.groupId = groupId
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(self.dataSensor)

    def handle(self, value):
        if value == None:
            value = 0.00
        else:
            value = round(value, 2)
        return value

    def main(self):
        ip = self.parameterGroupSensor['ipExt']
        api = self.parameterGroupSensor['endpoint']
        urlApi = "http://" + ip + api

        if self.dataSensor['numSensor'] > 0:
            sensorCount = self.dataSensor['numSensor']
            if self.parameterGroupSensor['deviceExt'] == 'on' :
                try:
                    get = requests.get(url=urlApi, timeout=10)
                    code = get.status_code
                    if code == 200:
                        data_json = get.json()
                        dataSensor = data_json['data']
                        
                        stateRemoteAC1 = dataSensor['ac1']
                        stateRemoteAC2 = dataSensor['ac2']
                        stateRemoteAC3 = dataSensor['ac3']
                        stateRemoteAC4 = dataSensor['ac4']

                        stateRemoteAC1 = self.handle(stateRemoteAC1)
                        stateRemoteAC2 = self.handle(stateRemoteAC2)
                        stateRemoteAC3 = self.handle(stateRemoteAC3)
                        stateRemoteAC4 = self.handle(stateRemoteAC4)
                        self.sensorValue = [stateRemoteAC1, stateRemoteAC2, stateRemoteAC3, stateRemoteAC4]
                        sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Success Sampling'
                    else:
                        self.sensorState = [False, False, False, False]
                        self.sensorValue = [-1, -1, -1, -1]
                        sensorMessage = str(self.dataSensor['numSensor']) + " Sensors Failed Sampling - Error Status Code " + str(code)
                except Exception as e:
                    self.sensorValue = [-1, -1, -1, -1]
                    sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Failed Sampling - ' + str(e)
                    self.sensorState = [False, False, False, False]
            else :
                self.sensorValue = [-1, -1, -1, -1]
                sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Success Sampling - State Device Extension Inactive'
        else :
            sensorMessage = 'No List Sensors Registered on Group Sensor ' + str(self.groupData[0]['name'])

        sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
        return sensorResult


class Network:
    def __init__(self, groupId, dataSensor, globalVariable):
        self.dataSensor = dataSensor
        print("Data Sensor:", self.dataSensor["sensorId"])
        self.groupId = groupId
        self.globalVariable = globalVariable
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(self.dataSensor)


    def handleErrorSNMP(self, oid_tipe):
        if oid_tipe == 0:
            value = 0
        else:
            value = 'N/A'
        return value


    def runPing(self, ipAddress, countPacket, timeout, sizePacket):
        try:
            resultPing = ping(target= ipAddress, count=int(countPacket), timeout=float(timeout), size=int(sizePacket))
            avgLat = resultPing.rtt_avg_ms
            state = True
            error = ''
        except Exception as e:
            avgLat = -1
            state = False
            error = str(e)
        result = {'value': avgLat, 'error': error, 'state': state}
        return result


    def readSNMP(self, ipAddress, community, port, oid_type, oid):
        try:
            value = puresnmp.get(ipAddress, community, oid, port=int(port))
            if isinstance(value, bytes):
                if '1.3.6.1.2.1.2.2.1.6' in oid:
                    value = '-'.join('{:02X}'.format(byte) for byte in value)
                else:
                    value = value.decode()
            state, error = True, ''
        except Exception as e:
            value = self.handleErrorSNMP(oid_type)
            state, error = False, str(e)
        result = {"value": value, "error": error, "state": state}
        return result


    def calculationSpeed(self, value, lastValue, diffTime):
        diffByte = int(value)-lastValue
        bps = round(diffByte*8,2)
        kbps = round(bps/diffTime/1000,2)
        mbps = round(kbps*0.0009765625,2)
        return mbps


    def main(self):
        if self.dataSensor['numSensor'] > 0 :
            try :
                numDevice = 1
                sensorTemporaryData = {}
                sensorTemporaryData[f"router{numDevice}"] = {}
                sensorTemporaryData[f"router{numDevice}"]['count'] = 0
                sensorCount = self.dataSensor['numSensor']
                for x in range(self.dataSensor['numSensor']):
                    sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]] = {}
                    if 'iface' in self.dataSensor['sensorId'][x].lower() or 'cpuload' in self.dataSensor['sensorId'][x].lower():
                        if 'latency' in self.dataSensor['sensorId'][x].lower() :
                            resultData = self.runPing(
                                self.parameterGroupSensor[f"ipRouter{numDevice}"], self.parameterListSensor[self.dataSensor['sensorId'][x]]['countPacket'],1,
                                self.parameterListSensor[self.dataSensor['sensorId'][x]]['sizePacket']
                            )
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'ping'
                        else :
                            resultData = self.readSNMP(
                                self.parameterGroupSensor[f"ipRouter{numDevice}"], self.parameterGroupSensor[f"comRouter{numDevice}"],
                                self.parameterGroupSensor[f"portRouter{numDevice}"], self.dataSensor['sensorDatatype'][x],
                                self.parameterListSensor[self.dataSensor['sensorId'][x]]['oid']
                            )

                            if 'spd' in self.dataSensor['sensorId'][x].lower():
                                nowTime = time.time()
                                diffTime = nowTime - self.globalVariable['lastTime'][self.dataSensor['sensorId'][x]]
                                sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp-calc-speed'
                                sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['diffTime'] = diffTime
                                sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['lastValue'] = self.globalVariable['lastValue'][self.dataSensor['sensorId'][x]]
                                self.globalVariable['lastValue'][self.dataSensor['sensorId'][x]] = resultData['value']
                                self.globalVariable['lastTime'][self.dataSensor['sensorId'][x]] = nowTime
                            else :
                                sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp'
                    elif 'space' in self.dataSensor['sensorId'][x].lower():
                        sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp-calc-subtract'
                        resultData = {'value': 0, 'state': 1}
                    else:
                        oid = re.sub(r'\d', '', self.dataSensor['sensorId'][x])
                        oid = f"oid{oid[0].upper()}{oid[1:]}"
                        resultData = self.readSNMP(
                            self.parameterGroupSensor[f"ipRouter{numDevice}"], self.parameterGroupSensor[f"comRouter{numDevice}"],
                            self.parameterGroupSensor[f"portRouter{numDevice}"], self.dataSensor['sensorDatatype'][x],
                            self.parameterGroupSensor[oid]
                        )
                        if 'uptime' in self.dataSensor['sensorId'][x].lower():
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp-uptime'
                        elif 'volt' in self.dataSensor['sensorId'][x].lower() or 'temp' in self.dataSensor['sensorId'][x].lower():
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp-calc-divided'
                        else:
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] = 'snmp'

                    sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['value'] = resultData['value']
                    sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['state'] = resultData['state']
                    sensorTemporaryData[f"router{numDevice}"]['count'] += resultData['state']

                for x in range(self.dataSensor['numSensor']):
                    if sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'snmp' or sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'ping':
                        if sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['state'] == False: sensorCount -= 1
                        self.sensorValue[x] = sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['value']
                    elif sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'snmp-uptime':
                        if sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['state'] == False: sensorCount -= 1
                        self.sensorValue[x] = str(sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['value'])
                    elif sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'snmp-calc-divided':
                        if sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['state'] == False: 
                            sensorCount -= 1
                            self.sensorValue[x] = 0
                        else:
                            self.sensorValue[x] = round(sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['value']/10,2)
                    elif sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'snmp-calc-speed':
                        self.sensorValue[x] = self.calculationSpeed(
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['value'],
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['lastValue'],
                            sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['diffTime']
                        )
                    elif sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][x]]['method'] == 'snmp-calc-subtract':
                        parameter = self.dataSensor['sensorId'][x].replace("Space", "")
                        parameterUsed, parameterTotal = 0, 0
                        for y in range(self.dataSensor['numSensor']):
                            if self.dataSensor['sensorId'][y] == f"{parameter}Used":
                                parameterUsed = y
                            if self.dataSensor['sensorId'][y] == f"{parameter}Total":
                                parameterTotal = y
                        self.sensorValue[x] = sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][parameterTotal]]['value'] - sensorTemporaryData[f"router{numDevice}"][self.dataSensor['sensorId'][parameterUsed]]['value']
                if sensorCount == self.dataSensor['numSensor']:
                    sensorMessage = str(sensorCount) + ' Sensors Success Sampling'
                else:    
                    sensorMessage = f"{str(sensorCount)} Sensors Success Sampling | {str(self.dataSensor['numSensor'] - sensorCount)} Sensors Failed Sampling"
            except Exception as e:
                sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Failed Sampling - ' + str(e)
        else:
            sensorMessage = 'No List Sensors Registered on Group Sensor ' + str(self.groupData[0]['name'])
        print("Sensor Value:",self.sensorValue)
        sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
        return sensorResult, self.globalVariable


class SensorNetwork():
    def handleErrorSNMP(oid_tipe):
        if oid_tipe == 0:
            value = '0'
        else:
            value = 'N/A'
        return value


    def runPing(ipAddress, countPacket, timeoutPing, sizePacket):
        try:
            resultPing = ping(target= ipAddress, count=int(countPacket), timeout=float(timeoutPing), size=int(sizePacket))
            avgLat = resultPing.rtt_avg_ms
            state = True
            error = ''
        except Exception as e:
            avgLat = -1
            state = False
            error = str(e)
        result = {'value': avgLat, 'error': error, 'state': state}
        return result


    def readSNMP(ip, community, port, oid_tipe, oid):
        try:
            value = puresnmp.get(ip, community, oid, port=int(port))
            if isinstance(value, bytes):
                value = value.decode()
            state, error = 1, ''
        except Exception as e:
            value = SensorNetwork.handleErrorSNMP(oid_tipe)
            state, error = 0, str(e)
        result = {"value": value, "error": error, "state": state}
        return result


    def calculationSpeed(value, lastValue, diffTime):
        diffByte = int(value)-lastValue
        bps = round(diffByte*8,2)
        kbps = round(bps/diffTime/1000,2)
        mbps = round(kbps*0.0009765625,2)
        return mbps


    def main(groupId, dataSensor, globalVariable):
        groupData = SensorGroupDB.selectOne(groupId)
        sensorValue = handleSensorValue(dataSensor)
        parameterGroup = CollectDataSensorFunction.getParameterGroupSensor(groupId)
        parameterListSensor = CollectDataSensorFunction.getParameterListSensor(groupId)

        if dataSensor['numSensor'] > 0:
            numDevice = 1
            sensorTemporaryData = {}
            sensorTemporaryData[f"router{numDevice}"] = {}
            sensorTemporaryData[f"router{numDevice}"]['count'] = 0

            for x in range(dataSensor['numSensor']):
                sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]] = {}
                if 'iface' in dataSensor['sensorId'][x].lower() or 'cpuload' in dataSensor['sensorId'][x].lower():
                    if 'latency' in dataSensor['sensorId'][x].lower():
                        resultData = SensorNetwork.runPing(parameterGroup[f"ipRouter{numDevice}"], parameterListSensor[dataSensor['sensorId'][x]]['countPacket'],
                                                        1, parameterListSensor[dataSensor['sensorId'][x]]['sizePacket'])
                        sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'ping'
                    else:
                        resultData = SensorNetwork.readSNMP(parameterGroup[f"ipRouter{numDevice}"], parameterGroup[f"comRouter{numDevice}"], parameterGroup[f"portRouter{numDevice}"],
                                                    dataSensor['sensorDatatype'][x], parameterListSensor[dataSensor['sensorId'][x]]['oid'])
                        if 'spd' in dataSensor['sensorId'][x].lower():
                            nowTime = time.time()
                            diffTime = nowTime - globalVariable['lastTime'][dataSensor['sensorId'][x]]
                            sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp-calc-speed'
                            sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['diffTime'] = diffTime
                            sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['lastValue'] = globalVariable['lastValue'][dataSensor['sensorId'][x]]
                            globalVariable['lastValue'][dataSensor['sensorId'][x]] = resultData['value']
                            globalVariable['lastTime'][dataSensor['sensorId'][x]] = nowTime
                        else:
                            sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp'
                elif 'space' in dataSensor['sensorId'][x].lower():
                    sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp-calc-subtract'
                    resultData = {'value': 0, 'state': 1}
                else:
                    oid = re.sub(r'\d', '', dataSensor['sensorId'][x])
                    oid = f"oid{oid[0].upper()}{oid[1:]}"
                    resultData = SensorNetwork.readSNMP(parameterGroup[f"ipRouter{numDevice}"], parameterGroup[f"comRouter{numDevice}"], parameterGroup[f"portRouter{numDevice}"],
                                                        dataSensor['sensorDatatype'][x], parameterGroup[oid])
                    if 'uptime' in dataSensor['sensorId'][x].lower():
                        sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp-uptime'
                    elif 'volt' in dataSensor['sensorId'][x].lower() or 'temp' in dataSensor['sensorId'][x].lower():
                        sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp-calc-divided'
                    else:
                        sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] = 'snmp'
                sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['value'] = resultData['value']
                sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['state'] = resultData['state']
                sensorTemporaryData[f"router{numDevice}"]['count'] += resultData['state']
            for x in range(dataSensor['numSensor']):
                if sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'snmp' or sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'ping':
                    sensorValue[x] = sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['value']
                elif sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'snmp-uptime':
                    sensorValue[x] = str(sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['value'])
                elif sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'snmp-calc-divided':
                    sensorValue[x] = round(sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['value']/10,2)
                elif sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'snmp-calc-speed':
                    sensorValue[x] = SensorNetwork.calculationSpeed(sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['value'], sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['lastValue'],
                                                                    sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['diffTime'])
                elif sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][x]]['method'] == 'snmp-calc-subtract':
                    parameter = dataSensor['sensorId'][x].replace("Space", "")
                    parameterUsed, parameterTotal = 0, 0
                    for y in range(dataSensor['numSensor']):
                        if dataSensor['sensorId'][y] == f"{parameter}Used":
                            parameterUsed = y
                        if dataSensor['sensorId'][y] == f"{parameter}Total":
                            parameterTotal = y
                    sensorValue[x] = sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][parameterTotal]]['value'] - sensorTemporaryData[f"router{numDevice}"][dataSensor['sensorId'][parameterUsed]]['value']
            status = str(dataSensor['numSensor']) + ' Sensors Success Sampling'
        else:
            status = 'No List Sensors Registered on Group Sensor ' + str(groupData[0][1])
        return sensorValue, status, globalVariable


class InternalSensor:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(dataSensor)
        self.url = "http://localhost/api/get/info"
        adcInputConnexVoltage = 0


    def main(self):
        if self.dataSensor['numSensor'] > 0:
            sensorCount = self.dataSensor['numSensor']
            try:
                serviceState = ServiceProjectFunction.checkActiveService("sensor2")
                
                if serviceState == 'active':
                    neuronVoltID = "PLS-B1D00"
                    value = SensorListDB.selectValue(neuronVoltID)
                    if len(value[0]['value']) > 0:
                        tegangan = value[0]['value']
                    else:
                        tegangan = 0.00
                    
                    if tegangan == None:
                        tegangan = 0.00
                    else:
                        tegangan = float(tegangan)
                    
                    
                else:
                    pinClk = 21
                    pinMiso = 19
                    pinMosi = 20
                    pinCs = 18
                    mcp3008 = MCP3008(
                        channel=int(self.parameterListSensor['nearonVolt']['pin']), clock_pin=pinClk, mosi_pin=pinMosi, miso_pin=pinMiso, select_pin=pinCs
                    )
                    adcInputConnexVoltage = mcp3008.voltage
                    tegangan = round((adcInputConnexVoltage)*float(self.parameterListSensor['nearonVolt']['offset']),2)
                    
                connexVolt = tegangan
                getData = requests.get(url=self.url, timeout=10)
                jsonData = getData.json()
                connexFan = jsonData['fan']
                connexCpuUsage = jsonData['cpu'].replace(' %','')
                connexCpuTemp = jsonData['temp']
                mem = psutil.virtual_memory()
                mem_total = round(float(mem.total/(2**20)))
                mem_used = round(float(mem.used/(2**20)))
                connexMemUsage = round(float(mem_used/mem_total * 100))
                hdd = psutil.disk_usage('/')
                hdd_total = round(float(hdd.total/(2**30)))
                hdd_used = round(float(hdd.used/(2**30)),1)
                connexStorageUsage = round(float(hdd_used/hdd_total * 100))
                connexUptime = jsonData['uptime']
                connexLastBoot = jsonData['last']
                self.sensorValue = [connexVolt, connexFan, connexCpuUsage, connexCpuTemp, connexMemUsage, connexStorageUsage, connexUptime, connexLastBoot]
                sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Success Sampling'

            except Exception as e:
                sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Failed Sampling - ' + str(e)
                self.sensorState = [False, False, False, False, False, False, False, False]
        else:
            sensorMessage = 'No List Sensors Registered on Group Sensor ' + str(self.groupData[0]['name'])
        sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
        return sensorResult


class Room:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(dataSensor)
        self.url = f"http://{self.parameterGroupSensor['ip']}/measures/current"


    def main(self):
        if self.dataSensor['numSensor'] > 0:
            try:
                responseData = requests.get(self.url, timeout=5)
                if responseData.status_code == 200:
                    airGradientData = responseData.json()
                    pm1 = airGradientData["pm01"]
                    pm2_5 = airGradientData["pm02"]
                    pm10 = airGradientData["pm10"]
                    temperature = airGradientData["atmp"]
                    humidity = airGradientData["rhum"]
                    co2 = airGradientData["rco2"]
                    tvoc = airGradientData["tvocIndex"]
                    nox = airGradientData["noxIndex"]
                    self.sensorState = [True, True, True, True, True, True, True, True]
                    sensorMessage = f"{self.dataSensor['numSensor']} Sensors Success Sampling"
                else:
                    pm1, pm2_5, pm10, temperature, humidity, co2, tvoc, nox = 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0, 0
                    self.sensorState = [False, False, False, False, False, False, False, False]
                    sensorMessage = f"{self.dataSensor['numSensor']} Sensors Failed Sampling - Status Code {responseData.status_code}"
                self.sensorValue = [pm1, pm2_5, pm10, temperature, humidity, co2, tvoc, nox]

            except Exception as e:
                sensorMessage = str(self.dataSensor['numSensor']) + ' Sensors Failed Sampling - ' + str(e)
                self.sensorState = [False, False, False, False, False, False, False, False]
        else:
            sensorMessage = 'No List Sensors Registered on Group Sensor ' + str(self.groupData[0]['name'])
        sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
        return sensorResult


class SensorRTU:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(dataSensor)
        
        # Handle port parameter with direct validation
        port_param = self.parameterGroupSensor.get("port", "")
        print("Parameter Group Sensor:", self.parameterGroupSensor)
        print("Port parameter:", port_param)
        
        # Check if port exists directly
        if port_param and port_param != "":
            # Try to use the port directly if it's a valid ttyUSB/ttyACM device
            if "ttyUSB" in port_param or "ttyACM" in port_param:
                self.port = "/dev/" + port_param
                print("Using port directly:", self.port)
            else:
                # Fallback to checkUSBDevice function
                usb_result = generalFunction.checkUSBDevice(str(port_param))
                self.port = usb_result[1]
                print("Port after checkUSBDevice:", self.port)
                if self.port != "N/A":
                    self.port = "/dev/" + self.port
        else:
            self.port = "N/A"
            print("Port parameter is empty or not found")
        
        # Handle baudrate parameter
        self.baudrate = int(self.parameterGroupSensor.get('baudrate', 9600))

    def main(self):
        if self.dataSensor['numSensor'] > 0:
            if self.port != "N/A": 
                try:
                    rtu_object = ModbusClient(method="rtu", port=self.port, baudrate=self.baudrate, parity='N', stopbits=1, bytesize=8)
                except Exception as e:
                    rtu_object = None
                if rtu_object != None:
                    sensor_count = 0
                    for x in range(self.dataSensor['numSensor']):
                        try:
                            sensor_id = self.dataSensor["sensorId"][x]
                            rtu_number = sensor_id[sensor_id.lower().find("rtu") + 3:]
                            slave_id = int(RtuDeviceDB.selectByNumber(rtu_number)[0]["slave_id"])
                            address = int(self.parameterListSensor[sensor_id]["address"])
                            count = int(self.parameterListSensor[sensor_id]["length"])
                            divider = float(self.parameterListSensor[sensor_id]["divider"])
                            # Handle different register formats
                            if address >= 40000:
                                # Holding registers (4xxxx) - format like 40005
                                address = address - 40001
                                read = rtu_object.read_holding_registers(address=address, count=count, unit=slave_id)
                                type = "value"
                            elif address >= 30000 and address < 40000:
                                # Input registers (3xxxx)
                                address = address - 30001
                                read = rtu_object.read_input_registers(address=address, count=count, unit=slave_id)
                                type = "value"
                            elif address >= 10000 and address < 20000:
                                # Coils (0xxxx)
                                address = address - 10001
                                read = rtu_object.read_coils(address=address, count=count, unit=slave_id)
                                type = "state"
                            elif address > 0 and address < 10000:
                                # Discrete inputs (1xxxx)
                                address = address - 1
                                read = rtu_object.read_discrete_inputs(address=address, count=count, unit=slave_id)
                                type = "state"
                            else:
                                # Default to holding registers for any other address
                                read = rtu_object.read_holding_registers(address=address, count=count, unit=slave_id)
                                type = "value"
                            if read.isError() == False:
                                if type == "state" : value = read.bits[0]
                                else: 
                                    if "offtime" in sensor_id.lower() or "runtime" in sensor_id.lower(): 
                                        value = (read.registers[0] * 65535) + read.registers[1]
                                        jam = value // 3600
                                        menit = (value % 3600) // 60
                                        detik = value % 60
                                        value = f"{jam:02}:{menit:02}:{detik:02}"
                                    else: 
                                        value = read.registers[0] / divider
                                        value = round(value)  # Keep as float with 2 decimal places
                                state = True
                                sensor_count += 1
                            else:
                                value = 0  # Use float for consistency
                                state = False
                            self.sensorValue[x] = value
                            self.sensorState[x] = state
                        except Exception as e:
                            self.sensorValue[x] = 0  # Use float for consistency
                            self.sensorState[x] = False
                    
                    if sensor_count == 0: sensorMessage = f"{sensor_count} Sensors Failed Sampling"
                    elif sensor_count == self.dataSensor['numSensor']: sensorMessage = f"{sensor_count} Sensors Success Sampling"
                    else: sensorMessage = f"{sensor_count} of {str(self.dataSensor['numSensor'])} Sensors Success Sampling"
                    
                else:
                    sensorMessage = f"{str(self.dataSensor['numSensor'])} Sensors Failed Sampling - RTU Device Not Found"
                                   
            else:
                sensorMessage = f"{str(self.dataSensor['numSensor'])} Sensors Failed Sampling - Port N/A"
                
        else:
            sensorMessage = f"No List Sensors Registered on Group Sensor {str(self.groupData[0]['name'])}"
        sensorResult = {"value": self.sensorValue, "message": sensorMessage, "state": self.sensorState}
        return sensorResult
        
        

class Weather:
    def __init__(self, groupId, dataSensor):
        self.groupId = groupId
        self.dataSensor = dataSensor
        self.groupData = SensorGroupDB.selectOne(self.groupId)
        self.parameterGroupSensor = CollectDataSensorFunction.getParameterGroupSensor(self.groupId)
        self.parameterListSensor = CollectDataSensorFunction.getParameterListSensor(self.groupId)
        self.sensorValue, self.sensorState = handleSensorValue(self.dataSensor)
        
        # Konfigurasi default untuk weather station
        self.port = self.parameterGroupSensor.get('port', '/dev/ttyUSB0')
        self.baudrate = int(self.parameterGroupSensor.get('baudrate', 4800))
        self.slaveId = int(self.parameterGroupSensor.get('slaveId', 2))
        
        # Register addresses untuk weather station
        self.windSpeed = 0x1F4
        self.windStrength = 0x1F5
        self.windDirection1 = 0x1F6
        self.windDirection2 = 0x1F7
        self.humidity = 0x1F8
        self.temperature = 0x1F9
        self.pm25 = 0x1FB
        self.pm10 = 0x1FC
        self.atmosphericPressure = 0x1FD
        self.illuminanceLow = 0x1FE
        self.illuminanceHigh = 0x1FF
        self.illuminance = 0x200
        self.rainfall = 0x201
        
        # Inisialisasi koneksi Modbus
        self.weatherObject = None
        self.connect()
        
        # Ambil daftar sensor untuk group ini
        self.sensor_list = SensorListDB.selectByGroupFull(self.groupId)
        self.sensor_id_map = {sensor['sensor_id']: sensor['id'] for sensor in self.sensor_list}

    def connect(self):
        """Fungsi untuk membuat koneksi ke weather station"""
        try:
            self.weatherObject = ModbusClient(method="rtu", port=self.port, baudrate=self.baudrate, timeout=2, retries=3)
            self.weatherObject.connect()
            return True
        except Exception as e:
            print(f"Error koneksi ke weather station: {e}")
            return False

    def _fallback_to_last_data(self):
        """Fungsi fallback ketika weather station tidak bisa diakses sama sekali"""
        print("Menggunakan fallback: mengambil semua data terakhir yang valid dari database")
        results = []
        state = []
        success_count = 0
        failed_count = 0
        error_messages = []
        
        for sensor_id in self.dataSensor["sensorId"]:
            last_valid_value, has_last_data = self.get_last_valid_data(sensor_id, max_age_hours=48)  # Lebih longgar untuk fallback
            if has_last_data:
                results.append(last_valid_value)
                state.append(False)  # State False karena menggunakan data lama
                success_count += 1
                error_messages.append(f"{sensor_id} - Using last valid data: {last_valid_value}")
            else:
                results.append(0.00)
                state.append(False)
                failed_count += 1
                error_messages.append(f"{sensor_id} - No valid data available")
        
        self.sensorValue = results
        self.sensorState = state
        
        if failed_count == 0:
            sensorMessage = f"{success_count} Sensors Success Sampling (Fallback Mode - Using Last Valid Data)"
        else:
            error_details = ", ".join(error_messages)
            sensorMessage = f"{success_count} Sensors Success Sampling (Fallback Mode) | {failed_count} Sensors Failed - {error_details}"
        
        # Fallback mode tidak bisa update ke log monitoring karena menggunakan data lama
        sensorResult = {
            "value": self.sensorValue, 
            "message": sensorMessage, 
            "state": self.sensorState,
            "can_update_log": False  # Fallback mode tidak bisa update log
        }
        return sensorResult

    def get_last_valid_data(self, sensor_id, max_age_hours=24):
        """Fungsi untuk mengambil data terakhir yang valid dari database log monitoring"""
        try:
            if sensor_id in self.sensor_id_map:
                sensor_db_id = self.sensor_id_map[sensor_id]
                # Ambil data terakhir dari log monitoring (tipe 9 = routine monitoring)
                last_data = LogSensorDB.selectLastOne(sensor_db_id)
                if last_data and len(last_data) > 0:
                    last_value = float(last_data[0]['data'])
                    last_timestamp = last_data[0]['timestamp']
                    
                    # Cek apakah data masih fresh (dalam 24 jam terakhir)
                    from datetime import datetime, timedelta
                    try:
                        last_time = datetime.strptime(last_timestamp, '%Y-%m-%d %H:%M:%S')
                        current_time = datetime.now()
                        age_hours = (current_time - last_time).total_seconds() / 3600
                        
                        if age_hours <= max_age_hours:
                            print(f"Data terakhir untuk {sensor_id}: {last_value} (timestamp: {last_timestamp}, umur: {age_hours:.1f} jam)")
                            return last_value, True
                        else:
                            print(f"Data untuk {sensor_id} terlalu lama: {age_hours:.1f} jam (max: {max_age_hours} jam)")
                            return 0.00, False
                    except Exception as time_error:
                        print(f"Error parsing timestamp untuk {sensor_id}: {time_error}")
                        # Jika ada error parsing timestamp, gunakan data anyway
                        return last_value, True
                else:
                    print(f"Tidak ada data terakhir untuk {sensor_id}")
                    return 0.00, False
            else:
                print(f"Sensor {sensor_id} tidak ditemukan dalam mapping database")
                return 0.00, False
        except Exception as e:
            print(f"Error mengambil data terakhir untuk {sensor_id}: {e}")
            return 0.00, False

    def read_register_safe(self, address, multiplier=1, unit=None, description=""):
        """Fungsi aman untuk membaca register dengan error handling"""
        if unit is None:
            unit = self.slaveId
            
        try:
            if self.weatherObject and self.weatherObject.is_socket_open():
                response = self.weatherObject.read_holding_registers(address=address, count=1, unit=unit)
                if hasattr(response, 'registers') and response.registers:
                    value = response.registers[0] * multiplier
                    return value, True
                else:
                    print(f"Error membaca {description}: Response tidak valid")
                    return 0, False
            else:
                print(f"Error membaca {description}: Koneksi tidak tersedia")
                return 0, False
        except Exception as e:
            print(f"Error membaca {description}: {e}")
            return 0, False

    def main(self):
        """Fungsi utama untuk membaca semua sensor weather"""
        if self.dataSensor['numSensor'] > 0:
            # Cek status koneksi terlebih dahulu
            if not self.weatherObject or not self.weatherObject.is_socket_open():
                print("Warning: Weather station tidak terhubung, mencoba reconnect...")
                if not self.connect():
                    print("Error: Gagal reconnect ke weather station")
                    # Jika tidak bisa connect sama sekali, gunakan semua data terakhir yang valid
                    return self._fallback_to_last_data()
            
            results = []
            state = []
            success_count = 0
            failed_count = 0
            error_messages = []
            all_sensors_success = True  # Flag untuk mengecek apakah semua sensor berhasil

            # Mapping sensor ID ke register dan multiplier
            sensor_mapping = {
                "windSpeed": (self.windSpeed, 0.01, "Wind Speed"),
                "windStrength": (self.windStrength, 1, "Wind Strength"),
                "windDirection1": (self.windDirection1, 1, "Wind Direction (0-7)"),
                "windDirection2": (self.windDirection2, 1, "Wind Direction (0-360)"),
                "humidity": (self.humidity, 0.1, "Humidity"),
                "temperature": (self.temperature, 0.1, "Temperature"),
                "pm25": (self.pm25, 1, "PM2.5"),
                "pm10": (self.pm10, 1, "PM1.0"),
                "atmosphericPressure": (self.atmosphericPressure, 0.1, "Atmospheric Pressure"),
                "illuminance": (self.illuminance, 100, "Illuminance"),
                "rainfall": (self.rainfall, 0.1, "Rainfall")
            }

            # Baca setiap sensor yang terdaftar
            for sensor_id in self.dataSensor["sensorId"]:
                if sensor_id in sensor_mapping:
                    address, multiplier, description = sensor_mapping[sensor_id]
                    value, success = self.read_register_safe(address, multiplier, description=description)
                    
                    if success:
                        # Format nilai sesuai dengan tipe sensor
                        if "windSpeed" in sensor_id:
                            value = round(value, 2)
                        elif "humidity" in sensor_id or "temperature" in sensor_id:
                            value = round(value, 2)
                        elif "atmosphericPressure" in sensor_id:
                            value = round(value, 2)
                        elif "rainfall" in sensor_id:
                            value = round(value, 2)
                        
                        results.append(value)
                        state.append(True)
                        success_count += 1
                    else:
                        # Jika sensor gagal terbaca, ambil data terakhir yang valid dari database
                        last_valid_value, has_last_data = self.get_last_valid_data(sensor_id, max_age_hours=24)
                        if has_last_data:
                            results.append(last_valid_value)
                            state.append(False)  # State tetap False karena menggunakan data lama
                            failed_count += 1
                            all_sensors_success = False  # Set flag ke False
                            error_messages.append(f"{description} Error - Using last valid data: {last_valid_value}")
                        else:
                            results.append(0.00)
                            state.append(False)
                            failed_count += 1
                            all_sensors_success = False  # Set flag ke False
                            error_messages.append(f"{description} Error - No valid data available")
                else:
                    # Sensor tidak dikenal
                    results.append(0.00)
                    state.append(False)
                    failed_count += 1
                    all_sensors_success = False  # Set flag ke False
                    error_messages.append(f"Unknown sensor: {sensor_id}")

            self.sensorValue = results
            self.sensorState = state

            # Buat pesan status
            if failed_count == 0:
                sensorMessage = f"{success_count} Sensors Success Sampling"
            else:
                error_details = ", ".join(error_messages)
                if failed_count == self.dataSensor['numSensor']:
                    sensorMessage = f"{failed_count} Sensors Failed Sampling ({error_details})"
                else:
                    sensorMessage = f"{self.dataSensor['numSensor']-failed_count} of {self.dataSensor['numSensor']} Sensors Success Sampling | {error_details}"

            # Tambahkan informasi kesehatan data
            data_health_info = self._check_data_health()
            if data_health_info:
                sensorMessage += f" | {data_health_info}"
            
            # Tambahkan flag untuk menandai apakah data bisa diupdate ke log monitoring
            sensorResult = {
                "value": self.sensorValue, 
                "message": sensorMessage, 
                "state": self.sensorState,
                "can_update_log": all_sensors_success  # Flag baru untuk menentukan apakah bisa update log
            }
            return sensorResult
        else:
            self.sensorState = []
            self.sensorValue = []
            sensorMessage = f"No List Sensors Registered on Group Sensor {str(self.groupData[0]['name'])}"
            sensorResult = {
                "value": self.sensorValue, 
                "message": sensorMessage, 
                "state": self.sensorState,
                "can_update_log": False  # Tidak ada sensor, tidak bisa update log
            }
            return sensorResult

    def _check_data_health(self):
        """Fungsi untuk mengecek kesehatan data dan memberikan rekomendasi"""
        try:
            stale_data_count = 0
            total_sensors = len(self.dataSensor["sensorId"])
            
            for i, sensor_id in enumerate(self.dataSensor["sensorId"]):
                if self.sensorState[i] == False:  # Jika menggunakan data lama
                    # Cek umur data
                    last_valid_value, has_last_data = self.get_last_valid_data(sensor_id, max_age_hours=24)
                    if has_last_data:
                        # Data ada tapi sudah lama
                        stale_data_count += 1
            
            if stale_data_count > 0:
                if stale_data_count == total_sensors:
                    return f"WARNING: Semua sensor menggunakan data lama (lebih dari 24 jam)"
                elif stale_data_count > total_sensors // 2:
                    return f"WARNING: {stale_data_count}/{total_sensors} sensor menggunakan data lama"
                else:
                    return f"INFO: {stale_data_count}/{total_sensors} sensor menggunakan data lama"
            
            return ""
        except Exception as e:
            print(f"Error dalam pengecekan kesehatan data: {e}")
            return ""

    def __del__(self):
        """Cleanup saat object dihapus"""
        if self.weatherObject:
            try:
                self.weatherObject.close()
            except:
                pass
        
        
