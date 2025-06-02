import json
import sys

sys.path.append('/home/connex/project/database')
from query_project_db import DeviceSettingDB


class settingDevice():
    def insert(deviceUID, deviceName, deviceVersion):
        try : 
            state = DeviceSettingDB.insert(deviceUID, deviceName, deviceVersion)
            result = {'state':state, 'message':'Device Setting Added Successfully!'} 
        except :
            result = {'state':'0', 'message':'Failed to Add Device Setting!'} 
        return json.dumps(result)
    
    def update(deviceUID, deviceName, deviceVersion):
        try : 
            state = DeviceSettingDB.update(deviceUID, deviceName, deviceVersion)
            result = {'state':state, 'message':'Update Successful! Your device settings have been successfully updated.'} 
        except :
            result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue updating your device settings.'} 
        return json.dumps(result)
