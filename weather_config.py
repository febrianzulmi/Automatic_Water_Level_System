#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weather Config - Konfigurasi untuk Weather Station Sensor
"""

# Konfigurasi Hardware
WEATHER_CONFIG = {
    "port": "/dev/ttyUSB0",      # Port serial untuk weather station
    "baudrate": 4800,            # Baudrate komunikasi serial
    "slaveId": 2,                # Modbus Slave ID
    "timeout": 2,                # Timeout dalam detik
    "retries": 3,                # Jumlah retry jika gagal
}

# Konfigurasi Sensor
SENSOR_CONFIG = {
    "windSpeed": {
        "address": 0x1F4,
        "multiplier": 0.01,
        "unit": "m/s",
        "description": "Wind Speed"
    },
    "windStrength": {
        "address": 0x1F5,
        "multiplier": 1,
        "unit": "",
        "description": "Wind Strength"
    },
    "windDirection1": {
        "address": 0x1F6,
        "multiplier": 1,
        "unit": "(0-7)",
        "description": "Wind Direction (0-7)"
    },
    "windDirection2": {
        "address": 0x1F7,
        "multiplier": 1,
        "unit": "°",
        "description": "Wind Direction (0-360)"
    },
    "humidity": {
        "address": 0x1F8,
        "multiplier": 0.1,
        "unit": "%",
        "description": "Humidity"
    },
    "temperature": {
        "address": 0x1F9,
        "multiplier": 0.1,
        "unit": "°C",
        "description": "Temperature"
    },
    "pm25": {
        "address": 0x1FB,
        "multiplier": 1,
        "unit": "μg/m³",
        "description": "PM2.5"
    },
    "pm10": {
        "address": 0x1FC,
        "multiplier": 1,
        "unit": "μg/m³",
        "description": "PM1.0"
    },
    "atmosphericPressure": {
        "address": 0x1FD,
        "multiplier": 0.1,
        "unit": "kPa",
        "description": "Atmospheric Pressure"
    },
    "illuminanceLow": {
        "address": 0x1FE,
        "multiplier": 1,
        "unit": "Lux",
        "description": "Illuminance Low"
    },
    "illuminanceHigh": {
        "address": 0x1FF,
        "multiplier": 1,
        "unit": "Lux",
        "description": "Illuminance High"
    },
    "illuminance": {
        "address": 0x200,
        "multiplier": 100,
        "unit": "Lux",
        "description": "Illuminance"
    },
    "rainfall": {
        "address": 0x201,
        "multiplier": 0.1,
        "unit": "mm",
        "description": "Rainfall"
    }
}

# Konfigurasi Default untuk Testing
DEFAULT_SENSOR_LIST = [
    "windSpeed",
    "windStrength", 
    "windDirection1",
    "windDirection2",
    "humidity",
    "temperature",
    "pm25",
    "rainfall"
]

# Konfigurasi Database
DB_CONFIG = {
    "groupId": 1,                # Group ID untuk database
    "updateInterval": 5,         # Interval update dalam detik
}

# Konfigurasi Logging
LOG_CONFIG = {
    "level": "INFO",             # Log level (DEBUG, INFO, WARNING, ERROR)
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "weather_sensor.log"
}

def get_sensor_info(sensor_id):
    """Mendapatkan informasi sensor berdasarkan ID"""
    return SENSOR_CONFIG.get(sensor_id, None)

def get_all_sensors():
    """Mendapatkan daftar semua sensor yang tersedia"""
    return list(SENSOR_CONFIG.keys())

def validate_sensor_list(sensor_list):
    """Validasi daftar sensor"""
    valid_sensors = []
    invalid_sensors = []
    
    for sensor in sensor_list:
        if sensor in SENSOR_CONFIG:
            valid_sensors.append(sensor)
        else:
            invalid_sensors.append(sensor)
    
    return valid_sensors, invalid_sensors

if __name__ == "__main__":
    print("=== Weather Station Configuration ===")
    print(f"Port: {WEATHER_CONFIG['port']}")
    print(f"Baudrate: {WEATHER_CONFIG['baudrate']}")
    print(f"Slave ID: {WEATHER_CONFIG['slaveId']}")
    print(f"Timeout: {WEATHER_CONFIG['timeout']}s")
    print(f"Retries: {WEATHER_CONFIG['retries']}")
    print("\nAvailable Sensors:")
    
    for sensor_id, config in SENSOR_CONFIG.items():
        print(f"  {sensor_id}: {config['description']} ({config['unit']})")
    
    print(f"\nDefault Sensor List: {', '.join(DEFAULT_SENSOR_LIST)}")
    print(f"Database Group ID: {DB_CONFIG['groupId']}")
    print(f"Update Interval: {DB_CONFIG['updateInterval']}s")
