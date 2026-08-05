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
        status = request.args.get("status")
        start = request.args.get("start")
        end = request.args.get("end")
        keyword = request.args.get("q")

        if status or start or end or keyword:
            data = db.get_filtered(
                status=status,
                start=start,
                end=end,
                keyword=keyword
            )

        else:
            data = db.get_all()

        return jsonify({
            "success": True,
            "count": len(data),
            "data": serialize(data)
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

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