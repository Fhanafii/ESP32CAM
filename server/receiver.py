from flask import Flask, request
import cv2
import numpy as np
import os
import subprocess
import threading, queue, time, worker
from ultralytics import YOLO
from datetime import datetime, timezone, timedelta  # added timedelta, timezone
from worker import send_whatsapp_video, init_whatsapp

app = Flask(__name__)

# Buat folder untuk menyimpan hasil deteksi jika belum ada
os.makedirs("frames", exist_ok=True)

# Load YOLOv8 OpenVINO model
model = YOLO("yolov8m_openvino_model/")

frames = []
counter = 0
batch_count = 0
# Buat antrean tugas
wa_queue = queue.Queue()

# WIB timezone (UTC+7)
WIB = timezone(timedelta(hours=7))

# Monitor esp32cam heartbeat
last_seen = datetime.now(WIB)

is_maintenance = False

@app.route('/toggle_maintenance', methods=['GET'])
def toggle_maintenance():
    global is_maintenance, frames
    is_maintenance = not is_maintenance
    if is_maintenance:
        frames = [] # Hapus frame yang nanggung saat maintenance dinyalakan
    status = "AKTIF" if is_maintenance else "NONAKTIF"
    return f"Mode Maintenance: {status}", 200

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    global last_seen
    last_seen = datetime.now(WIB)
    # Hanya print ke console (akan masuk ke error.log server)
    print(f"[HEARTBEAT] ESPCAM Aktif - {last_seen.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    return "OK", 200

def monitor_esp_health():
    global last_seen
    alert_logged = False
    
    while True:
        time_diff = datetime.now(WIB) - last_seen
        # Jika lebih dari 15 menit tidak ada kabar
        if time_diff > timedelta(minutes=15):
            if not alert_logged:
                # Log ini akan muncul di 'journalctl' dan 'error.log'
                print(f"!!! ALERT !!! ESPCAM OFFLINE SEJAK {last_seen.strftime('%H:%M:%S')}", flush=True)
                alert_logged = True
        else:
            if alert_logged:
                print("--- INFO --- ESPCAM KEMBALI ONLINE", flush=True)
                alert_logged = False
        
        time.sleep(60)

@app.route('/upload', methods=['POST'])
def upload():
    if is_maintenance:
        return "MAINTENANCE", 200 # Balas 200 agar ESP tidak retrying terus

    global counter, frames

    data = request.data
    npimg = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    if img is None:
        print("Frame corrupt, skipped")
        return "FAIL", 400

    frames.append(img)
    counter += 1
    print(f"Frame {counter} diterima")

    return "OK"

def create_video_from_frames(folder_path, output_name="output.mp4", fps=5):
    images = sorted([img for img in os.listdir(folder_path) if img.endswith(".jpg") and ("detected" in img or "undetected" in img)])

    if len(images) == 0:
        print("Tidak ada gambar untuk video")
        return

    first_frame = cv2.imread(os.path.join(folder_path, images[0]))
    height, width, _ = first_frame.shape

    video_path = os.path.join(folder_path, output_name)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v") # Gunakan codec MP4v untuk merangkai frame
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for image in images:
        img_path = os.path.join(folder_path, image)
        frame = cv2.imread(img_path)
        video.write(frame)

    video.release()
    print(f"Video berhasil dibuat: {video_path}")

def convert_to_whatsapp_format(input_path, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-vcodec", "libx264",
        "-acodec", "aac",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        output_path
    ]

    subprocess.run(command)

def whatsapp_worker():
    """Thread mandiri yang mengontrol Playwright"""
    print("WhatsApp Worker: Memulai Browser...")
    try:
        init_whatsapp() # Init di sini agar satu thread
        print("WhatsApp Worker: Browser SIAP!")
    except Exception as e:
        print(f"WhatsApp Worker: GAGAL INIT: {e}")
        return

    while True:
        # Menunggu tugas masuk ke antrean
        video_path, channel_name, caption = wa_queue.get()
        print(f"WhatsApp Worker: Mulai mengirim {video_path}")
        
        try:
            # Panggil fungsi kirim di worker.py
            success = send_whatsapp_video(video_path, channel_name, caption)
            if success:
                print(f"WhatsApp Worker: Berhasil kirim {video_path}")
            else:
                print(f"WhatsApp Worker: Gagal mengirim {video_path}")
        except Exception as e:
            print(f"WhatsApp Worker Error saat kirim: {e}")
        finally:
            wa_queue.task_done()

@app.route('/upload_done', methods=['POST'])
def upload_done():
    """Run YOLO on whatever frames are in the buffer"""
    global frames, batch_count, counter
    if is_maintenance:
        frames = [] # Bersihkan buffer agar tidak menumpuk
        return "MAINTENANCE", 200

    if len(frames) == 0:
        return "No frames to process", 400

    print(f"Running YOLO on {len(frames)} frames")

    # WIB timestamp
    timestamp = datetime.now(WIB).strftime("%Y-%m-%d_%H-%M-%S")
    batch_count += 1
    batch_folder = f"frames/batch_{batch_count}_{timestamp}"
    os.makedirs(batch_folder, exist_ok=True)

    detected_count = 0
    confidences = [] # List untuk menampung confidence

    try:
        for i, frame in enumerate(frames):
            frame_time = datetime.now(WIB).strftime("%H:%M:%S") # timestamp per frame 
            r = model(
                frame,
                conf=0.3,
                imgsz=640,
                classes=[0],
                device="cpu"
            )
            result = r[0]

            if len(result.boxes) > 0:
                detected_count += 1
                # Ambil confidence score (biasanya result.boxes.conf adalah tensor)
                conf_val = result.boxes.conf[0].item() 
                confidences.append(conf_val)
                annotated = result.plot()
                # Tambahkan timestamp ke frame
                cv2.putText(
                    annotated,
                    frame_time,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, # ukuran font lebih kecil
                    (0, 255, 0),
                    2
                )
                filename = f"{batch_folder}/{i:03d}_detected.jpg"
                cv2.imwrite(filename, annotated)
                print(f"Detected → {filename}")
            else:
                # Tambahkan timestamp juga ke frame tanpa deteksi
                cv2.putText(
                    frame,
                    frame_time,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    2
                )
                filename = f"{batch_folder}/{i:03d}_undetected.jpg"
                cv2.imwrite(filename, frame)
                print(f"No detection → {filename}")

        # Log deteksi
        with open(f"{batch_folder}/log.txt", "w") as f:
            f.write(f"Total frames: {len(frames)}\n")
            f.write(f"Detected: {detected_count}\n")
            f.write(f"Undetected: {len(frames) - detected_count}\n")

        print(f"Batch done! Saved to {batch_folder}")
        
        if detected_count > 1:
            video_name = f"batch_{batch_count}_detected.mp4"
        else:
            video_name = f"batch_{batch_count}_undetected.mp4"

        # Buat video dari frame yang sudah diproses
        raw_video = os.path.join(batch_folder, "temp.mp4")
        create_video_from_frames(batch_folder, output_name="temp.mp4", fps=5)

        # Konversi video ke format yang kompatibel
        final_video = os.path.join(batch_folder, video_name)
        convert_to_whatsapp_format(raw_video, final_video)  # overwrite dengan format yang sesuai
        os.remove(raw_video)

        # Hitung Rata-rata Confidence
        avg_conf = (sum(confidences) / len(confidences) * 100) if confidences else 0

        # Buat String Caption
        caption = (
            f"🚨 *DETEKSI MANUSIA TERKONFIRMASI*\n\n"
            f"🕒 *Waktu:* `{frame_time}`\n"
            f"📍 *Lokasi:* `Jl.B6 gang belakang masjid Al-muhajirin RT 07/ RW 013 Kel.Pejagalan, Kec.Penjaringan, Jakarta Utara`\n"
            f"📊 *Akurasi Rata-rata:* `{avg_conf:.1f}%`\n"
            f"📸 *Total Frame:* `{detected_count} pos / {len(frames)} total`\n"
            f"🆔 *Batch:* `{batch_count}`"
        )

        if detected_count > 0:
            # Masukkan data ke antrean, bukan membuat thread baru setiap saat
            print(f"Menambahkan ke antrean WA: {final_video}")
            wa_queue.put((final_video, "ESPCAM Deteksi RT 07", caption))
        

    except Exception as e:
        print("ERROR YOLO:", e)

    finally:
        frames = []  # reset buffer

    return "OK"

@app.route('/status')
def status():
    global page, last_seen, batch_count, wa_queue, is_maintenance
    actual_channel = worker.current_channel
    # Cek Kondisi Browser & Page Playwright
    is_wa_ready = False
    try:
        # Jika page ada dan tidak tertutup
        if page and not page.is_closed():
            # Cek apakah kita masih di domain whatsapp
            if "whatsapp" in page.url:
                is_wa_ready = True
    except Exception:
        is_wa_ready = False

    # Hitung selisih waktu heartbeat
    time_diff = datetime.now(WIB) - last_seen
    esp_status = "ONLINE" if time_diff.total_seconds() < 900 else "OFFLINE" # 15 menit threshold

    return {
        "server_time": datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S"),
        "system_mode": {
            "maintenance_mode": is_maintenance,
            "status": "MAINTENANCE" if is_maintenance else "RUNNING"
        },
        "whatsapp": {
            "status": "READY" if is_wa_ready else "CRASHED/DISCONNECTED",
            "current_channel": actual_channel if is_wa_ready else None,
            "queue_size": wa_queue.qsize()
        },
        "esp32cam": {
            "status": esp_status,
            "last_seen": last_seen.strftime("%Y-%m-%d %H:%M:%S"),
            "seconds_since_last_seen": int(time_diff.total_seconds())
        },
        "statistics": {
            "total_batch_processed": batch_count
        }
    }

# Jalankan worker saat aplikasi di-load oleh Gunicorn
# Gunakan start_wa_worker() hanya pada saat menggunakan Gunicorn, bukan saat run langsung untuk development
# Hapus atau komentari start_wa_worker() jika menjalankan langsung dengan python receiver.py untuk menghindari multiple thread saat development
def start_wa_worker():
    print("Memulai Thread Worker WhatsApp (Gunicorn)...", flush=True)
    t = threading.Thread(target=whatsapp_worker, daemon=True)
    t.start()

start_wa_worker()

if __name__ == "__main__":
    # 1. NYALAKAN WHATSAPP SEKALI SAJA SAAT STARTUP
    print("Memulai Browser WhatsApp...")
    threading.Thread(target=whatsapp_worker, daemon=True).start() # Mulai worker WhatsApp di thread terpisah 
    threading.Thread(target=monitor_esp_health, daemon=True).start() # Mulai monitoring kesehatan ESP
    print("Memulai Flask Server...")
    app.run(host="0.0.0.0", port=5000)