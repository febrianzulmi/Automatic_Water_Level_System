import sys
import time
import threading
import Adafruit_SSD1306
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw

sys.path.append('/home/connex/library')
from SynapsisLibrary import times
sys.path.append('/home/connex/project/database')
from query_project_db import SensorListDB, ActuatorDB, SystemServiceDB, SensorGroupDB
from dbFunction import dbFunction
sys.path.append('/home/connex/platform/function')
from networkFunction import networkFunction
sys.path.append('/home/connex/project/function')
from serviceProjectFunction import ServiceProjectFunction


page_data = {
    "systemPage": {"data": [], "timestamp": "", "lock": threading.Lock()},
    "environmentPage": {"data": [], "timestamp": "", "lock": threading.Lock()},
    "powerPage": {"data": [], "timestamp": "", "lock": threading.Lock()},
    "powerExtPage": {"data": [], "timestamp": "", "lock": threading.Lock()},
    "networkExtPage": {"data": [], "timestamp": "", "lock": threading.Lock()},
    "environmentExtPage": {"data": [], "timestamp": "", "lock": threading.Lock()}
}
current_data = []
current_timestamp = ""
data_lock = threading.Lock()
current_page_thread = None  
current_page = None  
stop_event = threading.Event() 
selected_item = 0
scroll_position = 0

class displayFunction():
    def setup(globalVariable):
        try:
            OLED = Adafruit_SSD1306.SSD1306_128_64(rst=globalVariable["oled"]["oled_reset"])
            OLED.begin()
            OLED.clear()
            OLED.display()
        except Exception as e:
            print(e)
            OLED = None
        globalVariable["oled"]["oled"] = OLED
        return globalVariable

    class mainFunction():
        def main(globalVariable):
                displayFunction.splashPage.content(globalVariable)
                time.sleep(5)
                displayFunction.homePage.content(globalVariable)
    
    class initialize():
        def content(globalVariable):
            timestamp = times.getDatetime()
            logService = "List Menu Page"
            print(f"{timestamp} - {logService}")
            SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['service']['service_name'])  
            image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
            menu_functions = {
                "Home": lambda: displayFunction.homePage.content(globalVariable),
                "System": lambda: displayFunction.systemPage.controll(globalVariable, 'systemPage'),
                "Network": lambda: displayFunction.networkPage.content(globalVariable),
                "Sensor": lambda: displayFunction.subMenuSensorPage.content(globalVariable),
                "Actuator": lambda: displayFunction.subMenuActuatorPage.content(globalVariable)
            }
            menu_items = ["Home", "System", "Network", "Sensor", "Actuator"]
            num_pages = len(menu_items)
            displayFunction.controlMenu.start_menu(num_pages, menu_functions, menu_items, globalVariable)
            globalVariable["oled"]["oled"].image(image)
            globalVariable["oled"]["oled"].display()
            return lambda: content(globalVariable)

    class threadFunction():
        def stop_current_thread():
            global current_page_thread, stop_event
            if current_page_thread is not None and current_page_thread.is_alive():
                stop_event.set()  
                current_page_thread.join()  
                stop_event.clear()  
    
    class splashPage():
        def content(globalVariable):
            timestamp = times.getDatetime()
            print(f"{timestamp} - Splash Page")
            image = Image.open(globalVariable['logo'])
            image = image.convert("L")
            image = image.resize((100, 50), Image.ANTIALIAS)
            image = image.convert("1")
            display_image = Image.new("1", (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
            pos_x = (globalVariable["oled"]["oled_width"] - 100) // 2
            pos_y = (globalVariable["oled"]["oled_height"] - 50) // 2
            display_image.paste(image, (pos_x, pos_y))
            globalVariable["oled"]["oled"].image(display_image)
            globalVariable["oled"]["oled"].display()

    class homePage():
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Home Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                homePageData = displayFunction.homePage.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), homePageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 10), f"UID : {homePageData['uid']}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 20), f"Device : {homePageData['device']}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 30), f"Summary : {displayFunction.homePage.sensorSummary()}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 40), f"Firmware : {homePageData['firmware']}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, homePageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.initialize.content(globalVariable)
                time.sleep(1)  
        
        def getSystemInfo():
            result = {"uid": "N/A", "device": "N/A", "summary": "-", "timestamp": "N/A", "firmware": "N/A"}
            timestamp = times.getDatetime()
            connexHomePage = dbFunction.getDeviceSetting() 
            if connexHomePage:  
                result['uid'] = connexHomePage.get('uid', 'N/A')
                result['device'] = connexHomePage.get('name', 'N/A')
                result['firmware'] = connexHomePage.get('version', 'N/A')
                result['timestamp'] = timestamp + "+07.00"
            else:
                result['uid'] = "N/A"
                result['device'] = "N/A"
                result['firmware'] = "N/A"
                result['timestamp'] = "N/A"
            return result
        
        def sensorSummary():
            summaryMessage = 'N/A'
            group = SensorGroupDB.selectGroupOrderedByNumber()
            count = 0
            for num in range(len(group)):
                sensorData = SensorListDB.selectByGroupFull(group[num]["id"])
                checkServices = ServiceProjectFunction.checkActiveService(f'sensor{group[num]["id"]}.service')
                if checkServices == 'inactive':
                    count += 1
                    print(f"Service {group[num]['name']} Error : Inactive Service")
                    summaryMessage = 'Error'
                else:
                    for data in sensorData:
                        if data['conditions'] == "Alarm Error":
                            count += 1
                            print(f"Service {data['name_group']} Error : List Sensor Error")
                            summaryMessage = 'Error'
                            break
                        else:
                            summaryMessage = 'Normal'
                return summaryMessage

    class systemPage():
        def getSystemInfo():
            group_id = SensorGroupDB.selectIsNumber("7")[0]["id"]
            connexSystemInfo = SensorListDB.selectByGroupFull(group_id)
            sensor_data = {}
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']
                result = [
                    f"Voltage : {sensor_data.get('nearonVolt', 'N/A')} V",
                    f"Fan Speed : {sensor_data.get('nearonFan', 'N/A')} %",  
                    f"CPU Usage : {sensor_data.get('nearonCpuUsage', 'N/A')} %",
                    f"Temperature : {sensor_data.get('nearonCpuTemp', 'N/A')} C",
                    f"Memory : {sensor_data.get('nearonMemUsage', 'N/A')} %",
                    f"Storage : {sensor_data.get('nearonStorageUsage', 'N/A')} %",
                    f"Uptime : {sensor_data.get('nearonUptime', 'N/A')}",
                    f"unknown: N/A"
                ]
                timestamp = times.getDatetime()
            else:
                result =  [
                    f"Voltage : N/A",
                    f"Fan Speed : N/A",  
                    f"CPU Usage : N/A",
                    f"Temperature : N/A",
                    f"Memory : N/A",
                    f"Storage : N/A",
                    f"Uptime : N/A",
                    f"unknown : N/A"
                ]
                timestamp = times.getDatetime()
            return result, timestamp
        
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set(): 
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.systemPage.getSystemInfo()
                    displayFunction.systemPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1)  

        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.initialize.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.systemPage.updateData, args=(globalVariable, current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.systemPage.getSystemInfo()
            functionMenu = lambda: displayFunction.systemPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
            
        def content(globalVariable, current_time, result):
            timestamp = times.getDatetime()
            logService = "System Page"
            print(f"{timestamp} - {logService}")
            global scroll_position
            image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
            draw = ImageDraw.Draw(image)

            draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
            draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)

            draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)

            start_index = scroll_position // 10
            end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))

            for i in range(start_index, end_index):
                draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)

            globalVariable['oled']['oled'].image(image)
            globalVariable['oled']['oled'].display()
            SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
            return lambda: content(globalVariable, current_time, result)

    class networkPage():
        def getSystemInfo():
            timestamp = times.getDatetime()
            result = {"ip_ethernet": "N/A", "ip_wireless": "N/A", "ssid": "N/A", "timestamp": "N/A"}
            result['ip_ethernet'] = networkFunction.getInterface('eth0')
            result['ip_wireless'] = networkFunction.getInterface('wlan0')
            result['ssid'] = networkFunction.getSSID('wlan0')
            result['timestamp'] = timestamp + "+07.00"
            return result
        
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Network Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                networkPageData = displayFunction.networkPage.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), networkPageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 15), chr(63382),  font=globalVariable["font"]["ethernet"], fill=255)
                draw.text((33, 19), f"{networkPageData['ip_ethernet']}", font=globalVariable["font"]["default"], fill=255)
                draw.text((33, 35), f"{networkPageData['ip_wireless']}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 36), chr(61931),  font=globalVariable["font"]["wifi"], fill=255)
                draw.text((33, 45), f"{networkPageData['ssid']}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, networkPageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.initialize.content(globalVariable)
                time.sleep(1)

    class menuPage():
        def content(menu_items, start_index, OLED, OLED_WIDTH, OLED_HEIGHT, FONT, FONT_SELECT):
            image = Image.new('1', (OLED_WIDTH, OLED_HEIGHT))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, OLED_WIDTH, OLED_HEIGHT), outline=0, fill=0)
            max_visible_items = OLED_HEIGHT // 20
            start_index = max(0, selected_item - max_visible_items // 2)
            end_index = min(len(menu_items), start_index + max_visible_items)
            for i in range(start_index, end_index):
                menu_y = 23 * (i - start_index)
        
                if i == selected_item:
                    draw.rectangle([(2, menu_y), (OLED_WIDTH - 2, menu_y + 20)], outline=255, fill=0)
                    draw.text((8, menu_y+1), '>', font=FONT_SELECT, fill=255)
                    text_y = menu_y + (20 - FONT.getsize(menu_items[i])[1]) // 2
                    draw.text((23, text_y), menu_items[i], font=FONT, fill=255)
                else:
                    text_y = menu_y + (20 - FONT.getsize(menu_items[i])[1]) // 2
                    draw.text((20, text_y), menu_items[i], font=FONT, fill=255)
            OLED.image(image)
            OLED.display()
    
    class environmentSensorPage():
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set(): 
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.environmentSensorPage.getSystemInfo()
                    displayFunction.environmentSensorPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1) 
        
        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.subMenuSensorPage.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.environmentSensorPage.updateData, args=(globalVariable,current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.environmentSensorPage.getSystemInfo()
            functionMenu = lambda: displayFunction.environmentSensorPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
        
        def content(globalVariable, current_time, result):
            timestamp = times.getDatetime()            
            logService = "Environment Sensor Page"
            print(f"{timestamp} - {logService}")
            global scroll_position
            image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
            draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)
            draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)
            start_index = scroll_position // 10
            end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))
            for i in range(start_index, end_index):
                draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)

            globalVariable['oled']['oled'].image(image)
            globalVariable['oled']['oled'].display()
            SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
            return lambda: content(globalVariable, current_time, result)
        
        def getSystemInfo():
            group_id = SensorGroupDB.selectIsNumber("1")[0]["id"]
            connexSystemInfo = SensorListDB.selectGroupByState(group_id, "1", "1")
            result = []
            sensor_data = {}
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']
                for sensor_name, item in sensor_data.items():
                    if "temp" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}°C")
                    elif "humid" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}%")
                    elif "door" in sensor_name.lower():
                        status = "Open" if item == '1' else "Close" if item == '0' else "N/A"
                        result.append(f"{sensor_name}: {status}")
                    elif "smoke" in sensor_name.lower():
                        status = "Detect" if item == '1' else "No Detect" if item == '0' else "N/A"
                        result.append(f"{sensor_name}: {status}")
                    else:
                        result.append(f"{sensor_name}: {item}")

            timestamp = times.getDatetime()
            return result, timestamp
    
    class powerSensorPage():
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set(): 
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.powerSensorPage.getSystemInfo()
                    displayFunction.powerSensorPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1) 
        
        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.subMenuSensorPage.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.powerSensorPage.updateData, args=(globalVariable,current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.powerSensorPage.getSystemInfo()
            functionMenu = lambda: displayFunction.powerSensorPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
            
        def content(globalVariable, current_time, result):
            while True:
                timestamp = times.getDatetime()
                logService = "Power Sensor Page"
                print(f"{timestamp} - {logService}")
                global scroll_position
                image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
                draw = ImageDraw.Draw(image)
                draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
                draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)
                draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)
                start_index = scroll_position // 10
                end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))
                for i in range(start_index, end_index):
                    draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)

                globalVariable['oled']['oled'].image(image)
                globalVariable['oled']['oled'].display()
                SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
                return lambda: content(globalVariable, current_time, result)

        def getSystemInfo():
            # connexSystemInfo = SensorListDB.selectByGroupFull("2")
            group_id = SensorGroupDB.selectIsNumber("2")[0]["id"]
            connexSystemInfo = SensorListDB.selectGroupByState(group_id, "1", "1")
            result = []
            sensor_data = {}
            timestamp = times.getDatetime()
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']
                
                for sensor_name, item in sensor_data.items():
                    if "voltage" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}V")
                    elif "current" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}A")
                    else:
                        result.append(f"{sensor_name}: {item}")
                
            timestamp = times.getDatetime()
            return result, timestamp
    
    class environmentExtSensorPage():
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set():  
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.environmentExtSensorPage.getSystemInfo()
                    displayFunction.environmentExtSensorPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1)
        
        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.subMenuSensorPage.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.environmentExtSensorPage.updateData, args=(globalVariable, current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.environmentExtSensorPage.getSystemInfo()
            functionMenu = lambda: displayFunction.environmentExtSensorPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
        

        def content(globalVariable, current_time, result):
            timestamp = times.getDatetime()
            logService = "Environment Extension Sensor Page"
            print(f"{timestamp} - {logService}")
            global scroll_position
            image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
            draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)
            draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)
            start_index = scroll_position // 10
            end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))
            for i in range(start_index, end_index):
                draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)
            globalVariable['oled']['oled'].image(image)
            globalVariable['oled']['oled'].display()
            SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
            return lambda: content(globalVariable, current_time, result)
        
        def getSystemInfo():
            # connexSystemInfo = SensorListDB.selectGroupByState("3", "1", "1")
            group_id = SensorGroupDB.selectIsNumber("3")[0]["id"]
            connexSystemInfo = SensorListDB.selectGroupByState(group_id, "1", "1")
            result = []
            sensor_data = {}
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']
                
                for sensor_name, item in sensor_data.items():
                    if "temp" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}°C")
                    elif "humid" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}%")
                    elif "door" in sensor_name.lower():
                        status = "Open" if item == '1' else "Close" if item == '0' else "N/A"
                        result.append(f"{sensor_name}: {status}")
                    elif "smoke" in sensor_name.lower():
                        status = "Detect" if item == '1' else "No Detect" if item == '0' else "N/A"
                        result.append(f"{sensor_name}: {status}")
                    elif "water" in sensor_name.lower():
                        status = "Detect" if item == '1' else "No Detect" if item == '0' else "N/A"
                        result.append(f"{sensor_name}: {status}")
                    else:
                        result.append(f"{sensor_name}: {item}")
                
            timestamp = times.getDatetime()
            return result, timestamp

    class powerExtSensorPage():
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set():  
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.powerExtSensorPage.getSystemInfo()
                    displayFunction.powerExtSensorPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1)

        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.subMenuSensorPage.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.powerExtSensorPage.updateData, args=(globalVariable, current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.powerExtSensorPage.getSystemInfo()
            functionMenu = lambda: displayFunction.powerExtSensorPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
        
        def content(globalVariable, current_time, result):
            timestamp = times.getDatetime()
            logService = "Power Extension Sensor Page"
            print(f"{timestamp} - {logService}")
            global scroll_position
            image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
            draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)
            draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)
            start_index = scroll_position // 10
            end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))
            for i in range(start_index, end_index):
                draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)
            globalVariable['oled']['oled'].image(image)
            globalVariable['oled']['oled'].display()
            SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
            return lambda: content(globalVariable, current_time, result)

        def getSystemInfo():
            # connexSystemInfo = SensorListDB.selectGroupByState("4", "1", "1")
            group_id = SensorGroupDB.selectIsNumber("4")[0]["id"]
            connexSystemInfo = SensorListDB.selectGroupByState(group_id, "1", "1")
            sensor_data = {}
            result = []
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']

                for sensor_name, item in sensor_data.items():
                    if "voltage" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}V")
                    elif "current" in sensor_name.lower():
                        result.append(f"{sensor_name}: {item}A")
                    else:
                        result.append(f"{sensor_name}: {item}")
                
            timestamp = times.getDatetime()
            return result, timestamp

    class networkSensorPage():
        def updateData(globalVariable, page_name):
            page_state = page_data[page_name]
            while not stop_event.is_set(): 
                if current_page == page_name:
                    with page_state["lock"]:
                        page_state["data"], page_state["timestamp"] = displayFunction.networkSensorPage.getSystemInfo()
                    displayFunction.networkSensorPage.content(globalVariable, page_state["timestamp"], page_state["data"])
                    time.sleep(5)
                else:
                    stop_event.wait(1) 
        
        def controll(globalVariable, page_name):
            global current_page_thread, current_page
            backFunction = lambda: displayFunction.subMenuSensorPage.content(globalVariable)
            current_page = page_name
            displayFunction.threadFunction.stop_current_thread()
            current_page_thread = threading.Thread(target=displayFunction.networkSensorPage.updateData, args=(globalVariable, current_page))
            current_page_thread.daemon = True
            current_page_thread.start()
            result, timestamp = displayFunction.networkSensorPage.getSystemInfo()
            functionMenu = lambda: displayFunction.networkSensorPage.content(globalVariable, timestamp, result)
            displayFunction.controlPage.button_control_page(page_name, globalVariable, functionMenu, displayFunction.controlPage.scroll_up_page, 
                                                            displayFunction.controlPage.scroll_down_page, backFunction)
        
        def content(globalVariable, current_time, result):
            timestamp = times.getDatetime()
            logService = "Network Sensor Page"
            print(f"{timestamp} - {logService}")
            global scroll_position
            image = Image.new('1', (globalVariable['oled']['oled_width'], globalVariable['oled']['oled_height']))
            draw = ImageDraw.Draw(image)
            draw.rectangle([(0, 0), (globalVariable['oled']['oled_width']-1, globalVariable['oled']['oled_height']-1)], outline=255, width=1)
            draw.text((10, 0), current_time+"+07.00", font=globalVariable['font']['navbar'], fill=255)
            draw.line((5, 10, globalVariable['oled']['oled_width'], 10), fill=255)
            start_index = scroll_position // 10
            end_index = min(start_index + (globalVariable['oled']['oled_height'] // 10) - 1, len(result))
            for i in range(start_index, end_index):
                draw.text((5, 10 + (i - start_index) * 10), result[i], font=globalVariable['font']['default'], fill=255)

            globalVariable['oled']['oled'].image(image)
            globalVariable['oled']['oled'].display()
            SystemServiceDB.updateStatusByName(logService, current_time, globalVariable['service']['service_name'])  
            return lambda: content(globalVariable, current_time, result)
        
        def getSystemInfo():
            group_id = SensorGroupDB.selectIsNumber("6")[0]["id"]
            connexSystemInfo = SensorListDB.selectByGroupFull(group_id)
            sensor_data = {}
            if connexSystemInfo:
                sensor_data = {}
                for row in connexSystemInfo:
                    sensor_data[row['sensor_id']] = row['value']
                hddSpace = round(float(sensor_data.get('router1HddSpace', 'N/A')) * 0.000976563, 2)
                hddUsed = round(float(sensor_data.get('router1HddUsed', 'N/A')) * 0.000976563, 2)
                hddTotal = round(float(sensor_data.get('router1HddTotal', 'N/A')) * 0.000976563, 2)
                memorySpace = round(float(sensor_data.get('router1MemSpace', 'N/A')) * 0.000976563, 2)
                memoryUsed = round(float(sensor_data.get('router1MemUsed', 'N/A')) * 0.000976563, 2)
                memoryTotal = round(float(sensor_data.get('router1MemTotal', 'N/A')) * 0.000976563, 2)
                result = [
                    f"Temperature: {sensor_data.get('router1Temp', 'N/A')}°C",
                    f"Voltage: {sensor_data.get('router1Volt', 'N/A')} V", 
                    f"CPU Load 1: {sensor_data.get('router1CpuLoad1', 'N/A')} %",
                    f"CPU Load 2: {sensor_data.get('router1CpuLoad2', 'N/A')} %",
                    f"CPU Load 3: {sensor_data.get('router1CpuLoad3', 'N/A')} %",
                    f"CPU Load 4: {sensor_data.get('router1CpuLoad4', 'N/A')} %",
                    f"CPU Freq: {sensor_data.get('router1CpuFreq', 'N/A')} MHz",
                    f"HDD Space: {hddSpace} MiB", 
                    f"HDD Used: {hddUsed} MiB",
                    f"HDD Total: {hddTotal }MiB",
                    f"Memory Space: {memorySpace} MiB",
                    f"Memory Used: {memoryUsed} MiB",
                    f"Memory Total: {memoryTotal} MiB",
                    f"Model: {sensor_data.get('router1Model', 'N/A')}", 
                    f"S/N: {sensor_data.get('router1SN', 'N/A')}",
                    f"Uptime: {sensor_data.get('router1Uptime', 'N/A')}",
                    f"Iface1 MAC: {sensor_data.get('router1Iface1Mac', 'N/A')}",
                    f"Iface1 Upload: {sensor_data.get('router1Iface1UpSpd', 'N/A')}",
                    f"Iface1 Download: {sensor_data.get('router1Iface1DownSpd', 'N/A')}",
                    f"Iface1 Latency: {sensor_data.get('router1Iface1Latency', 'N/A')}",
                    f"unknown: N/A"
                ]
                timestamp = times.getDatetime()
            else:
                result = [
                    f"Temp: N/A",
                    f"Voltage: N/A", 
                    f"CPU Load1: N/A",
                    f"CPU Load2: N/A",
                    f"CPU Load3: N/A",
                    f"CPU Load4: N/A",
                    f"CPU Frequency: N/A",
                    f"HDD Space: N/A", 
                    f"HDD Used: N/A",
                    f"HDD Total: N/A",
                    f"Memory Space: N/A",
                    f"Memory Used: N/A",
                    f"Memory Total: N/A",
                    f"Model: N/A", 
                    f"S/N: N/A",
                    f"Uptime: N/A",
                    f"Iface1 MAC: N/A",
                    f"Iface1 Upload: N/A",
                    f"Iface1 Download: N/A",
                    f"Iface1 Latency: N/A",
                    f"unknown: N/A"
                ]
                timestamp = times.getDatetime()
            return result, timestamp

    class subMenuSensorPage():
        def content(globalVariable):
            timestamp = times.getDatetime()
            logService = "Sub Menu Sensor Page"
            print(f"{timestamp} - {logService}")
            SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['service']['service_name'])  
            image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
            sub_menu_sensor_functions = {
                "Environment": lambda: displayFunction.environmentSensorPage.controll(globalVariable, 'environmentPage'),
                "Power": lambda: displayFunction.powerSensorPage.controll(globalVariable, "powerPage"),
                "Environment Ext": lambda: displayFunction.environmentExtSensorPage.controll(globalVariable, 'environmentExtPage'),
                "Power Ext": lambda: displayFunction.powerExtSensorPage.controll(globalVariable, 'powerExtPage')
                # "Network": lambda: displayFunction.networkSensorPage.controll(globalVariable, 'networkExtPage')
            }
            
            sub_menu_sensor_items = displayFunction.subMenuSensorPage.getSystemInfo()
            num_pages = len(sub_menu_sensor_items)
            displayFunction.controlMenu.start_menu(num_pages, sub_menu_sensor_functions, sub_menu_sensor_items, globalVariable)
            globalVariable["oled"]["oled"].image(image)
            globalVariable["oled"]["oled"].display()
            return lambda: content(globalVariable)
        
        def getSystemInfo():
            sensor_group = SensorGroupDB.selectByState("1")

            result = []
            for i in range(len(sensor_group)):
                if int(sensor_group[i]["number"]) in (5, 6, 7):
                    continue
                if sensor_group[i]["name"] == "Environment Extension":
                    result.append("Environment Ext")
                elif sensor_group[i]["name"] == "Power Extension":
                    result.append("Power Ext")
                else:
                    result.append(sensor_group[i]["name"])
            
            return result


    class remoteAcValue():
        def getSystemInfo():
            result = {"remote1": "N/A", "remote2": "N/A", "remote3": "N/A", "remote4": "N/A", "timestamp": "N/A"}
            timestamp = times.getDatetime()
            actuatorData = ActuatorDB.select()
            actuator_data = {'data_actuator': {}}
            if actuatorData:
                for row in actuatorData:
                    actuator_data['data_actuator'][row['actuator_id']] = (row['value'], row['last_update'])
                def convert_status(value):
                    if value == '1':
                        return "On"
                    elif value == '0':
                        return "Off"
                    else:
                        return "N/A"
                result["remote1"] = (convert_status(actuator_data['data_actuator'].get('remote1', ('N/A', 'N/A'))[0]), 
                                    actuator_data['data_actuator'].get('remote1', ('N/A', 'N/A'))[1])
                result["remote2"] = (convert_status(actuator_data['data_actuator'].get('remote2', ('N/A', 'N/A'))[0]), 
                                    actuator_data['data_actuator'].get('remote2', ('N/A', 'N/A'))[1])
                result["remote3"] = (convert_status(actuator_data['data_actuator'].get('remote3', ('N/A', 'N/A'))[0]), 
                                    actuator_data['data_actuator'].get('remote3', ('N/A', 'N/A'))[1])
                result["remote4"] = (convert_status(actuator_data['data_actuator'].get('remote4', ('N/A', 'N/A'))[0]), 
                                    actuator_data['data_actuator'].get('remote4', ('N/A', 'N/A'))[1])
                result['timestamp'] = timestamp + "+07.00"
            return result

    class remoteAC1():
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Remote AC 1 Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                remotePageData = displayFunction.remoteAcValue.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), remotePageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 10), f"Action Value: {remotePageData['remote1'][0]}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 20), f"Update: {remotePageData['remote1'][1]}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, remotePageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.subMenuActuatorPage.content(globalVariable)
                time.sleep(1)

    class remoteAC2():
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Remote AC 2 Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                remotePageData = displayFunction.remoteAcValue.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), remotePageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 10), f"Action Value: {remotePageData['remote2'][0]}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 20), f"Update: {remotePageData['remote2'][1]}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, remotePageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2) 
                    displayFunction.subMenuActuatorPage.content(globalVariable)
                time.sleep(1)
    
    class remoteAC3():
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Remote AC 3 Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                remotePageData = displayFunction.remoteAcValue.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), remotePageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 10), f"Action Value: {remotePageData['remote3'][0]}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 20), f"Update: {remotePageData['remote3'][1]}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, remotePageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.subMenuActuatorPage.content(globalVariable)
                time.sleep(1)
    
    class remoteAC4():
        def content(globalVariable):
            while True:
                timestamp = times.getDatetime()
                logService = "Remote AC 4 Page"
                print(f"{timestamp} - {logService}")
                image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
                draw = ImageDraw.Draw(image)
                remotePageData = displayFunction.remoteAcValue.getSystemInfo()
                draw.rectangle([(0, 0), (globalVariable["oled"]["oled_width"]-1, globalVariable["oled"]["oled_height"]-1)], outline=255, width=1)
                draw.text((10, 0), remotePageData['timestamp'], font=globalVariable["font"]["navbar"], fill=255)
                draw.line((5, 10, globalVariable["oled"]["oled_width"], 10), fill=255)
                draw.text((5, 10), f"Action Value: {remotePageData['remote4'][0]}", font=globalVariable["font"]["default"], fill=255)
                draw.text((5, 20), f"Update: {remotePageData['remote4'][1]}", font=globalVariable["font"]["default"], fill=255)
                globalVariable["oled"]["oled"].image(image)
                globalVariable["oled"]["oled"].display()
                SystemServiceDB.updateStatusByName(logService, remotePageData['timestamp'].replace('+07.00', ''), globalVariable['service']['service_name'])  
                if GPIO.input(globalVariable["button"]["back"]) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.subMenuActuatorPage.content(globalVariable)
                time.sleep(1)
        
    class subMenuActuatorPage():
        def content(globalVariable):
            timestamp = times.getDatetime()
            logService = "Sub Menu Actuator Page"
            print(f"{timestamp} - {logService}")
            SystemServiceDB.updateStatusByName(logService, timestamp, globalVariable['service']['service_name'])  
            
            image = Image.new('1', (globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"]))
            sub_menu_actuator_functions = {
                "Remote AC 1": lambda: displayFunction.remoteAC1.content(globalVariable),
                "Remote AC 2": lambda: displayFunction.remoteAC2.content(globalVariable),
                "Remote AC 3": lambda: displayFunction.remoteAC3.content(globalVariable),
                "Remote AC 4": lambda: displayFunction.remoteAC4.content(globalVariable)
            }
            sub_menu_actuator_items = ["Remote AC 1", "Remote AC 2", "Remote AC 3", "Remote AC 4"]
            num_pages = len(sub_menu_actuator_items)
            displayFunction.controlMenu.start_menu(num_pages, sub_menu_actuator_functions, sub_menu_actuator_items, globalVariable)
            globalVariable["oled"]["oled"].image(image)
            globalVariable["oled"]["oled"].display()
    
    class controlPage():
        def scroll_page(direction, page_name, globalVariable): 
            global scroll_position
            page_state = page_data[page_name]
            with page_state["lock"]:
                content_length = len(page_state["data"])
            max_scroll = max(0, (content_length - (globalVariable['oled']['oled_height'] // 10)) * 10)
            if direction == 'up':
                scroll_position = max(0, scroll_position - 10)
            elif direction == 'down':
                scroll_position = min(max_scroll, scroll_position + 10)
            displayFunction.systemPage.content(globalVariable, page_state["timestamp"], page_state["data"])

        def scroll_up_page(page_name, globalVariable):
            displayFunction.controlPage.scroll_page('up', page_name, globalVariable)

        def scroll_down_page(page_name, globalVariable):
            displayFunction.controlPage.scroll_page('down', page_name, globalVariable)

        def button_control_page(page_name, globalVariable, functionMenu, scroll_up_func, scroll_down_func, backFunction):
            while True:
                function = functionMenu
                if GPIO.input(globalVariable['button']['up']) == GPIO.LOW:
                    time.sleep(0.2)  
                    scroll_up_func(page_name, globalVariable)
                elif GPIO.input(globalVariable['button']['down']) == GPIO.LOW:
                    time.sleep(0.2)  
                    scroll_down_func(page_name, globalVariable)
                elif GPIO.input(globalVariable['button']['back']) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.threadFunction.stop_current_thread()
                    backFunction()
                elif GPIO.input(globalVariable['button']['select']) == GPIO.LOW:
                    time.sleep(0.2)  
                    functionMenu()  
                    while GPIO.input(globalVariable['button']['select']) == GPIO.LOW:
                        time.sleep(0.1)  

    class controlMenu():
        def scroll_down(menu_items, start_index, globalVariable):
            global selected_item
            selected_item = (selected_item + 1) % len(menu_items)
            displayFunction.menuPage.content(menu_items, start_index, globalVariable["oled"]["oled"],
                                                        globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"],
                                                        globalVariable["font"]["default"], globalVariable["font"]["select"])

        def scroll_up(menu_items, start_index, globalVariable):
            global selected_item
            selected_item = (selected_item - 1) % len(menu_items)
            displayFunction.menuPage.content(menu_items, start_index, globalVariable["oled"]["oled"],
                                                        globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"],
                                                        globalVariable["font"]["default"], globalVariable["font"]["select"])

        def button_control(num_pages, menu_functions, menu_items, start_index, BTN_UP_PIN,
                        BTN_DOWN_PIN, BTN_SELECT_PIN, BTN_BACK_PIN ,globalVariable):
            global selected_item
            selected_page = 0
            page_active = False
            while True:
                if not page_active:
                    displayFunction.menuPage.content(menu_items, start_index, globalVariable["oled"]["oled"],
                                                        globalVariable["oled"]["oled_width"], globalVariable["oled"]["oled_height"],
                                                        globalVariable["font"]["default"], globalVariable["font"]["select"])
                if GPIO.input(BTN_UP_PIN) == GPIO.LOW:
                    time.sleep(0.2) 
                    displayFunction.controlMenu.scroll_up(menu_items, start_index, globalVariable)
                    selected_page = (selected_page - 1) % num_pages
                elif GPIO.input(BTN_DOWN_PIN) == GPIO.LOW:
                    time.sleep(0.2)  
                    displayFunction.controlMenu.scroll_down(menu_items, start_index, globalVariable)
                    selected_page = (selected_page + 1) % num_pages
                elif GPIO.input(BTN_SELECT_PIN) == GPIO.LOW:
                    time.sleep(0.2)  
                    page_active = not page_active
                    if page_active:
                        selected_menu = menu_items[selected_item]
                        menu_functions[selected_menu]()  
                        while GPIO.input(BTN_SELECT_PIN) == GPIO.LOW:
                            time.sleep(0.1)
                elif GPIO.input(BTN_BACK_PIN) == GPIO.LOW:
                    time.sleep(0.2) 
            
                    if page_active:
                        page_active = False
                        selected_page = 0
                    else:
                        displayFunction.initialize.content(globalVariable)
                    time.sleep(0.5)
        
        def start_menu(num_pages, menu_functions, menu_items, globalVariable):
                global selected_item
                start_index = 0
                selected_item = 0
                displayFunction.controlMenu.button_control(num_pages, menu_functions, menu_items, start_index,
                                                        globalVariable['button']['up'], globalVariable['button']['down'],
                                                        globalVariable['button']['select'], globalVariable['button']['back'],
                                                        globalVariable)
