import cv2
import urllib.request
import numpy as np
import time
import os
from dotenv import load_dotenv

load_dotenv()

# stream url MJPEG dari ESP32CAM
stream_url = os.getenv("STREAM_URL")

stream = urllib.request.urlopen(stream_url)
bytes_data = b''

frames = []
start = time.time()

print("Recording...")

while time.time() - start < 20:

    bytes_data += stream.read(1024)

    a = bytes_data.find(b'\xff\xd8')
    b = bytes_data.find(b'\xff\xd9')

    if a != -1 and b != -1:

        jpg = bytes_data[a:b+2]
        bytes_data = bytes_data[b+2:]

        img = cv2.imdecode(
            np.frombuffer(jpg, dtype=np.uint8),
            cv2.IMREAD_COLOR
        )

        if img is not None:
            frames.append(img)
            print("frame:", len(frames))

stream.close()

if len(frames) == 0:
    print("Tidak ada frame diterima")
    exit()

height, width, _ = frames[0].shape
fps = len(frames) / 20

out = cv2.VideoWriter(
    "recording.avi",
    cv2.VideoWriter_fourcc(*'XVID'),
    fps,
    (width, height)
)

for frame in frames:
    out.write(frame)

out.release()

print("Video 20 detik tersimpan")
print("Total frame:", len(frames))
print("FPS:", fps)