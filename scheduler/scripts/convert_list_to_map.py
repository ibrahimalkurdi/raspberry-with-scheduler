import csv
import json

# Replace with your CSV file path
csv_file_path = "prayer_times_with_tahajjud_duha.csv"

# Output file names
python_output_file = "prayer_times_python_map.list"
js_output_file = "prayer_times_js_map.list"

python_maps = []
js_maps = []

with open(csv_file_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_map = {
            "Month": int(row["Month"]),
            "Day": int(row["Day"]),
            "Fajr": row["Fajr"],
            "Sunrise": row["Sunrise"],
            "Duha": row["Duha"],
            "Dhuhr": row["Dhuhr"],
            "Asr": row["Asr"],
            "Maghrib": row["Maghrib"],
            "Isha": row["Isha"],
            "Tahajjud": row["Tahajjud"]
        }
        python_maps.append(row_map)
        js_maps.append(row_map)

# Write Python map to file
with open(python_output_file, "w") as py_file:
    py_file.write("prayer_times = ")
    py_file.write(json.dumps(python_maps, indent=4))

# Write JavaScript map to file
with open(js_output_file, "w") as js_file:
    js_file.write("const prayerTimes = ")
    js_file.write(json.dumps(js_maps, indent=4))
    js_file.write(";")

print(f"Python map saved to {python_output_file}")
print(f"JavaScript map saved to {js_output_file}")

