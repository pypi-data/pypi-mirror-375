#!/bin/sh

# Script to dynamically configure nginx with the correct API port

echo "🔍 Detecting NovaTrace API port..."

# List of ports to try (in order of preference)
PORTS_TO_TRY="4444 4445 4446 4447"
API_PORT=""

# Function to check if a port is open
check_port() {
    local port=$1
    nc -z host.docker.internal $port 2>/dev/null
    return $?
}

# Try each port until we find one that's listening
for port in $PORTS_TO_TRY; do
    echo "   Checking port $port..."
    if check_port $port; then
        API_PORT=$port
        echo "   ✅ Found NovaTrace API on port $port"
        break
    fi
done

# If no port found, default to 4444 and show warning
if [ -z "$API_PORT" ]; then
    echo "   ⚠️  No NovaTrace API found on any port, defaulting to 4444"
    API_PORT=4444
fi

# Generate nginx configuration with the detected port
echo "🔧 Configuring nginx for API port $API_PORT..."

cat > /etc/nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    # Logging
    log_format main '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                    '\$status \$body_bytes_sent "\$http_referer" '
                    '"\$http_user_agent" "\$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile        on;
    tcp_nopush      on;
    tcp_nodelay     on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        # Handle React Router (SPA)
        location / {
            try_files \$uri \$uri/ /index.html;
        }

        # API proxy to NovaTrace backend (dynamic port: $API_PORT)
        location /api/ {
            proxy_pass http://host.docker.internal:$API_PORT/api/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
            proxy_cache_bypass \$http_upgrade;
            proxy_connect_timeout 5s;
            proxy_send_timeout 5s;
            proxy_read_timeout 5s;
        }

        # WebSocket proxy (dynamic port: $API_PORT)
        location /ws {
            proxy_pass http://host.docker.internal:$API_PORT;
            proxy_http_version 1.1;
            proxy_set_header Upgrade \$http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Static assets caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Error pages
        error_page 404 /index.html;
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
EOF

echo "✅ Nginx configured for API port $API_PORT"
echo "🚀 Starting nginx..."

# Start nginx
exec nginx -g "daemon off;"
