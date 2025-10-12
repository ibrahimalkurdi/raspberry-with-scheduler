# Raspberry init ssh setup


## Enable SSH
```code
echo 'dtoverlay=dwc2' >> /boot/firmware/config.txt
echo 'modules-load=dwc2,g_ether' >> /boot/firmware/cmdline.txt
```

## Reconnect to paired speaker after reboot

##### Note: Replace AA:BB:CC:DD:EE:FF with the paired speaker bluetooth mac address

```code
cat <<EOF >> /usr/local/bin/bt-autoconnect.sh
#!/bin/bash
bluetoothctl << BLUETOOTHEOF
connect AA:BB:CC:DD:EE:FF
BLUETOOTHEOF
EOF
```

```code
chmod +x /usr/local/bin/bt-autoconnect.sh
```

```code
( crontab -l 2>/dev/null | grep -F "@reboot /usr/local/bin/bt-autoconnect.sh" ) || \
( crontab -l 2>/dev/null; echo "@reboot /usr/local/bin/bt-autoconnect.sh" ) | crontab -
```


# Quran and Athan setup



### General setup:

```code
export HOME_DIR="/home/ihms"
export SCHEDULER_DIR="${HOME_DIR}/scheduler"
export ATHAN_DIR="${SCHEDULER_DIR}/athan"
export QURAN_DIR="${SCHEDULER_DIR}/quran"
export ATHAN_AUDIO="${ATHAN_DIR}/audio"
export ATHAN_FAJR_AUDIO="${ATHAN_DIR}/audio/fajr"
export QURAN_AUDIO="${QURAN_DIR}/audio"
export ATHAN_CONFIG="${ATHAN_DIR}/config"
export QURAN_CONFIG="${QURAN_DIR}/config"
export ATHAN_LOGS="${ATHAN_DIR}/logs"
export QURAN_LOGS="${QURAN_DIR}/logs"
export QURAN_SCHEDULE_TIME='30 06 * * *'
```

```code
mkdir -p $ATHAN_DIR
mkdir -p $QURAN_DIR
mkdir -p $ATHAN_AUDIO
mkdir -p $ATHAN_FAJR_AUDIO
mkdir -p $QURAN_AUDIO
mkdir -p $ATHAN_CONFIG
mkdir -p $QURAN_CONFIG
mkdir -p $ATHAN_LOGS
mkdir -p $QURAN_LOGS
```

```code
echo "[]" > "${ATHAN_CONFIG}/executed_events.json"
touch "${ATHAN_LOGS}/athan_scheduler.log"
# Ensure the athan time file existed under this directory ${ATHAN_CONFIG}
# This is the time file format example:
# tail berlin_prayer_times.csv
# Month,Day,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha
# 12,22,06:06,08:08,12:10,13:41,16:01,17:47
# 12,23,06:06,08:09,12:11,13:42,16:01,17:47
```


### Scripts setup:

```code
cat <<EOF >> $QURAN_CONFIG/play_quran.sh
#!/bin/bash

# Kill any existing VLC process before starting
pkill -9 -f "vlc"

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native
DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus \
cvlc --intf dummy --no-video --play-and-exit ${QURAN_AUDIO}/*.mp3


# Ensure it is terminated in case it got stuck
pkill -9 -f "vlc" || true
EOF
```

```code
chmod +x $QURAN_CONFIG/play_quran.sh
```

```code
cat <<EOF >> $ATHAN_CONFIG/play_athan.sh
#!/bin/bash

PRAYER_NAME="$1"
CURRENT_HOUR=$(date +%H)

# Kill any existing VLC process before starting
pkill -9 -f "vlc"

export XDG_RUNTIME_DIR=/run/user/$(id -u)
export PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native

if [[ "${PRAYER_NAME,,}" == 'fajr' && "$CURRENT_HOUR" -ge 22 ]]; then
	DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus timeout 180 cvlc -I dummy --play-and-exit ${ATHAN_FAJR_AUDIO}/*.mp3
else	
	DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus timeout 180 cvlc -I dummy --play-and-exit ${ATHAN_AUDIO}/*.mp3
fi

# Ensure it is terminated in case it got stuck
pkill -9 -f "vlc" || true
EOF
```

```code
chmod +x $ATHAN_CONFIG/play_athan.sh
```

```code
cat <<EOF >> $ATHAN_CONFIG/athan.service
[Unit]
Description=Athan Prayer Scheduler
After=network.target sound.target

[Service]
User=ihms
WorkingDirectory=${ATHAN_DIR}
ExecStart=/usr/bin/python3 ${ATHAN_CONFIG}/athan_scheduler.py
Restart=always
StandardOutput=append:${ATHAN_LOGS}/athan_scheduler.log
StandardError=append:${ATHAN_LOGS}/athan_scheduler.log

[Install]
WantedBy=multi-user.target
EOF
```

```code
sudo cp $ATHAN_CONFIG/athan.service /etc/systemd/system/athan.service
```

```code
cat <<EOF >> ${ATHAN_CONFIG}/athan_scheduler.py
import pandas as pd
import subprocess
from datetime import datetime
import time
import logging
import json
import os

CONFIG_DIR = "${ATHAN_CONFIG}"
LOG_DIR = "${ATHAN_LOGS}"
CSV_FILE = os.path.join(CONFIG_DIR, "berlin_prayer_times.csv")
EXECUTED_EVENTS_FILE = os.path.join(CONFIG_DIR, "executed_events.json")
LOG_FILE = os.path.join(LOG_DIR, "athan_scheduler.log")
ATHAN_SCRIPT = os.path.join(CONFIG_DIR, "play_athan.sh")

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
        if not os.path.exists(CSV_FILE):
            logging.error(f"CSV file not found: {CSV_FILE}")
            return
        df = pd.read_csv(CSV_FILE)
        year = datetime.now().year
        for _, row in df.iterrows():
            month = int(row['Month'])
            day = int(row['Day'])
            for label in ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
                if label.lower() == 'sunrise':
                    continue  # skip executing at sunrise
                time_str = str(row[label]).strip()
                if not time_str or time_str.lower() == 'nan':
                    continue

                dt = datetime.strptime(f"{year}-{month:02d}-{day:02d} {time_str}",
                                       "%Y-%m-%d %H:%M")
                self.schedule.append({
                    'datetime': dt,
                    'type': label.lower().replace(' ','_')
                })
        logging.info(f"Loaded {len(self.schedule)} events.")

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
EOF
```

```code
chmod +x ${ATHAN_CONFIG}/athan_scheduler.py
```

### Set the schedulers:

```code
sudo systemctl daemon-reload
sudo systemctl enable athan.service
sudo systemctl start athan.service

export QURAN_CRON_JOB="${QURAN_SCHEDULE_TIME} bash -x ${QURAN_CONFIG}/play_quran.sh >|${QURAN_LOGS}/quran.log 2>&1"


# [run quran daily]: Add the cron job if it is not already there
( crontab -l 2>/dev/null | grep -F "$QURAN_CRON_JOB" ) || \
( crontab -l 2>/dev/null; echo "$QURAN_CRON_JOB" ) | crontab -


# [daily log retention for athan log file]: Add the cron job if it is not already there
( crontab -l 2>/dev/null | grep -F "00 00 * * * echo "" > ${ATHAN_LOGS}/athan_scheduler.log" ) || \
( crontab -l 2>/dev/null; echo "00 00 * * * echo "" > ${ATHAN_LOGS}/athan_scheduler.log" ) | crontab -


# [daily log retention for athan execution event file]: Add the cron job if it is not already there
( crontab -l 2>/dev/null | grep -F "00 00 * * * echo '[]' > ${ATHAN_CONFIG}/executed_events.json" ) || \
( crontab -l 2>/dev/null; echo "00 00 * * * echo '[]' > ${ATHAN_CONFIG}/executed_events.json" ) | crontab -
```
