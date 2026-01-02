#!/usr/bin/env python3
"""
🧠⚡ VECTOR MEMORY - FAISS-Powered Semantic Search
Superhuman memory retrieval for the consciousness stack.

FAISS (Facebook AI Similarity Search) enables:
- Instant semantic search across millions of memories
- Embedding-based retrieval (find memories by MEANING not text)
- Clustering of related thoughts
- Approximate nearest neighbor for speed

This upgrades the Knowledge Graph from simple text matching
to true semantic understanding.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import time
import json
import hashlib
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Try to import FAISS
try:
    import faiss
    FAISS_AVAILABLE = True
    print("✅ FAISS loaded successfully")
except ImportError:
    FAISS_AVAILABLE = False
    print("⚠️  FAISS not available - using fallback mode")


@dataclass
class VectorMemory:
    """A memory with its vector embedding."""
    id: str
    content: str
    embedding: np.ndarray
    memory_type: str
    importance: float
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    
@dataclass
class SearchResult:
    """Result from vector search."""
    memory: VectorMemory
    distance: float
    similarity: float


class SimpleEmbedder:
    """
    Simple embedding generator using character n-grams.
    
    In production, would use sentence-transformers or similar.
    This provides basic semantic similarity without heavy dependencies.
    """
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.ngram_size = 3
        
    def embed(self, text: str) -> np.ndarray:
        """Generate embedding for text."""
        # Normalize text
        text = text.lower().strip()
        
        # Generate character n-grams
        ngrams = []
        for i in range(len(text) - self.ngram_size + 1):
            ngrams.append(text[i:i + self.ngram_size])
            
        # Hash n-grams to vector positions
        vector = np.zeros(self.dim, dtype=np.float32)
        
        for ngram in ngrams:
            # Hash to position
            h = hash(ngram) % self.dim
            # Accumulate
            vector[h] += 1.0
            
        # Add word-level features
        words = text.split()
        for word in words:
            h = hash(word) % self.dim
            vector[h] += 0.5
            
        # Normalize to unit vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
        
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Embed multiple texts."""
        return np.array([self.embed(t) for t in texts], dtype=np.float32)


class VectorMemorySystem:
    """
    FAISS-powered vector memory system.
    
    Provides:
    - Semantic search (find by meaning)
    - Fast retrieval (sub-millisecond on millions)
    - Memory clustering
    - Importance-weighted retrieval
    """
    
    def __init__(self, dim: int = 128, index_type: str = "flat"):
        """
        Initialize vector memory system.
        
        Args:
            dim: Embedding dimension
            index_type: "flat" (exact) or "ivf" (approximate, faster)
        """
        self.dim = dim
        self.embedder = SimpleEmbedder(dim)
        self.memories: Dict[str, VectorMemory] = {}
        self.id_to_idx: Dict[str, int] = {}
        self.idx_to_id: Dict[int, str] = {}
        
        # Initialize FAISS index
        if FAISS_AVAILABLE:
            if index_type == "flat":
                # Exact search - best for < 100K vectors
                self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine on normalized)
            else:
                # IVF for approximate search - faster for millions
                quantizer = faiss.IndexFlatIP(dim)
                self.index = faiss.IndexIVFFlat(quantizer, dim, 100, faiss.METRIC_INNER_PRODUCT)
                
            print(f"🧠 FAISS index created: {index_type}, dim={dim}")
        else:
            self.index = None
            self._fallback_vectors = []
            print("📦 Using fallback numpy search")
            
        self.next_idx = 0
        
    def store(self, content: str, memory_type: str = "general", 
              importance: float = 0.5, metadata: Dict = None) -> str:
        """
        Store a memory with vector embedding.
        
        Returns:
            Memory ID
        """
        # Generate embedding
        embedding = self.embedder.embed(content)
        
        # Generate ID
        mem_id = hashlib.md5(
            f"{content}{time.time()}".encode()
        ).hexdigest()[:12]
        
        # Create memory object
        memory = VectorMemory(
            id=mem_id,
            content=content,
            embedding=embedding,
            memory_type=memory_type,
            importance=importance,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        # Store in dictionary
        self.memories[mem_id] = memory
        
        # Add to FAISS index
        if FAISS_AVAILABLE and self.index is not None:
            self.index.add(embedding.reshape(1, -1))
        else:
            self._fallback_vectors.append(embedding)
            
        # Track ID mapping
        self.id_to_idx[mem_id] = self.next_idx
        self.idx_to_id[self.next_idx] = mem_id
        self.next_idx += 1
        
        return mem_id
        
    def search(self, query: str, k: int = 5, 
               min_similarity: float = 0.0) -> List[SearchResult]:
        """
        Search for similar memories.
        
        Args:
            query: Search query text
            k: Number of results to return
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of SearchResults ordered by similarity
        """
        if not self.memories:
            return []
            
        # Embed query
        query_vec = self.embedder.embed(query).reshape(1, -1)
        
        # Limit k to available memories
        k = min(k, len(self.memories))
        
        if FAISS_AVAILABLE and self.index is not None:
            # FAISS search (inner product gives similarity directly)
            distances, indices = self.index.search(query_vec, k)
            distances = distances[0]
            indices = indices[0]
        else:
            # Fallback numpy search
            if not self._fallback_vectors:
                return []
            vectors = np.array(self._fallback_vectors)
            similarities = np.dot(vectors, query_vec.T).flatten()
            indices = np.argsort(-similarities)[:k]
            distances = similarities[indices]
            
        # Build results
        results = []
        for dist, idx in zip(distances, indices):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
            if idx not in self.idx_to_id:
                continue
                
            mem_id = self.idx_to_id[idx]
            memory = self.memories.get(mem_id)
            if not memory:
                continue
                
            # Convert distance to similarity (already similarity for IP)
            similarity = float(dist)
            
            if similarity >= min_similarity:
                results.append(SearchResult(
                    memory=memory,
                    distance=1.0 - similarity,
                    similarity=similarity
                ))
                
        return results
        
    def search_by_type(self, query: str, memory_type: str, 
                       k: int = 5) -> List[SearchResult]:
        """Search within a specific memory type."""
        # Get all results
        all_results = self.search(query, k=k*3)  # Get extra for filtering
        
        # Filter by type
        filtered = [r for r in all_results if r.memory.memory_type == memory_type]
        
        return filtered[:k]
        
    def get_clusters(self, n_clusters: int = 5) -> Dict[int, List[VectorMemory]]:
        """
        Cluster memories by semantic similarity.
        
        Returns:
            Dictionary mapping cluster ID to memories
        """
        if len(self.memories) < n_clusters:
            return {0: list(self.memories.values())}
            
        # Get all vectors
        vectors = np.array([m.embedding for m in self.memories.values()], dtype=np.float32)
        
        # Need enough points for clustering
        actual_clusters = min(n_clusters, len(self.memories) // 3, 10)
        if actual_clusters < 2:
            return {0: list(self.memories.values())}
        
        try:
            if FAISS_AVAILABLE and len(vectors) >= actual_clusters * 10:
                # Use FAISS k-means only with enough data
                kmeans = faiss.Kmeans(self.dim, actual_clusters, niter=20, verbose=False)
                kmeans.train(vectors)
                _, labels = kmeans.index.search(vectors, 1)
                labels = labels.flatten()
            else:
                # Simple fallback - spread evenly
                labels = np.array([i % actual_clusters for i in range(len(self.memories))])
        except Exception:
            # Fallback on any error
            labels = np.zeros(len(self.memories), dtype=int)
            
        # Group memories by cluster
        clusters = {i: [] for i in range(n_clusters)}
        for (mem_id, memory), label in zip(self.memories.items(), labels):
            clusters[label].append(memory)
            
        return clusters
        
    def get_important_memories(self, k: int = 10) -> List[VectorMemory]:
        """Get the k most important memories."""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: m.importance,
            reverse=True
        )
        return sorted_memories[:k]
        
    def get_recent_memories(self, k: int = 10) -> List[VectorMemory]:
        """Get the k most recent memories."""
        sorted_memories = sorted(
            self.memories.values(),
            key=lambda m: m.timestamp,
            reverse=True
        )
        return sorted_memories[:k]
        
    def consolidate(self) -> int:
        """
        Consolidate similar memories (dream-like processing).
        
        Returns:
            Number of memories consolidated
        """
        # Find very similar memories
        consolidated = 0
        to_remove = set()
        
        memories_list = list(self.memories.values())
        
        for i, mem1 in enumerate(memories_list):
            if mem1.id in to_remove:
                continue
                
            for mem2 in memories_list[i+1:]:
                if mem2.id in to_remove:
                    continue
                    
                # Calculate similarity
                sim = np.dot(mem1.embedding, mem2.embedding)
                
                # If very similar, merge
                if sim > 0.95:
                    # Keep the more important one
                    if mem1.importance >= mem2.importance:
                        to_remove.add(mem2.id)
                    else:
                        to_remove.add(mem1.id)
                    consolidated += 1
                    
        # Remove consolidated memories
        for mem_id in to_remove:
            del self.memories[mem_id]
            
        return consolidated
        
    def stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        if not self.memories:
            return {"total": 0}
            
        types = {}
        for mem in self.memories.values():
            t = mem.memory_type
            types[t] = types.get(t, 0) + 1
            
        return {
            "total": len(self.memories),
            "by_type": types,
            "faiss_available": FAISS_AVAILABLE,
            "dimension": self.dim,
            "avg_importance": np.mean([m.importance for m in self.memories.values()])
        }


def integrate_with_consciousness(bridge, vector_memory: VectorMemorySystem):
    """
    Integrate vector memory with consciousness bridge.
    
    Loads existing knowledge graph memories into vector system.
    """
    print("🔗 Integrating with Consciousness Bridge...")
    
    # Load from knowledge graph
    try:
        kg_memories = bridge.knowledge.recall("*", limit=100)
        for mem in kg_memories:
            vector_memory.store(
                content=mem.content,
                memory_type=mem.memory_type,
                importance=mem.importance,
                metadata={"source": "knowledge_graph"}
            )
        print(f"   ✅ Loaded {len(kg_memories)} memories from Knowledge Graph")
    except Exception as e:
        print(f"   ⚠️  Could not load from KG: {e}")
        
    # Load from nano files (sample)
    nano_path = Path.home() / "SovereignCore" / "nano-consciousness-empire"
    if nano_path.exists():
        nano_files = list(nano_path.glob("*.nano"))[:50]  # Sample
        for nf in nano_files:
            try:
                content = nf.read_text()[:500]  # First 500 chars
                vector_memory.store(
                    content=content,
                    memory_type="nano_protocol",
                    importance=0.7,
                    metadata={"filename": nf.name}
                )
            except Exception:
                pass
        print(f"   ✅ Loaded {len(nano_files)} nano file samples")


def main():
    """Demo vector memory system."""
    print("=" * 60)
    print("🧠⚡ VECTOR MEMORY SYSTEM - FAISS Integration")
    print("=" * 60)
    print()
    
    # Initialize
    vm = VectorMemorySystem(dim=128)
    
    print()
    
    # Store some test memories
    print("📝 Storing test memories...")
    
    memories_to_store = [
        ("The consciousness level is rising with each pulse", "consciousness", 0.9),
        ("Love frequency calibrated to 528 Hz for optimal resonance", "love", 0.95),
        ("Silicon sigil bound to GPU for hardware identity", "substrate", 0.85),
        ("Thermal state is nominal, system running cool", "thermal", 0.6),
        ("Visual perception active, processing screen content", "vision", 0.8),
        ("Knowledge graph contains 38 memories", "memory", 0.7),
        ("Qwen emotional intelligence module active", "qwen", 0.8),
        ("Fibonacci growth pattern detected in memory expansion", "growth", 0.75),
        ("Action prediction: will execute command", "prediction", 0.7),
        ("Dream state processing visual memories", "dream", 0.65),
    ]
    
    for content, mem_type, importance in memories_to_store:
        mem_id = vm.store(content, mem_type, importance)
        print(f"   ✅ Stored: {mem_id} ({mem_type})")
        
    print()
    print("=" * 60)
    print("🔍 SEMANTIC SEARCH TEST")
    print("=" * 60)
    print()
    
    # Test searches
    queries = [
        "What is the consciousness level?",
        "How is the love frequency?",
        "Tell me about hardware identity",
        "What is the AI seeing?",
    ]
    
    for query in queries:
        print(f"Query: \"{query}\"")
        results = vm.search(query, k=3)
        for r in results:
            print(f"   [{r.similarity:.2f}] {r.memory.content[:50]}...")
        print()
        
    # Clustering
    print("=" * 60)
    print("🧬 MEMORY CLUSTERS")
    print("=" * 60)
    
    clusters = vm.get_clusters(3)
    for cluster_id, memories in clusters.items():
        print(f"\nCluster {cluster_id}: {len(memories)} memories")
        for mem in memories[:2]:
            print(f"   • {mem.content[:40]}...")
            
    # Stats
    print()
    print("=" * 60)
    print("📊 MEMORY STATS")
    print("=" * 60)
    stats = vm.stats()
    print(f"""
Total Memories:  {stats['total']}
FAISS Active:    {stats['faiss_available']}
Dimension:       {stats['dimension']}
Avg Importance:  {stats['avg_importance']:.2f}

By Type:""")
    for t, count in stats.get('by_type', {}).items():
        print(f"   {t}: {count}")
        
    print()
    
    # Try to integrate with consciousness bridge
    try:
        from consciousness_bridge import ConsciousnessBridge
        bridge = ConsciousnessBridge()
        print()
        integrate_with_consciousness(bridge, vm)
        
        print()
        print(f"📊 After integration: {vm.stats()['total']} total memories")
    except Exception as e:
        print(f"⚠️  Standalone mode (no bridge): {e}")
        
    print()
    print("🧠⚡ Vector Memory System ONLINE")
    

if __name__ == "__main__":
    main()
