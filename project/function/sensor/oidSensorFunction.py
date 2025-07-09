import os
import shutil
import sys

from collectDataSensorFunction import CollectDataSensorFunction

sys.path.append('/home/connex/project/database')
from query_project_db import SensorParameterGroupDB, SensorListDB
from sql_connex import snmp
sys.path.append("/home/connex/project/function")
from serviceProjectFunction import ServiceProjectFunction

class OidSensorFunction:
    def getBaseOID(group_id):
        getData = SensorParameterGroupDB.selectByGroupParameter(group_id, 'parent_oid')
        if len(getData) == 1:
            baseOid = getData[0]['value']
        else :
            baseOid = 'Undefined'
        return baseOid

    def createSensorOid():
        def handleValue(oid_type):
            if oid_type == 0:
                values = '0'
            else:
                values = 'N/A'
            return values
        base = "/home/connex"
        path_snmp =  base + "/project/sensor/oid"
        os.system("sudo rm -r " + path_snmp)
        cek = os.path.exists(path_snmp)
        if cek == False:
            os.system("sudo mkdir " + path_snmp)
        if base != '':
            sensors  = SensorListDB.select()
            if sensors:
                shutil.copy(base + '/platform/storage/snmpd.conf.master', '/etc/snmp/snmpd.conf')
                files = open("/etc/snmp/snmpd.conf", "a")
                files.write("\n")
                for itemSensor in range(len(sensors)):
                    id = sensors[itemSensor]['id']
                    oid_sensor = sensors[itemSensor]['oid']
                    base_oid = OidSensorFunction.getBaseOID(sensors[itemSensor]['group_id'])
                    oid = f"{base_oid}.{sensors[itemSensor]['oid_group']}.{oid_sensor}"
                    oid_script = path_snmp + "/" + oid + ".sh"
                    cek_script = os.path.exists(oid_script)
                    if cek_script == False:
                        f = open(oid_script, "w")
                        f.write("#!/bin/bash\n")
                        f.write("cat /tmp/" + oid)
                        f.close()
                    sensorByID = SensorListDB.selectById(id)
                    if sensorByID:
                        for itemSensor in sensorByID:
                            value = sensorByID[0]['value']
                            oid_tipe = sensorByID[0]['oid_tipe']
                        if value == None:
                            value = handleValue(oid_tipe)
                    else:
                        value = '0'
                        oid_tipe = 0
                    if oid_tipe == 0:
                        oid_tipe = 'integer'
                        if value == 'N/A':
                            value = 0
                        oid_value = int(float(value)*100)
                    else:
                        oid_tipe = 'string'
                        if value == 0:
                            value = 'N/A'
                        oid_value = value
                    oid_file = "/tmp/" + str(oid)
                    state = OidSensorFunction.writeSensorOidFile(oid_file, oid, oid_tipe, oid_value)
                    files.write("pass ." + oid + " /bin/sh " + oid_script + "\n")
                files.close()
                os.system("sudo systemctl restart snmpd")

    def generateOidAtBoot():
        dataSensor = CollectDataSensorFunction.all()
        for i in range(dataSensor['numSensor']):
            serviceName = "sensor" + str(dataSensor['groupId'][i])
            serviceData = ServiceProjectFunction.getServiceInfo(serviceName)
            base_oid = OidSensorFunction.getBaseOID(dataSensor['groupId'][i])
            sensor_data = SensorListDB.selectById(dataSensor['id'][i])
            last_oid = dataSensor['sensorOid'][i]
            oid_tipe = dataSensor['sensorDatatype'][i]
            if serviceData['state'] != "active":
                if 'state_sensor' != 'Success':
                    if oid_tipe == 0:
                        dataSensor['sensorValue'][i] = '0'
                    else:
                        dataSensor['sensorValue'][i] = 'N/A'
            oid = str(base_oid) + "." + str(last_oid)
            oid_file = "/tmp/" + str(oid)
            f = open(str(oid_file), "w")
            f.write("." + str(oid) + ".0")
            f.write("\n")
            if oid_tipe == 0:
                f.write("integer")
                value = int(float(dataSensor['sensorValue'][i])*100)
            else:
                f.write("string")
                value = dataSensor['sensorValue'][i]
            f.write("\n")
            f.write(str(value))
            f.write("\n")
            f.close()
            print("Sensor " + str(dataSensor['sensorName'][i]) + " (" + str(oid) + ") Updated with Value " + str(value))


    def writeSensorOidFile(oid_file, oid, oid_tipe, oid_value):
        try:
            f = open(str(oid_file), "w")
            f.write("." + str(oid) + ".0")
            f.write("\n")
            f.write(str(oid_tipe))
            f.write("\n")
            f.write(str(oid_value))
            f.write("\n")
            f.close()
            state = 1
        except Exception as e:
            state = 0
        return state
