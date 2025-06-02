import argparse
import sys
from puresnmp import get

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SensorGroupDB
from sql_connex import snmp
sys.path.append("/home/connex/project/function/sensor")
from oidSensorFunction import OidSensorFunction
 
 
parser = argparse.ArgumentParser()
 
# Adding optional argument
parser.add_argument("-i", "--ID", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
id = None

if args.ID != None:
   id = args.ID
    
def main():
    global id
    
    timestamp = times.getDatetime()
       
    ### OID CHECK ###
    sensor_data = SensorListDB.selectById(id)
    if len(sensor_data) == 1:
        group_id = sensor_data[0]['group_id']
        sensor_name = sensor_data[0]['name']
        sensor_oid = sensor_data[0]['oid']
        sensor_tipe = sensor_data[0]['oid_tipe'] 
        group_data = SensorGroupDB.selectOne(group_id)
        if len(group_data) == 1:
            group_name = group_data[0]['name']
        else:
            group_name = 'N/A'
        base_oid = OidSensorFunction.getBaseOID(group_id)
        oid = str(base_oid) + "." + str(sensor_oid)
        ip = '127.0.0.1'
        get_community = snmp.selectByName("community")
        if len(get_community):
            snmp_community = get_community[0]['value']
        else:
            snmp_community = 'public'  
        print("Timestamp : " + timestamp)
        print("Group Sensor : " + group_name)
        print("Sensor Name : " + sensor_name)
        print("OID Sensor : " + oid)
        if sensor_tipe == 0:
            print("OID Datatype : Integer")
        else:
            print("OID Datatype : String")           
        try:
            result = get(ip, snmp_community, oid)
            if sensor_tipe == 0:
                print("Value Raw : " + str(result))
                print("Value : " + str(result/100))
            else:
                print("Value Raw : " + str(result))
                print("Value : " + str(result.decode()))    
            print("State : Success")
        except Exception as e:
            print("State : Error Read OID " + str(e)) 
    else:
        print("State : Cannot Found Sensor List")
    #################

if __name__ == '__main__': main()
