from datetime import datetime

from database import Database

db = Database()

print("=" * 50)
print("Testing PostgreSQL Connection...")
print("=" * 50)

if db.test_connection():

    print("Connection Success")

    detection = {
        "batch_number": 999,
        "batch_folder": "frames/batch_test",
        "detected_at": datetime.now(),
        "total_frames": 15,
        "detected_frames": 12,
        "avg_confidence": 0.84,
        "presence_ratio": 0.80,
        "longest_streak": 8,
        "suspicion_score": 2,
        "status": "Perlu Dipantau",
        "whatsapp_sent": True,
    }

    db.save_detection(detection)

    print("Dummy Detection Saved")
    detections = db.get_all()
    print(f"\nTotal Data : {len(detections)}\n")
    print("Latest Detection")
    print(detections[0])

else:

    print("Failed Connection")