import json
import os

from flask import send_from_directory
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request

from config import ALLOWED_ORIGINS, API_BASE_URL
from database import Database

app = Flask(__name__)

db = Database()

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin")

    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Content-Type, Authorization"
        )

    return response

def serialize(data):

    return json.loads(
        json.dumps(
            data,
            default=lambda o:
                str(o) if isinstance(o, (UUID, datetime))
                else float(o) if isinstance(o, Decimal)
                else o
        )
    )

@app.route("/")
def home():

    return jsonify({
        "status":"ok",
        "service":"Monitoring API"
    })

@app.route("/api/detections", methods=["GET"])
def get_detections():

    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))

        status = request.args.get("status")
        start = request.args.get("start")
        end = request.args.get("end")
        keyword = request.args.get("keyword") or request.args.get("q")

        result = db.get_paginated(
            page=page,
            limit=limit,
            status=status,
            start=start,
            end=end,
            keyword=keyword
        )

        return jsonify({
            "success": True,
            "page": result["page"],
            "limit": result["limit"],
            "total": result["total"],
            "total_pages": result["total_pages"],
            "count": len(result["rows"]),
            "data": serialize(result["rows"])

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }),500

@app.route("/api/dashboard")
def dashboard():

    try:
        data = db.get_dashboard()
        return jsonify({
            "success":True,
            "data":serialize(data)
        })

    except Exception as e:

        return jsonify({
            "success":False,
            "message":str(e)
        }),500

@app.route("/api/detections/<uuid:detection_id>", methods=["GET"])
def get_detection(detection_id):

    try:
        detection = db.get_by_id(str(detection_id))

        if not detection:

            return jsonify({
                "success": False,
                "message": "Data tidak ditemukan"
            }), 404

        images, video = build_media(
            detection["batch_folder"],
            detection["batch_number"]
        )

        result = serialize(detection)

        result["images"] = images
        result["video"] = video

        return jsonify({
            "success": True,
            "data": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@app.route("/api/detections/<uuid:detection_id>/files")
def detection_files(detection_id):

    try:
        data = db.get_files_info(str(detection_id))

        if not data:

            return jsonify({
                "success": False,
                "message": "Data tidak ditemukan"
            }), 404

        batch_folder = data["batch_folder"]
        batch_number = data["batch_number"]

        absolute_folder = os.path.abspath(batch_folder)

        if not os.path.exists(absolute_folder):

            return jsonify({
                "success": False,
                "message": "Folder batch tidak ditemukan"
            }), 404

        images = []

        video = None

        for file in sorted(os.listdir(absolute_folder)):

            if file.lower().endswith(".jpg"):
                images.append({
                    "name": file,
                    "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
                })

            elif file.lower().endswith(".mp4"):
                video = {
                    "name": file,
                    "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
                }

        return jsonify({
            "success": True,
            "batch_folder": batch_folder,
            "batch_number": batch_number,
            "images": images,
            "video": video

        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route("/api/files/<path:filepath>")
def serve_file(filepath):

    try:
        absolute_path = os.path.abspath(filepath)
        folder = os.path.dirname(absolute_path)
        filename = os.path.basename(absolute_path)

        return send_from_directory(folder, filename)

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 404


def build_media(batch_folder, batch_number):

    absolute_folder = os.path.abspath(batch_folder)

    images = []
    video = None

    if not os.path.exists(absolute_folder):
        return images, video

    for file in sorted(os.listdir(absolute_folder)):

        if file.lower().endswith(".jpg"):
            images.append({
                "name": file,
                "detected": "_detected" in file,
                "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
            })

        elif file.lower().endswith(".mp4"):
            video = {
                "name": file,
                "url": f"{API_BASE_URL}/api/files/{batch_folder}/{file}"
            }

    return images, video

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
