#!/bin/bash
bash ./apply_settings.sh

cd ~/Desktop
ln -s scheduler/config/prayer_times_gui.desktop ./
ln -s scheduler/config/scheduler_settings_gui.desktop ./
cd -

cp ~/Desktop/scheduler/config/icons/athan-*.png /usr/share/icons/hicolor/48x48/apps/
sudo gtk-update-icon-cache /usr/share/icons/hicolor

sudo cp ~/Desktop/scheduler/config/systemd/audio_event_scheduler.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable audio_event_scheduler.service
sudo systemctl start audio_event_scheduler.service

cd ~/.config/autostart/
ln -s ~/Desktop/scheduler/config/scheduler_settings_gui.desktop ./

