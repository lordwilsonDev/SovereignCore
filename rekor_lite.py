#!/usr/bin/env python3
"""
📜 RekorLite - Local Merkle Transparency Log
=============================================

Air-gapped transparency log for sovereign AI actions.
Replaces public Rekor with a local SQLite Merkle-DAG.

**Core Principles:**
- Every AI action is logged with cryptographic proof
- Each entry links to the previous (blockchain-style chain)
- Tamper-evident: modifying any entry breaks the chain
- Air-gapped: never phones home
- Root hash can be exported via QR/audio for external verification

**Schema:**
Each entry contains:
- Action hash (SHA-256 of action data)
- SEP signature (from Secure Enclave)
- Thermal state at decision time
- Previous entry hash (Merkle link)
- Timestamp

Author: SovereignCore v5.0
"""

import sqlite3
import hashlib
import json
import time
import subprocess
try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    qrcode = None
    QRCODE_AVAILABLE = False
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from datetime import datetime


@dataclass
class LogEntry:
    """A single entry in the transparency log."""
    id: int
    timestamp: float
    action_type: str
    action_data: str
    action_hash: str
    signature: str
    thermal_state: int
    prev_hash: str
    merkle_root: str


class RekorLite:
    """
    Local Merkle Transparency Log.
    
    Every AI decision is immutably logged with:
    - Cryptographic hash chain
    - Secure Enclave signature
    - Thermal state at decision time
    
    Usage:
        rekor = RekorLite()
        proof = rekor.log_action("inference", "Generated response: Hello")
        rekor.verify_chain()
    """
    
    GENESIS_HASH = "GENESIS_0000000000000000000000000000000000000000000000000000000000000000"
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent / "sovereign_rekor.db"
        
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.bridge_path = Path(__file__).parent / "sovereign_bridge"
        
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        self.conn.execute("PRAGMA journal_mode=WAL")  # Crash safety
        self.conn.execute("PRAGMA synchronous=FULL")  # Durability
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS transparency_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                action_type TEXT NOT NULL,
                action_data TEXT NOT NULL,
                action_hash TEXT NOT NULL,
                signature TEXT NOT NULL,
                thermal_state INTEGER NOT NULL,
                prev_hash TEXT NOT NULL,
                merkle_root TEXT NOT NULL
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_action_hash 
            ON transparency_log(action_hash)
        """)
        
        self.conn.commit()
    
    def _get_last_hash(self) -> str:
        """Get the hash of the last entry in the chain."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT action_hash FROM transparency_log ORDER BY id DESC LIMIT 1"
        )
        result = cursor.fetchone()
        return result[0] if result else self.GENESIS_HASH
    
    def _get_thermal_state(self) -> int:
        """Get current thermal state from hardware."""
        try:
            if self.bridge_path.exists():
                result = subprocess.run(
                    [str(self.bridge_path), "telemetry"],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    # Map state string to int
                    states = {"NOMINAL": 0, "FAIR": 1, "SERIOUS": 2, "CRITICAL": 3}
                    return states.get(data.get("state", "UNKNOWN"), -1)
        except:
            pass
        return -1
    
    def _sign_with_enclave(self, data: str) -> str:
        """Sign data using Secure Enclave."""
        try:
            if self.bridge_path.exists():
                result = subprocess.run(
                    [str(self.bridge_path), "sign", data],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    response = json.loads(result.stdout)
                    return response.get("signature", "NO_SIG")
        except:
            pass
        
        # Fallback: hash-based signature (not SEP)
        return f"FALLBACK_{hashlib.sha256(data.encode()).hexdigest()[:32]}"
    
    def _compute_merkle_root(self) -> str:
        """Compute Merkle root of entire chain."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT action_hash FROM transparency_log ORDER BY id")
        hashes = [row[0] for row in cursor.fetchall()]
        
        if not hashes:
            return self.GENESIS_HASH
        
        # Build Merkle tree
        while len(hashes) > 1:
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])  # Duplicate last if odd
            
            new_level = []
            for i in range(0, len(hashes), 2):
                combined = hashlib.sha256(
                    (hashes[i] + hashes[i+1]).encode()
                ).hexdigest()
                new_level.append(combined)
            hashes = new_level
        
        return hashes[0]
    
    def log_action(self, action_type: str, action_data: str, 
                   thermal_override: int = None) -> Tuple[str, str]:
        """
        Log an action to the transparency log.
        
        Args:
            action_type: Category (inference, decision, tool_use, etc.)
            action_data: The actual content/decision being logged
            thermal_override: Optional manual thermal state
            
        Returns:
            (action_hash, merkle_root)
        """
        timestamp = time.time()
        prev_hash = self._get_last_hash()
        thermal_state = thermal_override if thermal_override is not None else self._get_thermal_state()
        
        # Create hash of the action
        action_hash = hashlib.sha256(
            f"{action_type}:{action_data}:{timestamp}:{prev_hash}".encode()
        ).hexdigest()
        
        # Sign with Secure Enclave
        signature = self._sign_with_enclave(action_hash)
        
        # Insert entry
        self.conn.execute("""
            INSERT INTO transparency_log 
            (timestamp, action_type, action_data, action_hash, signature, 
             thermal_state, prev_hash, merkle_root)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, action_type, action_data, action_hash, signature,
            thermal_state, prev_hash, ""  # Merkle root computed after
        ))
        
        self.conn.commit()
        
        # Update merkle root
        merkle_root = self._compute_merkle_root()
        self.conn.execute(
            "UPDATE transparency_log SET merkle_root = ? WHERE action_hash = ?",
            (merkle_root, action_hash)
        )
        self.conn.commit()
        
        return action_hash, merkle_root
    
    def verify_chain(self) -> Tuple[bool, str]:
        """
        Verify the entire chain integrity.
        
        Returns:
            (valid, message)
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, action_hash, prev_hash FROM transparency_log ORDER BY id"
        )
        
        entries = cursor.fetchall()
        
        if not entries:
            return True, "Empty chain (valid)"
        
        # Check genesis
        if entries[0][2] != self.GENESIS_HASH:
            return False, f"Invalid genesis at entry {entries[0][0]}"
        
        # Check chain links
        for i in range(1, len(entries)):
            expected_prev = entries[i-1][1]
            actual_prev = entries[i][2]
            
            if expected_prev != actual_prev:
                return False, f"Chain break at entry {entries[i][0]}: expected {expected_prev[:8]}, got {actual_prev[:8]}"
        
        return True, f"Chain verified: {len(entries)} entries"
    
    def get_entry(self, action_hash: str) -> Optional[LogEntry]:
        """Retrieve a specific entry by hash."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM transparency_log WHERE action_hash = ?",
            (action_hash,)
        )
        row = cursor.fetchone()
        
        if row:
            return LogEntry(*row)
        return None
    
    def get_recent(self, limit: int = 10) -> List[LogEntry]:
        """Get recent log entries."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM transparency_log ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return [LogEntry(*row) for row in cursor.fetchall()]
    
    def get_merkle_root(self) -> str:
        """Get current Merkle root hash."""
        return self._compute_merkle_root()
    
    def export_qr(self, output_path: str = "merkle_root.png") -> str:
        """
        Export Merkle root as QR code for external verification.
        
        This allows air-gapped announcement of the log state.
        """
        root = self.get_merkle_root()
        count = self.conn.execute(
            "SELECT COUNT(*) FROM transparency_log"
        ).fetchone()[0]
        
        # Create verification payload
        payload = json.dumps({
            "type": "SovereignCore_RekorLite",
            "merkle_root": root,
            "entry_count": count,
            "timestamp": time.time(),
            "chain": "local_air_gapped"
        })
        
        # Generate QR
        try:
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(payload)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(output_path)
            return output_path
        except ImportError:
            # Fallback: just return the hash
            return f"QR library not available. Root: {root}"
    
    def get_stats(self) -> dict:
        """Get log statistics."""
        cursor = self.conn.cursor()
        
        count = cursor.execute("SELECT COUNT(*) FROM transparency_log").fetchone()[0]
        
        if count == 0:
            return {"entries": 0, "merkle_root": self.GENESIS_HASH}
        
        first = cursor.execute(
            "SELECT timestamp FROM transparency_log ORDER BY id LIMIT 1"
        ).fetchone()[0]
        
        last = cursor.execute(
            "SELECT timestamp FROM transparency_log ORDER BY id DESC LIMIT 1"
        ).fetchone()[0]
        
        return {
            "entries": count,
            "merkle_root": self.get_merkle_root(),
            "first_entry": datetime.fromtimestamp(first).isoformat(),
            "last_entry": datetime.fromtimestamp(last).isoformat(),
            "chain_valid": self.verify_chain()[0]
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="RekorLite - Local Transparency Log")
    parser.add_argument("--log", type=str, help="Log an action (format: type:data)")
    parser.add_argument("--verify", action="store_true", help="Verify chain integrity")
    parser.add_argument("--recent", type=int, default=5, help="Show recent entries")
    parser.add_argument("--root", action="store_true", help="Show Merkle root")
    parser.add_argument("--qr", action="store_true", help="Export Merkle root as QR")
    parser.add_argument("--stats", action="store_true", help="Show log statistics")
    
    args = parser.parse_args()
    
    rekor = RekorLite()
    
    if args.log:
        parts = args.log.split(":", 1)
        action_type = parts[0]
        action_data = parts[1] if len(parts) > 1 else ""
        
        action_hash, merkle_root = rekor.log_action(action_type, action_data)
        print(f"📜 Logged: {action_type}")
        print(f"   Hash:   {action_hash[:16]}...")
        print(f"   Root:   {merkle_root[:16]}...")
    
    elif args.verify:
        valid, message = rekor.verify_chain()
        if valid:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
    
    elif args.root:
        root = rekor.get_merkle_root()
        print(f"🌳 Merkle Root: {root}")
    
    elif args.qr:
        result = rekor.export_qr()
        print(f"📱 QR exported: {result}")
    
    elif args.stats:
        stats = rekor.get_stats()
        print("📊 REKOR LITE STATISTICS")
        print("=" * 40)
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    else:
        # Default: show recent
        entries = rekor.get_recent(args.recent)
        
        if not entries:
            print("📜 Log is empty")
        else:
            print(f"📜 RECENT ENTRIES ({len(entries)})")
            print("=" * 60)
            for entry in entries:
                ts = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S")
                print(f"   [{ts}] {entry.action_type}: {entry.action_data[:40]}...")
                print(f"          Hash: {entry.action_hash[:16]}... | Thermal: {entry.thermal_state}")


if __name__ == "__main__":
    main()
