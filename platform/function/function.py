import shutil, subprocess, os, psutil, time, datetime, sys, random, string
import netifaces as ni
from netifaces import AF_INET, AF_INET6, AF_LINK, AF_PACKET, AF_BRIDGE
from werkzeug.security import generate_password_hash, check_password_hash
sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/platform/database')
from sql import user_db, fan, dashboard, interface, project, identity, services, info
from sql_project import *

def getServiceByName(name):
   getData = services.selectByName(name)
   serviceByName = getData[0]
   return serviceByName

def login_process(username, password, flag):
    fetch = user_db.selectOne(username)
    usernames = ''
    passwords = ''
    for row in fetch:
        id = row['id']
        usernames = row['username']
        passwords = row['password']
    if usernames == username:
       check = check_password_hash(passwords, password)
       if check == True:
          datetime = times.getDatetime()
          user_db.updateLogin(id, datetime, flag)
          return "2"
       else:
          return "1"
    else:
       return "0"

def checkSession(flag):
    fetch = user_db.checkLogin(flag)
    if len(fetch) > 0:
       for row in fetch:
           id_user = row['id']
           username = row['username']
           level = row['level']
           if int(flag) == 0:
              state = row['state']
           else:
              state = row['state_project']
    else:
       id_user = 0
       username = ''
       level = 0
       state = 0
    return id_user, username, level, state

# def offSession():
#     fetch = user_db.select()
#     if len(fetch) > 0:
#        for row in fetch:
#            id = row[0]
#            user_db.updateLogout(id,2)

# New Function OffSession
def offSession():
   getData = user_db.select()
   id = {}
   if getData :
      for item in getData:
         id = item['id']
         user_db.updateLogout(id,2)

def getDashboardSetting():
    try:
      get = dashboard.selectByName("name")
      for i in get:
          dashboard_name = i['value']
      get = dashboard.selectByName("port")
      for i in get:
          dashboard_port = i['value']
    except Exception as e:
      dashboard_port= '80'
      dashboard_name = 'Connex'
    return dashboard_port, dashboard_name

def getFanSetting():
    min_temp, max_temp = 25, 40
    min_fan, max_fan = 0, 100
    try:
      get = fan.selectByName("min_temp")
      for i in get:
          min_temp = int(i['value'])
      get = fan.selectByName("max_temp")
      for i in get:
          max_temp = int(i['value'])
      get = fan.selectByName("min_fan")
      for i in get:
          min_fan = int(i['value'])
      get = fan.selectByName("max_fan")
      for i in get:
          max_fan = int(i['value'])
    except Exception as e:
      min_temp, max_temp = 25, 40
      min_fan, max_fan = 0, 100
    return min_temp, max_temp, min_fan, max_fan

def getInterface(interface):
    state = subprocess.check_output("cat /sys/class/net/"+interface+"/operstate", shell=True)
    state = state.decode("utf-8")
    state = state.replace("\n","")
    if "eth" in interface:
       tipe = 0
    else:
       tipe = 1
    iface = ni.ifaddresses(interface)
    mac = iface[17][0]['addr']
    if len(iface) == 3:
       ip = ni.ifaddresses(interface)[AF_INET][0]['addr']
    else:
       ip = '-'
    return tipe, state, mac, ip

def getIface():
    get = interface.select()
    data = []
    if len(get)>0:
       for i in get:
           iface = i['name']
           data.append(iface)
    return data, len(get)

def getInterfaces():
    iface, length = getIface()
    data = []
    for x in range(length):
        name = iface[x]
        tipe, state, mac, ip = getInterface(name)
        data2 = interface.selectOne(name)
        for i in data2:
            con = i[2]
            if tipe == 0:
               data_json = {"name":name,"tipe":tipe,"state":state,"con":con,"mac":mac,"ip":ip}
            else:
               mode = i[3]
               ssid = getSSID(name)
               data_json = {"name":name,"tipe":tipe,"state":state,"mode":mode,"con":con,"mac":mac,"ip":ip,"ssid":ssid}
            data.append(data_json)
    return data, len(data)

def getProject():
    get = project.select()
    if len(get) > 0:
       for i in get:
           protocol = i['protocol']
           display = i['display']
           name = i['name']
           port = i['port']
           gateway = i['gateway']
           node = i['node']
    else:
       port = ''
       name = ''
       gateway = 0
       node = 0
       display = 0
       protocol = 0
    return name, port, gateway, node, display, protocol

def getIdentity():
    get = identity.selectByName("hostname")
    for i in get:
          hostname = i['value']
    get = identity.selectByName("password")
    for i in get:
          passw = i['value']
    return hostname, passw

def getSSID(interface):
    #ssid = os.popen("iw dev " + interface + " link | grep SSID | awk '{print $2}'").read()
    ssid = os.popen("iw dev " + interface + " link | grep SSID").read()
    ssid = ssid.replace('SSID:','')
    ssid = ssid.replace('\n','')
    ssid = ssid.replace('\t ','')
    if ssid == '':
       ssid = '-'
    return ssid

def getSystemInfo():
    def getValues(param):
        value = 'N/A'
        data = info.selectByName(param)
        for i in data:
            value = i['value']
        return value
    cpu_temp = getValues("cpu_temp")
    cpu_usage = getValues("cpu_usage")
    device_temp = getValues("temp")
    memory = getValues("memory")
    storage = getValues("storage")
    boot_time = getValues("boot_time")
    uptime = getValues("uptime")
    humid = getValues("humidity")
    fan = getValues("fan")
    return cpu_temp, cpu_usage, device_temp, memory, storage, boot_time, uptime, humid, fan

def getNetworkInfo():
    data, length = getIface()
    states = []
    macs = []
    ip = []
    cons = []
    dbs = []
    data_wifi = []
    configs = []
    for i in range(length):
        tipe, state, mac, curr_ip = getInterface(data[i])
        fetch = interface.selectOne(data[i])
        get = subprocess.check_output("ifconfig " + data[i], shell=True)
        get = get.decode("utf-8")
        get = get.split("\n")
        configs.append(get)
        if len(fetch) > 0:
          for x in fetch:
              name = x['name']
              tipe = x['tipe']
              conn = x['conn']
              addr = x['ip']
              subnet = x['subnet']
              gw = x['gateway']
              dns = x['dns']
              db = {'name':name,'tipe':tipe,'conn':conn,'addr':addr,'sb':subnet,'gw':gw,'dns':dns}
              dbs.append(db)
        macs.append(mac)
        ip.append(curr_ip)
        states.append(state)
        cons.append(conn)
        if "wlan" in data[i]:
           data_wifi.append(data[i])
    return data, length, states, macs, ip, cons, dbs, data_wifi, configs

def getSNMP():
    try:
      get = snmp.selectByName("community")
      for i in get:
          snmp_community = i['value']
      get = snmp.selectByName("user")
      for i in get:
          snmp_user = i['value']
      get = snmp.selectByName("password")
      for i in get:
          snmp_password= i['value']
    except Exception as e:
      snmp_community = 'connex'
      snmp_user = 'connex-user'
      snmp_password = 'connex-auth'
    return snmp_community, snmp_user, snmp_password

def getOID(name):
    cek = attributes.selectOne(name)
    if len(cek) > 0:
       for i in cek:
           param = i[2]
    else:
       param = ''
    return param

def base_protocol(protocol):
    if int(protocol) == 1:
       name = "http"
    elif int(protocol) == 2:
       name = "mqtt"
    elif int(protocol) == 3:
       name = "snmp"
    return name

def checkActiveService(nama):
    active =  subprocess.Popen(["systemctl", "is-active",  nama], stdout=subprocess.PIPE)
    (out, err) = active.communicate()
    active = out.decode('utf-8')
    active = active.replace('\n','')
    return active

def checkEnableService(nama):
    enable =  subprocess.Popen(["systemctl", "is-enabled",  nama], stdout=subprocess.PIPE)
    (outs, errs) = enable.communicate()
    enable = outs.decode('utf-8')
    enable = enable.replace('\n','')
    return enable

def file_read(source):
    f = open(source, 'r')
    data = f.readlines()
    f.close()
    return data

def file_write(source, data):
    f = open(source, 'w')
    f.writelines(data)
    f.close()

def checkDetailService(nama):
    detail =  subprocess.Popen("systemctl status " + nama + " | grep since", shell=True, stdout=subprocess.PIPE)
    (out, err) = detail.communicate()
    detail = out.decode('utf-8')
    detail = detail.replace('\n','')
    search1 = detail.find("since")
    search2 = detail.find("WIB")
    search3 = detail.find("ago")
    last_run = detail[search1+6:search2-1]
    since = detail[search2+5:search3]
    return last_run, since

class config():
    def hotspot(interface,ssid,passw,channel):
        path_platform = "/home/connex"
        data = file_read(path_platform + '/platform/storage/hostapd.conf.master')
        data[1] = "interface={}\n".format(interface)
        data[3] = "channel={}\n".format(channel)
        data[5] = "ssid={}\n".format(ssid)
        data[6] = "wpa_passphrase={}\n".format(passw)
        file_write('/etc/hostapd/hostapd.conf', data)

    def DHCP(value):
        base = "/home/connex"
        shutil.copy(base + '/platform/storage/dnsmasq.conf.master', '/etc/dnsmasq.conf')
        files = open("/etc/dnsmasq.conf", "a")
        files.write("\n")
        files.write("interface={}\n".format(value[0]))
        files.write("dhcp-range={},{},{},24h\n".format(value[1],value[2],value[3]))
        if value[4] != '':
           files.write("dhcp-option=3,{}".format(value[4]))
        if value[5] != '':
           files.write("dhcp-option=6,{}".format(value[5]))
        if value[6] != '':
           files.write(",{}\n".format(value[6]))
        else:
           files.write("\n")

    def network():
        shutil.copy('storage/network.master', '/etc/network/interfaces')
        f = open('/etc/network/interfaces', 'a')
        get = interface.select()
        if len(get) > 0:
           for i in range(len(get)):
               name = get[i]['name']
               tipe = get[i]['tipe']
               con = get[i]['conn']
               ip = get[i]['ip']
               gateway = get[i]['gateway']
               subnet = get[i]['subnet']
               dns = get[i]['dns']
               if con == 0:
                  if ip != "":
                     f.write('\nauto {}\n'.format(name))
                     f.write('iface {} inet static\n'.format(name))
                     f.write('\taddress {}\n'.format(ip))
                     f.write('\tnetmask {}\n'.format(subnet))
                     if gateway != "":
                        f.write('\tgateway {}\n'.format(gateway))
                     if dns != "":
                        f.write('\tdns-nameservers {}\n'.format(dns))
               else:
                  f.write('\nauto {}\n'.format(name))
                  f.write('iface {} inet dhcp\n'.format(name))
               if tipe == 1:
                  f.write('wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf\n')
        else:
          print("")
        f.close()
        os.system("service networking restart")
        os.system("service hostapd restart")
        os.system("service dnsmasq restart")

    def NTP(server, ip1, ip2, ip3):
        f = open('/etc/systemd/timesyncd.conf', 'r')
        data = f.readlines()
        f.close()
        if server == "0":
           data[14] = "NTP=id.pool.ntp.org\n"
        else:
           command = "NTP=" + ip1
           if ip2 != '':
              command = command + ' ' + str(ip2)
           if ip3 != '':
              command = command + ' ' + str(ip3)
           data[14] = command + '\n'
        f = open('storage/temp_ntp.txt', 'w')
        f.writelines(data)
        f.close()
        os.system('sudo mv storage/temp_ntp.txt /etc/systemd/timesyncd.conf')
        os.system("systemctl daemon-reload")
        os.system("systemctl restart systemd-timesyncd")

    def NTP2(server, ip):
        f = open('/etc/ntp.conf', 'r')
        data = f.readlines()
        f.close()
        if server == "1":
           data[17] = "server " + ip + " iburst\n"
           data[22] = "#pool 0.debian.pool.ntp.org iburst\n"
           data[23] = "#pool 1.debian.pool.ntp.org iburst\n"
           data[24] = "#pool 2.debian.pool.ntp.org iburst\n"
           data[25] = "#pool 3.debian.pool.ntp.org iburst\n"
        else:
           data[17] = "#server " + ip + " iburst\n"
           data[22] = "pool 0.debian.pool.ntp.org iburst\n"
           data[23] = "pool 1.debian.pool.ntp.org iburst\n"
           data[24] = "pool 2.debian.pool.ntp.org iburst\n"
           data[25] = "pool 3.debian.pool.ntp.org iburst\n"
        f = open('storage/temp_ntp.txt', 'w')
        f.writelines(data)
        f.close()
        os.system('sudo mv storage/temp_ntp.txt /etc/ntp.conf')

    def createService(path_platform, path_project, path, name_service, name_program):
       data = file_read(path_platform + '/storage/service.master')
       data[5] = "ExecStart={}\n".format("/usr/bin/python3 " + name_program)
       data[6] = "WorkingDirectory={}\n".format(path_project + path)
       file_write('/lib/systemd/system/' + name_service + '.service', data)
       inserts = services.insert(name_service, path_project + path, "/usr/bin/python3 " + name_program)
       fetch = services.selectByName(name_service)
       for x in fetch:
           id_service = x[0]
       return id_service

    def removeOID():
       base = "/home/connex"
       path_snmp =  base + "/project/sensor/oid"
       os.system("sudo rm -r " + path_snmp)
       base_oid = getOID('base')
       if base != '':
          sensors  = sensor.select()
          if len(sensors) > 0:
             shutil.copy(base + '/platform/storage/snmpd.conf.master', '/etc/snmp/snmpd.conf')
             for i in range(len(sensors)):
                 id_sensor = sensors[i][1]
                 oid = base_oid + "." + str(id_sensor)
                 os.system("sudo rm /tmp/" + oid)

    def createOID():
       base = "/home/connex"
       path_snmp =  base + "/project/sensor/oid"
       os.system("sudo rm -r " + path_snmp)
       cek = os.path.exists(path_snmp)
       if cek == False:
          os.system("sudo mkdir " + path_snmp)
       base_oid = getOID('base')
       if base != '':
          sensors  = sensor.select()
          if len(sensors) > 0:
             shutil.copy(base + '/platform/storage/snmpd.conf.master', '/etc/snmp/snmpd.conf')
             files = open("/etc/snmp/snmpd.conf", "a")
             files.write("\n")
             for i in range(len(sensors)):
                 id = sensors[i][0]
                 id_sensor = sensors[i][1]
                 oid = base_oid + "." + str(id_sensor)
                 oid_script = path_snmp + "/" + oid + ".sh"
                 cek_script = os.path.exists(oid_script)
                 if cek_script == False:
                    f = open(oid_script, "w")
                    f.write("#!/bin/bash\n")
                    f.write("cat /tmp/" + oid)
                    f.close()
                 values = logSensor.selectLastOne(id)
                 if len(values) > 0:
                    for i in values:
                        value = i[2]
                 else:
                    value = 0
                 f = open("/tmp/" + oid, "w")
                 f.write("." + str(oid))
                 f.write("\n")
                 f.write("integer")
                 f.write("\n")
                 f.write(str(value))
                 f.write("\n")
                 f.close()
                 files.write("pass ." + oid + " /bin/sh " + oid_script + "\n")
             files.close()
             os.system("sudo service snmpd restart")

