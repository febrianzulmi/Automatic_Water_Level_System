import requests, json, datetime, mysql.connector, statistics, time
import paho.mqtt.client as mqttClient
from threading import Thread
from collections import defaultdict

class packData():
    def userPack(user=None, password=None):
        pack = {"firmware_user":user,"firmware_password":password}
        return pack
        
    def dataPack(node_id=None, id=None, value=None, size=None, timestamp=None, state=None):
        pack = {}
        pack['node_id'] = node_id
        sensor = {}
        for i in range(size):
            sensor[str(id[i])] = str(value[i])
        pack['data'] = sensor
        if timestamp != None:
           pack['timestamp'] = str(timestamp)
        if state != None:
           pack['status'] = str(state) 
        return pack

    def sensorPack(id=None, value=None, size=None):
        sensor = {}
        for i in range(size):
            sensor[str(id[i])] = str(value[i])
        return sensor

class http():
    def auth(url=None, user=None, timeout=None):
        headers = {"content-type": "application/json"}
        try:
            user = json.dumps(user)
            result = requests.post(url=url, data=user, headers=headers, timeout=timeout)
            statusCode = result.status_code
            payload = result
            if statusCode == 200:
               dataAuth = result.headers
               dataCookie = dataAuth['Set-Cookie']
               dataCookie = dataCookie.split(';')
               token, expire = "", ""
               for x in dataCookie:
                   if "token" in  x: token = x.replace('token=','')
                   elif "Expires" in x: expire = x.replace(' Expires=','')
                   elif "expires" in x: expire = x.replace(' expires=','')
            else:
               token, expire = 'N/A', 'N/A'
        except Exception as e:
            statusCode, token, expire, payload = 444, 'N/A', 'N/A', str(e)
        resultData = {'state': statusCode, 'token': token, 'expire': expire, 'payload': payload}   
        return resultData
    
    def get(url=None, data=None, token=None, timeout=None):
        try:
            token = "token=" + str(token)
            headers = {"Cookie": token, "content-type": "application/json"}
            send = requests.get(url=url, headers=headers, timeout=timeout)
            payload = send
            statusCode = send.status_code
            message = ""
        except Exception as e:
            statusCode, payload, message = 444, {}, str(e)
        resultData = {'state': statusCode, 'payload': payload, "message": message}  
        return resultData
    
    def put(url=None, data=None, token=None, timeout=None):
        try:
           token = "token=" + str(token)
           headers = {"Cookie": token, "content-type": "application/json"}
           data = json.dumps(data)
           send = requests.put(url, data=data, headers=headers, timeout=timeout)
           payload = send
           statusCode = send.status_code
           message = ""
        except Exception as e:
           statusCode, payload, message = 444, {}, str(e)
        resultData = {'state': statusCode, 'payload': payload, "message": message}  
        return resultData

    def post(url=None, data=None, token=None, timeout=None):
        try:
           token = "token=" + str(token)
           headers = {"Cookie": token, "content-type": "application/json"}
           data = json.dumps(data)
           send = requests.post(url, data=data, headers=headers, timeout=timeout)
           payload = send
           statusCode = send.status_code
           message = ""
        except Exception as e:
           statusCode = 444
           statusCode, payload, message = 444, {}, str(e)
        resultData = {'state': statusCode, 'payload': payload, "message": message}  
        return resultData

connectionState = None
connectionCode = None
message = []
topics = None
check = None
logging = None
class mqtt():
    def on_connect(client, userdata, flags, rc):
        global connectionState, connectionCode
        if rc == 0:
           connectionState, connectionCode = True, rc
        else:
           connectionState, connectionCode = False, rc

    def on_disconnect(client, userdata, rc):
        global connectionState, connectionCode
        connectionState, connectionCode = False, rc

    def on_log(client, userdata, level, buf):
        global logging
        now = times.getDatetime()
        logging = now + " : " + buf

    def on_message(client, userdata, msg):
        global message
        now = times.getDatetime()
        messages = str(msg.payload.decode("utf-8"))
        messages = {'time':now, 'msg':messages, 'topic':str(msg.topic)}
        message.append(messages)
    
    def connect(broker=None, port=None, node_id=None, key=None, alive=None, timeout=None):
        global connectionState, connectionCode
        count = 0
        error = None
        client = mqttClient.Client()
        client.on_connect = mqtt.on_connect
        client.on_disconnect = mqtt.on_disconnect
        client.on_log = mqtt.on_log
        if alive == None:
           alive = 60
        try:
            client.username_pw_set(str(node_id), password=key)
            connectionCode = client.connect(broker, int(port), alive)
            client.loop_start()
        except Exception as e:
            client, error, connectionCode = None, e, -1
        if timeout == None:
           timeout = 10
        while count <= timeout:
            if connectionState != True:
               time.sleep(1)
            count += 1
        if error is not None:
           print("Connection Error : ", error) 
        return {"client": client, "state": connectionState, "code": connectionCode, "error": error}
    
    def publishMessage(client=None, topic=None, data=None, qos=None):
        try:
            data = json.dumps(data)
            publish = client.publish(topic, payload=data, qos=qos)
            return {"publishCode": int(publish.rc), "publishId": publish.mid, "errorMessage": None}
        except Exception as e:
            publish = None
            return {"publishCode": -1, "publishId": -1, "errorMessage": str(e)}

    def subscribeMessage(client=None, topic=None):
        try:
            subscribe = client.subscribe(topic)
            client.on_message = mqtt.on_message
            return {"mqttCode": subscribe[0], "mqttId": subscribe[1], "errorMessage": None}
        except Exception as e:
            subscribe = None
            return {"mqttCode": -1, "mqttId": -1, "errorMessage": str(e)}

    def unsubscribeMessage(client=None, topic=None):
        global message
        try:
            unsubscribe = client.unsubscribe(topic)
            message = []
            return {"mqttCode": unsubscribe[0], "mqttId": unsubscribe[1], "errorMessage": None}
        except Exception as e:
            unsubscribe = None
            return {"mqttCode": -1, "mqttId": -1, "errorMessage": str(e)}
        
    def receiveMessage():
        global message
        messages = message
        message = []
        return messages

    def checkConnection():
        global state
        return state
        
    def disconnect(client=None):
        try:
            disconnect = client.disconnect()
            return {"disconnectCode": disconnect, "errorMessage": None}
        except Exception as e:
            disconnect = None
            return {"disconnectCode": -1, "errorMessage": str(e)}
        
class times():
    def now():
        datenow = datetime.datetime.now()
        return datenow
    
    def getDatetime():
        datenow = times.now()
        datenow = datenow.strftime("%Y-%m-%d %H:%M:%S")
        return datenow

    def parseTime(datetimes):
        if datetimes == str:
           datetimes = times.convertStringToTime(datetimes)
        parseData = {'hour':datetimes.hour, 'minute':datetimes.minute, 'second':datetimes.second}
        return parseData
    
    def convertStringToTime(datetimes):
        datetimesTime = datetime.datetime.strptime(datetimes, "%Y-%m-%d %H:%M:%S")
        return datetimesTime
    
    def convertTimeToString(datetimes):
        datetimesString = datetimes.strftime("%Y-%m-%d %H:%M:%S")
        return datetimesString
        
    def convertToUTC(datetimes):
        if type(datetimes) == str:
           datetimes = times.convertStringToTime(datetimes)
        datetimesUTC = datetimes - datetime.timedelta(hours=7)   
        return datetimesUTC

class Scheduler():
    def check(interval_data, function, args=(), thread=False):
        if not isinstance(interval_data, list):
           interval_data = [interval_data]
        current_time = time.time()
        next_execution_times = []
        for interval in interval_data:
            if int(interval) == 0:
                next_execution_time = current_time
            else:
                next_execution_time = current_time + (int(interval) - current_time % int(interval))
            next_execution_times.append(next_execution_time )
        same_schedule_positions = Scheduler.find_same_schedule(next_execution_times)
        next_execution_time = min(next_execution_times)
        index = next_execution_times.index(next_execution_time)        
        sleep_time = max(0, next_execution_time - current_time)
        time.sleep(sleep_time)          
        if index not in same_schedule_positions:
            if thread == False:
                function(index, *args)
            else: 
                # run function as thread
                ThreadWithReturnValues(target=function, args=(index, *args)).start()
        else:
            if len(same_schedule_positions) > 0:
                for num in same_schedule_positions:
                    if thread == False: 
                        function(index, *args)
                    else: 
                        # run function as thread
                        ThreadWithReturnValues(target=function, args=(num, *args)).start() 

    def find_same_schedule(data):
        index_dict = defaultdict(list)
        for index, value in enumerate(data):
            index_dict[value].append(index)     
        same_schedule_positions = [indexes for indexes in index_dict.values() if len(indexes) > 1]
        if len(same_schedule_positions) > 0:
            same_schedule_positions = same_schedule_positions[0]
        return same_schedule_positions

class ThreadWithReturnValues(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    
    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)
    
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

class trigger():
    def schedule(time1=None,time2=None,interval=None,frekuensi=None):
        sample = interval/frekuensi
        if time2%interval == 0:
           if time2 - time1 == interval:
              state = 1
              state2 = 1
              time = time2
              return state, state2, time
           else:
              state = 1
              state2 = 1
              time = time2-interval
              return state, state2, time
        else:
           if ((time2-time1)%sample) == 0:
              if time2-time1 != 0:
                 state = 0
                 state2 = 1
                 time = time1
                 return state, state2, time
              else: 
                 state = 0
                 state2 = 0
                 time = time1
                 return state, state2, time
           else:
              state = 0
              state2 = 0
              time = time1
              return state, state2, time
            
    def check2(interval=None,tipe=None,waktu=None,state=None):
        nows = times.now()
        dates = nows.strftime("%Y-%m-%d %H:%M:%S")
        if tipe == 0:
           nows = nows.second
        elif tipe == 1:
           nows = nows.minute
        elif tipe == 2:
           nows = nows.hour
        if waktu != nows:
           waktu = nows
           state = 0
        flag = nows % interval
        if flag == 0:
           if state == 0:
              state = 1
        return state, waktu, dates 

class math():
    def average(sensor, sensors, frekuensi):
        if type(sensor) == list:
           rates = []
           for i in range(len(sensor)):
               sensors[i] += sensor[i]
               rates[i] = rates.append(0)
               rates[i] = sensors[i] / frekuensi
               rates[i] = round(rates[i],2)
        else:
           sensors += sensor
           rates = sensors / frekuensi
           rates = round(rates,2)
        return sensors, rates

    def modeBoolean(sensors,sensor):
        if type(sensors) == list:
           if len(sensor) == 0:
              for i in range(len(sensors)):
                  sensor.append([])
           for i in range(len(sensors)):
               sensor[i].append(sensors[i])
        else:
           sensor.append(sensors)
        sensor, modes = math.mode(sensor)
        return sensor, modes

    def mode(sensors):
        if type(sensors) == list:
           modes = []
           for i in range(len(sensors)):
               try:
                   modus = statistics.mode(sensors[i])
                   modes.append(modus)
               except:
                   modes.append(None)
        else:
           try:
               modes = 0
               modes = statistics.mode(sensors)
           except:
               modes = None 
        return sensors, modes

    def reset(sensors):
        if type(sensors) == list:
           for i in range(len(sensors)):
               sensors[i] = 0
        else:
           sensors = 0
        return sensors

    def resetBoolean(sensors):
        if type(sensors) == list:
           for i in range(len(sensors)):
               sensors[i] = []
        else:
           sensors = []
        return sensors

class sql():
    def connect(host=None, database=None, username=None, password=None):
        connection = mysql.connector.connect (
                host=host,
                database=database,
                user=username,
                password=password,
            )
        return connection

    def cursor(connect):
        return connect.cursor()

    def close(connection):
        connection.commit()
        connection.close()

    # def selectNoInput(connection=None, query=None):
    #     try:
    #         cursor = sql.cursor(connection)
    #         cursor.execute(query)
    #         fetchall = cursor.fetchall()
    #         cursor.close()
    #         sql.close(connection)
    #         return fetchall
    #     except Exception as e:
    #         print(e)
    #         return []
    
    def selectNoInput(connection=None, query=None):
        try:
            cursor = sql.cursor(connection)
            cursor.execute(query)
            fetchall = cursor.fetchall()
            columns = cursor.description
            result = []
            for value in fetchall:
                tmp = {}
                for (index,column) in enumerate(value):
                    tmp[columns[index][0]] = column
                result.append(tmp)
            fetchall = result
            cursor.close()
            sql.close(connection)
            return fetchall
        except Exception as e:
            print(e)
            return []

    # def selectWithInput(connection=None, query=None, value=None):
    #     try:
    #         cursor = sql.cursor(connection)
    #         cursor.execute(query, value)
    #         fetchall = cursor.fetchall()
    #         cursor.close()
    #         sql.close(connection)
    #         return fetchall
    #     except Exception as e:
    #         print(e)
    #         return []
    
    def selectWithInput(connection=None, query=None, value=None):
        try:
            cursor = sql.cursor(connection)
            cursor.execute(query, value)
            fetchall = cursor.fetchall()
            columns = cursor.description
            result = []
            for value in fetchall:
                tmp = {}
                for (index,column) in enumerate(value):
                    tmp[columns[index][0]] = column
                result.append(tmp)
            fetchall = result
            cursor.close()
            sql.close(connection)
            return fetchall
        except Exception as e:
            print(e)
            return []

    def execute(connection=None, query=None, value=None):
        try:
            cursor = sql.cursor(connection)
            cursor.execute(query, value)
            cursor.close()
            sql.close(connection)
            return '1'
        except Exception as e:
            print(e)
            return '0'
            
    def executeOnly(connection=None, query=None):
        try:
            cursor = sql.cursor(connection)
            cursor.execute(query)
            cursor.close()
            sql.close(connection)
            return '1'
        except Exception as e:
            print(e)
            return '0'
    
    def executeMany(connection=None, query=None, values=None):
        try:
            cursor = sql.cursor(connection)
            cursor.executemany(query, values)
            connection.commit()
            cursor.close()
            sql.close(connection)
            return '1'  # Success
        except Exception as e:
            print(f"Error in executemany: {e}")
            connection.rollback()
            return '0'  # Failure

