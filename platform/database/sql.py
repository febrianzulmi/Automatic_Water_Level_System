import mysql.connector, json, sys, os
sys.path.append('/home/connex/library')
from SynapsisLibrary import *

def openDB():
    with open('/home/connex/platform/database/db.json', 'r') as f:
        db = json.load(f)
        host = db['host']
        database = db['database']
        username = db['username']
        password = db['password']
    f.close()
    return host, database, username, password

host, database, username, password = openDB()

class user_db():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM user"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(usernames):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM user where username=%s"
        value = (usernames,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def checkLogin(flag):
        connection = sql.connect(host, database, username, password)
        if int(flag) == 0:
           query = "SELECT * FROM user where state=1"
        else:
           query = "SELECT * FROM user where state_project=1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insert(usernames,passwords,level,create):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO user (username,password,level,state,last_login,state_project,last_project,create_at) VALUES (%s, %s, %s, 0, %s, 0, %s, %s)"
        value = (usernames,passwords,level,create,create,create)
        action = sql.execute(connection, query, value)
        return action

    def updateLogin(id, last_login, flag):
        connection = sql.connect(host, database, username, password)
        if int(flag) == 0:
           query = "UPDATE user set state=1, last_login=%s WHERE id=%s"
        else:
           query = "UPDATE user set state_project=1, last_project=%s WHERE id=%s"
        value = (last_login, id)
        action = sql.execute(connection, query, value)
        return action

    def updateLogout(id, flag):
        connection = sql.connect(host, database, username, password)
        if int(flag) == 0:
           query = "UPDATE user set state=0 WHERE id=%s"
        elif int(flag) == 1:
           query = "UPDATE user set state_project=0 WHERE id=%s"
        else:
           query = "UPDATE user set state=0, state_project=0 WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM user WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class interface():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM interface"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM interface where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(name,tipe,mac,ip):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO interface (name,tipe,mac,ip) VALUES (%s, %s, %s, %s)"
        value = (name,tipe,mac,ip)
        action = sql.execute(connection, query, value)
        return action

    def update(name,tipe,mac,ip):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE interface set tipe=%s, mac=%s, ip=%s WHERE name=%s"
        value = (tipe,mac,ip,name)
        action = sql.execute(connection, query, value)
        return action

    def updateFull(name,tipe,con,mac,ip,subnet,gateway,dns):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE interface set tipe=%s, conn=%s, mac=%s, ip=%s, subnet=%s, gateway=%s, dns=%s WHERE name=%s"
        value = (tipe,con,mac,ip,subnet,gateway,dns,name)
        action = sql.execute(connection, query, value)
        return action

    def delete(name):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM interface WHERE name=%s"
        value = (name,)
        action = sql.execute(connection, query, value)
        return action

class wireless():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM wireless where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def update(name,interface,state,ssid,passw,channel):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE wireless set state=%s, interface=%s, ssid=%s, password=%s, channel=%s WHERE name=%s"
        value = (state,interface,ssid,passw,channel,name)
        action = sql.execute(connection, query, value)
        return action

class dhcp():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM dhcp where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE dhcp set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class info():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM info where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE info set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class fan():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM fan where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE fan set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class identity():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM identity where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE identity set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class dashboard():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM dashboard where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE dashboard set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class snmp():
    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT value FROM snmp where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def updateByName(name,value):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE snmp set value=%s WHERE name=%s"
        value = (value,name)
        action = sql.execute(connection, query, value)
        return action

class ntp():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM ntp where id = 1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def update(server, ip):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE ntp set server=%s, ip_ntp=%s WHERE id=1"
        value = (server, ip)
        action = sql.execute(connection, query, value)
        return action

class project():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM project where id = 1"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def insert(name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO project (id,name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display) VALUES (1, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        value = (name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display)
        action = sql.execute(connection, query, value)
        return action

    def update(name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE project set name=%s, port=%s, gateway=%s, node=%s, display=%s, protocol=%s, id_dashboard=%s, id_node=%s, id_gateway=%s, id_auth=%s, id_buffer=%s, id_display=%s WHERE id=1"
        value = (name,port,gateway,node,display,protocol,id_dashboard,id_node,id_gateway,id_auth,id_buffer,id_display)
        action = sql.execute(connection, query, value)
        return action

    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM project WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class crontabs():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM crontab"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM crontab where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(name, schedule, command):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO crontab (name,schedule,command,state) VALUES (%s, %s, %s, 1)"
        value = (name,schedule, command)
        action = sql.execute(connection, query, value)
        return action

    def update(name,schedule,command,state,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE crontab set name=%s, schedule=%s, command=%s, state=%s WHERE id=%s"
        value = (name,schedule,command,state,id)
        action = sql.execute(connection, query, value)
        return action

    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM crontab WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action

class services():
    def select():
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM services"
        fetchall = sql.selectNoInput(connection, query)
        return fetchall

    def selectByName(name):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM services where name=%s"
        value = (name,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def selectOne(id):
        connection = sql.connect(host, database, username, password)
        query = "SELECT * FROM services where id=%s"
        value = (id,)
        fetchall = sql.selectWithInput(connection, query, value)
        return fetchall

    def insert(name, path, command):
        connection = sql.connect(host, database, username, password)
        query = "INSERT INTO services (name,path,command,state,autostart) VALUES (%s, %s, %s, 1, 1)"
        value = (name,path,command)
        action = sql.execute(connection, query, value)
        return action

    def update(name,path,command,state,autostart,id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE services set name=%s, path=%s, command=%s, state=%s, autostart=%s WHERE id=%s"
        value = (name,path,command,state,autostart,id)
        action = sql.execute(connection, query, value)
        return action

    def updateService(name, path, command, id):
        connection = sql.connect(host, database, username, password)
        query = "UPDATE services set name=%s, path=%s, command=%s WHERE id=%s"
        value = (name, path, command, id)
        action = sql.execute(connection, query, value)
        return action

    def delete(id):
        connection = sql.connect(host, database, username, password)
        query = "DELETE FROM services WHERE id=%s"
        value = (id,)
        action = sql.execute(connection, query, value)
        return action
