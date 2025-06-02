path = "/home/connex"

import datetime
import pytz
import sys

sys.path.append(f"{path}/library")
from SynapsisLibrary import packData, http
sys.path.append(f"{path}/project/function")
from serverFunction import serverFunction
sys.path.append(f"{path}/project/database")
from query_project_db import ServerHttpAuthDB


class httpProtocolFunction():
    def getAuthentication(timestamp, global_variable):
        server_config = serverFunction.getServerConfig()
        url_auth = serverFunction.getServerDataByServerAndParameter(server_config["http"]["server"], "auth")
        http_authentication = serverFunction.getServerHttpAuth()
        
        if str(http_authentication["state"]) != "1":
            if url_auth["state"] == True:
                auth_data = packData.userPack(user=server_config["http"]["username"], password=server_config["http"]["password"])
                result_auth = http.auth(url=url_auth["data"], user=auth_data, timeout=10)
                
                if int(result_auth["state"]) == 200:
                    token = result_auth['token']
                    expire = result_auth['expire']
                    
                    if token == "" and expire == "":
                        ServerHttpAuthDB.updateValueByName(False, "state")
                        log_service = f"Failed Authentication - Token N/A - Status Code {result_auth['state']}"
                        color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                    
                    else:
                        ServerHttpAuthDB.updateValueByName(True, "state")
                        log_service = f"Success Authentication - Status Code {result_auth['state']}"
                        color_log_service = f"\033[92m{log_service} at {timestamp}\033[00m"
                    
                    ServerHttpAuthDB.updateValueByName(token, "token")
                    ServerHttpAuthDB.updateValueByName(expire, "expire")
                
                elif int(result_auth["state"]) == 404:
                    log_service = f"Failed Authentication - URL N/A on Server - Status Code {result_auth['state']}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                
                elif int(result_auth["state"]) == 405:
                    log_service = f"Failed Authentication - Method Not Allowed - Status Code {result_auth['state']}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                
                else:
                    log_service = f"Failed Authentication - Error {result_auth['payload']} - Status Code {result_auth['state']}"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
            
            else:
                ServerHttpAuthDB.updateValueByName("-", "token")
                ServerHttpAuthDB.updateValueByName("-", "expire")
                ServerHttpAuthDB.updateValueByName(False, "state")
                log_service = "Failed Authentication - URL N/A"
                color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"

        else:
            if http_authentication["expire"] == "" or http_authentication["expire"] == None:
                ServerHttpAuthDB.updateValueByName(False, "state")
                log_service = "Expire Time Authentication N/A"
                color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"
                
            else: 
                expire_time_format = "%a, %d %b %Y %H:%M:%S GMT"
                expire_time = datetime.datetime.strptime(http_authentication["expire"], expire_time_format)
                utc_zone = pytz.utc
                expire_time = utc_zone.localize(expire_time)
                datetime_format = "%Y-%m-%d %H:%M:%S"
                now_time = datetime.datetime.strptime(timestamp, datetime_format)
                local_zone = pytz.timezone("Asia/Jakarta")
                now_time = local_zone.localize(now_time)
                now_time = now_time.astimezone(pytz.utc)
                
                if now_time < expire_time:
                    log_service = "Device Already Authentication with Server"
                    color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
                
                elif now_time > expire_time:
                    ServerHttpAuthDB.updateValueByName(False, "state")
                    log_service = "Device Authentication Already Expire"
                    color_log_service = f"\033[31m{log_service} at {timestamp}\033[00m"

                else:
                    log_service = "Device Already Authentication with Server"
                    color_log_service = f"\033[94m{log_service} at {timestamp}\033[00m"
        
        global_variable["logger"].debug(f"{color_log_service}\n")
        return log_service


    def runPostMethod(server_config, parameter_api, data_pack, flag=None):
        url_endpoint = serverFunction.getServerDataByServerAndParameter(server_config["server"], parameter_api)
        
        if url_endpoint["state"] == True:
            http_auth = serverFunction.getServerHttpAuth()
            if str(http_auth["state"]) == "1":
                if parameter_api == "notif":
                    url_endpoint["data"] = url_endpoint["data"] + data_pack
                    http_data = http.post(url=url_endpoint["data"], data=None, token=http_auth["token"], timeout=60)
            
                else:   
                    if flag == True:    
                        print("URL : ", url_endpoint["data"])
                    http_data = http.post(url=url_endpoint["data"], data=data_pack, token=http_auth["token"], timeout=60)
            
                state_code = http_data["state"]
                
                if int(state_code) == 200:
                    state_http = "Success"
                    log_http, payload_http = http_data["message"], http_data["payload"].json()
            
                else: 
                    state_http = "Failed"
                    
                    if int(state_code) == 444:   
                        log_http, payload_http = http_data["message"], http_data["payload"] 
                    
                    elif int(state_code) == 404:
                        log_http, payload_http = "URL N/A on Server", http_data['payload'].text                        
                    
                    elif int(state_code) == 405:
                        log_http, payload_http = "Method Not Allowed", http_data['payload'].text                        
                    
                    else: 
                        payload = http_data['payload'].json()
                        log_http, payload_http = payload['message'], payload

            else:
                state_http, state_code, log_http, payload_http = "Failed", 401, "Token N/A", {}
        
        else:    
            state_http, state_code, log_http, payload_http = "Failed", 404, "URL N/A on Device", {}
        
        result_http = {"state": state_http, "log": log_http, "state_code": state_code, "payload": payload_http}   
        return result_http
    
    
    def runPutMethod(server_config, parameter_api, data_pack):
        url_endpoint = serverFunction.getServerDataByServerAndParameter(server_config["server"], parameter_api)
        
        if url_endpoint["state"] == True:
            http_auth = serverFunction.getServerHttpAuth()
        
            if str(http_auth["state"]) == "1":
                http_data = http.put(url=url_endpoint["data"], data=data_pack, token=http_auth["token"], timeout=60)
                state_code = http_data["state"]
            
                if int(state_code) == 200:
                    state_http = "Success"
                    log_http, payload_http = http_data["message"], http_data["payload"].json()
            
                else:
                    state_http = "Failed"
                    
                    if int(state_code) == 444:   
                        log_http, payload_http = http_data["message"], http_data["payload"] 

                    elif int(state_code) == 404:
                        log_http, payload_http = "URL N/A on Server", http_data['payload'].text                        
                    
                    elif int(state_code) == 405:
                        log_http, payload_http = "Method Not Allowed", http_data['payload'].text                        
                    
                    else: 
                        payload = http_data['payload'].json()
                        log_http, payload_http = payload['message'], payload
            
            else:
                state_http, state_code, log_http, payload_http = "Failed", 401, "Token N/A", {}
        
        else:    
            state_http, state_code, log_http, payload_http = "Failed", 404, "URL N/A on Device", {}
        
        result_http = {"state": state_http, "log": log_http, "state_code": state_code, "payload": payload_http}    
        return result_http
    
    
    def runGetMethod(server_config, parameter_api):
        url_endpoint = serverFunction.getServerDataByServerAndParameter(server_config["server"], parameter_api)
        
        if url_endpoint["state"] == True:
            http_authentication = serverFunction.getServerHttpAuth()
        
            if str(http_authentication["state"]) == "1":
                http_data = http.get(url_endpoint["data"], token=http_authentication["token"], timeout=10) 
                state_code = http_data["state"]
        
                if int(http_data["state"]) == 200:
                    state_http, state_code = "Success", http_data["state"]
                    log_http, payload_http = http_data["message"], http_data["payload"].json()["data"]
        
                else:
                    state_http = "Failed"
                    if int(state_code) == 444:  
                        log_http, payload_http = http_data["message"], http_data["payload"] 

                    elif int(state_code) == 404:
                        log_http, payload_http = "URL N/A on Server", http_data['payload'].text                        
                    
                    elif int(state_code) == 405:
                        log_http, payload_http = "Method Not Allowed", http_data['payload'].text                        
                    
                    else: 
                        payload = http_data['payload'].json()
                        log_http, payload_http = payload['message'], payload
        
            else:
                state_http, state_code, log_http, payload_http = "Failed", 401, "Token N/A", {}   
        
        else:
            state_http, state_code, log_http, payload_http = "Failed", 404, "URL N/A on Device", {}
        
        result_http = {"state": state_http, "log": log_http, "state_code": state_code, "payload": payload_http}      
        return result_http 