import json, os, subprocess, psutil, socket, shutil, magic, zipfile, sys
import netifaces as ni
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_file
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
from pythonping import ping
from pathlib import Path
sys.path.append('/home/connex/platform/function')
from networkFunction import *
from function import *
sys.path.append('/home/connex/platform/database')
from sql import *
from sql_project import *

dashboard_port, dashboard_name = getDashboardSetting()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'platform'

offSession()

@app.route('/')
def index():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    data, length, states, macs, ip, cons, dbs, data_wifi, configs = getNetworkInfo()
    name, port, gateway, node, display, protocol = getProject()
    if name == '' and port == '' and gateway == 0 and node == 0 and display == 0 and protocol == 0:
       flag = 0
    else:
       flag = 1
    return render_template('index.html', rule=rule, data=data, length=length, states=states, macs=macs, ip=ip, cons=cons, port=port, name=name, status=status, username=username, level=level, flag=flag, dashboard_name=dashboard_name)

@app.route('/login')
def login():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    return render_template('login.html', rule=rule, status=status, username=username, level=level, dashboard_name=dashboard_name)

@app.route('/login', methods=['POST'])
def login_post():
    username2 = request.form.get('username')
    password2 = request.form.get('password')
    flag = request.form.get('flag')
    check = login_process(username2, password2, flag)
    if check == "2":
       return redirect(url_for('index'))
    elif check == "1":
       flash('Wrong Password. Please Check Your Login and Try Again')
       return redirect(url_for('login'))
    else:
       flash('Wrong Username. Please Check Your Login and Try Again')
       return redirect(url_for('login'))

@app.route('/setting/identity')
def identity_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    hostname, password = getIdentity()
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('identity.html', rule=rule, status=status, username=username, level=level, hostname=hostname, password=password, dashboard_name=dashboard_name)

@app.route('/identity_post', methods=['POST'])
def identity_post():
    hostname = request.form.get('hostname')
    password = request.form.get('password')
    file_conf = file_read("/etc/hostname")
    file_conf[0] = hostname
    file_write("/etc/hostname", file_conf)
    file_conf2 = file_read("/etc/hosts")
    file_conf2[5] = "127.0.0.1\t" + hostname
    file_write("/etc/hosts", file_conf2)
    identity.updateByName("hostname", hostname)
    identity.updateByName("password", password)
    return redirect(url_for('identity_form'))

@app.route('/setting/user')
def user_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    users = user_db.select()
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('user.html', rule=rule, status=status, username=username, level=level,
                           users=users, dashboard_name=dashboard_name)

@app.route('/user/add', methods=['POST'])
def user_post():
    usernames = request.form.get('username')
    passwords = request.form.get('password')
    passwords = generate_password_hash(passwords)
    level = request.form.get('level')
    datetime = times.getDatetime()
    post = user_db.insert(usernames,passwords,level,datetime)
    return redirect(url_for('user_form'))

@app.route('/user/delete/<id>')
def user_delete(id):
    delete = user_db.delete(id)
    return redirect(url_for('user_form'))

@app.route('/setting/appereance', methods=['GET', 'POST'])
def appereance_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    page = '1'
    if request.method == 'POST':
       page = request.form.get('page')
       uploaded_file = request.files['file']
       filename = secure_filename(uploaded_file.filename)
       if int(page) == 1:
          uploaded_file.save(os.path.join('/home/connex/platform/static/img/wallpaper.jpg'))
       elif int(page) == 2:
          uploaded_file.save(os.path.join('/home/connex/platform/static/img/splash.png'))
          os.system("sudo cp /home/connex/platform/static/img/splash.png /usr/share/plymouth/themes/pix/splash.png")
       elif int(page) == 3:
          uploaded_file.save(os.path.join('/home/connex/platform/static/img/menu.png'))
          os.system("sudo cp /home/connex/platform/static/img/menu.png /usr/share/icons/hicolor/32x32/apps/rpi.png")
          os.system("sudo cp /home/connex/platform/static/img/menu.png /usr/share/icons/PiXflat/16x16/apps/rpi.png")
          os.system("sudo cp /home/connex/platform/static/img/menu.png /usr/share/icons/PiXflat/24x24/apps/rpi.png")
          os.system("sudo cp /home/connex/platform/static/img/menu.png /usr/share/icons/PiXflat/32x32/apps/rpi.png")
          os.system("sudo cp /home/connex/platform/static/img/menu.png /usr/share/icons/PiXflat/48x48/apps/rpi.png")
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('appereance.html', rule=rule, status=status, username=username, level=level, page=page, dashboard_name=dashboard_name)

@app.route('/setting/dashboard', methods=['GET', 'POST'])
def dashboard_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    page = '1'
    if request.method == 'POST':
       page = request.form.get('page')
       if int(page) == 1:
          dashboard_name = request.form.get('dashboard_name')
          dashboard.updateByName("name",dashboard_name)
       elif int(page) == 2:
          dashboard_port = request.form.get('dashboard_port')
          dashboard.updateByName("port",dashboard_port)
       elif int(page) == 3:
          uploaded_file = request.files['file']
          filename = secure_filename(uploaded_file.filename)
          uploaded_file.save(os.path.join('/home/connex/platform/static/img/logo.png'))
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('dashboard.html', rule=rule, status=status, username=username, level=level, dashboard_port=dashboard_port, dashboard_name=dashboard_name, page=page)

@app.route('/setting/fan', methods=['GET', 'POST'])
def fan_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    page = '1'
    if request.method == 'POST':
       page = request.form.get('page')
       if int(page) == 1:
          min_fan = request.form.get('min_fan')
          max_fan = request.form.get('max_fan')
          fan.updateByName("min_fan",min_fan)
          fan.updateByName("max_fan",max_fan)
       elif int(page) == 2:
          min_temp = request.form.get('min_temp')
          max_temp = request.form.get('max_temp')
          fan.updateByName("min_temp",min_temp)
          fan.updateByName("max_temp",max_temp)
    min_temp, max_temp, min_fan, max_fan = getFanSetting()
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('fan.html', rule=rule, status=status, username=username, level=level, dashboard_port=dashboard_port, dashboard_name=dashboard_name,
                          min_temp=min_temp, max_temp=max_temp, min_fan=min_fan, max_fan=max_fan, page=page)

@app.route('/setting/snmp', methods=['GET', 'POST'])
def snmp_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    snmp_community, snmp_user, snmp_password = getSNMP()
    page = '1'
    active = checkActiveService("snmpd")
    enable = checkEnableService("snmpd")
    if active == 'active' and enable == 'enabled':
       snmp_state = 1
    elif active == 'inactive' and enable == 'disabled':
       snmp_state = 0
    else:
       if active == 'active':
          snmp_state = 1
       else:
          snmp_state = 0
    if request.method == 'POST':
       page = request.form.get('page')
       if int(page) == 1:
          snmp_state = request.form.get('snmp_state')
          if int(snmp_state) == 1:
             os.system("sudo service snmpd start")
             os.system("sudo systemctl enable snmpd")
          else:
             os.system("sudo service snmpd stop")
             os.system("sudo systemctl disable snmpd")
          snmp.updateByName("state", snmp_state)
       elif int(page) == 2:
          snmp_community = request.form.get('snmp_community')
          snmp_conf = file_read("/etc/snmp/snmpd.conf")
          snmp_conf[47] = "rocommunity " + snmp_community + "\n"
          file_write("/etc/snmp/snmpd.conf", snmp_conf)
          snmp_conf2 = file_read("/home/connex/platform/storage/snmpd.conf.master")
          snmp_conf2[47] = "rocommunity " + snmp_community + "\n"
          file_write("/home/connex/platform/storage/snmpd.conf.master", snmp_conf2)
          os.system("sudo service snmpd restart")
          snmp.updateByName("community", snmp_community)
       elif int(page) == 3:
          snmp_user = request.form.get('snmp_user')
          snmp_password = request.form.get('snmp_password')
          snmp_conf = file_read("/etc/snmp/snmpd.conf")
          snmp_conf[32] = "createUser " + snmp_user + " SHA \"" + snmp_password + "\" DES\n"
          snmp_conf[66] = "rwuser " + snmp_user + " priv\n"
          file_write("/etc/snmp/snmpd.conf", snmp_conf)
          snmp_conf2 = file_read("/home/connex/platform/storage/snmpd.conf.master")
          snmp_conf[32] = "createUser " + snmp_user + " SHA \"" + snmp_password + "\" DES\n"
          snmp_conf[66] = "rwuser " + snmp_user + " priv\n"
          file_write("/home/connex/platform/storage/snmpd.conf.master", snmp_conf2)
          os.system("sudo service snmpd restart")
          snmp.updateByName("user", snmp_user)
          snmp.updateByName("password", snmp_password)

    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('snmp.html', rule=rule, status=status, username=username, level=level, dashboard_port=dashboard_port, dashboard_name=dashboard_name, page=page, snmp_community=snmp_community, snmp_user=snmp_user, snmp_password=snmp_password, snmp_state=snmp_state)

@app.route('/setting/project', methods=['GET', 'POST'])
def project_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    name, port, gateway, node, display, protocol = getProject()
    if name == '' and port == '' and gateway == 0 and node == 0 and display == 0 and protocol == 0:
       flag = 0
    else:
       flag = 1
    select = project.select()
    base = "/home/connex"
    try:
      now = request.args['source']
      location = request.args['location']
    except:
      now = "project"
      location = "project"
    if location == base:
       location = 'project'
    location = os.path.join(base,location)
    if request.method == 'POST':
       action = request.form.get('action')
       now = request.form.get('loc')
       location = request.form.get('parent')
       if action == 'down':
          if now != "project":
             location = Path(location)
             location = location.parent.absolute()
    if now != "project":
       location = os.path.join(location,now)
    parents = Path(location)
    parents = parents.parent.absolute()
    back = os.path.split(parents)
    back = back[1]
    if len(select) > 0:
       list = os.listdir(location)
       types = []
       sizes = []
       editors = []
       zipes = []
       for i in list:
           paths = os.path.join(location,i)
           cek = os.path.isdir(paths)
           types.append(cek)
           zip = zipfile.is_zipfile(paths)
           zipes.append(zip)
           if cek == True:
              editors.append('Directory')
              size = 0
              for (path, dirs, files) in os.walk(paths):
                  for file in files:
                      filename = os.path.join(path, file)
                      size += os.path.getsize(filename)
              if size > 1024*999:
                 size = round(size/(1024*1024),2)
                 size = str(size) + " mb"
              elif size > 1024:
                 size = round(size/1024,2)
                 size = str(size) + " kb"
              else:
                 size = str(size) + " b"
              sizes.append(size)
           else:
              try:
                 f = open(paths,"r")
                 f = f.readlines()
              except:
                 format = magic.from_file(paths, mime = True)
                 f = 'Unsupported File Format ' + str(format)
              editors.append(f)
              size = os.path.getsize(paths)
              if size > 1024*999:
                 size = round(size/(1024*1024),2)
                 size = str(size) + " mb"
              elif size > 1024:
                 size = round(size/1024,2)
                 size = str(size) + " kb"
              else:
                 size = str(size) + " b"
              sizes.append(size)
    else:
       list = []
       types = []
       sizes = []
       editors = []
       zipes = []
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('project.html', rule=rule, status=status, name=name, port=port,
                           gateway=gateway, node=node, display=display, select=select, location=location, parents=parents, now=now, back=back, list=list, types=types, sizes=sizes, editors=editors, zipes=zipes, protocol=protocol, flag=flag,
                           dashboard_name=dashboard_name, username=username)

@app.route('/project/add', methods=['POST'])
def project_post():
    name = request.form.get('name')
    port = request.form.get('port')
    gateway = request.form.get('gateway')
    node = request.form.get('node')
    display = request.form.get('display')
    protocol = request.form.get('protocol')
    if gateway == None:
       gateway = 0
    if node == None:
       node = 0
    base = "/home/connex"
    path_platform = base + "/platform"
    path_project = base + "/project"
    id_dashboard, id_node, id_gateway, id_auth, id_buffer, id_display = 0, 0, 0, 0, 0, 0
    os.system("sudo mkdir " + path_project)
    os.system("sudo cp " + path_platform + "/storage/project/dashboard " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/monitoring " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/auth " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/notification " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/system " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/synchronize " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/log " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/function " + path_project + " -r")
    os.system("sudo cp " + path_platform + "/storage/project/database " + path_project + " -r")
    os.system("sudo mkdir " + path_project + "/sensor")
    os.system("sudo mkdir " + path_project + "/actuator")
    config.createService(path_platform, path_project, "/dashboard", "connex_dashboard", "connex_dashbaord.py") # => connex_dashboard
    config.createService(path_platform, path_project, "/monitoring", "connex_routine", "connex_routine.py") # => connex_routine
    config.createService(path_platform, path_project, "/monitoring", "connex_buffer", "connex_buffer.py") # => connex_buffer
    config.createService(path_platform, path_project, "/monitoring", "connex_alarm", "connex_alarm.py") # => connex_alarm
    config.createService(path_platform, path_project, "/synchronize", "connex_sync", "connex_sync.py") # => connex_sync
    config.createService(path_platform, path_project, "/notification", "connex_notif", "connex_notif.py") # => connex_notif
    config.createService(path_platform, path_project, "/auth", "connex_auth", "connex_auth.py") # => connex_auth
    config.createService(path_platform, path_project, "/log", "connex_log", "connex_log.py") # => connex_log
    config.createService(path_platform, path_project, "/system", "connex_support", "connex_support.py") # => connex_support
    config.createService(path_platform, path_project, "/system", "connex_boot", "connex_boot.py") # => connex_boot
    if int(display) == 1:
       os.system("sudo cp " + path_platform + "/storage/project/display " + path_project + " -r")
       id_display = config.createService(path_platform, path_project, "/display", "connex_display", "display.py")
    os.system("sudo systemctl start connex_dashboard")
    os.system("sudo systemctl enable connex_dashboard")
    os.system("sudo systemctl daemon-reload")
    inserts = project.insert(name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display)
    return redirect(url_for('project_form'))

@app.route('/project/edit', methods=['POST'])
def project_edit():
    name = request.form.get('name')
    port = request.form.get('port')
    gateway = request.form.get('gateway')
    node = request.form.get('node')
    display = request.form.get('display')
    protocol = request.form.get('protocol')
    if gateway == None:
       gateway = 0
    if node == None:
       node = 0
    fetch = project.select()
    if len(fetch) > 0:
       for i in range(len(fetch)):
           gateways = fetch[i]['gateway']
           nodes = fetch[i]['node']
           displays = fetch[i]['display']
           protocols = fetch[i]['protocol']
           id_dashboard = fetch[i]['id_dashboard']
           id_gateway = fetch[i]['id_gateway']
           id_node = fetch[i]['id_node']
           id_auth = fetch[i]['id_auth']
           id_buffer = fetch[i]['id_buffer']
           id_display = fetch[i]['id_display']
    updates = project.update(name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display)
    return redirect(url_for('project_form'))

@app.route('/project/reset')
def project_reset():
    base = "/home/connex"
    config.removeOID()
    fetch = groups.select()
    if len(fetch) > 0:
       for i in range(len(fetch)):
           service_sensor = fetch[i][5]
           service_delete(service_sensor)
    fetch = project.select()
    if len(fetch) > 0:
       for i in range(len(fetch)):
           id_dashboard = fetch[i]['id_dashboard']
           id_node = fetch[i]['id_node']
           id_auth = fetch[i]['id_auth']
           id_buffer = fetch[i]['id_buffer']
           id_display = fetch[i]['id_display']
    deletes = project.delete(1)
    service_delete(id_node)
    service_delete(id_auth)
    service_delete(id_buffer)
    service_delete(id_dashboard)
    service_delete(id_display)
    attributes.reset()
    intervals.reset()
    setting.reset()
    gateway.reset()
    logSendNode.reset()
    logSendGateway.reset()
    logBufferNode.reset()
    logBufferGateway.reset()
    logSensor.reset()
    logError.reset()
    sensor.deleteAll()
    sensor.reset()
    params.reset()
    groups.deleteAll()
    groups.reset()
    os.system("sudo rm " + base + "/project -r")
    return redirect(url_for('project_form'))

@app.route('/project/file/editor', methods=['POST'])
def project_file_editor():
    editor = request.form.get('editor')
    path = request.form.get('path')
    source = request.form.get('source')
    paths = os.path.join(path,source)
    f = open(paths, "w")
    f.writelines(editor)
    f.close()
    basename = os.path.split(path)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/content/add', methods=['POST'])
def project_content_add():
    path = request.form.get('path')
    tipe = request.form.get('tipe')
    name = request.form.get('name')
    if int(tipe) == 0:
       os.system("touch " + path + "/" + name)
    else:
       os.system("mkdir " + path + "/" + name)
    basename = os.path.split(path)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/<type>/edit', methods=['POST'])
def project_content_edit(type):
    path = request.form.get('path')
    last_name = request.form.get('last_name')
    new_name = request.form.get('new_name')
    os.system("sudo mv " + path + "/" + last_name + " " + path + "/" + new_name)
    basename = os.path.split(path)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/<type>/delete', methods=['POST'])
def project_content_delete(type):
    path = request.form.get('path')
    source = request.form.get('source')
    paths = os.path.join(path,source)
    if type == "folder":
       os.system("sudo rm " + paths + " -r")
    else:
       os.system("sudo rm " + paths)
    basename = os.path.split(path)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/content/copy', methods=['POST'])
def project_content_copy():
    loc = request.form.get('path')
    source = request.form.get('source')
    destination = request.form.get('destination')
    parent = request.form.get('parent')
    sources = os.path.join(loc,source)
    if destination == "this":
       destination = loc
       destination = destination + "/" + source + "_copy"
       if os.path.exists(destination) == True:
          destination = destination + "_copy"
    elif destination == "parent":
       destination = os.path.split(loc)
       destination = destination[0]
    else:
       destination = os.path.join(loc,destination)
    print(destination)
    if os.path.isdir(sources) == True:
       os.system("sudo cp -r " + sources + " " + destination)
    else:
       os.system("sudo cp " + sources + " " + destination)
    basename = os.path.split(loc)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/content/cut', methods=['POST'])
def project_content_cut():
    loc = request.form.get('path')
    source = request.form.get('source')
    destination = request.form.get('destination')
    parent = request.form.get('parent')
    sources = os.path.join(loc,source)
    if destination == "parent":
       destination = os.path.split(loc)
       destination = destination[0]
    else:
       destination = os.path.join(loc,destination)
    os.system("sudo mv " + sources + " " + destination)
    basename = os.path.split(loc)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/<type>/archive/<filenames>', methods=['POST'])
def project_content_archive(type,filenames):
    loc = request.form.get('path')
    zipname = request.form.get('filename')
    source = os.path.join(loc,filenames)
    zippath = os.path.join(loc,zipname)
    if type == "folder":
       zip = shutil.make_archive(zippath,'zip',source)
    else:
       zip = shutil.make_archive(zippath,'zip',loc, filenames)
    basename = os.path.split(loc)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/<type>/unarchive/<filenames>', methods=['POST'])
def project_content_unarchive(type,filenames):
    loc = request.form.get('path')
    parent = request.form.get('parent')
    destination = request.form.get('destination')
    if destination == "this":
       destination = loc
    elif destination == "parent":
       destination = os.path.split(loc)
       destination = destination[0]
    else:
       destination = os.path.join(loc,destination)
    source = os.path.join(loc,filenames)
    unzip = shutil.unpack_archive(source,destination,"zip")
    basename = os.path.split(loc)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/project/<type>/download/<filenames>', methods=['POST'])
def project_content_download(type,filenames):
    loc = request.form.get('path')
    source = os.path.join(loc,filenames)
    os.system("sudo rm /home/connex/platform/storage/upload/*")
    if type == "folder":
       zipname = "/home/connex/platform/storage/upload/" + filenames
       files = shutil.make_archive(zipname, 'zip', source)
       source = files
    return redirect(url_for('project_download', filename=source))

@app.route('/project/content/download/<folder>', methods=['POST'])
def project_content_download_all(folder):
    source = request.form.get('path')
    os.system("sudo rm /home/connex/platform/storage/upload/*")
    zipname = "/home/connex/platform/storage/upload/" + folder
    download = shutil.make_archive(zipname, 'zip', source)
    return redirect(url_for('project_download', filename=download))

@app.route('/project/download')
def project_download():
    download = request.args['filename']
    return send_file(download, as_attachment=True)

@app.route('/project/content/upload', methods=['POST'])
def project_content_upload():
    loc = request.form.get('path')
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    uploaded_file.save(os.path.join(loc, filename))
    basename = os.path.split(loc)
    return redirect(url_for('project_form', source=basename[1], location=basename[0].replace("/home/connex/","")))

@app.route('/crontab/add', methods=['POST'])
def crontab_post():
    nama = request.form.get('name')
    schedule = request.form.get('schedule')
    command = request.form.get('command')
    add = crontabs.insert(nama,schedule,command)
    fetch = crontabs.select()
    shutil.copy('storage/crontab.master', '/var/spool/cron/crontabs/root')
    f = open('/var/spool/cron/crontabs/root', 'a')
    if len(fetch) > 0:
       for i in range(len(fetch)):
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if active == 1:
              f.write('{} {}\n'.format(schedules,commands))
           else:
              f.write('#{} {}\n'.format(schedules,command))
    else:
       f.write('{} {}\n'.format(schedule,command))
    return redirect(url_for('crontab'))

@app.route('/crontab/edit/<id>', methods=['POST'])
def crontab_edit(id):
    nama = request.form.get('name')
    schedule = request.form.get('schedule')
    command = request.form.get('command')
    state = request.form.get('state')
    update = crontabs.update(nama,schedule,command,state,id)
    fetch = crontabs.select()
    shutil.copy('storage/crontab.master', '/var/spool/cron/crontabs/root')
    f = open('/var/spool/cron/crontabs/root', 'a')
    if len(fetch) > 0:
       for i in range(len(fetch)):
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if active == 1:
              f.write('{} {}\n'.format(schedules,commands))
           else:
              f.write('#{} {}\n'.format(schedules,commands))
    return redirect(url_for('crontab'))

@app.route('/crontab/delete/<id>')
def crontab_delete(id):
    deletes = crontabs.delete(id)
    fetch = crontabs.select()
    shutil.copy('storage/crontab.master', '/var/spool/cron/crontabs/root')
    f = open('/var/spool/cron/crontabs/root', 'a')
    if len(fetch) > 0:
       for i in range(len(fetch)):
           no = fetch[i]['id']
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if active == 1:
              if no != id:
                 f.write('{} {}\n'.format(schedules,commands))
    return redirect(url_for('crontab'))

@app.route('/crontab/start/<id>')
def crontab_start(id):
    fetch = crontabs.select()
    shutil.copy('storage/crontab.master', '/var/spool/cron/crontabs/root')
    f = open('/var/spool/cron/crontabs/root', 'a')
    if len(fetch) > 0:
       for i in range(len(fetch)):
           no = fetch[i]['id']
           names = fetch[i]['name']
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if int(id) == int(no):
              updates = crontabs.update(names,schedules,commands,1,id)
    fetch = crontabs.select()
    if len(fetch) > 0:
       for i in range(len(fetch)):
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if int(active) == 1:
              f.write('{} {}\n'.format(schedules,commands))
           else:
              f.write('#{} {}\n'.format(schedules,commands))
    return redirect(url_for('crontab'))

@app.route('/crontab/stop/<id>')
def crontab_stop(id):
    fetch = crontabs.select()
    shutil.copy('storage/crontab.master', '/var/spool/cron/crontabs/root')
    f = open('/var/spool/cron/crontabs/root', 'a')
    if len(fetch) > 0:
       for i in range(len(fetch)):
           no = fetch[i]['id']
           names = fetch[i]['name']
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if int(id) == int(no):
              updates = crontabs.update(names,schedules,commands,0,id)
    fetch = crontabs.select()
    if len(fetch) > 0:
       for i in range(len(fetch)):
           schedules = fetch[i]['schedule']
           commands = fetch[i]['command']
           active = fetch[i]['state']
           if int(active) == 1:
              f.write('{} {}\n'.format(schedules,commands))
           else:
              f.write('#{} {}\n'.format(schedules,commands))
    return redirect(url_for('crontab'))

@app.route('/setting/crontab')
def crontab():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    fetch = crontabs.select()
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_crontab.html', rule=rule, status=status, fetch=fetch, username=username, dashboard_name=dashboard_name)

@app.route('/service/add', methods=['POST'])
def service_post():
    nama = request.form.get('name')
    path = request.form.get('path')
    command = request.form.get('command')
    nama2 = nama.replace(" ","")
    f = open('storage/service.master', 'r')
    data = f.readlines()
    f.close()
    data[5]="ExecStart={}\n".format(command)
    data[6]="WorkingDirectory={}\n".format(path)
    f = open('/lib/systemd/system/'+nama2+'.service', 'w')
    f.writelines(data)
    f.close()
    os.system("sudo systemctl start "+nama2)
    os.system("sudo systemctl enable "+nama2)
    os.system("sudo systemctl daemon-reload")
    add = services.insert(nama,path,command)
    return redirect(url_for('service_form'))

@app.route('/service/edit/<id>', methods=['POST'])
def service_edit(id):
    nama = request.form.get('name')
    path = request.form.get('path')
    command = request.form.get('command')
    state = request.form.get('state')
    autostart = request.form.get('autostart')
    nama2 = nama.replace(" ","")
    select = services.selectOne(id)
    if len(select):
       for i in range(len(select)):
           last_nama = select[i]['name']
           last_nama = last_nama.replace(" ","")
           os.system("sudo rm /lib/systemd/system/" + last_nama + ".service")
           os.system("sudo systemctl daemon-reload")
    update = services.update(nama,path,command,state,autostart,id)
    f = open('storage/service.master', 'r')
    data = f.readlines()
    f.close()
    data[5]="ExecStart={}\n".format(command)
    data[6]="WorkingDirectory={}\n".format(path)
    f = open('/lib/systemd/system/' + nama2 + '.service', 'w')
    f.writelines(data)
    f.close()
    os.system("sudo systemctl start "+ nama2)
    os.system("sudo systemctl enable "+ nama2)
    os.system("sudo systemctl daemon-reload")
    return redirect(url_for('service_form'))

@app.route('/service/editor/<id>', methods=['POST'])
def service_editor(id):
    editor = request.form.get('editor')
    select = services.selectOne(id)
    if len(select):
       for i in range(len(select)):
           nama = select[i]['name']
           nama = nama.replace(" ","")
           f = open("/lib/systemd/system/" + nama + ".service", "w")
           f.writelines(editor)
           f.close()
    return redirect(url_for('service_form'))

@app.route('/service/delete/<id>')
def service_delete(id):
    select = services.selectOne(id)
    if len(select) > 0:
       for i in range(len(select)):
           nama = select[i]['name']
           nama = nama.replace(" ","")
           os.system("rm /lib/systemd/system/" + nama + ".service")
           os.system("sudo systemctl daemon-reload")
    deletes = services.delete(id)
    return redirect(url_for('service_form'))

@app.route('/service/enable/<id>')
def service_enable(id):
    select = services.selectOne(id)
    if len(select) > 0:
       for i in range(len(select)):
           name = select[i]['name'].replace(" ","")
           update = services.update(name,select[i][2],select[i][3],select[i][4],1,id)
           os.system("sudo systemctl enable " + name)
    return redirect(url_for('service_form'))

@app.route('/service/disable/<id>')
def service_disable(id):
    select = services.selectOne(id)
    if len(select) > 0:
       for i in range(len(select)):
           name = select[i]['name'].replace(" ","")
           update = services.update(name,select[i][2],select[i][3],select[i][4],0,id)
           os.system("sudo systemctl disable " + name)
    return redirect(url_for('service_form'))

@app.route('/service/stop/<id>')
def service_stop(id):
    select = services.selectOne(id)
    if len(select) > 0:
       for i in range(len(select)):
           name = select[i]['name'].replace(" ","")
           update = services.update(name,select[i][2],select[i][3],0,select[i][5],id)
           os.system("sudo service " + name + " stop")
    return redirect(url_for('service_form'))

@app.route('/service/start/<id>')
def service_start(id):
    select = services.selectOne(id)
    if len(select) > 0:
       for i in range(len(select)):
           name = select[i]['name'].replace(" ","")
           update = services.update(name,select[i][2],select[i][3],1,select[i][5],id)
           os.system("sudo service " + name + " start")
    return redirect(url_for('service_form'))

@app.route('/setting/service')
def service_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    fetch = services.select()
    editor = []
    if len(fetch) > 0:
       for i in range(len(fetch)):
           nama = fetch[i]['name']
           nama = nama.replace(" ","")
           f = open("/lib/systemd/system/"+nama+".service","r")
           f = f.readlines()
           editor.append(f)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_service.html', rule=rule, status=status, fetch=fetch, editor=editor, dashboard_name=dashboard_name, username=username)

@app.route('/setting/network', methods=['POST','GET'])
def network_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.path)
    data, length, states, macs, ip, cons, dbs, data_wifi, configs = getNetworkInfo()
    wifis = []
    now_wifis = []
    if request.method == 'POST':
      now = request.form.get('wireless')
    else:
      if len(data_wifi) > 0:
         now = data_wifi[0]
      else:
         now = '-'
    if now == '-':
       wifis = []
       now_wifis = '-'
    else:
       wifis = get_parsed_cells(now)
       now_wifis = getSSID(now)
    hotspot = wireless.selectByName("hotspot")
    hotspot = hotspot[0]
    station = wireless.selectByName("station")
    station = station[0]
    param = ['interface', 'start', 'end', 'subnet', 'gateway', 'dns1', 'dns2']
    dhcp_data = []
    for i in param:
      get = dhcp.selectByName(i)
      dhcp_data.append(get[0]['value'])
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('network.html', status=status, rule=rule, data=data, length=length, macs=macs, ip=ip, states=states, cons=cons, dbs=dbs, wifis=wifis, now_wifis=now_wifis, data_wifi=data_wifi, configs=configs, now=now, dashboard_name=dashboard_name, username=username, hotspot=hotspot, station=station, dhcp_data=dhcp_data)

@app.route('/network/<iface>/post', methods=['POST'])
def network_post(iface):
    con = request.form.get('connection_'+iface)
    tipe, state, mac, ip = getInterface(iface)
    if int(con) == 0:
       ip_new = request.form.get('ip_'+iface)
       subnet = request.form.get('subnet_'+iface)
       gateway = request.form.get('gateway_'+iface)
       dns = request.form.get('dns_'+iface)
       if int(tipe) == 0:
          interface.updateFull(iface,tipe,con,mac,ip_new,subnet,gateway,dns)
       else:
          db = interface.selectOne(iface)
         #  for i in db:
         #      mode = i[3]
          interface.updateFull(iface,tipe,con,mac,ip_new,subnet,gateway,dns)
    else:
       if int(tipe) == 0:
          interface.updateFull(iface,tipe,con,mac,"","","","")
       else:
          db = interface.selectOne(iface)
         #  for i in db:
         #      mode = i[3]
          interface.updateFull(iface,tipe,con,mac,"","","","")
    config.network()
    return redirect(url_for('network_form'))

@app.route('/network/<iface>/connect', methods=['POST'])
def network_connect(iface):
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    wireless.update("station",iface,1,ssid,password,0)
    shutil.copy('storage/wpa.master', '/etc/wpa_supplicant/wpa_supplicant.conf')
    f = open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a')
    f.write('\nnetwork={\n')
    f.write('ssid=\"{}\"\n'.format(ssid))
    f.write('psk=\"{}\"'.format(password))
    f.write('\n}')
    f.close()
    os.system("service networking restart")
    return redirect(url_for('network_form'))

@app.route('/network/reset/config')
def network_reset():
    wireless.update("station","",0,"","",0)
    shutil.copy('storage/wpa.master', '/etc/wpa_supplicant/wpa_supplicant.conf')
    return redirect(url_for('network_form'))

@app.route('/network/hotspot', methods=['POST'])
def network_hotspot():
    interface = request.form.get('interface')
    enable = request.form.get('enable')
    ssid = request.form.get('ssid')
    passw= request.form.get('passw')
    channel = request.form.get('channel')
    if enable == "on":
       enable = 1
       config.hotspot(interface,ssid,passw,channel)
       os.system("sudo service hostapd restart")
       os.system("sudo systemctl enable hostapd")
    else:
       enable = 0
       os.system("sudo service hostapd stop")
       os.system("sudo systemctl disable hostapd")
    wireless.update("hotspot",interface,enable,ssid,passw,channel)
    return redirect(url_for('network_form'))

@app.route('/network/dhcp/post', methods=['POST'])
def network_dhcp():
    interface = request.form.get('interface')
    start = request.form.get('start')
    end = request.form.get('end')
    subnet = request.form.get('subnet')
    gateway = request.form.get('gateway')
    dns1 = request.form.get('dns1')
    dns2 = request.form.get('dns2')
    param = ['interface', 'start', 'end', 'subnet', 'gateway', 'dns1', 'dns2']
    value = [interface, start, end, subnet, gateway, dns1, dns2]
    for i in range(len(param)):
        dhcp.updateByName(param[i], value[i])
    config.DHCP(value)
    os.system("sudo service dnsmasq restart")
    return redirect(url_for('network_form'))

@app.route('/network/<iface>/restart')
def network_restart(interface):
    restart = os.system("/etc/init.d/networking restart")
    return redirect(url_for('network_form'))

@app.route('/setting/ntp')
def ntp_form():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    select = ntp.select()
    for i in select:
        server = i['server']
        ip_ntp = i['ip_ntp']
    ip1, ip2, ip3 = '', '', ''
    if ip_ntp != '':
       ip_ntp = ip_ntp.split(' ')
       for x in range(len(ip_ntp)):
           if x == 0: ip1 = ip_ntp[x]
           elif x == 1: ip2 = ip_ntp[x]
           elif x == 2: ip3 = ip_ntp[x]
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('ntp.html', rule=rule, status=status, ip1=ip1, ip2=ip2, ip3=ip3,
                           server=server, dashboard_name=dashboard_name, username=username)

@app.route('/ntp/post', methods=['POST'])
def ntp_post():
    server = request.form.get('server')
    if server == "1":
       ip1 = request.form.get('ip1')
       ip2 = request.form.get('ip2')
       ip3 = request.form.get('ip3')
    else:
       ip1, ip2, ip3 = '', '', ''
    config.NTP(server, ip1, ip2, ip3)
    ip_ntp = ip1
    if ip2 != '':
      ip_ntp = ip_ntp + ' ' + ip2
    if ip3 != '':
      ip_ntp = ip_ntp + ' ' + ip3
    post = ntp.update(server, ip_ntp)
    return redirect(url_for('ntp_form'))

@app.route('/ntp/restart')
def ntp_restart():
    restart = os.system("systemctl restart systemd-timesyncd")
    return redirect(url_for('ntp_form'))

@app.route('/control/ping', methods=['GET','POST'])
def control_ping():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    result, ip = '-', ''
    if request.method == 'POST':
       ip = request.form.get('ip')
       try:
          result = ping(ip, verbose=True)
          result = str(result)
          result = result.split('\r\n')
       except:
          result = ['Cannot Ping ' + str(ip)]
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_ping.html', rule=rule, status=status, username=username,
                            result=result, ip=ip, dashboard_name=dashboard_name)

@app.route('/control/ntp', methods=['GET','POST'])
def control_ntp():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    ip, task, result, result2 = '', '0', '-', '-'
    if request.method == 'POST':
       def run(result):
           (out, err) = result.communicate()
           result = out.decode('utf-8')
           return result
       task = request.form.get('task')
       if int(task) == 0:
          ip = request.form.get('ip')
          result = subprocess.Popen(["ntpdate", "-u", ip], stdout=subprocess.PIPE)
          result = run(result)
          if result == '':
             result = ['No Synchronize']
          else:
             result = [result]
       elif int(task):
          result2 = subprocess.Popen("date", stdout=subprocess.PIPE)
          result2 = run(result2)
          result2 = [result2]
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_ntp.html', rule=rule, status=status, username=username,
    result=result, result2=result2, ip=ip, task=task, dashboard_name=dashboard_name)

@app.route('/control/rtc', methods=['GET','POST'])
def control_rtc():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    get_time = times.now()
    date_now = get_time.strftime("%Y-%m-%d")
    time_now = get_time.strftime("%H:%M")
    task, result, result2, result3, result4 = '0', '-', '-', '-', '-'
    if request.method == 'POST':
       def run(result):
           (out, err) = result.communicate()
           result = out.decode('utf-8')
           if result == '':
              result = ['Please Check Hardware Clock']
           else:
              result = [result]
           return result
       task = request.form.get('task')
       if int(task) == 0:
          result = subprocess.Popen(["hwclock","-r"], stdout=subprocess.PIPE)
          result = run(result)
       elif int(task) == 1:
          write = request.form.get('write')
          if write == "auto":
             result2 = subprocess.Popen(["hwclock","-w"], stdout=subprocess.PIPE)
             time.sleep(1)
             result2 = subprocess.Popen(["hwclock","-r"], stdout=subprocess.PIPE)
             result2 = run(result2)
          elif write == "system":
             result4 = subprocess.Popen(["hwclock","-s"], stdout=subprocess.PIPE)
             time.sleep(1)
             result4 = subprocess.Popen(["hwclock","-r"], stdout=subprocess.PIPE)
             result4 = run(result4)
          elif write == "manual":
             date_now = request.form.get('date')
             time_now = request.form.get('time')
             datetimes = str(date_now) + " " + str(time_now) + ":00"
             result3 = subprocess.Popen(["hwclock","--set","--date", datetimes], stdout=subprocess.PIPE)
             time.sleep(1)
             result3 = subprocess.Popen(["hwclock","-r"], stdout=subprocess.PIPE)
             result3 = run(result3)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_rtc.html', rule=rule, status=status, username=username,
                            result=result, result2=result2, result3=result3, result4=result4, task=task, date_now=date_now, time_now=time_now, dashboard_name=dashboard_name)

@app.route('/control/gpio', methods=['GET','POST'])
def control_gpio():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    task, pin2, type2, pin, type, action, result, result2 = '0', '', '', '', '', '', '-', '-'
    if request.method == 'POST':
       def run(result):
           (out, err) = result.communicate()
           result = out.decode('utf-8')
           result = result.split('\n')
           result.pop(len(result)-1)
           return result
       task = request.form.get('task')
       if int(task) == 0:
          pin2 = request.form.get('pin2')
          type2 = request.form.get('type2')
          result2 = subprocess.Popen(["python3", "testing/gpio_test.py", "-p", pin2, "-m", task, "-t", type2], stdout=subprocess.PIPE)
          result2 = run(result2)
       elif int(task) == 1:
          pin = request.form.get('pin')
          type = request.form.get('type')
          action = request.form.get('action')
          result = subprocess.Popen(["python3", "testing/gpio_test.py", "-p", pin, "-m", task, "-t", type, "-a", action], stdout=subprocess.PIPE)
          result = run(result)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_gpio.html', rule=rule, status=status, result=result, pin=pin,
                           pin2=pin2, task=task, type=type, type2=type2, action=action, result2=result2, username=username,
                           dashboard_name=dashboard_name)

@app.route('/control/pwm', methods=['GET','POST'])
def control_pwm():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    pin, type, frekuensi, cycle, result, = '', '', '', '', '-'
    if request.method == 'POST':
       def run(result):
           (out, err) = result.communicate()
           result = out.decode('utf-8')
           result = result.split('\n')
           result.pop(len(result)-1)
           return result
       frekuensi = request.form.get('frekuensi')
       pin = request.form.get('pin')
       type = request.form.get('type')
       cycle = request.form.get('cycle')
       result = subprocess.Popen(["python3", "testing/pwm_test.py", "-p", pin, "-f", frekuensi, "-t", type, "-c", cycle], stdout=subprocess.PIPE)
       result = run(result)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_pwm.html', rule=rule, status=status, result=result, pin=pin,
                           type=type, frekuensi=frekuensi, cycle=cycle, username=username, dashboard_name=dashboard_name)

@app.route('/control/adc', methods=['GET','POST'])
def control_adc():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    pin, gain, result = '', '','-'
    if request.method == 'POST':
       pin = request.form.get('pin')
       gain = request.form.get('gain')
       result = subprocess.Popen(["python3", "testing/adc_test.py", "-p", pin, "-g", gain], stdout=subprocess.PIPE)
       (out, err) = result.communicate()
       result = out.decode('utf-8')
       result = result.split('\n')
       result.pop(len(result)-1)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_adc.html', rule=rule, status=status, result=result, pin=pin,
                           gain=gain, dashboard_name=dashboard_name)

@app.route('/control/serial', methods=['GET','POST'])
def control_serial():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    def run(result):
        (out, err) = result.communicate()
        result = out.decode('utf-8')
        result = result.split('\n')
        result.pop(len(result)-1)
        return result
    serial = subprocess.Popen(["python3", "testing/serial_list.py"], stdout=subprocess.PIPE)
    serial = run(serial)
    pin, pin2, timeout, timeout2, rate, rate2, value = '', '', '', '', '', '', ''
    task, result, result2, result3 = '0', '-', '-', '-'
    if request.method == 'POST':
       task = request.form.get('task')
       if int(task) == 0:
          result = subprocess.Popen(["python3", "testing/serial_detect.py"], stdout=subprocess.PIPE)
          result = run(result)
       elif int(task) == 1:
          pin = request.form.get('pin')
          rate = request.form.get('rate')
          timeout = request.form.get('timeout')
          result2 = subprocess.Popen(["python3", "testing/serial_read.py", "-p", pin, "-t", timeout, "-r", rate], stdout=subprocess.PIPE)
          result2 = run(result2)
       elif int(task) == 2:
          pin2 = request.form.get('pin2')
          value = request.form.get('value')
          rate2 = request.form.get('rate2')
          timeout2 = request.form.get('timeout2')
          result3 = subprocess.Popen(["python3", "testing/serial_write.py", "-p", pin2, "-t", timeout2, "-r", rate2, "-v", value], stdout=subprocess.PIPE)
          result3 = run(result3)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_serial.html', rule=rule, username=username, status=status, result=result, pin=pin,
                           task=task, serial=serial, result2=result2, timeout=timeout, rate=rate, pin2=pin2, timeout2=timeout2, rate2=rate2, value=value,
                           result3=result3, dashboard_name=dashboard_name)

@app.route('/control/i2c', methods=['GET','POST'])
def control_i2c():
    dashboard_port, dashboard_name = getDashboardSetting()
    id_user, username, level, status = checkSession(0)
    rule = str(request.url_rule)
    task, result, result2, result3 = '0', '-', '-', '-'
    address, reg, value, address2, reg2, value2 = '', '', '', '', '', ''
    if request.method == 'POST':
       def run(result):
           (out, err) = result.communicate()
           result = out.decode('utf-8')
           result = result.split('\n')
           result.pop(len(result)-1)
           return result
       task = request.form.get('task')
       if int(task) == 0:
          result = subprocess.Popen(["python3","testing/i2c_detect.py"], stdout=subprocess.PIPE)
          result = run(result)
       elif int(task) == 1:
            address = request.form.get('address')
            reg = request.form.get('reg')
            value = request.form.get('value')
            result2 = subprocess.Popen(["python3","testing/i2c_read.py","-a", address,"-s",reg, "-b",value], stdout=subprocess.PIPE)
            result2 = run(result2)
       elif int(task) == 2:
            address2 = request.form.get('address2')
            reg2 = request.form.get('reg2')
            value2 = request.form.get('value2')
            result3 = subprocess.Popen(["python3","testing/i2c_write.py","-a", address2,"-r",reg2, "-d",value2], stdout=subprocess.PIPE)
            result3 = run(result3)
    if int(status) == 0:
       flash('Please Login to Access the Page')
       return redirect(url_for('login'))
    return render_template('control_i2c.html', username=username, rule=rule, status=status, result=result, result2=result2, result3=result3, task=task, address=address, address2=address2, reg=reg, reg2=reg2, value=value, value2=value2, dashboard_name=dashboard_name)

@app.route('/do/clear/<task>')
def clear(task):
    if task == 'ping':
       return redirect(url_for('control_ping'))
    elif task == 'ntp':
       return redirect(url_for('control_ntp'))
    elif task == 'rtc':
       return redirect(url_for('control_rtc'))
    elif task == 'gpio':
       return redirect(url_for('control_gpio'))
    elif task == 'adc':
       return redirect(url_for('control_adc'))
    elif task == 'pwm':
       return redirect(url_for('control_pwm'))
    elif task == 'serial':
       return redirect(url_for('control_serial'))
    elif task == 'i2c':
       return redirect(url_for('control_i2c'))

@app.route('/do/reboot')
def do_reboot():
    os.system("sudo reboot")
    return redirect('/')

@app.route('/api/get/info')
def api_get_info():
    cpu_temp, cpu_usage, device_temp, memory, storage, boot_time, uptime, humid, fan = getSystemInfo()
    info = {"dev_temp":device_temp,"dev_humid":humid,"fan":fan,"temp":cpu_temp,"storage":storage,"cpu":cpu_usage,"memory":memory,"uptime":uptime,"last":boot_time}
    return json.dumps(info)

@app.route('/api/get/time')
def get_time():
    datetime = times.now()
    day = int(datetime.strftime("%w"))
    month = int(datetime.strftime("%m"))
    hari = ['Minggu','Senin','Selasa','Rabu','Kamis','Jum\'at','Sabtu']
    bulan = ['Januari','Februari','Maret','April','Mei','Juni','Juli','Agustus','September','Oktober','November','Desember']
    datetime = datetime.strftime(hari[day] + ", %d " + bulan[month-1] + " %Y %H:%M:%S")
    return datetime

@app.route('/api/project')
def api_project():
    name, port, gateway, node, display, protocol = getProject()
    data = {"name":name,"port":port,"gateway":gateway,"node":node,"display":display,"protocol":protocol}
    data = json.dumps(data)
    return data

@app.route('/api/project/session')
def api_project_session():
    id_user, username, level, state = checkSession(1)
    data = {"id":id_user,"username":username,"level":level,"state":state}
    data = json.dumps(data)
    return data

@app.route('/api/project/login', methods=['POST'])
def api_project_login():
    username2 = request.form.get('username')
    password2 = request.form.get('password')
    flag = request.form.get('flag')
    check = login_process(username2, password2, flag)
    return check

@app.route('/api/project/logout', methods=['POST'])
def api_project_logout():
    id = request.form.get('id')
    print(id)
    user_db.updateLogout(id,1)
    return "1"

@app.route('/api/service/<name>')
def api_service(name):
    fetch = getServiceByName(name)
    data = {"name":name,"id":fetch['id']}
    data = json.dumps(data)
    return data

@app.route('/api/service/delete/<id>')
def api_service_delete(id):
    deletes = services.delete(id)
    return deletes

@app.route('/api/service', methods=['POST'])
def api_service_post():
    nama = request.form.get('name')
    path = request.form.get('path')
    command = request.form.get('command')
    nama2 = nama.replace(" ","")
    inserts = services.insert(nama2,path,command)
    return inserts

@app.route('/logout')
def logout():
    id_user, username, level, status = checkSession(0)
    user_db.updateLogout(id_user, 0)
    return redirect(url_for('index'))

# @app.errorhandler(Exception)
# def handle_exception(e):
#     dashboard_port, dashboard_name = getDashboardSetting()
#     id_user, username, level, status = checkSession(0)
#     rule = str(request.url_rule)
#     error = e
#     return render_template('error.html', rule=rule, username=username, dashboard_name=dashboard_name, status=status, error=error)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=dashboard_port, debug=True)
