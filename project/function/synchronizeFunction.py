path = "/home/connex"

import datetime
import json
import os
import sys

sys.path.append(f"{path}/library")
from SynapsisLibrary import times, mqtt
sys.path.append(f"{path}/project/database")
from query_project_db import SensorListDB, ActuatorListDB, ActuatorScheduleDB, SystemServiceDB, DeviceSettingDB
sys.path.append(f"{path}/project/function/sensor")
from collectDataSensorFunction import CollectDataSensorFunction
sys.path.append(f"{path}/project/function")
from generalFunction import generalFunction
from httpProtocolFunction import httpProtocolFunction
from mqttProtocolFunction import mqttProtocolFunction
from serverFunction import serverFunction


class synchronizeFunction():
    def runSync(device_setting, feature_setting, server_config, global_variable):
        project_data = generalFunction.getProjectSetting()
        protocol_monitoring = project_data["protocol"] # 1: HTTP, 2: MQTT, 3: SNMP
        timestamp = times.getDatetime()
        thread_sync = []
        global_variable["log"] = []
        
        if str(protocol_monitoring) == "1":
            if str(feature_setting["syncNode"]) == "1":
                try:
                    thread_sync_node = generalFunction.ThreadWithReturnValues(target=synchronizeFunction.syncNodeHttp, 
                                                                              args=(device_setting, server_config["http"], timestamp, global_variable))
                    thread_sync_node.start()
                    thread_sync.append(thread_sync_node)
            
                    if global_variable["flagRebootSync"] == 0:
                        threadSyncNodeReboot = generalFunction.ThreadWithReturnValues(target=synchronizeFunction.syncNodeRebootHttp, 
                                                                                      args=(server_config["http"], timestamp, global_variable))
                        threadSyncNodeReboot.start()
                        thread_sync.append(threadSyncNodeReboot)
                
                except Exception as e:
                    log_service = f"Error Synchronize Node Detail - {e}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    global_variable["log"].append(log_service)

            else:
                log_service = "Feature Synchronize Node Option Setting Inactive"
                color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                global_variable["logger"].debug(f"{color_log_service}\n")
                global_variable["log"].append(log_service)
        
            if str(feature_setting["syncSensor"]) == "1":
                try:
                    thread_sync_sensor = generalFunction.ThreadWithReturnValues(target=synchronizeFunction.syncSensorHttp, 
                                                                                args=(server_config["http"], timestamp, global_variable))
                    thread_sync_sensor.start()
                    thread_sync.append(thread_sync_sensor)
                
                except Exception as e:
                    log_service = f"Error Synchronize Sensor Detail - {e}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    global_variable["log"].append(log_service)
        
            else:
                log_service = "Feature Synchronize Sensor Option Setting Inactive"
                color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                global_variable["logger"].debug(f"{color_log_service}\n")
                global_variable["log"].append(log_service)
        
            if str(feature_setting["syncActuator"]) == "1":
                try:
                    thread_sync_actuator = generalFunction.ThreadWithReturnValues(target=synchronizeFunction.syncActuatorHttp, 
                                                                                  args=(server_config["http"], timestamp, global_variable))
                    thread_sync_actuator.start()
                    thread_sync.append(thread_sync_actuator) 
                
                except Exception as e:
                    log_service = f"Error Synchronize Actuator Detail - {e}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    global_variable["log"].append(log_service)
        
            else:
                log_service = "Feature Synchronize Actuator Option Setting Inactive"
                color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                global_variable["logger"].debug(f"{color_log_service}\n")
                global_variable["log"].append(log_service)
        
        elif str(protocol_monitoring) == "2":
            if global_variable["updateReboot"] == 0:
                pass
        
            for x in global_variable["topicSubscriptionState"]:
                parameter = x.capitalize()
                topic_name = f"{parameter} Detail"
                run_subscribe, result_mqtt, log_service = 0, {}, ""
            
                if global_variable["topicSubscriptionState"][x]["state"] == 0:
                    if str(global_variable["topicSubscriptionState"][x]["setting"]) == "1":
                        result_mqtt = mqttProtocolFunction.runSubscription("Subscribe", server_config["mqtt"], global_variable["topicSubscriptionState"][x]["topic"], global_variable)
                        if result_mqtt["state"] == "Success": 
                            global_variable["topicSubscriptionState"][x]["state"] = 1 
                        run_subscribe = 1 # --> State Action for Subscribe Topic
            
                    else:
                        run_subscribe = 2 # --> State Action for Synchronize Inactive
            
                else:
                    if global_variable["mqttConnection"] == False or global_variable["mqttConnection"] == None:
                        result_mqtt = mqttProtocolFunction.runSubscription("Subscribe", server_config["mqtt"], global_variable["topicSubscriptionState"][x]["topic"], global_variable)
                        if result_mqtt["state"] == "Success":
                            global_variable["topicSubscriptionState"][x]["state"] = 1 
                        run_subscribe = 1 # --> State Action for Subscribe Topic
            
                    else:
                        if str(global_variable["topicSubscriptionState"][x]["setting"]) == "0":
                            run_subscribe = 3 # --> State Action for Unsubscribe
                            result_mqtt = mqttProtocolFunction.runSubscription("Unsubscribe", server_config["mqtt"], global_variable["topicSubscriptionState"][x]["topic"], global_variable)
                            if result_mqtt["state"] == "Success":
                                global_variable["topicSubscriptionState"][x]["state"] = 0 
            
                        else:
                            pass
            
                if run_subscribe == 1:
                    log_service = f"{result_mqtt['state']} Subscribe Topic {topic_name}"
                    color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
                    global_variable["log"].append(log_service)
            
                elif run_subscribe == 2:
                    log_service = f"Feature Synchronize {topic_name} Setting Inactive"
                    color_log_service = f"\033[93m{log_service} at {timestamp}\033[00m"
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
                    global_variable["log"].append(log_service)
            
                elif run_subscribe == 3:
                    log_service = f"{result_mqtt['state']} Unsubscribe Topic {topic_name}"
                    color_log_service = "\033[93m{} at {}\033[00m".format(log_service, timestamp)
                    global_variable["logger"].debug(f"{color_log_service}\n")
                    # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
                    global_variable["log"].append(log_service)
            
            synchronizeFunction.runCheckReceiveMessageMQTT(device_setting, server_config["mqtt"], global_variable)
        
        else:
            log_service = "Protocol Synchronize Setting N/A"
            color_log_service = f"\033[93m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
            
        for num in range(len(thread_sync)) :
            thread_sync[num].join()  
        
        log_service = " | ".join(global_variable["log"])
        SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])


    def syncNodeHttp(device_data, server_config, timestamp, global_variable):
        result_http = httpProtocolFunction.runGetMethod(server_config, "node")
        
        if result_http["state"] == "Success":
            synchronizeFunction.syncNodeData(device_data, result_http["payload"], timestamp, global_variable)
        
        else:
            log_service = f"{result_http['state']} Sync Node ({device_data['uid']}) Data - Status Code {result_http['state_code']} ({result_http['log']})"     
            color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
    
    
    def syncNodeRebootHttp(server_config, timestamp, global_variable):
        data_pack = {"reboot_status": 0}
        result_http = httpProtocolFunction.runPutMethod(server_config, "reboot", data_pack)
        
        if result_http["state"] == "Success":
            global_variable["flagRebootSync"] = 1
            log_service = f"{result_http['state']} Sync Reboot State"
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
        
        else:
            log_service = f"{result_http['state']} Sync Reboot State - {result_http['log']}"
            color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
        
        global_variable["flagRebootSync"] = 1    
        global_variable["logger"].debug(f"{color_log_service}\n")
        # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
        global_variable["log"].append(log_service)
     
        
    def syncSensorHttp(server_config, timestamp, global_variable):
        result_http = httpProtocolFunction.runGetMethod(server_config, "sensor")
        
        if result_http["state"] == "Success":
            synchronizeFunction.syncSensorData(result_http["payload"], timestamp, global_variable)
        
        else:
            log_service = f"{result_http['state']} Sync Sensor Data - Status Code {result_http['state_code']} ({result_http['log']})"
            color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)


    def syncActuatorHttp(server_config, timestamp, global_variable):
        result_http = httpProtocolFunction.runGetMethod(server_config, "actuator")
        
        if result_http["state"] == "Success":
            synchronizeFunction.syncActuatorData(result_http["payload"], timestamp, global_variable)
        
        else:
            log_service = f"{result_http['state']} Sync Actuator Data - Status Code {result_http['state_code']} ({result_http['log']})"
            color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
    
    
    def runCheckReceiveMessageMQTT(device_data, server_config, global_variable):
        datetimes = times.now()
        timestamp = times.convertTimeToString(datetimes) 
        messages_data = mqtt.receiveMessage()
        
        if len(messages_data) > 0:
            for x in range(len(messages_data)):
                receive_topic = messages_data[x]["topic"]
                message = messages_data[x]["msg"]  
            
                for y in global_variable["topicSubscriptionState"]:
                    topic = serverFunction.getServerDataByServerAndParameter(server_config["server"], y)
            
                    if receive_topic == topic["data"]:
                        if y == "sensor":
                            message = json.loads(message)
                            synchronizeFunction.syncSensorData(message, timestamp, global_variable)
                            break
            
                        elif y == "node":
                            message = json.loads(message)
                            synchronizeFunction.syncNodeData(device_data, message, timestamp, global_variable)
                            break
            
                        elif y == "actuator":
                            message = json.loads(message)
                            synchronizeFunction.syncActuatorData(message, timestamp, global_variable)
                            break


    def syncNodeData(device_data, message, timestamp, global_variable):
        nodeId = message["id"]
        if device_data["uid"] == nodeId:
            device_name = message["name"]
            reboot_state = message["reboot_status"]
            DeviceSettingDB.updateByName("name", device_name)
            log_service = f"Success Sync Node ({nodeId}) Data"
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
            
            if int(reboot_state) == 1:
                log_service = "Device Trigger Reboot from Server"     
                color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
                global_variable["logger"].debug(f"{color_log_service}\n")
                # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
                global_variable["log"].append(log_service)
                os.system("sudo reboot")
    
    
    def syncSensorData(message, timestamp, global_variable):
        if len(message) > 0:
            sensor_data = CollectDataSensorFunction.all()
            count_sensor = 0
            
            for x in range(len(message)):
                sensor_id = message[x]["costume_id"]
            
                for y in range(sensor_data["numSensor"]):
                    if sensor_id == sensor_data["sensorId"][y]:
                        count_sensor += 1
                        sensor_name = message[x]["name"]
                        sensor_unit = message[x]["unit"]
                        sensor_alarm = message[x]["alarm"]
            
                        if sensor_alarm == "" or sensor_alarm == None: sensor_alarm = 0
                        elif sensor_alarm == True: sensor_alarm = 1 
                        elif sensor_alarm == False: sensor_alarm = 0
                        
                        sensor_alarm_type = message[x]["alarm_type"]
                        if sensor_alarm_type == "": sensor_alarm_type = 0
                        elif sensor_alarm_type == "&": sensor_alarm_type = 3
                        elif sensor_alarm_type == ">": sensor_alarm_type = 2
                        elif sensor_alarm_type == "<": sensor_alarm_type = 1
                        # else: sensor_alarm_type = -1
                        
                        sensor_alarm_max = message[x]["highest_value"]
                        sensor_alarm_min = message[x]["lowest_value"]
                        updateDB = SensorListDB.updateParam(sensor_name, sensor_alarm, sensor_alarm_max, sensor_alarm_min, sensor_unit, sensor_alarm_type, timestamp, sensor_id) 
                        break
            
            log_service = f"Success Sync {count_sensor} of {sensor_data['numSensor']} Sensor Data"  
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])    
            global_variable["log"].append(log_service)
        
        else:
            log_service = f"No Sensor Sync from Server"       
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
    
    
    def syncActuatorData(message, timestamp, global_variable):
        if len(message) > 0:
            actuator_sync = 0
            actuator_data = ActuatorListDB.select()
            
            for x in range(len(message)):
                for y in range(len(actuator_data)):
                    actuator_id = message[x]["costume_id"]
                    # actuatorId = message[x]["custom_id"]
                
                    if actuator_id == actuator_data[y]["actuator_custom_id"]:
                        actuator_sync += 1
                        actuator_name = message[x]["name"]
                        
                        actuator_value = message[x]["value"]
                        if actuator_value == "true": actuator_value = 1
                        elif actuator_value == "false": actuator_value = 0 
                        
                        actuator_schedule = message[x]["scheduling"]
                        if actuator_schedule == True:
                            schedule_server = message[x]["scheduler"]
                            schedule_db = ActuatorScheduleDB.selectByActuatorId(actuator_data[y]["id"])
                            id_schedule_db, id_schedule_server = [], []
                            
                            ### Logic for Add Schedule from Server ###
                            for num1 in range(len(schedule_db)):
                                schedule_db_day = schedule_db[num1]["day"]
                                schedule_db_time = schedule_db[num1]["time"]
                                schedule_db_time = datetime.datetime.strptime(str(schedule_db_time), "%H:%M:%S")
                                schedule_db_time = schedule_db_time.strftime("%H:%M")
                                schedule_db_value = schedule_db[num1]["value"]
                                id_schedule_db.append(schedule_db[num1]["id"])
                                
                                for num2 in range(len(schedule_server)):
                                    schedule_server_day = schedule_server[num2]["day"].title()
                                    schedule_server_time = schedule_server[num2]["time"]
                                    schedule_server_value = schedule_server[num2]["value"]
                                
                                    if str(schedule_db_day) == str(schedule_server_day) and str(schedule_db_time) == str(schedule_server_time) and str(schedule_db_value) == str(schedule_server_value):
                                        id_schedule_server.append(schedule_db[num1]["id"])
                                        break
                            
                            ### Logic for Remove Schedule from Server ###
                            for num1 in range(len(schedule_server)):
                                schedule_server_day = schedule_server[num1]["day"]
                                schedule_server_time = schedule_server[num1]["time"]
                                schedule_server_value = schedule_server[num1]["value"]
                                check_schedule = ActuatorScheduleDB.selectBySchedule(actuator_data[y]["id"], schedule_server_day, schedule_server_time, schedule_server_value)
                                
                                if len(check_schedule) == 0:
                                    schedule_id = generalFunction.GenerateId.generateIdNearon("actuator", "actuator-schedule")
                                    schedule_server_day = schedule_server_day.title()
                                    ActuatorScheduleDB.insert(schedule_id, actuator_data[y]["id"], schedule_server_day, schedule_server_time, schedule_server_value)
                            
                            schedule_sync = set(id_schedule_db) - set(id_schedule_server)
                            schedule_sync = list(schedule_sync)
                            for num1 in range(len(schedule_sync)):
                                ActuatorScheduleDB.deleteById(schedule_sync[num1])
                        
                        elif actuator_schedule == False:
                            actuator_schedule = 0 
                            ActuatorScheduleDB.deleteByActId(actuator_data[y]["id"])
                        updateDB = ActuatorListDB.updateParam(actuator_name, actuator_value, timestamp, actuator_schedule, actuator_data[y]["id"])
                        break
            
            log_service = f"Success Sync {actuator_sync} of {len(actuator_data)} Actuator Data"  
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)
        
        else:
            log_service = f"No Actuator Sync from Server"       
            color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
            global_variable["logger"].debug(f"{color_log_service}\n")
            # SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            global_variable["log"].append(log_service)