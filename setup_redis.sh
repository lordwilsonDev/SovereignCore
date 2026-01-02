#!/bin/bash
# Setup Redis with production configuration for SovereignCore

set -e

echo "Setting up Redis for SovereignCore..."
echo ""

# Check if Redis is installed
if ! command -v redis-server &> /dev/null; then
    echo "❌ Redis is not installed"
    echo "Install with: brew install redis (macOS) or apt-get install redis (Linux)"
    exit 1
fi

echo "✓ Redis is installed"

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    REDIS_CONF_DIR="/usr/local/etc/redis"
    REDIS_DATA_DIR="/usr/local/var/db/redis"
    REDIS_LOG_DIR="/usr/local/var/log"
else
    # Linux
    REDIS_CONF_DIR="/etc/redis"
    REDIS_DATA_DIR="/var/lib/redis"
    REDIS_LOG_DIR="/var/log/redis"
fi

echo "Configuration directory: $REDIS_CONF_DIR"
echo "Data directory: $REDIS_DATA_DIR"
echo "Log directory: $REDIS_LOG_DIR"
echo ""

# Create directories if they don't exist
sudo mkdir -p "$REDIS_CONF_DIR"
sudo mkdir -p "$REDIS_DATA_DIR"
sudo mkdir -p "$REDIS_LOG_DIR"

echo "Copying configuration files..."

# Backup existing config if it exists
if [ -f "$REDIS_CONF_DIR/redis.conf" ]; then
    echo "Backing up existing redis.conf..."
    sudo cp "$REDIS_CONF_DIR/redis.conf" "$REDIS_CONF_DIR/redis.conf.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Copy new configuration
sudo cp redis.conf "$REDIS_CONF_DIR/redis.conf"
sudo cp users.acl "$REDIS_CONF_DIR/users.acl"

# Set proper permissions
sudo chmod 640 "$REDIS_CONF_DIR/redis.conf"
sudo chmod 640 "$REDIS_CONF_DIR/users.acl"

if [[ "$OSTYPE" == "darwin"* ]]; then
    sudo chown $(whoami):staff "$REDIS_CONF_DIR/redis.conf"
    sudo chown $(whoami):staff "$REDIS_CONF_DIR/users.acl"
else
    sudo chown redis:redis "$REDIS_CONF_DIR/redis.conf"
    sudo chown redis:redis "$REDIS_CONF_DIR/users.acl"
fi

echo "✓ Configuration files copied"
echo ""

echo "⚠️  IMPORTANT: Update passwords in the following files:"
echo "   1. $REDIS_CONF_DIR/redis.conf (requirepass)"
echo "   2. $REDIS_CONF_DIR/users.acl (all user passwords)"
echo "   3. .env (REDIS_PASSWORD)"
echo ""

echo "To start Redis with the new configuration:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "   brew services restart redis"
    echo "Or:"
    echo "   redis-server $REDIS_CONF_DIR/redis.conf"
else
    echo "   sudo systemctl restart redis"
    echo "Or:"
    echo "   sudo redis-server $REDIS_CONF_DIR/redis.conf"
fi

echo ""
echo "To test the connection:"
echo "   redis-cli -a <your-password> ping"
echo ""
echo "✓ Redis setup complete!"
