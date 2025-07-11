import json
import os
import shutil
import sys

sys.path.append('/home/connex/platform/database')
from sql import services


class serviceSensor():
    def createSensorFile(number):
        def file_read(source):
            file = open(source, 'r')
            data = file.readlines()
            file.close()
            return data
        def file_write(source, data):
            file = open(source, 'w')
            file.writelines(data)
            file.close()
        basePath = '/home/connex'
        
        ##### Create Service #####
        filenameSensor = f'sensor{number}'
        data = file_read(basePath + '/platform/storage/service.master')
        command = "/usr/bin/python3 " + filenameSensor + ".py"
        path = basePath + "/project/sensor"
        data[5] = "ExecStart={}\n".format(command)
        data[6] = "WorkingDirectory={}\n".format(path)
        file_write('/lib/systemd/system/' + filenameSensor + '.service', data)
        services.insert(filenameSensor, path, command)
        check = services.selectByName(filenameSensor)
        service_id = 0
        if len(check) == 1: service_id = check[0]['id']
            
    
        ##### Create File #####   
        fileSensorPath = basePath + '/project/sensor/sensor' + str(number) + '.py'
        fileCheckSensorPath = basePath + '/project/sensor/check_sensor' + str(number) + '.py'
        shutil.copy(basePath + "/platform/storage/sensor/sensor.py", fileSensorPath)
        shutil.copy(basePath + "/platform/storage/sensor/check_sensor.py", fileCheckSensorPath)
        fileSensorData = file_read(fileSensorPath)
        fileSensorData[0] = 'group_id = ' + str(number) + '\n'
        file_write(fileSensorPath, fileSensorData)
        fileCheckSensorData = file_read(fileCheckSensorPath)
        fileCheckSensorData[0] = 'group_id = ' + str(number) + '\n'
        file_write(fileCheckSensorPath, fileCheckSensorData)
        os.system(f"sudo chown connex:connex {basePath}/project/sensor/*")
        os.system("sudo systemctl daemon-reload")
        return service_id

    def deleteSensorFile(number, service_id):
        base_path = '/home/connex'
        filename_sensor = f'actuator{number}'
        service_file_path = f'/lib/systemd/system/{filename_sensor}.service'
        sensor_file_path = base_path + f'/project/sensor/sensor{number}.py'
        check_sensor_file_path = base_path + f'/project/sensor/check_actuator{number}.py'
            
        services.delete(service_id)
        os.system(f"sudo systemctl stop {filename_sensor}")
        os.system(f"sudo systemctl disable {filename_sensor}")
        if os.path.exists(service_file_path): os.remove(service_file_path)
        if os.path.exists(sensor_file_path): os.remove(sensor_file_path)
        if os.path.exists(check_sensor_file_path): os.remove(check_sensor_file_path)
        os.system("sudo systemctl daemon-reload")
            
            
    def renameSensorFile(last_number, number, service_id):
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
        last_filename = f'sensor{last_number}'
        filename = f'sensor{number}'

        last_service_file_path = f'/lib/systemd/system/{last_filename}.service'
        filename_service_file_path = f'/lib/systemd/system/{filename}.service'
        last_sensor_file_path = base_path + f'/project/sensor/sensor{last_number}.py'
        filename_sensor_file_path = base_path + f'/project/sensor/sensor{number}.py'
        last_check_sensor_file_path = base_path + f'/project/sensor/check_sensor{last_number}.py'
        filename_check_sensor_file_path = base_path + f'/project/sensor/check_sensor{number}.py'
        command = f"/usr/bin/python3 {filename}.py"
            
        services.updateService(filename, f"{base_path}/project/sensor/", command, service_id)

        if os.path.exists(last_service_file_path): os.rename(last_service_file_path, filename_service_file_path)
        if os.path.exists(last_sensor_file_path): os.rename(last_sensor_file_path, filename_sensor_file_path)
        if os.path.exists(last_check_sensor_file_path): os.rename(last_check_sensor_file_path, filename_check_sensor_file_path)

        service_data = file_read(filename_service_file_path)
        service_data[5] = f"ExecStart={command}\n"
        service_data[6] = f"WorkingDirectory={base_path}/project/sensor\n"
        file_write(filename_service_file_path, service_data)

        def update_file_with_number(file_path, number):
            data = file_read(file_path)
            data[0] = f'group_number = {number}\n'
            file_write(file_path, data)

        update_file_with_number(filename_sensor_file_path, number)
        update_file_with_number(filename_check_sensor_file_path, number)

        os.system(f"sudo chown connex:connex {base_path}/project/sensor/*")
        os.system("sudo systemctl daemon-reload")

