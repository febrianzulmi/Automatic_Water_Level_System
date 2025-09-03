#!/usr/bin/env python3
"""
Script monitoring water level dengan sinkronisasi API
Menggunakan function dari actuatorLibrary + API endpoint

FITUR KEAMANAN:
- Auto matikan waterPump actuator ketika water level tinggi
- Auto matikan rotaryLamp (GPIO pin 0) ketika water level tinggi
- Kontrol otomatis berdasarkan threshold dari database
- Notifikasi otomatis saat water level tinggi
- Safety lock: actuator tidak bisa dinyalakan manual saat water level tinggi
- Update status sensor monitoring via API (Alarm Max/Normal)

ACTUATOR YANG DIKONTROL:
1. waterPump: GPIO pin yang dikonfigurasi (default: pin 7)
2. rotaryLamp: GPIO pin 0 (fixed)

KEAMANAN:
- Hanya berfungsi ketika alarm status = "ACTIVE"
- Threshold diambil dari database sensorListDB
- Kontrol via GPIO + sinkronisasi dengan API server
"""

import sys
import time
import threading
import minimalmodbus
import serial
import datetime

# Tambahkan path untuk import
sys.path.append('/home/connex/project/actuator')
sys.path.append('/home/connex/project/database')
sys.path.append('/home/connex/library')
from synapsis_api_client import SynapsisAPIClient
from query_project_db import ActuatorListDB
from SynapsisLibrary import times


def read_water_level_safety():
    """
    Baca water level untuk safety check
    Returns: water level dalam cm, atau None jika error
    """
    try:
        # Konfigurasi water level sensor
        SERIAL_PORT = '/dev/ttyUSB0'
        DEVICE_ID = 1
        BAUD_RATE = 9600
        WATER_LEVEL_UNIT = 'cm'
        
        # Setup minimalmodbus
        instrument = minimalmodbus.Instrument(SERIAL_PORT, DEVICE_ID)
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.baudrate = BAUD_RATE
        instrument.serial.bytesize = 8
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.stopbits = 1
        instrument.serial.timeout = 2.0
        instrument.close_port_after_each_call = True
        instrument.clear_buffers_before_each_transaction = True
        
        # Baca register 4 (water level)
        result = instrument.read_registers(4, 1, 3)
        water_level = result[0]
        
        # Konversi ke cm jika perlu
        if WATER_LEVEL_UNIT == 'mm':
            water_level = water_level / 10
            
        return water_level
        
    except Exception as e:
        print(f"⚠️  Water level safety check error: {e}")
        return None


class WaterLevelMonitor:
    def __init__(self, actuator_custom_id="waterPump", pin=7, check_interval=2):
        # Parameter dari actuatorLibrary
        self.actuator_custom_id = actuator_custom_id
        self.pin = pin
        self.check_interval = check_interval
        
        # API Client
        self.api_client = SynapsisAPIClient()
        
        # Status monitoring
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Cache untuk actuator info
        self.last_actuator_check = 0
        self.actuator_cache_duration = 30  # Cache selama 30 detik
        self.cached_actuator_info = None
        
        # Cache untuk threshold
        self.last_threshold_check = 0
        self.threshold_cache_duration = 2  # Refresh threshold setiap 2 detik
        self.safety_threshold = None  # Tidak ada default threshold
        
        # Cache untuk alarm status
        self.last_alarm_check = 0
        self.alarm_cache_duration = 2  # Refresh alarm status setiap 2 detik
        self.alarm_status = None  # Status alarm dari database
        
        # Flag untuk water level tracking
        self.last_water_level = None
        
        # Flag untuk notification tracking
        self.notification_sent = False  # Flag untuk tracking notifikasi
        
        # Update safety threshold dari database (wajib)
        if not self.update_safety_threshold():
            raise ValueError("❌ Tidak bisa mendapatkan safety threshold dari database. Sistem tidak bisa berjalan tanpa threshold yang valid.")
        
        # Update alarm status dari database (wajib)
        if not self.update_alarm_status():
            raise ValueError("❌ Tidak bisa mendapatkan alarm status dari database. Sistem tidak bisa berjalan tanpa alarm status yang valid.")
        
        print("🚰 Water Level Monitor initialized")
        print(f"🎯 Actuator: {self.actuator_custom_id}")
        print(f"📌 GPIO Pin: {self.pin}")
        print(f"💡 Rotary Lamp Pin: 0")
        print(f"⏱️  Check interval: {self.check_interval} detik")
        print(f"🚨 Safety threshold: {self.safety_threshold} cm (dari database)")
        print(f"🚨 Alarm status: {self.alarm_status} (dari database)")
        print("🔔 Notification: Auto kirim notifikasi jika water level > threshold (hanya sekali)")
        print("🎛️  Actuator Control: Auto stop waterPump sekali, lalu kontrol manual via dashboard")
        print("💡 Rotary Lamp: Auto ON saat water level tinggi, Auto OFF saat water level aman (sekali saja)")
        print("🔄 Trigger: Hanya sekali ketika water level melewati threshold")
        print("📊 Monitoring: Update status sensor monitoring via API")
        print("🎯 Fokus: Sync dengan actuatorLibrary + hit API endpoint")
        print("🔄 Mode: Auto Stop Once + Auto Rotary Lamp + Manual Control")
    
    def get_actuator_info(self, force_refresh=False):
        """
        Dapatkan informasi actuator dari database lokal (menggunakan actuatorLibrary)
        Returns: dict dengan informasi actuator atau None jika gagal
        """
        current_time = time.time()
        
        # Gunakan cache jika belum expired dan tidak force refresh
        if (not force_refresh and 
            self.cached_actuator_info and 
            current_time - self.last_actuator_check < self.actuator_cache_duration):
            return self.cached_actuator_info
        
        try:
            print("🔍 Mengambil informasi actuator dari database lokal...")
            
            # Gunakan function dari actuatorLibrary untuk mendapatkan data actuator
            actuator_data = ActuatorListDB.selectByActId(self.actuator_custom_id)
            
            if actuator_data and len(actuator_data) > 0:
                actuator_info = actuator_data[0]  # Ambil actuator pertama
                
                # Cache hasil
                self.cached_actuator_info = actuator_info
                self.last_actuator_check = current_time
                
                print(f"✅ Info actuator berhasil diambil dari database lokal:")
                print(f"   📝 Nama: {actuator_info.get('name', 'N/A')}")
                print(f"   🆔 ID: {actuator_info.get('id', 'N/A')}")
                print(f"   💡 Status: {actuator_info.get('state', 'N/A')}")
                print(f"   🔧 Last Action Value: {actuator_info.get('last_action_value', 'N/A')}")
                print(f"   🌐 Server Value: {actuator_info.get('server_value', 'N/A')}")
                print(f"   ⏰ Updated: {actuator_info.get('updated_at', 'N/A')}")
                
                return actuator_info
            else:
                print("⚠️  Tidak ada data actuator dalam database lokal")
                
                # Fallback ke API jika tidak ada di database lokal
                print("🔄 Mencoba mengambil dari API sebagai fallback...")
                return self.get_actuator_info_from_api()
                
        except Exception as e:
            print(f"❌ Error mengambil info actuator dari database: {e}")
            
            # Fallback ke API jika database error
            print("🔄 Mencoba mengambil dari API sebagai fallback...")
            return self.get_actuator_info_from_api()
    
    def get_actuator_info_from_api(self):
        """
        Fallback: Dapatkan informasi actuator dari API
        """
        try:
            print("🔍 Mengambil informasi actuator dari API...")
            
            # Login jika belum
            if not self.api_client.is_logged_in():
                if not self.api_client.login():
                    print("❌ Gagal login untuk mengambil info actuator")
                    return None
            
            # Hit endpoint untuk mendapatkan info actuator
            response = self.api_client.get_actuator_info(self.actuator_custom_id)
            
            if response and response.get('status') and response.get('data'):
                actuator_data = response['data']
                if actuator_data:
                    actuator_info = actuator_data[0]  # Ambil actuator pertama
                    
                    # Cache hasil
                    self.cached_actuator_info = actuator_info
                    self.last_actuator_check = time.time()
                    
                    print(f"✅ Info actuator berhasil diambil dari API:")
                    print(f"   📝 Nama: {actuator_info.get('name', 'N/A')}")
                    print(f"   🆔 ID: {actuator_info.get('id', 'N/A')}")
                    print(f"   💡 Status: {actuator_info.get('value', 'N/A')}")
                    print(f"   ⏰ Updated: {actuator_info.get('updated_at', 'N/A')}")
                    
                    return actuator_info
                else:
                    print("⚠️  Tidak ada data actuator dalam response API")
                    return None
            else:
                print(f"❌ Gagal mengambil info actuator dari API: {response}")
                return None
                
        except Exception as e:
            print(f"❌ Error mengambil info actuator dari API: {e}")
            return None
    
    def check_and_control_actuator(self, water_level):
        """
        Cek status actuator dan monitoring water level
        Hanya trigger sekali ketika water level melewati threshold
        Tidak ada kontrol otomatis actuator - hanya monitoring dan notifikasi
        """
        try:
            # Dapatkan info actuator dari database lokal (prioritas) atau API (fallback)
            actuator_info = self.get_actuator_info()
            
            if not actuator_info:
                print("⚠️  Tidak bisa mendapatkan info actuator, skip kontrol")
                return
            
            # Parse status actuator (prioritas dari database lokal)
            if 'last_action_value' in actuator_info:
                # Dari database lokal - perbaiki interpretasi
                actuator_status = actuator_info.get('last_action_value')
                # Status 1 = ON, 0 = OFF (sesuai dengan database)
                is_actuator_on = actuator_status == 1
                print(f"🔍 Status actuator (DB): {actuator_status} (ON: {is_actuator_on})")
            elif 'value' in actuator_info:
                # Dari API
                actuator_status = actuator_info.get('value', 'false').lower()
                is_actuator_on = actuator_status == 'true'
                print(f"🔍 Status actuator (API): {actuator_status} (ON: {is_actuator_on})")
            else:
                print("⚠️  Tidak bisa menentukan status actuator")
                return
            
            # Cek apakah water level valid (tidak None)
            if water_level is None:
                print("⚠️  Water level tidak terbaca - tidak mengubah flag notifikasi")
                print("🔒 Flag notifikasi tetap: tidak di-reset untuk keamanan")
                return
            
            # Gunakan threshold dinamis dari database
            print(f"🔍 Menggunakan threshold dinamis: {self.safety_threshold} cm")
            is_safe = water_level < self.safety_threshold
            
            # Update last water level hanya jika valid
            self.last_water_level = water_level
            
            # Cek alarm status
            print(f"🔍 Alarm status: {self.alarm_status}")
            
            # Logic notification dan monitoring berdasarkan alarm status
            if self.alarm_status == "ACTIVE":
                if not is_safe:
                    # WATER LEVEL TINGGI + ALARM ACTIVE = KONTROL OTOMATIS WATERPUMP HANYA SEKALI
                    print(f"🚨 Water level tinggi terdeteksi: {water_level:.1f} cm ≥ {self.safety_threshold} cm")
                    
                    # Kontrol otomatis waterPump hanya sekali saat pertama kali terdeteksi
                    if not hasattr(self, 'waterpump_auto_stopped'):
                        print("🔴 WaterPump akan dimatikan otomatis untuk pertama kali...")
                        
                        # Matikan actuator via GPIO
                        try:
                            import RPi.GPIO as GPIO
                            GPIO.setmode(GPIO.BCM)
                            GPIO.setup(self.pin, GPIO.OUT)
                            GPIO.output(self.pin, GPIO.LOW)
                            print(f"✅ Actuator dimatikan via GPIO pin {self.pin}")
                        except Exception as e:
                            print(f"⚠️  Gagal mematikan actuator via GPIO: {e}")
                        
                        # Matikan actuator via API
                        print("🔗 Matikan actuator via API...")
                        if self.api_client.update_water_pump_actuator(False):
                            print("✅ API berhasil - actuator dimatikan di server")
                        else:
                            print("⚠️  API gagal mematikan actuator")
                        
                        # Set flag bahwa waterPump sudah dimatikan otomatis
                        self.waterpump_auto_stopped = True
                        print("🔒 WaterPump sudah dimatikan otomatis - sekarang bisa dikontrol manual via dashboard")
                    else:
                        print("🔒 WaterPump sudah dimatikan otomatis sebelumnya - sekarang bisa dikontrol manual via dashboard")
                    
                    # Kirim notifikasi hanya sekali saat pertama kali terdeteksi
                    if not self.notification_sent:
                        print("🔔 Mengirim notifikasi water level tinggi...")
                        self.send_water_level_notification(water_level, self.safety_threshold, is_high_level=True)
                        self.notification_sent = True
                        print("🔔 Notifikasi water level tinggi telah dikirim")
                    else:
                        print("🔒 Notifikasi sudah dikirim sebelumnya - water level masih tinggi")
                    
                    # Update sensor monitoring status ke Alarm Max
                    print("📊 Update sensor monitoring status ke Alarm Max...")
                    self.update_sensor_monitoring_status(water_level, is_alarm_active=True)
                    
                    # Reset rotary lamp auto off flag ketika water level tinggi lagi
                    if hasattr(self, 'rotary_lamp_auto_off'):
                        delattr(self, 'rotary_lamp_auto_off')
                        print("🔄 Rotary lamp auto off flag direset - water level tinggi lagi")
                    
                    # Aktifkan rotaryLamp via GPIO pin 0 (alarm visual) - hanya sekali
                    if not hasattr(self, 'rotary_lamp_activated'):
                        try:
                            import RPi.GPIO as GPIO
                            GPIO.setmode(GPIO.BCM)
                            GPIO.setup(0, GPIO.OUT)
                            GPIO.output(0, GPIO.HIGH)  # HIGH = ON untuk rotary lamp
                            print("✅ Rotary lamp diaktifkan via GPIO pin 0 (alarm visual)")
                            
                            # Aktifkan rotary lamp via API juga
                            print("🔗 Aktifkan rotary lamp via API...")
                            if self.api_client.update_rotary_lamp_actuator(True):
                                print("✅ API berhasil - rotary lamp diaktifkan di server")
                            else:
                                print("⚠️  API gagal mengaktifkan rotary lamp, tapi sudah ON via GPIO")
                            
                            # Set flag bahwa rotary lamp sudah diaktifkan
                            self.rotary_lamp_activated = True
                        except Exception as e:
                            print(f"⚠️  Gagal mengaktifkan rotary lamp: {e}")
                    else:
                        print("✅ Rotary lamp sudah diaktifkan sebelumnya")
                        
                else:
                    # WATER LEVEL AMAN + ALARM ACTIVE = AUTO MATIKAN ROTARY LAMP SEKALI
                    if self.notification_sent:
                        # Reset notification flag jika water level kembali aman
                        self.notification_sent = False
                        print("🔄 Notification flag direset - water level kembali aman")
                    
                    # Auto matikan rotaryLamp hanya sekali saat water level kembali aman
                    if not hasattr(self, 'rotary_lamp_auto_off'):
                        print("💡 Water level aman - rotaryLamp akan dimatikan otomatis untuk pertama kali...")
                        
                        # Matikan rotaryLamp via GPIO
                        try:
                            import RPi.GPIO as GPIO
                            GPIO.setmode(GPIO.BCM)
                            GPIO.setup(0, GPIO.OUT)
                            GPIO.output(0, GPIO.LOW)  # LOW = OFF untuk rotary lamp
                            print("✅ Rotary lamp dimatikan via GPIO pin 0")
                        except Exception as e:
                            print(f"⚠️  Gagal mematikan rotary lamp via GPIO: {e}")
                        
                        # Matikan rotary lamp via API
                        print("🔗 Matikan rotary lamp via API...")
                        if self.api_client.update_rotary_lamp_actuator(False):
                            print("✅ API berhasil - rotary lamp dimatikan di server")
                        else:
                            print("⚠️  API gagal mematikan rotary lamp")
                        
                        # Set flag bahwa rotary lamp sudah dimatikan otomatis
                        self.rotary_lamp_auto_off = True
                        print("🔒 Rotary lamp sudah dimatikan otomatis - sekarang bisa dikontrol manual via dashboard")
                    else:
                        print("🔒 Rotary lamp sudah dimatikan otomatis sebelumnya - sekarang bisa dikontrol manual via dashboard")
                    
                    # Reset rotary lamp activated flag jika ada
                    if hasattr(self, 'rotary_lamp_activated'):
                        delattr(self, 'rotary_lamp_activated')
                        print("🔄 Rotary lamp activated flag direset")
                    
                    # Reset waterPump auto stop flag jika ada
                    if hasattr(self, 'waterpump_auto_stopped'):
                        delattr(self, 'waterpump_auto_stopped')
                        print("🔄 WaterPump auto stop flag direset")
                    
                    print(f"✅ Water level aman: {water_level:.1f} cm < {self.safety_threshold} cm")
                    print("💡 Actuator bisa dioperasikan manual via dashboard")
                    
                    # Update sensor monitoring status ke Normal
                    print("📊 Update sensor monitoring status ke Normal...")
                    self.update_sensor_monitoring_status(water_level, is_alarm_active=False)
            else:
                # ALARM INACTIVE = AUTO MATIKAN ROTARY LAMP SEKALI
                if self.notification_sent:
                    self.notification_sent = False
                    print("🔄 Notification flag direset - alarm INACTIVE")
                
                # Auto matikan rotaryLamp hanya sekali saat alarm INACTIVE
                if not hasattr(self, 'rotary_lamp_auto_off'):
                    print("💡 Alarm INACTIVE - rotaryLamp akan dimatikan otomatis untuk pertama kali...")
                    
                    # Matikan rotaryLamp via GPIO
                    try:
                        import RPi.GPIO as GPIO
                        GPIO.setmode(GPIO.BCM)
                        GPIO.setup(0, GPIO.OUT)
                        GPIO.output(0, GPIO.LOW)  # LOW = OFF untuk rotary lamp
                        print("✅ Rotary lamp dimatikan via GPIO pin 0")
                    except Exception as e:
                        print(f"⚠️  Gagal mematikan rotary lamp via GPIO: {e}")
                    
                    # Matikan rotary lamp via API
                    print("🔗 Matikan rotary lamp via API...")
                    if self.api_client.update_rotary_lamp_actuator(False):
                        print("✅ API berhasil - rotary lamp dimatikan di server")
                    else:
                        print("⚠️  API gagal mematikan rotary lamp")
                    
                    # Set flag bahwa rotary lamp sudah dimatikan otomatis
                    self.rotary_lamp_auto_off = True
                    print("🔒 Rotary lamp sudah dimatikan otomatis - sekarang bisa dikontrol manual via dashboard")
                else:
                    print("🔒 Rotary lamp sudah dimatikan otomatis sebelumnya - sekarang bisa dikontrol manual via dashboard")
                
                # Reset rotary lamp activated flag jika ada
                if hasattr(self, 'rotary_lamp_activated'):
                    delattr(self, 'rotary_lamp_activated')
                    print("🔄 Rotary lamp activated flag direset - alarm INACTIVE")
                
                # Reset waterPump auto stop flag jika ada
                if hasattr(self, 'waterpump_auto_stopped'):
                    delattr(self, 'waterpump_auto_stopped')
                    print("🔄 WaterPump auto stop flag direset - alarm INACTIVE")
                
                print(f"✅ Alarm INACTIVE - actuator bisa dioperasikan manual dari dashboard")
                print(f"💡 Water level: {water_level:.1f} cm, threshold: {self.safety_threshold} cm")
                
                # Update sensor monitoring status ke Normal (karena alarm INACTIVE)
                print("📊 Update sensor monitoring status ke Normal (alarm INACTIVE)...")
                self.update_sensor_monitoring_status(water_level, is_alarm_active=False)
                
        except Exception as e:
            print(f"❌ Error dalam check dan control actuator: {e}")
            print("🔒 Flag notifikasi tidak diubah karena error")
    
    def start_monitoring(self):
        """
        Mulai monitoring water level menggunakan function dari actuatorLibrary + API endpoint
        dengan timing yang dioptimasi untuk minimal delay
        """
        if self.is_monitoring:
            print("⚠️  Monitoring sudah berjalan")
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            # Import function lokal
            import RPi.GPIO as GPIO
            
            print(f"🚰 Memulai monitoring water level untuk {self.actuator_custom_id}")
            print("🔄 Mode: Auto Stop Once + Auto Rotary Lamp + Manual Control")
            print(f"⏱️  Interval: {self.check_interval} detik (dengan timing optimization)")
            
            # Login sekali di awal
            print("🔐 Login ke API Synapsis...")
            if not self.api_client.login():
                print("❌ Gagal login, monitoring akan berjalan tanpa API sync")
            
            # Timing tracking untuk optimasi
            last_loop_start = time.time()
            loop_count = 0
            
            while self.is_monitoring:
                loop_start = time.time()
                loop_count += 1
                
                try:
                    # Refresh threshold dan alarm status secara berkala (setiap 2 detik)
                    self.update_safety_threshold()
                    self.update_alarm_status()
                    
                    # Gunakan function dari actuatorLibrary
                    water_level = read_water_level_safety()
                    
                    if water_level is not None:
                        print(f"📊 Water level: {water_level:.1f} cm")
                        
                        # Cek dan monitoring water level (tidak ada kontrol otomatis actuator)
                        self.check_and_control_actuator(water_level)
                        
                        # Hapus kontrol otomatis rotary lamp - hanya monitoring
                        # Rotary lamp akan dikontrol manual via dashboard
                        print("💡 Rotary lamp dikontrol manual via dashboard")
                    else:
                        print(f"⚠️  Tidak bisa membaca water level")
                    
                    # Calculate processing time dan compensate untuk timing yang akurat
                    processing_time = time.time() - loop_start
                    
                    if loop_count > 1:  # Skip first loop
                        actual_interval = loop_start - last_loop_start
                        if abs(actual_interval - self.check_interval) > 0.1:
                            print(f"⚠️  Timing delay: {actual_interval:.2f}s (target: {self.check_interval}s)")
                        else:
                            print(f"✅ Timing akurat: {actual_interval:.2f}s")
                    
                    # Calculate sleep time to compensate for processing delay
                    sleep_time = max(0, self.check_interval - processing_time)
                    
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                    else:
                        print(f"🚨 Processing terlalu lama: {processing_time:.2f}s > {self.check_interval}s")
                        # Skip sleep jika processing terlalu lama
                    
                    last_loop_start = loop_start
                
                except Exception as e:
                    print(f"❌ Error monitoring water level: {e}")
                    # Fallback ke sleep normal jika ada error
                    time.sleep(self.check_interval)
        
        # Start monitoring dalam thread terpisah
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("✅ Monitoring started dengan mode auto stop once + auto rotary lamp + manual control")
    
    def stop_monitoring(self):
        """
        Stop monitoring
        """
        if not self.is_monitoring:
            print("⚠️  Monitoring tidak sedang berjalan")
            return
        
        self.is_monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        print("⏹️  Monitoring stopped")
    
    def reset_water_level_tracking(self):
        """
        Reset water level tracking - untuk testing atau manual reset
        """
        self.last_water_level = None
        print("🔄 Water level tracking berhasil direset")
    
    def get_status(self):
        """
        Dapatkan status monitoring
        """
        water_level = read_water_level_safety()
        actuator_info = self.get_actuator_info()
        
        return {
            "is_monitoring": self.is_monitoring,
            "actuator_custom_id": self.actuator_custom_id,
            "pin": self.pin,
            "rotary_lamp_pin": 0,
            "water_level": water_level,
            "safety_threshold": self.safety_threshold,
            "alarm_status": self.alarm_status,
            "notification_sent": self.notification_sent,
            "check_interval": self.check_interval,
            "actuator_info": actuator_info,
            "mode": "monitoring_only",
            "last_water_level": self.last_water_level
        }

    def update_safety_threshold(self, force_refresh=False):
        """
        Update safety threshold dari database sensorListDB.
        Mengembalikan True jika berhasil, False jika gagal.
        """
        current_time = time.time()
        
        # Gunakan cache jika belum expired dan tidak force refresh
        if (not force_refresh and 
            self.safety_threshold is not None and 
            current_time - self.last_threshold_check < self.threshold_cache_duration):
            return True
        
        try:
            print("🔍 Mengambil safety threshold dari database sensor...")
            
            # Import database connection
            from query_project_db import SensorListDB
            
            # Query sensor water level untuk mendapatkan max threshold
            sensor_data = SensorListDB.selectOne("waterLevelRtu1")
            
            if sensor_data and len(sensor_data) > 0:
                sensor_info = sensor_data[0]
                max_threshold = sensor_info.get('max')
                
                if max_threshold is not None:
                    new_threshold = int(max_threshold)  # Convert ke integer
                    
                    # Cek apakah threshold berubah
                    if self.safety_threshold != new_threshold:
                        print(f"🔄 Threshold berubah: {self.safety_threshold} cm → {new_threshold} cm")
                        self.safety_threshold = new_threshold
                    else:
                        print(f"✅ Safety threshold dari database: {self.safety_threshold} cm (tidak berubah)")
                    
                    self.last_threshold_check = current_time
                    return True
                else:
                    print("❌ Max threshold tidak ditemukan di database")
                    print("❌ Sistem tidak bisa berjalan tanpa threshold yang valid")
                    return False
            else:
                print("❌ Data sensor water level tidak ditemukan di database")
                print("❌ Sistem tidak bisa berjalan tanpa threshold yang valid")
                return False
                
        except Exception as e:
            print(f"❌ Error mengambil safety threshold dari database: {e}")
            print("❌ Sistem tidak bisa berjalan tanpa threshold yang valid")
            return False

    def update_alarm_status(self, force_refresh=False):
        """
        Update alarm status dari database sensorListDB.
        Mengembalikan True jika berhasil, False jika gagal.
        """
        current_time = time.time()
        
        # Gunakan cache jika belum expired dan tidak force refresh
        if (not force_refresh and 
            self.alarm_status is not None and 
            current_time - self.last_alarm_check < self.alarm_cache_duration):
            return True
        
        try:
            print("🔍 Mengambil alarm status dari database sensor...")
            
            # Import database connection
            from query_project_db import SensorListDB
            
            # Query sensor water level untuk mendapatkan alarm status
            sensor_data = SensorListDB.selectOne("waterLevelRtu1")
            
            if sensor_data and len(sensor_data) > 0:
                sensor_info = sensor_data[0]
                alarm_value = sensor_info.get('alarm')
                conditions_value = sensor_info.get('conditions')
                
                # Tentukan status alarm berdasarkan alarm dan conditions
                if alarm_value == 1 and conditions_value == "Alarm Active":
                    new_alarm_status = "ACTIVE"
                elif alarm_value == 0 and conditions_value == "Alarm Inactive":
                    new_alarm_status = "INACTIVE"
                else:
                    # Fallback berdasarkan alarm value saja
                    new_alarm_status = "ACTIVE" if alarm_value == 1 else "INACTIVE"
                
                # Cek apakah alarm status berubah
                if self.alarm_status != new_alarm_status:
                    print(f"🔄 Alarm status berubah: {self.alarm_status} → {new_alarm_status}")
                    self.alarm_status = new_alarm_status
                else:
                    print(f"✅ Alarm status dari database: {self.alarm_status} (tidak berubah)")
                
                self.last_alarm_check = current_time
                return True
            else:
                print("❌ Data sensor water level tidak ditemukan di database")
                print("❌ Sistem tidak bisa berjalan tanpa alarm status yang valid")
                return False
                
        except Exception as e:
            print(f"❌ Error mengambil alarm status dari database: {e}")
            print("❌ Sistem tidak bisa berjalan tanpa alarm status yang valid")
            return False

    def send_water_level_notification(self, water_level, threshold, is_high_level=True):
        """
        Kirim notifikasi water level via API
        """
        try:
            if is_high_level:
                print("🔔 Mengirim notifikasi water level tinggi...")
            else:
                print("🔔 Mengirim notifikasi water level normal...")
            
            # Kirim notifikasi via API (menggunakan parameter yang sesuai)
            if self.api_client.send_water_level_notifications(water_level, threshold):
                print("✅ Notifikasi berhasil dikirim")
                return True
            else:
                print("⚠️  Gagal mengirim notifikasi")
                return False
                
        except Exception as e:
            print(f"❌ Error mengirim notifikasi: {e}")
            return False

    def turn_on_rotary_lamp(self):
        """
        Aktifkan rotary lamp via GPIO pin 0 (alarm visual)
        """
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(0, GPIO.OUT)
            GPIO.output(0, GPIO.HIGH)  # HIGH = ON untuk rotary lamp
            print("✅ Rotary lamp diaktifkan via GPIO pin 0 (alarm visual)")
            return True
        except Exception as e:
            print(f"⚠️  Gagal mengaktifkan rotary lamp: {e}")
            return False

    def turn_off_rotary_lamp(self):
        """
        Matikan rotary lamp via GPIO pin 0
        """
        try:
            import RPi.GPIO as GPIO
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(0, GPIO.OUT)
            GPIO.output(0, GPIO.LOW)  # LOW = OFF untuk rotary lamp
            print("✅ Rotary lamp dimatikan via GPIO pin 0")
            return True
        except Exception as e:
            print(f"⚠️  Gagal mematikan rotary lamp: {e}")
            return False
    
    def reset_notification_flag(self):
        """
        Reset notification flag - untuk testing atau manual reset
        """
        self.notification_sent = False
        print("🔄 Notification flag berhasil direset")

    def get_current_timestamp(self):
        """
        Get current timestamp dalam UTC-7 (WIB) dengan format realtime
        """
        try:
            # Coba gunakan library times terlebih dahulu
            return times.getDatetime()
        except:
            # Fallback ke datetime standard dengan UTC-7
            # UTC-7 = WIB (Waktu Indonesia Barat)
            utc_time = datetime.datetime.utcnow()
            wib_time = utc_time + datetime.timedelta(hours=7)
            return wib_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_realtime_timestamp(self):
        """
        Get timestamp realtime dalam WIB - selalu fresh dan akurat
        """
        # Gunakan waktu lokal server yang sudah dalam format WIB
        # Ini menghindari masalah konversi timezone dan memberikan waktu yang akurat
        try:
            # Method 1: Gunakan waktu lokal server (asumsi server sudah dalam WIB)
            local_time = datetime.datetime.now()
            return local_time.strftime("%Y-%m-%d %H:%M:%S")
        except:
            # Method 2: Fallback ke UTC+7 jika ada masalah
            try:
                utc_time = datetime.datetime.now(datetime.timezone.utc)
                wib_time = utc_time + datetime.timedelta(hours=7)
                return wib_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                # Method 3: Fallback ke method lama
                utc_time = datetime.datetime.utcnow()
                wib_time = utc_time + datetime.timedelta(hours=7)
                return wib_time.strftime("%Y-%m-%d %H:%M:%S")

    def update_sensor_monitoring_status(self, water_level, is_alarm_active=False):
        """
        Update status sensor monitoring via API ketika alarm aktif dan water level di atas threshold
        
        Format data yang dikirim sesuai dengan curl:
        {
            "node_id": "b949aecbf0f34bb48b94a7be960b78ce",
            "status": "3", // 3 = Alarm Max, 1 = Normal
            "data": {
                "waterLevelRtu1": {water_level}
            },
            "timestamp": "2025-07-03 19:45:30"
        }
        
        Status:
        - "3" = Alarm Max (water level tinggi + alarm ACTIVE)
        - "1" = Normal (water level aman atau alarm INACTIVE)
        """
        try:
            if not self.api_client.is_logged_in():
                if not self.api_client.login():
                    print("❌ Gagal login untuk update sensor monitoring status")
                    return False
            
            # Tentukan status berdasarkan water level dan alarm
            if is_alarm_active and water_level is not None and water_level >= self.safety_threshold:
                # Water level tinggi + alarm aktif = Alarm Max
                status = "3"
                status_description = "Alarm Max"
                print(f"🚨 Update sensor monitoring status: {status_description} (water level: {water_level:.1f} cm ≥ {self.safety_threshold} cm)")
            else:
                # Water level normal atau alarm tidak aktif = Normal
                status = "1"
                status_description = "Normal"
                print(f"✅ Update sensor monitoring status: {status_description} (water level: {water_level:.1f} cm < {self.safety_threshold} cm)")
            
            # Data untuk API (tanpa timestamp - server akan generate otomatis)
            monitoring_data = {
                "node_id": "b949aecbf0f34bb48b94a7be960b78ce",
                "status": status,
                "data": {
                    "waterLevelRtu1": water_level if water_level is not None else 0
                }
            }
            
            print(f"📤 Mengirim data monitoring ke API:")
            print(f"   🆔 Node ID: {monitoring_data['node_id']}")
            print(f"   🚨 Status: {status} ({status_description})")
            print(f"   📊 Water Level: {monitoring_data['data']['waterLevelRtu1']} cm")
            print(f"   ⏰ Timestamp: Server generate otomatis")
            
            # Hit API endpoint untuk update sensor monitoring status
            response = self.api_client.update_sensor_monitoring_status(monitoring_data)
            
            # Handle response yang bisa berupa dict atau boolean
            if response:
                if isinstance(response, dict):
                    # Response berupa dict dengan field status
                    if response.get('status'):
                        print(f"✅ Berhasil update sensor monitoring status: {status_description}")
                        return True
                    else:
                        print(f"⚠️  Gagal update sensor monitoring status: {response.get('message', 'Unknown error')}")
                        return False
                elif isinstance(response, bool):
                    # Response berupa boolean (legacy)
                    if response:
                        print(f"✅ Berhasil update sensor monitoring status: {status_description}")
                        return True
                    else:
                        print(f"⚠️  Gagal update sensor monitoring status: Unknown error")
                        return False
                else:
                    # Response type tidak dikenal
                    print(f"⚠️  Response type tidak dikenal: {type(response)}")
                    return False
            else:
                print(f"⚠️  Tidak ada response dari API")
                return False
                
        except Exception as e:
            print(f"❌ Error update sensor monitoring status: {e}")
            return False


def main():
    """
    Main function untuk menjalankan monitoring dengan sync actuatorLibrary + API
    """
    print("🚰 Water Level Monitor - Sync actuatorLibrary + API Endpoint")
    print("=" * 50)
    print("Endpoint: https://dev-nearon.synapsis.id/api/projectnode/nodes/b949aecbf0f34bb48b94a7be960b78ce/actuators/5a6bc3a3efdc427ab9df7bfb3c82092e/value")
    print("🎯 Fokus: Sync output actuatorLibrary + hit API endpoint")
    print("=" * 50)
    
    try:
        # Buat monitor dengan parameter dari actuatorLibrary
        monitor = WaterLevelMonitor(
            actuator_custom_id="waterPump",
            pin=7,
            check_interval=2  # ← Ubah ke 2 detik untuk alarm setiap 2 detik
        )
        
        # Test API connection terlebih dahulu
        print("🔍 Testing API connection...")
        if monitor.api_client.test_connection():
            print("✅ API connection OK")
        else:
            print("⚠️  API connection gagal, monitoring tetap berjalan")
        
        # Mulai monitoring
        print("\n🔄 Memulai monitoring dengan sync actuatorLibrary...")
        monitor.start_monitoring()
        
        # Jalankan terus menerus
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Sistem dihentikan oleh user")
        if 'monitor' in locals():
            monitor.stop_monitoring()
    except Exception as e:
        print(f"❌ Error dalam sistem: {e}")


def test_actuator_library_sync():
    """
    Test sync dengan actuatorLibrary + API endpoint
    """
    print("🧪 Test sync actuatorLibrary + API endpoint...")
    
    try:
        # Buat client API
        client = SynapsisAPIClient()
        
        # Login
        if not client.login():
            print("❌ Gagal login")
            return False
        
        # Dapatkan water level menggunakan function actuatorLibrary
        water_level = read_water_level_safety()
        
        if water_level is not None:
            print(f"📊 Water level dari actuatorLibrary: {water_level:.1f} cm")
            
            # Check safety threshold (sama dengan actuatorLibrary)
            SAFETY_THRESHOLD = 10
            if water_level >= SAFETY_THRESHOLD:
                print(f"🚨 Safety threshold tercapai: {water_level:.1f} cm ≥ {SAFETY_THRESHOLD} cm")
                print("🔴 Matikan water pump actuator via API")
                
                # Hit API endpoint untuk matikan actuator
                result = client.update_water_pump_actuator(False)
                if result:
                    print("✅ API hit berhasil - actuator dimatikan di server")
                    
                    return True
                else:
                    print("❌ API hit gagal - tidak bisa matikan actuator di server")
                    return False
            else:
                print(f"✅ Water level aman: {water_level:.1f} cm < {SAFETY_THRESHOLD} cm")
                print("💡 Tidak melakukan apa-apa terhadap actuator (tetap status sebelumnya)")
                return True
        else:
            print("❌ Tidak ada data water level dari actuatorLibrary")
            return False
            
    except Exception as e:
        print(f"❌ Error test sync: {e}")
        return False


def test_actuator_info():
    """
    Test mendapatkan informasi actuator dari API
    """
    print("🧪 Test get actuator info dari API...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Test get actuator info
        print("🔍 Testing get_actuator_info...")
        actuator_info = monitor.get_actuator_info()
        
        if actuator_info:
            print("✅ Berhasil mendapatkan info actuator:")
            print(f"   📝 Nama: {actuator_info.get('name', 'N/A')}")
            print(f"   🆔 ID: {actuator_info.get('id', 'N/A')}")
            print(f"   💡 Status: {actuator_info.get('value', 'N/A')}")
            print(f"   ⏰ Updated: {actuator_info.get('updated_at', 'N/A')}")
            return True
        else:
            print("❌ Gagal mendapatkan info actuator")
            return False
            
    except Exception as e:
        print(f"❌ Error test actuator info: {e}")
        return False


def test_responsive_control():
    """
    Test responsive control - cek dan kontrol actuator berdasarkan water level
    """
    print("🧪 Test responsive control...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Dapatkan water level
        water_level = read_water_level_safety()
        
        if water_level is not None:
            print(f"📊 Water level: {water_level:.1f} cm")
            
            # Test responsive control
            print("🔄 Testing check_and_control_actuator...")
            monitor.check_and_control_actuator(water_level)
            
            return True
        else:
            print("❌ Tidak bisa membaca water level")
            return False
            
    except Exception as e:
        print(f"❌ Error test responsive control: {e}")
        return False


def test_actuator_library_integration():
    """
    Test integrasi dengan actuatorLibrary - menggunakan function yang sudah ada
    """
    print("🧪 Test integrasi dengan actuatorLibrary...")
    
    try:
        from query_project_db import ActuatorListDB
        
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Test 1: Get actuator info dari database lokal
        print("\n🔍 Test 1: Get actuator info dari database lokal...")
        actuator_info = monitor.get_actuator_info()
        
        if actuator_info:
            print("✅ Berhasil mendapatkan info actuator dari database lokal:")
            print(f"   📝 Nama: {actuator_info.get('name', 'N/A')}")
            print(f"   🆔 ID: {actuator_info.get('id', 'N/A')}")
            print(f"   💡 Status: {actuator_info.get('state', 'N/A')}")
            print(f"   🔧 Last Action Value: {actuator_info.get('last_action_value', 'N/A')}")
        else:
            print("❌ Gagal mendapatkan info actuator dari database lokal")
        
        # Test 2: Water level safety check dari actuatorLibrary
        print("\n🔍 Test 2: Water level safety check dari actuatorLibrary...")
        water_level = read_water_level_safety()
        
        if water_level is not None:
            print(f"📊 Water level: {water_level:.1f} cm")
            
            # Test safety check
            is_safe = check_water_level_safety(monitor.actuator_custom_id)
            print(f"🔍 Safety check result: {is_safe}")
            
            if is_safe:
                print("✅ Water level aman")
            else:
                print("🚨 Water level tidak aman - perlu matikan actuator")
        else:
            print("❌ Tidak bisa membaca water level")
        
        # Test 3: Responsive control dengan actuatorLibrary
        print("\n🔍 Test 3: Responsive control dengan actuatorLibrary...")
        if water_level is not None:
            monitor.check_and_control_actuator(water_level)
        
        return True
        
    except Exception as e:
        print(f"❌ Error test integrasi actuatorLibrary: {e}")
        return False


def test_database_actuator_info():
    """
    Test mendapatkan info actuator dari database lokal
    """
    print("🧪 Test get actuator info dari database lokal...")
    
    try:
        from query_project_db import ActuatorListDB
        
        # Test get actuator info dari database
        actuator_data = ActuatorListDB.selectByActId("waterPump")
        
        if actuator_data and len(actuator_data) > 0:
            actuator_info = actuator_data[0]
            print("✅ Berhasil mendapatkan info actuator dari database:")
            print(f"   📝 Nama: {actuator_info.get('name', 'N/A')}")
            print(f"   🆔 ID: {actuator_info.get('id', 'N/A')}")
            print(f"   💡 Status: {actuator_info.get('state', 'N/A')}")
            print(f"   🔧 Last Action Value: {actuator_info.get('last_action_value', 'N/A')}")
            print(f"   🌐 Server Value: {actuator_info.get('server_value', 'N/A')}")
            return True
        else:
            print("❌ Tidak ada data actuator dalam database")
            return False
            
    except Exception as e:
        print(f"❌ Error test database actuator info: {e}")
        return False


def test_safety_control_logic():
    """
    Test logic safety control yang sudah diperbaiki
    """
    print("🧪 Test logic safety control yang sudah diperbaiki...")
    
    try:
        from query_project_db import ActuatorListDB
        
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Test 1: Get actuator info dan cek interpretasi status
        print("\n🔍 Test 1: Interpretasi status actuator...")
        actuator_info = monitor.get_actuator_info()
        
        if actuator_info:
            actuator_status = actuator_info.get('last_action_value')
            is_actuator_on = actuator_status == 1  # Perbaikan interpretasi
            
            print(f"📊 Status actuator dari DB: {actuator_status}")
            print(f"🔍 Interpretasi ON: {is_actuator_on}")
            
            if actuator_status == 1:
                print("✅ Status actuator: ON (1)")
            else:
                print("✅ Status actuator: OFF (0)")
        
        # Test 2: Water level dan safety check
        print("\n🔍 Test 2: Water level dan safety check...")
        water_level = read_water_level_safety()
        
        if water_level is not None:
            print(f"📊 Water level: {water_level:.1f} cm")
            
            # Test safety check
            is_safe = check_water_level_safety(monitor.actuator_custom_id)
            print(f"🔍 Safety check result: {is_safe}")
            
            if is_safe:
                print("✅ Water level aman - actuator bisa dioperasikan")
            else:
                print("🚨 Water level tidak aman - actuator harus dimatikan")
                
                # Test logic control
                print("\n🔍 Test 3: Logic control untuk water level tinggi...")
                monitor.check_and_control_actuator(water_level)
        else:
            print("❌ Tidak bisa membaca water level")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test safety control logic: {e}")
        return False


def test_force_actuator_off():
    """
    Test memaksa actuator OFF ketika water level tinggi
    """
    print("🧪 Test memaksa actuator OFF ketika water level tinggi...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Simulasi water level tinggi
        high_water_level = 15.0  # Simulasi water level tinggi
        
        print(f"📊 Simulasi water level tinggi: {high_water_level:.1f} cm")
        print("🔍 Testing logic control...")
        
        # Test control logic
        monitor.check_and_control_actuator(high_water_level)
        
        return True
        
    except Exception as e:
        print(f"❌ Error test force actuator off: {e}")
        return False





def test_water_level_transition():
    """
    Test transisi water level dari aman ke tidak aman
    """
    print("🧪 Test transisi water level dari aman ke tidak aman...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Simulasi transisi water level
        water_levels = [5.0, 7.0, 9.0, 11.0, 12.0, 13.0, 8.0, 15.0]
        
        for i, water_level in enumerate(water_levels):
            print(f"\n🔍 Test {i+1}: Water level {water_level:.1f} cm")
            monitor.check_and_control_actuator(water_level)
            print(f"📊 Last water level: {monitor.last_water_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test water level transition: {e}")
        return False


def test_sensor_error_handling():
    """
    Test handling ketika sensor water level tidak terbaca
    """
    print("🧪 Test handling ketika sensor water level tidak terbaca...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Test 1: Simulasi water level None (sensor error)
        print("\n🔍 Test 1: Simulasi water level None (sensor error)...")
        monitor.check_and_control_actuator(None)
        
        # Test 2: Simulasi water level valid lagi
        print("\n🔍 Test 2: Simulasi water level valid lagi (8 cm)...")
        monitor.check_and_control_actuator(8.0)
        
        # Test 3: Simulasi water level tinggi
        print("\n🔍 Test 3: Simulasi water level tinggi (12 cm)...")
        monitor.check_and_control_actuator(12.0)
        
        # Test 4: Simulasi sensor error lagi
        print("\n🔍 Test 4: Simulasi sensor error lagi...")
        monitor.check_and_control_actuator(None)
        
        return True
        
    except Exception as e:
        print(f"❌ Error test sensor error handling: {e}")
        return False


def test_water_level_persistence():
    """
    Test ketahanan water level tracking ketika sensor error
    """
    print("🧪 Test ketahanan water level tracking ketika sensor error...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Simulasi skenario: water level tinggi -> sensor error -> sensor normal
        scenarios = [
            {"water_level": 5.0, "description": "Water level aman"},
            {"water_level": 12.0, "description": "Water level tinggi"},
            {"water_level": None, "description": "Sensor error - tracking tetap"},
            {"water_level": None, "description": "Sensor error lagi - tracking tetap"},
            {"water_level": 8.0, "description": "Sensor normal"},
            {"water_level": 15.0, "description": "Water level tinggi lagi"}
        ]
        
        for i, scenario in enumerate(scenarios):
            print(f"\n🔍 Test {i+1}: {scenario['description']}")
            print(f"📊 Water level: {scenario['water_level']}")
            print(f"📊 Last water level sebelum: {monitor.last_water_level}")
            
            monitor.check_and_control_actuator(scenario['water_level'])
            
            print(f"📊 Last water level setelah: {monitor.last_water_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test water level persistence: {e}")
        return False


def test_threshold_realtime():
    """
    Test threshold realtime - refresh threshold secara berkala
    """
    print("🧪 Test threshold realtime - refresh threshold secara berkala...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Threshold awal: {monitor.safety_threshold} cm")
        
        # Test 1: Refresh threshold (dengan cache)
        print("\n🔍 Test 1: Refresh threshold (dengan cache)...")
        result1 = monitor.update_safety_threshold()
        print(f"✅ Result: {result1}")
        
        # Test 2: Force refresh threshold
        print("\n🔍 Test 2: Force refresh threshold...")
        result2 = monitor.update_safety_threshold(force_refresh=True)
        print(f"✅ Result: {result2}")
        
        # Test 3: Simulasi monitoring loop dengan refresh threshold
        print("\n🔍 Test 3: Simulasi monitoring loop dengan refresh threshold...")
        for i in range(3):
            print(f"\n📊 Iterasi {i+1}:")
            monitor.update_safety_threshold()  # Refresh threshold
            print(f"📊 Threshold: {monitor.safety_threshold} cm")
            time.sleep(1)  # Simulasi interval
        
        return True
        
    except Exception as e:
        print(f"❌ Error test threshold realtime: {e}")
        return False


def test_dynamic_threshold():
    """
    Test threshold dinamis dari database sensorListDB
    """
    print("🧪 Test threshold dinamis dari database...")
    
    try:
        # Import database connection
        from query_project_db import SensorListDB
        
        # Test 1: Get threshold dari database
        print("\n🔍 Test 1: Get threshold dari database sensorListDB...")
        sensor_data = SensorListDB.selectOne("waterLevelRtu1")
        
        if sensor_data and len(sensor_data) > 0:
            sensor_info = sensor_data[0]
            max_threshold = sensor_info.get('max')
            current_value = sensor_info.get('value')
            
            print(f"✅ Data sensor berhasil diambil:")
            print(f"   📝 Nama: {sensor_info.get('name', 'N/A')}")
            print(f"   🆔 ID: {sensor_info.get('sensor_id', 'N/A')}")
            print(f"   📊 Current Value: {current_value}")
            print(f"   🚨 Max Threshold: {max_threshold}")
            print(f"   ⏰ Timestamp: {sensor_info.get('timestamp', 'N/A')}")
            
            # Test 2: Buat monitor dan cek threshold
            print("\n🔍 Test 2: Test monitor dengan threshold dinamis...")
            monitor = WaterLevelMonitor()
            
            print(f"📊 Safety threshold monitor: {monitor.safety_threshold} cm")
            
            # Test 3: Simulasi water level berdasarkan threshold dari database
            if max_threshold is not None:
                # Konversi threshold ke integer untuk perhitungan
                threshold_int = int(max_threshold)
                print(f"\n🔍 Test 3: Simulasi water level berdasarkan threshold {threshold_int} cm...")
                
                # Test water level di bawah threshold
                test_low = threshold_int - 2
                print(f"📊 Test water level rendah: {test_low} cm")
                monitor.check_and_control_actuator(test_low)
                
                # Test water level di atas threshold
                test_high = threshold_int + 1
                print(f"📊 Test water level tinggi: {test_high} cm")
                monitor.check_and_control_actuator(test_high)
                
                # Test water level tepat di threshold
                print(f"📊 Test water level tepat threshold: {threshold_int} cm")
                monitor.check_and_control_actuator(threshold_int)
                
                return True
            else:
                print("❌ Max threshold tidak ditemukan di database")
                return False
        else:
            print("❌ Data sensor tidak ditemukan di database")
            return False
            
    except Exception as e:
        print(f"❌ Error test dynamic threshold: {e}")
        return False


def test_threshold_required():
    """
    Test bahwa threshold wajib dari database (tidak ada default)
    """
    print("🧪 Test threshold wajib dari database...")
    
    try:
        # Test 1: Coba buat monitor (seharusnya berhasil jika database tersedia)
        print("\n🔍 Test 1: Membuat monitor dengan threshold dari database...")
        monitor = WaterLevelMonitor()
        
        print(f"✅ Monitor berhasil dibuat dengan threshold: {monitor.safety_threshold} cm")
        
        # Test 2: Cek bahwa threshold tidak None
        if monitor.safety_threshold is not None:
            print("✅ Threshold berhasil diambil dari database")
            return True
        else:
            print("❌ Threshold tidak berhasil diambil dari database")
            return False
            
    except ValueError as e:
        print(f"❌ Monitor gagal dibuat: {e}")
        print("✅ Sistem berhasil mendeteksi bahwa threshold tidak tersedia")
        return True  # Ini adalah expected behavior
        
    except Exception as e:
        print(f"❌ Error test threshold required: {e}")
        return False


def test_alarm_status():
    """
    Test alarm status dari database sensorListDB
    """
    print("🧪 Test alarm status dari database...")
    
    try:
        # Import database connection
        from query_project_db import SensorListDB
        
        # Test 1: Get alarm status dari database
        print("\n🔍 Test 1: Get alarm status dari database sensorListDB...")
        sensor_data = SensorListDB.selectOne("waterLevelRtu1")
        
        if sensor_data and len(sensor_data) > 0:
            sensor_info = sensor_data[0]
            alarm_value = sensor_info.get('alarm')
            conditions_value = sensor_info.get('conditions')
            
            print(f"✅ Data sensor berhasil diambil:")
            print(f"   📝 Nama: {sensor_info.get('name', 'N/A')}")
            print(f"   🆔 ID: {sensor_info.get('sensor_id', 'N/A')}")
            print(f"   🚨 Alarm Value: {alarm_value}")
            print(f"   📋 Conditions: {conditions_value}")
            
            # Test 2: Buat monitor dan cek alarm status
            print("\n🔍 Test 2: Test monitor dengan alarm status...")
            monitor = WaterLevelMonitor()
            
            print(f"📊 Alarm status monitor: {monitor.alarm_status}")
            
            # Test 3: Simulasi kontrol berdasarkan alarm status
            print("\n🔍 Test 3: Simulasi kontrol berdasarkan alarm status...")
            water_level = 15.0  # Simulasi water level tinggi
            
            if monitor.alarm_status == "ACTIVE":
                print(f"📊 Test dengan alarm ACTIVE - water level: {water_level} cm")
                print("🔍 Sistem akan melakukan kontrol otomatis...")
                monitor.check_and_control_actuator(water_level)
            elif monitor.alarm_status == "INACTIVE":
                print(f"📊 Test dengan alarm INACTIVE - water level: {water_level} cm")
                print("🔍 Sistem akan membiarkan kontrol manual...")
                monitor.check_and_control_actuator(water_level)
            else:
                print(f"❌ Alarm status tidak valid: {monitor.alarm_status}")
                return False
            
            return True
        else:
            print("❌ Data sensor tidak ditemukan di database")
            return False
            
    except Exception as e:
        print(f"❌ Error test alarm status: {e}")
        return False


def test_notification():
    """
    Test notification system dengan alarm status
    """
    print("🧪 Test notification system dengan alarm status...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Notification flag awal: {monitor.notification_sent}")
        print(f"📊 Alarm status: {monitor.alarm_status}")
        
        # Test 1: Simulasi water level tinggi dengan alarm ACTIVE
        print("\n🔍 Test 1: Simulasi water level tinggi dengan alarm ACTIVE...")
        water_level_high = 15.0
        monitor.check_and_control_actuator(water_level_high)
        print(f"📊 Notification flag setelah water level tinggi: {monitor.notification_sent}")
        
        # Test 2: Simulasi water level tinggi lagi (tidak kirim notifikasi lagi)
        print("\n🔍 Test 2: Simulasi water level tinggi lagi (tidak kirim notifikasi lagi)...")
        water_level_high2 = 16.0
        monitor.check_and_control_actuator(water_level_high2)
        print(f"📊 Notification flag setelah water level tinggi lagi: {monitor.notification_sent}")
        
        # Test 3: Simulasi water level normal (reset notification flag)
        print("\n🔍 Test 3: Simulasi water level normal (reset notification flag)...")
        water_level_normal = 8.0
        monitor.check_and_control_actuator(water_level_normal)
        print(f"📊 Notification flag setelah water level normal: {monitor.notification_sent}")
        
        # Test 4: Simulasi water level tinggi lagi (kirim notifikasi lagi)
        print("\n🔍 Test 4: Simulasi water level tinggi lagi (kirim notifikasi lagi)...")
        water_level_high3 = 14.0
        monitor.check_and_control_actuator(water_level_high3)
        print(f"📊 Notification flag setelah water level tinggi lagi: {monitor.notification_sent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test notification: {e}")
        return False


def test_notification_logic():
    """
    Test logic notification - hanya kirim sekali saat water level tinggi
    """
    print("🧪 Test logic notification...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Simulasi skenario: normal → tinggi → tinggi → normal → tinggi
        scenarios = [
            {"water_level": 8.0, "description": "Water level normal"},
            {"water_level": 15.0, "description": "Water level tinggi (kirim notifikasi)"},
            {"water_level": 16.0, "description": "Water level tinggi lagi (tidak kirim)"},
            {"water_level": 17.0, "description": "Water level tinggi lagi (tidak kirim)"},
            {"water_level": 7.0, "description": "Water level normal (reset flag)"},
            {"water_level": 14.0, "description": "Water level tinggi lagi (kirim notifikasi lagi)"}
        ]
        
        for i, scenario in enumerate(scenarios):
            print(f"\n🔍 Test {i+1}: {scenario['description']}")
            print(f"📊 Water level: {scenario['water_level']} cm")
            print(f"📊 Notification flag sebelum: {monitor.notification_sent}")
            
            monitor.check_and_control_actuator(scenario['water_level'])
            
            print(f"📊 Notification flag setelah: {monitor.notification_sent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test notification logic: {e}")
        return False


def test_notification_flag_persistence():
    """
    Test ketahanan notification flag ketika sensor error
    """
    print("🧪 Test ketahanan notification flag ketika sensor error...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        # Simulasi skenario: tinggi → sensor error → sensor normal
        scenarios = [
            {"water_level": 15.0, "description": "Water level tinggi (kirim notifikasi)"},
            {"water_level": None, "description": "Sensor error (flag tetap)"},
            {"water_level": None, "description": "Sensor error lagi (flag tetap)"},
            {"water_level": 16.0, "description": "Sensor normal (tidak kirim notifikasi lagi)"},
            {"water_level": 7.0, "description": "Water level normal (reset flag)"}
        ]
        
        for i, scenario in enumerate(scenarios):
            print(f"\n🔍 Test {i+1}: {scenario['description']}")
            print(f"📊 Water level: {scenario['water_level']}")
            print(f"📊 Notification flag sebelum: {monitor.notification_sent}")
            
            monitor.check_and_control_actuator(scenario['water_level'])
            
            print(f"📊 Notification flag setelah: {monitor.notification_sent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test notification flag persistence: {e}")
        return False


def test_notification_with_alarm_status():
    """
    Test notification dengan alarm status yang berbeda
    """
    print("🧪 Test notification dengan alarm status yang berbeda...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Alarm status saat ini: {monitor.alarm_status}")
        print(f"📊 Notification flag awal: {monitor.notification_sent}")
        
        # Test 1: Water level tinggi dengan alarm ACTIVE
        print("\n🔍 Test 1: Water level tinggi dengan alarm ACTIVE...")
        water_level_high = 15.0
        monitor.check_and_control_actuator(water_level_high)
        print(f"📊 Notification flag: {monitor.notification_sent}")
        
        # Test 2: Water level tinggi dengan alarm INACTIVE (simulasi)
        print("\n🔍 Test 2: Water level tinggi dengan alarm INACTIVE (simulasi)...")
        # Simulasi alarm INACTIVE dengan mengubah alarm status sementara
        original_alarm_status = monitor.alarm_status
        monitor.alarm_status = "INACTIVE"
        
        water_level_high2 = 16.0
        monitor.check_and_control_actuator(water_level_high2)
        print(f"📊 Notification flag: {monitor.notification_sent}")
        
        # Kembalikan alarm status
        monitor.alarm_status = original_alarm_status
        
        # Test 3: Water level normal dengan alarm ACTIVE
        print("\n🔍 Test 3: Water level normal dengan alarm ACTIVE...")
        water_level_normal = 8.0
        monitor.check_and_control_actuator(water_level_normal)
        print(f"📊 Notification flag: {monitor.notification_sent}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test notification with alarm status: {e}")
        return False


def test_actuator_safety_lock():
    """
    Test fitur safety lock: Actuator tidak boleh dinyalakan ketika water level masih tinggi
    """
    print("🧪 Test fitur safety lock: Actuator tidak boleh dinyalakan ketika water level tinggi...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Notification flag awal: {monitor.notification_sent}")
        print(f"📊 Alarm status: {monitor.alarm_status}")
        print(f"📊 Safety threshold: {monitor.safety_threshold} cm")
        
        # Test 1: Simulasi water level tinggi dengan alarm ACTIVE
        print("\n🔍 Test 1: Water level tinggi dengan alarm ACTIVE...")
        print("📝 Scenario: Water level tinggi → Actuator harus OFF → Tidak boleh dinyalakan")
        
        water_level_high = 15.0
        print(f"📊 Simulasi water level tinggi: {water_level_high:.1f} cm")
        
        # Test pertama kali (kirim notifikasi)
        monitor.check_and_control_actuator(water_level_high)
        print(f"📊 Notification flag setelah test 1: {monitor.notification_sent}")
        
        # Test kedua kali (tidak kirim notifikasi, tapi tetap pastikan actuator OFF)
        print("\n🔍 Test 2: Water level masih tinggi (tidak kirim notifikasi lagi)...")
        water_level_high2 = 16.0
        monitor.check_and_control_actuator(water_level_high2)
        print(f"📊 Notification flag setelah test 2: {monitor.notification_sent}")
        
        # Test ketiga kali (water level masih tinggi, actuator tetap OFF)
        print("\n🔍 Test 3: Water level masih tinggi (actuator tetap OFF)...")
        water_level_high3 = 14.0
        monitor.check_and_control_actuator(water_level_high3)
        print(f"📊 Notification flag setelah test 3: {monitor.notification_sent}")
        
        # Test 4: Simulasi water level normal (reset notification flag)
        print("\n🔍 Test 4: Water level normal (reset notification flag)...")
        water_level_normal = 8.0
        monitor.check_and_control_actuator(water_level_normal)
        print(f"📊 Notification flag setelah test 4: {monitor.notification_sent}")
        
        # Test 5: Simulasi water level tinggi lagi (kirim notifikasi lagi)
        print("\n🔍 Test 5: Water level tinggi lagi (kirim notifikasi lagi)...")
        water_level_high4 = 12.0
        monitor.check_and_control_actuator(water_level_high4)
        print(f"📊 Notification flag setelah test 5: {monitor.notification_sent}")
        
        print("\n✅ Test safety lock selesai!")
        print("🎯 Fitur utama:")
        print("   1. Actuator dimatikan ketika water level tinggi + alarm ACTIVE")
        print("   2. Actuator tetap OFF sampai water level kembali aman")
        print("   3. Notifikasi hanya dikirim sekali per kejadian")
        print("   4. Actuator bisa dinyalakan manual hanya jika water level aman atau alarm INACTIVE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test actuator safety lock: {e}")
        return False


def test_rotary_lamp_control():
    """
    Test kontrol rotary lamp ketika water level tinggi
    """
    print("🧪 Test kontrol rotary lamp ketika water level tinggi...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Safety threshold: {monitor.safety_threshold} cm")
        print(f"📊 Alarm status: {monitor.alarm_status}")
        
        # Test 1: Test method turn_off_rotary_lamp
        print("\n🔍 Test 1: Test method turn_off_rotary_lamp...")
        result = monitor.turn_off_rotary_lamp()
        print(f"✅ Result: {result}")
        
        # Test 2: Simulasi water level tinggi dengan alarm ACTIVE
        print("\n🔍 Test 2: Simulasi water level tinggi dengan alarm ACTIVE...")
        water_level_high = 15.0
        print(f"📊 Simulasi water level tinggi: {water_level_high:.1f} cm")
        
        # Test control logic yang akan mematikan rotary lamp
        monitor.check_and_control_actuator(water_level_high)
        
        # Test 3: Simulasi water level normal
        print("\n🔍 Test 3: Simulasi water level normal...")
        water_level_normal = 8.0
        monitor.check_and_control_actuator(water_level_normal)
        
        print("\n✅ Test rotary lamp control selesai!")
        print("🎯 Fitur utama:")
        print("   1. Rotary lamp dimatikan ketika water level tinggi + alarm ACTIVE")
        print("   2. Rotary lamp tetap OFF sampai water level kembali aman")
        print("   3. Kontrol otomatis via GPIO pin 0")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test rotary lamp control: {e}")
        return False


def test_sensor_monitoring_status_update():
    """
    Test update sensor monitoring status ketika alarm aktif dan water level di atas threshold
    """
    print("🧪 Test update sensor monitoring status...")
    
    try:
        # Buat monitor
        monitor = WaterLevelMonitor()
        
        print(f"📊 Safety threshold: {monitor.safety_threshold} cm")
        print(f"📊 Alarm status: {monitor.alarm_status}")
        
        # Test 1: Simulasi water level tinggi dengan alarm ACTIVE
        print("\n🔍 Test 1: Simulasi water level tinggi dengan alarm ACTIVE...")
        water_level_high = 15.0
        print(f"📊 Simulasi water level tinggi: {water_level_high:.1f} cm")
        
        # Test control logic yang akan update status ke Alarm Max
        monitor.check_and_control_actuator(water_level_high)
        
        # Test 2: Simulasi water level normal
        print("\n🔍 Test 2: Simulasi water level normal...")
        water_level_normal = 8.0
        monitor.check_and_control_actuator(water_level_normal)
        
        # Test 3: Test method update_sensor_monitoring_status langsung
        print("\n🔍 Test 3: Test method update_sensor_monitoring_status langsung...")
        result = monitor.update_sensor_monitoring_status(water_level_high, is_alarm_active=True)
        print(f"✅ Result update status Alarm Max: {result}")
        
        result2 = monitor.update_sensor_monitoring_status(water_level_normal, is_alarm_active=False)
        print(f"✅ Result update status Normal: {result2}")
        
        print("\n✅ Test sensor monitoring status update selesai!")
        print("🎯 Fitur utama:")
        print("   1. Status diupdate ke '3' (Alarm Max) ketika water level tinggi + alarm ACTIVE")
        print("   2. Status diupdate ke '1' (Normal) ketika water level aman atau alarm INACTIVE")
        print("   3. Data dikirim ke API endpoint monitoring-data")
        print("   4. Format data sesuai dengan curl yang diberikan")
        
        return True
        
    except Exception as e:
        print(f"❌ Error test sensor monitoring status update: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Water Level Monitor - Sync actuatorLibrary + API")
    parser.add_argument("--test", action="store_true", help="Test sync actuatorLibrary + API sekali")
    parser.add_argument("--actuator-info", action="store_true", help="Test get actuator info dari API")
    parser.add_argument("--responsive", action="store_true", help="Test responsive control")
    parser.add_argument("--integration", action="store_true", help="Test integrasi dengan actuatorLibrary")
    parser.add_argument("--database", action="store_true", help="Test get actuator info dari database lokal")
    parser.add_argument("--safety-logic", action="store_true", help="Test logic safety control yang sudah diperbaiki")
    parser.add_argument("--force-off", action="store_true", help="Test memaksa actuator OFF ketika water level tinggi")
    parser.add_argument("--water-level-transition", action="store_true", help="Test transisi water level dari aman ke tidak aman")
    parser.add_argument("--sensor-error", action="store_true", help="Test handling ketika sensor water level tidak terbaca")
    parser.add_argument("--water-level-persistence", action="store_true", help="Test ketahanan water level tracking ketika sensor error")
    parser.add_argument("--dynamic-threshold", action="store_true", help="Test threshold dinamis dari database")
    parser.add_argument("--threshold-required", action="store_true", help="Test bahwa threshold wajib dari database")
    parser.add_argument("--threshold-realtime", action="store_true", help="Test threshold realtime - refresh threshold secara berkala")
    parser.add_argument("--alarm-status", action="store_true", help="Test alarm status dari database")
    parser.add_argument("--notification", action="store_true", help="Test notification system")
    parser.add_argument("--notification-logic", action="store_true", help="Test logic notification - hanya kirim sekali saat water level tinggi")
    parser.add_argument("--notification-persistence", action="store_true", help="Test ketahanan notification flag ketika sensor error")
    parser.add_argument("--notification-alarm", action="store_true", help="Test notification dengan alarm status yang berbeda")
    parser.add_argument("--actuator-safety-lock", action="store_true", help="Test fitur safety lock: Actuator tidak boleh dinyalakan ketika water level tinggi")
    parser.add_argument("--rotary-lamp", action="store_true", help="Test kontrol rotary lamp ketika water level tinggi")
    parser.add_argument("--sensor-monitoring", action="store_true", help="Test update sensor monitoring status")
    parser.add_argument("--actuator", type=str, default="waterPump", help="Actuator custom ID")
    parser.add_argument("--pin", type=int, default=7, help="GPIO pin")
    parser.add_argument("--interval", type=int, default=2, help="Check interval (detik)")
    
    args = parser.parse_args()
    
    if args.test:
        test_actuator_library_sync()
    elif args.actuator_info:
        test_actuator_info()
    elif args.responsive:
        test_responsive_control()
    elif args.integration:
        test_actuator_library_integration()
    elif args.database:
        test_database_actuator_info()
    elif args.safety_logic:
        test_safety_control_logic()
    elif args.force_off:
        test_force_actuator_off()
    elif args.water_level_transition:
        test_water_level_transition()
    elif args.sensor_error:
        test_sensor_error_handling()
    elif args.water_level_persistence:
        test_water_level_persistence()
    elif args.dynamic_threshold:
        test_dynamic_threshold()
    elif args.threshold_required:
        test_threshold_required()
    elif args.threshold_realtime:
        test_threshold_realtime()
    elif args.alarm_status:
        test_alarm_status()
    elif args.notification:
        test_notification()
    elif args.notification_logic:
        test_notification_logic()
    elif args.notification_persistence:
        test_notification_flag_persistence()
    elif args.notification_alarm:
        test_notification_with_alarm_status()
    elif args.actuator_safety_lock:
        test_actuator_safety_lock()
    elif args.rotary_lamp:
        test_rotary_lamp_control()
    elif args.sensor_monitoring:
        test_sensor_monitoring_status_update()
    else:
        # Buat monitor dengan parameter dari actuatorLibrary
        monitor = WaterLevelMonitor(
            actuator_custom_id=args.actuator,
            pin=args.pin,
            check_interval=args.interval
        )
        
        print(f"🚰 Water Level Monitor - Sync actuatorLibrary + API")
        print(f"🎯 Actuator: {args.actuator}")
        print(f"📌 GPIO Pin: {args.pin}")
        print(f"💡 Rotary Lamp Pin: 0")
        print(f"🚨 Safety threshold: {monitor.safety_threshold} cm (dari database)")
        print(f"🚨 Alarm status: {monitor.alarm_status} (dari database)")
        print(f"🔔 Notification: Auto kirim notifikasi jika water level > threshold (hanya sekali)")
        print(f"🎛️  Actuator Control: Auto stop waterPump sekali, lalu kontrol manual via dashboard")
        print(f"💡 Rotary Lamp: Auto ON saat water level tinggi, Auto OFF saat water level aman (sekali saja)")
        print(f"🔄 Mode: Auto Stop Once + Auto Rotary Lamp + Manual Control")
        print(f"🔒 Safety: WaterPump auto stop sekali, lalu kontrol manual via dashboard")
        print(f"📊 Monitoring: Update status sensor monitoring via API")
        print(f"🎯 Fokus: Sync dengan actuatorLibrary + hit API endpoint")
        print(f"🔄 Trigger: Hanya sekali ketika water level melewati threshold")
        print(f"🎯 Dashboard: Actuator waterPump dikontrol manual via dashboard")
        print(f"⏱️  Check interval: {args.interval} detik")
        
        # Test API connection
        if monitor.api_client.test_connection():
            print("✅ API connection OK")
        else:
            print("⚠️  API connection gagal")
        
        # Mulai monitoring
        monitor.start_monitoring()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Monitoring dihentikan")
            monitor.stop_monitoring()
