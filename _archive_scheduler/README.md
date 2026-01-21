## Raspberry init ssh setup


### Enable SSH
```code
cd /boot/firmware
echo 'dtoverlay=dwc2' >> ./config.txt
echo 'modules-load=dwc2,g_ether' >> ./cmdline.txt
```

### Enable ELECROW 7 Inch HDMI Touchscreen Monitor
https://www.elecrow.com/download/product/DIS78950R/7_inch_HDMI_touchscreen_monitor_user_manual.pdf?srsltid=AfmBOooSWo0WnD30zQw_URRowO0aCE8X3MtZUtwk8LRfGRsv59t8UXvt
```code
cd /boot/firmware
echo 'hdmi_force_hotplug=1' >> ./config.txt
echo 'max_usb_current=1' >> ./config.txt
echo 'hdmi_group=2' >> ./config.txt
echo 'hdmi_mode=1' >> ./config.txt
echo 'hdmi_mode=87' >> ./config.txt
echo 'hdmi_cvt 1024 600 60 6 0 0 0' >> ./config.txt
echo 'hdmi_drive=2' >> ./config.txt
```
## Update & Upgrade OS and disable WIFI powersaving optoin:
```
sudo apt update && sudo apt upgrade -y
```
Create wifi-powersave-off script for servicectl
```
sudo tee /etc/systemd/system/wifi-powersave-off.service << EOF
[Unit]
Description=Disable wlan0 powersave
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/sbin/iw dev wlan0 set power_save off

[Install]
WantedBy=multi-user.target
EOF
```
Enable and start the service
```
sudo systemctl daemon-reload
sudo systemctl enable wifi-powersave-off.service
sudo systemctl start wifi-powersave-off.service
```
check:
```
sudo systemctl status wifi-powersave-off.service
iwconfig
```

## Bluetooth setup, install required python package:
```
sudo apt install -y pi-bluetooth bluez blueman

sudo systemctl enable bluetooth
sudo systemctl start bluetooth
sudo systemctl status bluetooth


bluetoothctl list


sudo rfkill list all
sudo rfkill unblock bluetooth
sudo rfkill list

sudo hciconfig hci0 up


bluetoothctl

power on
agent on
default-agent
scan on
pair 08:EB:ED:05:62:A3 # replace it with bluetooh MAC ID
trust 08:EB:ED:05:62:A3 # replace it with bluetooh MAC ID
connect 08:EB:ED:05:62:A3 # replace it with bluetooh MAC ID

sudo apt-get install python3-pandas
```

### Reconnect to the paired bluetooth speaker after OS reboot

##### Note: Replace AA:BB:CC:DD:EE:FF with the paired speaker bluetooth mac address

```code
sudo tee /usr/local/bin/bt-autoconnect.sh > /dev/null <<'EOF'
#!/bin/bash
bluetoothctl <<'BLUETOOTHEOF'
connect AA:BB:CC:DD:EE:FF
BLUETOOTHEOF
EOF
```

```code
sudo chmod +x /usr/local/bin/bt-autoconnect.sh
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

PRAYER_NAME="\$1"
CURRENT_HOUR=\$(date +%H)
ATHAN_AUDIO_DIR="/home/ihms/Desktop/scheduler/athan/audio"

# Kill any existing VLC process before starting
pkill -9 -f "vlc" || true

# Runtime user id (not hard coded)
export XDG_RUNTIME_DIR="/run/user/\$(id -u)"
export PULSE_SERVER="unix:/run/user/\$(id -u)/pulse/native"

# For GUI audio applications
export DISPLAY=":0"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/\$(id -u)/bus"

# Select correct audio folder
case "\${PRAYER_NAME,,}" in

    fajr)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/fajr/"*.mp3
        ;;

    dhuhr)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/dhuhr/"*.mp3
        ;;

    asr)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/asr/"*.mp3
        ;;

    maghrib)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/maghrib/"*.mp3
        ;;

    isha)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/isha/"*.mp3
        ;;

    tahajjud)
        cvlc --intf dummy --no-video --play-and-exit "\${ATHAN_AUDIO_DIR}/tahajjud/"*.mp3
        ;;

    *)
        echo "ERROR - \$(date +%d-%m-%Y--%H-%M): Unknown prayer: '\$PRAYER_NAME'"
        echo "Allowed: fajr, sunrise, dhuhr, asr, maghrib, isha, tahajjud"
        ;;
esac

# Ensure VLC is terminated in case it got stuck
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

# Touch Screen Athan & Quran setup:
Build initial script to create athan desktop icon and run it in the reboot

```
Note:
To execute the athan desktop script by clicking on the icon, it needs this change:
From the Desktop GUI, click on: Raspberry icon -> Accessories -> File Manager -> Edit -> Preferences -> (check this box) Don't ask options on launch executable file
```

### Init Vars:
```
export HOME_DIR="/home/ihms/Desktop"
export SCHEDULER_DIR="${HOME_DIR}/scheduler"
export SCRIPTS_DIR="${SCHEDULER_DIR}/scripts"
mkdir -p "$SCRIPTS_DIR"
```

### Build up the script:
```
cat << EOF > $SCRIPTS_DIR/install_athan_desktop.sh
#!/bin/bash

### 1) Create scheduler directory and the athan_start script
cat << 'EOD' > "$SCRIPTS_DIR/athan_start.sh"
#!/bin/bash

# Wait until localhost is reachable
while ! curl -s http://localhost >/dev/null; do
    sleep 1
done

# Remove HSTS file (extra safety)
rm -f ~/.mozilla/firefox/*.default*/SiteSecurityServiceState.txt

# Kill Firefox if running
pkill firefox

# Start clean Firefox on HTTP
firefox --private-window --no-remote --new-instance "http://localhost"
EOD

chmod +x "$SCRIPTS_DIR/athan_start.sh"


### 2) Create the real athan.desktop inside script directory

cat << 'EOD' > "$SCRIPTS_DIR/athan.desktop"
[Desktop Entry]
Type=Application
Name=Athan Display
Comment=Open local Athan page
Exec=$SCRIPTS_DIR/athan_start.sh
Icon=web-browser
Terminal=false
Categories=Utility;
EOD

chmod +x "$SCRIPTS_DIR/athan.desktop"


### 3) Create symlink in ~/.local/share/applications

mkdir -p "$HOME/.local/share/applications"
rm -f "$HOME/.local/share/applications/athan.desktop"
ln -s "$SCRIPTS_DIR/athan.desktop" "$HOME/.local/share/applications/athan.desktop"


### 4) Create symlink in ~/.config/autostart

mkdir -p "$HOME/.config/autostart"
rm -f "$HOME/.config/autostart/athan.desktop"
ln -s "$SCRIPTS_DIR/athan.desktop" "$HOME/.config/autostart/athan.desktop"


### 5) Create symlink on Desktop (no popup)

mkdir -p "$HOME/Desktop"
rm -f "$HOME/Desktop/athan.desktop"
ln -s "$SCRIPTS_DIR/athan.desktop" "$HOME/Desktop/athan.desktop"

echo "✓ Athan installed successfully."
echo "✓ Script created at $SCRIPTS_DIR/athan_start.sh"
echo "✓ Desktop Entry stored at $SCRIPTS_DIR/athan.desktop"
echo "✓ Symlink added to ~/.local/share/applications/athan.desktop (menu entry)"
echo "✓ Symlink added to ~/.config/autostart/athan.desktop (autostart enabled)"
echo "✓ Symlink added to ~/Desktop/athan.desktop (no-popup launcher)"
EOF
```

### Execute the script
```
chmod +x $SCRIPT_DIR/install_athan.sh
bash $SCRIPT_DIR/install_athan.sh
```
