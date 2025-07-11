
<div align="center">
  <img src="https://raw.githubusercontent.com/platane/platane/output/github-contribution-grid-snake-dark.svg" alt="Snake animation" />
</div>

<h1 align="center">🏡 Smart‑Home</h1>

<p align="center">
  Sistem Smart Home berbasis <strong>ESP32 + Golang + Python</strong><br>
  Automatisasi, kontrol suhu, lampu, dan kipas secara real‑time.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-development-yellow" alt="status">
  <img src="https://img.shields.io/badge/made%20with-Go%20%7C%20Python%20%7C%20ESP32-blue" alt="tech">
  <img src="https://img.shields.io/github/license/BagusA23/Smart-home" alt="license">
</p>

---

## 🔍 Ringkasan

| Komponen     | Teknologi & Fungsi                          |
|--------------|----------------------------------------------|
| **API**      | Backend Golang (Gin) + PostgreSQL / SQLite   |
| **APP**      | UI Desktop Python (Tkinter/CustomTkinter)    |
| **ESP32**    | Firmware Arduino — sensor & aktuator         |
| **Komunikasi** | HTTP REST API, JSON                         |

---

## 🚀 Fitur Utama

- 📡 Monitoring suhu & kelembapan **real-time**
- 💡 Kontrol perangkat rumah: **lampu, kipas, dll**
- 🔐 Sistem **autentikasi login/register**
- ⚙️ Otomatisasi suhu dengan **logika fuzzy** 
- 🗂️ CRUD data perangkat
- 🌙 UI versi **dark mode**

---

## 📸 Tampilan (Coming Soon!)

```markdown
📷 assets/screenshot-ui.png
🧠 Tambahkan screenshot antarmuka dan wiring board di sini nanti!
```

## 🧩 Arsitektur Sistem  
```
ESP32 <--HTTP--> Backend API <--CRUD--> Desktop APP
```
 - ESP32 mengirim data sensor via HTTP  
 - Backend API menyimpan & mengatur logika kontrol  
 - APP mengontrol perangkat dan membaca status dari API

## 📦 Struktur Folder
```
SMART_HOME/
├── API/        → Backend Go (REST API)
├── APP/        → UI Desktop Python
├── Esp32/      → Source Code ESP32 (Arduino)
└── README.md
```


## 🛠️ Instalasi & Setup  
1. Jalankan Backend (API)
```
cd API  
go mod tidy  
go run main.go  
```
2. Jalankan Desktop App  
```
cd APP  
pip install -r requirements.txt  
python main.py  
```
3. Upload Firmware ke ESP32  
- Buka Esp32/ di Arduino IDE / PlatformIO  
- Edit SSID, password, dan URL API  
- Upload ke board ESP32  

## 🧠 Fitur Tambahan (Future Plan)  
✅ Kontrol manual perangkat  
✅ UI versi Dark/Light Mode  
✅ Autentikasi user (login/register)  
✅ Fuzzy logic otomatisasi suhu  
✅ Notifikasi Telegram saat event (overheat, gas, dll)  

## 👨‍💻 Tentang Developer  
Bagus Ardiansyah  
💻 Mahasiswa Teknik Informatika  
📍 Fokus: IoT • Backend • Desktop Apps  
📫 GitHub [@BagusA23](https://github.com/BagusA23)  

📄 Lisensi  
MIT License © 2025 Bagus Ardiansyah  

<p align="center"> <sub>Made with ❤️ using Go, Python, and ESP32</sub><br> <sub>Powered by kopi dan deadline ✨</sub> </p> 
