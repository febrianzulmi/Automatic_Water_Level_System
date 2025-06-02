import sys

sys.path.append('/home/connex/project/database')
from query_project_db import FeatureSettingDB, DeviceSettingDB


class dbFunction():    
    def getDeviceSetting():
        getData = DeviceSettingDB.select()
        deviceSetting = {}
        if getData :
            for item in getData :
                    item['updatedAt'] = item['updatedAt'].isoformat()
                    if item['name'] in ['uid', 'name', 'version'] :
                        deviceSetting[item['name']]= item['value']      
        else :
            deviceSetting = {'uid': '', 'name': '', 'version': ''}
        return deviceSetting
            
            
    def getFeatureSetting():
        getData = FeatureSettingDB.select()
        feature_setting = {}
        if getData :
            for item in getData :     
                feature_setting[item['name']] = item['value']          
        return feature_setting