#!/bin/bash

# The name you found from 'nmcli connection show'
WIFI_NAME="preconfigured"
LOG_FILE="/home/ihms/Desktop/scheduler/logs/wifi_rebooter.log"

# Auto-detect default gateway
ROUTER_IP=$(ip route | awk '/default/ {print $3; exit}')

# Fallback in case it couldn't be detected
if [[ -z "$ROUTER_IP" ]]; then
    echo "$(date): Could not determine gateway IP!" >> "$LOG_FILE"
    exit 1
fi

# Ensure log file exists
if [[ ! -f "$LOG_FILE" ]]; then
    touch "$LOG_FILE"
fi

# Ping the router twice
ping -c2 "$ROUTER_IP" > /dev/null

if [ $? != 0 ]; then
    echo "$(date): WiFi down! Attempting reconnect..." >> "$LOG_FILE"
    sudo nmcli connection up id "$WIFI_NAME"
fi

