import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import mqtt
sys.path.append('/home/connex/project/function')
from serverFunction import serverFunction


class mqttProtocolFunction():
    def runPublish(serverConfig, parameterTopic, dataPack, globalVariable, flag=None):
        serverTopic = serverFunction.getServerDataByServerAndParameter(serverConfig['server'], parameterTopic)
        if globalVariable['mqttConnection'] == False or globalVariable['mqttConnection'] == None:
            initConnection = 1
            connectionData = mqtt.connect(serverConfig['domainAddress'], serverConfig['port'], serverConfig['username'], serverConfig['password'], alive=5, timeout=10)
            globalVariable['mqttConnection'] = connectionData['state']
            globalVariable['mqttClient'] = connectionData['client']
        if globalVariable['mqttConnection'] == True and globalVariable['mqttClient'] is not None:
            if serverTopic['state'] == True:
                publishData = mqtt.publishMessage(globalVariable['mqttClient'], serverTopic['data'], dataPack, qos=0)
                if publishData['publishCode'] == 0:
                    stateMqtt, logMqtt, stateCode = 'Success', '', publishData['publishCode'] 
                else:
                    if publishData['publishId'] == -1 and publishData['publishCode'] == -1:
                        logMqtt = 'Publish Error (Publish Message Error {})'.format(publishData['errorMessage'])
                    else:
                        logMqtt = 'Publish Failed (Publish Message Code {})'.format(publishData['publishCode'])
                    stateMqtt, stateCode =  "Failed",  publishData['publishCode'] 
            else:
                stateMqtt, logMqtt, stateCode = 'Failed', 'Topic N/A', -1 
        else:
            stateMqtt = 'Failed'
            if initConnection == 1:
                logMqtt = 'Connection Failed (Connection Code {}) with Message Error {}'.format(connectionData['code'], connectionData['error'])
                stateCode = connectionData['code']
            else:
                logMqtt = 'Connection Failed (Publish Message Code {})'.format(publishData['publishCode'])
                stateCode = publishData['publishCode']
        if flag == True:
            print(f"Server : {serverConfig['domainAddress']}")
            print(f"Topic : {serverTopic['data']}")
        resultPublish = {"state": stateMqtt, "log": logMqtt, "state_code": stateCode}         
        return resultPublish  
    
    def runSubscription(action, serverConfig, parameterTopic, globalVariable):
        serverTopic = serverFunction.getServerDataByServerAndParameter(serverConfig['server'], parameterTopic)
        if globalVariable['mqttConnection'] == False or globalVariable['mqttConnection'] == None:
            initConnection = 1
            connectionData = mqtt.connect(serverConfig['domainAddress'], serverConfig['port'], serverConfig['username'], serverConfig['password'], alive=5, timeout=10)
            globalVariable['mqttConnection'] = connectionData['state']
            globalVariable['mqttClient'] = connectionData['client']
        if globalVariable['mqttConnection'] == True and globalVariable['mqttClient'] is not None:
            if serverTopic['state'] == True:
                if action == "Subscribe":
                    mqttData = mqtt.subscribeMessage(globalVariable['mqttClient'], serverTopic['data'])
                else:
                    mqttData = mqtt.unsubscribeMessage(globalVariable['mqttClient'], serverTopic['data'])
                if mqttData['mqttCode'] == 0:
                    stateMqtt, logMqtt, stateCode = 'Success', '', mqttData['mqttCode'] 
                else:
                    if mqttData['mqttId'] == -1 and mqttData['mqttCode'] == -1:
                        logMqtt = 'Subscribe Error (Subscribe Message Error {})'.format(mqttData['errorMessage'])
                    else:
                        logMqtt = 'Subscribe Failed (Subscribe Message Code {})'.format(mqttData['mqttCode'])
                    stateMqtt, stateCode =  "Failed",  mqttData['mqttCode'] 
            else:
                stateMqtt, logMqtt, stateCode = 'Failed', 'Topic N/A', -1 
        else:
            stateMqtt = 'Failed'
            if initConnection == 1:
                logMqtt = 'Connection Failed (Connection Code {}) with Message Error {}'.format(connectionData['code'], connectionData['error'])
                stateCode = connectionData['code']
            else:
                logMqtt = 'Connection Failed (Publish Message Code {})'.format(mqttData['mqttCode'])
                stateCode = mqttData['mqttCode']
        resultPublish = {"state": stateMqtt, "log": logMqtt, "state_code": stateCode}         
        return resultPublish