#!/usr/bin/env python3
"""
Sleep Cycle - Memory Consolidation During Idle
Compresses and prunes low-value memories to maintain system health.

Usage:
    from sleep_cycle import SleepCycle
    sleep = SleepCycle()
    sleep.consolidate()  # Run during idle periods
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


class SleepCycle:
    """
    Memory consolidation system that runs during idle periods.
    
    Operations:
    1. Prune: Remove memories below value threshold
    2. Compress: Merge similar memories
    3. Archive: Move old memories to cold storage
    4. Dream: Generate synthetic experiences from patterns (see dream_engine.py)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.akashic_path = self.base_dir / "data" / "akashic_local.json"
        self.archive_path = self.base_dir / "data" / "akashic_archive.json"
        self.log_path = self.base_dir / "data" / "sleep_cycles.log"
        
        # Configuration
        self.prune_threshold = 0.3  # Memories with value < this are pruned
        self.archive_age_days = 7  # Memories older than this are archived
        self.max_active_memories = 1000  # Cap on active memories
        
        self.archive_path.parent.mkdir(exist_ok=True)
    
    def consolidate(self) -> dict:
        """
        Run the full consolidation cycle.
        
        Returns:
            Dict with stats: pruned, compressed, archived, duration
        """
        start_time = time.time()
        
        print("💤 SLEEP CYCLE: Beginning memory consolidation...")
        
        memories = self._load_memories()
        initial_count = len(memories)
        
        # Phase 1: Prune low-value memories
        memories, pruned = self._prune(memories)
        print(f"   🗑️  Pruned {pruned} low-value memories")
        
        # Phase 2: Archive old memories
        memories, archived = self._archive(memories)
        print(f"   📦 Archived {archived} old memories")
        
        # Phase 3: Compress similar memories
        memories, compressed = self._compress(memories)
        print(f"   🗜️  Compressed {compressed} similar memories")
        
        # Phase 4: Enforce cap
        memories, capped = self._enforce_cap(memories)
        if capped > 0:
            print(f"   📉 Capped {capped} excess memories")
        
        # Save consolidated memories
        self._save_memories(memories)
        
        duration = time.time() - start_time
        final_count = len(memories)
        
        result = {
            "initial_count": initial_count,
            "final_count": final_count,
            "pruned": pruned,
            "archived": archived,
            "compressed": compressed,
            "capped": capped,
            "duration_seconds": duration
        }
        
        self._log_cycle(result)
        
        print(f"   ✅ Consolidation complete: {initial_count} -> {final_count} memories ({duration:.2f}s)")
        
        return result
    
    def _load_memories(self) -> list:
        """Load memories from active storage."""
        if not self.akashic_path.exists():
            return []
        
        with open(self.akashic_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'memories' in data:
            return data['memories']
        return []
    
    def _save_memories(self, memories: list):
        """Save memories to active storage."""
        with open(self.akashic_path, 'w') as f:
            json.dump(memories, f, indent=2)
    
    def _prune(self, memories: list) -> tuple:
        """Remove memories with value below threshold."""
        kept = []
        pruned = 0
        
        for m in memories:
            value = m.get('value', m.get('confidence', 0.5))
            if value >= self.prune_threshold:
                kept.append(m)
            else:
                pruned += 1
        
        return kept, pruned
    
    def _archive(self, memories: list) -> tuple:
        """Move old memories to cold storage."""
        cutoff = datetime.now() - timedelta(days=self.archive_age_days)
        active = []
        to_archive = []
        
        for m in memories:
            timestamp = m.get('timestamp', m.get('created_at', ''))
            try:
                if isinstance(timestamp, str):
                    mem_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    if mem_time.replace(tzinfo=None) < cutoff:
                        to_archive.append(m)
                        continue
            except:
                pass
            active.append(m)
        
        # Append to archive
        if to_archive:
            existing_archive = []
            if self.archive_path.exists():
                with open(self.archive_path, 'r') as f:
                    existing_archive = json.load(f)
            
            existing_archive.extend(to_archive)
            
            with open(self.archive_path, 'w') as f:
                json.dump(existing_archive, f, indent=2)
        
        return active, len(to_archive)
    
    def _compress(self, memories: list) -> tuple:
        """Merge similar memories based on content hash."""
        # Group by content hash (first 100 chars)
        groups = defaultdict(list)
        for m in memories:
            content = str(m.get('content', m.get('key', '')))[:100]
            hash_key = hashlib.md5(content.encode()).hexdigest()[:8]
            groups[hash_key].append(m)
        
        compressed = []
        merged_count = 0
        
        for hash_key, group in groups.items():
            if len(group) == 1:
                compressed.append(group[0])
            else:
                # Merge: keep highest value, combine access counts
                best = max(group, key=lambda m: m.get('value', 0))
                best['access_count'] = sum(m.get('access_count', 1) for m in group)
                best['merged_from'] = len(group)
                compressed.append(best)
                merged_count += len(group) - 1
        
        return compressed, merged_count
    
    def _enforce_cap(self, memories: list) -> tuple:
        """Enforce maximum memory count."""
        if len(memories) <= self.max_active_memories:
            return memories, 0
        
        # Sort by value, keep top N
        memories.sort(key=lambda m: m.get('value', 0), reverse=True)
        kept = memories[:self.max_active_memories]
        capped = len(memories) - self.max_active_memories
        
        return kept, capped
    
    def _log_cycle(self, result: dict):
        """Log the consolidation cycle."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            **result
        }
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Sleep Cycle - Memory Consolidation')
    parser.add_argument('--consolidate', action='store_true', help='Run consolidation')
    parser.add_argument('--status', action='store_true', help='Show memory status')
    
    args = parser.parse_args()
    
    sleep = SleepCycle()
    
    if args.consolidate:
        sleep.consolidate()
    elif args.status:
        memories = sleep._load_memories()
        archive = []
        if sleep.archive_path.exists():
            with open(sleep.archive_path, 'r') as f:
                archive = json.load(f)
        
        print(f"📊 MEMORY STATUS")
        print(f"   Active: {len(memories)}")
        print(f"   Archived: {len(archive)}")
        print(f"   Max Active: {sleep.max_active_memories}")
    else:
        print("Usage: python3 sleep_cycle.py --consolidate")
