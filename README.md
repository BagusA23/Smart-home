# 🏠 SMART HOME PROJECT

🚀 Proyek ini adalah sistem **Smart Home berbasis ESP32** yang terintegrasi dengan:
- Backend API (Go + Gin)
- Desktop UI (Python + Tkinter)
- Kontrol Perangkat IoT (Lampu, Kipas, Sensor Suhu, dsb.)

---

## 📦 Struktur Proyek

```
SMART_HOME/
├── API/ # Backend Golang: REST API untuk kontrol perangkat & sensor
├── APP/ # Aplikasi desktop (Python Tkinter) untuk kontrol user
├── Esp32/ # Kode untuk microcontroller (ESP32 + Arduino)
```


---

## ⚙️ Teknologi yang Digunakan

| Komponen     | Teknologi                         |
|--------------|-----------------------------------|
| Backend API  | Go (Gin Framework) + PostgreSQL   |
| Frontend UI  | Python (CustomTkinter)            |
| IoT Device   | ESP32 + Arduino Framework         |
| Komunikasi   | HTTP REST API                     |

---

## 🌐 Fitur Utama

✅ Monitoring suhu & kelembapan secara real-time  
✅ Kontrol lampu dan kipas dari aplikasi desktop  
✅ Sistem otomatisasi suhu menggunakan fuzzy logic *(on development)*  
✅ Modular per ruangan: kamar, dapur, ruang tamu  
✅ Autentikasi user (login/register)  

---

## 📸 Preview Aplikasi

*(Coming Soon!)*  
Tambahkan screenshot aplikasi desktop dan wiring ESP di sini.

---

## 📡 Integrasi IoT

- 📍ESP32 terhubung ke jaringan WiFi
- 📍Data sensor dikirim via HTTP POST ke server
- 📍Perintah dari aplikasi dikirim ke ESP melalui REST API

---

## 🛠 Cara Jalankan

### 1. Backend (API)
```
cd API
go run main.go
```

2. Frontend (Aplikasi Desktop)
```
cd APP
python main.py
```

3. ESP32
   - Upload kode dari folder Esp32 ke ESP32 via Arduino IDE
   - Pastikan koneksi WiFi & endpoint API sudah sesuai
  
👨‍💻 Developer
👤 Bagus Ardiansyah
Mahasiswa Teknik Informatika | IoT & Software Enthusiast

📫 GitHub


💡 Rencana Pengembangan
 CRUD perangkat

✅ Kontrol LED & Fan
✅ UI versi dark mode
✅ Fuzzy logic untuk pengaturan suhu otomatis
✅ Android app via Bluetooth
✅ Notifikasi via Telegram

 📜 License
MIT License © 2025 Bagus Ardiansyah
