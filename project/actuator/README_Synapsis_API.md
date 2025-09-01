# 🚰 Synapsis API Client untuk Water Level Safety Monitoring

Sistem monitoring water level dengan fokus pada safety threshold dan hit API endpoint untuk matikan actuator saat water level mencapai titik safety.

## 📋 Fitur Utama

- ✅ **Login API**: Login ke Synapsis menggunakan credentials firmware
- ✅ **Session Management**: Mengelola session dan token otomatis
- ✅ **Safety Threshold**: Menggunakan threshold safety 10 cm dari actuatorLibrary
- ✅ **Conditional API Hit**: Hanya hit API endpoint ketika water level ≥ 10 cm
- ✅ **Multi-Platform Notification**: Kirim alert ke WA, Telegram, Web, Email
- ✅ **Real-time Monitoring**: Monitoring kontinyu dengan thread terpisah
- ✅ **Error Handling**: Penanganan error dan retry mechanism

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Water Level   │    │  Synapsis API   │    │   API Synapsis  │
│     Sensor      │───▶│     Client      │───▶│   (Actuator)    │
│ (actuatorLibrary)│    │  Safety Trigger │    │   (Shutdown)    │
│ Safety: 10cm    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 File yang Dibuat

```
project/actuator/
├── synapsis_api_client.py      # Client API untuk login dan hit endpoint
├── water_level_monitor.py      # Script monitoring water level
├── test_synapsis_api.py        # Script testing API client
└── README_Synapsis_API.md      # Dokumentasi ini
```

## 🔐 Login API

### Endpoint Login
```
URL: https://dev-api-nearon.synapsis.id/v1/auth/login/connex
Method: POST
Headers: Content-Type: application/json
```

### Payload Login
```json
{
  "firmware_user": "synapsis",
  "firmware_password": "password"
}
```

### Response Login
- **Success (200)**: Token disimpan di session cookies
- **Error**: Log error dan retry mechanism

## 🚰 Actuator API

### Endpoint Actuator
```
URL: https://dev-nearon.synapsis.id/api/projectnode/nodes/a917a64f76cb44c2944980aa31043c56/actuators/327d21b0742a49d5b8a359320ef73b66/value
Method: PUT
Headers: 
  - Content-Type: application/json
  - Cookie: token=<session_token>
```

### Payload Actuator
```json
{
  "value": "false"   // Matikan pompa
}
```
```json
{
  "value": "true"    // Nyalakan pompa
}
```

## 📢 Notification API

### Endpoint Notification
```
URL: https://dev-nearon.synapsis.id/api/notification/send
Method: POST
Headers: 
  - Cookie: token=<session_token>
```

### Query Parameters
```
subject=🚨 Water Level Critical: Hampir Melebihi Batas Aman
message=Ketinggian air telah mencapai 85% dari kapasitas. Segera lakukan tindakan pencegahan untuk menghindari kemungkinan bahaya lain
level=1
type=wa|telegram|web|email
node_id=8b08e66239364a61bc0aa16ceb8a927f
```

### Notification Types
- **WA**: WhatsApp notification
- **Telegram**: Telegram bot notification  
- **Web**: Web notification
- **Email**: Email notification

## 🚀 Cara Penggunaan

### 1. Test API Client
```bash
cd project/actuator
python3 test_synapsis_api.py
```

### 2. Jalankan Monitoring
```bash
# Monitoring dengan threshold default
python3 water_level_monitor.py

# Monitoring dengan parameter custom
python3 water_level_monitor.py --actuator "pump_1" --pin 8 --interval 3

# Test sinkronisasi sekali
python3 water_level_monitor.py --test

# Test notification untuk semua tipe
python3 water_level_monitor.py --notification
```

### 3. Test API Client Langsung
```bash
python3 synapsis_api_client.py
```

## 📊 Log Output

### Login Success
```
🔐 Login ke: https://dev-api-nearon.synapsis.id/v1/auth/login/connex
👤 User: synapsis
📊 Response Status: 200
✅ Login berhasil
📄 Response: {...}
🔑 Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Actuator Update
```
🚰 Update actuator: https://dev-nearon.synapsis.id/api/projectnode/nodes/...
📦 Payload: {'value': 'false'}
📊 Response Status: 200
✅ API update berhasil - Water pump actuator: false
📄 Response: {...}
```

### Monitoring Real-time dengan Notification
```
🚰 Water Level Monitor initialized
🎯 Actuator: water_pump
📌 GPIO Pin: 7
⏱️  Check interval: 5 detik

🔐 Login ke API Synapsis...
✅ Login berhasil

🔄 Memulai monitoring water level...
[2024-01-15 14:30:25] Level air: 5.2 cm
✅ Water level aman: 5.2 cm
💡 Tidak melakukan apa-apa terhadap actuator (tetap status sebelumnya)

[2024-01-15 14:30:30] Level air: 12.3 cm
🚨 SAFETY TRIGGER: Water level 12.3 cm ≥ 10 cm
🔴 Matikan pompa water_pump via GPIO pin 7
✅ Pompa water_pump berhasil dimatikan untuk keamanan
🔗 Hit API endpoint untuk matikan actuator di server...
✅ API hit berhasil - actuator dimatikan di server Synapsis
📢 Kirim notification alert...
📱 Kirim ke WA...
✅ Notification berhasil dikirim via wa
📱 Kirim ke TELEGRAM...
✅ Notification berhasil dikirim via telegram
📱 Kirim ke WEB...
✅ Notification berhasil dikirim via web
📱 Kirim ke EMAIL...
✅ Notification berhasil dikirim via email
📊 Summary: 4/4 notification berhasil dikirim
```

## 🧪 Testing

### Menu Testing (test_synapsis_api.py)
1. **Test login API** - Validasi login credentials
2. **Test update actuator** - Validasi update actuator
3. **Test pembacaan water level** - Validasi sensor
4. **Test logika trigger** - Validasi logika kontrol
5. **Test kontrol manual** - Validasi kontrol manual
6. **Tampilkan status saat ini** - Cek status real-time
7. **Test API connection lengkap** - Test sistem lengkap

### Contoh Test Manual
```python
from synapsis_api_client import SynapsisAPIClient

# Buat client
client = SynapsisAPIClient()

# Login
if client.login():
    # Update actuator
    client.update_water_pump_actuator(False)  # Matikan pompa
    client.update_water_pump_actuator(True)   # Nyalakan pompa
```

## ⚙️ Konfigurasi

### Threshold Default
- **Safety Threshold**: 10 cm (matikan pompa)
- **Check Interval**: 5 detik
- **Logic**: Hanya hit API ketika water level ≥ 10 cm

### Credentials
- **Username**: synapsis
- **Password**: password
- **Login URL**: https://dev-api-nearon.synapsis.id/v1/auth/login/connex

## 🔧 Parameter Command Line

### water_level_monitor.py
```bash
--test          # Test sinkronisasi sekali
--high 85       # High threshold (cm)
--low 15        # Low threshold (cm)
--interval 15   # Check interval (detik)
```

### Contoh Penggunaan
```bash
# Monitoring dengan threshold 15-85 cm, check setiap 15 detik
python3 water_level_monitor.py --high 85 --low 15 --interval 15

# Test sinkronisasi sekali
python3 water_level_monitor.py --test
```

## 🔒 Keamanan

### Session Management
- Token disimpan di session cookies
- Automatic token refresh jika expired
- Secure session handling

### Error Handling
- Graceful handling jika login gagal
- Retry mechanism untuk API calls
- Timeout protection
- Logging error untuk debugging

### Thread Safety
- Monitoring berjalan di background thread
- Tidak mengganggu sistem utama
- Clean shutdown saat interrupt

## 🔄 Integrasi dengan Sistem Existing

### actuatorLibrary.py
- Menggunakan `read_water_level_safety()` untuk baca sensor
- Tidak mengubah file actuatorLibrary.py
- Terpisah dan independen

### SynapsisLibrary.py
- Menggunakan `times.getDatetime()` untuk timestamp
- Konsisten dengan format waktu sistem

## 🚨 Troubleshooting

### Login Gagal
1. Cek koneksi internet
2. Verifikasi credentials (synapsis/password)
3. Cek endpoint login URL
4. Test dengan `test_synapsis_api.py`

### Actuator Update Gagal
1. Cek token session
2. Verifikasi endpoint actuator URL
3. Cek payload format
4. Test dengan menu "Test update actuator"

### Sensor Tidak Terbaca
1. Cek koneksi USB ke sensor
2. Verifikasi port `/dev/ttyUSB0`
3. Test dengan menu "Test pembacaan water level"

### Monitoring Tidak Berjalan
1. Cek thread status
2. Verifikasi parameter threshold
3. Cek log error di console
4. Test dengan `--test` flag

## 📈 Monitoring Dashboard

### Status Real-time
```
🚰 Water Level Monitor dengan threshold: 20-80 cm
⏱️  Check interval: 10 detik
✅ API connection OK

[2024-01-15 14:30:25] Level air: 45.2 cm
✅ Water level normal (45.2 cm)

[2024-01-15 14:30:35] Level air: 85.1 cm
🚨 Water level tinggi (85.1 cm ≥ 80 cm)
🔴 Matikan water pump actuator
✅ API update berhasil - Water pump actuator: false
```

### Log Aktivitas
```
🔐 Login ke API Synapsis...
✅ Login berhasil
🔑 Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

🚰 Update actuator: https://dev-nearon.synapsis.id/api/projectnode/nodes/...
📦 Payload: {'value': 'false'}
✅ API update berhasil - Water pump actuator: false
```

## 🔄 Changelog

### v1.0.0 (2024-01-15)
- ✅ Synapsis API Client dengan login
- ✅ Session management dan token handling
- ✅ Water level monitoring dengan API sync
- ✅ Automatic trigger berdasarkan threshold
- ✅ Testing tools lengkap
- ✅ Command line interface
- ✅ Dokumentasi komprehensif

---

**Dibuat dengan ❤️ menggunakan Synapsis API**
