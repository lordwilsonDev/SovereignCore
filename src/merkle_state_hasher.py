#!/usr/bin/env python3
"""
Merkle State Hasher - Tamper-Evident State Snapshots
Creates cryptographic hashes of the world state for immutable history.

Usage:
    from merkle_state_hasher import MerkleStateHasher
    hasher = MerkleStateHasher()
    hash = hasher.snapshot_state()
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

class MerkleStateHasher:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.world_state_path = self.base_dir / "world_state.json"
        self.snapshot_log_path = self.base_dir / "data" / "merkle_snapshots.log"
        self.snapshot_log_path.parent.mkdir(exist_ok=True)
    
    def compute_merkle_root(self, data: dict) -> str:
        """
        Compute SHA-256 hash of the entire state dictionary.
        For a true Merkle tree, you'd hash each field and combine.
        This simplified version hashes the canonical JSON representation.
        """
        # Canonical JSON: sorted keys, no whitespace
        canonical = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    
    def load_world_state(self) -> dict:
        """Load the current world state from disk."""
        if not self.world_state_path.exists():
            return {"error": "world_state.json not found"}
        
        with open(self.world_state_path, 'r') as f:
            return json.load(f)
    
    def snapshot_state(self) -> dict:
        """
        Take a snapshot of the current world state.
        Returns a signed snapshot record.
        """
        state = self.load_world_state()
        
        if "error" in state:
            return state
        
        merkle_root = self.compute_merkle_root(state)
        timestamp = datetime.now().isoformat()
        
        snapshot = {
            "timestamp": timestamp,
            "merkle_root": merkle_root,
            "generation": state.get("generation", 0),
            "age": state.get("age", "UNKNOWN"),
            "system_mass": state.get("system_mass", 0),
            "ascended_masters": state.get("ascended_masters", 0)
        }
        
        # Append to log
        self._append_to_log(snapshot)
        
        print(f"📜 MERKLE SNAPSHOT: {merkle_root[:16]}...")
        print(f"   Generation: {snapshot['generation']}, Mass: {snapshot['system_mass']}")
        
        return snapshot
    
    def _append_to_log(self, snapshot: dict):
        """Append snapshot to the immutable log."""
        with open(self.snapshot_log_path, 'a') as f:
            f.write(json.dumps(snapshot) + "\n")
    
    def verify_state(self) -> bool:
        """
        Verify current state against the last snapshot.
        Returns True if state is consistent, False if tampered.
        """
        state = self.load_world_state()
        current_hash = self.compute_merkle_root(state)
        
        if not self.snapshot_log_path.exists():
            print("⚠️ No snapshots to verify against.")
            return True
        
        # Read last snapshot
        with open(self.snapshot_log_path, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return True
        
        last_snapshot = json.loads(lines[-1])
        last_hash = last_snapshot['merkle_root']
        
        if current_hash == last_hash:
            print("✅ STATE VERIFIED: Merkle root matches last snapshot.")
            return True
        else:
            print("🚨 STATE MISMATCH: Current state differs from last snapshot!")
            print(f"   Expected: {last_hash[:16]}...")
            print(f"   Got:      {current_hash[:16]}...")
            return False
    
    def get_snapshot_history(self, limit=10) -> list:
        """Return the last N snapshots."""
        if not self.snapshot_log_path.exists():
            return []
        
        with open(self.snapshot_log_path, 'r') as f:
            lines = f.readlines()
        
        snapshots = [json.loads(line) for line in lines[-limit:]]
        return snapshots


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Merkle State Hasher')
    parser.add_argument('--snapshot', action='store_true', help='Take a snapshot')
    parser.add_argument('--verify', action='store_true', help='Verify current state')
    parser.add_argument('--history', type=int, default=0, help='Show last N snapshots')
    
    args = parser.parse_args()
    
    hasher = MerkleStateHasher()
    
    if args.snapshot:
        hasher.snapshot_state()
    elif args.verify:
        hasher.verify_state()
    elif args.history > 0:
        history = hasher.get_snapshot_history(args.history)
        for s in history:
            print(f"[{s['timestamp']}] Gen {s['generation']} | {s['merkle_root'][:16]}...")
    else:
        # Default: snapshot
        hasher.snapshot_state()
