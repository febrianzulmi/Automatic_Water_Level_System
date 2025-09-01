#!/usr/bin/env python3
"""
Script testing untuk Synapsis API Client
"""

import sys
import time

# Tambahkan path untuk import
sys.path.append('/home/connex/project/actuator')
from synapsis_api_client import SynapsisAPIClient, get_water_level_from_actuator_library, test_api_client

def test_login():
    """Test login API"""
    print("🧪 Testing login API...")
    
    client = SynapsisAPIClient()
    result = client.login()
    
    if result:
        print("✅ Login test berhasil")
        return True
    else:
        print("❌ Login test gagal")
        return False

def test_update_actuator():
    """Test update actuator"""
    print("🧪 Testing update actuator...")
    
    client = SynapsisAPIClient()
    
    # Login terlebih dahulu
    if not client.login():
        print("❌ Gagal login, tidak bisa test update actuator")
        return False
    
    # Test update ke false
    print("🔧 Test 1: Set actuator ke FALSE")
    result1 = client.update_water_pump_actuator(False)
    
    time.sleep(3)
    
    # Test update ke true
    print("🔧 Test 2: Set actuator ke TRUE")
    result2 = client.update_water_pump_actuator(True)
    
    if result1 and result2:
        print("✅ Update actuator test berhasil")
        return True
    else:
        print("❌ Update actuator test gagal")
        return False

def test_water_level_reading():
    """Test pembacaan water level"""
    print("🧪 Testing pembacaan water level...")
    
    water_level = get_water_level_from_actuator_library()
    
    if water_level is not None:
        print(f"✅ Water level berhasil dibaca: {water_level:.1f} cm")
        return True
    else:
        print("❌ Gagal membaca water level")
        return False

def test_safety_trigger_logic():
    """Test logika safety trigger berdasarkan level"""
    print("🧪 Testing logika safety trigger berdasarkan level...")
    
    client = SynapsisAPIClient()
    
    # Login terlebih dahulu
    if not client.login():
        print("❌ Gagal login, tidak bisa test safety trigger logic")
        return False
    
    # Test berbagai level air untuk safety threshold
    test_levels = [5, 8, 10, 12, 15]
    safety_threshold = 10
    
    for level in test_levels:
        print(f"\n📊 Testing level air: {level} cm (Safety threshold: {safety_threshold} cm)")
        result = client.trigger_safety_shutdown(level, safety_threshold)
        
        if result:
            if level >= safety_threshold:
                print(f"✅ Safety trigger berhasil untuk level {level} cm (≥ {safety_threshold} cm)")
            else:
                print(f"✅ Water level aman untuk level {level} cm (< {safety_threshold} cm)")
        else:
            print(f"❌ Safety trigger gagal untuk level {level} cm")
        
        time.sleep(2)  # Delay antara test
    
    return True

def test_manual_control():
    """Test kontrol manual"""
    print("🧪 Testing kontrol manual...")
    
    client = SynapsisAPIClient()
    
    # Login terlebih dahulu
    if not client.login():
        print("❌ Gagal login, tidak bisa test kontrol manual")
        return False
    
    print("🔧 Test 1: Matikan pompa (FALSE)")
    result1 = client.update_water_pump_actuator(False)
    
    time.sleep(3)
    
    print("🔧 Test 2: Nyalakan pompa (TRUE)")
    result2 = client.update_water_pump_actuator(True)
    
    if result1 and result2:
        print("✅ Kontrol manual test berhasil")
        return True
    else:
        print("❌ Kontrol manual test gagal")
        return False


def test_notification():
    """Test notification untuk semua tipe"""
    print("🧪 Testing notification untuk semua tipe...")
    
    client = SynapsisAPIClient()
    
    # Login terlebih dahulu
    if not client.login():
        print("❌ Gagal login, tidak bisa test notification")
        return False
    
    # Test notification dengan water level 12 cm (120% dari threshold)
    test_water_level = 12
    safety_threshold = 10
    
    print(f"📊 Test notification untuk water level: {test_water_level} cm")
    print(f"📊 Safety threshold: {safety_threshold} cm")
    
    # Kirim notification
    result = client.send_water_level_notifications(test_water_level, safety_threshold)
    
    if result:
        print("✅ Test notification berhasil")
        return True
    else:
        print("❌ Test notification gagal")
        return False

def show_current_status():
    """Tampilkan status saat ini"""
    print("📊 Status saat ini...")
    
    # Water level
    water_level = get_water_level_from_actuator_library()
    if water_level is not None:
        print(f"💧 Water level: {water_level:.1f} cm")
        
        # Analisis safety threshold
        safety_threshold = 10
        if water_level >= safety_threshold:
            print(f"🚨 Level: SAFETY THRESHOLD ({water_level:.1f} cm ≥ {safety_threshold} cm)")
            print("🔴 Pompa harus MATI via API endpoint")
        else:
            print(f"✅ Level: AMAN ({water_level:.1f} cm < {safety_threshold} cm)")
    else:
        print("⚠️  Water level: Tidak dapat dibaca")
    
    # Test API connection
    print("\n🔍 Testing API connection...")
    client = SynapsisAPIClient()
    if client.test_connection():
        print("✅ API connection: OK")
    else:
        print("❌ API connection: GAGAL")

def main():
    """Menu utama testing"""
    print("🚰 Testing Synapsis API Client - Safety Trigger + Notification")
    print("=" * 50)
    print("1. Test login API")
    print("2. Test update actuator")
    print("3. Test pembacaan water level")
    print("4. Test safety trigger logic")
    print("5. Test kontrol manual")
    print("6. Test notification (WA, Telegram, Web, Email)")
    print("7. Tampilkan status saat ini")
    print("8. Test API connection lengkap")
    print("9. Keluar")
    print("=" * 50)
    
    while True:
        try:
            choice = input("Pilih menu (1-8): ").strip()
            
            if choice == "1":
                test_login()
            elif choice == "2":
                test_update_actuator()
            elif choice == "3":
                test_water_level_reading()
            elif choice == "4":
                test_safety_trigger_logic()
            elif choice == "5":
                test_manual_control()
            elif choice == "6":
                test_notification()
            elif choice == "7":
                show_current_status()
            elif choice == "8":
                print("🧪 Testing API connection lengkap...")
                test_api_client()
            elif choice == "9":
                print("👋 Keluar dari testing")
                break
            else:
                print("❌ Pilihan tidak valid")
                
        except KeyboardInterrupt:
            print("\n👋 Keluar dari testing")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
