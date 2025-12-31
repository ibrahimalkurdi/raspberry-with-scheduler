#!/usr/bin/env python3
import subprocess
from datetime import datetime, time as dt_time
import time
import logging
import json
import os
import configparser


MAIN_DIR = "/home/ihms/Desktop/scheduler"

CONFIG_DIR = os.path.join(MAIN_DIR, "config")
SCRIPTS_DIR = os.path.join(MAIN_DIR, "config","scripts")
LOG_DIR = os.path.join(MAIN_DIR, "logs")

SETTINGS_INI_FILE = os.path.join(CONFIG_DIR, "config.ini")
PRAYER_PYTHON_MAP_FILE = os.path.join(CONFIG_DIR, "prayer_times_map.py")
EXECUTED_EVENTS_FILE = os.path.join(CONFIG_DIR, "executed-events.json")
AUDIO_EVENT_SCHEDULER_LOG_FILE = os.path.join(LOG_DIR, "audio_event_scheduler.log")
PLAYER_APP_SCRIPT_FILE = os.path.join(SCRIPTS_DIR, "play_audio.sh")

# ──────────────────────────────────────────────────────────────
# Labels
# ──────────────────────────────────────────────────────────────

PRAYER_LABELS = [
    'Fajr', 'Sunrise', 'Athkar_elsabah', 'Duha',
    'Dhuhr', 'Asr', 'Maghrib', 'Athkar_elmasa',
    'Isha', 'Tahajjud'
]

QURAN_EVENT_LABEL = "Quran"

CONFIG_TO_PRAYER = {
    "enable_prayer_fajr": "Fajr",
    "enable_prayer_dhuhr": "Dhuhr",
    "enable_prayer_asr": "Asr",
    "enable_prayer_maghrib": "Maghrib",
    "enable_prayer_isha": "Isha",
    "enable_tahajjud_prayer": "Tahajjud",
    "enable_duha_prayer": "Duha",
    "enable_athkar_elsabah": "Athkar_elsabah",
    "enable_athkar_elmasa": "Athkar_elmasa",
}

CONFIG_TO_DAILY_EVENT = {
    "enable_listen_to_quran": QURAN_EVENT_LABEL
}

# ──────────────────────────────────────────────────────────────
# Config helpers
# ──────────────────────────────────────────────────────────────

def load_skipped_events():
    skipped = ["Sunrise"]  # always skipped

    if not os.path.exists(SETTINGS_INI_FILE):
        return skipped

    config = configparser.ConfigParser()
    config.read(SETTINGS_INI_FILE)

    if "Settings" not in config:
        return skipped

    for key, label in CONFIG_TO_PRAYER.items():
        if not config["Settings"].getboolean(key, fallback=True):
            skipped.append(label)

    for key, label in CONFIG_TO_DAILY_EVENT.items():
        if not config["Settings"].getboolean(key, fallback=True):
            skipped.append(label)

    return skipped


def load_quran_time():
    if not os.path.exists(SETTINGS_INI_FILE):
        return None

    config = configparser.ConfigParser()
    config.read(SETTINGS_INI_FILE)

    try:
        time_str = config["Settings"].get("listen_to_quran", fallback=None)
        if not time_str:
            return None
        return datetime.strptime(time_str.strip(), "%H:%M").time()
    except ValueError:
        logger.error("Invalid listen_to_quran format (expected HH:MM)")
        return None


def load_quran_audio_checked():
    if not os.path.exists(SETTINGS_INI_FILE):
        return None

    config = configparser.ConfigParser()
    config.read(SETTINGS_INI_FILE)

    return config["Settings"].get("quran_audio_checked", fallback=None)


def log_current_config():
    logger.info("========== Scheduler Configuration ==========")

    logger.info(f"CONFIG_DIR = {CONFIG_DIR}")
    logger.info(f"LOG_DIR = {LOG_DIR}")
    logger.info(f"SETTINGS_INI_FILE = {SETTINGS_INI_FILE}")
    logger.info(f"PRAYER_PYTHON_MAP_FILE = {PRAYER_PYTHON_MAP_FILE}")
    logger.info(f"PLAYER_APP_SCRIPT_FILE = {PLAYER_APP_SCRIPT_FILE}")

    if not os.path.exists(SETTINGS_INI_FILE):
        logger.warning("config.ini not found")
        return

    config = configparser.ConfigParser()
    config.read(SETTINGS_INI_FILE)

    if "Settings" not in config:
        logger.warning("No [Settings] section in config.ini")
        return

    logger.info("[Settings]")
    for key, value in config["Settings"].items():
        logger.info(f"  {key} = {value}")

    skipped = load_skipped_events()
    quran_time = load_quran_time()

    logger.info(f"Skipped events (effective): {skipped}")
    logger.info(f"Quran time (effective): {quran_time}")

    logger.info("============================================")



# ──────────────────────────────────────────────────────────────
# Logging
# ──────────────────────────────────────────────────────────────

logger = logging.getLogger("scheduler")
logger.setLevel(logging.INFO)

# THIS LINE STOPS DUPLICATION
logger.propagate = False

if logger.hasHandlers():
    logger.handlers.clear()

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler = logging.FileHandler(AUDIO_EVENT_SCHEDULER_LOG_FILE)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# ──────────────────────────────────────────────────────────────
# Load config AFTER logging is ready
# ──────────────────────────────────────────────────────────────

SKIPPED_EVENTS = load_skipped_events()
SKIPPED_EVENTS_SET = {e.lower() for e in SKIPPED_EVENTS}

log_current_config()


# ──────────────────────────────────────────────────────────────
# Scheduler
# ──────────────────────────────────────────────────────────────

class AthanScheduler:
    def __init__(self):
        self.schedule = []
        self.executed_events = self.load_executed_events()
        self.load_schedule()

    def load_executed_events(self):
        if os.path.exists(EXECUTED_EVENTS_FILE):
            with open(EXECUTED_EVENTS_FILE, "r") as f:
                return set(json.load(f))
        return set()

    def save_executed_events(self):
        with open(EXECUTED_EVENTS_FILE, "w") as f:
            json.dump(list(self.executed_events), f)

    def load_schedule(self):
        self.schedule.clear()

        # ───── Load prayer times ─────
        if not os.path.exists(PRAYER_PYTHON_MAP_FILE):
            logger.error(f"Prayer map not found: {PRAYER_PYTHON_MAP_FILE}")
            return

        prayer_globals = {}

        with open(PRAYER_PYTHON_MAP_FILE, "r") as f:
            exec(f.read(), {}, prayer_globals)


        prayer_times = prayer_globals.get("prayerTimes")
        if not prayer_times:
            logger.error("No prayerTimes variable found")
            return

        year = datetime.now().year

        for row in prayer_times:
            month = int(row.get("Month", row.get("month", 1)))
            day = int(row.get("Day", row.get("day", 1)))

            for label in PRAYER_LABELS:
                if label.lower() in SKIPPED_EVENTS_SET:
                    continue

                time_str = None
                for k in row:
                    if k.lower() == label.lower():
                        time_str = str(row[k]).strip()
                        break

                if not time_str or time_str.lower() == "nan":
                    continue

                try:
                    dt = datetime.strptime(
                        f"{year}-{month:02d}-{day:02d} {time_str}",
                        "%Y-%m-%d %H:%M"
                    )
                except ValueError:
                    continue

                self.schedule.append({
                    "datetime": dt,
                    "type": label.lower().replace(" ", "_")
                })

        # ───── Daily Quran event ─────
        if QURAN_EVENT_LABEL.lower() not in SKIPPED_EVENTS_SET:
            quran_time = load_quran_time()
            if quran_time:
                today = datetime.now().date()
                dt = datetime.combine(today, quran_time)

                quran_audio = load_quran_audio_checked()

                self.schedule.append({
                    "datetime": dt,
                    "type": "quran",
                    "audio_list": quran_audio
                })

                logger.info(f"Scheduled daily Quran at {dt}")

        logger.info(f"Total scheduled events: {len(self.schedule)}")

    def execute_athan(self, event):
        eid = f"{event['datetime'].strftime('%Y-%m-%d_%H:%M')}_{event['type']}"

        if not os.path.exists(PLAYER_APP_SCRIPT_FILE):
            logger.error(f"Athan script not found: {PLAYER_APP_SCRIPT_FILE}")
            return

        try:
            cmd = [PLAYER_APP_SCRIPT_FILE, event["type"]]

            if event["type"] == "quran" and event.get("audio_list"):
                cmd.append(event["audio_list"])

            subprocess.run(
                cmd,
                check=True,
                cwd=CONFIG_DIR
            )
            self.executed_events.add(eid)
            self.save_executed_events()
            logger.info(f"Executed {event['type']} at {event['datetime']}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Execution failed: {e}")

    def run(self):
        logger.info("Athan Scheduler started")

        while True:
            now = datetime.now()

            if now.second == 0:
                for event in self.schedule:
                    eid = f"{event['datetime'].strftime('%Y-%m-%d_%H:%M')}_{event['type']}"

                    if (
                        event["datetime"].year == now.year and
                        event["datetime"].month == now.month and
                        event["datetime"].day == now.day and
                        event["datetime"].hour == now.hour and
                        event["datetime"].minute == now.minute and
                        eid not in self.executed_events
                    ):
                        logger.info(f"Triggering {event['type']}")
                        self.execute_athan(event)

                time.sleep(1)
            else:
                time.sleep(0.5)


if __name__ == "__main__":
    AthanScheduler().run()

