#!/bin/bash
set -euo pipefail

MAIN_DIR="/home/ihms/Desktop/scheduler"

# -------------------------------
# Logging
# -------------------------------
LOG_FILE="$MAIN_DIR/logs/play_audio.log"
LOG_DIR="$(dirname "$LOG_FILE")"
mkdir -p "$LOG_DIR"
exec >>"$LOG_FILE" 2>&1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

# -------------------------------
# Configuration
# -------------------------------
PRAYER_NAME="${1:-}"
QURAN_AUDIO_MP3_LIST="${2:-}"
LOCK_FILE="$MAIN_DIR/var/player.lock"
AUDIO_DIR="$MAIN_DIR/audio"
VLC_PID=""
CURRENT_HOUR=$(date +%H)

PRIORITY_PRAYERS=("fajr" "dhuhr" "asr" "maghrib" "isha")
PRAYER_NAME_LOWER="${PRAYER_NAME,,}"



# -------------------------------
# Cleanup handler
# -------------------------------
cleanup() {
    log "Cleaning up..."

    if [[ -n "${VLC_PID}" ]] && kill -0 "$VLC_PID" 2>/dev/null; then
        kill -TERM "$VLC_PID" 2>/dev/null || true
        sleep 1
        kill -KILL "$VLC_PID" 2>/dev/null || true
    fi

    flock -u 200
    rm -f "$LOCK_FILE"
}

trap cleanup EXIT INT TERM HUP

# -------------------------------
# Validate input
# -------------------------------
if [[ -z "$PRAYER_NAME" ]]; then
    log "Usage: $0 <prayer_name>"
    exit 1
fi

# -------------------------------
# Log executed command
# -------------------------------
if [[ -n "$QURAN_AUDIO_MP3_LIST" ]]; then
    log "$PRAYER_NAME \"$QURAN_AUDIO_MP3_LIST\""
else
    log "$PRAYER_NAME"
fi


# -------------------------------
# Priority prayers override
# -------------------------------
if [[ " ${PRIORITY_PRAYERS[*]} " =~ " ${PRAYER_NAME_LOWER} " ]]; then
    log "Priority prayer '$PRAYER_NAME' detected. Killing other running instances..."
    # Kill other instances of this script
    for pid in $(pgrep -f "player-app.sh"); do
        if [[ $pid -ne $$ ]]; then
            log "Killing existing instance PID $pid"
            pkill -P "$pid" vlc || true
            kill -TERM "$pid" || true
        fi
    done
fi

# -------------------------------
# Acquire lock
# -------------------------------
exec 200>"$LOCK_FILE" || exit 1

if [[ " ${PRIORITY_PRAYERS[*]} " =~ " ${PRAYER_NAME_LOWER} " ]]; then
    # Wait for lock if priority prayer
    flock 200
else
    # Non-priority: exit if another instance is running
    flock -n 200 || {
        log "Another instance is already running. Exiting."
        exit 0
    }
fi

# -------------------------------
# Environment (audio + GUI)
# -------------------------------
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
export PULSE_SERVER="unix:/run/user/$(id -u)/pulse/native"
export DISPLAY=":0"
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus"

# -------------------------------
# Select audio directory
# -------------------------------
if [[ "$PRAYER_NAME_LOWER" == 'isha' && "$CURRENT_HOUR" -ge 22 ]]; then
    PLAYER_DIR="$AUDIO_DIR/fajr"
else
    case "$PRAYER_NAME_LOWER" in
        fajr)           PLAYER_DIR="$AUDIO_DIR/fajr" ;;
        duha)           PLAYER_DIR="$AUDIO_DIR/duha" ;;
        athkar_elsabah) PLAYER_DIR="$AUDIO_DIR/athkar_elsabah" ;;
        dhuhr)          PLAYER_DIR="$AUDIO_DIR/dhuhr" ;;
        asr)            PLAYER_DIR="$AUDIO_DIR/asr" ;;
        maghrib)        PLAYER_DIR="$AUDIO_DIR/maghrib" ;;
        athkar_elmasa)  PLAYER_DIR="$AUDIO_DIR/athkar_elmasa" ;;
        isha)           PLAYER_DIR="$AUDIO_DIR/isha" ;;
        tahajjud)       PLAYER_DIR="$AUDIO_DIR/tahajjud" ;;
        quran)          PLAYER_DIR="$AUDIO_DIR/quran" ;;
        *)
            log "ERROR: Unknown prayer '$PRAYER_NAME'"
            log "Allowed: fajr, duha, athkar_elsabah, dhuhr, asr, maghrib, athkar_elmasa, isha, tahajjud, quran"
            exit 1
            ;;
    esac
fi

# -------------------------------
# Ensure audio files exist
# -------------------------------
FILES=()

if [[ "$PRAYER_NAME_LOWER" == "quran" && -n "$QURAN_AUDIO_MP3_LIST" ]]; then
    IFS=',' read -ra AUDIO_NAMES <<< "$QURAN_AUDIO_MP3_LIST"

    for name in "${AUDIO_NAMES[@]}"; do
        file="$PLAYER_DIR/$(basename "$name")"
        if [[ "$file" == *.mp3 && -f "$file" ]]; then
            FILES+=("$file")
        fi
    done
else
    shopt -s nullglob
    FILES=("$PLAYER_DIR"/*.mp3)
    shopt -u nullglob
fi

if (( ${#FILES[@]} == 0 )); then
    log "ERROR: No audio files found to play"
    exit 1
fi

# -------------------------------
# Play
# -------------------------------
log "Playing $PRAYER_NAME..."
cvlc --intf dummy --no-video --play-and-exit "${FILES[@]}" &
VLC_PID=$!

# Wait until VLC finishes
wait "$VLC_PID"