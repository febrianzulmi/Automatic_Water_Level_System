import datetime 
import json
import os
import sys
import shutil

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/platform/database')
from sql import services
sys.path.append('/home/connex/project/database')
from query_project_db import ActuatorListDB, ActuatorScheduleDB, LogActuatorDB, SensorListDB, ActuatorParameterListDB, ActuatorParameterGroupDB
sys.path.append('/home/connex/project/function')
from notificationFunction import notificationFunction


class ActuatorFunction():
    def checkSyncValueFunction(actuator_data, timestamp, actionActuator, global_variable):
        actuator_run = {"value": [], "action": [], "count": 0}
        for x in range(len(actuator_data)):
            actuator_run["value"].append(actuator_data[x]["last_action_value"])
            if actuator_data[x]["last_action_value"] != None: actuator_run["action"].append(True)
            else: actuator_run["action"].append(False)
            actuator_run["count"] += 1
        status_actuator = actionActuator(global_variable, actuator_run, actuator_data)
        status_actuator["summary"] = f"{status_actuator['summary']} - Controlled by Boot Sync"
        for x in range(len(actuator_data)):
            global_variable["logger"].debug(f"- Sync {actuator_data[x]['name']} ({actuator_data[x]['actuator_custom_id']})")
            global_variable["logger"].debug(f"  o Action Value : {status_actuator['value'][x]}")
            global_variable["logger"].debug(f"  o Result Action : {status_actuator['state'][x]}")
            global_variable["logger"].debug(f"  o Result Message : {status_actuator['message'][x]}")
            if status_actuator["state"][x] == True:
                control = "1x Action"
                ActuatorListDB.updateAction(actuator_run["value"][x], 0, timestamp, actuator_data[x]["id"])
                LogActuatorDB.insert(actuator_data[x]["id"], actuator_run["value"][x], 0, timestamp)
                notificationFunction.generateNotificationActuator(actuator_data[x]["id"], 0, actuator_run["value"][x], timestamp, control)
        return status_actuator
    
    
    def checkServerValueFunction(actuator_data, timestamp, actionActuator, global_variable):
        actuator_run = {"value": [], "action": [], "count": 0}
        for x in range(len(actuator_data)):
            if str(actuator_data[x]["server_value"]) != str(actuator_data[x]["last_server_value"]):
                actuator_run["value"].append(actuator_data[x]["server_value"])
                actuator_run["action"].append(True)
                actuator_run["count"] += 1
            else:
                actuator_run["value"].append(None)
                actuator_run["action"].append(False)
        if actuator_run["count"] > 0:
            status_actuator = actionActuator(global_variable, actuator_run, actuator_data)
            status_actuator["summary"] = f"{status_actuator['summary']} - Controlled by Server Remote"
            for x in range(len(actuator_data)):
                if actuator_run["action"][x] == True:
                    global_variable["logger"].debug(f"- Actuator {actuator_data[x]['name']} ({actuator_data[x]['actuator_custom_id']})")
                    global_variable["logger"].debug(f"  o Action Value : {status_actuator['value'][x]}")
                    global_variable["logger"].debug(f"  o Result Action : {status_actuator['state'][x]}")
                    global_variable["logger"].debug(f"  o Result Message : {status_actuator['message'][x]}")    
                    if status_actuator["state"][x] == True:
                        control = "1x Action"
                        ActuatorListDB.updateAction(actuator_run["value"][x], 0, timestamp, actuator_data[x]["id"])
                        ActuatorListDB.updateLastServer(actuator_run["value"][x], timestamp, actuator_data[x]["id"])
                        LogActuatorDB.insert(actuator_data[x]["id"], actuator_run["value"][x], 0, timestamp)
                        notificationFunction.generateNotificationActuator(actuator_data[x]["id"], 1, actuator_run["value"][x], timestamp, control)
        else:
            status_actuator = {"state": [], "value": [], "summary": "No Triggered Actuator by Server Remote", "message": [], "": 0}
        return status_actuator 
    
        
    def checkScheduleFunction(actuator_data, timestamp, actionActuator, global_variable):
        nows = times.now()
        now_time = nows.strftime("%H:%M")
        now_day = nows.strftime("%A")
        actuator_run = {"value": [], "action": [], "count": 0, "schedule": [], "id": []}
        for x in range(len(actuator_data)):
            schedule = ActuatorScheduleDB.selectByActuatorId(actuator_data[x]['id'])
            if len(schedule) > 0:
                schedule_trigger = None
                for i in range(len(schedule)):
                    id_sch = schedule[i]['id']
                    day = schedule[i]['day']
                    time = schedule[i]['time']
                    time = datetime.datetime.strptime(str(time), "%H:%M:%S")
                    time = time.strftime("%H:%M")
                    value = schedule[i]['value']
                    state = schedule[i]['state']
                    if now_time == time and now_day == day:
                        if state == 0 or state == None:
                            schedule_trigger = True
                            schedule_data = {"id": id_sch, "day": day, "time": time}
                            actuator_run["value"].append(value)
                            actuator_run["action"].append(True)
                            actuator_run["count"] += 1
                            actuator_run["schedule"].append(schedule_data)
                            actuator_run["id"].append(actuator_data[x]['actuator_custom_id'])
                            break
                        break
                    else:
                        ActuatorScheduleDB.updateState(0, id_sch)
                if schedule_trigger != True:
                    actuator_run["value"].append(None)
                    actuator_run["action"].append(False)  
                    actuator_run["schedule"].append({}) 
                    actuator_run["id"].append(actuator_data[x]['actuator_custom_id'])
            else:
                actuator_run["value"].append(None)
                actuator_run["action"].append(False)  
                actuator_run["schedule"].append({})    
                actuator_run["id"].append(actuator_data[x]['actuator_custom_id'])                    
        if actuator_run["count"] > 0:
            status_actuator = actionActuator(global_variable, actuator_run, actuator_data)
            status_actuator["summary"] = f"{status_actuator['summary']} - Controlled by Schedule"
            for x in range(len(actuator_data)):
                if actuator_run["action"][x] == True:
                    global_variable["logger"].debug(f"- Actuator {actuator_data[x]['name']} ({actuator_data[x]['actuator_custom_id']})")
                    global_variable["logger"].debug(f"  o Schedule Time : {actuator_run['schedule'][x]['day']} - {actuator_run['schedule'][x]['time']}")
                    global_variable["logger"].debug(f"  o Action Value : {status_actuator['value'][x]}")
                    global_variable["logger"].debug(f"  o Result Action : {status_actuator['state'][x]}")
                    global_variable["logger"].debug(f"  o Result Message : {status_actuator['message'][x]}")
                    if status_actuator["state"][x] == True:
                        control = "1x Action"
                        ActuatorScheduleDB.updateState(1, actuator_run["schedule"][x]["id"])
                        ActuatorListDB.updateAction(actuator_run["value"][x], 2, timestamp, actuator_data[x]["id"])
                        LogActuatorDB.insert(actuator_data[x]["id"], actuator_run["value"][x], 2, timestamp)
                        notificationFunction.generateNotificationActuator(actuator_data[x]["id"], 2, actuator_run["value"][x], timestamp, control)
        else:
            status_actuator = {"state": [], "value": [], "summary": "No Triggered Actuator by Schedule", "message": [], "": 0}
        return status_actuator         
  
   
    def getParameterListActuator(number):
        parameterData = ActuatorParameterListDB.selectByActuatorGroupNumberFull(number)
        if len(parameterData) > 0:
            result = {}
            for item in parameterData:
                actuator_custom_id = item['actuator_custom_id']
                parameter = item['parameter']
                value = item['value']
                if actuator_custom_id not in result:
                    result[actuator_custom_id] = {}
                result[actuator_custom_id][parameter] = value
        else :
            result = {}
        return result
    
    
    def getParameterGroupActuator(number):
        parameterData = ActuatorParameterGroupDB.selectByActuatorGroupNumberFull(number)
        if len(parameterData) > 0:
            result = {}
            for item in parameterData:
                result[item['parameter']] = item['value']
        else :
            result = {}
        return result


    class ServiceActuator():
        def createActuatorFile(number):
            def file_read(source):
                file = open(source, 'r')
                data = file.readlines()
                file.close()
                return data
            def file_write(source, data):
                file = open(source, 'w')
                file.writelines(data)
                file.close()
            base_path = '/home/connex'
            
            ##### Create Service #####
            filename_actuator = f'actuator{number}'
            data = file_read(base_path + '/platform/storage/service.master')
            command = "/usr/bin/python3 " + filename_actuator + ".py"
            path = base_path + "/project/actuator"
            data[5] = "ExecStart={}\n".format(command)
            data[6] = "WorkingDirectory={}\n".format(path)
            file_write('/lib/systemd/system/' + filename_actuator + '.service', data)
            services.insert(filename_actuator, path, command)
            check = services.selectByName(filename_actuator)
            service_id = 0
            if len(check) == 1: service_id = check[0]['id']
            
            ##### Create File #####   
            file_actuator_path = base_path + '/project/actuator/actuator' + str(number) + '.py'
            file_check_actuator_path = base_path + '/project/actuator/check_actuator' + str(number) + '.py'
            shutil.copy(base_path + "/platform/storage/actuator/actuator.py", file_actuator_path)
            shutil.copy(base_path + "/platform/storage/actuator/check_actuator.py", file_check_actuator_path)
            file_actuator_data = file_read(file_actuator_path)
            file_actuator_data[0] = 'number = ' + str(number) + '\n'
            file_write(file_actuator_path, file_actuator_data)
            file_check_actuator_data = file_read(file_check_actuator_path)
            file_check_actuator_data[0] = 'number = ' + str(number) + '\n'
            file_write(file_check_actuator_path, file_check_actuator_data)
            os.system(f"sudo chown connex:connex {base_path}/project/actuator/*")
            os.system("sudo systemctl daemon-reload")
            return service_id


        def deleteActuatorFile(number, service_id):
            base_path = '/home/connex'
            filename_actuator = f'actuator{number}'
            service_file_path = f'/lib/systemd/system/{filename_actuator}.service'
            actuator_file_path = base_path + f'/project/actuator/actuator{number}.py'
            check_actuator_file_path = base_path + f'/project/actuator/check_actuator{number}.py'
            
            services.delete(service_id)
            os.system(f"sudo systemctl stop {filename_actuator}")
            os.system(f"sudo systemctl disable {filename_actuator}")
            if os.path.exists(service_file_path): os.remove(service_file_path)
            if os.path.exists(actuator_file_path): os.remove(actuator_file_path)
            if os.path.exists(check_actuator_file_path): os.remove(check_actuator_file_path)
            os.system("sudo systemctl daemon-reload")
            
            
        def renameActuatorFile(last_number, number, service_id):
            def file_read(source):
                file = open(source, 'r')
                data = file.readlines()
                file.close()
                return data
            
            def file_write(source, data):
                file = open(source, 'w')
                file.writelines(data)
                file.close()

            base_path = '/home/connex'
            last_filename = f'actuator{last_number}'
            filename = f'actuator{number}'

            last_service_file_path = f'/lib/systemd/system/{last_filename}.service'
            filename_service_file_path = f'/lib/systemd/system/{filename}.service'
            last_actuator_file_path = base_path + f'/project/actuator/actuator{last_number}.py'
            filename_actuator_file_path = base_path + f'/project/actuator/actuator{number}.py'
            last_check_actuator_file_path = base_path + f'/project/actuator/check_actuator{last_number}.py'
            filename_check_actuator_file_path = base_path + f'/project/actuator/check_actuator{number}.py'
            command = f"/usr/bin/python3 {filename}.py"
            
            services.updateService(filename, filename_service_file_path, command, service_id)

            if os.path.exists(last_service_file_path): os.rename(last_service_file_path, filename_service_file_path)
            if os.path.exists(last_actuator_file_path): os.rename(last_actuator_file_path, filename_actuator_file_path)
            if os.path.exists(last_check_actuator_file_path): os.rename(last_check_actuator_file_path, filename_check_actuator_file_path)

            service_data = file_read(filename_service_file_path)
            service_data[5] = f"ExecStart={command}\n"
            service_data[6] = f"WorkingDirectory={base_path}/project/actuator\n"
            file_write(filename_service_file_path, service_data)

            def update_file_with_number(file_path, number):
                data = file_read(file_path)
                data[0] = f'number = {number}\n'
                file_write(file_path, data)

            update_file_with_number(filename_actuator_file_path, number)
            update_file_with_number(filename_check_actuator_file_path, number)

            os.system(f"sudo chown connex:connex {base_path}/project/actuator/*")
            os.system("sudo systemctl daemon-reload")