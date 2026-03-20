from flask import Flask, request
import cv2
import numpy as np

app = Flask(__name__)

frames = []
counter = 0

@app.route('/upload', methods=['POST'])
def upload():
    global counter

    data = request.data

    npimg = np.frombuffer(data, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    frames.append(img)

    cv2.imwrite(f"frame_{counter}.jpg", img)
    counter += 1

    print(f"Frame {counter} diterima")

    return "OK"

app.run(host="0.0.0.0", port=5000)