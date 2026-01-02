#!/bin/bash
# SovereignCore Backup Script
# Backs up Redis data, database, and configuration files

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/sovereigncore}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="sovereigncore_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================"
echo "SovereignCore Backup Script"
echo "========================================"
echo "Timestamp: ${TIMESTAMP}"
echo "Backup directory: ${BACKUP_DIR}"
echo ""

# Create backup directory
mkdir -p "${BACKUP_PATH}"

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Backup Redis data
log "Backing up Redis data..."
if command -v redis-cli &> /dev/null; then
    # Trigger Redis save
    redis-cli BGSAVE || warn "Redis BGSAVE failed"
    sleep 2
    
    # Copy RDB file
    if [ -f /var/lib/redis/dump.rdb ]; then
        cp /var/lib/redis/dump.rdb "${BACKUP_PATH}/redis_dump.rdb"
        log "✓ Redis RDB backed up"
    else
        warn "Redis dump.rdb not found"
    fi
    
    # Copy AOF file if it exists
    if [ -f /var/lib/redis/appendonly.aof ]; then
        cp /var/lib/redis/appendonly.aof "${BACKUP_PATH}/redis_appendonly.aof"
        log "✓ Redis AOF backed up"
    fi
else
    warn "redis-cli not found, skipping Redis backup"
fi

# Backup SQLite database
log "Backing up SQLite database..."
if [ -f sovereign_rekor.db ]; then
    sqlite3 sovereign_rekor.db ".backup '${BACKUP_PATH}/sovereign_rekor.db'"
    log "✓ SQLite database backed up"
else
    warn "sovereign_rekor.db not found"
fi

# Backup configuration files
log "Backing up configuration files..."
mkdir -p "${BACKUP_PATH}/config"

# List of config files to backup
CONFIG_FILES=(
    ".env"
    "redis.conf"
    "users.acl"
    "prometheus.yml"
    "alertmanager.yml"
    "alerts.yml"
    "docker-compose.yml"
    "gunicorn.conf.py"
)

for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "${BACKUP_PATH}/config/"
        log "✓ Backed up: $file"
    fi
done

# Backup data directories
log "Backing up data directories..."
if [ -d "data" ]; then
    cp -r data "${BACKUP_PATH}/data"
    log "✓ Data directory backed up"
fi

if [ -d "mcp_data" ]; then
    cp -r mcp_data "${BACKUP_PATH}/mcp_data"
    log "✓ MCP data backed up"
fi

if [ -d "memory" ]; then
    cp -r memory "${BACKUP_PATH}/memory"
    log "✓ Memory directory backed up"
fi

# Create backup metadata
log "Creating backup metadata..."
cat > "${BACKUP_PATH}/backup_info.txt" << EOF
SovereignCore Backup Information
================================
Backup Date: $(date)
Backup Name: ${BACKUP_NAME}
Hostname: $(hostname)
Backup Contents:
- Redis data (RDB/AOF)
- SQLite database
- Configuration files
- Data directories

To restore this backup, run:
  ./restore.sh ${BACKUP_NAME}
EOF

# Compress backup
log "Compressing backup..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}"
rm -rf "${BACKUP_NAME}"
log "✓ Backup compressed: ${BACKUP_NAME}.tar.gz"

# Calculate backup size
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
log "Backup size: ${BACKUP_SIZE}"

# Clean old backups
log "Cleaning old backups (retention: ${RETENTION_DAYS} days)..."
find "${BACKUP_DIR}" -name "sovereigncore_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete
log "✓ Old backups cleaned"

# Verify backup
log "Verifying backup integrity..."
if tar -tzf "${BACKUP_NAME}.tar.gz" > /dev/null 2>&1; then
    log "✓ Backup integrity verified"
else
    error "Backup verification failed!"
    exit 1
fi

echo ""
echo "========================================"
log "✓ Backup completed successfully!"
echo "========================================"
echo "Backup file: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "Backup size: ${BACKUP_SIZE}"
echo ""

# Optional: Upload to remote storage
if [ -n "${REMOTE_BACKUP_PATH}" ]; then
    log "Uploading to remote storage..."
    # Example: rsync to remote server
    # rsync -avz "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "${REMOTE_BACKUP_PATH}/"
    # Example: AWS S3
    # aws s3 cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "s3://your-bucket/backups/"
    # Example: Google Cloud Storage
    # gsutil cp "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "gs://your-bucket/backups/"
fi

exit 0
