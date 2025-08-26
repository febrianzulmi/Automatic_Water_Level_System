# 🚰 Water Level Safety - Integrasi ke ActuatorLibrary

Fitur safety water level telah diintegrasikan langsung ke `actuatorLibrary.py` untuk mematikan pompa otomatis saat level air mencapai 10 cm.

## 🎯 Fitur yang Ditambahkan

### **1. Safety Check Saat Aktivasi Pompa**
- **Fungsi:** `check_water_level_safety(actuator_custom_id)`
- **Cara Kerja:** Cek water level sebelum mengaktifkan pompa
- **Hasil:** Jika level ≥ 10 cm, pompa tidak akan diaktifkan

### **2. Monitoring Kontinyu**
- **Fungsi:** `start_water_level_monitoring(actuator_custom_id, pin)`
- **Cara Kerja:** Monitor water level setiap 5 detik saat pompa aktif
- **Hasil:** Matikan pompa otomatis jika level ≥ 10 cm

### **3. Baca Water Level Sensor**
- **Fungsi:** `read_water_level_safety()`
- **Cara Kerja:** Baca sensor RS485 register 4
- **Hasil:** Return water level dalam cm

## 🔧 Cara Kerja

### **Flow Safety System:**

1. **User mengaktifkan pompa** via dashboard
2. **ActuatorLibrary dipanggil** dengan value = 1
3. **Safety check dijalankan** sebelum aktivasi
4. **Jika level < 10 cm:**
   - Pompa diaktifkan
   - Monitoring kontinyu dimulai
5. **Jika level ≥ 10 cm:**
   - Pompa tidak diaktifkan
   - Emergency shutdown message

### **Monitoring Kontinyu:**

1. **Thread terpisah** untuk monitoring
2. **Cek water level** setiap 5 detik
3. **Jika level ≥ 10 cm:**
   - Matikan pompa via GPIO
   - Stop monitoring thread
4. **Jika level < 10 cm:**
   - Lanjutkan monitoring

## 📊 Output Log

### **Saat Pompa Diaktifkan:**
```
✅ Water level aman: 5.2 cm < 10 cm
🔄 Monitoring thread started untuk waterPump
Success Run 1 of 1 Actuator from 1 Actuator
```

### **Saat Water Level Tinggi:**
```
🚨 SAFETY ALERT: Water level 12.5 cm ≥ 10 cm
🔴 Pompa waterPump akan dimatikan untuk keamanan
🚨 EMERGENCY SHUTDOWN: Pompa waterPump dimatikan paksa
Emergency Shutdown - Water Level High
```

### **Saat Monitoring Kontinyu:**
```
🚰 Memulai monitoring water level untuk waterPump
✅ Water level aman: 7.8 cm
✅ Water level aman: 8.2 cm
🚨 SAFETY TRIGGER: Water level 10.1 cm ≥ 10 cm
🔴 Matikan pompa waterPump via GPIO pin 0
✅ Pompa waterPump berhasil dimatikan untuk keamanan
```

## ⚙️ Konfigurasi

### **Konfigurasi Sensor (dalam fungsi `read_water_level_safety()`):**
```python
SERIAL_PORT = '/dev/ttyUSB0'    # Port sensor RS485
DEVICE_ID = 1                   # ID device Modbus
BAUD_RATE = 9600                # Baud rate
WATER_LEVEL_UNIT = 'cm'         # Unit sensor
```

### **Safety Threshold:**
```python
SAFETY_THRESHOLD = 10  # cm - Level untuk safety OFF
```

### **Monitoring Interval:**
```python
time.sleep(5)  # Cek setiap 5 detik
```

## 🎯 Deteksi Pompa

Sistem akan mendeteksi pompa berdasarkan nama actuator:
- **Kata kunci:** `"water"` atau `"pump"` dalam `actuator_custom_id`
- **Contoh:** `waterPump`, `pump1`, `water_pump`, dll.

## 🛡️ Keamanan

### **Multiple Safety Layer:**
1. **Pre-activation check** - Cek sebelum aktifkan
2. **Continuous monitoring** - Monitor saat aktif
3. **Emergency shutdown** - Matikan langsung via GPIO
4. **Thread safety** - Monitoring dalam thread terpisah

### **Error Handling:**
- **Sensor error** - Biarkan pompa berjalan
- **GPIO error** - Log error dan lanjutkan
- **Timeout** - Retry otomatis

## 📝 Penggunaan

### **Otomatis Terintegrasi:**
- Tidak perlu modifikasi kode lain
- Safety check otomatis saat pompa diaktifkan
- Monitoring kontinyu otomatis

### **Log Output:**
- Semua aktivitas safety tercatat di log
- Pesan error dan warning jelas
- Status monitoring real-time

## ⚠️ Troubleshooting

### **Sensor Tidak Terdeteksi:**
```
⚠️  Water level safety check error: [Errno 2] No such file or directory: '/dev/ttyUSB0'
```
**Solusi:** Cek port serial dan koneksi sensor

### **GPIO Error:**
```
❌ Error monitoring water level: GPIO error
```
**Solusi:** Cek koneksi GPIO dan permission

### **Monitoring Tidak Start:**
```
🔄 Monitoring thread started untuk waterPump
```
**Solusi:** Cek apakah nama actuator mengandung "water" atau "pump"

---

**🎯 Sistem safety water level siap digunakan!**
