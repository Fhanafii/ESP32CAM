from flask import Flask, request
import cv2
import numpy as np
import os
from ultralytics import YOLO
from datetime import datetime, timezone, timedelta  # added timedelta, timezone

app = Flask(__name__)

# Buat folder untuk menyimpan hasil deteksi jika belum ada
os.makedirs("frames", exist_ok=True)

# Load YOLOv8 OpenVINO model
model = YOLO("yolov8s_openvino_model/")

frames = []
counter = 0
batch_count = 0

# WIB timezone (UTC+7)
WIB = timezone(timedelta(hours=7))

@app.route('/upload', methods=['POST'])
def upload():
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

def create_video_from_frames(folder_path, output_name="output.mp4", fps=3):
    images = sorted([img for img in os.listdir(folder_path) if img.endswith(".jpg")])

    if len(images) == 0:
        print("Tidak ada gambar untuk video")
        return

    first_frame = cv2.imread(os.path.join(folder_path, images[0]))
    height, width, _ = first_frame.shape

    video_path = os.path.join(folder_path, output_name)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    for image in images:
        img_path = os.path.join(folder_path, image)
        frame = cv2.imread(img_path)
        video.write(frame)

    video.release()
    print(f"Video berhasil dibuat: {video_path}")

@app.route('/upload_done', methods=['POST'])
def upload_done():
    """Run YOLO on whatever frames are in the buffer"""
    global frames, batch_count, counter

    if len(frames) == 0:
        return "No frames to process", 400

    print(f"Running YOLO on {len(frames)} frames")

    # WIB timestamp
    timestamp = datetime.now(WIB).strftime("%Y-%m-%d_%H-%M-%S")
    batch_count += 1
    batch_folder = f"frames/batch_{batch_count}_{timestamp}"
    os.makedirs(batch_folder, exist_ok=True)

    detected_count = 0

    try:
        for i, frame in enumerate(frames):
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
                annotated = result.plot()
                # Tambahkan timestamp ke frame
                cv2.putText(
                    annotated,
                    timestamp,
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
                    timestamp,
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

        create_video_from_frames(batch_folder, output_name=video_name, fps=3)
    except Exception as e:
        print("ERROR YOLO:", e)

    finally:
        frames = []  # reset buffer

    return "OK"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)