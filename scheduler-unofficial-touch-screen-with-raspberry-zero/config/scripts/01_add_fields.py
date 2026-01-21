import pandas as pd
from datetime import datetime, timedelta
import configparser
import os

# ===== CONFIGURATION =====
MAIN_DIR = "/home/ihms/Desktop/scheduler"
CONFIG_DIR = os.path.join(MAIN_DIR, "config")

SETTINGS_INI_FILE = os.path.join(CONFIG_DIR, "config.ini")
PRAYER_INPUT_CSV_FILE =  os.path.join(CONFIG_DIR, "input-prayers-time.csv")
PRAYER_OUTPUT_CSV_FILE = os.path.join(CONFIG_DIR, "prayer_times.csv")

# Default values
DEFAULT_TAHAJJUD = 20
DEFAULT_DUHA = 60
DEFAULT_ATHKAR_ELSABAH = 60
DEFAULT_ATHKAR_ELMASA = 20

# Read the config
config = configparser.ConfigParser()
if os.path.exists(SETTINGS_INI_FILE):
    config.read(SETTINGS_INI_FILE)
    tahajjud_time = int(config.get('Settings', 'tahajjud_time', fallback=DEFAULT_TAHAJJUD))
    duha_time = int(config.get('Settings', 'duha_time', fallback=DEFAULT_DUHA))
    athkar_elsabah_time = int(config.get('Settings', 'athkar_elsabah_time', fallback=DEFAULT_ATHKAR_ELSABAH))
    athkar_elmasa_time = int(config.get('Settings', 'athkar_elmasa_time', fallback=DEFAULT_ATHKAR_ELMASA))
else:
    print(f"Config file not found at {SETTINGS_INI_FILE}. Using default values.")
    tahajjud_time = DEFAULT_TAHAJJUD
    duha_time = DEFAULT_DUHA
    athkar_elsabah_time = DEFAULT_ATHKAR_ELSABAH
    athkar_elmasa_time = DEFAULT_ATHKAR_ELMASA

# ===== LOAD CSV =====
if os.path.exists(PRAYER_INPUT_CSV_FILE):
    df = pd.read_csv(PRAYER_INPUT_CSV_FILE)
else:
    raise FileNotFoundError(f"CSV file not found: {PRAYER_INPUT_CSV_FILE}")

# ===== CALCULATION FUNCTIONS =====
def calculate_tahajjud(fajr_time):
    fajr_dt = datetime.strptime(fajr_time, '%H:%M')
    return (fajr_dt - timedelta(minutes=tahajjud_time)).strftime('%H:%M')

def calculate_athkar_elsabah(fajr_time):
    fajr_dt = datetime.strptime(fajr_time, '%H:%M')
    return (fajr_dt + timedelta(minutes=athkar_elsabah_time)).strftime('%H:%M')

def calculate_duha(dhuhr_time):
    dhuhr_dt = datetime.strptime(dhuhr_time, '%H:%M')
    return (dhuhr_dt - timedelta(minutes=duha_time)).strftime('%H:%M')

def calculate_athkar_elmasa(maghrib_time):
    maghrib_dt = datetime.strptime(maghrib_time, '%H:%M')
    return (maghrib_dt + timedelta(minutes=athkar_elmasa_time)).strftime('%H:%M')

# ===== APPLY CALCULATIONS =====
df['Athkar_elsabah'] = df['Fajr'].apply(calculate_athkar_elsabah)
df['Duha'] = df['Dhuhr'].apply(calculate_duha)
df['Athkar_elmasa'] = df['Maghrib'].apply(calculate_athkar_elmasa)
df['Tahajjud'] = df['Fajr'].apply(calculate_tahajjud)

# ===== REORDER COLUMNS =====
desired_order = [
    'Month', 'Day', 'Fajr', 'Sunrise', 'Athkar_elsabah', 'Duha', 'Dhuhr',
    'Asr', 'Maghrib', 'Athkar_elmasa', 'Isha', 'Tahajjud'
]
df = df[desired_order]

# ===== SAVE CSV =====
df.to_csv(PRAYER_OUTPUT_CSV_FILE, index=False)
print(df)
print("Exported file is: " + PRAYER_OUTPUT_CSV_FILE)

