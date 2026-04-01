# ESP32-CAM Smart Security System

Project ini merupakan sistem keamanan sederhana berbasis **ESP32-CAM + YOLOv8** untuk mendeteksi manusia secara real-time.
ESP32-CAM akan mengirimkan frame ke server, kemudian diproses menggunakan YOLOv8 (OpenVINO) untuk mendeteksi objek manusia.

---

## 🚀 Features

* 📷 Capture gambar dari ESP32-CAM
* 📡 Kirim gambar ke server (Flask)
* 🧠 Deteksi manusia menggunakan YOLOv8
* ⚡ Optimasi CPU dengan OpenVINO
* 🗑️ Hapus frame mentah otomatis
* 📁 Simpan hanya hasil deteksi (efisien storage)

---

## 🛠️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Fhanafii/ESP32CAM.git
cd ESP32CAM
```

---

### 2. Setup ESP32-CAM

Buat file baru bernama `wifi_config.h`, lalu isi:

```c
#define WIFI_SSID "your_wifissid"
#define WIFI_PASSWORD "your_wifipassword"
```

---

### 3. Set Server URL

Edit file konfigurasi `wifi_config.h` dan sesuaikan:

```c
#define SERVER_URL "your_serverurl"
```

Contoh:

```c
#define SERVER_URL "http://192.168.1.10:5000/upload"
```

---

### 4. Upload ke ESP32

Install **PlatformIO** di VS Code, lalu upload program ke ESP32-CAM.

---

## YOLOv8 Pipeline Setup (Server)

### 1. Masuk ke folder server

```bash
cd server
```

---

### 2. Buat Virtual Environment (Python 3.10)

```bash
py -3.10 -m venv venv310
venv310\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Download & Export Model OpenVINO

```bash
yolo export model=yolov8n.pt format=openvino
```

Setelah proses selesai, akan muncul folder:

```
yolov8n_openvino_model/
```

---

### 5. Jalankan Server

```bash
python receiver.py
```

Server akan berjalan di:

```
http://0.0.0.0:5000
```

---

## Cara Kerja Sistem

1. ESP32-CAM menangkap gambar
2. Gambar dikirim ke server Flask
3. Server mengumpulkan beberapa frame (batch)
4. YOLOv8 memproses gambar
5. Jika terdeteksi manusia, output akan:

   * Manusia terdeteksi! Disimpan
6. Jika tidak:

   * Tidak ada manusia terdeteksi.
7. Semua frame mentah dihapus otomatis

---

## Output

* `detected_*.jpg` → hasil deteksi manusia
* Frame mentah → otomatis dihapus

---

## ⚠️ Notes

* Pastikan ESP32 dan server berada di jaringan yang sama
* Gunakan Python 3.10 untuk kompatibilitas terbaik
* OpenVINO direkomendasikan untuk performa CPU lebih cepat

---

## Author

Developed by [Fhanafii](https://github.com/Fhanafii)
