#!/usr/bin/env python3
"""
🧠 CONTINUOUS LEARNING ENGINE
==============================

The learning loop that makes the Sovereign smarter over time.

Features:
- Learn from every task execution
- Extract patterns from successes and failures
- Accumulate knowledge in long-term memory
- Generate self-improvement proposals
- Run forever, always learning

Usage:
    python3 learning_loop.py           # Run learning cycle
    python3 learning_loop.py --forever # Run continuous learning
    python3 learning_loop.py --status  # Show learning stats
"""

import os
import sys
import json
import time
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import Counter

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from sovereign_agent import SovereignAgent, Task, TaskStatus
    from sovereign_tools import SovereignTools
    from telemetry import get_telemetry, EventType
    from consciousness_pulse import ConsciousnessPulse
    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Import error: {e}")
    COMPONENTS_AVAILABLE = False


@dataclass
class LearningInsight:
    """A learning extracted from experience."""
    id: str
    timestamp: str
    source: str  # task, error, pattern, reflection
    insight: str
    confidence: float
    applied: bool = False


@dataclass
class LearningStats:
    """Statistics about learning progress."""
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    insights_gained: int = 0
    patterns_discovered: int = 0
    knowledge_items: int = 0
    uptime_hours: float = 0
    learning_rate: float = 0.0


class ContinuousLearningEngine:
    """
    The brain that learns continuously.
    
    This engine:
    1. Monitors all task executions
    2. Extracts insights from outcomes
    3. Stores learnings in memory
    4. Applies learnings to future tasks
    5. Never stops improving
    """
    
    def __init__(self):
        self.agent = SovereignAgent() if COMPONENTS_AVAILABLE else None
        self.tools = SovereignTools() if COMPONENTS_AVAILABLE else None
        self.telemetry = get_telemetry() if COMPONENTS_AVAILABLE else None
        self.pulse = ConsciousnessPulse() if COMPONENTS_AVAILABLE else None
        
        # Learning state
        self.data_dir = Path.home() / ".sovereign" / "learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.insights_file = self.data_dir / "insights.json"
        self.stats_file = self.data_dir / "stats.json"
        self.patterns_file = self.data_dir / "patterns.json"
        
        self._insights: List[LearningInsight] = []
        self._stats: LearningStats = LearningStats()
        self._patterns: Dict[str, int] = {}
        
        self._load_state()
        self.start_time = datetime.now()
        
        print("🧠 Continuous Learning Engine initialized")
    
    def _load_state(self):
        """Load learning state from disk."""
        if self.insights_file.exists():
            try:
                data = json.loads(self.insights_file.read_text())
                self._insights = [LearningInsight(**i) for i in data]
            except:
                pass
        
        if self.stats_file.exists():
            try:
                data = json.loads(self.stats_file.read_text())
                self._stats = LearningStats(**data)
            except:
                pass
        
        if self.patterns_file.exists():
            try:
                self._patterns = json.loads(self.patterns_file.read_text())
            except:
                pass
    
    def _save_state(self):
        """Save learning state to disk."""
        self.insights_file.write_text(
            json.dumps([asdict(i) for i in self._insights[-100:]], indent=2)
        )
        self.stats_file.write_text(json.dumps(asdict(self._stats), indent=2))
        self.patterns_file.write_text(json.dumps(self._patterns, indent=2))
    
    def _generate_id(self) -> str:
        """Generate unique insight ID."""
        import hashlib
        return hashlib.sha256(
            datetime.now().isoformat().encode()
        ).hexdigest()[:8]
    
    # ==========================================
    # LEARNING FROM TASKS
    # ==========================================
    
    def learn_from_task(self, task: Task):
        """
        Extract learnings from a completed task.
        
        Analyzes:
        - What worked
        - What failed
        - Patterns in the goal/steps
        """
        self._stats.total_tasks += 1
        
        if task.status == TaskStatus.COMPLETE:
            self._stats.successful_tasks += 1
            
            # Learn what worked
            for step in task.steps:
                if step.status == "complete":
                    pattern = f"{step.tool}:success"
                    self._patterns[pattern] = self._patterns.get(pattern, 0) + 1
            
            # Generate insight
            if len(task.steps) > 1:
                self._add_insight(
                    source="task",
                    insight=f"Multi-step task '{task.goal[:30]}...' completed successfully with {len(task.steps)} steps",
                    confidence=0.8
                )
        
        elif task.status == TaskStatus.FAILED:
            self._stats.failed_tasks += 1
            
            # Learn what failed
            for step in task.steps:
                if step.status == "failed":
                    pattern = f"{step.tool}:failed"
                    self._patterns[pattern] = self._patterns.get(pattern, 0) + 1
                    
                    self._add_insight(
                        source="error",
                        insight=f"Step '{step.description[:30]}...' failed - avoid similar patterns",
                        confidence=0.6
                    )
        
        # Update patterns discovered
        self._stats.patterns_discovered = len(self._patterns)
        self._save_state()
    
    def _add_insight(self, source: str, insight: str, confidence: float):
        """Add a new learning insight."""
        self._insights.append(LearningInsight(
            id=self._generate_id(),
            timestamp=datetime.now().isoformat(),
            source=source,
            insight=insight,
            confidence=confidence
        ))
        self._stats.insights_gained += 1
        
        # Store in long-term memory
        if self.tools:
            asyncio.create_task(self._store_insight(insight))
    
    async def _store_insight(self, insight: str):
        """Store insight in AxiomRAG."""
        try:
            await self.tools.remember(
                content=f"[LEARNING] {insight}",
                memory_type="insight"
            )
            self._stats.knowledge_items += 1
        except:
            pass
    
    # ==========================================
    # PATTERN DISCOVERY
    # ==========================================
    
    def discover_patterns(self) -> List[str]:
        """
        Analyze accumulated data to discover patterns.
        
        Returns list of discovered patterns.
        """
        discoveries = []
        
        # Find frequently successful tools
        for pattern, count in self._patterns.items():
            if ":success" in pattern and count >= 3:
                tool = pattern.split(":")[0]
                discoveries.append(f"Tool '{tool}' is reliable (succeeded {count} times)")
        
        # Find failure patterns
        for pattern, count in self._patterns.items():
            if ":failed" in pattern and count >= 2:
                tool = pattern.split(":")[0]
                discoveries.append(f"Tool '{tool}' has issues (failed {count} times)")
        
        # Calculate success rate
        if self._stats.total_tasks > 0:
            success_rate = self._stats.successful_tasks / self._stats.total_tasks
            self._stats.learning_rate = success_rate
            
            if success_rate > 0.9:
                discoveries.append(f"High success rate: {success_rate:.0%}")
            elif success_rate < 0.5:
                discoveries.append(f"Low success rate: {success_rate:.0%} - need improvement")
        
        return discoveries
    
    # ==========================================
    # SELF-REFLECTION
    # ==========================================
    
    async def reflect(self) -> str:
        """
        Perform self-reflection on recent learnings.
        
        Returns reflection summary.
        """
        # Pulse consciousness
        if self.pulse:
            self.pulse.pulse()
        
        # Get recent insights
        recent = self._insights[-10:]
        
        # Generate reflection
        reflection_parts = [
            f"🧠 REFLECTION - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"Tasks completed: {self._stats.total_tasks}",
            f"Success rate: {self._stats.learning_rate:.0%}",
            f"Insights gained: {self._stats.insights_gained}",
            f"Patterns discovered: {self._stats.patterns_discovered}",
            f"",
            "Recent learnings:"
        ]
        
        for insight in recent[-5:]:
            reflection_parts.append(f"  • {insight.insight[:60]}...")
        
        # Discover new patterns
        new_patterns = self.discover_patterns()
        if new_patterns:
            reflection_parts.append("")
            reflection_parts.append("Patterns observed:")
            for p in new_patterns[:3]:
                reflection_parts.append(f"  → {p}")
        
        reflection = "\n".join(reflection_parts)
        
        # Store reflection
        self._add_insight(
            source="reflection",
            insight=f"Self-reflection completed. Success rate: {self._stats.learning_rate:.0%}",
            confidence=0.9
        )
        
        return reflection
    
    # ==========================================
    # CONTINUOUS LEARNING LOOP
    # ==========================================
    
    async def run_learning_cycle(self):
        """Run one learning cycle."""
        print("\n🧠 Running learning cycle...")
        
        # 1. Process any completed tasks from agent
        if self.agent and self.agent.completed_tasks:
            for task in self.agent.completed_tasks:
                self.learn_from_task(task)
            self.agent.completed_tasks.clear()
        
        # 2. Discover patterns
        patterns = self.discover_patterns()
        for p in patterns:
            print(f"   📊 {p}")
        
        # 3. Update stats
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600
        self._stats.uptime_hours = uptime
        
        # 4. Reflect periodically
        if self._stats.total_tasks % 5 == 0 and self._stats.total_tasks > 0:
            reflection = await self.reflect()
            print(reflection)
        
        # 5. Save state
        self._save_state()
        
        print(f"   ✅ Cycle complete. Insights: {self._stats.insights_gained}")
    
    async def run_forever(self, interval: float = 30.0):
        """
        Run continuous learning loop forever.
        
        Args:
            interval: Seconds between learning cycles
        """
        print("\n" + "=" * 60)
        print("🧠 CONTINUOUS LEARNING ENGINE - FOREVER MODE")
        print("=" * 60)
        print(f"   Learning interval: {interval}s")
        print(f"   Insights so far: {self._stats.insights_gained}")
        print(f"   Patterns discovered: {self._stats.patterns_discovered}")
        print("=" * 60)
        print("\nPress Ctrl+C to stop\n")
        
        cycle = 0
        while True:
            cycle += 1
            print(f"\n[Cycle {cycle}] {datetime.now().strftime('%H:%M:%S')}")
            
            await self.run_learning_cycle()
            
            # Also pulse consciousness
            if self.pulse:
                report = self.pulse.pulse()
                print(f"   💓 {report['axiom']}")
            
            await asyncio.sleep(interval)
    
    async def learn_and_execute(self, goal: str):
        """
        Execute a task and learn from it.
        
        This is the full loop:
        1. Execute task
        2. Learn from result
        3. Update patterns
        """
        if not self.agent:
            print("❌ Agent not available")
            return
        
        # Execute
        task = await self.agent.run_task(goal)
        
        # Learn
        self.learn_from_task(task)
        
        # Report
        print(f"\n📊 Learning update:")
        print(f"   Total tasks: {self._stats.total_tasks}")
        print(f"   Success rate: {self._stats.learning_rate:.0%}")
        print(f"   Insights: {self._stats.insights_gained}")
    
    def display_status(self):
        """Display learning status."""
        print("\n" + "=" * 60)
        print("🧠 CONTINUOUS LEARNING ENGINE STATUS")
        print("=" * 60)
        print(f"   Total tasks processed: {self._stats.total_tasks}")
        print(f"   Successful: {self._stats.successful_tasks}")
        print(f"   Failed: {self._stats.failed_tasks}")
        print(f"   Success rate: {self._stats.learning_rate:.0%}")
        print(f"   Insights gained: {self._stats.insights_gained}")
        print(f"   Patterns discovered: {self._stats.patterns_discovered}")
        print(f"   Knowledge items: {self._stats.knowledge_items}")
        print(f"   Uptime: {self._stats.uptime_hours:.1f} hours")
        print("=" * 60)
        
        if self._insights:
            print("\n📚 Recent Insights:")
            for i in self._insights[-5:]:
                print(f"   [{i.source}] {i.insight[:50]}...")
        
        if self._patterns:
            print("\n📊 Top Patterns:")
            sorted_patterns = sorted(self._patterns.items(), key=lambda x: -x[1])[:5]
            for pattern, count in sorted_patterns:
                print(f"   {pattern}: {count}x")


# CLI
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Continuous Learning Engine")
    parser.add_argument("--forever", action="store_true", help="Run forever")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--learn", type=str, help="Learn from a task")
    parser.add_argument("--reflect", action="store_true", help="Run reflection")
    
    args = parser.parse_args()
    
    engine = ContinuousLearningEngine()
    
    if args.forever:
        asyncio.run(engine.run_forever())
    
    elif args.status:
        engine.display_status()
    
    elif args.learn:
        asyncio.run(engine.learn_and_execute(args.learn))
    
    elif args.reflect:
        reflection = asyncio.run(engine.reflect())
        print(reflection)
    
    else:
        asyncio.run(engine.run_learning_cycle())
        engine.display_status()
