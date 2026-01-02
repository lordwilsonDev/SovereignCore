#!/bin/bash
# Install SovereignCore as a systemd service

set -e

echo "Installing SovereignCore systemd service..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Configuration
INSTALL_DIR="/opt/sovereigncore"
SERVICE_USER="sovereign"
SERVICE_GROUP="sovereign"

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd -r -s /bin/bash -d "$INSTALL_DIR" -m "$SERVICE_USER"
else
    echo "Service user already exists: $SERVICE_USER"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/certs"

# Copy application files
echo "Copying application files..."
cp -r . "$INSTALL_DIR/"

# Set ownership
echo "Setting ownership..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"

# Create virtual environment
echo "Creating Python virtual environment..."
su - "$SERVICE_USER" -c "cd $INSTALL_DIR && python3 -m venv .venv"
su - "$SERVICE_USER" -c "cd $INSTALL_DIR && .venv/bin/pip install --upgrade pip"
su - "$SERVICE_USER" -c "cd $INSTALL_DIR && .venv/bin/pip install -r requirements.txt"

# Copy systemd service file
echo "Installing systemd service file..."
cp sovereigncore.service /etc/systemd/system/
chmod 644 /etc/systemd/system/sovereigncore.service

# Reload systemd
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
echo "Enabling service..."
systemctl enable sovereigncore

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "  1. Configure environment: sudo nano $INSTALL_DIR/.env"
echo "  2. Update passwords in .env file"
echo "  3. Start service: sudo systemctl start sovereigncore"
echo "  4. Check status: sudo systemctl status sovereigncore"
echo "  5. View logs: sudo journalctl -u sovereigncore -f"
echo ""
echo "Service commands:"
echo "  Start:   sudo systemctl start sovereigncore"
echo "  Stop:    sudo systemctl stop sovereigncore"
echo "  Restart: sudo systemctl restart sovereigncore"
echo "  Status:  sudo systemctl status sovereigncore"
echo "  Logs:    sudo journalctl -u sovereigncore -f"
echo ""
