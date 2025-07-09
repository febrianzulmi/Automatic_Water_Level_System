import datetime
import sys

sys.path.append("/home/connex/project/database")
from query_project_db import RtuParameterDB, RtuDeviceDB, SensorListDB


rtu_device = RtuDeviceDB.select()
rtu_parameter = RtuParameterDB.select()
sensor_list = SensorListDB.selectByGroupNumberFull("1")

sensor_list = [
    {"name": "Voltage RTU 1", "sensor_id": "voltageRtu1", "oid": "1", "created_at": "2025-07-04 09:00:01"},
    {"name": "Current RTU 1", "sensor_id": "currentRtu1", "oid": "2", "created_at": "2025-07-04 09:00:02"},
    {"name": "Voltage RTU 2", "sensor_id": "voltageRtu2", "oid": "3", "created_at": "2025-07-04 09:00:03"},
    {"name": "Current RTU 2", "sensor_id": "currentRtu2", "oid": "4", "created_at": "2025-07-04 09:00:04"},
    {"name": "Power RTU 1", "sensor_id": "powerRtu1", "oid": "5", "created_at": "2025-07-04 09:00:05"},
    {"name": "Power RTU 2", "sensor_id": "powerRtu2", "oid": "6", "created_at": "2025-07-04 09:00:06"}
    # {"name": "Voltage RTU 6", "sensor_id": "voltageRtu6", "oid": "7", "created_at": "2025-07-04 09:00:07"},
    # {"name": "Current RTU 6", "sensor_id": "currentRtu6", "oid": "8", "created_at": "2025-07-04 09:00:08"},
    # {"name": "Power RTU 6", "sensor_id": "powerRtu6", "oid": "9", "created_at": "2025-07-04 09:00:09"},
    # {"name": "Voltage RTU 5", "sensor_id": "voltageRtu5", "oid": "10", "created_at": "2025-07-04 09:00:10"},
    # {"name": "Current RTU 5", "sensor_id": "currentRtu5", "oid": "11", "created_at": "2025-07-04 09:00:11"},
    # {"name": "Power RTU 5", "sensor_id": "powerRtu5", "oid": "12", "created_at": "2025-07-04 09:00:12"},
    # {"name": "Total RTU 1", "sensor_id": "totalRtu1", "oid": "13", "created_at": "2025-07-04 09:00:13"},    
    # {"name": "Total RTU 2", "sensor_id": "totalRtu2", "oid": "14", "created_at": "2025-07-04 09:00:14"},    
    # {"name": "Total RTU 5", "sensor_id": "totalRtu5", "oid": "15", "created_at": "2025-07-04 09:00:15"},
    # {"name": "Total RTU 6", "sensor_id": "totalRtu6", "oid": "16", "created_at": "2025-07-04 09:00:16"}        
]

print(f"{'Sensor ID':<20} {'OID':<5} {'Created At'}")
print(f"{'-'*20} {'-'*5} {'-'*26}")
for item in sensor_list:
    print(f"{str(item['sensor_id']):<20} {str(item['oid']):<5} {str(item['created_at'])}")

print("--------------------------------------------------------------------------------------")

oid = 0
for x in range(len(rtu_device)):
    for y in range(len(rtu_parameter)):
        parameter_id = f"{rtu_parameter[y]['custom_id']}Rtu{rtu_device[x]['number']}"
        for z in range(len(sensor_list)): 
            sensor_id = sensor_list[z]["sensor_id"]
            if parameter_id == sensor_id:
                oid += 1
                datetime_new = datetime.datetime.now()
                sensor_list[z]["oid"] = oid
                sensor_list[z]["created_at"] = datetime_new
                break

sensor_list.sort(key=lambda item: item["created_at"])
print(f"{'Sensor ID':<20} {'OID':<5} {'Created At'}")
print(f"{'-'*20} {'-'*5} {'-'*26}")
for item in sensor_list:
    print(f"{str(item['sensor_id']):<20} {str(item['oid']):<5} {str(item['created_at'])}")