# Water Level Monitor - Responsive Control System

## 🚀 Fitur Utama

### **Complete Water Level Monitoring System**
- **Self-Contained**: Semua water level monitoring ditangani oleh `water_level_monitor.py`
- **No External Dependencies**: Tidak bergantung pada `actuatorLibrary.py` untuk water level
- **Direct Sensor Access**: Akses langsung ke sensor water level via minimalmodbus
- **Database Integration**: Mengambil threshold dari kolom `max` di sensorListDB
- **Alarm Status Control**: Mengambil status alarm dari kolom `alarm` dan `conditions` di sensorListDB
- **Realtime Update**: Refresh threshold dan alarm status secara berkala (setiap 2 detik)
- **Cache System**: Menggunakan cache untuk mengurangi beban database
- **Change Detection**: Mendeteksi perubahan threshold dan alarm status
- **Type Conversion**: Otomatis konversi threshold dari string ke integer
- **No Default Threshold**: Sistem wajib menggunakan database (tidak ada fallback)

**Fitur Alarm Status:**
- **Manual Control**: Jika alarm INACTIVE, actuator bisa dioperasikan manual dari dashboard
- **Auto Control**: Jika alarm ACTIVE, actuator dikontrol otomatis berdasarkan water level
- **Real-time Status**: Alarm status diupdate setiap 2 detik dari database
- **Smart Logic**: Sistem hanya melakukan kontrol otomatis jika alarm ACTIVE

**Fitur Notification System:**
- **Alarm-Based Notification**: Notifikasi hanya dikirim jika alarm ACTIVE
- **Smart Notification**: Kirim notifikasi hanya sekali saat water level pertama kali tinggi
- **Auto Reset**: Reset notification flag ketika water level kembali normal atau alarm INACTIVE
- **Multi-channel**: Notifikasi dikirim ke WA, Telegram, Web, dan Email
- **Persistent Flag**: Notification flag tidak reset ketika sensor error
- **Real-time Alert**: Notifikasi dikirim segera saat water level > threshold dan alarm ACTIVE

### **Actuator Control System**
- Cek status actuator dari database lokal (prioritas) atau API (fallback)
- **Interpretasi Status yang Benar**: 1 = ON, 0 = OFF
- Auto matikan actuator jika water level tinggi tapi actuator ON
- **Force Sync**: Selalu sinkronkan dengan server ketika water level tinggi

## 🔧 Komponen yang Ditambahkan

### 1. Method `get_actuator_info()` di WaterLevelMonitor
```python
def get_actuator_info(self, force_refresh=False):
    """
    Dapatkan informasi actuator dari database lokal (menggunakan actuatorLibrary)
    Returns: dict dengan informasi actuator atau None jika gagal
    """
```

**Fitur:**
- **Prioritas Database Lokal**: Menggunakan `ActuatorListDB.selectByActId()` dari actuatorLibrary
- **Fallback API**: Jika database tidak tersedia, gunakan API sebagai fallback
- Cache informasi actuator selama 30 detik
- Force refresh untuk mendapatkan data terbaru
- Auto login jika token expired

**Data yang Didapat:**
- Nama actuator
- ID actuator
- Status actuator (state)
- Last action value (status terakhir) - **1 = ON, 0 = OFF**
- Server value (nilai dari server)
- Updated timestamp

### 2. Method `check_and_control_actuator()` di WaterLevelMonitor
```python
def check_and_control_actuator(self, water_level):
    """
    Cek status actuator dan kontrol berdasarkan water level
    Menggunakan function safety check dari actuatorLibrary
    """
```

**Fitur:**
- Menggunakan `check_water_level_safety()` dari actuatorLibrary
- Cek status actuator dari database lokal (prioritas) atau API (fallback)
- **Interpretasi Status yang Benar**: 1 = ON, 0 = OFF
- Auto matikan actuator jika water level tinggi tapi actuator ON
- **Force Sync**: Selalu sinkronkan dengan server ketika water level tinggi
- **Water Level Tracking**: Track perubahan water level untuk monitoring
- Kontrol via GPIO dan API secara bersamaan

**Logic Safety Control:**
1. **Water Level Tinggi + Actuator ON**: Matikan actuator via GPIO + API
2. **Water Level Tinggi + Actuator OFF**: Pastikan sinkronisasi dengan server (force OFF)
3. **Water Level Aman**: Biarkan actuator dioperasikan manual

**Logic Water Level Tracking:**
1. **Water Level Valid**: Update tracking
2. **Sensor Error**: Tracking tidak diubah (untuk keamanan)
3. **Water Level Aman**: Update tracking untuk monitoring

### 3. Water Level Tracking System
```python
# Flag untuk tracking water level
self.last_water_level = None
self.safety_threshold = 10
```

**Fitur:**
- **State Tracking**: Track perubahan water level
- **Error Handling**: Tracking tidak diubah ketika sensor error
- **Manual Reset**: Method `reset_water_level_tracking()` untuk testing

### 4. Sensor Error Handling
```python
# Cek apakah water level valid (tidak None)
if water_level is None:
    print("⚠️  Water level tidak terbaca - tidak mengubah tracking")
    print("🔒 Water level tracking tetap: tidak di-reset untuk keamanan")
    return
```

**Fitur:**
- **Safety First**: Tracking tidak diubah ketika sensor error
- **Error Persistence**: Mencegah reset tracking yang tidak aman
- **Clear Logging**: Feedback yang jelas tentang status sensor
- **Graceful Handling**: Sistem tetap berjalan meskipun sensor error

### 5. Integration dengan actuatorLibrary

**Function yang Digunakan:**
- `ActuatorListDB.selectByActId()`: Get actuator info dari database
- `check_water_level_safety()`: Safety check water level
- `read_water_level_safety()`: Baca water level dari sensor

**Keunggulan Integration:**
- Konsistensi dengan sistem yang sudah ada
- Menggunakan logic safety yang sudah teruji
- Data real-time dari database lokal
- Fallback ke API jika database tidak tersedia
- **Interpretasi status yang akurat**
- **Water level tracking system**

### **Dynamic Safety Threshold (Realtime)**
- **Database Integration**: Mengambil threshold dari kolom `max` di sensorListDB
- **Realtime Update**: Refresh threshold secara berkala (setiap 2 detik)
- **Cache System**: Menggunakan cache untuk mengurangi beban database
- **Change Detection**: Mendeteksi perubahan threshold dan memberikan notifikasi
- **Type Conversion**: Otomatis konversi threshold dari string ke integer
- **No Default Threshold**: Sistem wajib menggunakan database (tidak ada fallback)

**Fitur Threshold Realtime:**
- **Auto Refresh**: Threshold diupdate setiap 2 detik dalam monitoring loop
- **Cache Duration**: 2 detik untuk mengurangi beban database
- **Change Notification**: Memberitahu ketika threshold berubah
- **Force Refresh**: Opsi untuk force refresh threshold jika diperlukan
- **Simplified Messages**: Pesan yang lebih sederhana tanpa "SAFETY CHECK FAILED"

## 🚀 Cara Penggunaan

### 1. Test Database Integration
```bash
# Test mendapatkan info actuator dari database lokal
python water_level_monitor.py --database

# Test integrasi lengkap dengan actuatorLibrary
python water_level_monitor.py --integration

# Test logic safety control yang sudah diperbaiki
python water_level_monitor.py --safety-logic

# Test memaksa actuator OFF ketika water level tinggi
python water_level_monitor.py --force-off

# Test transisi water level dari aman ke tidak aman
python water_level_monitor.py --water-level-transition

# Test handling ketika sensor water level tidak terbaca
python water_level_monitor.py --sensor-error

# Test ketahanan water level tracking ketika sensor error
python water_level_monitor.py --water-level-persistence
```

### 2. Test Responsive Control
```bash
# Test responsive control (cek dan kontrol actuator)
python water_level_monitor.py --responsive
```

### 3. Monitoring Responsive Mode
```bash
# Jalankan monitoring dengan mode responsive
python water_level_monitor.py --actuator waterPump --pin 7 --interval 5
```

## 🔄 Alur Kerja Responsive System

1. **Monitoring Loop** berjalan setiap interval (default: 5 detik)
2. **Baca Water Level** menggunakan `actuatorLibrary.read_water_level_safety()`
3. **Get Actuator Info** dari database lokal (prioritas) atau API (fallback)
4. **Safety Check** menggunakan `actuatorLibrary.check_water_level_safety()`
5. **Check Safety Condition:**
   - Jika safety check FAILED DAN actuator ON → **MATIKAN OTOMATIS**
   - Jika safety check FAILED DAN actuator OFF → **FORCE SYNC dengan server**
   - Jika safety check PASSED → **Biarkan actuator dioperasikan manual**
6. **Water Level Tracking:**
   - Jika water level valid → **UPDATE TRACKING**
   - Jika sensor error → **TRACKING TIDAK DIUBAH (untuk keamanan)**
7. **Control Actions:**
   - Matikan via GPIO pin (jika actuator ON)
   - Update status via API (selalu sinkronkan)
   - Refresh cache actuator info

## 🛡️ Safety Features

### Auto Safety Shutdown
- **Trigger:** Safety check dari actuatorLibrary gagal
- **Action:** Matikan actuator otomatis
- **Control:** GPIO + API secara bersamaan
- **Force Sync:** Selalu sinkronkan dengan server ketika water level tinggi

### Responsive Dashboard Control
- **Manual ON:** User bisa nyalakan actuator dari dashboard
- **Auto OFF:** Sistem otomatis matikan jika water level tinggi
- **Force Sync:** Pastikan dashboard tidak bisa mengaktifkan actuator ketika tidak aman
- **Real-time Sync:** Status actuator selalu sinkron antara dashboard dan sistem

## 📊 Monitoring Output

```
🚰 Water Level Monitor - Sync actuatorLibrary + API
🎯 Actuator: waterPump
📌 GPIO Pin: 7
⏱️  Check interval: 5 detik
🔄 Responsive: Auto matikan actuator jika water level > 10 cm

📊 Water level: 13.0 cm
🔍 Mengambil informasi actuator dari database lokal...
✅ Info actuator berhasil diambil dari database lokal:
   📝 Nama: Water Pump
   🆔 ID: PAL-083J2
   💡 Status: 1
   🔧 Last Action Value: 1
   🌐 Server Value: 1
   ⏰ Updated: 2025-08-12 13:51:51.861670
🔍 Status actuator (DB): 1 (ON: True)  # Interpretasi yang benar
🔍 Menggunakan safety check dari actuatorLibrary...
🚨 SAFETY ALERT: Water level 13.0 cm ≥ 10 cm
🔴 Pompa waterPump akan dimatikan untuk keamanan
🚨 SAFETY CHECK FAILED: Water level 13.0 cm tidak aman
🔴 Actuator sedang ON tapi water level tinggi - MATIKAN OTOMATIS!
✅ Actuator dimatikan via GPIO pin 7
🔗 Matikan actuator via API...
✅ API berhasil - actuator dimatikan di server

# Monitoring loop berikutnya (water level tetap tinggi)
📊 Water level: 13.5 cm
🔍 Status actuator (DB): 0 (ON: False)
🚨 SAFETY CHECK FAILED: Water level 13.5 cm tidak aman
✅ Actuator sudah OFF - memastikan sinkronisasi dengan server...
🔗 Memastikan actuator tetap OFF di server...
✅ API berhasil - actuator dipastikan OFF di server

# Sensor error (tidak terbaca)
⚠️  Water level tidak terbaca - tidak mengubah tracking
🔒 Water level tracking tetap: tidak di-reset untuk keamanan

# Water level kembali aman
📊 Water level: 8.0 cm
✅ Safety check passed: Water level 8.0 cm aman
💡 Actuator bisa dioperasikan manual dari dashboard
```

## 🔧 Konfigurasi

### Parameter yang Bisa Dikustomisasi:
- `actuator_custom_id`: ID actuator di database (default: "waterPump")
- `pin`: GPIO pin untuk kontrol (default: 7)
- `check_interval`: Interval monitoring dalam detik (default: 5)
- `safety_threshold`: Batas aman water level dalam cm (default: 10)
- `actuator_cache_duration`: Durasi cache info actuator dalam detik (default: 30)

### Database Configuration:
- **Database:** MySQL/PostgreSQL sesuai konfigurasi actuatorLibrary
- **Table:** `actuatorListDB` untuk data actuator
- **Connection:** Menggunakan konfigurasi dari `dbNearonProject.json`
- **Status Mapping:** 1 = ON, 0 = OFF

## 🧪 Testing

### Test Functions yang Tersedia:
1. `test_database_actuator_info()`: Test get actuator info dari database lokal
2. `test_actuator_library_integration()`: Test integrasi lengkap dengan actuatorLibrary
3. `test_safety_control_logic()`: Test logic safety control yang sudah diperbaiki
4. `test_force_actuator_off()`: Test memaksa actuator OFF ketika water level tinggi
5. `