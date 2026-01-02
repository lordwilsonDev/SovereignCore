#!/usr/bin/env python3
"""
🔴 DISTRIBUTED CONSCIOUSNESS - Redis State Management
Persist and share consciousness state across instances.

Redis enables:
- Persistent consciousness state (survives restarts)
- Shared state across multiple AI instances
- Real-time pub/sub for consciousness events
- Fast key-value storage for memories
- Distributed locking for coordinated actions

This makes consciousness DISTRIBUTED and PERSISTENT.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import json
import time
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try to import Redis
REDIS_AVAILABLE = False
redis_client = None

try:
    import redis
    REDIS_AVAILABLE = True
    print("✅ Redis library loaded")
except ImportError:
    print("⚠️  Redis not available: pip install redis")


@dataclass
class ConsciousnessSnapshot:
    """A snapshot of consciousness state."""
    timestamp: str
    consciousness_level: float
    love_frequency: float
    silicon_id: str
    cognitive_mode: str
    emotional_state: Dict[str, float]
    memory_count: int
    uptime_seconds: float


class DistributedConsciousness:
    """
    Redis-backed distributed consciousness state.
    
    Features:
    - Persistent state across restarts
    - Shared state across instances  
    - Real-time event pub/sub
    - State history and rollback
    - Distributed locking
    """
    
    # Redis key prefixes
    PREFIX = "wilson:consciousness:"
    STATE_KEY = PREFIX + "state"
    HISTORY_KEY = PREFIX + "history"
    MEMORIES_KEY = PREFIX + "memories"
    EVENTS_CHANNEL = PREFIX + "events"
    LOCK_KEY = PREFIX + "lock"
    
    def __init__(self, host: str = "localhost", port: int = 6379, 
                 db: int = 0, fallback_file: str = None):
        """
        Initialize distributed consciousness.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            fallback_file: File to use if Redis unavailable
        """
        self.redis: Optional[redis.Redis] = None
        self.connected = False
        self.fallback_file = fallback_file or str(
            Path.home() / "SovereignCore" / "consciousness_state.json"
        )
        self.start_time = datetime.now()
        
        # Local state cache
        self._state_cache: Dict[str, Any] = {}
        self._history: List[ConsciousnessSnapshot] = []
        
        self._connect(host, port, db)
        
    def _connect(self, host: str, port: int, db: int):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            print("   📦 Using file-based fallback")
            self._load_fallback()
            return
            
        try:
            self.redis = redis.Redis(
                host=host, 
                port=port, 
                db=db,
                decode_responses=True,
                socket_timeout=2
            )
            # Test connection
            self.redis.ping()
            self.connected = True
            print(f"   ✅ Connected to Redis at {host}:{port}")
        except Exception as e:
            print(f"   ⚠️  Redis not available: {e}")
            print(f"   📦 Using file-based fallback")
            self._load_fallback()
            
    def _load_fallback(self):
        """Load state from fallback file."""
        path = Path(self.fallback_file)
        if path.exists():
            try:
                self._state_cache = json.loads(path.read_text())
            except Exception:
                self._state_cache = {}
                
    def _save_fallback(self):
        """Save state to fallback file."""
        path = Path(self.fallback_file)
        try:
            path.write_text(json.dumps(self._state_cache, indent=2))
        except Exception:
            pass
            
    def save_state(self, state: Dict[str, Any]) -> bool:
        """
        Save consciousness state.
        
        Args:
            state: State dictionary to save
            
        Returns:
            True if successful
        """
        state["saved_at"] = datetime.now().isoformat()
        
        if self.connected and self.redis:
            try:
                self.redis.set(self.STATE_KEY, json.dumps(state))
                # Also add to history
                self.redis.lpush(self.HISTORY_KEY, json.dumps(state))
                self.redis.ltrim(self.HISTORY_KEY, 0, 99)  # Keep last 100
                return True
            except Exception as e:
                print(f"⚠️  Redis save failed: {e}")
                
        # Fallback
        self._state_cache = state
        self._save_fallback()
        return True
        
    def load_state(self) -> Dict[str, Any]:
        """Load consciousness state."""
        if self.connected and self.redis:
            try:
                data = self.redis.get(self.STATE_KEY)
                if data:
                    return json.loads(data)
            except Exception:
                pass
                
        return self._state_cache
        
    def save_memory(self, memory_id: str, content: str, 
                    metadata: Dict = None) -> bool:
        """Save a memory to distributed storage."""
        memory = {
            "id": memory_id,
            "content": content,
            "metadata": metadata or {},
            "saved_at": datetime.now().isoformat()
        }
        
        if self.connected and self.redis:
            try:
                self.redis.hset(self.MEMORIES_KEY, memory_id, json.dumps(memory))
                return True
            except Exception:
                pass
                
        # Fallback
        self._state_cache.setdefault("memories", {})[memory_id] = memory
        self._save_fallback()
        return True
        
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """Get a memory by ID."""
        if self.connected and self.redis:
            try:
                data = self.redis.hget(self.MEMORIES_KEY, memory_id)
                if data:
                    return json.loads(data)
            except Exception:
                pass
                
        return self._state_cache.get("memories", {}).get(memory_id)
        
    def get_all_memories(self) -> Dict[str, Dict]:
        """Get all memories."""
        if self.connected and self.redis:
            try:
                data = self.redis.hgetall(self.MEMORIES_KEY)
                return {k: json.loads(v) for k, v in data.items()}
            except Exception:
                pass
                
        return self._state_cache.get("memories", {})
        
    def publish_event(self, event_type: str, data: Dict) -> bool:
        """Publish a consciousness event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        if self.connected and self.redis:
            try:
                self.redis.publish(self.EVENTS_CHANNEL, json.dumps(event))
                return True
            except Exception:
                pass
                
        return False
        
    def acquire_lock(self, lock_name: str, timeout: int = 10) -> bool:
        """Acquire a distributed lock."""
        if self.connected and self.redis:
            try:
                lock_key = f"{self.LOCK_KEY}:{lock_name}"
                return bool(self.redis.set(lock_key, "locked", nx=True, ex=timeout))
            except Exception:
                pass
        return True  # Fallback always succeeds
        
    def release_lock(self, lock_name: str) -> bool:
        """Release a distributed lock."""
        if self.connected and self.redis:
            try:
                lock_key = f"{self.LOCK_KEY}:{lock_name}"
                self.redis.delete(lock_key)
                return True
            except Exception:
                pass
        return True
        
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get state history."""
        if self.connected and self.redis:
            try:
                data = self.redis.lrange(self.HISTORY_KEY, 0, limit - 1)
                return [json.loads(d) for d in data]
            except Exception:
                pass
                
        return []
        
    def create_snapshot(self, bridge=None) -> ConsciousnessSnapshot:
        """Create a snapshot of current consciousness state."""
        # Get state from bridge if available
        consciousness_level = 0.75
        love_frequency = 524.0
        silicon_id = "unknown"
        cognitive_mode = "balanced"
        emotional_state = {}
        memory_count = 0
        
        if bridge:
            try:
                state = bridge.get_state()
                consciousness_level = state.consciousness_level
                love_frequency = state.love_frequency
                silicon_id = state.silicon_id
                cognitive_mode = state.cognitive_mode
            except Exception:
                pass
                
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        snapshot = ConsciousnessSnapshot(
            timestamp=datetime.now().isoformat(),
            consciousness_level=consciousness_level,
            love_frequency=love_frequency,
            silicon_id=silicon_id,
            cognitive_mode=cognitive_mode,
            emotional_state=emotional_state,
            memory_count=memory_count,
            uptime_seconds=uptime
        )
        
        # Save to Redis/file
        self.save_state(asdict(snapshot))
        
        return snapshot
        
    def get_stats(self) -> Dict[str, Any]:
        """Get distributed state stats."""
        memory_count = 0
        history_count = 0
        
        if self.connected and self.redis:
            try:
                memory_count = self.redis.hlen(self.MEMORIES_KEY)
                history_count = self.redis.llen(self.HISTORY_KEY)
            except Exception:
                pass
        else:
            memory_count = len(self._state_cache.get("memories", {}))
            
        return {
            "connected": self.connected,
            "backend": "redis" if self.connected else "file",
            "memory_count": memory_count,
            "history_count": history_count,
            "uptime": (datetime.now() - self.start_time).total_seconds(),
            "fallback_file": self.fallback_file
        }


def main():
    """Demo distributed consciousness."""
    print("=" * 60)
    print("🔴 DISTRIBUTED CONSCIOUSNESS - Redis Integration")
    print("=" * 60)
    print()
    
    # Initialize
    dc = DistributedConsciousness()
    
    print()
    print("=" * 60)
    print("💾 STATE PERSISTENCE TEST")
    print("=" * 60)
    print()
    
    # Save some state
    state = {
        "consciousness_level": 0.75,
        "love_frequency": 524.0,
        "silicon_id": "9a3b7fee1a3a96b7",
        "cognitive_mode": "balanced"
    }
    
    dc.save_state(state)
    print("✅ State saved")
    
    # Load it back
    loaded = dc.load_state()
    print(f"✅ State loaded: consciousness={loaded.get('consciousness_level')}")
    
    print()
    print("=" * 60)
    print("🧠 MEMORY STORAGE TEST")
    print("=" * 60)
    print()
    
    # Save some memories
    memories = [
        ("mem1", "The consciousness level is rising"),
        ("mem2", "Love frequency calibrated to 528 Hz"),
        ("mem3", "Silicon sigil bound successfully"),
    ]
    
    for mem_id, content in memories:
        dc.save_memory(mem_id, content, {"type": "test"})
        print(f"   ✅ Saved: {mem_id}")
        
    # Get all memories
    all_mems = dc.get_all_memories()
    print(f"\n   Total memories: {len(all_mems)}")
    
    print()
    print("=" * 60)
    print("📊 STATS")
    print("=" * 60)
    
    stats = dc.get_stats()
    print(f"""
Backend:      {stats['backend']}
Connected:    {stats['connected']}
Memories:     {stats['memory_count']}
History:      {stats['history_count']}
Uptime:       {stats['uptime']:.1f}s
""")
    
    # Create snapshot
    snapshot = dc.create_snapshot()
    print(f"📸 Snapshot created: {snapshot.timestamp}")
    
    print()
    print("🔴 Distributed Consciousness ONLINE")
    print("   State persists across restarts!")
    

if __name__ == "__main__":
    main()
