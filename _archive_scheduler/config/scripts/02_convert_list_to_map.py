import csv
import json
import os

# Replace with your CSV file path

MAIN_DIR = "/home/ihms/Desktop/scheduler"
CONFIG_DIR = os.path.join(MAIN_DIR, "config")

PRAYER_INPUT_CSV_FILE = os.path.join(CONFIG_DIR, "prayer_times.csv")
PRAYER_PYTHON_MAP_FILE = os.path.join(CONFIG_DIR, "prayer_times_map.py")

python_maps = []


with open(PRAYER_INPUT_CSV_FILE, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_map = {
            "Month": int(row["Month"]),
            "Day": int(row["Day"]),
            "Fajr": row["Fajr"],
            "Sunrise": row["Sunrise"],
            "Athkar_elsabah": row["Athkar_elsabah"],
            "Duha": row["Duha"],
            "Dhuhr": row["Dhuhr"],
            "Asr": row["Asr"],
            "Maghrib": row["Maghrib"],
            "Athkar_elmasa": row["Athkar_elmasa"],
            "Isha": row["Isha"],
            "Tahajjud": row["Tahajjud"]
        }
        python_maps.append(row_map)

# Write Python map to file
with open(PRAYER_PYTHON_MAP_FILE, "w") as py_file:
    py_file.write("prayerTimes = ")
    py_file.write(json.dumps(python_maps, indent=4))

print(f"Python map saved to {PRAYER_PYTHON_MAP_FILE}")

