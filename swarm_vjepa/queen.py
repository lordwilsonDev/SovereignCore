#!/usr/bin/env python3
"""
👑 VJEPA Swarm Queen (Coordinator)
==================================

The Queen coordinates all workers in the VJEPA training swarm.
She distributes work, aggregates knowledge, and keeps morale high!

Features:
- Partitions data across workers
- Launches worker processes
- Aggregates gradients (federated learning)
- Monitors swarm health
- Provides kind encouragement

Kind Messages Enabled 💜
"""

import os
import json
import time
import random
import multiprocessing as mp
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import signal
import sys


# =============================================================================
# QUEEN MESSAGES
# =============================================================================

QUEEN_MESSAGES = {
    "awakening": "👑 The Swarm Queen awakens! Preparing to coordinate learning...",
    "loading_data": "📂 Loading filesystem knowledge...",
    "data_loaded": "✅ Knowledge loaded: {nodes} files, {relationships} relationships",
    "partitioning": "🔪 Dividing data among {n} workers...",
    "workers_ready": "🐝 All {n} workers are ready! Let the learning begin!",
    "training_start": "🚀 SWARM TRAINING STARTED! Go little bees, go!",
    "training_progress": "📊 Swarm Progress: {complete}/{total} workers done",
    "aggregating": "🤝 Workers returning... aggregating their knowledge...",
    "training_complete": "🎉 TRAINING COMPLETE! The swarm has learned!",
    "saving": "💾 Saving the collective wisdom...",
    "error": "🤔 A worker needs help, but the swarm is resilient!",
    "farewell": "👑 The Queen rests. Until next time, beautiful swarm! 💜"
}

def queen_print(message_key: str, **kwargs):
    """Print a regal message."""
    msg = QUEEN_MESSAGES.get(message_key, message_key)
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{timestamp}] {msg.format(**kwargs)}")


# =============================================================================
# SWARM CONFIGURATION
# =============================================================================

@dataclass
class SwarmConfig:
    """Configuration for the VJEPA swarm."""
    num_workers: int = 4
    data_path: str = "~/SovereignCore/swarm_vjepa/data/filesystem_knowledge.json"
    output_path: str = "~/SovereignCore/swarm_vjepa/data/trained_model.json"
    max_steps_per_worker: int = 500
    learning_rate: float = 0.001
    batch_size: int = 32


# =============================================================================
# THE QUEEN
# =============================================================================

class SwarmQueen:
    """
    The Queen coordinates the VJEPA training swarm.
    """
    
    def __init__(self, config: SwarmConfig):
        self.config = config
        self.knowledge: Optional[Dict] = None
        self.worker_results: List[Dict] = []
        self.start_time: Optional[datetime] = None
        
        queen_print("awakening")
    
    def load_data(self) -> bool:
        """Load filesystem knowledge."""
        queen_print("loading_data")
        
        data_path = Path(self.config.data_path).expanduser()
        if not data_path.exists():
            print(f"   ❌ Data not found at {data_path}")
            print("   💡 Run: python crawler.py first!")
            return False
        
        with open(data_path) as f:
            self.knowledge = json.load(f)
        
        nodes = len(self.knowledge.get("nodes", []))
        rels = len(self.knowledge.get("relationships", []))
        queen_print("data_loaded", nodes=nodes, relationships=rels)
        return True
    
    def partition_data(self) -> List[List[Dict]]:
        """Partition data across workers."""
        queen_print("partitioning", n=self.config.num_workers)
        
        nodes = self.knowledge.get("nodes", [])
        random.shuffle(nodes)
        
        # Divide into partitions
        partition_size = len(nodes) // self.config.num_workers
        partitions = []
        
        for i in range(self.config.num_workers):
            start = i * partition_size
            if i == self.config.num_workers - 1:
                partition = nodes[start:]
            else:
                partition = nodes[start:start + partition_size]
            partitions.append(partition)
            print(f"   🐝 Worker {i}: {len(partition)} files")
        
        return partitions
    
    def train_swarm(self):
        """Run distributed training across all workers."""
        if not self.load_data():
            return None
        
        partitions = self.partition_data()
        queen_print("workers_ready", n=self.config.num_workers)
        
        # Import worker module
        from worker import VJEPAWorker, WorkerConfig
        
        self.start_time = datetime.now()
        queen_print("training_start")
        print("\n" + "─"*60)
        
        # Train each worker (sequential for now, could be parallel)
        for i in range(self.config.num_workers):
            print(f"\n{'='*60}")
            print(f"🐝 TRAINING WORKER {i}")
            print("="*60 + "\n")
            
            config = WorkerConfig(
                worker_id=i,
                total_workers=self.config.num_workers,
                data_partition=partitions[i],
                learning_rate=self.config.learning_rate,
                batch_size=self.config.batch_size,
                max_steps=self.config.max_steps_per_worker
            )
            
            worker = VJEPAWorker(config)
            result = worker.train()
            self.worker_results.append(result)
            
            queen_print("training_progress", 
                       complete=i+1, 
                       total=self.config.num_workers)
        
        print("\n" + "─"*60)
        queen_print("aggregating")
        
        # Aggregate results
        aggregated = self._aggregate_results()
        
        queen_print("training_complete")
        return aggregated
    
    def _aggregate_results(self) -> Dict[str, Any]:
        """Aggregate results from all workers."""
        total_steps = sum(r.get("steps", 0) for r in self.worker_results)
        avg_loss = sum(r.get("final_loss", 0) for r in self.worker_results) / len(self.worker_results)
        
        duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "training_summary": {
                "total_workers": self.config.num_workers,
                "total_steps": total_steps,
                "average_final_loss": avg_loss,
                "duration_seconds": duration,
                "steps_per_second": total_steps / duration if duration > 0 else 0
            },
            "worker_results": self.worker_results,
            "metadata": {
                "trained_at": datetime.now().isoformat(),
                "data_source": self.config.data_path
            }
        }
    
    def save_results(self, results: Dict):
        """Save training results."""
        queen_print("saving")
        
        output_path = Path(self.config.output_path).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"   💾 Saved to: {output_path}")
    
    def print_summary(self, results: Dict):
        """Print training summary."""
        summary = results.get("training_summary", {})
        
        print("\n" + "="*60)
        print("👑 SWARM TRAINING SUMMARY")
        print("="*60)
        print(f"""
   🐝 Workers:           {summary.get('total_workers', 0)}
   📊 Total Steps:       {summary.get('total_steps', 0)}
   📉 Average Loss:      {summary.get('average_final_loss', 0):.4f}
   ⏱️  Duration:          {summary.get('duration_seconds', 0):.1f}s
   🚀 Steps/Second:      {summary.get('steps_per_second', 0):.1f}
        """)
        print("="*60)
        
        queen_print("farewell")


# =============================================================================
# CLI
# =============================================================================

def signal_handler(sig, frame):
    print("\n\n👑 Queen received interrupt. Swarm shutting down gracefully...")
    sys.exit(0)


if __name__ == "__main__":
    import argparse
    
    signal.signal(signal.SIGINT, signal_handler)
    
    parser = argparse.ArgumentParser(description="👑 VJEPA Swarm Queen")
    parser.add_argument("--workers", type=int, default=4,
                        help="Number of workers")
    parser.add_argument("--data", type=str,
                        default="~/SovereignCore/swarm_vjepa/data/filesystem_knowledge.json",
                        help="Path to filesystem knowledge")
    parser.add_argument("--output", type=str,
                        default="~/SovereignCore/swarm_vjepa/data/trained_model.json",
                        help="Output path for trained model")
    parser.add_argument("--steps", type=int, default=500,
                        help="Max steps per worker")
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("👑 VJEPA SWARM QUEEN")
    print("   Training VJEPA on Your Filesystem")
    print("="*60)
    
    config = SwarmConfig(
        num_workers=args.workers,
        data_path=args.data,
        output_path=args.output,
        max_steps_per_worker=args.steps
    )
    
    queen = SwarmQueen(config)
    results = queen.train_swarm()
    
    if results:
        queen.save_results(results)
        queen.print_summary(results)
