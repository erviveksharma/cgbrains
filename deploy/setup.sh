#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/cyberglobes/cgbrains.git"
APP_DIR="/var/www/cgbrains"
VENV_DIR="$APP_DIR/venv"

echo "=== cgbrains: one-time server setup ==="

# 1. Clone repo
if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repo to $APP_DIR ..."
    sudo mkdir -p "$APP_DIR"
    sudo chown www-data:www-data "$APP_DIR"
    sudo -u www-data git clone "$REPO_URL" "$APP_DIR"
else
    echo "$APP_DIR already exists, skipping clone."
fi

# 2. Python venv + deps
echo "Creating Python venv ..."
sudo -u www-data python3 -m venv "$VENV_DIR"
sudo -u www-data "$VENV_DIR/bin/pip" install --upgrade pip
sudo -u www-data "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

# 3. .env file
if [ ! -f "$APP_DIR/.env" ]; then
    echo ""
    echo ">>> Create $APP_DIR/.env with your config (AZURE_OPENAI_API_KEY, QDRANT_URL, etc.)"
    echo ">>> Then re-run this script or start the service manually."
    sudo cp "$APP_DIR/deploy/.env.example" "$APP_DIR/.env" 2>/dev/null || \
        sudo touch "$APP_DIR/.env"
    sudo chown www-data:www-data "$APP_DIR/.env"
    sudo chmod 600 "$APP_DIR/.env"
    echo "Created $APP_DIR/.env — please edit it now."
    read -rp "Press Enter when .env is configured ..."
fi

# 4. systemd unit
echo "Installing systemd service ..."
sudo cp "$APP_DIR/deploy/cgbrains.service" /etc/systemd/system/cgbrains.service
sudo systemctl daemon-reload
sudo systemctl enable cgbrains
sudo systemctl start cgbrains

# 5. nginx config
echo "Installing nginx config ..."
sudo cp "$APP_DIR/deploy/nginx.conf" /etc/nginx/sites-available/cgbrains
sudo ln -sf /etc/nginx/sites-available/cgbrains /etc/nginx/sites-enabled/cgbrains
sudo nginx -t
sudo systemctl reload nginx

# 6. SSL via certbot
echo "Obtaining SSL certificate ..."
sudo certbot --nginx -d cgbrains.cyberglobes.ai

echo ""
echo "=== Setup complete ==="
echo "Verify: sudo systemctl status cgbrains"
echo "Verify: curl https://cgbrains.cyberglobes.ai/health"
