import json
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import packData, http
sys.path.append('/home/connex/project/database')
from query_project_db import ServerHttpDB, ServerMqttDB, ServerSettingDB, ServerHttpAuthDB
sys.path.append('/home/connex/project/function')
from serverFunction import serverFunction


class settingServer():
    def updateConfig(domainAddress, ipAddress, port, user, passw, server):
        try:
            state = ServerSettingDB.updateByName(domainAddress, ipAddress, port, user, passw, server)
            if server == 'http':
                result = {'state':state, 'message':'Update Successful! Your http config have been successfully updated.'} 
            else:
                result = {'state':state, 'message':'Update Successful! Your mqtt config have been successfully updated.'}
        except Exception as e:
            result = {'state':'0', 'message':f'Update Failed! Sorry, there was an issue updating - {str(e)}'} 
        return json.dumps(result)
    
    class http():
        def insertAPI(name, parameter, type, api):
            try:
                state = ServerHttpDB.insert(name, parameter, type, api)
                result = {'state':state, 'message':'Server HTTP API added successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed to Add Server HTTP API - ' + str(e)}
            return json.dumps(result)
        
        def updateAPI(name, parameter, type, api, id):
            try:
                state = ServerHttpDB.update(name, parameter, type, api, id)
                result = {'state':state, 'message':'Update Successful! Your Server HTTP API have been successfully updated.'}
            except Exception as e:
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
            return json.dumps(result)
        
        def deleteAPI(name):
            try:
                state = ServerHttpDB.delete(name)
                result = {'state':state, 'message':'Server HTTP API deleted successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed Delete Server HTTP API - ' + str(e)}
            return json.dumps(result)
        
        def deleteAuth():
            try:
                ServerHttpAuthDB.deleteValueByName("token")
                ServerHttpAuthDB.deleteValueByName("expire")
                ServerHttpAuthDB.deleteValueByName("state")
                result = {'state':'1', 'message':'Clear Authentication Successfully!'} 
            except Exception as e:
                result = {'state':'0', 'message':f'Clear Authentication Failed! Sorry, there was an issue - {str(e)}'} 
            return json.dumps(result)

        def getAuth():
            try:
                serverConfig = serverFunction.getServerConfig()
                urlAuth = serverFunction.getServerDataByServerAndParameter(serverConfig['http']['server'], "auth")
                if urlAuth['state'] == True:
                    authData = packData.userPack(serverConfig['http']['username'], serverConfig['http']['password'])
                    resultAuth = http.auth(urlAuth['data'], authData, timeout=10)
                    if  resultAuth['state'] == 200:
                        token = resultAuth['token']
                        expire = resultAuth['expire']
                        ServerHttpAuthDB.updateValueByName(token, "token")
                        ServerHttpAuthDB.updateValueByName(expire, "expire")
                        ServerHttpAuthDB.updateValueByName(True, "state")
                        result = {'state':'1', 'message':'A new authentication token has been successfully obtained!'}
                    else:
                        result = {'state':'0', 'message': 'Unable to get a new authentication token - status code {}'.format(str(resultAuth['state']))}
                else:
                    result = {'state':'0', 'message': 'Unable to get a new authentication token - URL N/A'}
            except Exception as e:
                result = {'state':'0', 'message': 'Unable to get a new authentication token - {}'.format((e))}
            return json.dumps(result)
    
    class mqtt():
        def insertTopic(name, parameter, api):
            try:
                state = ServerMqttDB.insert(name, parameter, api)
                result = {'state':state, 'message':'Server MQTT Topic added successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed to Add Server MQTT Topic - ' + str(e)}
            return json.dumps(result)
        
        def updateTopic(name, parameter, topic, id):
            try:
                state = ServerMqttDB.update(name, parameter, topic, id)
                result = {'state':state, 'message':'Update Successful! Your Server MQTT Topic have been successfully updated.'}
            except Exception as e:
                result = {'state':'0', 'message':'Update Failed! Sorry, there was an issue - ' + str(e)}
            return json.dumps(result)
        
        def deleteTopic(id):
            try:
                state = ServerMqttDB.delete(id)
                result = {'state':state, 'message':'Server MQTT Topic deleted successfully!'}
            except Exception as e:
                result = {'state':'0', 'message':'Failed Delete Server MQTT Topic - ' + str(e)}
            return json.dumps(result)
   