#!/bin/bash
# SovereignCore Restore Script
# Restores from a backup created by backup.sh

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/sovereigncore}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "========================================"
echo "SovereignCore Restore Script"
echo "========================================"
echo ""

# Check if backup name provided
if [ -z "$1" ]; then
    echo "Usage: $0 <backup_name>"
    echo ""
    echo "Available backups:"
    ls -lh "${BACKUP_DIR}"/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_NAME="$1"
BACKUP_FILE="${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Check if backup exists
if [ ! -f "${BACKUP_FILE}" ]; then
    error "Backup file not found: ${BACKUP_FILE}"
    exit 1
fi

log "Backup file: ${BACKUP_FILE}"
log "Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)"
echo ""

# Confirmation
read -p "This will restore from backup and overwrite current data. Continue? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Restore cancelled."
    exit 0
fi

echo ""
log "Starting restore process..."

# Stop services
log "Stopping services..."
if command -v systemctl &> /dev/null; then
    systemctl stop sovereigncore || warn "Failed to stop sovereigncore service"
    systemctl stop redis || warn "Failed to stop redis service"
elif command -v docker-compose &> /dev/null; then
    docker-compose down || warn "Failed to stop docker services"
fi

# Extract backup
log "Extracting backup..."
TEMP_DIR=$(mktemp -d)
tar -xzf "${BACKUP_FILE}" -C "${TEMP_DIR}"
BACKUP_EXTRACTED="${TEMP_DIR}/${BACKUP_NAME}"

# Display backup info
if [ -f "${BACKUP_EXTRACTED}/backup_info.txt" ]; then
    echo ""
    cat "${BACKUP_EXTRACTED}/backup_info.txt"
    echo ""
fi

# Restore Redis data
log "Restoring Redis data..."
if [ -f "${BACKUP_EXTRACTED}/redis_dump.rdb" ]; then
    cp "${BACKUP_EXTRACTED}/redis_dump.rdb" /var/lib/redis/dump.rdb
    chown redis:redis /var/lib/redis/dump.rdb 2>/dev/null || true
    log "✓ Redis RDB restored"
fi

if [ -f "${BACKUP_EXTRACTED}/redis_appendonly.aof" ]; then
    cp "${BACKUP_EXTRACTED}/redis_appendonly.aof" /var/lib/redis/appendonly.aof
    chown redis:redis /var/lib/redis/appendonly.aof 2>/dev/null || true
    log "✓ Redis AOF restored"
fi

# Restore SQLite database
log "Restoring SQLite database..."
if [ -f "${BACKUP_EXTRACTED}/sovereign_rekor.db" ]; then
    cp "${BACKUP_EXTRACTED}/sovereign_rekor.db" ./sovereign_rekor.db
    log "✓ SQLite database restored"
fi

# Restore configuration files
log "Restoring configuration files..."
if [ -d "${BACKUP_EXTRACTED}/config" ]; then
    cp -r "${BACKUP_EXTRACTED}/config/"* .
    log "✓ Configuration files restored"
fi

# Restore data directories
log "Restoring data directories..."
if [ -d "${BACKUP_EXTRACTED}/data" ]; then
    rm -rf data
    cp -r "${BACKUP_EXTRACTED}/data" .
    log "✓ Data directory restored"
fi

if [ -d "${BACKUP_EXTRACTED}/mcp_data" ]; then
    rm -rf mcp_data
    cp -r "${BACKUP_EXTRACTED}/mcp_data" .
    log "✓ MCP data restored"
fi

if [ -d "${BACKUP_EXTRACTED}/memory" ]; then
    rm -rf memory
    cp -r "${BACKUP_EXTRACTED}/memory" .
    log "✓ Memory directory restored"
fi

# Set proper permissions
log "Setting permissions..."
chown -R sovereign:sovereign . 2>/dev/null || true

# Clean up
log "Cleaning up temporary files..."
rm -rf "${TEMP_DIR}"

# Start services
log "Starting services..."
if command -v systemctl &> /dev/null; then
    systemctl start redis || warn "Failed to start redis service"
    sleep 2
    systemctl start sovereigncore || warn "Failed to start sovereigncore service"
elif command -v docker-compose &> /dev/null; then
    docker-compose up -d || warn "Failed to start docker services"
fi

echo ""
echo "========================================"
log "✓ Restore completed successfully!"
echo "========================================"
echo ""
log "Verifying services..."
sleep 5

# Health check
if curl -f http://localhost:8528/health > /dev/null 2>&1; then
    log "✓ API is healthy"
else
    warn "API health check failed - please verify manually"
fi

echo ""
log "Restore complete. Please verify your data."
exit 0
