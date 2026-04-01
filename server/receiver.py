from flask import Flask, request
import cv2
import numpy as np
import os
from ultralytics import YOLO

app = Flask(__name__)

# Buat folder untuk menyimpan hasil deteksi jika belum ada
os.makedirs("detected", exist_ok=True)

# Load model YOLOv8
model = YOLO("yolov8n_openvino_model/")

frames = []
counter = 0

BATCH_SIZE = 15

@app.route('/upload', methods=['POST'])
def upload():
    global counter,frames

    data = request.data

    npimg = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    #FILTER FRAME RUSAK
    if img is None:
        print("Frame corrupt, di-skip")
        return "FAIL", 400

    frames.append(img)

    cv2.imwrite(f"frame_{counter}.jpg", img)
    counter += 1

    print(f"Frame {counter} diterima")

    # Jalankan Yolo jika sudah terkumpul 15 frame
    if len(frames) >= BATCH_SIZE:

        print("Menjalankan YOLO (OpenVINO)...")

        results = model(
            frames, 
            conf=0.3,
            classes=[0], # Hanya deteksi orang (class 0 pada COCO)
            device="cpu"
        )

        detected = False # flag apakah ada manusia

        for i, result in enumerate(results):

            # cek apakah ada bounding box (manusia terdeteksi)
            if len(result.boxes) > 0:
                detected = True

                annotated = result.plot()

                filename = f"detected/detected_{counter}_{i}.jpg"
                cv2.imwrite(filename, annotated)

                print(f"Manusia terdeteksi! Disimpan: {filename}")

                # tampilkan (optional)
                cv2.imshow("Detection", annotated)
                cv2.waitKey(1)

        if not detected:
                print("Tidak ada manusia terdeteksi.")

        print("YOLO selesai!")

        # Hapus semua frame mentah
        start_index = counter - BATCH_SIZE
        for i in range(start_index, counter):
            try:
                os.remove(f"frame_{i}.jpg")
            except:
                 pass
        print("Frame mentah dihapus.")

        frames = []  # reset buffer

    return "OK"

app.run(host="0.0.0.0", port=5000)
