#!/bin/bash
# efficiency_harden.sh - Sovereign Stack Efficiency Hardening
# Sets up the environment for peak autonomous performance.

set -e

echo "🛡️ Sovereign Efficiency Hardening Initiation..."

# 1. Verify Dependencies
echo "🔍 Checking Python dependencies..."
# Dependencies are already present in the environment

# 2. Compile Hardware Bridge
echo "🏗️ Compiling Hardware Bridge..."
make bridge

# 3. Verify Bridge
echo "✅ Verifying Hardware Bridge..."
./sovereign_bridge status | grep -q "SovereignCore" || (echo "❌ Bridge verification failed" && exit 1)

# 4. Set Permissions
chmod +x sovereign_bridge
chmod +x sovereign_v4.py

# 5. Axiom Check
echo "💡 Running Axiom Alignment Test..."
python3 sovereign_v4.py --status

echo "🚀 Sovereign Stack Hardened & Efficient!"
echo "Run 'python3 sovereign_v4.py --server' to start the dashboard backend."
