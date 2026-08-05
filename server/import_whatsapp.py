import re
from datetime import datetime

from database import Database

db = Database()


def parse(text):

    data = {}

    data["detected_at"] = datetime.strptime(

        re.search(

            r"Waktu:\s*`(.+?)`",

            text

        ).group(1),

        "%Y-%m-%d %H:%M:%S"

    )

    data["status"] = re.search(

        r"Status:\s*`(.+?)`",

        text

    ).group(1)

    data["avg_confidence"] = float(

        re.search(

            r"Confidence YOLO:\s*`([\d.]+)%`",

            text

        ).group(1)

    )

    frame = re.search(

        r"Total Frame:\s*`(\d+)\s*pos\s*/\s*(\d+)\s*total`",

        text

    )

    data["detected_frames"] = int(frame.group(1))

    data["total_frames"] = int(frame.group(2))

    data["presence_ratio"] = float(

        re.search(

            r"Presence Ratio:\s*`([\d.]+)`",

            text

        ).group(1)

    )

    data["longest_streak"] = int(

        re.search(

            r"Longest Streak:\s*`(\d+)`",

            text

        ).group(1)

    )

    data["batch_number"] = int(

        re.search(

            r"Batch:\s*`(\d+)`",

            text

        ).group(1)

    )

    if data["status"] == "Normal":

        score = 1

    elif data["status"] == "Perlu Dipantau":

        score = 2

    else:

        score = 3

    data["suspicion_score"] = score

    return data


print()

print("Paste Caption WhatsApp")

print("Akhiri dengan Ctrl+Z (Windows) lalu Enter")

print()

text = ""

try:

    while True:

        text += input() + "\n"

except EOFError:

    pass

data = parse(text)

print()

print(data)

confirm = input(
    "\nUpdate database? (y/n): "
)

if confirm.lower() == "y":

    db.update_detection_from_whatsapp(
        batch_number=data["batch_number"],
        detected_at=data["detected_at"],
        avg_confidence=data["avg_confidence"],
        presence_ratio=data["presence_ratio"],
        longest_streak=data["longest_streak"],
        suspicion_score=data["suspicion_score"],
        status=data["status"]
    )

    print("✓ Database berhasil diupdate")

else:
    print("Dibatalkan")