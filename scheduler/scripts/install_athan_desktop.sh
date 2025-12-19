#!/bin/bash

### 1) Create scheduler directory and the athan_start script
cat << 'EOD' > "/home/ihms/Desktop/scheduler/scripts/athan_start.sh"
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

chmod +x "/home/ihms/Desktop/scheduler/scripts/athan_start.sh"


### 2) Create the real athan.desktop inside script directory

cat << 'EOD' > "/home/ihms/Desktop/scheduler/scripts/athan.desktop"
[Desktop Entry]
Type=Application
Name=Athan Display
Comment=Open local Athan page
Exec=/home/ihms/Desktop/scheduler/scripts/athan_start.sh
Icon=web-browser
Terminal=false
Categories=Utility;
EOD

chmod +x "/home/ihms/Desktop/scheduler/scripts/athan.desktop"


### 3) Create symlink in ~/.local/share/applications

mkdir -p "/home/ihms/.local/share/applications"
rm -f "/home/ihms/.local/share/applications/athan.desktop"
ln -s "/home/ihms/Desktop/scheduler/scripts/athan.desktop" "/home/ihms/.local/share/applications/athan.desktop"


### 4) Create symlink in ~/.config/autostart

mkdir -p "/home/ihms/.config/autostart"
rm -f "/home/ihms/.config/autostart/athan.desktop"
ln -s "/home/ihms/Desktop/scheduler/scripts/athan.desktop" "/home/ihms/.config/autostart/athan.desktop"


### 5) Create symlink on Desktop (no popup)

mkdir -p "/home/ihms/Desktop"
rm -f "/home/ihms/Desktop/athan.desktop"
ln -s "/home/ihms/Desktop/scheduler/scripts/athan.desktop" "/home/ihms/Desktop/athan.desktop"



echo "✓ Athan installed successfully."
echo "✓ Script created at /home/ihms/Desktop/scheduler/scripts/athan_start.sh"
echo "✓ Desktop Entry stored at /home/ihms/Desktop/scheduler/scripts/athan.desktop"
echo "✓ Symlink added to ~/.local/share/applications/athan.desktop (menu entry)"
echo "✓ Symlink added to ~/.config/autostart/athan.desktop (autostart enabled)"
echo "✓ Symlink added to ~/Desktop/athan.desktop (no-popup launcher)"
