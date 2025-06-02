import datetime
import subprocess
import sys
import time

sys.path.append('/home/connex/project/function')
from dbFunction import dbFunction
from notificationFunction import notificationFunction
sys.path.append('/home/connex/project/database')
from query_project_db import SystemServiceDB, LogErrorDB


class ServiceProjectFunction:
    def actionService(action, autorun, service_name):
        result = {'action_status': "0", 'autorun_status': "0",  "message": ""}
        valid_actions = ['start', 'stop']
        valid_autorun = ['enable', 'disable']
        
        if action not in valid_actions or autorun not in valid_autorun:
            raise ValueError("Invalid 'action' or 'autorun' parameter. Use 'start', 'stop', 'enable', or 'disable'.")
        
        try:
            action_process = subprocess.Popen(
                ["sudo", "systemctl", action, service_name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            action_out, action_err = action_process.communicate()
            if action_process.returncode == 0:
                result['action_status'] = 1
                result["message"] += F"Action {action} Service and "
            else:
                print(f"Action Error: {action_err.decode('utf-8')}")
                result['action_status'] = 0
                result['autorun_status'] = 0
                result["message"] = f"Action Error: {action_err.decode('utf-8')}"
                return result
        except Exception as e:
            print(f"Exception during action: {str(e)}")
            result['action_status'] = 0
            result['autorun_status'] = 0
            result["message"] = f"Exception during action: {str(e)}"
            return result

        try:
            autorun_process = subprocess.Popen(
                ["sudo", "systemctl", autorun, service_name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            autorun_out, autorun_err = autorun_process.communicate()
            if autorun_process.returncode == 0:
                result['autorun_status'] = 1
                result["message"] += F"Autorun {autorun} Successfully"
            else:
                print(f"Autorun Error: {autorun_err.decode('utf-8')}")
                result['action_status'] = 0
                result['autorun_status'] = 0
                result["message"] = f"Action Error: {action_err.decode('utf-8')}"
        except Exception as e:
            print(f"Exception during autorun: {str(e)}")
            result['action_status'] = 0
            result['autorun_status'] = 0
            result["message"] = f"Exception during autorun: {str(e)}"
            return result

        return result

    def checkDetailService(nama):
        detail = subprocess.Popen(f"systemctl status {nama} | grep since", shell=True, stdout=subprocess.PIPE)
        out, err = detail.communicate()
        detail = out.decode('utf-8').replace('\n', '')
        
        search1 = detail.find("since")
        search2 = detail.find("WIB")
        search3 = detail.find("ago")
        
        last_run = detail[search1 + 6:search2 - 1]
        since = detail[search2 + 5:search3]
        
        return last_run, since


    def checkActiveService(nama):
        active = subprocess.Popen(["systemctl", "is-active", nama], stdout=subprocess.PIPE)
        out, err = active.communicate()
        active = out.decode('utf-8').replace('\n', '')
        return active


    def checkEnableService(nama):
        enable = subprocess.Popen(["systemctl", "is-enabled", nama], stdout=subprocess.PIPE)
        outs, errs = enable.communicate()
        enable = outs.decode('utf-8').replace('\n', '')
        return enable

    def restartService(nama):
      try:
         subprocess.run(["sudo", "systemctl", "restart", nama], check=True)
         return f"Service '{nama}' restarted successfully."
      except subprocess.CalledProcessError as e:
         return f"Failed to start service '{nama}': {e}"
    
    def restartNetworkService():
        services = SystemServiceDB.select()
        if len(services) > 0:
            for num in range(len(services)):
                serviceName = services[num]['name']
                if 'routine' in serviceName or 'buffer' in serviceName or 'alarm' in serviceName or 'sync' in serviceName or 'notif' in serviceName:
                    restart = ServiceProjectFunction.restartService(serviceName)


    def getServiceInfo(serviceName):
        """Get Service State
        Return serviceStatus, serviceState, and serviceLastUpdated
        """
        getData = SystemServiceDB.selectByName(serviceName)
        serviceData = {}

        if len(getData) > 0:
            newData = getData[0]
            serviceData.update({'state': newData['service']})
            serviceData.update({'log': newData['state']})
            serviceData.update({'last_update': newData['last_update']})
        else:
            serviceData.update({'state': ServiceProjectFunction.checkActiveService(serviceName)})
            serviceData.update({'log': '-'})
            serviceData.update({'last_update': '-'})
        return serviceData


    def handlingServiceError(name, error, global_variable):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        error_details = {
            'service': name,
            'filename': str(exc_traceback.tb_frame.f_code.co_filename),
            'line': str(exc_traceback.tb_lineno),
            'type': str(exc_type.__name__),
            'message': str(error)
        }
        
        message = f"{error_details['type']} ({error_details['message']})"
        timestamp = datetime.datetime.now()
        
        LogErrorDB.insert(error_details['service'], message, error_details['filename'], error_details['line'], timestamp)
        SystemServiceDB.updateStatusByName(f"Service Error - {message}", timestamp, global_variable["serviceName"])
        
        feature_setting = dbFunction.getFeatureSetting()
        if int(feature_setting['notification']) == 1:
            notificationFunction.generateNotificationNode("Service Error", error_details, feature_setting)
        
        global_variable["logger"].debug(f"Error : \033[31m{error_details}\033[00m")
        time.sleep(10)
    

