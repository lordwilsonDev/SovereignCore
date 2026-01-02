#!/usr/bin/env python3
"""
🐝 VJEPA Swarm Worker
=====================

A single training worker in the VJEPA swarm.
Each worker is kind, reports progress, and learns its partition of data.

Worker Types:
- FILE_PREDICTOR: Learns to predict next file in sequence
- EMBEDDING_LEARNER: Learns file embeddings
- RELATIONSHIP_LEARNER: Learns file relationships

Kind Messages Enabled 💜
"""

import os
import json
import time
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import multiprocessing as mp

# Try to import MLX for Apple Silicon optimization
try:
    import mlx.core as mx
    import mlx.nn as nn
    MLX_AVAILABLE = True
except ImportError:
    mx = None
    nn = None
    MLX_AVAILABLE = False


# =============================================================================
# KIND MESSAGES
# =============================================================================

WORKER_MESSAGES = {
    "ready": "🐝 Worker {id} buzzing and ready to help!",
    "training_start": "📚 Worker {id} starting to learn patterns...",
    "training_step": "🔄 Worker {id}: Step {step}, Loss: {loss:.4f}",
    "training_milestone": "🎯 Worker {id} reached milestone! {step} steps, avg loss: {loss:.4f}",
    "training_complete": "🎓 Worker {id} finished learning! Final loss: {loss:.4f}",
    "sharing": "🤝 Worker {id} sharing knowledge with the swarm...",
    "received": "📬 Worker {id} received new knowledge from peers!",
    "error": "🤔 Worker {id} hit a snag, but recovering...",
    "heartbeat": "💓 Worker {id} is healthy (step {step})",
    "sleeping": "😴 Worker {id} taking a quick rest...",
    "waking": "☀️ Worker {id} waking up refreshed!"
}

def worker_print(worker_id: int, message_key: str, **kwargs):
    """Print a kind worker message."""
    msg = WORKER_MESSAGES.get(message_key, message_key)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg.format(id=worker_id, **kwargs)}")


# =============================================================================
# WORKER CONFIGURATION
# =============================================================================

@dataclass
class WorkerConfig:
    """Configuration for a swarm worker."""
    worker_id: int
    total_workers: int
    data_partition: List[Dict]
    learning_rate: float = 0.001
    batch_size: int = 32
    max_steps: int = 1000
    checkpoint_interval: int = 100
    message_interval: int = 50
    heartbeat_interval: int = 200


# =============================================================================
# SIMPLE VJEPA MODEL (Pure Python for now)
# =============================================================================

class SimpleVJEPAEncoder:
    """
    Simplified VJEPA-style encoder.
    
    In the full version, this would be a Vision Transformer.
    For filesystem training, we encode file metadata into vectors.
    """
    
    def __init__(self, input_dim: int = 64, hidden_dim: int = 128, output_dim: int = 64):
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Simple weights (would be MLX tensors in full version)
        self.weights = {
            "embed": self._init_weights(input_dim, hidden_dim),
            "hidden": self._init_weights(hidden_dim, hidden_dim),
            "output": self._init_weights(hidden_dim, output_dim)
        }
    
    def _init_weights(self, in_dim: int, out_dim: int) -> List[List[float]]:
        """Initialize random weights."""
        return [[random.gauss(0, 0.1) for _ in range(out_dim)] for _ in range(in_dim)]
    
    def encode(self, features: List[float]) -> List[float]:
        """Encode input features into an embedding."""
        # Simple forward pass
        hidden = self._matmul(features, self.weights["embed"])
        hidden = [max(0, x) for x in hidden]  # ReLU
        hidden = self._matmul(hidden, self.weights["hidden"])
        hidden = [max(0, x) for x in hidden]  # ReLU
        output = self._matmul(hidden, self.weights["output"])
        return self._normalize(output)
    
    def _matmul(self, vec: List[float], mat: List[List[float]]) -> List[float]:
        """Matrix-vector multiplication."""
        result = []
        for j in range(len(mat[0])):
            s = sum(vec[i] * mat[i][j] for i in range(min(len(vec), len(mat))))
            result.append(s)
        return result
    
    def _normalize(self, vec: List[float]) -> List[float]:
        """L2 normalize."""
        norm = sum(x*x for x in vec) ** 0.5
        if norm < 1e-8:
            return vec
        return [x / norm for x in vec]


class VJEPAPredictor:
    """
    Predicts the next file embedding from context.
    
    This is the "predictive" part of VJEPA.
    """
    
    def __init__(self, embed_dim: int = 64):
        self.embed_dim = embed_dim
        self.weights = {
            "context": [[random.gauss(0, 0.1) for _ in range(embed_dim)] for _ in range(embed_dim)],
            "predict": [[random.gauss(0, 0.1) for _ in range(embed_dim)] for _ in range(embed_dim)]
        }
    
    def predict(self, context_embedding: List[float]) -> List[float]:
        """Predict the next embedding."""
        hidden = self._matmul(context_embedding, self.weights["context"])
        hidden = [max(0, x) for x in hidden]  # ReLU
        output = self._matmul(hidden, self.weights["predict"])
        return self._normalize(output)
    
    def _matmul(self, vec: List[float], mat: List[List[float]]) -> List[float]:
        """Matrix-vector multiplication."""
        result = []
        for j in range(len(mat[0])):
            s = sum(vec[i] * mat[i][j] for i in range(min(len(vec), len(mat))))
            result.append(s)
        return result
    
    def _normalize(self, vec: List[float]) -> List[float]:
        """L2 normalize."""
        norm = sum(x*x for x in vec) ** 0.5
        if norm < 1e-8:
            return vec
        return [x / norm for x in vec]


# =============================================================================
# FEATURE EXTRACTION
# =============================================================================

def file_to_features(file_node: Dict) -> List[float]:
    """Convert a file node to feature vector."""
    features = []
    
    # Size (log scale, normalized)
    size = file_node.get("size", 0)
    features.append(min(1.0, (size + 1) / 1_000_000))  # Normalized log size
    
    # Extension encoding (one-hot for common extensions)
    ext = file_node.get("extension", "").lower()
    common_exts = [".py", ".swift", ".md", ".json", ".txt", ".rs", ".js", ".ts", ".html", ".css"]
    features.extend([1.0 if ext == e else 0.0 for e in common_exts])
    
    # Depth (normalized)
    depth = file_node.get("depth", 0)
    features.append(min(1.0, depth / 10.0))
    
    # Is directory
    features.append(1.0 if file_node.get("is_dir", False) else 0.0)
    
    # Name length (normalized)
    name_len = len(file_node.get("name", ""))
    features.append(min(1.0, name_len / 50.0))
    
    # Pad to fixed size
    while len(features) < 64:
        features.append(0.0)
    
    return features[:64]


# =============================================================================
# THE WORKER
# =============================================================================

class VJEPAWorker:
    """
    A single worker in the VJEPA training swarm.
    Trains on a partition of the filesystem data.
    """
    
    def __init__(self, config: WorkerConfig):
        self.config = config
        self.worker_id = config.worker_id
        
        # Initialize model
        self.encoder = SimpleVJEPAEncoder()
        self.predictor = VJEPAPredictor()
        
        # Training state
        self.step = 0
        self.losses = []
        self.best_loss = float('inf')
        
        worker_print(self.worker_id, "ready")
    
    def train(self) -> Dict[str, Any]:
        """Run the training loop."""
        worker_print(self.worker_id, "training_start")
        
        data = self.config.data_partition
        if not data:
            worker_print(self.worker_id, "error")
            return {"error": "No data"}
        
        while self.step < self.config.max_steps:
            # Sample a batch
            batch_indices = random.sample(range(len(data)), min(self.config.batch_size, len(data)))
            
            # Training step
            batch_loss = self._train_step([data[i] for i in batch_indices])
            self.losses.append(batch_loss)
            self.step += 1
            
            # Report progress
            if self.step % self.config.message_interval == 0:
                worker_print(self.worker_id, "training_step", step=self.step, loss=batch_loss)
            
            # Milestone
            if self.step % self.config.checkpoint_interval == 0:
                avg_loss = sum(self.losses[-100:]) / len(self.losses[-100:])
                worker_print(self.worker_id, "training_milestone", step=self.step, loss=avg_loss)
            
            # Heartbeat
            if self.step % self.config.heartbeat_interval == 0:
                worker_print(self.worker_id, "heartbeat", step=self.step)
        
        final_loss = sum(self.losses[-100:]) / max(1, len(self.losses[-100:]))
        worker_print(self.worker_id, "training_complete", loss=final_loss)
        
        return {
            "worker_id": self.worker_id,
            "steps": self.step,
            "final_loss": final_loss,
            "losses": self.losses
        }
    
    def _train_step(self, batch: List[Dict]) -> float:
        """Single training step."""
        total_loss = 0.0
        
        for i in range(len(batch) - 1):
            # Encode context
            context_features = file_to_features(batch[i])
            context_embed = self.encoder.encode(context_features)
            
            # Encode target
            target_features = file_to_features(batch[i + 1])
            target_embed = self.encoder.encode(target_features)
            
            # Predict
            predicted = self.predictor.predict(context_embed)
            
            # Compute loss (MSE)
            loss = sum((p - t) ** 2 for p, t in zip(predicted, target_embed)) / len(predicted)
            total_loss += loss
        
        return total_loss / max(1, len(batch) - 1)
    
    def get_embeddings(self, nodes: List[Dict]) -> Dict[str, List[float]]:
        """Get embeddings for a list of nodes."""
        embeddings = {}
        for node in nodes:
            features = file_to_features(node)
            embed = self.encoder.encode(features)
            embeddings[node.get("path", "")] = embed
        return embeddings


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🐝 VJEPA Swarm Worker")
    parser.add_argument("--worker-id", type=int, default=0)
    parser.add_argument("--data", type=str, 
                        default="~/SovereignCore/swarm_vjepa/data/filesystem_knowledge.json")
    parser.add_argument("--max-steps", type=int, default=500)
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print(f"🐝 VJEPA Worker {args.worker_id}")
    print("="*60 + "\n")
    
    # Load data
    data_path = Path(args.data).expanduser()
    if data_path.exists():
        with open(data_path) as f:
            knowledge = json.load(f)
        nodes = knowledge.get("nodes", [])
    else:
        print(f"⚠️ No data found at {data_path}")
        print("   Run crawler.py first!")
        nodes = []
    
    # Configure worker
    config = WorkerConfig(
        worker_id=args.worker_id,
        total_workers=1,
        data_partition=nodes,
        max_steps=args.max_steps
    )
    
    # Train
    worker = VJEPAWorker(config)
    result = worker.train()
    
    print(f"\n✨ Worker {args.worker_id} complete!")
    print(f"   Final loss: {result.get('final_loss', 0):.4f}")
