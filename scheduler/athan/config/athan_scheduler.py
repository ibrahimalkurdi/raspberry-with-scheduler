import subprocess
from datetime import datetime
import time
import logging
import json
import os

CONFIG_DIR = "/home/ihms/Desktop/scheduler/athan/config"
LOG_DIR = "/home/ihms/Desktop/scheduler/athan/logs"
PY_MAP_FILE = os.path.join(CONFIG_DIR, "prayer_times_python_map.list")
EXECUTED_EVENTS_FILE = os.path.join(CONFIG_DIR, "executed_events.json")
LOG_FILE = os.path.join(LOG_DIR, "athan_scheduler.log")
ATHAN_SCRIPT = os.path.join(CONFIG_DIR, "play_athan.sh")

# Global prayer labels
PRAYER_LABELS = ['Fajr', 'Sunrise', 'Duha', 'Dhuhr', 'Asr', 'Maghrib', 'Isha', 'Tahajjud']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

class AthanScheduler:
    def __init__(self):
        self.schedule = []
        self.executed_events = self.load_executed_events()
        self.load_schedule()

    def load_executed_events(self):
        if os.path.exists(EXECUTED_EVENTS_FILE):
            with open(EXECUTED_EVENTS_FILE, 'r') as f:
                return set(json.load(f))
        return set()

    def save_executed_events(self):
        with open(EXECUTED_EVENTS_FILE, 'w') as f:
            json.dump(list(self.executed_events), f)

    def load_schedule(self):
        if not os.path.exists(PY_MAP_FILE):
            logging.error(f"Prayer times file not found: {PY_MAP_FILE}")
            return

        # Load the prayer_times map from the Python file
        prayer_times_globals = {}
        with open(PY_MAP_FILE, 'r') as f:
            code = f.read()
            exec(code, {}, prayer_times_globals)  # executes the file safely

        if 'prayer_times' not in prayer_times_globals:
            logging.error("No 'prayer_times' variable found in the file")
            return

        prayer_times_list = prayer_times_globals['prayer_times']
        year = datetime.now().year

        for row in prayer_times_list:
            # Support Month/Day keys in any capitalization
            month = int(row.get('Month', row.get('month', 1)))
            day = int(row.get('Day', row.get('day', 1)))

            for label in PRAYER_LABELS:
                # Skip Sunrise regardless of capitalization
                if label.lower() == 'sunrise':
                    continue

                # Fetch the key case-insensitively
                time_str = None
                key_found = None
                for key in row:
                    if key.lower() == label.lower():
                        time_str = str(row[key]).strip()
                        key_found = key
                        break

                if not time_str or time_str.lower() == 'nan':
                    continue

                try:
                    dt = datetime.strptime(f"{year}-{month:02d}-{day:02d} {time_str}",
                                           "%Y-%m-%d %H:%M")
                except ValueError as e:
                    logging.error(f"Invalid time format for {label} on {month}/{day}: {time_str}")
                    continue

                self.schedule.append({
                    'datetime': dt,
                    'type': label.lower().replace(' ', '_')
                })

        logging.info(f"Loaded {len(self.schedule)} events from map file.")

    def execute_athan(self, event):
        eid = f"{event['datetime'].strftime('%Y-%m-%d_%H:%M')}_{event['type']}"
        if not os.path.exists(ATHAN_SCRIPT):
            logging.error(f"Athan script not found: {ATHAN_SCRIPT}")
            return
        try:
            subprocess.run(
                [ATHAN_SCRIPT, event['type']],
                check=True,
                cwd=CONFIG_DIR
            )
            self.executed_events.add(eid)
            self.save_executed_events()
            logging.info(f"Executed athan for {event['type']} at {event['datetime']}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Athan script failed: {e}")

    def run(self):
        logging.info("Athan Scheduler started.")
        while True:
            now = datetime.now()

            # Only check at the beginning of each minute
            if now.second == 0:
                for event in self.schedule:
                    eid = f"{event['datetime'].strftime('%Y-%m-%d_%H:%M')}_{event['type']}"
                    # Trigger only if it's exactly the scheduled minute
                    if (event['datetime'].year == now.year and
                        event['datetime'].month == now.month and
                        event['datetime'].day == now.day and
                        event['datetime'].hour == now.hour and
                        event['datetime'].minute == now.minute and
                        eid not in self.executed_events):
                        
                        logging.info(f"Triggering {event['type']} at {event['datetime']}")
                        self.execute_athan(event)

                # Sleep the remainder of the minute to avoid multiple triggers in the same minute
                time.sleep(1)

            else:
                # Sleep briefly so we catch the top of the next minute
                time.sleep(0.5)


if __name__ == "__main__":
    AthanScheduler().run()

