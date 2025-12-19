#!/bin/bash

PRAYER_NAME="$1"
CURRENT_HOUR=$(date +%H)
ATHAN_AUDIO_DIR="/home/ihms/Desktop/scheduler/athan/audio"

# Kill any existing VLC process before starting
pkill -9 -f "vlc" || true

# Runtime user id (not hard coded)
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export PULSE_SERVER="unix:/run/user/$(id -u)/pulse/native"

# For GUI audio applications
export DISPLAY=":0"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# Select correct audio folder
case "${PRAYER_NAME,,}" in

    fajr)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/fajr/"*.mp3
        ;;

    duha)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/duha/"*.mp3
        ;;

    dhuhr)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/dhuhr/"*.mp3
        ;;

    asr)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/asr/"*.mp3
        ;;

    maghrib)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/maghrib/"*.mp3
        ;;

    isha)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/isha/"*.mp3
        ;;

    tahajjud)
        cvlc --intf dummy --no-video --play-and-exit "${ATHAN_AUDIO_DIR}/tahajjud/"*.mp3
        ;;

    *)
        echo "ERROR - $(date +%d-%m-%Y--%H-%M): Unknown prayer: '$PRAYER_NAME'"
        echo "Allowed: fajr, sunrise, dhuhr, asr, maghrib, isha, tahajjud"
        ;;
esac

# Ensure VLC is terminated in case it got stuck
pkill -9 -f "vlc" || true
