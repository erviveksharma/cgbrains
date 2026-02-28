#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/var/www/cgbrains"
VENV_DIR="$APP_DIR/venv"

echo "=== cgbrains: deploying update ==="

cd "$APP_DIR"

echo "Pulling latest code ..."
sudo -u www-data git pull

echo "Installing dependencies ..."
sudo -u www-data "$VENV_DIR/bin/pip" install -r requirements.txt

echo "Restarting service ..."
sudo systemctl restart cgbrains

echo "Waiting for service to start ..."
sleep 2

echo "Health check ..."
if curl -sf http://127.0.0.1:8100/health; then
    echo ""
    echo "=== Deploy successful ==="
else
    echo ""
    echo "!!! Health check failed. Check logs: sudo journalctl -u cgbrains -n 50"
    exit 1
fi
