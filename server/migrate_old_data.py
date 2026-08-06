import os
import re
from datetime import datetime

from database import Database

db = Database()

FRAMES_DIR = "frames"


def parse_folder(folder_name):

    match = re.match(
        r"batch_(\d+)_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})",
        folder_name
    )

    if not match:
        return None

    batch_number = int(match.group(1))

    date = match.group(2)

    time = match.group(3).replace("-", ":")

    detected_at = datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M:%S"
    )

    return batch_number, detected_at


def scan_batch(path):

    total_frames = 0
    detected_frames = 0

    for file in sorted(os.listdir(path)):

        if file.endswith(".jpg"):

            total_frames += 1

            if "_detected" in file:
                detected_frames += 1

    return {
        "total_frames": total_frames,
        "detected_frames": detected_frames,
    }


def migrate():

    inserted = 0
    skipped = 0
    folders = sorted(os.listdir(FRAMES_DIR))

    for folder in folders:

        full_path = os.path.join(
            FRAMES_DIR,
            folder
        )

        if not os.path.isdir(full_path):
            continue

        relative_folder = f"frames/{folder}"

        parsed = parse_folder(folder)

        if not parsed:

            print("[INVALID]", folder)

            continue

        batch_number, detected_at = parsed

        if db.exists_batch_folder(relative_folder):

            skipped += 1

            print("[SKIP]", folder)

            continue

        result = scan_batch(full_path)

        if result["detected_frames"] == 0:

            skipped += 1
            print(f"[SKIP - NO DETECTION] {folder}")
            continue

        db.insert_detection({
            "batch_number": batch_number,
            "detected_at": detected_at,
            "total_frames": result["total_frames"],
            "detected_frames": result["detected_frames"],
            "avg_confidence": None,
            "presence_ratio": None,
            "longest_streak": None,
            "suspicion_score": None,
            "status": None,
            "batch_folder": relative_folder,
            "whatsapp_sent": False
        })

        inserted += 1

        print(
            f"[OK] Batch {batch_number}"
        )

    print()
    print("==========")
    print("Inserted :", inserted)
    print("Skipped  :", skipped)


if __name__ == "__main__":
    migrate()