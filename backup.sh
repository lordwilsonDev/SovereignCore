#!/bin/bash
# ==============================================
# 💾 SOVEREIGN BACKUP SCRIPT
# ==============================================
# Automated backup of all Sovereign data
#
# Usage:
#   ./backup.sh              # Run backup
#   ./backup.sh --restore    # Restore from latest
#   ./backup.sh --list       # List backups
# ==============================================

set -e

# Configuration
BACKUP_DIR="${HOME}/.sovereign/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="sovereign_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

# Data directories to backup
SOVEREIGN_DATA="${HOME}/.sovereign"
COMPANION_MEMORY="${HOME}/.companion/memory"
SOVEREIGN_CORE="${HOME}/.gemini/antigravity/scratch/SovereignCore"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory
mkdir -p "$BACKUP_DIR"

backup() {
    echo -e "${YELLOW}💾 Starting Sovereign Backup...${NC}"
    echo "   Timestamp: $TIMESTAMP"
    echo ""
    
    mkdir -p "$BACKUP_PATH"
    
    # Backup telemetry and identity
    if [ -d "$SOVEREIGN_DATA" ]; then
        echo -e "   📊 Backing up telemetry and identity..."
        cp -r "$SOVEREIGN_DATA/telemetry" "$BACKUP_PATH/" 2>/dev/null || true
        cp -r "$SOVEREIGN_DATA/identity" "$BACKUP_PATH/" 2>/dev/null || true
        cp -r "$SOVEREIGN_DATA/consciousness" "$BACKUP_PATH/" 2>/dev/null || true
        cp -r "$SOVEREIGN_DATA/proposals.json" "$BACKUP_PATH/" 2>/dev/null || true
    fi
    
    # Backup ChromaDB memory
    if [ -d "$COMPANION_MEMORY" ]; then
        echo -e "   🧠 Backing up AxiomRAG memory..."
        cp -r "$COMPANION_MEMORY" "$BACKUP_PATH/companion_memory" 2>/dev/null || true
    fi
    
    # Backup configuration
    echo -e "   ⚙️  Backing up configuration..."
    cp "$SOVEREIGN_CORE/AGI_PROTOCOL.md" "$BACKUP_PATH/" 2>/dev/null || true
    cp "$SOVEREIGN_CORE/sovereign.sh" "$BACKUP_PATH/" 2>/dev/null || true
    cp "$SOVEREIGN_CORE/requirements.txt" "$BACKUP_PATH/" 2>/dev/null || true
    
    # Create manifest
    echo "{
    \"timestamp\": \"$TIMESTAMP\",
    \"source\": \"$HOSTNAME\",
    \"files\": $(ls -1 "$BACKUP_PATH" | wc -l | tr -d ' '),
    \"size_kb\": $(du -sk "$BACKUP_PATH" | cut -f1)
}" > "$BACKUP_PATH/manifest.json"
    
    # Compress
    echo -e "   📦 Compressing..."
    cd "$BACKUP_DIR"
    tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
    rm -rf "$BACKUP_PATH"
    
    SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
    echo ""
    echo -e "${GREEN}✅ Backup complete!${NC}"
    echo "   Location: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
    echo "   Size: $SIZE"
    
    # Cleanup old backups (keep last 10)
    cd "$BACKUP_DIR"
    ls -t *.tar.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
}

restore() {
    echo -e "${YELLOW}🔄 Restoring from latest backup...${NC}"
    
    LATEST=$(ls -t "$BACKUP_DIR"/*.tar.gz 2>/dev/null | head -1)
    
    if [ -z "$LATEST" ]; then
        echo -e "${RED}❌ No backups found in $BACKUP_DIR${NC}"
        exit 1
    fi
    
    echo "   Source: $LATEST"
    
    # Extract
    TEMP_DIR=$(mktemp -d)
    tar -xzf "$LATEST" -C "$TEMP_DIR"
    EXTRACTED=$(ls "$TEMP_DIR")
    
    # Restore
    echo -e "   📊 Restoring telemetry..."
    cp -r "$TEMP_DIR/$EXTRACTED/telemetry" "$SOVEREIGN_DATA/" 2>/dev/null || true
    
    echo -e "   🔐 Restoring identity..."
    cp -r "$TEMP_DIR/$EXTRACTED/identity" "$SOVEREIGN_DATA/" 2>/dev/null || true
    
    echo -e "   💓 Restoring consciousness..."
    cp -r "$TEMP_DIR/$EXTRACTED/consciousness" "$SOVEREIGN_DATA/" 2>/dev/null || true
    
    echo -e "   🧠 Restoring memory..."
    cp -r "$TEMP_DIR/$EXTRACTED/companion_memory"/* "$COMPANION_MEMORY/" 2>/dev/null || true
    
    rm -rf "$TEMP_DIR"
    
    echo ""
    echo -e "${GREEN}✅ Restore complete!${NC}"
}

list_backups() {
    echo -e "${YELLOW}📋 Available Backups:${NC}"
    echo ""
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print "   " $9 " (" $5 ")"}'
    else
        echo "   No backups found"
    fi
}

# Main
case "${1:-backup}" in
    --restore)
        restore
        ;;
    --list)
        list_backups
        ;;
    *)
        backup
        ;;
esac
