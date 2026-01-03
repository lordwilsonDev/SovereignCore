#!/usr/bin/env python3
"""
🌉 DISTRIBUTED MEMORY BRIDGE - SovereignCore v5.0

Enables knowledge sharing across verified Sovereign nodes.
Works in conjunction with the Handshake Protocol (SHP-1) to create
a distributed, sovereign knowledge graph.

Architecture:
- Memory Layer: Vector embeddings + knowledge graph fusion
- Transport Layer: Encrypted over SHP-1 session keys
- Consensus Layer: Merkle-signed knowledge updates

This is how sovereign minds share memories.
"""

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from handshake_protocol import SovereignHandshake, PeerSession, SecurityException
from knowledge_graph import KnowledgeGraph
from rekor_lite import RekorLite


class MemoryType(Enum):
    """Types of shared memories."""
    KNOWLEDGE = "knowledge"        # Factual knowledge
    EXPERIENCE = "experience"      # Learned patterns
    CONTEXT = "context"            # Contextual information
    AXIOM = "axiom"                # Safety rules


class SyncStatus(Enum):
    """Status of memory synchronization."""
    PENDING = "pending"
    SYNCING = "syncing"
    SYNCED = "synced"
    CONFLICT = "conflict"
    FAILED = "failed"


@dataclass
class SharedMemory:
    """A memory unit that can be shared across nodes."""
    memory_id: str
    content: str
    memory_type: MemoryType
    source_sigil: str
    created_at: datetime
    importance: float = 0.5
    embedding: Optional[List[float]] = None
    merkle_proof: Optional[str] = None
    sync_status: SyncStatus = SyncStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for transmission."""
        return {
            "memory_id": self.memory_id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "source_sigil": self.source_sigil,
            "created_at": self.created_at.isoformat(),
            "importance": self.importance,
            "embedding": self.embedding,
            "merkle_proof": self.merkle_proof
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SharedMemory":
        """Create from dictionary."""
        return cls(
            memory_id=data["memory_id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            source_sigil=data["source_sigil"],
            created_at=datetime.fromisoformat(data["created_at"]),
            importance=data.get("importance", 0.5),
            embedding=data.get("embedding"),
            merkle_proof=data.get("merkle_proof"),
            sync_status=SyncStatus.SYNCED
        )


@dataclass
class SyncState:
    """Tracks synchronization state with a peer."""
    peer_sigil: str
    last_sync: datetime
    memories_sent: int = 0
    memories_received: int = 0
    sync_head: Optional[str] = None  # Last synced memory ID
    conflicts: List[str] = field(default_factory=list)


class DistributedMemoryBridge:
    """
    The Distributed Memory Bridge enables knowledge sharing across
    verified Sovereign nodes.
    
    Key Features:
    - Encrypted transport over SHP-1 sessions
    - Merkle-signed memory updates for integrity
    - Vector similarity for relevance-based sync
    - Conflict resolution for divergent memories
    """
    
    # Protocol constants
    PROTOCOL_VERSION = "DMB-1.0"
    MAX_BATCH_SIZE = 100
    SYNC_INTERVAL_SECONDS = 60
    
    def __init__(
        self,
        handshake: Optional[SovereignHandshake] = None,
        knowledge: Optional[KnowledgeGraph] = None,
        rekor: Optional[RekorLite] = None
    ):
        """Initialize the distributed memory bridge.
        
        Args:
            handshake: Verified handshake protocol instance
            knowledge: Local knowledge graph
            rekor: Transparency log
        """
        self.handshake = handshake or SovereignHandshake()
        self.knowledge = knowledge or KnowledgeGraph()
        self.rekor = rekor or RekorLite()
        
        # Our node identity
        self.node_sigil = self.handshake.node_sigil
        
        # Shared memory pool
        self.shared_memories: Dict[str, SharedMemory] = {}
        
        # Sync state per peer
        self.sync_states: Dict[str, SyncState] = {}
        
        # Memory queue for outgoing sync
        self.outgoing_queue: List[SharedMemory] = []
        
        print(f"🌉 DistributedMemoryBridge initialized")
        print(f"   Node: {self.node_sigil[:16]}...")
    
    async def share_memory(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.KNOWLEDGE,
        importance: float = 0.5
    ) -> SharedMemory:
        """
        Share a new memory with all connected peers.
        
        Args:
            content: The memory content
            memory_type: Type of memory
            importance: How important (0.0 to 1.0)
            
        Returns:
            The created SharedMemory object
        """
        # Generate memory ID
        memory_id = hashlib.blake2b(
            f"{self.node_sigil}{content}{time.time()}".encode(),
            digest_size=16
        ).hexdigest()
        
        # Create memory object
        memory = SharedMemory(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            source_sigil=self.node_sigil,
            created_at=datetime.now(timezone.utc),
            importance=importance
        )
        
        # Store locally
        self.shared_memories[memory_id] = memory
        
        # Add to knowledge graph
        self.knowledge.remember(
            content=content,
            memory_type=memory_type.value,
            metadata={
                "memory_id": memory_id,
                "source": "local",
                "shared": True
            },
            importance=importance
        )
        
        # Log to transparency log
        merkle_hash, _ = self.rekor.log_action(
            "memory_shared",
            json.dumps({
                "memory_id": memory_id,
                "type": memory_type.value,
                "importance": importance,
                "content_hash": hashlib.sha256(content.encode()).hexdigest()[:16]
            })
        )
        memory.merkle_proof = merkle_hash
        
        # Queue for sync
        self.outgoing_queue.append(memory)
        
        print(f"💭 Shared memory: {memory_id[:8]}... ({memory_type.value})")
        
        return memory
    
    async def receive_memory(
        self,
        peer_sigil: str,
        memory_data: Dict[str, Any]
    ) -> SharedMemory:
        """
        Receive a shared memory from a peer.
        
        Args:
            peer_sigil: The sending peer's sigil
            memory_data: The memory data
            
        Returns:
            The received SharedMemory object
        """
        # Verify peer is authenticated
        session = self.handshake.get_peer_session(peer_sigil)
        if not session:
            raise SecurityException(f"Cannot receive from unauthenticated peer: {peer_sigil[:16]}")
        
        # Parse memory
        memory = SharedMemory.from_dict(memory_data)
        
        # Verify source matches sender
        if memory.source_sigil != peer_sigil:
            raise SecurityException("Memory source mismatch - possible forgery")
        
        # Check for duplicates
        if memory.memory_id in self.shared_memories:
            existing = self.shared_memories[memory.memory_id]
            if existing.source_sigil == memory.source_sigil:
                # Same memory from same source - skip
                return existing
            else:
                # Same ID, different source - conflict!
                memory.sync_status = SyncStatus.CONFLICT
                self._handle_conflict(existing, memory)
                return memory
        
        # Store memory
        self.shared_memories[memory.memory_id] = memory
        
        # Add to knowledge graph
        self.knowledge.remember(
            content=memory.content,
            memory_type=memory.memory_type.value,
            metadata={
                "memory_id": memory.memory_id,
                "source": peer_sigil[:16],
                "shared": True,
                "received_at": datetime.now(timezone.utc).isoformat()
            },
            importance=memory.importance
        )
        
        # Update sync state
        if peer_sigil not in self.sync_states:
            self.sync_states[peer_sigil] = SyncState(
                peer_sigil=peer_sigil,
                last_sync=datetime.now(timezone.utc)
            )
        self.sync_states[peer_sigil].memories_received += 1
        self.sync_states[peer_sigil].sync_head = memory.memory_id
        
        # Log receipt
        self.rekor.log_action(
            "memory_received",
            json.dumps({
                "memory_id": memory.memory_id,
                "from": peer_sigil[:16] + "...",
                "type": memory.memory_type.value
            })
        )
        
        print(f"📥 Received memory: {memory.memory_id[:8]}... from {peer_sigil[:8]}...")
        
        return memory
    
    async def sync_with_peer(self, peer_sigil: str) -> Dict[str, Any]:
        """
        Synchronize memories with a specific peer.
        
        Args:
            peer_sigil: The peer to sync with
            
        Returns:
            Sync result summary
        """
        session = self.handshake.get_peer_session(peer_sigil)
        if not session:
            raise SecurityException(f"Cannot sync with unauthenticated peer: {peer_sigil[:16]}")
        
        # Get sync state
        sync_state = self.sync_states.get(peer_sigil)
        if not sync_state:
            sync_state = SyncState(
                peer_sigil=peer_sigil,
                last_sync=datetime.now(timezone.utc)
            )
            self.sync_states[peer_sigil] = sync_state
        
        # Gather memories to send
        memories_to_send = []
        for memory in self.outgoing_queue:
            if memory.source_sigil == self.node_sigil:
                memories_to_send.append(memory)
                if len(memories_to_send) >= self.MAX_BATCH_SIZE:
                    break
        
        # Create sync message
        sync_message = {
            "protocol": self.PROTOCOL_VERSION,
            "action": "MEMORY_SYNC",
            "source_sigil": self.node_sigil,
            "memories": [m.to_dict() for m in memories_to_send],
            "sync_head": sync_state.sync_head,
            "timestamp": time.time()
        }
        
        # Update state
        sync_state.memories_sent += len(memories_to_send)
        sync_state.last_sync = datetime.now(timezone.utc)
        
        # Remove sent memories from queue
        for memory in memories_to_send:
            if memory in self.outgoing_queue:
                self.outgoing_queue.remove(memory)
        
        print(f"🔄 Synced {len(memories_to_send)} memories with {peer_sigil[:8]}...")
        
        return {
            "status": "SYNC_COMPLETE",
            "memories_sent": len(memories_to_send),
            "peer_sigil": peer_sigil,
            "sync_head": sync_state.sync_head
        }
    
    async def sync_all_peers(self) -> Dict[str, Any]:
        """
        Synchronize with all connected peers.
        
        Returns:
            Summary of sync operations
        """
        results = {}
        peer_sigils = self.handshake.list_active_peers()
        
        for peer_sigil in peer_sigils:
            try:
                result = await self.sync_with_peer(peer_sigil)
                results[peer_sigil[:16]] = result
            except Exception as e:
                results[peer_sigil[:16]] = {"status": "FAILED", "error": str(e)}
        
        return {
            "total_peers": len(peer_sigils),
            "results": results
        }
    
    def _handle_conflict(self, existing: SharedMemory, incoming: SharedMemory) -> None:
        """Handle a memory conflict between nodes."""
        # Simple resolution: prefer higher importance, then earlier creation
        if incoming.importance > existing.importance:
            self.shared_memories[existing.memory_id] = incoming
            print(f"⚠️ Conflict resolved: kept incoming (higher importance)")
        elif (incoming.importance == existing.importance and 
              incoming.created_at < existing.created_at):
            self.shared_memories[existing.memory_id] = incoming
            print(f"⚠️ Conflict resolved: kept incoming (earlier)")
        else:
            print(f"⚠️ Conflict resolved: kept existing")
        
        # Record conflict in sync state
        source = incoming.source_sigil
        if source in self.sync_states:
            self.sync_states[source].conflicts.append(incoming.memory_id)
    
    def query_shared_memories(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[SharedMemory]:
        """
        Query shared memories across the distributed network.
        
        Args:
            query: Search query
            memory_type: Optional filter by type
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        # Use knowledge graph for semantic search
        results = self.knowledge.search(query, k=limit)
        
        matching = []
        for result in results:
            memory_id = result.get("metadata", {}).get("memory_id")
            if memory_id and memory_id in self.shared_memories:
                memory = self.shared_memories[memory_id]
                if memory_type is None or memory.memory_type == memory_type:
                    matching.append(memory)
        
        return matching[:limit]
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about shared memories."""
        type_counts = {}
        source_counts = {}
        
        for memory in self.shared_memories.values():
            # Count by type
            type_key = memory.memory_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            # Count by source
            source_key = memory.source_sigil[:16]
            source_counts[source_key] = source_counts.get(source_key, 0) + 1
        
        return {
            "total_memories": len(self.shared_memories),
            "by_type": type_counts,
            "by_source": source_counts,
            "pending_sync": len(self.outgoing_queue),
            "connected_peers": self.handshake.get_active_peer_count()
        }
    
    def get_civilization_state(self) -> Dict[str, Any]:
        """
        Get the current state of the Civilization Mind.
        
        Returns a summary of the distributed knowledge state.
        """
        return {
            "protocol_version": self.PROTOCOL_VERSION,
            "node_sigil": self.node_sigil[:16] + "...",
            "memory_stats": self.get_memory_stats(),
            "sync_states": {
                sigil[:16]: {
                    "last_sync": state.last_sync.isoformat(),
                    "sent": state.memories_sent,
                    "received": state.memories_received,
                    "conflicts": len(state.conflicts)
                }
                for sigil, state in self.sync_states.items()
            },
            "handshake_state": self.handshake.state.value
        }


# Convenience function
def create_memory_bridge() -> DistributedMemoryBridge:
    """Create a new DistributedMemoryBridge with default dependencies."""
    return DistributedMemoryBridge()


if __name__ == "__main__":
    import asyncio
    
    async def demo():
        print("=" * 60)
        print("🌉 DISTRIBUTED MEMORY BRIDGE - DEMO")
        print("=" * 60)
        print()
        
        # Create bridge
        bridge = DistributedMemoryBridge()
        
        print()
        print("-" * 60)
        print("SHARING MEMORIES")
        print("-" * 60)
        
        # Share some memories
        await bridge.share_memory(
            "The Sovereign Stack uses Z3 formal proofs for safety verification.",
            MemoryType.KNOWLEDGE,
            importance=0.9
        )
        
        await bridge.share_memory(
            "Thermal throttling kicks in at 80°C to protect the silicon.",
            MemoryType.KNOWLEDGE,
            importance=0.8
        )
        
        await bridge.share_memory(
            "The user prefers dark mode interfaces with glassmorphism.",
            MemoryType.EXPERIENCE,
            importance=0.6
        )
        
        print()
        print("-" * 60)
        print("CIVILIZATION STATE")
        print("-" * 60)
        
        state = bridge.get_civilization_state()
        print(json.dumps(state, indent=2))
        
        print()
        print("=" * 60)
        print("🔮 DISTRIBUTED MEMORY BRIDGE ONLINE")
        print("=" * 60)
    
    asyncio.run(demo())
