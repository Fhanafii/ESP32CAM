from flask import Flask
from flask import jsonify
from flask import request

from database import Database

app = Flask(__name__)

db = Database()

@app.route("/")
def home():

    return jsonify({

        "status":"ok",

        "service":"Monitoring API"

    })

@app.route("/api/detections")
def detections():

    data = db.get_all()

    return jsonify(data)

@app.route("/api/detections/<id>")
def detection(id):

    data = db.get_by_id(id)

    return jsonify(data)

@app.route("/api/filter")
def filter_detection():

    start=request.args.get("start")

    end=request.args.get("end")

    data=db.get_by_date(start,end)

    return jsonify(data)

if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )