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

