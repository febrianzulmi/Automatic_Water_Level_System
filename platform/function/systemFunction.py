import datetime
import os
import subprocess
import sys
sys.path.append('/home/connex/platform/')
from function import checkActiveService, checkEnableService, checkDetailService
sys.path.append('/home/connex/platform/database')
from sql import info, services
sys.path.append('/home/connex/platform/function')
from boardFunction import boardFunction
sys.path.append('/home/connex/project/database')
from query_project_db import SystemServiceDB

class systemFunction():
    def readInformationSBC(globalVariable):
        print("---------- Read SBC Information ----------")
        temp = boardFunction.readCPUTemp()
        temp = temp.replace("\n","")
        storage = boardFunction.readStorage()
        usage = boardFunction.readCpuAndMemory() 
        usage['cpu'] = str(usage['cpu']) + " %"
        systemTime = boardFunction.readUptime()
        if globalVariable['fan'] == 1: # --> Control FAN By DHT
            result = boardFunction.readDHT11(globalVariable['device']['dht'])
            if result['status'] == True:
                fanSpeed = boardFunction.controlFanSpeed(globalVariable['device']['fan'], result['temperature'])  
                info.updateByName("temp", result['temperature'])
                info.updateByName("humidity", result['humidity'])
                info.updateByName("fan", fanSpeed)
                print("Temperature : ", result['temperature'], "(Updated)")
                print("Humidity : ", result['humidity'], "(Updated)")
                print("Fan Speed : ", fanSpeed, "(Control by DHT11 Temperature)")
                globalVariable['error'] = 0
            else:
                globalVariable['error'] += 1 
                if globalVariable['error'] <= 12:
                    print("Temperature : ", result['temperature'])
                    print("Humidity : ", result['humidity'])
                    print("Fan Speed : No Change")   
                else:
                    fanSpeed = boardFunction.controlFanSpeed(globalVariable['device']['fan'], 40)  
                    info.updateByName("temp", result['temperature'])
                    info.updateByName("humidity", result['humidity'])
                    info.updateByName("fan", fanSpeed)
                    print("Temperature : ", result['temperature'], "(Updated)")
                    print("Humidity : ", result['humidity'], "(Updated)")       
                    print("Fan Speed : ", fanSpeed)
        else: # --> Control FAN by CPU Temp
            fanSpeed = boardFunction.controlFanSpeed(globalVariable['device']['fan'], float(temp)) 
            info.updateByName("fan", fanSpeed) 
            print("Fan Speed : ", fanSpeed, "(Control by CPU Temperature)")
        info.updateByName("cpu_temp", temp)
        info.updateByName("cpu_usage", usage['cpu'])
        info.updateByName("memory", usage['memory'])
        info.updateByName("storage", storage)
        info.updateByName("uptime", systemTime['uptime'])
        info.updateByName("boot_time", systemTime['bootTime'])
        print("CPU Temperature : ", temp)
        print("CPU Usage : ", usage['cpu'])
        print("Memory : ", usage['memory'])
        print("Storage : ", storage)
        print("Uptime : ", systemTime['uptime'])
        print("Boot Time : ", systemTime['bootTime'])
        print("------------------------------------------")
    
    def checkSyncTime():
        def checkCommand(command):
            result = subprocess.check_output(command, shell=True)
            result = result.decode("utf-8")
            result = result.replace("\n","")
            return result
        print("---------- Sync RTC Time ----------")   
        sync = checkCommand("timedatectl | grep synchronized")	
        sync = sync.replace("System clock synchronized: ","")
        if sync == "no":
            print("Sync Time : ", sync)
            systemTime = checkCommand("date")
            print("System Time : ", systemTime)
            try:
                os.system("hwclock -s")	
                rtcTime = checkCommand("hwclock")
                print("RTC Time : ", rtcTime)
            except:
                print("RTC Time : No RTC Detect")
        else:
            print("Sync Time : ", sync)
        f = open("/home/connex/platform/logConnexTime.txt", "w")
        now = datetime.datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S")
        log = sync + ' ' + str(now)
        f.write(log)
        f.close()
        print("-----------------------------------") 

    def checkServiceProject():
        print("---------- Check Service ----------")
        get_service = services.select()
        for i in range(len(get_service)):
            service_name = get_service[i]['name']
            get_system = SystemServiceDB.selectByName(service_name)
            state = checkActiveService(service_name)
            enable = checkEnableService(service_name)
            if enable == 'disabled' and state == 'inactive':
                since, last_run = '-', '-'
            else:
                last_run, since = checkDetailService(service_name)
            if len(get_system) > 0:
                SystemServiceDB.updateServiceByName(state, enable, last_run, since, service_name)
            else:
                SystemServiceDB.insert(service_name, state, enable, last_run, since)
            print(get_service[i]['name'], '|', state, '|', enable, '|', last_run, '|', since)
        print("-----------------------------------")
    