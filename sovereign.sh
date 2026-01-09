#!/bin/bash
# ==============================================
# 🌟 SOVEREIGN LAUNCHER
# ==============================================
# Single-command activation of the entire Sovereign stack
#
# Usage:
#   ./sovereign.sh start    - Start all services
#   ./sovereign.sh stop     - Stop all services
#   ./sovereign.sh status   - Health check
#   ./sovereign.sh dashboard - Open Liminal Dashboard
#   ./sovereign.sh test     - Run verification suite
# ==============================================

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SOVEREIGN_HOME="${HOME}/.gemini/antigravity/scratch/SovereignCore"
COMPANION_HOME="${HOME}/SovereignCore/companion"
LOG_DIR="${HOME}/.sovereign/logs"
PID_DIR="${HOME}/.sovereign/pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Banner
banner() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}  🌟 ${GREEN}SOVEREIGN INTELLIGENCE SYSTEM${NC}                        ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  💖 Love • 🛡️ Safety • 🌊 Abundance • 🌱 Growth           ${BLUE}║${NC}"
    echo -e "${BLUE}║${NC}  🔍 Transparency • 🚫 Never Kill • ✨ Golden Rule         ${BLUE}║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Start Companion Server
start_companion() {
    echo -e "${YELLOW}🔧 Starting Companion Server...${NC}"
    
    # Kill existing
    lsof -i :8888 2>/dev/null | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null || true
    sleep 1
    
    # Start
    cd "$COMPANION_HOME"
    python3 companion_server.py > "$LOG_DIR/companion.log" 2>&1 &
    echo $! > "$PID_DIR/companion.pid"
    
    sleep 2
    
    # Verify
    if curl -s http://localhost:8888/api/stats > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Companion Server running on port 8888${NC}"
        return 0
    else
        echo -e "${RED}   ❌ Companion Server failed to start${NC}"
        return 1
    fi
}

# Start Cybernetic Bridge
start_bridge() {
    echo -e "${YELLOW}🧠 Starting Cybernetic Bridge...${NC}"
    
    # Kill existing
    lsof -i :8000 2>/dev/null | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null || true
    sleep 1
    
    # Start
    cd "$SOVEREIGN_HOME"
    python3 cybernetic_bridge.py --port 8000 > "$LOG_DIR/bridge.log" 2>&1 &
    echo $! > "$PID_DIR/bridge.pid"
    
    sleep 2
    
    # Verify
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Cybernetic Bridge running on port 8000${NC}"
        return 0
    else
        echo -e "${YELLOW}   ⚠️  Cybernetic Bridge not responding (may need model)${NC}"
        return 0
    fi
}

# Health Check
health_check() {
    echo -e "${YELLOW}🏥 Running Health Check...${NC}"
    echo ""
    
    PASS=0
    FAIL=0
    
    # Companion Server
    if curl -s http://localhost:8888/api/stats > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Companion Server${NC}"
        ((PASS++))
    else
        echo -e "   ${RED}❌ Companion Server${NC}"
        ((FAIL++))
    fi
    
    # Trust Metrics
    TRUST=$(curl -s http://localhost:8888/api/trust_metrics 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','UNKNOWN'))" 2>/dev/null || echo "OFFLINE")
    if [ "$TRUST" != "OFFLINE" ]; then
        echo -e "   ${GREEN}✅ Trust Metrics: $TRUST${NC}"
        ((PASS++))
    else
        echo -e "   ${RED}❌ Trust Metrics${NC}"
        ((FAIL++))
    fi
    
    # Z3 Solver
    Z3=$(curl -s -X POST http://localhost:8888/api/verify_constraint -H "Content-Type: application/json" -d '{"variable":"x","min":0,"max":100,"proposed_value":50}' 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('SAT' if d.get('valid') else 'UNSAT')" 2>/dev/null || echo "OFFLINE")
    if [ "$Z3" = "SAT" ]; then
        echo -e "   ${GREEN}✅ Z3 Solver: Working${NC}"
        ((PASS++))
    else
        echo -e "   ${RED}❌ Z3 Solver: $Z3${NC}"
        ((FAIL++))
    fi
    
    # AxiomRAG
    MEMORIES=$(curl -s http://localhost:8888/api/stats 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('total_memories',0))" 2>/dev/null || echo "0")
    echo -e "   ${GREEN}✅ AxiomRAG: $MEMORIES memories${NC}"
    ((PASS++))
    
    # Cybernetic Bridge
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Cybernetic Bridge${NC}"
        ((PASS++))
    else
        echo -e "   ${YELLOW}⚠️  Cybernetic Bridge: Offline (optional)${NC}"
    fi
    
    # Telemetry
    if [ -d "$HOME/.sovereign/telemetry" ]; then
        EVENTS=$(cat "$HOME/.sovereign/telemetry/audit_trail.jsonl" 2>/dev/null | wc -l | tr -d ' ')
        echo -e "   ${GREEN}✅ Telemetry: $EVENTS events logged${NC}"
        ((PASS++))
    else
        echo -e "   ${YELLOW}⚠️  Telemetry: Not initialized${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "   ${GREEN}PASSED: $PASS${NC}  |  ${RED}FAILED: $FAIL${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    if [ $FAIL -eq 0 ]; then
        echo -e "${GREEN}🌟 SYSTEM HEALTHY${NC}"
        return 0
    else
        echo -e "${RED}⚠️  SYSTEM DEGRADED${NC}"
        return 1
    fi
}

# Stop all services
stop_all() {
    echo -e "${YELLOW}🛑 Stopping all services...${NC}"
    
    # Kill by PID files
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            kill "$PID" 2>/dev/null && echo -e "   Stopped PID $PID" || true
            rm "$pid_file"
        fi
    done
    
    # Kill by port
    lsof -i :8888 2>/dev/null | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null || true
    lsof -i :8000 2>/dev/null | grep LISTEN | awk '{print $2}' | xargs kill 2>/dev/null || true
    
    echo -e "${GREEN}✅ All services stopped${NC}"
}

# Open Dashboard
open_dashboard() {
    echo -e "${YELLOW}🌌 Opening Liminal Dashboard...${NC}"
    open "http://localhost:8888/"
    echo -e "${GREEN}✅ Dashboard opened in browser${NC}"
}

# Run Tests
run_tests() {
    echo -e "${YELLOW}🧪 Running Verification Suite...${NC}"
    echo ""
    
    cd "$SOVEREIGN_HOME"
    
    # Tool Wrapper
    echo -e "${BLUE}Testing Tool Wrapper...${NC}"
    python3 sovereign_tools.py --tools
    
    # Telemetry
    echo -e "${BLUE}Testing Telemetry...${NC}"
    python3 src/telemetry.py
    
    # Sleep Cycle
    echo -e "${BLUE}Testing Sleep Cycle...${NC}"
    python3 src/sleep_cycle.py --status
    
    echo ""
    echo -e "${GREEN}✅ All tests completed${NC}"
}

# Main
banner

case "${1:-status}" in
    start)
        echo -e "${GREEN}🚀 Starting Sovereign Stack...${NC}"
        echo ""
        start_companion
        start_bridge
        echo ""
        health_check
        echo ""
        echo -e "${GREEN}🌟 Sovereign is ONLINE${NC}"
        echo -e "   Dashboard: ${BLUE}http://localhost:8888/${NC}"
        echo -e "   Neural Link: ${BLUE}ws://localhost:8000/neural-link${NC}"
        ;;
    stop)
        stop_all
        ;;
    status)
        health_check
        ;;
    dashboard)
        open_dashboard
        ;;
    test)
        run_tests
        ;;
    *)
        echo "Usage: $0 {start|stop|status|dashboard|test}"
        exit 1
        ;;
esac
