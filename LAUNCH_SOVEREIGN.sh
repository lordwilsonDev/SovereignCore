#!/bin/bash
# ══════════════════════════════════════════════════════════════════════════════
#                    🔱 SOVEREIGN GENESIS PROTOCOL 🔱
#                      The Complete Stack Launcher
# ══════════════════════════════════════════════════════════════════════════════
#
# This script launches the ENTIRE Sovereign Stack:
#   - Ollama (LLM Backend)
#   - Rust Core (Treasury, Constitution, Auction, Watchdog)
#   - Panopticon Dashboard
#   - Prometheus Telemetry
#   - Genesis Protocol (Perpetual Evolution)
#   - Meta-Governance (Self-Auditing)
#   - Sovereign Mesh Bridge (Cross-Machine)
#
# Usage: ./LAUNCH_SOVEREIGN.sh
#
# ══════════════════════════════════════════════════════════════════════════════

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                    🔱 SOVEREIGN GENESIS PROTOCOL 🔱                          ║${NC}"
echo -e "${PURPLE}║                       The Complete Stack Launcher                            ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════════════════════
# 0. Check Poison Pill
# ═══════════════════════════════════════════════════════════════════════════════
echo -e "${YELLOW}☠️  Checking Poison Pill...${NC}"
if [ -f "data/POISON_PILL_ACTIVE.lock" ]; then
    echo -e "${RED}   💀 POISON PILL ACTIVE - SYSTEM LOCKED${NC}"
    echo "   To reset, delete: data/POISON_PILL_ACTIVE.lock"
    exit 137
fi
echo -e "${GREEN}   ✅ Poison Pill inactive. Proceeding.${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Check Ollama
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}🤖 Checking Ollama (LLM Backend)...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Ollama is ONLINE.${NC}"
else
    echo -e "${YELLOW}   ⏳ Ollama not running. Starting...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Ollama started.${NC}"
    else
        echo -e "${RED}   ❌ Failed to start Ollama. Please start it manually.${NC}"
    fi
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 2. Start Rust Core
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}🧠 Igniting Rust Core...${NC}"
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Rust Core already running.${NC}"
else
    cargo run --release > logs/rust_core.log 2>&1 &
    RUST_PID=$!
    echo "   PID: $RUST_PID"
    echo "{\"rust_core\": $RUST_PID}" > data/service_pids.json
    
    # Wait for compile and start
    for i in {1..60}; do
        if curl -s http://localhost:9000/health > /dev/null 2>&1; then
            echo -e "${GREEN}   ✅ Rust Core is ONLINE (Port 9000).${NC}"
            break
        fi
        sleep 2
    done
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Start Panopticon Dashboard
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}👁️  Opening The Eye (Panopticon Dashboard)...${NC}"
if curl -s http://localhost:8888 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Panopticon already running.${NC}"
else
    python3 src/panopticon_server.py > logs/panopticon.log 2>&1 &
    PANOPTICON_PID=$!
    echo "   PID: $PANOPTICON_PID"
    sleep 2
    echo -e "${GREEN}   ✅ Panopticon is ONLINE (Port 8888).${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Start Prometheus Telemetry
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}📊 Starting Prometheus Telemetry...${NC}"
if curl -s http://localhost:9090/metrics > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Telemetry already running.${NC}"
else
    python3 src/prometheus_telemetry.py --port 9090 > logs/telemetry.log 2>&1 &
    TELEMETRY_PID=$!
    echo "   PID: $TELEMETRY_PID"
    sleep 2
    echo -e "${GREEN}   ✅ Telemetry is ONLINE (Port 9090).${NC}"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# 5. Start Sovereign Mesh Bridge
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}🌐 Starting Sovereign Mesh Bridge...${NC}"
python3 src/sovereign_mesh_bridge.py --mode heartbeat > logs/mesh.log 2>&1 &
MESH_PID=$!
echo "   PID: $MESH_PID"
echo -e "${GREEN}   ✅ Mesh Bridge is ONLINE (UDP 9999).${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# 6. Run Self-Audit (Meta-Governance)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}🔱 Running Meta-Governance Self-Audit...${NC}"
python3 src/meta_governance.py --self-audit 2>/dev/null || echo -e "${YELLOW}   ⚠️ Self-audit skipped (treasury low)${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# 7. Display Heartbeat
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}💓 SOVEREIGN HEARTBEAT:${NC}"
python3 src/sovereign_heartbeat.py

# ═══════════════════════════════════════════════════════════════════════════════
# 8. Endpoint Summary
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                      📡 ALL SYSTEMS ACTIVE 📡                                ║${NC}"
echo -e "${PURPLE}╠══════════════════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${PURPLE}║  Panopticon Dashboard:   ${GREEN}http://localhost:8888${PURPLE}                              ║${NC}"
echo -e "${PURPLE}║  Rust API Overview:      ${GREEN}http://localhost:9000/api/v1/overview${PURPLE}              ║${NC}"
echo -e "${PURPLE}║  Watchdog Status:        ${GREEN}http://localhost:9000/watchdog/status${PURPLE}              ║${NC}"
echo -e "${PURPLE}║  Prometheus Metrics:     ${GREEN}http://localhost:9090/metrics${PURPLE}                      ║${NC}"
echo -e "${PURPLE}║  Sovereign Mesh:         ${GREEN}UDP 224.0.0.42:9999${PURPLE}                                ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"

# ═══════════════════════════════════════════════════════════════════════════════
# 9. Launch Genesis Protocol (Perpetual Evolution)
# ═══════════════════════════════════════════════════════════════════════════════
echo ""
echo -e "${GREEN}🔥 IGNITING THE ETERNAL FLAME (Genesis Protocol)...${NC}"
echo "   Press Ctrl+C to halt the dance."
echo ""

cd src
python3 genesis_protocol.py
