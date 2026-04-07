# 📷 ESP32-CAM Smart Security System

Project ini merupakan sistem keamanan sederhana berbasis **ESP32-CAM + YOLOv8** untuk mendeteksi manusia secara real-time.  
ESP32-CAM akan mengirimkan frame ke server, kemudian diproses menggunakan YOLOv8 (OpenVINO) untuk mendeteksi objek manusia.

---

## 🚀 Features
- 📷 Capture gambar dari ESP32-CAM  
- 📡 Kirim gambar ke server (Flask)  
- 🧠 Deteksi manusia menggunakan YOLOv8  
- ⚡ Optimasi CPU dengan OpenVINO  
- 🎬 Pembuatan video batch otomatis (.mp4)  
- 💬 Kirim notifikasi video + caption ke WhatsApp Channel  
- 🗑️ Hapus frame mentah otomatis  
- 📁 Simpan hanya hasil deteksi (efisien storage)  

---

## 🛠️ Hardware Setup (ESP32-CAM)

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/ESP32CAM.git
cd ESP32CAM
```

### 2. Setup ESP32-CAM
Buat file baru bernama `wifi_config.h`, lalu isi:

```cpp
#define WIFI_SSID "your_wifissid"
#define WIFI_PASSWORD "your_wifipassword"
```

### 3. Set Server URL
Edit file `wifi_config.h` dan sesuaikan IP server Anda:

```cpp
#define SERVER_URL "http://your_server_ip:5000/upload"
```

### 4. Upload ke ESP32
Install **PlatformIO** di VS Code, lalu upload program ke ESP32-CAM.

---

## 💻 YOLOv8 Pipeline Setup (Laptop - Development)

### 1. Masuk ke folder server
```bash
cd server
```

### 2. Buat Virtual Environment (Python 3.10)
```bash
py -3.10 -m venv venv310
venv310\Scripts\activate
```

### 3. Install Dependencies & Playwright
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Download & Export Model OpenVINO
```bash
yolo export model=yolov8s.pt format=openvino
```

### 5. Jalankan Server
```bash
python receiver.py
```

---

## ☁️ YOLOv8 Pipeline Setup (Ubuntu Server - Production)

### 1. Persiapan Sistem & Library GUI
```bash
sudo apt update
sudo apt install python3.10-venv ffmpeg xvfb libgl1 libglib2.0-0 -y
```

### 2. Setup Venv & Gunicorn
```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
playwright install chromium
sudo venv/bin/playwright install-deps chromium
```

### 3. Login WhatsApp via Screenshot (Headless)
```bash
xvfb-run python3 login_manual.py
```
Tarik file `qr_scan.png` ke laptop menggunakan scp command, lalu scan via HP.
```bash
scp user@ip_address:~/ESP32CAM/server/qr_scan.png .
```
### 4. Jalankan via Production Server (Gunicorn)
```bash
PYTHONUNBUFFERED=1 xvfb-run --auto-servernum gunicorn -w 1 --threads 4 --timeout 120 -b 0.0.0.0:5000 receiver:app
```
### Optional (jika port belum terbuka)
```bash
sudo ufw allow 5000
```
---

## ⚙️ Cara Kerja Sistem

1. ESP32-CAM menangkap gambar  
2. Gambar dikirim ke server Flask  
3. Server mengumpulkan beberapa frame (batch)  
4. YOLOv8 memproses gambar menggunakan OpenVINO  

### Output:
- Jika **terdeteksi manusia**:
  - `detected_*.jpg`
  - dibuat video → `batch_*_detected.mp4`

- Jika **tidak terdeteksi manusia**:
  - `undetected_*.jpg`
  - dibuat video → `batch_*_undetected.mp4`

5. Batch dengan deteksi manusia akan dikirim ke WhatsApp Channel secara otomatis (dengan akurasi & timestamp)

---

## ⚠️ Notes
- Pastikan ESP32 dan server berada di jaringan yang sama  
- Gunakan Python 3.10 untuk kompatibilitas terbaik (Playwright & OpenVINO)  
- Gunakan flag `-w 1` pada Gunicorn untuk menghindari konflik session WhatsApp  
- `xvfb-run` wajib digunakan di server headless agar Playwright dapat berjalan  

---

## 👤 Author
Developed by **Fhanafii**

---