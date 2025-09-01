#!/usr/bin/env python3
"""
Client API untuk login dan hit endpoint Synapsis
Berdasarkan curl yang diberikan
"""

import requests
import json
import time
import sys
import os

# Tambahkan path untuk import
sys.path.append('/home/connex/library')
from SynapsisLibrary import times

class SynapsisAPIClient:
    def __init__(self):
        # Konfigurasi API
        self.LOGIN_URL = "https://dev-api-nearon.synapsis.id/v1/auth/login/connex"
        self.ACTUATOR_URL = "https://dev-nearon.synapsis.id/api/projectnode/nodes/b949aecbf0f34bb48b94a7be960b78ce/actuators/5a6bc3a3efdc427ab9df7bfb3c82092e/value"
        
        # Node ID yang valid (sama dengan actuator)
        self.NODE_ID = "b949aecbf0f34bb48b94a7be960b78ce"
        
        # Credentials
        self.firmware_user = "synapsis"
        self.firmware_password = "password"
        
        # Session
        self.token = None
        self.session = requests.Session()
        
        print("🚰 Synapsis API Client initialized")
    
    def is_logged_in(self):
        """
        Cek apakah sudah login (token ada)
        """
        return self.token is not None
    
    def get_actuator_info(self, actuator_custom_id="connex"):
        """
        Dapatkan informasi actuator dari API
        Endpoint: https://dev-api-nearon.synapsis.id/v1/projectnode/nodes/{node_id}/actuators/{actuator_custom_id}
        """
        try:
            # Pastikan sudah login
            if self.token is None:
                print("🔐 Token tidak ada, melakukan login...")
                if not self.login():
                    return None
            
            # URL untuk mendapatkan info actuator
            actuator_info_url = f"https://dev-api-nearon.synapsis.id/v1/projectnode/nodes/{self.NODE_ID}/actuators/{actuator_custom_id}"
            
            # Headers untuk request
            headers = {
                'Cookie': f'token={self.token}'
            }
            
            print(f"🔍 Get actuator info: {actuator_info_url}")
            print(f"🎯 Actuator ID: {actuator_custom_id}")
            
            # Kirim request GET
            response = self.session.get(
                actuator_info_url,
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Berhasil mendapatkan info actuator")
                print(f"📄 Response: {response_data}")
                return response_data
            else:
                print(f"❌ Gagal mendapatkan info actuator - Status: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
                # Jika token expired, coba login ulang
                if response.status_code == 401:
                    print("🔄 Token expired, mencoba login ulang...")
                    self.token = None
                    if self.login():
                        return self.get_actuator_info(actuator_custom_id)
                
                return None
                
        except Exception as e:
            print(f"❌ Error get actuator info: {e}")
            return None
    
    def login(self):
        """
        Login ke API Synapsis berdasarkan curl yang diberikan
        """
        try:
            # Headers sesuai curl
            headers = {
                'Content-Type': 'application/json'
            }
            
            # Data payload sesuai curl
            data = {
                "firmware_user": self.firmware_user,
                "firmware_password": self.firmware_password
            }
            
            print(f"🔐 Login ke: {self.LOGIN_URL}")
            print(f"👤 User: {self.firmware_user}")
            
            # Kirim request login
            response = self.session.post(
                self.LOGIN_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse response
                response_data = response.json()
                print("✅ Login berhasil")
                print(f"📄 Response: {response_data}")
                
                # Simpan token dari cookies
                if 'token' in self.session.cookies:
                    self.token = self.session.cookies['token']
                    print(f"🔑 Token: {self.token}")
                else:
                    print("⚠️  Token tidak ditemukan di cookies")
                
                return True
            else:
                print(f"❌ Login gagal - Status: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error login: {e}")
            return False
    
    def update_water_pump_actuator(self, value):
        """
        Update status actuator water pump via API
        """
        try:
            # Pastikan sudah login
            if self.token is None:
                print("🔐 Token tidak ada, melakukan login...")
                if not self.login():
                    return False
            
            # Headers untuk actuator update
            headers = {
                'Content-Type': 'application/json',
                'Cookie': f'token={self.token}'
            }
            
            # Payload untuk update actuator
            data = {"value": str(value).lower()}
            
            print(f"🚰 Update actuator: {self.ACTUATOR_URL}")
            print(f"📦 Payload: {data}")
            
            # Kirim request PUT
            response = self.session.put(
                self.ACTUATOR_URL,
                headers=headers,
                json=data,
                timeout=10
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ API update berhasil - Water pump actuator: {value}")
                print(f"📄 Response: {response.text}")
                return True
            else:
                print(f"❌ API update gagal - Status: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
                # Jika token expired, coba login ulang
                if response.status_code == 401:
                    print("🔄 Token expired, mencoba login ulang...")
                    self.token = None
                    if self.login():
                        return self.update_water_pump_actuator(value)
                
                return False
                
        except Exception as e:
            print(f"❌ Error update actuator: {e}")
            return False
    
    def send_notification(self, subject, message, level=1, notification_type="web", node_id=None):
        """
        Kirim notification via API Synapsis
        """
        try:
            # Pastikan sudah login
            if self.token is None:
                print("🔐 Token tidak ada, melakukan login...")
                if not self.login():
                    return False
            
            # Gunakan node_id default jika tidak diberikan
            if node_id is None:
                node_id = self.NODE_ID
            
            # Notification URL
            notification_url = "https://dev-nearon.synapsis.id/api/notification/send"
            
            # Headers untuk notification
            headers = {
                'Cookie': f'token={self.token}'
            }
            
            # Query parameters
            params = {
                'subject': subject,
                'message': message,
                'level': level,
                'type': notification_type,
                'node_id': node_id
            }
            
            print(f"📢 Kirim notification: {notification_url}")
            print(f"📦 Type: {notification_type}")
            print(f"📋 Subject: {subject}")
            print(f"💬 Message: {message}")
            print(f"🆔 Node ID: {node_id}")
            print(f"📊 Level: {level}")
            
            # Kirim request POST
            response = self.session.post(
                notification_url,
                headers=headers,
                params=params,
                timeout=10
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"✅ Notification berhasil dikirim via {notification_type}")
                print(f"📄 Response: {response.text}")
                return True
            else:
                print(f"❌ Notification gagal - Status: {response.status_code}")
                print(f"❌ Response: {response.text}")
                
                # Jika token expired, coba login ulang
                if response.status_code == 401:
                    print("🔄 Token expired, mencoba login ulang...")
                    self.token = None
                    if self.login():
                        return self.send_notification(subject, message, level, notification_type, node_id)
                
                return False
                
        except Exception as e:
            print(f"❌ Error send notification: {e}")
            return False
    
    def send_water_level_notifications(self, water_level, safety_threshold=10):
        """
        Kirim notification untuk semua tipe ketika water level critical
        """
        try:
            # Hitung persentase water level
            # percentage = (water_level / safety_threshold) * 100
            
            # Subject dan message
            subject = "🚨 Water Level Critical: Hampir Melebihi Batas Aman"
            message = f"Ketinggian air telah mencapai 85% dari kapasitas. Segera lakukan tindakan pencegahan untuk menghindari kemungkinan bahaya lain"
            
            # Node ID (gunakan yang sama dengan actuator)
            node_id = self.NODE_ID
            
            # Kirim notification untuk semua tipe
            notification_types = ["wa", "telegram", "web", "email"]
            success_count = 0
            
            print(f"📢 Kirim notification untuk water level {water_level:.1f} cm")
            
            for notification_type in notification_types:
                print(f"\n📱 Kirim ke {notification_type.upper()}...")
                if self.send_notification(subject, message, level=1, notification_type=notification_type, node_id=node_id):
                    success_count += 1
                else:
                    print(f"⚠️  Gagal kirim ke {notification_type}")
                
                time.sleep(1)  # Delay antar notification
            
            print(f"\n📊 Summary: {success_count}/{len(notification_types)} notification berhasil dikirim")
            return success_count > 0
            
        except Exception as e:
            print(f"❌ Error send water level notifications: {e}")
            return False
    
    def trigger_safety_shutdown(self, water_level, safety_threshold=10):
        """
        Trigger safety shutdown untuk matikan actuator saat water level mencapai safety threshold
        """
        try:
            if water_level >= safety_threshold:
                # Safety threshold tercapai - matikan pompa
                print(f"🚨 SAFETY TRIGGER: Water level {water_level} cm ≥ {safety_threshold} cm")
                print("🔴 Matikan water pump actuator via API endpoint")
                return self.update_water_pump_actuator(False)
            else:
                # Water level aman
                print(f"✅ Water level aman: {water_level} cm < {safety_threshold} cm")
                return True
                
        except Exception as e:
            print(f"❌ Error safety trigger: {e}")
            return False
    
    def test_connection(self):
        """
        Test koneksi API
        """
        print("🧪 Testing koneksi API...")
        
        # Test login
        if not self.login():
            return False
        
        # Test update actuator dengan false
        result = self.update_water_pump_actuator(False)
        if result:
            print("✅ API connection test berhasil")
            return True
        else:
            print("❌ API connection test gagal")
            return False


def get_water_level_from_actuator_library():
    """
    Dapatkan water level dari actuatorLibrary
    """
    try:
        # Import fungsi dari actuatorLibrary
        sys.path.append('/home/connex/project/actuator')
        from actuatorLibrary import read_water_level_safety
        
        water_level = read_water_level_safety()
        
        if water_level is not None:
            print(f"📊 Water level dari actuatorLibrary: {water_level:.1f} cm")
            return water_level
        else:
            print("⚠️  Tidak bisa membaca water level dari actuatorLibrary")
            return None
            
    except Exception as e:
        print(f"❌ Error membaca water level: {e}")
        return None


def sync_safety_trigger(safety_threshold=10):
    """
    Sinkronisasi safety trigger dengan API actuator
    """
    try:
        # Buat client API
        client = SynapsisAPIClient()
        
        # Login
        if not client.login():
            print("❌ Gagal login, tidak bisa sinkronisasi safety trigger")
            return False
        
        # Dapatkan water level
        water_level = get_water_level_from_actuator_library()
        
        if water_level is not None:
            # Trigger safety shutdown berdasarkan level
            result = client.trigger_safety_shutdown(water_level, safety_threshold)
            return result
        else:
            print("❌ Tidak ada data water level untuk safety trigger")
            return False
            
    except Exception as e:
        print(f"❌ Error safety trigger sync: {e}")
        return False


def test_api_client():
    """
    Test API client
    """
    print("🧪 Testing Synapsis API Client...")
    
    client = SynapsisAPIClient()
    
    # Test login
    if client.login():
        print("✅ Login test berhasil")
        
        # Test update actuator
        if client.update_water_pump_actuator(False):
            print("✅ Update actuator test berhasil")
            
            # Test notification sederhana
            print("\n🧪 Testing notification...")
            if client.send_notification("Test", "Test message", level=1, notification_type="web"):
                print("✅ Notification test berhasil")
            else:
                print("❌ Notification test gagal")
            
            return True
        else:
            print("❌ Update actuator test gagal")
            return False
    else:
        print("❌ Login test gagal")
        return False


def test_notification_simple():
    """
    Test notification dengan parameter sederhana
    """
    print("🧪 Testing notification sederhana...")
    
    client = SynapsisAPIClient()
    
    if client.login():
        # Test dengan parameter minimal
        result = client.send_notification(
            subject="Test Notification",
            message="Ini adalah test notification",
            level=1,
            notification_type="web"
        )
        
        if result:
            print("✅ Notification sederhana berhasil")
            return True
        else:
            print("❌ Notification sederhana gagal")
            return False
    else:
        print("❌ Login gagal")
        return False


def test_get_actuator_info():
    """
    Test mendapatkan informasi actuator
    """
    print("🧪 Testing get actuator info...")
    
    client = SynapsisAPIClient()
    
    if client.login():
        # Test get actuator info
        actuator_info = client.get_actuator_info("connex")
        
        if actuator_info and actuator_info.get('status') and actuator_info.get('data'):
            print("✅ Get actuator info berhasil")
            data = actuator_info['data'][0]
            print(f"   📝 Nama: {data.get('name', 'N/A')}")
            print(f"   🆔 ID: {data.get('id', 'N/A')}")
            print(f"   💡 Status: {data.get('value', 'N/A')}")
            print(f"   ⏰ Updated: {data.get('updated_at', 'N/A')}")
            return True
        else:
            print("❌ Get actuator info gagal")
            return False
    else:
        print("❌ Login gagal")
        return False


if __name__ == "__main__":
    print("🚰 Synapsis API Client Test")
    print("=" * 50)
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Synapsis API Client Test")
    parser.add_argument("--actuator-info", action="store_true", help="Test get actuator info")
    
    args = parser.parse_args()
    
    if args.actuator_info:
        test_get_actuator_info()
    else:
        test_api_client()
