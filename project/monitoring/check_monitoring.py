import sys
import argparse

sys.path.append('/home/connex/library')
from SynapsisLibrary import packData, times
sys.path.append('/home/connex/project/function')
from httpProtocolFunction import httpProtocolFunction
from mqttProtocolFunction import mqttProtocolFunction
from serverFunction import serverFunction
from dbFunction import dbFunction
sys.path.append('/home/connex/project/function/sensor')
from collectDataSensorFunction import CollectDataSensorFunction

globalVariable = {'mqttConnection': None, 'mqttClient': None}
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--Protocol", help = "Show Output")
args = parser.parse_args()
protocol = None
if args.Protocol != None:
    protocol = args.Protocol

def main():
    try:
        timestamp = times.getDatetime()
        timestampUTC = times.convertToUTC(timestamp)
        sensorData = CollectDataSensorFunction.all()
        deviceSetting = dbFunction.getDeviceSetting()
        serverConfig = serverFunction.getServerConfig()
        dataPack = packData.dataPack(deviceSetting['uid'], sensorData['sensorId'], sensorData['sensorValue'], sensorData['numSensor'], timestampUTC, 9)  
        if str(protocol) == 'HTTP':
            print(f'Timestamp : {timestamp}')
            print(f"Protocol : HTTP")
            resultMonitoring = httpProtocolFunction.runPostMethod(serverConfig['http'], 'receiver', dataPack, flag=True)
            print(f"Data Pack : {dataPack}")
            print(f"Message : {resultMonitoring['state']} Monitoring - Status Code {resultMonitoring['state_code']}")
        elif str(protocol) == 'MQTT':
            print(f'Timestamp: {timestamp}')
            print(f"Protocol : MQTT")
            resultMonitoring = mqttProtocolFunction.runPublish(serverConfig['mqtt'], "data", dataPack, globalVariable, flag=True)
            print(f"Data Pack : {dataPack}")
            print(f"Message : {resultMonitoring['state']} Monitoring - Status Code {resultMonitoring['state_code']}")
    except Exception as e:
        print(f'Error : {e} ')

if __name__ == '__main__': main()
