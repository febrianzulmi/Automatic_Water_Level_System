
from math import sqrt
import re
import sys
import time

from gpiozero import MCP3008
import minimalmodbus
import psutil
import puresnmp
from pythonping import ping
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import requests
import RPi.GPIO as GPIO
import serial

sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SensorGroupDB, EnvironmentDeviceDB, PowerDeviceDB,  SensorPortConfigDB, RtuDeviceDB
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


    def main(self):
        self.groupData = SensorGroupDB.selectOne(self.groupId)

        if self.dataSensor['numSensor'] > 0:
            self.handler_mapping = {
                "1": Environment.SensorHandler.readSHT20,
                "2": Environment.SensorHandler.readSmoke,
                "3": Environment.SensorHandler.readDoor,
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
        self.port = generalFunction.checkUSBDevice(str(self.parameterGroupSensor["port"]))
        self.port = self.port[1]
        if self.port != "N/A":
            self.port = "/dev/" + self.port
        print(f'Port : {self.port}')
        self.baudrate = int(self.parameterGroupSensor['baudrate'])

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
                            divider = int(self.parameterListSensor[sensor_id]["divider"])
                            if address > 0 and address < 20000:
                                if address > 10000: address = address - 10001
                                else: address = address - 1
                                read = rtu_object.read_discrete_inputs(address=address, count=count, unit=slave_id)
                                type = "state"
                            else:
                                if address > 30000 and address < 40000: address = address - 30001
                                elif address > 40000: address = address - 40001
                                read = rtu_object.read_input_registers(address=address, count=count, unit=slave_id)
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
                                    else: value = int(read.registers[0]) / int(divider)
                                state = True
                                sensor_count += 1
                            else:
                                value = 0
                                state = False
                            self.sensorValue[x] = value
                            self.sensorState[x] = state
                        except Exception as e:
                            self.sensorValue[x] = 0
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
        
        