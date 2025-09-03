#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weather Sensor - Main function untuk Weather Station Sensor
Menggunakan class Weather dari sensorLibrary.py
"""

import sys
import time
import os

# Tambahkan path ke sys.path
sys.path.append('/home/connex/project/sensor')
from sensorLibrary import Weather

def main():
    """Main function untuk menjalankan weather station sensor"""
    
    # Konfigurasi default untuk testing
    groupId = 1  # Sesuaikan dengan group ID yang sesuai
    dataSensor = {
        "numSensor": 8,  # Jumlah sensor yang akan dibaca
        "sensorId": [
            "windSpeed",
            "windStrength", 
            "windDirection1",
            "windDirection2",
            "humidity",
            "temperature",
            "pm25",
            "rainfall"
        ],
        "sensorDatatype": [0, 0, 0, 0, 0, 0, 0, 0]  # 0 untuk numeric, 1 untuk string
    }
    
    print("=== Weather Station Sensor ===")
    print(f"Group ID: {groupId}")
    print(f"Jumlah Sensor: {dataSensor['numSensor']}")
    print(f"Port: /dev/ttyUSB0")
    print(f"Baudrate: 4800")
    print(f"Slave ID: 2")
    print("=" * 30)
    
    try:
        # Inisialisasi weather station
        weather_station = Weather(groupId, dataSensor)
        
        # Loop utama untuk membaca sensor
        while True:
            try:
                print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Membaca sensor...")
                
                # Baca semua sensor
                result = weather_station.main()
                
                # Tampilkan hasil
                print(f"Status: {result['message']}")
                print("Data Sensor:")
                
                for i, sensor_id in enumerate(dataSensor['sensorId']):
                    value = result['value'][i]
                    state = result['state'][i]
                    status = "✓" if state else "✗"
                    
                    # Format output sesuai tipe sensor
                    if "windSpeed" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} m/s")
                    elif "windStrength" in sensor_id:
                        print(f"  {status} {sensor_id}: {value}")
                    elif "windDirection" in sensor_id:
                        if "1" in sensor_id:
                            print(f"  {status} {sensor_id}: {value} (0-7)")
                        else:
                            print(f"  {status} {sensor_id}: {value}°")
                    elif "humidity" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} %")
                    elif "temperature" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} °C")
                    elif "pm" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} μg/m³")
                    elif "atmosphericPressure" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} kPa")
                    elif "illuminance" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} Lux")
                    elif "rainfall" in sensor_id:
                        print(f"  {status} {sensor_id}: {value} mm")
                    else:
                        print(f"  {status} {sensor_id}: {value}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\nProgram dihentikan oleh user")
                break
            except Exception as e:
                print(f"\nError utama: {e}")
                print("Mencoba koneksi ulang...")
                try:
                    # Coba reconnect
                    weather_station.connect()
                except:
                    pass
                time.sleep(5)
                continue
            
            # Tunggu 5 detik sebelum membaca lagi
            time.sleep(5)
            
    except Exception as e:
        print(f"Error inisialisasi weather station: {e}")
        return 1
    
    finally:
        print("Program selesai")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
