import pandas as pd
from datetime import datetime, timedelta

# Load the CSV
df = pd.read_csv('berlin_prayer_times.csv')

# Function to calculate Tahajjud (Fajr - 20 minutes)
def calculate_tahajjud(fajr_time):
    fajr_dt = datetime.strptime(fajr_time, '%H:%M')
    tahajjud_dt = fajr_dt - timedelta(minutes=20)
    return tahajjud_dt.strftime('%H:%M')

# Function to calculate Duha (Dhuhr - 60 minutes)
def calculate_duha(dhuhr_time):
    dhuhr_dt = datetime.strptime(dhuhr_time, '%H:%M')
    duha_dt = dhuhr_dt - timedelta(minutes=60)
    return duha_dt.strftime('%H:%M')

# Apply both calculations
df['Tahajjud'] = df['Fajr'].apply(calculate_tahajjud)
df['Duha'] = df['Dhuhr'].apply(calculate_duha)

# Reorder columns as requested
desired_order = [
    'Month', 'Day', 'Fajr', 'Sunrise', 'Duha', 'Dhuhr',
    'Asr', 'Maghrib', 'Isha', 'Tahajjud'
]

df = df[desired_order]

# Save the updated CSV
df.to_csv('prayer_times_with_tahajjud_duha.csv', index=False)

print(df)
print("Exported file is: prayer_times_with_tahajjud_duha.csv")
