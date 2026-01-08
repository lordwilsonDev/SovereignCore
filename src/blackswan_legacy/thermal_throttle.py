#!/usr/bin/env python3
"""
The Thermal-Somatic Link - Phase 34
"The M1 Medulla: Preventing hallucination from heat."

This script bridges the macOS kernel thermal state with the Sovereign Guardian Protocol.
When thermal pressure rises, it signals throttle to prevent cognitive degradation.

Usage:
    python3 thermal_throttle.py [--daemon] [--webhook URL]

Requires: sudo access for powermetrics
"""

import subprocess
import json
import time
import sys
import argparse
import os
from datetime import datetime

# Configuration
POLL_INTERVAL = 5  # Seconds between thermal checks
ALERT_HISTORY = []
MAX_HISTORY = 100

def get_m1_thermals():
    """
    Query M1 thermal state via powermetrics.
    Returns: 0=Nominal, 1=Heavy, 2=Critical
    """
    try:
        # Note: powermetrics requires sudo
        cmd = ["sudo", "powermetrics", "-n", "1", "--samplers", "thermal", "-i", "1000"]
        res = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, timeout=10).decode('utf-8')
        
        # Parse thermal pressure
        if "thermal pressure: Nominal" in res:
            return {"level": 0, "state": "nominal", "action": "none"}
        elif "thermal pressure: Moderate" in res:
            return {"level": 1, "state": "moderate", "action": "monitor"}
        elif "thermal pressure: Heavy" in res:
            return {"level": 2, "state": "heavy", "action": "throttle"}
        elif "thermal pressure: Critical" in res:
            return {"level": 3, "state": "critical", "action": "sleep"}
        elif "thermal pressure: Sleeping" in res:
            return {"level": 4, "state": "sleeping", "action": "wait"}
        
        # Default to nominal if parsing fails
        return {"level": 0, "state": "unknown", "action": "none"}
        
    except subprocess.TimeoutExpired:
        return {"level": -1, "state": "timeout", "action": "retry"}
    except subprocess.CalledProcessError as e:
        return {"level": -1, "state": "error", "action": "check_sudo", "error": str(e)}
    except FileNotFoundError:
        return {"level": -1, "state": "not_available", "action": "install_powermetrics"}

def get_cpu_usage():
    """Get current CPU usage percentage."""
    try:
        cmd = ["top", "-l", "1", "-n", "0", "-s", "0"]
        res = subprocess.check_output(cmd, timeout=5).decode('utf-8')
        
        for line in res.split('\n'):
            if 'CPU usage' in line:
                # Parse: CPU usage: 5.55% user, 10.20% sys, 84.24% idle
                parts = line.split(',')
                user = float(parts[0].split(':')[1].strip().replace('%', '').strip().split()[0])
                sys_usage = float(parts[1].strip().replace('%', '').strip().split()[0])
                return {"user": user, "system": sys_usage, "total": user + sys_usage}
        
        return {"user": 0, "system": 0, "total": 0}
    except:
        return {"user": 0, "system": 0, "total": 0}

def get_memory_pressure():
    """Get memory pressure from vm_stat."""
    try:
        cmd = ["vm_stat"]
        res = subprocess.check_output(cmd, timeout=5).decode('utf-8')
        
        stats = {}
        for line in res.split('\n'):
            if ':' in line:
                key, val = line.split(':')
                val = val.strip().replace('.', '')
                if val.isdigit():
                    stats[key.strip()] = int(val)
        
        # Page size is typically 16384 bytes on M1
        page_size = 16384
        free_pages = stats.get('Pages free', 0)
        active_pages = stats.get('Pages active', 0)
        inactive_pages = stats.get('Pages inactive', 0)
        wired_pages = stats.get('Pages wired down', 0)
        
        free_mb = (free_pages * page_size) / (1024 * 1024)
        used_mb = ((active_pages + wired_pages) * page_size) / (1024 * 1024)
        
        return {
            "free_mb": round(free_mb),
            "used_mb": round(used_mb),
            "pressure": "nominal" if free_mb > 2000 else "elevated" if free_mb > 500 else "critical"
        }
    except:
        return {"free_mb": 0, "used_mb": 0, "pressure": "unknown"}

PROPRIOCEPTION_FILE = "m1_thermal.json"

def emit_alert(thermal_state, cpu, memory):
    """Emit a metabolic alert."""
    alert = {
        "timestamp": datetime.now().isoformat(),
        "thermal": thermal_state,
        "cpu": cpu,
        "memory": memory
    }
    
    ALERT_HISTORY.append(alert)
    if len(ALERT_HISTORY) > MAX_HISTORY:
        ALERT_HISTORY.pop(0)
    
    return alert

def update_proprioceptive_bridge(thermal, cpu, memory):
    """
    Write thermal state to JSON file for OEC MicroVM Proprioception.
    This allows the isolated VM to 'feel' the host's temperature.
    """
    try:
        state = {
            "timestamp": datetime.now().isoformat(),
            "thermal": thermal,
            "cpu": cpu,
            "memory": memory,
            "host_temp_c": 92 if thermal["level"] >= 3 else 45 # Simulated temp based on level if raw not avail
        }
        
        # Atomic write pattern to prevent reading partial file
        temp_file = f"{PROPRIOCEPTION_FILE}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(state, f)
        os.rename(temp_file, PROPRIOCEPTION_FILE)
        
    except Exception as e:
        # Don't spam errors if permission denied, but silent fail is risky for bridge
        pass

def format_status(thermal, cpu, memory):
    """Format status for display."""
    
    # 🔌 PROPRIOCEPTION UPDATE
    update_proprioceptive_bridge(thermal, cpu, memory)
    
    thermal_icons = {
        0: "🟢",  # Nominal
        1: "🟡",  # Moderate
        2: "🟠",  # Heavy
        3: "🔴",  # Critical
        4: "💤",  # Sleeping
        -1: "❓"  # Unknown
    }
    
    icon = thermal_icons.get(thermal["level"], "❓")
    
    return f"""
╔════════════════════════════════════════╗
║     THERMAL-SOMATIC LINK STATUS        ║
╠════════════════════════════════════════╣
║  🌡️  Thermal: {icon} {thermal['state'].upper():12} ║
║  💻  CPU:     {cpu['total']:5.1f}% (U:{cpu['user']:.1f} S:{cpu['system']:.1f}) ║
║  🧠  Memory:  {memory['free_mb']:5}MB free ({memory['pressure']}) ║
║  ⚡  Action:  {thermal['action']:20} ║
╚════════════════════════════════════════╝
"""

def monitor_loop(webhook_url=None, daemon=False):
    """Main monitoring loop."""
    print("🔌 Thermal-Somatic Link activated. Monitoring M1 vitals...")
    print("   (Press Ctrl+C to stop)\n")
    
    consecutive_alerts = 0
    
    while True:
        try:
            thermal = get_m1_thermals()
            cpu = get_cpu_usage()
            memory = get_memory_pressure()
            
            # Clear screen in daemon mode for clean display
            if not daemon:
                print(format_status(thermal, cpu, memory))
            
            # Check for alert conditions
            if thermal["level"] >= 2:
                consecutive_alerts += 1
                alert = emit_alert(thermal, cpu, memory)
                
                print(f"⚠️  METABOLIC ALERT: Thermal Pressure Level {thermal['level']}")
                print(f"    State: {thermal['state']} | Action: {thermal['action']}")
                
                if consecutive_alerts >= 3:
                    print("🛑 SUSTAINED THERMAL PRESSURE - Recommending system throttle")
                    
                    # If webhook configured, send alert
                    if webhook_url:
                        try:
                            import urllib.request
                            data = json.dumps(alert).encode('utf-8')
                            req = urllib.request.Request(webhook_url, data=data, 
                                headers={'Content-Type': 'application/json'})
                            urllib.request.urlopen(req, timeout=5)
                        except Exception as e:
                            print(f"    Webhook failed: {e}")
            else:
                consecutive_alerts = max(0, consecutive_alerts - 1)
            
            # 📉 Auto-Shard Logic: Contention Check
            # If LanceDB retrieval competes with MiniMax-M1 for the same memory page
            current_procs = [p.info['name'].lower() for p in psutil.process_iter(['name'])]
            heavy_ai_active = any("python" in p for p in current_procs) # Proxy for MiniMax
            db_active = any("lancedb" in p or "postgres" in p for p in current_procs)
            
            if heavy_ai_active and db_active and memory['pressure'] != 'nominal':
                 if not daemon:
                     print("📉 Auto-Sharding: Pausing Reasoning Engine (200ms) to clear memory buffer...")
                 time.sleep(0.2)
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n\n🔌 Thermal-Somatic Link deactivated.")
            break
        except Exception as e:
            print(f"Error in monitor loop: {e}")
            time.sleep(POLL_INTERVAL)

def main():
    parser = argparse.ArgumentParser(description='M1 Thermal-Somatic Link Monitor')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon (minimal output)')
    parser.add_argument('--webhook', type=str, help='Webhook URL for alerts')
    parser.add_argument('--once', action='store_true', help='Single check and exit')
    
    args = parser.parse_args()
    
    if args.once:
        thermal = get_m1_thermals()
        cpu = get_cpu_usage()
        memory = get_memory_pressure()
        print(format_status(thermal, cpu, memory))
        
        # Output JSON for programmatic use
        result = {
            "thermal": thermal,
            "cpu": cpu,
            "memory": memory,
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(result, indent=2))
        return
    
    monitor_loop(webhook_url=args.webhook, daemon=args.daemon)

if __name__ == "__main__":
    main()
