from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, make_response
import json, os, sys, subprocess, psutil, socket, shutil, requests, io
import pyexcel as pe
import pandas as pd
sys.path.append('../database')
from sql import *
from function import *

project_name, project_port, project_gateway, project_node, project_protocol = getData()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'project'

@app.route('/get/time')
def get_time():
    datetime = times.now()
    day = int(datetime.strftime("%w"))
    month = int(datetime.strftime("%m"))
    hari = ['Minggu','Senin','Selasa','Rabu','Kamis','Jum\'at','Sabtu']
    bulan = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
    datetime = datetime.strftime(hari[day] + ", %d " + bulan[month-1] + " %Y %H:%M:%S")
    return datetime

@app.route('/')
def index():
    rule = str(request.url_rule)
    id, username, state, level = checkSession()
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    node_id, name, ip, port, key, token = getSetting()
    sensors = sensor.select()
    sensor_data = logSensor.selectAll()
    buffer_node = logBufferNode.selectAll()
    send_node = logSendNode.selectAll()
    last_data= []
    if len(sensors) > 0:
       for i in range(len(sensors)):
           data = logSensor.selectLastOne(sensors[i][0])
           data2 = logSensor.selectOne(sensors[i][0])
           if len(data) > 0:
              for x in range(len(data)):
                  value = data[x][2]
                  timestamp = data[x][3]
              datas = (len(data2),value,timestamp)
              last_data.append(datas)
           else:
              datas = (len(data2),'-','-')
              last_data.append(datas)
    nodes = logSendGateway.selectNode()
    errors = logError.selectAll()
    send_gateway = logSendGateway.selectAll()
    buffer_gateway = logBufferGateway.selectAll()
    node_data = []
    if len(nodes) > 0:
       for i in range(len(nodes)):
           send = logSendGateway.selectByNode(nodes[i][0])
           buffer = logBufferGateway.selectByNode(nodes[i][0])
           datas = (nodes[i][0],len(send),len(buffer))
           node_data.append(datas)
    return render_template('index.html', project_port=project_port, project_name=project_name, project_gateway=project_gateway, project_node=project_node, project_protocol=project_protocol, rule=rule, node_id=node_id, name=name, key=key, token=token, sensors=sensors, sensor_data=sensor_data, buffer_node=buffer_node, send_node=send_node, last_data=last_data, node_data=node_data, send_gateway=send_gateway, buffer_gateway=buffer_gateway, errors=errors, nodes=nodes, state=state, username=username)

@app.route('/login')
def login():
    id, username, state, level = checkSession()
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    rule = str(request.url_rule)
    return render_template('login.html', project_port=project_port, project_name=project_name, project_gateway=project_gateway,
                           project_node=project_node, project_protocol=project_protocol, rule=rule, state=state, username=username)

@app.route('/login', methods=['POST'])
def login_post():
    username2 = request.form.get('username')
    password2 = request.form.get('password')
    flag = request.form.get('flag')
    port = getPort()
    data = {"username":username2,"password":password2,"flag":flag}
    try:
       login = requests.post('http://localhost:' + port + '/api/project/login', data=data)
       check = login.text
    except Exception as e:
       check = 0
    if check == "2":
       return redirect(url_for('index'))
    elif check == "1":
       flash('Wrong Password. Please Check Your Login and Try Again')
       return redirect(url_for('login'))
    else:
       flash('Wrong Username. Please Check Your Login and Try Again')
       return redirect(url_for('login'))

@app.route('/logout')
def logout():
    id, username, state, level = checkSession()
    port = getPort()
    data = {"id":id}
    try:
       logout = requests.post('http://localhost:' + port + '/api/project/logout', data=data)
    except:
       pass
    return redirect(url_for('index'))

@app.route('/setting')
def setting_form():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    node_id, name, ip, port, key, token = getSetting()
    attribute = attributes.select()
    sensors = sensor.select()
    group = groups.select()
    param = params.select()
    gateways = gateway.select()
    if len(gateways) == 0:
       gateway_value = ''
    else:
       for i in gateways:
           gateway_value = i[1]
    interval = intervals.select()
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('setting.html', project_port=project_port, project_name=project_name, project_gateway=project_gateway, project_node=project_node, node_id=node_id, name=name, ip=ip, port=port, key=key, token=token, attribute=attribute, sensors=sensors, gateway_value=gateway_value, interval=interval,group=group,param=param, project_protocol=project_protocol, rule=rule, state=state, username=username)

@app.route('/setting_post', methods=['POST'])
def setting_post():
    node_id = request.form.get('node_id')
    name = request.form.get('name')
    ip = request.form.get('ip')
    port = request.form.get('port')
    key = request.form.get('key')
    fetch = setting.select()
    if node_id == '':
       node_id = 0
    if len(fetch) == 0:
       inserts = setting.insert(node_id,name,ip,port,key)
    else:
       updates = setting.update(node_id,name,ip,port,key)
    return redirect(url_for('setting_form'))

@app.route('/token/reset')
def token_reset():
    update =  setting.updateToken('')
    return redirect(url_for('setting_form'))

@app.route('/token/get')
def token_get():
    fetch = setting.select()
    for i in fetch:
        node_id = i[1]
        ip = i[3]
        port = i[4]
        key = i[5]
    cek = attributes.selectOne("auth")
    if len(cek) > 0:
       for i in cek:
           param = i[2]
           link = 'http://'+ip+':'+port+param
           print('URL : ',link)
           user = packData.userPack(node_id, key)
           auth = http.getToken(link, user)
           if auth != 'Failed Get Token':
              update =  setting.updateToken(auth)
    return redirect(url_for('setting_form'))

@app.route('/attribute_post', methods=['POST'])
def attribute_post():
    name = request.form.get('name')
    value = request.form.get('value')
    inserts = attributes.insert(name,value)
    return redirect(url_for('setting_form'))

@app.route('/attribute_update/<id>', methods=['POST'])
def attribute_update(id):
    name = request.form.get('name')
    value = request.form.get('value')
    updates = attributes.update(name,value,id)
    return redirect(url_for('setting_form'))

@app.route('/attribute_delete/<id>')
def attribute_delete(id):
    deletes = attributes.deleteOne(id)
    return redirect(url_for('setting_form'))

@app.route('/interval/add', methods=['POST'])
def interval_post():
    name = request.form.get('name')
    interval = request.form.get('interval')
    unit = request.form.get('unit')
    inserts = intervals.insert(name,interval,unit)
    return redirect(url_for('setting_form'))

@app.route('/interval/update/<id>', methods=['POST'])
def interval_update(id):
    name = request.form.get('name')
    interval = request.form.get('interval')
    unit = request.form.get('unit')
    updates = intervals.update(name,interval,unit,id)
    return redirect(url_for('setting_form'))

@app.route('/interval/delete/<id>')
def interval_delete(id):
    deletes = intervals.deleteOne(id)
    return redirect(url_for('setting_form'))

@app.route('/gateway/add', methods=['POST'])
def gateway_post():
    value = request.form.get('value')
    gateways = gateway.select()
    if len(gateways) == 0:
       inserts = gateway.insert(value)
    else:
       updates = gateway.update(value)
    return redirect(url_for('setting_form'))

@app.route('/sensor/add', methods=['POST'])
def sensor_post():
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    sensor_id = request.form.get('sensor_id')
    name = request.form.get('name')
    group_id = request.form.get('group_id')
    inserts = sensor.insert(sensor_id,group_id,name)
    if int(project_protocol) == 3:
       createOID()
    return redirect(url_for('setting_form'))

@app.route('/sensor/update/<id>', methods=['POST'])
def sensor_update(id):
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    sensor_id = request.form.get('sensor_id')
    name = request.form.get('name')
    group_id = request.form.get('group_id')
    if int(project_protocol) == 3:
       sensors  = sensor.select()
       base_oid = getOID('base')
       if len(sensors) > 0:
          for i in range(len(sensors)):
              last_id = sensors[i][1]
              oid = base_oid + "." + str(last_id)
              os.system("sudo rm /tmp/" + oid)
    updates = sensor.update(sensor_id,group_id,name,id)
    if int(project_protocol) == 3:
       createOID()
    return redirect(url_for('setting_form'))

@app.route('/sensor/delete/<id>')
def sensor_delete(id):
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    deletes = sensor.deleteOne(id)
    if int(project_protocol) == 3:
       createOID()
    return redirect(url_for('setting_form'))

@app.route('/param/add', methods=['POST'])
def param_post():
    group_id = request.form.get('group_id')
    name = request.form.get('name')
    param = request.form.get('param')
    inserts = params.insert(group_id,name,param)
    return redirect(url_for('setting_form'))

@app.route('/param/update/<id>', methods=['POST'])
def param_update(id):
    group_id = request.form.get('group_id')
    name = request.form.get('name')
    param = request.form.get('param')
    updates = params.update(group_id,name,param,id)
    return redirect(url_for('setting_form'))

@app.route('/param/delete/<id>')
def param_delete(id):
    deletes = params.deleteOne(id)
    return redirect(url_for('setting_form'))

@app.route('/group/add', methods=['POST'])
def group_post():
    base = "/home/connex/"
    name = request.form.get('name')
    interval = request.form.get('interval')
    unit = request.form.get('unit')
    frekuensi = request.form.get('frekuensi')
    inserts = groups.insert(name,interval,unit,frekuensi,0)
    select = groups.selectByName(name)
    for i in range(len(select)):
        group_id = select[i][0]
    filename1 = "sensor" + str(group_id)
    filename2 = "check_sensor" + str(group_id)
    def file_read(source):
        f = open(source, 'r')
        data = f.readlines()
        f.close()
        return data
    def file_write(source, data):
        f = open(source, 'w')
        f.writelines(data)
        f.close()
    data = file_read(base + 'platform/storage/service.master')
    command = "/usr/bin/python " + filename1 + ".py"
    path = base + "project/sensor/"
    data[5] = "ExecStart={}\n".format(command)
    data[6] = "WorkingDirectory={}\n".format(path)
    file_write('/lib/systemd/system/' + filename1 + '.service', data)
    port = getPort()
    url = "http://localhost:" + port
    data = {"name":filename1, "path":path, "command":command}
    send = requests.post(url + "/api/service", data=data)
    fetch = requests.get(url + "/api/service/" + filename1)
    fetch = fetch.text
    fetch = json.loads(fetch)
    service_id = fetch['id']
    updates = groups.update(name,interval,unit,frekuensi,service_id,group_id)
    filesensor1 = base + 'project/sensor/sensor' + str(group_id) + '.py'
    filesensor2 = base + 'project/sensor/check_sensor' + str(group_id) + '.py'
    shutil.copy(base + "platform/storage/sensor/sensor.py", filesensor1)
    shutil.copy(base + "platform/storage/sensor/check_sensor.py", filesensor2)
    data1 = file_read(filesensor1)
    data1[0] = 'group_id = ' + str(group_id) + '\n'
    file_write(filesensor1, data1)
    data2 = file_read(filesensor2)
    data2[0] = 'group_id = ' + str(group_id) + '\n'
    file_write(filesensor2, data2)
    return redirect(url_for('setting_form'))

@app.route('/group/update/<id>', methods=['POST'])
def group_update(id):
    name = request.form.get('name')
    interval = request.form.get('interval')
    unit = request.form.get('unit')
    frekuensi = request.form.get('frekuensi')
    service_id = request.form.get('service_id')
    updates = groups.update(name,interval,unit,frekuensi,service_id,id)
    return redirect(url_for('setting_form'))

@app.route('/group/delete/<id>')
def group_delete(id):
    base = "/home/connex/"
    fetch = groups.selectOne(id)
    for i in fetch:
        service_id = i[5]
    port = getPort()
    url = "http://localhost:" + port
    fetch = requests.get(url + "/api/service/delete/" + str(service_id))
    deletes = groups.deleteOne(id)
    os.system("sudo rm " + base + "project/node/sensor" + id + ".py")
    os.system("sudo rm " + base + "project/node/check_sensor" + id + ".py")
    os.system("sudo systemctl stop sensor" + id)
    os.system("sudo rm " + base + "/lib/systemd/system/sensor" + id + ".service")
    os.system("sudo systemctl daemon-reload")
    return redirect(url_for('setting_form'))

@app.route('/log/send_node', methods=['GET','POST'])
def log_send_node():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if datetime1 == ' ' and datetime2 == ' ':
       fetch = logSendNode.selectAll()
    else:
       fetch = logSendNode.selectByTime(datetime1,datetime2)
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_sendNode.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2, project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node, state=state, username=username)

@app.route('/log/send_node/update/<id>', methods=['POST'])
def log_send_node_update(id):
    data = request.form.get('data')
    state = request.form.get('state')
    buffer = request.form.get('buffer')
    timestamp = request.form.get('timestamp')
    updates = logSendNode.updateAll(data,state,buffer,timestamp,id)
    return redirect(url_for('log_send_node'))

@app.route('/log/send_node/delete', methods=['POST'])
def log_send_node_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    if datetime1 == ' ' and datetime2 == ' ':
       deletes = logSendNode.deleteAll()
    else:
       deletes = logSendNode.deleteByTime(datetime1,datetime2)
    return redirect(url_for('log_send_node'))

@app.route('/log/send_node/delete/<id>')
def log_send_node_delete(id):
    delete = logSendNode.deleteOne(id)
    return redirect(url_for('log_send_node'))

@app.route('/log/send_node/download', methods=['POST'])
def log_send_node_download():
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    if datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logSendNode.selectAll()
    else:
       fetch = logSendNode.selectByTime(datetimes1,datetimes2)
    datas = []
    header = ['data','state','buffer','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        data.append(json.loads(fetch[row][1]))
        data.append(fetch[row][2])
        if int(fetch[row][3]) == 0:
           buffer = "Yes"
        elif int(fetch[row][3]) == 1:
           buffer = "No"
        else:
           buffer = "Done"
        data.append(buffer)
        data.append(fetch[row][4])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    node_id, name, ip, port, key, token = getSetting()
    filename = "Log_Send (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/send_node/upload', methods=['POST'])
def log_send_node_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        datas = data['data'][row]
        datas = datas.replace("'","\"")
        buffer = data['buffer'][row]
        state = data['state'][row]
        state = int(state)
        if buffer == 'Yes':
           buffer = 0
        elif buffer == 'No':
           buffer = 1
        else:
           buffer = 2
        timestamp = data['timestamp'][row]
        inserts = logSendNode.insert(datas,state,buffer,timestamp)
    return redirect(url_for('log_send_node'))

@app.route('/log/send_gateway', methods=['GET','POST'])
def log_send_gateway():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    node_id = ''
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
       node_id = request.form.get('node_id')
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if node_id == '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logSendGateway.selectAll()
    elif node_id != '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logSendGateway.selectByNode(node_id)
    else:
       fetch = logSendGateway.selectByTime(node_id,datetime1,datetime2)
    fetch2 = logSendGateway.selectNode()
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_sendGateway.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2, fetch2=fetch2, node_id=node_id,
                           project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node
                           , state=state, username=username)

@app.route('/log/send_gateway/update/<id>', methods=['POST'])
def log_send_gateway_update(id):
    node_id = request.form.get('node_id')
    data = request.form.get('data')
    state = request.form.get('state')
    buffer = request.form.get('buffer')
    timestamp = request.form.get('timestamp')
    updates = logSendGateway.updateAll(node_id,data,state,buffer,timestamp,id)
    return redirect(url_for('log_send_gateway'))

@app.route('/log/send_gateway/delete', methods=['POST'])
def log_send_gateway_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    node_id = request.form.get('node_id')
    if node_id == '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logSendGateway.deleteAll()
    elif node_id != '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logSendGateway.deleteByNode(node_id)
    else:
       deletes = logSendGateway.deleteByTime(node_id,datetime1,datetime2)
    return redirect(url_for('log_send_gateway'))

@app.route('/log/send_gateway/delete/<id>')
def log_send_gateway_delete(id):
    delete = logSendGateway.deleteOne(id)
    return redirect(url_for('log_send_gateway'))

@app.route('/log/send_gateway/download', methods=['POST'])
def log_send_gateway_download():
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    node_id = request.form.get('node_id')
    if node_id == '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logSendGateway.selectAll()
    elif node_id != '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logSendGateway.selectByNode(node_id)
    else:
       fetch = logSendGateway.selectByTime(node_id,datetimes1,datetimes2)
    datas = []
    header = ['node_id','data','state','buffer','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        data.append(fetch[row][1])
        data.append(json.loads(fetch[row][2]))
        data.append(fetch[row][3])
        if int(fetch[row][4]) == 0:
           buffer = "Yes"
        elif int(fetch[row][4]) == 1:
           buffer = "No"
        else:
           buffer = "Done"
        data.append(buffer)
        data.append(fetch[row][5])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    node_id, name, ip, port, key, token = getSetting()
    filename = "Log_Send (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/send_gateway/upload', methods=['POST'])
def log_send_gateway_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        node_id = data['node_id'][row]
        node_id = int(node_id)
        sensor = data['data'][row]
        sensor = sensor.replace("'","\"")
        buffer = data['buffer'][row]
        state = data['state'][row]
        state = int(state)
        if buffer == 'Yes':
           buffer = 0
        elif buffer == 'No':
           buffer = 1
        else:
           buffer = 2
        timestamp = data['timestamp'][row]
        inserts = logSendGateway.insert(node_id,sensor,state,buffer,timestamp)
    return redirect(url_for('log_send_gateway'))

@app.route('/log/buffer_node', methods=['GET','POST'])
def log_buffer_node():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if datetime1 == ' ' and datetime2 == ' ':
       fetch = logBufferNode.selectAll()
    else:
       fetch = logBufferNode.selectByTime(datetime1,datetime2)
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_bufferNode.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2,
                           project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node
                           , state=state, username=username)

@app.route('/log/buffer_node/update/<id>', methods=['POST'])
def log_buffer_node_update(id):
    data = request.form.get('data')
    timestamp = request.form.get('timestamp')
    updates = logBufferNode.updateAll(data,timestamp,id)
    return redirect(url_for('log_buffer_node'))

@app.route('/log/buffer_node/delete', methods=['POST'])
def log_buffer_node_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    if datetime1 == ' ' and datetime2 == ' ':
       deletes = logBufferNode.deleteAll()
    else:
       deletes = logBufferNode.deleteByTime(datetime1,datetime2)
    return redirect(url_for('log_buffer_node'))

@app.route('/log/buffer_node/delete/<id>')
def log_buffer_node_delete(id):
    delete = logBufferNode.deleteOne(id)
    return redirect(url_for('log_buffer_node'))

@app.route('/log/buffer_node/download', methods=['POST'])
def log_buffer_node_download():
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    if datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logBufferNode.selectAll()
    else:
       fetch = logBufferNode.selectByTime(datetimes1,datetimes2)
    datas = []
    header = ['data','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        data.append(json.loads(fetch[row][1]))
        data.append(fetch[row][2])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    node_id, name, ip, port, key, token = getSetting()
    filename = "Log_Buffer (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/buffer_node/upload', methods=['POST'])
def log_buffer_node_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        datas = data['data'][row]
        datas = datas.replace("'","\"")
        timestamp = data['timestamp'][row]
        inserts = logBufferNode.insert(datas,timestamp)
    return redirect(url_for('log_buffer_node'))

@app.route('/log/buffer_gateway', methods=['GET','POST'])
def log_buffer_gateway():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    node_id = ''
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
       node_id = request.form.get('node_id')
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if node_id == '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logBufferGateway.selectAll()
    elif node_id != '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logBufferGateway.selectByNode(node_id)
    else:
       fetch = logBufferGateway.selectByTime(node_id,datetime1,datetime2)
    fetch2 = logBufferGateway.selectNode()
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_bufferGateway.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2, fetch2=fetch2, node_id=node_id,
                           project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node
                           , state=state, username=username)

@app.route('/log/buffer_gateway/update/<id>', methods=['POST'])
def log_buffer_gateway_update(id):
    node_id = request.form.get('node_id')
    data = request.form.get('data')
    timestamp = request.form.get('timestamp')
    updates = logBufferGateway.updateAll(node_id,data,timestamp,id)
    return redirect(url_for('log_buffer_gateway'))

@app.route('/log/buffer_gateway/delete', methods=['POST'])
def log_buffer_gateway_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    node_id = request.form.get('node_id')
    if node_id == '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logBufferGateway.deleteAll()
    elif node_id != '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logBufferGateway.deleteByNode(node_id)
    else:
       deletes = logBufferGateway.deleteByTime(node_id,datetime1,datetime2)
    return redirect(url_for('log_buffer_gateway'))

@app.route('/log/buffer_gateway/delete/<id>')
def log_buffer_gateway_delete(id):
    delete = logBufferGateway.deleteOne(id)
    return redirect(url_for('log_buffer_gateway'))

@app.route('/log/buffer_gateway/download', methods=['POST'])
def log_buffer_gateway_download():
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    node_id = request.form.get('node_id')
    if node_id == '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logBufferGateway.selectAll()
    elif node_id != '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logBufferGateway.selectByNode(node_id)
    else:
       fetch = logBufferGateway.selectByTime(node_id,datetimes1,datetimes2)
    datas = []
    header = ['node_id','data','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        data.append(fetch[row][1])
        data_sensor = fetch[row][2]
        data.append(json.loads(data_sensor))
        data.append(fetch[row][3])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    node_id, name, ip, port, key, token = getSetting()
    filename = "Log_Buffer (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/buffer_gateway/upload', methods=['POST'])
def log_buffer_gateway_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        node_id = data['node_id'][row]
        node_id = int(node_id)
        datas = data['data'][row]
        datas = datas.replace("'","\"")
        timestamp = data['timestamp'][row]
        inserts = logBufferGateway.insert(node_id,datas,timestamp)
    return redirect(url_for('log_buffer_gateway'))

@app.route('/log/sensor', methods=['GET','POST'])
def log_sensor():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    sensor_id = ''
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
       sensor_id = request.form.get('sensor_id')
       print(sensor_id)
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if sensor_id == '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logSensor.selectAll()
    elif sensor_id != '' and datetime1 == ' ' and datetime2 == ' ':
       fetch = logSensor.selectBySensor(sensor_id)
    else:
       fetch = logSensor.selectByTime(sensor_id,datetime1,datetime2)
    fetch2 = sensor.select()
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_sensor.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2, fetch2=fetch2, sensor_id=sensor_id,
                           project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node,
                           state=state, username=username)

@app.route('/log/sensor/update/<id>', methods=['POST'])
def log_sensor_update(id):
    sensor_id = request.form.get('sensor_id')
    data = request.form.get('data')
    timestamp = request.form.get('timestamp')
    updates = logSensor.updateAll(sensor_id,data,timestamp,id)
    return redirect(url_for('log_sensor'))

@app.route('/log/sensor/delete', methods=['POST'])
def log_sensor_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    sensor_id = request.form.get('sensor_id')
    if sensor_id == '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logSensor.deleteAll()
    elif sensor_id != '' and datetime1 == ' ' and datetime2 == ' ':
       deletes = logSensor.deleteByNode(sensor_id)
    else:
       deletes = logSensor.deleteByTime(sensor_id,datetime1,datetime2)
    return redirect(url_for('log_sensor'))

@app.route('/log/sensor/delete/<id>')
def log_sensor_delete(id):
    delete = logSensor.deleteOne(id)
    return redirect(url_for('log_sensor'))

@app.route('/log/sensor/download', methods=['POST'])
def log_sensor_download():
    node_id, name, ip, port, key, token = getSetting()
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    sensor_id = request.form.get('sensor_id')
    if sensor_id == '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logBuffer.selectAll()
    elif sensor_id != '' and datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logSensor.selectBySensor(sensor_id)
    else:
       fetch = logSensor.selectByTime(sensor_id,datetimes1,datetimes2)
    datas = []
    header = ['sensor_id','data','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        id = fetch[row][1]
        get = sensor.selectById(id)
        for i in get:
            sensor_id = i[1]
        data.append(sensor_id)
        data_sensor = fetch[row][2]
        data.append(data_sensor)
        data.append(fetch[row][3])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    filename = "Log_Sensor (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/sensor/upload', methods=['POST'])
def log_sensor_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        sensor_id = data['sensor_id'][row]
        sensor_id = int(sensor_id)
        get = sensor.selectOne(sensor_id)
        for i in get:
            id = i[0]
        id = int(id)
        print(id, '-', sensor_id)
        data_sensor = data['data'][row]
        data_sensor = str(data_sensor)
        timestamp = data['timestamp'][row]
        inserts = logSensor.insert(id,data_sensor,timestamp)
    return redirect(url_for('log_sensor'))

@app.route('/log/error', methods=['GET','POST'])
def log_error():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    get_time = times.now()
    date1 = get_time.strftime("%Y-%m-01")
    time1 = '00:00'
    date2 = get_time.strftime("%Y-%m-%d")
    time2 = get_time.strftime("%H:%M")
    node_id = ''
    if request.method == 'POST':
       date1 = request.form.get('date1')
       time1 = request.form.get('time1')
       date2 = request.form.get('date2')
       time2 = request.form.get('time2')
    datetime1 = date1 + ' ' + time1
    datetime2 = date2 + ' ' + time2
    if datetime1 == ' ' and datetime2 == ' ':
       fetch = logError.selectAll()
    else:
       fetch = logError.selectByTime(datetime1,datetime2)
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('log_error.html', rule=rule, fetch=fetch, date1=date1, time1=time1, date2=date2, time2=time2, node_id=node_id,
                           project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node,
                           state=state, username=username)

@app.route('/log/error/update/<id>', methods=['POST'])
def log_error_update(id):
    data = request.form.get('data')
    error = request.form.get('error')
    timestamp = request.form.get('timestamp')
    updates = logError.updateAll(data,error,timestamp,id)
    return redirect(url_for('log_error'))

@app.route('/log/error/delete', methods=['POST'])
def log_error_deletes():
    datetime1 = request.form.get('datetime1')
    datetime2 = request.form.get('datetime2')
    if datetime1 == ' ' and datetime2 == ' ':
       deletes = logError.deleteAll()
    else:
       deletes = logError.deleteByTime(datetime1,datetime2)
    return redirect(url_for('log_error'))

@app.route('/log/error/delete/<id>')
def log_error_delete(id):
    delete = logError.deleteOne(id)
    return redirect(url_for('log_error'))

@app.route('/log/error/download', methods=['POST'])
def log_error_download():
    datetimes1 = request.form.get('datetimes1')
    datetimes2 = request.form.get('datetimes2')
    if datetimes1 == ' ' and datetimes2 == ' ':
       fetch = logError.selectAll()
    else:
       fetch = logError.selectByTime(datetimes1,datetimes2)
    datas = []
    header = ['data','error','timestamp']
    datas.append(header)
    for row in range(len(fetch)):
        data = []
        data2 = fetch[row][1]
        if type(data2) == dict:
           data2 = json.loads(data2)
        data.append(data2)
        data.append(fetch[row][2])
        data.append(fetch[row][3])
        datas.append(data)
    sheet = pe.Sheet(datas)
    sheets = io.StringIO()
    sheet.save_to_memory("csv", sheets)
    node_id, name, ip, port, key, token = getSetting()
    filename = "Log_Error (Node ID " + str(node_id) + ").csv"
    output = make_response(sheets.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

@app.route('/log/error/upload', methods=['POST'])
def log_error_upload():
    uploaded_file = request.files['file']
    data = pd.read_csv(uploaded_file)
    for row in range(len(data)):
        datas = data['data'][row]
        error = data['error'][row]
        timestamp = data['timestamp'][row]
        inserts = logError.insert(datas,error,timestamp)
    return redirect(url_for('log_error'))

@app.route('/check/sensor', methods=['GET','POST'])
def check_sensor():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    sensor_id = ''
    result = '-'
    sensors = groups.select()
    if request.method == 'POST':
       sensor_id = request.form.get('sensor')
       filename = "check_sensor" + sensor_id + ".py"
       result = subprocess.Popen(["python3", "/home/connex/project/sensor/"+filename], stdout=subprocess.PIPE)
       (out, err) = result.communicate()
       result = out.decode('utf-8')
       result = result.split('\n')
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('check_sensor.html', sensors=sensors, project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node,
                           rule=rule, sensor_id=sensor_id, result=result, state=state, username=username)

@app.route('/check/send', methods=['GET','POST'])
def check_send():
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    project_name, project_port, project_gateway, project_node, project_protocol = getData()
    tipe = ''
    result = '-'
    if request.method == 'POST':
       tipe = request.form.get('tipe')
       if int(project_protocol) == 1:
          protocol = "http"
       elif int(project_protocol) == 2:
          protocol = "mqtt"
       elif int(project_protocol) == 3:
          protocol = "snmp"
       if tipe == 'node':
          filename = "/home/connex/project/node/check_" + protocol + ".py"
       elif tipe == 'gateway':
          filename = "/home/connex/project/gateway/check_send.py"
       result = subprocess.Popen(["python3", filename], stdout=subprocess.PIPE)
       (out, err) = result.communicate()
       result = out.decode('utf-8')
       result = result.split('\n')
       if result[0] == '':
          result = '-'
    if int(state) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('check_send.html', project_name=project_name, project_port=project_port, project_gateway=project_gateway, project_node=project_node,
                           rule=rule, result=result, tipe=tipe, state=state, username=username)

@app.route('/do/reboot')
def do_reboot():
    os.system("sudo reboot")
    return redirect('/')

@app.errorhandler(Exception)
def handle_exception(e):
    id, username, state, level = checkSession()
    rule = str(request.url_rule)
    error = e
    return render_template('error.html', rule=rule, username=username, state=state, error=error)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=project_port, debug=True)
