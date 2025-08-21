import asyncio
import datetime
import sys

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, SystemServiceDB
from sql_connex import info, wireless
sys.path.append('/home/connex/project/function')
from dbFunction import dbFunction
from serviceProjectFunction import ServiceProjectFunction
sys.path.append('/home/connex/platform/function')
from networkFunction import networkFunction

page_updated = {}
update_task = None
command_lock = asyncio.Lock()
active_page = 1

class DisplayFunction():
    class MainFunction():
        async def send_command(loop, ser, command, global_variable):
            print(command)
            try:
                async with command_lock:
                    end = b'\xff\xff\xff'
                    if len(command) > 0:
                        command_full = b''
                        for x in range(len(command)):
                            com = command[x]
                            encodes = com.encode('ascii')
                            commands = encodes + end
                            command_full += commands
                    print(command_full)
                    await loop.run_in_executor(None, lambda: ser.write(command_full))
            except Exception as e:
                global_variable["logger"].debug(f"Error Send Serial : {e}")
                ServiceProjectFunction.handlingServiceError('Display', str(e), global_variable)
            
        async def read_serial(loop, ser, global_variable):
            counts = 0
            while True:
                counts+=1
                try:
                    response = await loop.run_in_executor(None, lambda: ser.read(8))
                    if response:
                        await DisplayFunction.MainFunction.handle_page_change(loop, ser, response, global_variable)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    ServiceProjectFunction.handlingServiceError('Display', str(e), global_variable)
                    global_variable["logger"].debug(f"Error Read Serial : {e}")
        
        async def setGroup(loop, ser, state_name, last_name, last_update, global_variable):
            command = []
            command.append(last_name + '.txt=\"' + str(last_update) + '\"')
            command.append(state_name + '.pco=0')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
        
        async def setServiceError(loop, ser, name, global_variable):
            command = []
            command.append(name + '.txt=\"Error\"')
            command.append(name + '.bco=64512')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable) 
        
        async def setServiceRunning(loop, ser, name, global_variable):
            command = []
            command.append(name + '.txt=\"Running\"')
            command.append(name + '.bco=2016')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable) 

        async def setServiceStop(loop, ser, name, global_variable):
            command = []
            command.append(name + '.txt=\"Stop\"')
            command.append(name + '.bco=63488')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable) 
        
        async def stateProcessSensor(loop, ser, state_name, last_name, last_update, state_sensor, service, global_variable):
            if service == 'active':

                await DisplayFunction.MainFunction.setGroup(loop, ser, state_name, last_name, last_update, global_variable)
                if 'Success' in state_sensor:

                    await DisplayFunction.MainFunction.setServiceRunning(loop, ser, state_name, global_variable)
                    state = 1
                else:
                    await DisplayFunction.MainFunction.setServiceError(loop, ser, state_name, global_variable)
                    state = 0
            else:

                await DisplayFunction.MainFunction.setGroup(loop, ser, state_name, last_name, "N/A", global_variable)
                await DisplayFunction.MainFunction.setServiceStop(loop, ser, state_name, global_variable)
                state = 2
            return state
        
        async def handle_page_change(loop, ser, response, global_variable):
            global active_page, update_task

            page_id = None
            if 0x01 in response:
                page_id = 1
            elif 0x02 in response:
                page_id = 2
            elif 0x03 in response:
                page_id = 3
            elif 0x04 in response:
                page_id = 4
            elif 0x05 in response:
                page_id = 5
            elif 0x06 in response:
                page_id = 6
            elif 0x07 in response:
                page_id = 7

            if page_id is not None and page_id != active_page:
                active_page = page_id
                await DisplayFunction.update_page(loop, ser, page_id, global_variable)
                page_updated[page_id] = True

                if update_task is not None:
                    update_task.cancel()
                    try:
                        await update_task
                    except asyncio.CancelledError:
                        pass

                update_task = asyncio.create_task(DisplayFunction.MainFunction.update_values_periodically(loop, ser, global_variable))

            if page_id is not None:
                if page_id != active_page:
                    active_page = page_id
                    await DisplayFunction.update_page(loop, ser, page_id, global_variable)
                    page_updated[page_id] = True
                    asyncio.create_task(DisplayFunction.MainFunction.update_values_periodically(loop, ser, global_variable))


        async def update_values_periodically(loop, ser, global_variable):
            while True:
                await DisplayFunction.NavbarPage.content(loop, ser, global_variable)

                if active_page == 1:
                    await DisplayFunction.HomePage.content(loop, ser, global_variable)
                elif active_page == 3:
                    await DisplayFunction.RtuSensorPage_1.content(loop, ser, global_variable)
                elif active_page == 4:
                    await DisplayFunction.ACLoadOutput.content(loop, ser, global_variable)
                elif active_page == 5:
                    await DisplayFunction.RtuSensorPage_2.content(loop, ser, global_variable)
                elif active_page == 6:
                    await DisplayFunction.RtuSensorPage_3.content(loop, ser, global_variable)
                elif active_page == 7:
                    await DisplayFunction.RtuSensorPage_4.content(loop, ser, global_variable)
                
                await asyncio.sleep(0.5)


    class NavbarPage():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "Navbar Page"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            navbar_data = DisplayFunction.NavbarPage.getSystemInfo()
            command = []
            command.append(navbar_data['tempIcon'])
            command.append('id.txt=\"' + navbar_data['id'] + '\"')
            command.append('name.txt=\"' + navbar_data['device'] + '\"')
            command.append('date.txt=\"' + navbar_data['date'] + '\"')
            command.append('time.txt=\"' + navbar_data['time'] + '\"')
            command.append('suhu.txt=\"' + str(navbar_data["suhu"][0]["value"]) + ' C\"')
            command.append('fan.txt=\"' + str(navbar_data["fan"][0]["value"]) + ' %\"')
            command.append('version.txt=\"' + str(navbar_data['version']) + '\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)

        def getSystemInfo():
            result = {'id': 'N/A', 'device': 'N/A', 'date': 'N/A', 'time': 'N/A', 'suhu': 'N/A', 'fan': 'N/A', 'version': 'N/A', "tempIcon": 'suhu.pco=63488'}
            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
            times = now.strftime("%H:%M:%S")
            days = now.strftime("%d/%m/%y")
            navbar_page = dbFunction.getDeviceSetting()
            result['id'] = navbar_page.get('uid', 'N/A')
            result['device'] = navbar_page.get('name', 'N/A')
            result['version'] = f"Firmware Version {navbar_page.get('version', 'N/A')}"
            result['date'] = str(days)
            result['time'] = str(times)
            result['suhu'] = info.selectByName("temp")
            result['fan'] = info.selectByName("fan")
            if result['suhu'][0]["value"] != 'N/A':
                if float(result["suhu"][0]["value"]) > 70.0:
                    result['tempIcon'] = 'suhu.pco=63488'
                else:
                    result['tempIcon'] = 'suhu.pco=65535'
            else:
                result['tempIcon'] = 'suhu.pco=63488'
            return result
        
    
    class HomePage():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "Home Page"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            home_page_data = DisplayFunction.HomePage.getSystemInfo()
            command = []
            command.append(home_page_data['wifiIcon'])
            command.append('home.ssid.txt=\"' + home_page_data['ssid'] + '\"')
            command.append('home.ipwlan.txt=\"' + home_page_data['ipwlan'] + '\"')
            command.append('home.ipeth.txt=\"' + home_page_data['ipeth'] + '\"')
            command.append('home.uptime.txt=\"'+ home_page_data["uptime"][0]["value"] + '\"')
            command.append('home.lastboot.txt=\"'+ home_page_data["lastboot"][0]["value"] + '\"')
            command.append('home.cpu.txt=\"'+ home_page_data["cpu"][0]["value"] + '\"')
            command.append('home.cputemp.txt=\"'+ home_page_data["cputemp"][0]["value"] + ' C\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

        def getSystemInfo():
            result = {'ssid': 'N/A','ipwlan': 'N/A','ipeth': 'N/A', 'uptime': 'N/A', 'lastboot': 'N/A', 'cpu': 'N/A', 'cputemp': 'N/A', 'temp': 'N/A', 'version': 'N/A', 'wifiIcon': 'home.logowlan.pic=7'}
            version = dbFunction.getDeviceSetting()
            wireless_mode = wireless.selectAll()

            result['ipeth'] = networkFunction.getInterface('eth0')
            result['ipwlan'] = networkFunction.getInterface('wlan0')
            result['version'] = f"Firmware Version {version.get('version', 'N/A')}"
            result['lastboot'] = info.selectByName("boot_time")
            result['cpu'] = info.selectByName("cpu_usage")
            result['uptime'] = info.selectByName("uptime")
            result['cputemp'] = info.selectByName("cpu_temp")
            result['temp'] = info.selectByName("temp")
            if int(wireless_mode[0]["state"]) == 0:
                result['wifiIcon'] = 'home.logowlan.pic=7'
                result['ssid'] = networkFunction.getSSID('wlan0')
            elif int(wireless_mode[0]["state"]) == 1:
                result['wifiIcon'] = 'home.logowlan.pic=10'
                result['ssid'] = wireless_mode[0]["ssid"]
            return result


    class RtuSensorPage_1():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "RTU Sensor Page 1"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            rtu_sensor_data = await DisplayFunction.RtuSensorPage_1.getSystemInfo(loop, ser, global_variable)
            command = []
            # command.append('rtu1.supplyVoltRtu1.txt=\"' + str(rtu_sensor_data['supplyVoltRtu1']) + ' V\"')
            # command.append('rtu1.mtrStateRtu1.txt=\"' + str(rtu_sensor_data['motorRunStateRtu1']) + '\"')
            # command.append('rtu1.runFreqRtu1.txt=\"' + str(rtu_sensor_data['runningFreqRtu1']) + '\"')
            # command.append('rtu1.intkPressRtu1.txt=\"' + str(rtu_sensor_data['intakePressRtu1']) + '\"')
            # command.append('rtu1.motorTempRtu1.txt=\"' + str(rtu_sensor_data['motorTempRtu1']) + '\"')
            # command.append('rtu1.ltchdAlrm0Rtu1.txt=\"' + str(rtu_sensor_data['latchedAlarm0Rtu1']) + '\"')
            command.append('rtu1.waterLevelRtu1.txt=\"' + str(rtu_sensor_data['waterLevelRtu1']) + '\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

    
        async def getSystemInfo(loop, ser, global_variable):
            system_info = SensorListDB.selectByGroupNumberFull("1")
            sensor_data = {}
            if system_info:
                sensor_data = {}
                for row in system_info:
                    sensor_data[row['sensor_id']] = row['value']
            service_condition = ServiceProjectFunction.getServiceInfo("sensor1")

            state_rtu = await  DisplayFunction.MainFunction.stateProcessSensor(loop, ser, "rtu1.statertu1", "rtu1.lastrtu1", service_condition['last_update'], 
                                                                               service_condition['log'], service_condition['state'], global_variable)
            
            if state_rtu == 0:
                sensor_data['supplyVoltRtu1'], sensor_data['motorRunStateRtu1'], sensor_data['runningFreqRtu1'] = 0, 0, 0
                sensor_data['intakePressRtu1'], sensor_data['motorTempRtu1'], sensor_data['latchedAlarm0Rtu1'] =  0, 0, 0
            elif state_rtu == 2:
                sensor_data['supplyVoltRtu1'], sensor_data['motorRunStateRtu1'], sensor_data['runningFreqRtu1'] = 'N/A', 'N/A', 'N/A'
                sensor_data['intakePressRtu1'], sensor_data['motorTempRtu1'], sensor_data['latchedAlarm0Rtu1'] = 'N/A', 'N/A', 'N/A'
            return sensor_data
    
    
    class RtuSensorPage_2():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "RTU Sensor Page 2"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            rtu_sensor_data = await DisplayFunction.RtuSensorPage_2.getSystemInfo(loop, ser, global_variable)
            command = []
            # command.append('rtu2.supplyVoltRtu2.txt=\"' + str(rtu_sensor_data['supplyVoltRtu2']) + ' V\"')
            # command.append('rtu2.mtrStateRtu2.txt=\"' + str(rtu_sensor_data['motorRunStateRtu2']) + '\"')
            # command.append('rtu2.runFreqRtu2.txt=\"' + str(rtu_sensor_data['runningFreqRtu2']) + '\"')
            # command.append('rtu2.intkPressRtu2.txt=\"' + str(rtu_sensor_data['intakePressRtu2']) + '\"')
            # command.append('rtu2.motorTempRtu2.txt=\"' + str(rtu_sensor_data['motorTempRtu2']) + '\"')
            # command.append('rtu2.ltchdAlrm0Rtu2.txt=\"' + str(rtu_sensor_data['latchedAlarm0Rtu2']) + '\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

    
        async def getSystemInfo(loop, ser, global_variable):
            system_info = SensorListDB.selectByGroupNumberFull("1")
            sensor_data = {}
            if system_info:
                sensor_data = {}
                for row in system_info:
                    sensor_data[row['sensor_id']] = row['value']
            service_condition = ServiceProjectFunction.getServiceInfo("sensor1")

            state_rtu = await  DisplayFunction.MainFunction.stateProcessSensor(loop, ser, "rtu2.statertu2", "rtu2.lastrtu2", service_condition['last_update'], 
                                                                               service_condition['log'], service_condition['state'], global_variable)
            
            if state_rtu == 0:
                sensor_data['supplyVoltRtu2'], sensor_data['motorRunStateRtu2'], sensor_data['runningFreqRtu2'] = 0, 0, 0
                sensor_data['intakePressRtu2'], sensor_data['motorTempRtu2'], sensor_data['latchedAlarm0Rtu2'] =  0, 0, 0
            elif state_rtu == 2:
                sensor_data['supplyVoltRtu2'], sensor_data['motorRunStateRtu2'], sensor_data['runningFreqRtu2'] = 'N/A', 'N/A', 'N/A'
                sensor_data['intakePressRtu2'], sensor_data['motorTempRtu2'], sensor_data['latchedAlarm0Rtu2'] = 'N/A', 'N/A', 'N/A'
            return sensor_data
    
    
    class RtuSensorPage_3():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "RTU Sensor Page 3"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            rtu_sensor_data = await DisplayFunction.RtuSensorPage_3.getSystemInfo(loop, ser, global_variable)
            command = []
            # command.append('rtu3.supplyVoltRtu3.txt=\"' + str(rtu_sensor_data['supplyVoltRtu3']) + ' V\"')
            # command.append('rtu3.mtrStateRtu3.txt=\"' + str(rtu_sensor_data['motorRunStateRtu3']) + '\"')
            # command.append('rtu3.runFreqRtu3.txt=\"' + str(rtu_sensor_data['runningFreqRtu3']) + '\"')
            # command.append('rtu3.intkPressRtu3.txt=\"' + str(rtu_sensor_data['intakePressRtu3']) + '\"')
            # command.append('rtu3.motorTempRtu3.txt=\"' + str(rtu_sensor_data['motorTempRtu3']) + '\"')
            # command.append('rtu3.ltchdAlrm0Rtu3.txt=\"' + str(rtu_sensor_data['latchedAlarm0Rtu3']) + '\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

    
        async def getSystemInfo(loop, ser, global_variable):
            system_info = SensorListDB.selectByGroupNumberFull("1")
            sensor_data = {}
            if system_info:
                sensor_data = {}
                for row in system_info:
                    sensor_data[row['sensor_id']] = row['value']
            service_condition = ServiceProjectFunction.getServiceInfo("sensor1")

            state_rtu = await  DisplayFunction.MainFunction.stateProcessSensor(loop, ser, "rtu3.statertu3", "rtu3.lastrtu3", service_condition['last_update'], 
                                                                               service_condition['log'], service_condition['state'], global_variable)
            
            if state_rtu == 0:
                sensor_data['supplyVoltRtu3'], sensor_data['motorRunStateRtu3'], sensor_data['runningFreqRtu3'] = 0, 0, 0
                sensor_data['intakePressRtu3'], sensor_data['motorTempRtu3'], sensor_data['latchedAlarm0Rtu3'] =  0, 0, 0
            elif state_rtu == 2:
                sensor_data['supplyVoltRtu3'], sensor_data['motorRunStateRtu3'], sensor_data['runningFreqRtu3'] = 'N/A', 'N/A', 'N/A'
                sensor_data['intakePressRtu3'], sensor_data['motorTempRtu3'], sensor_data['latchedAlarm0Rtu3'] = 'N/A', 'N/A'
            return sensor_data
    

    class RtuSensorPage_4():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "RTU Sensor Page 4"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            rtu_sensor_data = await DisplayFunction.RtuSensorPage_4.getSystemInfo(loop, ser, global_variable)
            command = []
            # command.append('rtu4.supplyVoltRtu4.txt=\"' + str(rtu_sensor_data['supplyVoltRtu4']) + ' V\"')
            # command.append('rtu4.mtrStateRtu4.txt=\"' + str(rtu_sensor_data['motorRunStateRtu4']) + '\"')
            # command.append('rtu4.runFreqRtu4.txt=\"' + str(rtu_sensor_data['runningFreqRtu4']) + '\"')
            # command.append('rtu4.intkPressRtu4.txt=\"' + str(rtu_sensor_data['intakePressRtu4']) + '\"')
            # command.append('rtu4.motorTempRtu4.txt=\"' + str(rtu_sensor_data['motorTempRtu4']) + '\"')
            # command.append('rtu4.ltchdAlrm0Rtu4.txt=\"' + str(rtu_sensor_data['latchedAlarm0Rtu4']) + '\"')
            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

    
        async def getSystemInfo(loop, ser, global_variable):
            system_info = SensorListDB.selectByGroupNumberFull("1")
            sensor_data = {}
            if system_info:
                sensor_data = {}
                for row in system_info:
                    sensor_data[row['sensor_id']] = row['value']
            service_condition = ServiceProjectFunction.getServiceInfo("sensor1")

            state_rtu = await  DisplayFunction.MainFunction.stateProcessSensor(loop, ser, "rtu4.statertu4", "rtu4.lastrtu4", service_condition['last_update'], 
                                                                               service_condition['log'], service_condition['state'], global_variable)
            
            if state_rtu == 0:
                sensor_data['supplyVoltRtu4'], sensor_data['motorRunStateRtu4'], sensor_data['runningFreqRtu4'] = 0, 0, 0
                sensor_data['intakePressRtu4'], sensor_data['motorTempRtu4'], sensor_data['latchedAlarm0Rtu4'] =  0, 0, 0
            elif state_rtu == 2:
                sensor_data['supplyVoltRtu4'], sensor_data['motorRunStateRtu4'], sensor_data['runningFreqRtu4'] = 'N/A', 'N/A', 'N/A'
                sensor_data['intakePressRtu4'], sensor_data['motorTempRtu4'], sensor_data['latchedAlarm0Rtu4'] = 'N/A', 'N/A'
            return sensor_data
    
    class ACLoadOutput():
        async def content(loop, ser, global_variable):
            timestamp = times.getDatetime()
            logService = "AC Load Output Page"
            global_variable["logger"].debug(f"{timestamp} - {logService}")
            acload_output_data = await DisplayFunction.ACLoadOutput.getSystemInfo(loop, ser, global_variable)
            command = []
            command.append('acload.acLoadCurrent1.txt=\"' + str(acload_output_data['acLoadCurrent1']) + ' A\"')
            command.append('acload.acLoadCurrent2.txt=\"' + str(acload_output_data['acLoadCurrent2']) + ' A\"')
            command.append('acload.acLoadCurrent3.txt=\"' + str(acload_output_data['acLoadCurrent3']) + ' A\"')
            command.append('acload.acLoadCurrent4.txt=\"' + str(acload_output_data['acLoadCurrent4']) + ' A\"')
            command.append('acload.acLoadCurrent5.txt=\"' + str(acload_output_data['acLoadCurrent5']) + ' A\"')


            await DisplayFunction.MainFunction.send_command(loop, ser, command, global_variable)
            SystemServiceDB.updateStatusByName(logService, timestamp, "nearon_display")

        async def getSystemInfo(loop, ser, global_variable):
            system_info = SensorListDB.selectByGroupNumberFull("3")
            sensor_data = {}
            if system_info:
                sensor_data = {}
                for row in system_info:
                    sensor_data[row['sensor_id']] = row['value']
            service_condition = ServiceProjectFunction.getServiceInfo("sensor3")
            
            # Hanya jalankan stateProcessSensor jika ser tidak None
            if ser is not None:
                state_ac = await  DisplayFunction.MainFunction.stateProcessSensor(loop, ser, "acload.stateacload", "acload.lastacload", service_condition['last_update'], 
                                                                                   service_condition['log'], service_condition['state'], global_variable)
                if state_ac == 0:
                    sensor_data['acLoadCurrent1'], sensor_data['acLoadCurrent2'], sensor_data['acLoadCurrent3'] = 0, 0, 0
                    sensor_data['acLoadCurrent4'], sensor_data['acLoadCurrent5'] =  0, 0
            
                elif state_ac == 2:
                    sensor_data['acLoadCurrent1'], sensor_data['acLoadCurrent2'], sensor_data['acLoadCurrent3'] = 'N/A', 'N/A', 'N/A'
                    sensor_data['acLoadCurrent4'], sensor_data['acLoadCurrent5'] = 'N/A', 'N/A'
                    
            else:
                # Jika ser None, gunakan nilai default
                sensor_data['acLoadCurrent1'] = sensor_data.get('acLoadCurrent1', 0)
                sensor_data['acLoadCurrent2'] = sensor_data.get('acLoadCurrent2', 0)
                sensor_data['acLoadCurrent3'] = sensor_data.get('acLoadCurrent3', 0)
                sensor_data['acLoadCurrent4'] = sensor_data.get('acLoadCurrent4', 0)
                sensor_data['acLoadCurrent5'] = sensor_data.get('acLoadCurrent5', 0)

                
            return sensor_data



    async def update_page(loop, ser, page_id, global_variable):
        if page_id == 1:  # Home Page
            await DisplayFunction.HomePage.content(loop, ser, global_variable)
        elif page_id == 3:  # RTU Sensor Page 1
            await DisplayFunction.RtuSensorPage_1.content(loop, ser, global_variable)
        elif page_id == 4:  # AC Load Output
            await DisplayFunction.ACLoadOutput.content(loop, ser, global_variable)
        elif page_id == 5:  # RTU Sensor Page 2
            await DisplayFunction.RtuSensorPage_2.content(loop, ser, global_variable)
        elif page_id == 6:  # RTU Sensor Page 3
            await DisplayFunction.RtuSensorPage_3.content(loop, ser, global_variable)
        elif page_id == 7:  # RTU Sensor Page 4
            await DisplayFunction.RtuSensorPage_4.content(loop, ser, global_variable)

