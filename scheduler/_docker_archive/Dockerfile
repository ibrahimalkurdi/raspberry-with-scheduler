FROM alpine:3.18

# Install Nginx, bash, and tzdata
RUN apk add --no-cache nginx bash tzdata \
    && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && echo "Europe/Berlin" > /etc/timezone

# Set timezone
ENV TZ=Europe/Berlin

# Copy Nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Copy static site files
COPY index.html prayer_times_js_map.list /var/www/html/

# Expose port
EXPOSE 80

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]

