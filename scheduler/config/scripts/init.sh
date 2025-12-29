#!/bin/bash

echo "replace all home directory hardcoded with acutal home directory $HOME"
echo "These are the actual files which are going to be changed:"
cd ~/Desktop/scheduler
grep -rl "/home/ihms" .

echo "Apply the HOME directory changes..."
find . -type f -exec sed -i "s|/home/ihms|$HOME|g" {} +
cd -

cd 
echo "apply apply_settings.sh script..."
bash ~/Desktop/scheduler/config/scripts/apply_settings.sh

echo "shortcut for desktop applications on ~/Desktop..."
cd ~/Desktop
ln -s scheduler/config/prayer_times_gui.desktop ./
ln -s scheduler/config/scheduler_settings_gui.desktop ./
cd -

echo "copy icons for Desktop applications..."
cp ~/Desktop/scheduler/config/icons/athan-*.png /usr/share/icons/hicolor/48x48/apps/
sudo gtk-update-icon-cache /usr/share/icons/hicolor

echo "Enable and start audio_event_scheduler.service"
sudo cp ~/Desktop/scheduler/config/systemd/audio_event_scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable audio_event_scheduler.service
sudo systemctl start audio_event_scheduler.service

echo "Set scheduler_settings_gui.desktop as an autostart application..."
cd ~/.config/autostart/
ln -s ~/Desktop/scheduler/config/prayer_times_gui.desktop ./
cd -
