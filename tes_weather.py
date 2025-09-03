from pymodbus.client.sync import ModbusSerialClient as ModbusClient
import time

port = "/dev/ttyUSB0"
baudrate = 4800
slaveId = 2

weatherObject = ModbusClient(method="rtu", port=port, baudrate=baudrate, timeout=2, retries=3)
weatherObject.connect()

windSpeed = 0x1F4
windStrength = 0x1F5
windDirection1 = 0x1F6
windDirection2 = 0x1F7
humidity = 0x1F8
temperature = 0x1F9
pm25 = 0x1FB
pm10 = 0x1FC
atmosphericPressure = 0x1FD
illuminanceLow = 0x1FE
illuminanceHigh = 0x1FF
illuminance = 0x200
rainfall = 0x201

def read_register_safe(address, multiplier=1, unit=slaveId, description=""):
    """Fungsi aman untuk membaca register dengan error handling"""
    try:
        response = weatherObject.read_holding_registers(address=address, count=1, unit=unit)
        if hasattr(response, 'registers') and response.registers:
            value = response.registers[0] * multiplier
            return value, True
        else:
            print(f"Error membaca {description}: Response tidak valid")
            return 0, False
    except Exception as e:
        print(f"Error membaca {description}: {e}")
        return 0, False

def main():
    # Wind Speed
    windSpeedData, success = read_register_safe(windSpeed, 0.01, description="Wind Speed")
    if success:
        print(f"Wind Speed : {round(windSpeedData, 2)} m/s")
    else:
        print("Wind Speed : Error")

    # Wind Strength
    windStrengthData, success = read_register_safe(windStrength, 1, description="Wind Strength")
    if success:
        print(f"Wind Strength : {windStrengthData}")
    else:
        print("Wind Strength : Error")

    # Wind Direction (0-7)
    windDirection1Data, success = read_register_safe(windDirection1, 1, description="Wind Direction 1")
    if success:
        print(f"Wind Direction (0-7) : {windDirection1Data}")
    else:
        print("Wind Direction (0-7) : Error")

    # Wind Direction (0-360)
    windDirection2Data, success = read_register_safe(windDirection2, 1, description="Wind Direction 2")
    if success:
        print(f"Wind Direction (0-360) : {windDirection2Data}")
    else:
        print("Wind Direction (0-360) : Error")

    # Humidity
    humidityData, success = read_register_safe(humidity, 0.1, description="Humidity")
    if success:
        print(f"Humidity : {round(humidityData, 2)} %")
    else:
        print("Humidity : Error")

    # Temperature
    temperatureData, success = read_register_safe(temperature, 0.1, description="Temperature")
    if success:
        print(f"Temperature : {round(temperatureData, 2)} C")
    else:
        print("Temperature : Error")

    # PM2.5
    pm25Data, success = read_register_safe(pm25, 1, description="PM2.5")
    if success:
        print(f"PM2.5 : {pm25Data} ug/m3")
    else:
        print("PM2.5 : Error")

    # PM1.0
    pm10Data, success = read_register_safe(pm10, 1, description="PM1.0")
    if success:
        print(f"PM1.0 : {pm10Data} ug/m3")
    else:
        print("PM1.0 : Error")

    # Atmospheric Pressure
    atmosphericPressureData, success = read_register_safe(atmosphericPressure, 0.1, description="Atmospheric Pressure")
    if success:
        print(f"Atmospheric Pressure : {round(atmosphericPressureData, 2)} kPa")
    else:
        print("Atmospheric Pressure : Error")

    # Illuminance
    illuminanceData, success = read_register_safe(illuminance, 100, description="Illuminance")
    if success:
        print(f"Illuminance : {illuminanceData} Lux")
    else:
        print("Illuminance : Error")

    # Rainfall
    rainfallData, success = read_register_safe(rainfall, 0.1, description="Rainfall")
    if success:
        print(f"Rainfall : {round(rainfallData, 2)} mm")
    else:
        print("Rainfall : Error")
    
    print("-------------------------------------------------------")

while True:
    try:
        main()
    except Exception as e:
        print(f"Error utama: {e}")
        print("Mencoba koneksi ulang...")
        try:
            weatherObject.close()
            weatherObject.connect()
        except:
            pass
    time.sleep(5)