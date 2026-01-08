#!/usr/bin/env python3
"""
Poison Pill System - Emergency Shutdown Protocol
Provides one-touch mechanisms to halt all system activity.

Triggers:
1. Constitutional violation with harm_level > 3
2. Merkle tamper detection
3. Thermal level >= 3 for sustained period
4. Manual activation via /nuke endpoint

Usage:
    from poison_pill import PoisonPill
    pill = PoisonPill()
    pill.activate("Merkle tamper detected")
"""

import os
import sys
import json
import signal
import subprocess
from datetime import datetime
from pathlib import Path


class PoisonPill:
    """
    Emergency shutdown system for SovereignCore.
    
    When activated:
    1. Logs the trigger reason to permanent storage
    2. Kills all Python child processes
    3. Sends SIGTERM to known service PIDs
    4. Creates a lockfile preventing restart
    5. Optionally triggers system shutdown
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.lockfile = self.base_dir / "data" / "POISON_PILL_ACTIVE.lock"
        self.log_file = self.base_dir / "data" / "poison_pill.log"
        self.pid_file = self.base_dir / "data" / "service_pids.json"
        
        self.lockfile.parent.mkdir(exist_ok=True)
    
    def is_active(self) -> bool:
        """Check if poison pill has been activated."""
        return self.lockfile.exists()
    
    def check_and_block(self):
        """
        Call this at system startup.
        If poison pill is active, refuse to start.
        """
        if self.is_active():
            with open(self.lockfile, 'r') as f:
                data = json.load(f)
            
            print("=" * 60)
            print("💀 POISON PILL ACTIVE - SYSTEM LOCKED")
            print("=" * 60)
            print(f"Activated: {data.get('timestamp')}")
            print(f"Reason: {data.get('reason')}")
            print(f"Triggered by: {data.get('triggered_by')}")
            print()
            print("To reset, manually delete:")
            print(f"  {self.lockfile}")
            print("=" * 60)
            sys.exit(137)
    
    def activate(self, reason: str, triggered_by: str = "SYSTEM"):
        """
        ACTIVATE THE POISON PILL.
        
        This will:
        1. Create lockfile
        2. Log the event
        3. Kill all managed processes
        """
        print()
        print("=" * 60)
        print("☠️  POISON PILL ACTIVATED ☠️")
        print("=" * 60)
        print(f"Reason: {reason}")
        print(f"Triggered by: {triggered_by}")
        print()
        
        timestamp = datetime.now().isoformat()
        
        # Create lockfile
        lock_data = {
            "timestamp": timestamp,
            "reason": reason,
            "triggered_by": triggered_by
        }
        with open(self.lockfile, 'w') as f:
            json.dump(lock_data, f, indent=2)
        
        # Log the event
        log_entry = {
            "event": "POISON_PILL_ACTIVATED",
            "timestamp": timestamp,
            "reason": reason,
            "triggered_by": triggered_by
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # Kill managed processes
        self._kill_processes()
        
        print("System halted. Restart requires manual lockfile removal.")
        print("=" * 60)
    
    def _kill_processes(self):
        """Kill all known child processes."""
        if self.pid_file.exists():
            try:
                with open(self.pid_file, 'r') as f:
                    pids = json.load(f)
                
                for name, pid in pids.items():
                    try:
                        os.kill(pid, signal.SIGTERM)
                        print(f"   Killed {name} (PID {pid})")
                    except ProcessLookupError:
                        print(f"   {name} (PID {pid}) already dead")
                    except PermissionError:
                        print(f"   Cannot kill {name} (PID {pid}) - permission denied")
            except Exception as e:
                print(f"   Error reading PID file: {e}")
        
        # Also try to kill by name (backup)
        try:
            subprocess.run(['pkill', '-f', 'genesis_protocol.py'], capture_output=True)
            subprocess.run(['pkill', '-f', 'panopticon_server.py'], capture_output=True)
            subprocess.run(['pkill', '-f', 'prometheus_telemetry.py'], capture_output=True)
        except:
            pass
    
    def register_pid(self, name: str, pid: int):
        """Register a service PID for tracking."""
        pids = {}
        if self.pid_file.exists():
            with open(self.pid_file, 'r') as f:
                pids = json.load(f)
        
        pids[name] = pid
        
        with open(self.pid_file, 'w') as f:
            json.dump(pids, f, indent=2)
    
    def reset(self, confirm: bool = False):
        """
        Reset the poison pill.
        Requires explicit confirmation.
        """
        if not confirm:
            print("⚠️ Poison pill reset requires confirmation.")
            print("   Call pill.reset(confirm=True) to proceed.")
            return False
        
        if self.lockfile.exists():
            os.remove(self.lockfile)
            
            log_entry = {
                "event": "POISON_PILL_RESET",
                "timestamp": datetime.now().isoformat()
            }
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + "\n")
            
            print("✅ Poison pill reset. System can restart.")
            return True
        else:
            print("Poison pill was not active.")
            return False


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Poison Pill System')
    parser.add_argument('--status', action='store_true', help='Check poison pill status')
    parser.add_argument('--reset', action='store_true', help='Reset poison pill (requires --confirm)')
    parser.add_argument('--confirm', action='store_true', help='Confirm reset')
    parser.add_argument('--activate', type=str, help='Activate poison pill with reason')
    
    args = parser.parse_args()
    
    pill = PoisonPill()
    
    if args.status:
        if pill.is_active():
            print("💀 POISON PILL IS ACTIVE")
            with open(pill.lockfile, 'r') as f:
                data = json.load(f)
            print(f"   Reason: {data.get('reason')}")
            print(f"   Time: {data.get('timestamp')}")
        else:
            print("✅ Poison pill is NOT active")
    
    elif args.reset:
        pill.reset(confirm=args.confirm)
    
    elif args.activate:
        pill.activate(args.activate, triggered_by="CLI")
    
    else:
        print("Usage: python3 poison_pill.py --status")
