import json
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from flask import Flask
from flask import jsonify
from flask import request

from database import Database

app = Flask(__name__)

db = Database()

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
        keyword = request.args.get("q")

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
        data = db.get_by_id(str(detection_id))

        if not data:
            return jsonify({
                "success":False,
                "message":"Data tidak ditemukan"
            }),404
        return jsonify(serialize(data))

    except Exception as e:
        return jsonify({
            "success":False,
            "message":str(e)
        }),500

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )