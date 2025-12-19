#!/bin/bash

# Kill any existing VLC process before starting
pkill -9 -f "vlc"

export XDG_RUNTIME_DIR=/run/user/1000
export PULSE_SERVER=unix:/run/user/1000/pulse/native
DISPLAY=:0 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus cvlc --intf dummy --no-video --play-and-exit /home/ihms/Desktop/scheduler/quran/audio/*.mp3


# Ensure it is terminated in case it got stuck
pkill -9 -f "vlc" || true
