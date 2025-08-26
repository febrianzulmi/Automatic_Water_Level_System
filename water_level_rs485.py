#!/usr/bin/env python3
"""
Water Level Sensor RS485 Modbus Reader with Water Pump Control
Configuration:
- Device ID: 1
- Function: 03 (Read Holding Registers)
- Measuring Value Address: 4
- Baud rate: 9600
- Data Bits: 8
- Parity: None
- Stop Bit: 1
- Water Pump Control: GPIO 0
- Pump ON: Water level <= 0 cm
- Pump OFF: Water level >= 10 cm
"""

import minimalmodbus
import serial
import time
import sys
import RPi.GPIO as GPIO

class WaterLevelSensor:
    def __init__(self, port='/dev/ttyUSB0', device_id=1, baudrate=9600, pump_pin=0):
        """
        Initialize the water level sensor with pump control
        
        Args:
            port (str): Serial port (e.g., '/dev/ttyUSB0', '/dev/ttyS0', 'COM1')
            device_id (int): Modbus device ID
            baudrate (int): Baud rate (default: 9600)
            pump_pin (int): GPIO pin for water pump control (default: 0)
        """
        self.port = port
        self.device_id = device_id
        self.baudrate = baudrate
        self.pump_pin = pump_pin
        
        # Initialize GPIO for pump control
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pump_pin, GPIO.OUT)
        GPIO.output(pump_pin, GPIO.LOW)  # Start with pump OFF
        
        # Initialize the Modbus instrument
        self.instrument = minimalmodbus.Instrument(port, device_id)
        
        # Configure Modbus settings
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.serial.baudrate = baudrate
        self.instrument.serial.bytesize = 8
        self.instrument.serial.parity = serial.PARITY_NONE
        self.instrument.serial.stopbits = 1
        self.instrument.serial.timeout = 1.0
        self.instrument.close_port_after_each_call = True
        self.instrument.clear_buffers_before_each_transaction = True
        
        # Pump control thresholds (in cm)
        self.pump_on_threshold = 0    # Pump ON when level <= 0 cm
        self.pump_off_threshold = 10  # Pump OFF when level >= 10 cm
        self.pump_status = False      # Current pump status
        
    def control_pump(self, water_level_cm):
        """
        Control water pump based on water level
        
        Args:
            water_level_cm (float): Water level in centimeters
        """
        new_pump_status = self.pump_status
        
        # Convert water level from mm to cm if needed
        if water_level_cm > 100:  # If value is in mm, convert to cm
            water_level_cm = water_level_cm / 10
        
        # Control logic
        if water_level_cm <= self.pump_on_threshold and not self.pump_status:
            # Turn pump ON
            GPIO.output(self.pump_pin, GPIO.HIGH)
            self.pump_status = True
            new_pump_status = True
            print(f"🟢 POMPA AKTIF - Level air: {water_level_cm:.1f} cm")
            
        elif water_level_cm >= self.pump_off_threshold and self.pump_status:
            # Turn pump OFF
            GPIO.output(self.pump_pin, GPIO.LOW)
            self.pump_status = False
            new_pump_status = False
            print(f"🔴 POMPA MATI - Level air: {water_level_cm:.1f} cm")
        
        return new_pump_status
    
    def read_water_level(self):
        """
        Read water level from register address 4 using function code 03
        
        Returns:
            dict: Dictionary containing water level value and status
        """
        try:
            # Read register 4 (measuring value address) with function code 03
            # Function code 03 is automatically used by read_registers method
            result = self.instrument.read_registers(4, 1, 3)
            water_level = result[0]
            
            return {
                "success": True,
                "water_level": water_level,
                "unit": "mm",  # Assuming millimeters, adjust as needed
                "message": f"Successfully read water level: {water_level}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "water_level": None,
                "unit": None,
                "message": f"Error reading water level: {str(e)}"
            }
    
    def read_water_level_continuous(self, interval=5):
        """
        Continuously read water level data and control pump
        
        Args:
            interval (int): Reading interval in seconds
        """
        print(f"🚰 SISTEM KONTROL LEVEL AIR & POMPA")
        print("=" * 60)
        print(f"📡 Port: {self.port}")
        print(f"🆔 Device ID: {self.device_id}")
        print(f"⚡ Baud rate: {self.baudrate}")
        print(f"📍 Register address: 4")
        print(f"🔧 Function code: 03")
        print(f"⏱️  Reading interval: {interval} seconds")
        print(f"🔌 Pump GPIO Pin: {self.pump_pin}")
        print(f"🟢 Pompa AKTIF: Level ≤ {self.pump_on_threshold} cm")
        print(f"🔴 Pompa MATI: Level ≥ {self.pump_off_threshold} cm")
        print("=" * 60)
        print("Tekan Ctrl+C untuk menghentikan monitoring")
        print("-" * 60)
        
        try:
            while True:
                result = self.read_water_level()
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                
                if result["success"]:
                    water_level = result['water_level']
                    water_level_cm = water_level / 10  # Convert mm to cm
                    
                    # Control pump
                    pump_status = self.control_pump(water_level_cm)
                    
                    # Display status
                    pump_icon = "🟢" if pump_status else "🔴"
                    pump_text = "AKTIF" if pump_status else "MATI"
                    
                    print(f"[{timestamp}] Level Air: {water_level_cm:.1f} cm ({water_level} mm) | Pompa: {pump_icon} {pump_text}")
                else:
                    print(f"[{timestamp}] ❌ ERROR: {result['message']}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring dihentikan oleh user.")
            # Turn off pump when stopping
            GPIO.output(self.pump_pin, GPIO.LOW)
            print("🔴 Pompa dimatikan untuk keamanan.")
        finally:
            GPIO.cleanup()
    
    def test_connection(self):
        """
        Test the Modbus connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to read a register to test connection
            result = self.instrument.read_registers(4, 1, 3)
            print(f"✅ Test koneksi berhasil! Nilai yang dibaca: {result[0]} mm")
            return True
        except Exception as e:
            print(f"❌ Test koneksi gagal: {str(e)}")
            return False
    
    def test_pump(self):
        """
        Test pump functionality
        """
        print("🧪 Testing pompa air...")
        print("🔴 Mematikan pompa...")
        GPIO.output(self.pump_pin, GPIO.LOW)
        time.sleep(2)
        
        print("🟢 Mengaktifkan pompa...")
        GPIO.output(self.pump_pin, GPIO.HIGH)
        time.sleep(3)
        
        print("🔴 Mematikan pompa...")
        GPIO.output(self.pump_pin, GPIO.LOW)
        print("✅ Test pompa selesai!")

def main():
    """Main function to run the water level sensor reader with pump control"""
    
    # Configuration
    PORT = '/dev/ttyUSB0'  # Change this to your actual port
    DEVICE_ID = 1
    BAUD_RATE = 9600
    PUMP_PIN = 0  # GPIO pin for water pump
    
    # Create sensor instance
    sensor = WaterLevelSensor(port=PORT, device_id=DEVICE_ID, baudrate=BAUD_RATE, pump_pin=PUMP_PIN)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Test connection
            sensor.test_connection()
        elif sys.argv[1] == 'pump':
            # Test pump
            sensor.test_pump()
        elif sys.argv[1] == 'single':
            # Single reading
            result = sensor.read_water_level()
            if result["success"]:
                water_level_cm = result['water_level'] / 10
                print(f"Level Air: {water_level_cm:.1f} cm ({result['water_level']} mm)")
                sensor.control_pump(water_level_cm)
            else:
                print(f"Error: {result['message']}")
        else:
            print("🚰 Water Level Sensor dengan Kontrol Pompa")
            print("\nPenggunaan:")
            print("  python water_level_rs485.py          # Monitoring kontinyu dengan kontrol pompa")
            print("  python water_level_rs485.py test     # Test koneksi sensor")
            print("  python water_level_rs485.py pump     # Test pompa air")
            print("  python water_level_rs485.py single   # Baca sekali dengan kontrol pompa")
    else:
        # Continuous monitoring with pump control (default)
        sensor.read_water_level_continuous()

if __name__ == "__main__":
    main()
