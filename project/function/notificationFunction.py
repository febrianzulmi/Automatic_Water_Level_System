path = "/home/connex"

import random
import sys
import string

sys.path.append(f"{path}/library")
from SynapsisLibrary import times
sys.path.append(f"{path}/project/database")
from query_project_db import LogNotifDB, SystemServiceDB, ActuatorListDB
sys.path.append(f"{path}/project/function")
from httpProtocolFunction import httpProtocolFunction
from mqttProtocolFunction import mqttProtocolFunction
from dbFunction import dbFunction
from generalFunction import generalFunction


class notificationFunction():
    def runNotification(num, notification_data, server_config, global_variable):
        result_notification = 0
        timestamp = times.getDatetime()
        nearon_device_info = dbFunction.getDeviceSetting()
        id_notif = notification_data[num]["id"]
        subject_message = notification_data[num]["subject"]
        notif_message = notification_data[num]["message"]
        type_message = notification_data[num]["notif"].lower()
        types = notification_data[num]["type"]
        project_data = generalFunction.getProjectSetting()
        protocol_monitoring = project_data["protocol"] # 1: HTTP, 2: MQTT, 3: SNMP 
        if type_message == "whatsapp": type_message =  "wa"
        
        if str(protocol_monitoring) == "1":
            server = "nearon"

            if server == "dcm":
                notif_pack = notificationFunction.dcmVersion(nearon_device_info, subject_message, type_message, notif_message, types)
                result_monitoring = httpProtocolFunction.runPostMethod(server_config["http"], "notif", notif_pack)

            else:
                url_notification = notificationFunction.connexVersion(nearon_device_info, subject_message, type_message, notif_message, types)
                result_monitoring = httpProtocolFunction.runPostMethod(server_config["http"], "notif", url_notification)

            if result_monitoring["state"] == "Success":
                result_notification = 1
                global_variable["countNotification"] += 1
                LogNotifDB.updateNotif(id_notif, "Success", timestamp)
                log_service = "Running {} of {} Notification Data".format(global_variable["countNotification"], len(notification_data))
                SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])

            else:
                result_notification = 0
        
        elif str(protocol_monitoring) == "2":
            if types != "Device": level = "1"
            else: level = "5"

            data_pack_notification = {"node_id": nearon_device_info["uid"], "subject": subject_message, "message": notif_message, "type": type_message, "level": level}
            result_monitoring = mqttProtocolFunction.runPublish(server_config["mqtt"], "notif", data_pack_notification, global_variable)
            if result_monitoring["state"] == "Success": 
                result_notification = 1
                global_variable["countNotification"] += 1
                LogNotifDB.updateNotif(id_notif, "Success", timestamp)
                log_service = "Running {} of {} Notification Data".format(global_variable["countNotification"], len(notification_data))
                SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
            
            else:
                result_notification = 0
        
        else:
            result_notification = 0
            result_monitoring = {"state": "Failed", "log": "Protocol N/A", "state_code": "444", "payload": {}}       

        if result_notification == 0:
            log = f"Status Code {result_monitoring['state_code']}"       
            log_service = f"Running {global_variable['countNotification']} of {len(notification_data)} Notification Data | {log}"
        
        else:
            log_service = f"Running {global_variable['countNotification']} of {len(notification_data)} Notification Data"
        
        SystemServiceDB.updateStatusByName(log_service, timestamp, global_variable["serviceName"])
        result_notification = {"state": result_notification, "message": result_monitoring}
        return result_notification


    def dcmVersion(nearon_device_info, subject_message, type_message, notif_message, types):
        notif_pack = {}
        notif_pack["node_id"] = nearon_device_info["uid"]
        notif_pack["subject"] = subject_message
        notif_pack["message"] = notif_message
        if types != "Device": level = "5"
        else: level = "1"
        notif_pack["level"] = level
        notif_pack["type"] = type_message
        return notif_pack


    def connexVersion(nearon_device_info, subject_message, type_message, notif_message, types):
        url_notification = f"/send?node_id={str(nearon_device_info['uid'])}"
        if types != 'Device':
            url_notification = f"{url_notification}&level=5"
        else:
            url_notification = f"{url_notification}&level=1"
        url_notification = f"{url_notification}&message={str(notif_message)}&type={str(type_message)}&subject={str(subject_message)}"
        return url_notification


    def generateNotificationSensor(id_sensor, name_sensor, value, config_alarm, type_alarm, unit, timestamp, feature_setting):
        setting_data = dbFunction.getDeviceSetting()
        unix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        device_name = f"{setting_data['name']} ({setting_data['uid']})"
        
        if unit == None: unit = ""
        if unit == "#": unit = "%23"
        if unit == " ": unit = ""
        
        if "door" in name_sensor.lower():
            if str(value) == "1": value = "1 (Open)"
            elif str(value) == "0": value = "0 (Close)"
            else: "-1 (N/A)"
        
        elif "smoke" in name_sensor.lower():
            if str(value) == "1": value = "1 (Detect)"
            elif str(value) == "0": value = "0 (No Detect)" 
            else: value = "-1 (N/A)" 
        
        elif "water" in name_sensor.lower():
            if str(value) == "1": value = "1 (No Detect)"
            elif str(value) == "0": value = "0 (Detect)"
            else: value = "-1 (N/A)"   
        
        if unit != "":
            if unit == "%": value = f"{value}{unit}"
            else: value = f"{value} {unit}"
        
        subject_notification_web = f"Node {str(device_name)} - Alarm Sensor Notification"
        subject_notification = f"Node {str(device_name)} Notification"
        
        email_message = f"Node : <b><i>{device_name}</i></b><br>" \
                    f"Type Notification : <b><i>Sensor Alarm</i></b><br>" \
                    f"Sensor : <b><i>{name_sensor}</i></b><br>" \
                    f"Value : <b><i>{value}</i></b><br>"
        telegram_message = f"<b>{subject_notification} %23{str(unix)}</b><br><br>" \
                            f"Type Notification : <b><i>Sensor Alarm</i></b><br>" \
                            f"Sensor : <b><i>{name_sensor}</i></b><br>" \
                            f"Value : <b><i>{value}</i></b><br>"
        web_message = f"Sensor {name_sensor} value is {value}"
        whatsapp_message = f"Node *_{device_name}_* - Sensor *_{name_sensor}_* value is *_{value}_*"

        if type_alarm == "Alarm Error":
            email_message += f"Condition : <b><i>Alarm Error</i></b><br>"
            telegram_message += f"Condition : <b><i>Alarm Error</i></b><br>"
            web_message += f" reach Error Condition"
            whatsapp_message += f" reach *_Error Condition_*"

        else:
            limit_min, limit_max = str(config_alarm["min"]), str(config_alarm["max"])
            if unit != "":
                limit_min = f"{limit_min} {unit}"
                limit_max = f"{limit_max} {unit}"
            
            email_message += f"Condition : <b><i>{type_alarm}</i></b><br>"
            telegram_message += f"Condition : <b><i>{type_alarm}</i></b><br>"
            
            if type_alarm == "Normal":
                web_message += f" reach Normal Condition"
                whatsapp_message += f" reach *_Normal Condition_*"
            
            elif type_alarm == "Alarm Min":
                web_message += f" reach The Lowest Value"
                whatsapp_message += f" reach *_The Lowest Value_*"
            
            elif type_alarm == "Alarm Max":
                web_message += f" reach The Highest Value"
                whatsapp_message += f" reach *_The Highest Value_*"
            
            if str(config_alarm["config"]) == "3":
                email_message += f"Limit Min Value : <b><i>{limit_min}</i></b><br>" \
                                f"Limit Max Value : <b><i>{limit_max}</i></b><br>" \
                                f"Configuration Alarm : <b><i>Alarm Min %26 Alarm Max</i></b><br>" 
                telegram_message += f"Limit Min Value : <b><i>{limit_min}</i></b><br>" \
                                f"Limit Max Value : <b><i>{limit_max}</i></b><br>" \
                                f"Configuration Alarm : <b><i>Alarm Min %26 Alarm Max</i></b><br>" 
                web_message += f" with alarm configuration Alarm Min ({limit_min}) %26 Alarm Max ({limit_max})"
                whatsapp_message += f" with alarm configuration *_Alarm Min ({limit_min}) %26 Alarm Max ({limit_max})_*"
            
            elif str(config_alarm["config"]) == "2":
                email_message += f"Limit Max Value : <b><i>{limit_max}</i></b><br>" \
                                f"Configuration Alarm : <b><i>Alarm Max Only</i></b><br>" 
                telegram_message += f"Limit Max Value : <b><i>{limit_max}</i></b><br>" \
                                    f"Configuration Alarm : <b><i>Alarm Max Only</i></b><br>" 
                web_message += f" with alarm configuration Alarm Max Only ({limit_max})"
                whatsapp_message += f" with alarm configuration *_Alarm Max Only ({limit_max})_*"
            
            elif str(config_alarm["config"]) == "1":
                email_message += f"Limit Min Value : <b><i>{limit_min}</i></b><br>" \
                                f"Configuration Alarm : <b><i>Alarm Min Only</i></b><br>" 
                telegram_message += f"Limit Min Value : <b><i>{limit_min}</i></b><br>" \
                                    f"Configuration Alarm : <b><i>Alarm Min Only</i></b><br>" 
                web_message += f" with alarm configuration Alarm Min Only ({limit_min})"
                whatsapp_message += f" with alarm configuration *_Alarm Min Only ({limit_min})_*"
                
        web_message += f" at {timestamp} GMT%2B7"
        whatsapp_message += f" at *_{timestamp} GMT%2B7_*"
        email_message += f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
        telegram_message += f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
        
        if int(feature_setting["notificationSensorWeb"]) == 1:
            LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Web", subject_notification_web, web_message, "Waiting", timestamp)
        if int(feature_setting["notificationSensorWA"]) == 1:
            LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Whatsapp", "-", whatsapp_message, "Waiting", timestamp)
        if int(feature_setting["notificationSensorEmail"]) == 1:
            LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Email", subject_notification, email_message, "Waiting", timestamp)
        if int(feature_setting["notificationSensorTelegram"]) == 1:
            LogNotifDB.insert("Sensor", name_sensor, type_alarm, "Telegram", "-", telegram_message, "Waiting", timestamp)


    def generateNotificationNode(type, message, feature_setting):
        device_setting = dbFunction.getDeviceSetting()
        timestamp = times.getDatetime()
        unix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        device_name = f"{device_setting['name']} ({device_setting['uid']})"
        
        subject_notification_web = f"Node {str(device_name)} - Device Information Notification"
        subject_notification = F"Node {str(device_name)} Notification"
        
        if type == "Power On":
            email_message = f"Node : <b><i>{device_name}</i></b><br>" \
                            f"Type Notification : <b><i>Device Information</i></b><br>" \
                            f"Information : <b><i>Power On</i></b><br>" \
                            f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
            telegram_message = f"<b>{subject_notification} %23{str(unix)}</b><br><br>" \
                                f"Type Notification : <b><i>Device Information</i></b><br>" \
                                f"Information : <b><i>Power On</i></b><br>" \
                                f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
            web_message = f"Powered On at {timestamp} GMT%2B7"
            whatsapp_message = f"Node *_{device_setting['name']}_* is *_Powered On_* at *_{timestamp} GMT%2B7_*"
        
        elif type == "Service Error":
            email_message = f"Node : <b><i>{device_name}</i></b><br>" \
                        f"Type Notification : <b><i>Service Warning</i></b><br>" \
                        f"Service : <b><i>{message['service']}</i></b><br>" \
                        f"Error : <b><i>{message['type']} ({message['message']} in Line {message['line']})</i></b><br>" \
                        f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
            telegram_message = f"<b>{subject_notification} %23{str(unix)}</b><br><br>" \
                            f"Type Notification : <b><i>Service Warning</i></b><br>" \
                            f"Service : <b><i>{message['service']}</i></b><br>" \
                            f"Error : <b><i>{message['type']} ({message['message']} in Line {message['line']})</i></b><br>" \
                            f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>"
            web_message = f"Service {message['service']} is error {message['type']} ({message['message']}) in line {message['line']} at {timestamp} GMT%2B7"
            whatsapp_message = f"Node *_{device_name}_* - Service *_{message['service']}_* is error *_{message['type']} ({message['message']})_* in line *_{message['line']}_* at *_{timestamp} GMT%2B7_*"
        
        if int(feature_setting["notificationNodeWeb"]) == 1:
            LogNotifDB.insert("Device", "-", type, "Web", subject_notification_web, web_message, "Waiting", timestamp)
        if int(feature_setting["notificationNodeTelegram"]) == 1:
            LogNotifDB.insert("Device", "-", type, "Telegram", "-", telegram_message, "Waiting", timestamp)
        if int(feature_setting["notificationNodeWA"]) == 1:
            LogNotifDB.insert("Device", "-", type, "Whatsapp", "-", whatsapp_message, "Waiting", timestamp)
        if int(feature_setting["notificationNodeEmail"]) == 1:
            LogNotifDB.insert("Device", "-", type, "Email", subject_notification, email_message, "Waiting", timestamp)


    def generateNotificationActuator(id_act, state, value, timestamp, control):
        device_setting = dbFunction.getDeviceSetting()
        feature_setting = dbFunction.getFeatureSetting()
        device_name = f"{device_setting['name']} ({device_setting['uid']})"
        unix = "".join(random.choices(string.ascii_letters + string.digits, k=8))
        
        act_detail = ActuatorListDB.selectById(id_act)
        for x in act_detail:
            actuator_name = x["name"]
        
        # if str(value) == "1": value = "Action"
        # elif str(value) == "0": value = "OFF"
        # else: value = F"N/A ({value})"
        
        if str(state) == "0": state = "First Boot"
        elif str(state) == "1": state = "Server Remote"
        elif str(state) == "2": state = "Schedule"
        elif str(state) == "3": state = "Local Remote"

        subject_notification_web = f"Node {device_name} - Control Actuator Notification"
        subject_notification = f"Node {device_name} Notification"

        email_message = f"Node : <b><i>{device_name}</i></b><br>" \
                    f"Type Notification : <b><i>Actuator Control</i></b><br>" \
                    f"Actuator : <b><i>{actuator_name}</i></b><br>" \
                    f"Trigger Control : <b><i>{state}</i></b><br>"
        telegram_message = f"<b>{subject_notification} %23{str(unix)}</b><br><br>" \
                        f"Type Notification : <b><i>Actuator Control</i></b><br>" \
                        f"Actuator : <b><i>{actuator_name}</i></b><br>" \
                        f"Trigger Control : <b><i>{state}</i></b><br>" \
                            
        if str(state) == "First Boot":
            email_message += f"Value : <b><i>{value} (Synchronize from Last Control Value)</i></b><br>"
            telegram_message += f"Value : <b><i>{value} (Synchronize from Last Control Value)</i></b> <br>"
            web_message = f"Actuator {actuator_name} is controlled ({control}) by {state} with " \
                        f"value {value} (Synchronize from Last Control Value) at {timestamp} GMT%2B7"
            whatsapp_message = f"Node *_{device_name}_* - Actuator *_{actuator_name}_* is controlled *_({control})_* by *_{state}_* with " \
                            f"value *_{value} (Synchronize from Last Control Value)_* at *_{timestamp} GMT%2B7_*"

        else:
            email_message += f"Value : <b><i>{value}</i></b><br>"
            telegram_message += f"Value : <b><i>{value}</i></b><br>"
            web_message = f"Actuator {actuator_name} is controlled ({control}) by {state} with " \
                        f"value {value} at {timestamp} GMT%2B7"
            whatsapp_message = f"Node *_{device_name}_* - Actuator *_{actuator_name}_* is controlled *_({control})_* by *_{state}_* with " \
                            f"value *_{value}_* at *_{timestamp} GMT%2B7_*"

        email_message += f"Control : <b><i>{control}</i></b><br>" \
                        f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>" 
        telegram_message += f"Control : <b><i>{control}</i></b><br>" \
                        f"Timestamp : <b><i>{timestamp} GMT%2B7</i></b>" 

        if int(feature_setting["notificationActuatorWeb"]) == 1:
            LogNotifDB.insert("Actuator", actuator_name , state, "Web", subject_notification_web, web_message, "Waiting", timestamp)
        if int(feature_setting["notificationActuatorWA"]) == 1:
            LogNotifDB.insert("Actuator", actuator_name , state, "Whatsapp", "-", whatsapp_message, "Waiting", timestamp)
        if int(feature_setting["notificationActuatorEmail"]) == 1:
            LogNotifDB.insert("Actuator", actuator_name , state, "Email", subject_notification, email_message, "Waiting", timestamp)
        if int(feature_setting["notificationActuatorTelegram"]) == 1:
            LogNotifDB.insert("Actuator", actuator_name , state, "Telegram", "-", telegram_message, "Waiting", timestamp)