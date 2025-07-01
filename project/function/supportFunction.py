import os
import subprocess
import sys 
import time
import RPi.GPIO as GPIO

sys.path.append('/home/connex/library')
from SynapsisLibrary import times, sql
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SensorGroupDB, ResetDatabaseProject
sys.path.append('/home/connex/project/function')
from serviceProjectFunction import ServiceProjectFunction
sys.path.append('/home/connex/platform/database')
from databaseReset import resetDatabase, openDB, openDBProject


LED_PIN = 9
RESET_PIN = 10
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  
GPIO.setup(LED_PIN, GPIO.OUT) 
GPIO.setup(RESET_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
globalVariabel = {"delayBlink": 0.2, "gapGroupSensorBlink": 2, "configFile": {}, "sourceConfig": "/home/connex/platform/default/config"}

globalVariabel['configFile'] = {
    "interfaces": "/etc/network/",
    "hostapd.conf": "/etc/hostapd",
    "wpa_supplicant.conf": "/etc/wpa_supplicant",
    "dnsmasq.conf": "/etc",
    "config.txt": "/boot",
    "snmpd.conf": "/etc/snmp",
    "timesyncd.conf": "/etc/systemd"
}

class supportFunctionSystem:
    def blinkLED(times):
        for _ in range(times):
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(globalVariabel['delayBlink'])
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(globalVariabel['delayBlink'])
        time.sleep(globalVariabel['gapGroupSensorBlink'])    

    def ledErrorCheck():
        timestamp = times.getDatetime()
        count = 0
        group = SensorGroupDB.selectGroupOrderedByNumber()

        for num in range(len(group)):
            sensorData = SensorListDB.selectByGroupFull(group[num]["id"])
            checkServices = ServiceProjectFunction.checkActiveService(f'sensor{group[num]["number"]}.service')
            countBlink = int(group[num]["number"])

            if checkServices == 'inactive':
                count += 1
                print(f"{timestamp} - Service {group[num]['name']} Error : Inactive Service")
                supportFunctionSystem.blinkLED(countBlink)
            
            else:
                for data in sensorData:
                    if data['conditions'] == "Alarm Error":
                        count += 1
                        print(f"{timestamp} - Service {data['name_group']} Error : List Sensor Error")
                        supportFunctionSystem.blinkLED(countBlink)
                        break
        
        if count == 0: print(f"{timestamp} - All Sensors Normal")

    def copy_files():
        timestamp = times.getDatetime()
        for file_name, dest_dir in globalVariabel["configFile"].items():
            source_file = os.path.join(globalVariabel['sourceConfig'], file_name)
            dest_file = os.path.join(dest_dir, file_name)
            try:
                subprocess.run(['sudo', 'cp', source_file, dest_file], check=True)
                print(f"{timestamp} - Copied {file_name} to {dest_dir}")
            except Exception as e:
                print(f"{timestamp} - Failed to copy {file_name} to {dest_dir}: {e}")

    def verify_files():
        timestamp = times.getDatetime()
        all_files_copied = True
        for file_name, dest_dir in globalVariabel['configFile'].items():
            source_file = os.path.join(globalVariabel['sourceConfig'], file_name)
            dest_file = os.path.join(dest_dir, file_name)
            if not os.path.exists(dest_file):
                print(f"{timestamp} - File {file_name} not found in {dest_dir}")
                all_files_copied = False
            else:
                if os.path.getsize(source_file) != os.path.getsize(dest_file):
                    print(f"{timestamp} - File {file_name} in {dest_dir} is not the correct size")
                    all_files_copied = False
        return all_files_copied

    def writeDatabase():
        timestamp = times.getDatetime()
        db_path = '/home/connex/platform/default/db'
        sql_files = [f for f in os.listdir(db_path) if f.endswith('.sql')]
        all_files_overwrite = True
        for sql_file in sql_files:
            table_name = os.path.splitext(sql_file)[0]
            file_path = os.path.join(db_path, sql_file)
            print(f"{timestamp} - Deleting table: {table_name}")
            if table_name == 'featureSettingDB':
                delete_result_project = ResetDatabaseProject.deleteTable(table_name)
                if not delete_result_project:
                    print(f"{timestamp} - Failed to delete table {table_name}")
                    all_files_overwrite = False
                    return all_files_overwrite
                else:
                    print(f"{timestamp} - Deleting table successfully : {table_name}")

                print(f"{timestamp} - Inserting data from: {file_path}")
                host, database, username, password = openDBProject()
                insert_result = sql.import_sql_file(file_path, host, database, username, password)
                if not insert_result:
                    print(f"{timestamp} - Failed to insert data from {file_path}")
                    all_files_overwrite = False
                    return all_files_overwrite
                else:
                    print(f"{timestamp} - SQL file imported successfully from {file_path}")
            else:
                delete_result = resetDatabase.deleteTable(table_name)
                if not delete_result:
                    print(f"{timestamp} - Failed to delete table {table_name}")
                    all_files_overwrite = False
                    return all_files_overwrite
                else:
                    print(f"{timestamp} - Deleting table successfully : {table_name}")

                print(f"{timestamp} - Inserting data from: {file_path}")
                host, database, username, password = openDB()
                insert_result = sql.import_sql_file(file_path, host, database, username, password)
                if not insert_result:
                    print(f"{timestamp} - Failed to insert data from {file_path}")
                    all_files_overwrite = False
                    return all_files_overwrite
                else:
                    print(f"{timestamp} - SQL file imported successfully from {file_path}")
                
            print(f"{timestamp} - Table {table_name} refreshed successfully.")
        return all_files_overwrite
    
    def resetSystem():
        timestamp = times.getDatetime()
        start_time = time.time()
        while GPIO.input(RESET_PIN) == GPIO.LOW:
            if time.time() - start_time >= 10:
                print(f"{timestamp} - Button pressed for 10 seconds, copying files and overwrite database...")
                time.sleep(1)
                supportFunctionSystem.copy_files()
                supportFunctionSystem.writeDatabase()
                if supportFunctionSystem.verify_files() and supportFunctionSystem.writeDatabase():
                    print(f"{timestamp} - All files copied and all database overwrite successfully. System will reboot.")
                    subprocess.run(['sudo', 'reboot'])
                else:
                    print(f"{timestamp} - File verification failed")
                return
        print(f"{timestamp} - Button released before 10 seconds")
