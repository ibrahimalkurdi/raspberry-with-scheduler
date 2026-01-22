# Islamic Prayer Scheduler (Raspberry Pi)

This project provides an Islamic prayer time scheduler designed to run on a Raspberry Pi with a touchscreen. Follow the steps below to properly set up and run the application.

---
## Minimum Hardware Requirements

The following hardware components are required to run the Islamic Prayer Scheduler reliably:

- **Raspberry Pi 4 Model B** (minimum 1 GB RAM)
- **Official Raspberry Pi 7-inch Touchscreen Display**
- **OneNineDesign Touch Screen Case**
- **Official Raspberry Pi USB-C Power Supply** (5.1V / 3A)
- **DSI Ribbon Cable** (for connecting the touchscreen display to the Raspberry Pi)
- **SSD or SD card** (at least 32GB)

## Prerequisites
- Internet connection
- Keyboard, mouse, and display (for initial setup)

## How to Connect the Hardware

Follow the steps below to connect the Raspberry Pi and touchscreen correctly.

1. Connect the **DSI ribbon cable** from the Raspberry Pi DSI port to the touchscreen display.
2. Ensure the ribbon cable orientation is correct and firmly seated.
3. Mount the Raspberry Pi and touchscreen into the **OneNineDesign Touch Screen Case**.
4. Connect the **official USB-C power supply** to power on the device.

It should look like the diagram below:

[Hardware Connection Diagram](assets/raspberry-pi-4-with-raspberry-7-inches-touch-screen.png)




---

## Setup Instructions

### Step 0: Raspberry Pi Basic Setup

1. Download and install the latest Raspberry Pi OS.  
2. Burn the OS image to your SSD or SD card.  
3. Attach the storage device to the Raspberry Pi.  
4. Power on the Raspberry Pi and complete the initial OS setup.  

**Additional setup:**  

- **Enable SSH:**  
  1. Click on the Raspberry Pi icon on the desktop.  
  2. Navigate to **Preferences → Raspberry Pi Configuration → Interfaces**.  
  3. Click **Enable** next to SSH.  
  4. Click **OK** to save.  

- **Enable Executable Files:**  
  1. Open **File Manager**.  
  2. Go to **Edit → Preferences**.  
  3. Check the option **"Don't ask options on launch executable file"**.
---

### Step 1: Update the System

Run the following command to update and upgrade your system packages:
```
sudo apt update && sudo apt upgrade
```

### Step 2: Clone the Repository

Run:
```
git clone <repository-url>
```
---

### Step 3: Change Directory to the Project

Run:
```
cd islamic-prayer-scheduler
```
---

### Step 4: Rename the Scheduler Directory

Run:
```
mv scheduler-official-touch-screen-with-raspberry-pi-4 scheduler
```
---

### Step 5: Copy Scheduler to Desktop

Run:
```
cp -r scheduler ~/Desktop/
```
---

### Step 6: Add Prayer Times (CSV File)

Create a CSV file containing prayer times for your city and country using the following format:
```
Month,Day,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha
```
Sample data:
```
Month,Day,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Isha  
1,1,06:10,08:10,12:15,13:50,16:09,17:55  
1,2,06:10,08:10,12:15,13:51,16:10,17:56  
1,3,06:10,08:10,12:16,13:52,16:11,17:57  
1,4,06:10,08:10,12:16,13:53,16:12,17:58  
...
```
Once the file is ready, copy it to your Desktop using the following exact filename:
```
~/Desktop/إدخال-مواقيت-الصلاة-للمستخدم.csv
```
IMPORTANT: The filename must match exactly, including Arabic characters.

---

### Step 7: Run Initialization Script

Run:
```
bash ~/Desktop/scheduler/config/scripts/init.sh
```
---

### Step 8: Configure Cron Jobs

1. View the cron configuration file:
```
   cat ~/Desktop/scheduler/config/crontab.txt
```

2. Open the crontab editor:
```
   crontab -e
```

3. Copy and paste the contents of crontab.txt into the editor, then save and exit.

### Step 9: Verify Scheduler Service (Check Step)

To verify that the audio event scheduler service is running correctly, run:
```
sudo systemctl status audio_event_scheduler.service
```
The service should be in an active (running) state.

## Step 10: Running the Prayer Time GUIs

To start the **Prayer Time Countdown GUI** and the **Scheduler Settings GUI**, simply double-click the corresponding icons on the Raspberry Pi Desktop.

Once launched, the applications should appear similar to the images shown below:


<p>
  &nbsp;&nbsp;
  <img src="assets/athan-app-icon-64.png" alt="Prayer GUI" />
</p>
<p>
  <img src="assets/athan-settings-app-icon-84.png" alt="Scheduler Settings GUI" />
</p>




---

## Completion

After completing all steps, the Islamic Prayer Scheduler will be fully configured and will run automatically based on the configured prayer times.

---

## Notes

- Ensure the system date and timezone are correctly set.
- Update the CSV file whenever prayer times change.
- Re-run the initialization script if major configuration changes are made.

---

## License

Specify your project license here.




