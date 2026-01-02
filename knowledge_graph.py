#!/usr/bin/env python3
"""
🧠 Knowledge Graph - Persistent Memory for SovereignCore
========================================================

The Memory Layer that never forgets.
Stores embeddings, relationships, and conversation history.

Features:
- Vector similarity search
- Episodic memory (conversations)
- Semantic memory (concepts)
- Graph relationships
- Local persistence (no cloud needed!)

Kind Messages Enabled 💜
"""

import os
import json
import sqlite3
import hashlib
import math
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

# =============================================================================
# KIND MESSAGES
# =============================================================================

MEMORY_MESSAGES = {
    "init": "🧠 Knowledge Graph awakening... memories loading...",
    "ready": "✨ Memory is ready! I remember {count} things.",
    "storing": "💾 Storing new memory: {preview}...",
    "stored": "✅ Memory saved! ID: {id}",
    "searching": "🔍 Searching memories for: {query}...",
    "found": "💡 Found {count} related memories!",
    "not_found": "🤔 Hmm, I don't remember anything about that yet.",
    "connecting": "🔗 Creating connection: {source} ↔ {target}",
    "forgetting": "🗑️ Letting go of old memory: {id}",
    "stats": "📊 Memory stats: {memories} memories, {connections} connections"
}

def memory_print(message_key: str, **kwargs):
    """Print a thoughtful memory message."""
    msg = MEMORY_MESSAGES.get(message_key, message_key)
    print(f"[Memory] {msg.format(**kwargs)}")


# =============================================================================
# MEMORY TYPES
# =============================================================================

@dataclass
class Memory:
    """A single memory unit."""
    id: str
    content: str
    embedding: List[float]
    memory_type: str  # "episodic", "semantic", "procedural"
    metadata: Dict[str, Any]
    created_at: str
    accessed_at: str
    access_count: int = 0
    importance: float = 0.5
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Memory":
        return cls(**data)


@dataclass
class Connection:
    """A relationship between memories."""
    source_id: str
    target_id: str
    relationship: str  # "related_to", "caused_by", "part_of", "similar_to"
    strength: float = 1.0
    created_at: str = ""


# =============================================================================
# SIMPLE EMBEDDER (No external dependencies)
# =============================================================================

class SimpleEmbedder:
    """
    Creates embeddings from text using simple techniques.
    For production, replace with Sentence Transformers or similar.
    """
    
    def __init__(self, dim: int = 64):
        self.dim = dim
        # Simple word vectors (would be loaded from file in production)
        self.vocab = {}
        self._build_simple_vocab()
    
    def _build_simple_vocab(self):
        """Build a simple character-based embedding."""
        # Use character trigrams for simple embeddings
        pass
    
    def embed(self, text: str) -> List[float]:
        """Create embedding from text."""
        # Simple bag-of-characters approach
        text = text.lower()
        
        # Character frequency
        char_counts = defaultdict(int)
        for c in text:
            if c.isalnum():
                char_counts[c] += 1
        
        # Create feature vector
        features = []
        
        # Character frequencies (26 letters + 10 digits = 36 dims)
        for c in 'abcdefghijklmnopqrstuvwxyz0123456789':
            features.append(char_counts.get(c, 0) / max(1, len(text)))
        
        # Text statistics
        features.append(len(text) / 1000)  # Normalized length
        features.append(text.count(' ') / max(1, len(text)))  # Word density
        features.append(sum(1 for c in text if c.isupper()) / max(1, len(text)))  # Caps ratio
        
        # Pad to dimension
        while len(features) < self.dim:
            features.append(0.0)
        
        # Normalize
        norm = math.sqrt(sum(x*x for x in features))
        if norm > 0:
            features = [x / norm for x in features]
        
        return features[:self.dim]


# =============================================================================
# VECTOR STORE (Simple SQLite-based)
# =============================================================================

class VectorStore:
    """
    Simple vector store using SQLite.
    Stores memories with their embeddings for similarity search.
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT,
                embedding TEXT,
                memory_type TEXT,
                metadata TEXT,
                created_at TEXT,
                accessed_at TEXT,
                access_count INTEGER DEFAULT 0,
                importance REAL DEFAULT 0.5
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                source_id TEXT,
                target_id TEXT,
                relationship TEXT,
                strength REAL DEFAULT 1.0,
                created_at TEXT,
                PRIMARY KEY (source_id, target_id, relationship)
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)
        """)
        
        conn.commit()
        conn.close()
    
    def store(self, memory: Memory) -> str:
        """Store a memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO memories 
            (id, content, embedding, memory_type, metadata, created_at, accessed_at, access_count, importance)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.id,
            memory.content,
            json.dumps(memory.embedding),
            memory.memory_type,
            json.dumps(memory.metadata),
            memory.created_at,
            memory.accessed_at,
            memory.access_count,
            memory.importance
        ))
        
        conn.commit()
        conn.close()
        return memory.id
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Retrieve a memory by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memories WHERE id = ?", (memory_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_memory(row)
        return None
    
    def _row_to_memory(self, row) -> Memory:
        """Convert database row to Memory object."""
        return Memory(
            id=row[0],
            content=row[1],
            embedding=json.loads(row[2]),
            memory_type=row[3],
            metadata=json.loads(row[4]),
            created_at=row[5],
            accessed_at=row[6],
            access_count=row[7],
            importance=row[8]
        )
    
    def search(self, query_embedding: List[float], limit: int = 5, 
               memory_type: Optional[str] = None) -> List[Tuple[Memory, float]]:
        """Search for similar memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if memory_type:
            cursor.execute(
                "SELECT * FROM memories WHERE memory_type = ?", 
                (memory_type,)
            )
        else:
            cursor.execute("SELECT * FROM memories")
        
        rows = cursor.fetchall()
        conn.close()
        
        # Compute similarities
        results = []
        for row in rows:
            memory = self._row_to_memory(row)
            similarity = self._cosine_similarity(query_embedding, memory.embedding)
            results.append((memory, similarity))
        
        # Sort by similarity
        results.sort(key=lambda x: -x[1])
        return results[:limit]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity."""
        dot = sum(x*y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x*x for x in a))
        norm_b = math.sqrt(sum(x*x for x in b))
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def add_connection(self, conn_obj: Connection):
        """Add a connection between memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO connections 
            (source_id, target_id, relationship, strength, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            conn_obj.source_id,
            conn_obj.target_id,
            conn_obj.relationship,
            conn_obj.strength,
            conn_obj.created_at or datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_connections(self, memory_id: str) -> List[Connection]:
        """Get all connections for a memory."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM connections 
            WHERE source_id = ? OR target_id = ?
        """, (memory_id, memory_id))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            Connection(
                source_id=row[0],
                target_id=row[1],
                relationship=row[2],
                strength=row[3],
                created_at=row[4]
            )
            for row in rows
        ]
    
    def count(self) -> Tuple[int, int]:
        """Count memories and connections."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM memories")
        mem_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM connections")
        conn_count = cursor.fetchone()[0]
        
        conn.close()
        return mem_count, conn_count


# =============================================================================
# KNOWLEDGE GRAPH
# =============================================================================

class KnowledgeGraph:
    """
    The complete Knowledge Graph for SovereignCore.
    Combines vector store with graph relationships.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path.home() / "SovereignCore" / "memory" / "knowledge.db"
        self.store = VectorStore(self.db_path)
        self.embedder = SimpleEmbedder()
        
        memory_print("init")
        mem_count, _ = self.store.count()
        memory_print("ready", count=mem_count)
    
    def remember(self, content: str, memory_type: str = "semantic",
                 metadata: Optional[Dict] = None, importance: float = 0.5) -> str:
        """Store a new memory."""
        memory_print("storing", preview=content[:50])
        
        # Generate ID
        memory_id = hashlib.sha256(
            f"{content}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # Generate embedding
        embedding = self.embedder.embed(content)
        
        # Create memory
        memory = Memory(
            id=memory_id,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            metadata=metadata or {},
            created_at=datetime.now().isoformat(),
            accessed_at=datetime.now().isoformat(),
            access_count=0,
            importance=importance
        )
        
        # Store
        self.store.store(memory)
        memory_print("stored", id=memory_id)
        
        return memory_id
    
    def recall(self, query: str, limit: int = 5,
               memory_type: Optional[str] = None) -> List[Dict]:
        """Recall related memories."""
        memory_print("searching", query=query[:30])
        
        # Embed query
        query_embedding = self.embedder.embed(query)
        
        # Search
        results = self.store.search(query_embedding, limit, memory_type)
        
        if results:
            memory_print("found", count=len(results))
            return [
                {
                    "memory": mem.to_dict(),
                    "similarity": sim,
                    "connections": [
                        asdict(c) for c in self.store.get_connections(mem.id)
                    ]
                }
                for mem, sim in results
            ]
        else:
            memory_print("not_found")
            return []
    
    def connect(self, source_id: str, target_id: str, 
                relationship: str, strength: float = 1.0):
        """Create a connection between memories."""
        memory_print("connecting", source=source_id[:8], target=target_id[:8])
        
        conn = Connection(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            strength=strength,
            created_at=datetime.now().isoformat()
        )
        self.store.add_connection(conn)
    
    def remember_conversation(self, user_message: str, ai_response: str,
                              context: Optional[Dict] = None) -> Tuple[str, str]:
        """Store a conversation exchange as episodic memory."""
        # Store user message
        user_id = self.remember(
            f"User: {user_message}",
            memory_type="episodic",
            metadata={"role": "user", "context": context or {}},
            importance=0.6
        )
        
        # Store AI response
        ai_id = self.remember(
            f"AI: {ai_response}",
            memory_type="episodic",
            metadata={"role": "assistant", "context": context or {}},
            importance=0.5
        )
        
        # Connect them
        self.connect(user_id, ai_id, "prompted", strength=1.0)
        
        return user_id, ai_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        mem_count, conn_count = self.store.count()
        memory_print("stats", memories=mem_count, connections=conn_count)
        
        return {
            "total_memories": mem_count,
            "total_connections": conn_count,
            "db_path": str(self.db_path)
        }


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🧠 Knowledge Graph")
    parser.add_argument("command", choices=["remember", "recall", "stats", "test"])
    parser.add_argument("--content", type=str, help="Content to remember")
    parser.add_argument("--query", type=str, help="Query to recall")
    parser.add_argument("--type", type=str, default="semantic", 
                        help="Memory type: semantic, episodic, procedural")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🧠 KNOWLEDGE GRAPH")
    print("="*60 + "\n")
    
    kg = KnowledgeGraph()
    
    if args.command == "remember":
        if args.content:
            memory_id = kg.remember(args.content, memory_type=args.type)
            print(f"\n✅ Remembered with ID: {memory_id}")
        else:
            print("❌ Need --content to remember")
    
    elif args.command == "recall":
        if args.query:
            results = kg.recall(args.query)
            print(f"\n📚 Found {len(results)} memories:\n")
            for r in results:
                mem = r["memory"]
                print(f"  [{mem['id'][:8]}] {mem['content'][:60]}...")
                print(f"      Similarity: {r['similarity']:.3f}")
        else:
            print("❌ Need --query to recall")
    
    elif args.command == "stats":
        stats = kg.get_stats()
        print(f"\n📊 Knowledge Graph Stats:")
        for k, v in stats.items():
            print(f"   {k}: {v}")
    
    elif args.command == "test":
        print("🧪 Testing Knowledge Graph...\n")
        
        # Store some memories
        id1 = kg.remember("SovereignCore is an AI architecture for Apple Silicon", 
                         importance=0.9)
        id2 = kg.remember("BitNet uses 1.58-bit quantization for efficient inference",
                         importance=0.8)
        id3 = kg.remember("The swarm learns patterns from filesystem data",
                         importance=0.7)
        
        # Connect them
        kg.connect(id1, id2, "contains")
        kg.connect(id1, id3, "uses")
        
        # Recall
        results = kg.recall("How does SovereignCore work?")
        
        print(f"\n✅ Test complete!")
        print(f"   Stored: 3 memories")
        print(f"   Retrieved: {len(results)} memories")
        print(f"   Top match similarity: {results[0]['similarity']:.3f}")
