import json, sys
from flask import Flask, request, jsonify
sys.path.append('../database')
from sql import *
from function import getGatewayHTTP, getSetting, getURL, checkURL

port = getGatewayHTTP()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gateway'

@app.route('/api/data', methods=['POST'])
def api_data():
    ### GET DEVICE DATA ###
    id_device, name, ip, port, key, token = getSetting()
    url_data = getURL(ip, port, "data")
    check_data = checkURL(url_data)
    #######################
    ### RETRIEVE API DATA ###
    data = request.get_json()                                 
    node_id = data['node_id']
    sensor = data['data']
    if 'date_time' in data:
        timestamp = data['date_time']
    else:
        timestamp = times.getDatetime()
        data['date_time'] = timestamp
    #########################    
    ### PROCESS TO PLATFORM ###
    sensor_pack = json.dumps(sensor)
    if token == 0 or token == "" or token == None:
       state = 410
       buffer = 0
       messages = {'message': 'Gateway Token Undefined'}    
    else:
       if check_data == 0:
          state = 420
          buffer = 0
          messages = {'message': 'Gateway URL Undefined'} 
       else:       
          status, payload = http.postHTTP(url_data, data, token)
          if status == 200:
             payload = json.loads(payload)
             message = payload['message']
             if message == 'Data created successfully!':
                buffer = 1
                state = status
             else:
                buffer = 1
                state = 400
             messages = {'message': message}
          else:
             buffer = 0
             state = status
             messages = {'message': 'Gateway Send Error'}
    if buffer == 0:
       logging = logBufferGateway.insert(node_id,sensor_pack,timestamp) 
    logging = logSendGateway.insert(node_id,sensor_pack,state,buffer,timestamp)
    ###########################
    messages = json.dumps(messages)
    return messages, 200   

@app.errorhandler(Exception)
def handle_exception(e):
    try:
      datas = request.get_json()
      datas = json.dumps(datas)
    except:
      datas = ' '
    timestamp = times.getDatetime()
    error = e
    logging = logError.insert(datas, str(error), timestamp)
    return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)