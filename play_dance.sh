#!/bin/bash
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║             🎭 SOVEREIGN DANCE PROTOCOL v5.0 🎭                              ║"
echo "║                 Full Stack Activation                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"

# Ensure Ollama is running
echo ""
echo "🤖 Checking Ollama (LLM Backend)..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is ONLINE."
else
    echo "   ⚠️ Ollama not detected. Starting Ollama..."
    ollama serve > sovereign_ollama.log 2>&1 &
    sleep 2
fi

# 1. Start Rust SovereignCore (Upper Brain, Treasury, Constitution, Auction, Watchdog, API)
echo ""
echo "🧠 Igniting Rust Core (Actix-Web Server)..."
cd src
cargo run > ../sovereign_rust.log 2>&1 &
RUST_PID=$!
cd ..
echo "   PID: $RUST_PID"

# Wait for Rust to compile and start
echo "   (Waiting for Rust to compile...)"
sleep 10

# Health Check
if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo "   ✅ Rust Core is ONLINE (Port 9000)."
else
    echo "   ⚠️ Rust Core not responding yet. Check sovereign_rust.log."
fi

# 2. Start Panopticon Dashboard (The Eye)
echo ""
echo "👁️  Opening The Eye (Panopticon Dashboard)..."
python3 src/panopticon_server.py > sovereign_panopticon.log 2>&1 &
PAN_PID=$!
echo "   PID: $PAN_PID"

# Wait for Python server
sleep 2
if curl -s http://localhost:8888 > /dev/null 2>&1; then
    echo "   ✅ Panopticon is ONLINE (Port 8888)."
else
    echo "   ⚠️ Panopticon not responding yet. Check sovereign_panopticon.log."
fi

# Display Access Info
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                 📡 SYSTEM ENDPOINTS ACTIVE 📡                                ║"
echo "╠══════════════════════════════════════════════════════════════════════════════╣"
echo "║  Panopticon Dashboard:  http://localhost:8888                                ║"
echo "║  Rust API Overview:     http://localhost:9000/api/v1/overview                ║"
echo "║  Watchdog Status:       http://localhost:9000/watchdog/status                ║"
echo "║  Health Check:          http://localhost:9000/health                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 3. Start Genesis Engine (The Soul) in Perpetual Mode
echo "🔥 IGNITING THE ETERNAL FLAME (Genesis Protocol - Perpetual Evolution)..."
echo "   (Press Ctrl+C to end the dance)"
echo ""
python3 src/genesis_protocol.py --perpetual

# Cleanup on exit (triggered by Ctrl+C)
echo ""
echo "🛑 CURTAIN CALL (Stopping Servers)..."
kill $RUST_PID 2>/dev/null
kill $PAN_PID 2>/dev/null
echo "   Goodbye."
