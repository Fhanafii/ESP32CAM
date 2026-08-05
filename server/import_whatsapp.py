import sys
from datetime import datetime

from database import Database

db = Database()


def parse_caption(text: str):

    data = {}

    for raw in text.splitlines():

        line = raw.strip()

        if not line:
            continue

        if "Waktu:" in line:

            value = line.split("Waktu:", 1)[1]
            value = value.replace("`", "").strip()

            data["detected_at"] = datetime.strptime(
                value,
                "%Y-%m-%d %H:%M:%S"
            )

        elif "Status:" in line:

            value = line.split("Status:", 1)[1]
            data["status"] = value.replace("`", "").strip()

        elif "Confidence YOLO:" in line:

            value = line.split("Confidence YOLO:", 1)[1]
            value = value.replace("%", "")
            value = value.replace("`", "").strip()

            data["avg_confidence"] = float(value)

        elif "Total Frame:" in line:

            value = line.split("Total Frame:", 1)[1]
            value = value.replace("`", "").strip()

            left, right = value.split("/")

            detected = left.replace("pos", "").strip()

            total = right.replace("total", "").strip()

            data["detected_frames"] = int(detected)

            data["total_frames"] = int(total)

        elif "Presence Ratio:" in line:

            value = line.split("Presence Ratio:", 1)[1]
            value = value.replace("`", "").strip()

            data["presence_ratio"] = float(value)

        elif "Longest Streak:" in line:

            value = line.split("Longest Streak:", 1)[1]
            value = value.replace("frame", "")
            value = value.replace("frames", "")
            value = value.replace("`", "").strip()

            data["longest_streak"] = int(value)

        elif "Batch:" in line:

            value = line.split("Batch:", 1)[1]
            value = value.replace("`", "").strip()

            data["batch_number"] = int(value)

    if data["status"] == "Normal":

        data["suspicion_score"] = 1

    elif data["status"] == "Perlu Dipantau":

        data["suspicion_score"] = 2

    else:

        data["suspicion_score"] = 3

    return data


def split_captions(text: str):

    captions = []

    current = []

    for line in text.splitlines():

        if "================================" in line:

            if current:

                captions.append("\n".join(current))

                current = []

            continue

        if line.strip():

            current.append(line)

        elif current:

            current.append(line)

    if current:

        captions.append("\n".join(current))

    return captions


def update_database(data):

    db.update_detection_from_whatsapp(

        batch_number=data["batch_number"],

        detected_at=data["detected_at"],

        avg_confidence=data["avg_confidence"],

        presence_ratio=data["presence_ratio"],

        longest_streak=data["longest_streak"],

        suspicion_score=data["suspicion_score"],

        status=data["status"]

    )


def main():

    if len(sys.argv) > 1:

        filename = sys.argv[1]

        with open(filename, "r", encoding="utf-8") as f:

            text = f.read()

    else:

        print()

        print("Paste Caption WhatsApp")

        print("Linux  : CTRL+D")

        print("Windows: CTRL+Z lalu Enter")

        print()

        text = ""

        try:

            while True:

                text += input() + "\n"

        except EOFError:

            pass

    captions = split_captions(text)

    if not captions:

        print("Tidak ada caption ditemukan.")

        return

    success = 0

    failed = 0

    skipped = 0

    print()

    print(f"Total Caption : {len(captions)}")

    print()

    for index, caption in enumerate(captions, start=1):

        try:

            data = parse_caption(caption)

            update_database(data)

            success += 1

            print(

                f"[{index}/{len(captions)}] "

                f"Batch {data['batch_number']} ✓"

            )

        except Exception as e:

            failed += 1

            print(

                f"[{index}/{len(captions)}] "

                f"Gagal : {e}"

            )

    print()

    print("==============================")
    print(f"Berhasil : {success}")
    print(f"Gagal    : {failed}")
    print(f"Skipped  : {skipped}")
    print("==============================")

if __name__ == "__main__":

    main()