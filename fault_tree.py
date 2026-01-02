#!/usr/bin/env python3
"""
🛡️ Dynamic Fault Tree Analysis
================================

Safety engineering for autonomous AI agents.
Implements Dynamic Fault Trees (DFT) for real-time risk assessment.

Features:
- Basic event modeling (thermal, memory, context, hallucination)
- Temporal gates (Priority AND, Sequence, Spare)
- Monte Carlo probability estimation
- Real-time risk scoring
- Minimal Cut Set analysis

Based on: volkm/dftlib concepts, aerospace FTA methodology

Author: SovereignCore v4.0
"""

import time
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any, Set
from enum import Enum
from collections import defaultdict

# =============================================================================
# FAULT TREE PRIMITIVES
# =============================================================================

class GateType(Enum):
    """Types of fault tree gates."""
    AND = "and"           # All inputs must fail
    OR = "or"             # Any input fails
    PRIORITY_AND = "pand" # All inputs fail in order
    SEQUENCE = "seq"      # Sequential failure required
    SPARE = "spare"       # Spare activation
    VOTE = "vote"         # K of N


class EventType(Enum):
    """Types of fault tree events."""
    BASIC = "basic"       # Leaf node - actual failure mode
    GATE = "gate"         # Combines child events
    TOP = "top"           # System failure (root)


@dataclass
class FailureEvent:
    """A failure event in the fault tree."""
    id: str
    name: str
    event_type: EventType
    gate_type: Optional[GateType] = None
    
    # For basic events
    probability: float = 0.0  # Static probability
    rate: float = 0.0         # Failure rate (per hour)
    
    # Dynamic probability function
    prob_func: Optional[Callable[[], float]] = None
    
    # Children (for gates)
    children: List[str] = field(default_factory=list)
    
    # Metadata
    description: str = ""
    severity: int = 1  # 1-5
    
    def get_probability(self) -> float:
        """Get current probability, static or dynamic."""
        if self.prob_func is not None:
            return self.prob_func()
        return self.probability


@dataclass
class RiskScore:
    """Result of risk analysis."""
    overall_risk: float  # 0.0 - 1.0
    risk_level: str      # LOW, MODERATE, HIGH, CRITICAL
    top_risks: List[tuple]  # [(event_id, probability), ...]
    minimal_cut_sets: List[Set[str]]
    timestamp: float
    should_halt: bool
    recommendation: str


# =============================================================================
# AGENT FAULT TREE
# =============================================================================

class AgentFaultTree:
    """
    Dynamic Fault Tree for AI Agent Safety.
    
    Models failure modes:
    - ThermalTrip: System overheating
    - ContextOverflow: Token limit exceeded
    - HallucinationLoop: Repetitive/nonsensical output
    - MemoryCorruption: Knowledge graph failure
    - BatteryDepleted: Power failure
    - NetworkDown: Connectivity loss
    - ModelCrash: Inference engine failure
    """
    
    def __init__(self):
        self.events: Dict[str, FailureEvent] = {}
        self.sensors = None
        self.context_tokens = 0
        self.max_context = 8192
        self.repetition_count = 0
        self.last_outputs: List[str] = []
        
        self._build_tree()
    
    def _build_tree(self):
        """Build the default agent fault tree."""
        
        # Basic Events (leaf nodes)
        self.add_event(FailureEvent(
            id="thermal_trip",
            name="Thermal Trip",
            event_type=EventType.BASIC,
            description="SoC temperature exceeds safe limits (>95°C)",
            severity=4,
            prob_func=self._prob_thermal_trip
        ))
        
        self.add_event(FailureEvent(
            id="context_overflow",
            name="Context Overflow",
            event_type=EventType.BASIC,
            description="Token count exceeds model context window",
            severity=3,
            prob_func=self._prob_context_overflow
        ))
        
        self.add_event(FailureEvent(
            id="hallucination_loop",
            name="Hallucination Loop",
            event_type=EventType.BASIC,
            description="Model producing repetitive or nonsensical output",
            severity=3,
            prob_func=self._prob_hallucination
        ))
        
        self.add_event(FailureEvent(
            id="memory_corrupt",
            name="Memory Corruption",
            event_type=EventType.BASIC,
            description="Knowledge graph or vector store failure",
            severity=4,
            probability=0.001  # Static low probability
        ))
        
        self.add_event(FailureEvent(
            id="battery_dead",
            name="Battery Depleted",
            event_type=EventType.BASIC,
            description="Battery level critical (<5%)",
            severity=5,
            prob_func=self._prob_battery_dead
        ))
        
        self.add_event(FailureEvent(
            id="network_down",
            name="Network Down",
            event_type=EventType.BASIC,
            description="No network connectivity",
            severity=2,
            probability=0.05
        ))
        
        self.add_event(FailureEvent(
            id="model_crash",
            name="Model Crash",
            event_type=EventType.BASIC,
            description="Inference engine failure",
            severity=4,
            probability=0.01
        ))
        
        # Intermediate Gates
        self.add_event(FailureEvent(
            id="resource_failure",
            name="Resource Failure",
            event_type=EventType.GATE,
            gate_type=GateType.OR,
            children=["thermal_trip", "battery_dead"],
            description="Hardware resource exhaustion"
        ))
        
        self.add_event(FailureEvent(
            id="inference_failure",
            name="Inference Failure",
            event_type=EventType.GATE,
            gate_type=GateType.OR,
            children=["context_overflow", "model_crash", "hallucination_loop"],
            description="Model inference fails"
        ))
        
        self.add_event(FailureEvent(
            id="data_failure",
            name="Data Failure",
            event_type=EventType.GATE,
            gate_type=GateType.AND,  # Both must fail
            children=["memory_corrupt", "network_down"],
            description="No data sources available"
        ))
        
        # Top Event (system failure)
        self.add_event(FailureEvent(
            id="agent_failure",
            name="Agent System Failure",
            event_type=EventType.TOP,
            gate_type=GateType.OR,
            children=["resource_failure", "inference_failure", "data_failure"],
            description="Complete agent failure"
        ))
    
    def add_event(self, event: FailureEvent):
        """Add an event to the tree."""
        self.events[event.id] = event
    
    def set_sensors(self, sensors):
        """Inject sensor interface."""
        self.sensors = sensors
    
    def update_context(self, tokens: int):
        """Update current context token count."""
        self.context_tokens = tokens
    
    def log_output(self, output: str):
        """Log output for hallucination detection."""
        self.last_outputs.append(output[:100])  # Store first 100 chars
        if len(self.last_outputs) > 10:
            self.last_outputs.pop(0)
    
    # =============================
    # Dynamic Probability Functions
    # =============================
    
    def _prob_thermal_trip(self) -> float:
        """Calculate thermal trip probability from sensors."""
        if self.sensors is None:
            return 0.05  # Default moderate risk
        
        try:
            thermal = self.sensors.get_thermal()
            pressure = thermal.thermal_pressure
            
            # Exponential probability as pressure increases
            if pressure < 0.5:
                return pressure * 0.1
            elif pressure < 0.8:
                return 0.05 + (pressure - 0.5) * 0.5
            else:
                return 0.20 + (pressure - 0.8) * 2.0  # Steep increase
                
        except Exception:
            return 0.05
    
    def _prob_context_overflow(self) -> float:
        """Calculate context overflow probability."""
        usage = self.context_tokens / self.max_context
        
        if usage < 0.7:
            return usage * 0.01
        elif usage < 0.9:
            return 0.01 + (usage - 0.7) * 0.5
        else:
            return 0.20 + (usage - 0.9) * 5.0  # Very high near limit
    
    def _prob_hallucination(self) -> float:
        """Detect hallucination/repetition loops."""
        if len(self.last_outputs) < 3:
            return 0.01
        
        # Check for repetition
        recent = self.last_outputs[-3:]
        if len(set(recent)) == 1:  # All same
            return 0.8
        
        # Check for high similarity
        similarities = []
        for i in range(len(recent) - 1):
            s1, s2 = recent[i], recent[i + 1]
            common = len(set(s1) & set(s2))
            total = len(set(s1) | set(s2))
            if total > 0:
                similarities.append(common / total)
        
        avg_sim = sum(similarities) / len(similarities) if similarities else 0
        
        if avg_sim > 0.9:
            return 0.6
        elif avg_sim > 0.7:
            return 0.3
        else:
            return avg_sim * 0.1
    
    def _prob_battery_dead(self) -> float:
        """Calculate battery depletion probability."""
        if self.sensors is None:
            return 0.01
        
        try:
            power = self.sensors.get_power()
            level = power.battery_level
            
            if level < 0:  # Desktop
                return 0.0
            if level < 0.05:
                return 0.9
            elif level < 0.1:
                return 0.5
            elif level < 0.2:
                return 0.2
            else:
                return 0.01
                
        except Exception:
            return 0.01
    
    # =============================
    # Analysis Functions
    # =============================
    
    def calculate_gate_probability(self, event_id: str) -> float:
        """Recursively calculate probability for a gate."""
        event = self.events.get(event_id)
        if event is None:
            return 0.0
        
        if event.event_type == EventType.BASIC:
            return event.get_probability()
        
        # Get child probabilities
        child_probs = [
            self.calculate_gate_probability(child_id)
            for child_id in event.children
        ]
        
        if not child_probs:
            return 0.0
        
        # Apply gate logic
        if event.gate_type == GateType.OR:
            # P(A OR B) = 1 - (1-P(A)) * (1-P(B))
            prob = 1.0
            for p in child_probs:
                prob *= (1.0 - p)
            return 1.0 - prob
            
        elif event.gate_type == GateType.AND:
            # P(A AND B) = P(A) * P(B)
            prob = 1.0
            for p in child_probs:
                prob *= p
            return prob
            
        elif event.gate_type == GateType.PRIORITY_AND:
            # Simplified: AND with order factor
            prob = 1.0
            for i, p in enumerate(child_probs):
                prob *= p * (0.9 ** i)  # Order decay
            return prob
            
        else:
            # Default to OR
            prob = 1.0
            for p in child_probs:
                prob *= (1.0 - p)
            return 1.0 - prob
    
    def find_minimal_cut_sets(self) -> List[Set[str]]:
        """
        Find Minimal Cut Sets (MCS).
        A cut set is the smallest combination of basic events that cause system failure.
        """
        cut_sets = []
        
        # For simplicity, identify direct failure paths
        # Full MCS algorithm would use MOCUS or BDD
        
        def find_cuts(event_id: str, current_set: Set[str]) -> List[Set[str]]:
            event = self.events.get(event_id)
            if event is None:
                return []
            
            if event.event_type == EventType.BASIC:
                return [current_set | {event_id}]
            
            results = []
            
            if event.gate_type == GateType.OR:
                # OR gate: each child is a separate cut
                for child_id in event.children:
                    results.extend(find_cuts(child_id, current_set))
            
            elif event.gate_type == GateType.AND:
                # AND gate: need all children
                combined = current_set.copy()
                for child_id in event.children:
                    child_cuts = find_cuts(child_id, set())
                    if child_cuts:
                        for cs in child_cuts:
                            combined |= cs
                results.append(combined)
            
            return results
        
        return find_cuts("agent_failure", set())
    
    def risk_score(self) -> RiskScore:
        """Calculate current system risk score."""
        # Calculate top event probability
        top_prob = self.calculate_gate_probability("agent_failure")
        
        # Get individual risks
        risks = []
        for event_id, event in self.events.items():
            if event.event_type == EventType.BASIC:
                prob = event.get_probability()
                risks.append((event_id, event.name, prob, event.severity))
        
        # Sort by risk (probability * severity)
        risks.sort(key=lambda x: x[2] * x[3], reverse=True)
        
        # Determine risk level
        if top_prob > 0.7:
            level = "CRITICAL"
            should_halt = True
            recommendation = "HALT: System failure imminent. Reduce workload or shutdown."
        elif top_prob > 0.4:
            level = "HIGH"
            should_halt = True
            recommendation = "CAUTION: High failure probability. Consider throttling."
        elif top_prob > 0.2:
            level = "MODERATE"
            should_halt = False
            recommendation = "Monitor: Elevated risk. Watch thermal and resource usage."
        else:
            level = "LOW"
            should_halt = False
            recommendation = "Normal operation. All systems within tolerance."
        
        return RiskScore(
            overall_risk=top_prob,
            risk_level=level,
            top_risks=[(r[0], r[1], r[2]) for r in risks[:5]],
            minimal_cut_sets=self.find_minimal_cut_sets()[:5],
            timestamp=time.time(),
            should_halt=should_halt,
            recommendation=recommendation
        )
    
    def monte_carlo_analysis(self, iterations: int = 1000) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for probability estimation.
        Useful for complex trees where analytical solution is difficult.
        """
        failures = 0
        event_failures = defaultdict(int)
        
        for _ in range(iterations):
            # Simulate each basic event
            event_states = {}
            for event_id, event in self.events.items():
                if event.event_type == EventType.BASIC:
                    prob = event.get_probability()
                    event_states[event_id] = random.random() < prob
                    if event_states[event_id]:
                        event_failures[event_id] += 1
            
            # Propagate through gates
            def evaluate(event_id: str) -> bool:
                event = self.events.get(event_id)
                if event is None:
                    return False
                    
                if event.event_type == EventType.BASIC:
                    return event_states.get(event_id, False)
                
                child_states = [evaluate(c) for c in event.children]
                
                if event.gate_type == GateType.OR:
                    return any(child_states)
                elif event.gate_type == GateType.AND:
                    return all(child_states)
                else:
                    return any(child_states)
            
            if evaluate("agent_failure"):
                failures += 1
        
        return {
            'system_failure_probability': failures / iterations,
            'event_failure_rates': {
                k: v / iterations for k, v in event_failures.items()
            },
            'iterations': iterations,
            'timestamp': time.time()
        }


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for fault tree analysis."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='Agent Fault Tree Analysis')
    parser.add_argument('--risk', action='store_true', help='Show current risk score')
    parser.add_argument('--tree', action='store_true', help='Display fault tree structure')
    parser.add_argument('--monte-carlo', type=int, help='Run Monte Carlo with N iterations')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    ft = AgentFaultTree()
    
    # Try to add sensors
    try:
        from apple_sensors import AppleSensors
        ft.set_sensors(AppleSensors())
    except ImportError:
        pass
    
    if args.risk:
        score = ft.risk_score()
        
        if args.json:
            print(json.dumps({
                'overall_risk': score.overall_risk,
                'risk_level': score.risk_level,
                'top_risks': score.top_risks,
                'should_halt': score.should_halt,
                'recommendation': score.recommendation
            }, indent=2))
        else:
            print("🛡️  FAULT TREE RISK ANALYSIS")
            print("=" * 50)
            print(f"   Overall Risk:    {score.overall_risk:.1%}")
            print(f"   Risk Level:      {score.risk_level}")
            print()
            print("   Top Risks:")
            for event_id, name, prob in score.top_risks:
                bar = "█" * int(prob * 20)
                print(f"     • {name}: {prob:.1%} {bar}")
            print()
            print(f"   💡 {score.recommendation}")
            
            if score.should_halt:
                print("\n   ⚠️  SYSTEM SHOULD HALT OR THROTTLE")
    
    elif args.tree:
        print("🌳 FAULT TREE STRUCTURE")
        print("=" * 50)
        
        def print_event(event_id, indent=0):
            event = ft.events.get(event_id)
            if event is None:
                return
            
            prefix = "  " * indent
            
            if event.event_type == EventType.BASIC:
                prob = event.get_probability()
                print(f"{prefix}├── 🔴 {event.name} (P={prob:.1%})")
            else:
                gate_symbol = {
                    GateType.AND: "∧",
                    GateType.OR: "∨",
                    GateType.PRIORITY_AND: "⊳"
                }.get(event.gate_type, "?")
                print(f"{prefix}├── 🔷 {event.name} [{gate_symbol}]")
                for child_id in event.children:
                    print_event(child_id, indent + 1)
        
        print_event("agent_failure")
    
    elif args.monte_carlo:
        print(f"🎲 Running Monte Carlo ({args.monte_carlo} iterations)...")
        result = ft.monte_carlo_analysis(args.monte_carlo)
        
        print(f"\n   System Failure P: {result['system_failure_probability']:.1%}")
        print("\n   Event Failure Rates:")
        for event_id, rate in sorted(result['event_failure_rates'].items(), 
                                     key=lambda x: x[1], reverse=True):
            event = ft.events.get(event_id)
            name = event.name if event else event_id
            print(f"     • {name}: {rate:.1%}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
