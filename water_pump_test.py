#!/usr/bin/env python3
"""
Water Level Sensor RS485 dengan Kontrol Pompa Air - Versi Test Sederhana
Fitur:
- Monitoring level air secara real-time
- Safety OFF otomatis saat level tinggi (10 cm)
- Kontrol ON manual via dashboard
- Tanpa logging file
- Tanpa fitur keamanan
- Hanya untuk tes
"""

import minimalmodbus
import serial
import time
import sys
import RPi.GPIO as GPIO
from datetime import datetime

# Konfigurasi
SERIAL_PORT = '/dev/ttyUSB0'
DEVICE_ID = 1
BAUD_RATE = 9600
READING_INTERVAL = 1
PUMP_GPIO_PIN = 0
PUMP_OFF_THRESHOLD = 10  # Pompa MATI saat level ≥ 10 cm (Safety OFF)
WATER_LEVEL_UNIT = 'cm'

class WaterPumpTest:
    def __init__(self):
        """Initialize sensor dan pompa"""
        self.setup_gpio()
        self.setup_sensor()
        self.pump_status = False
        self.pump_start_time = None
        
    def setup_gpio(self):
        """Setup GPIO untuk kontrol pompa"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(PUMP_GPIO_PIN, GPIO.OUT)
            GPIO.output(PUMP_GPIO_PIN, GPIO.LOW)  # Start dengan pompa MATI
            print(f"✅ GPIO Pin {PUMP_GPIO_PIN} berhasil disetup")
        except Exception as e:
            print(f"❌ Error setup GPIO: {e}")
            raise
            
    def setup_sensor(self):
        """Setup sensor water level RS485"""
        try:
            self.instrument = minimalmodbus.Instrument(SERIAL_PORT, DEVICE_ID)
            self.instrument.mode = minimalmodbus.MODE_RTU
            self.instrument.serial.baudrate = BAUD_RATE
            self.instrument.serial.bytesize = 8
            self.instrument.serial.parity = serial.PARITY_NONE
            self.instrument.serial.stopbits = 1
            self.instrument.serial.timeout = 1.0
            self.instrument.close_port_after_each_call = True
            self.instrument.clear_buffers_before_each_transaction = True
            print(f"✅ Sensor RS485 berhasil disetup pada port {SERIAL_PORT}")
        except Exception as e:
            print(f"❌ Error setup sensor: {e}")
            raise
            
    def read_water_level(self):
        """Baca level air dari sensor"""
        try:
            result = self.instrument.read_registers(4, 1, 3)
            water_level = result[0]
            
            return {
                "success": True,
                "water_level": water_level,
                "unit": WATER_LEVEL_UNIT
            }
        except Exception as e:
            return {
                "success": False,
                "water_level": None,
                "unit": None,
                "error": str(e)
            }
            
    def control_pump(self, water_level_cm):
        """Kontrol pompa - Hanya OFF otomatis saat level tinggi"""
        # Hanya matikan pompa saat level tinggi (safety OFF)
        if water_level_cm >= PUMP_OFF_THRESHOLD and self.pump_status:
            self.turn_pump_off(f"Level air mencapai {water_level_cm:.1f} cm")
            
        return self.pump_status
        
    def turn_pump_on(self, water_level_cm):
        """Aktifkan pompa"""
        try:
            GPIO.output(PUMP_GPIO_PIN, GPIO.HIGH)
            self.pump_status = True
            self.pump_start_time = time.time()
            print(f"🟢 POMPA AKTIF - Level air: {water_level_cm:.1f} cm")
        except Exception as e:
            print(f"❌ Error mengaktifkan pompa: {e}")
            
    def turn_pump_off(self, reason=""):
        """Matikan pompa"""
        try:
            GPIO.output(PUMP_GPIO_PIN, GPIO.LOW)
            runtime = 0
            if self.pump_start_time:
                runtime = time.time() - self.pump_start_time
                
            self.pump_status = False
            self.pump_start_time = None
            
            message = f"🔴 POMPA MATI - {reason}"
            if runtime > 0:
                message += f" (Runtime: {runtime:.1f}s)"
                
            print(message)
        except Exception as e:
            print(f"❌ Error mematikan pompa: {e}")
        
    def run_test(self):
        """Jalankan test monitoring"""
        print("🚰 SISTEM KONTROL LEVEL AIR & POMPA - VERSI TEST")
        print("=" * 60)
        print(f"📡 Port: {SERIAL_PORT}")
        print(f"🆔 Device ID: {DEVICE_ID}")
        print(f"⚡ Baud rate: {BAUD_RATE}")
        print(f"🔌 Pump GPIO Pin: {PUMP_GPIO_PIN}")
        print(f"🔴 Pompa MATI: Level ≥ {PUMP_OFF_THRESHOLD} cm (Safety OFF)")
        print(f"🟢 Pompa ON: Manual control via dashboard")
        print(f"⏱️  Interval: {READING_INTERVAL} detik")
        print("=" * 60)
        print("Tekan Ctrl+C untuk menghentikan")
        print("-" * 60)
        
        try:
            while True:
                result = self.read_water_level()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                if result["success"]:
                    water_level = result['water_level']
                    water_level_cm = water_level / 10 if WATER_LEVEL_UNIT == 'mm' else water_level
                    
                    # Kontrol pompa
                    pump_status = self.control_pump(water_level_cm)
                    
                    # Tampilkan status
                    pump_icon = "🟢" if pump_status else "🔴"
                    pump_text = "AKTIF" if pump_status else "MATI"
                    
                    status_msg = f"[{timestamp}] Level: {water_level_cm:.1f} cm | Pompa: {pump_icon} {pump_text}"
                    
                    # Tambahkan info runtime jika pompa aktif
                    if pump_status and self.pump_start_time:
                        runtime = time.time() - self.pump_start_time
                        status_msg += f" (Runtime: {runtime:.1f}s)"
                        
                    print(status_msg)
                else:
                    print(f"[{timestamp}] ❌ ERROR: {result.get('error', 'Unknown error')}")
                    
                time.sleep(READING_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n🛑 Test dihentikan oleh user")
        finally:
            self.cleanup()
            
    def cleanup(self):
        """Bersihkan resources"""
        try:
            self.turn_pump_off("Test dihentikan")
            GPIO.cleanup()
            print("✅ Cleanup selesai")
        except Exception as e:
            print(f"❌ Error saat cleanup: {e}")
            
    def test_sensor(self):
        """Test sensor water level"""
        print("🧪 Testing sensor water level...")
        result = self.read_water_level()
        if result["success"]:
            water_level_cm = result['water_level'] / 10 if WATER_LEVEL_UNIT == 'mm' else result['water_level']
            print(f"✅ Sensor OK - Level: {water_level_cm:.1f} cm ({result['water_level']} {WATER_LEVEL_UNIT})")
        else:
            print(f"❌ Sensor Error: {result.get('error', 'Unknown error')}")
            
    def test_pump(self):
        """Test pompa air"""
        print("🧪 Testing pompa air...")
        print("🔴 Mematikan pompa...")
        self.turn_pump_off("Test")
        time.sleep(2)
        
        print("🟢 Mengaktifkan pompa...")
        self.turn_pump_on(0)
        time.sleep(3)
        
        print("🔴 Mematikan pompa...")
        self.turn_pump_off("Test selesai")
        print("✅ Test pompa selesai!")

def main():
    """Main function"""
    try:
        controller = WaterPumpTest()
        
        if len(sys.argv) > 1:
            if sys.argv[1] == 'test':
                controller.test_sensor()
            elif sys.argv[1] == 'pump':
                controller.test_pump()
            elif sys.argv[1] == 'help':
                print("🚰 Water Pump Test - Versi Sederhana")
                print("\nPenggunaan:")
                print("  python water_pump_test.py          # Monitoring kontinyu")
                print("  python water_pump_test.py test     # Test sensor")
                print("  python water_pump_test.py pump     # Test pompa")
                print("  python water_pump_test.py help     # Bantuan ini")
            else:
                print("❌ Command tidak dikenal. Gunakan 'help' untuk bantuan.")
        else:
            # Monitoring kontinyu (default)
            controller.run_test()
            
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
