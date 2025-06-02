import os
import sys
import time

sys.path.append("/home/connex/project/function")
from dbFunction import dbFunction
from notificationFunction import notificationFunction
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction
sys.path.append('/home/connex/project/database')
from query_project_db import SensorGroupDB
sys.path.append("/home/connex/platform/function")
from backupFunction import backupFunction


os.system("sudo rfkill unblock wifi")
print("Handle Block WiFi")
print("-----------------------------------")

time.sleep(20)
feature_setting = dbFunction.getFeatureSetting()
if int(feature_setting["notification"]) == 1:
   notificationFunction.generateNotificationNode("Power On", "", feature_setting)
   print("State : Success Create Notification Power On")
else:
   print("State : Connex Notification Setting Inactive")
print("-----------------------------------")

backupFunction.config()
backupFunction.service()
backupFunction.db()
print("Backup Config OS, Service, and DB")
print("-----------------------------------")

OidSensorFunction.generateOidAtBoot()

print("Check Sensor Group State")
print("-----------------------------------")

sensorGroupData = SensorGroupDB.select()
for x in range(len(sensorGroupData)):
   if sensorGroupData[x]['state'] == '1':
      os.system(f"sudo systemctl start sensor{sensorGroupData[x]['number']}.service && sudo systemctl enable sensor{sensorGroupData[x]['number']}.service")
   else:
      os.system(f"sudo systemctl stop sensor{sensorGroupData[x]['number']}.service && sudo systemctl disable sensor{sensorGroupData[x]['number']}.service")