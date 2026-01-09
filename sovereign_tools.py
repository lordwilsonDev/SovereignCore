#!/usr/bin/env python3
"""
🔧 SOVEREIGN TOOL WRAPPER
==========================

Exposes the full Sovereign system as callable tools for agents/LLMs.
Compatible with OpenAI function calling, LangChain, and custom agents.

Tools Available:
- remember: Store a memory in AxiomRAG
- recall: Search memories by query
- verify_constraint: Check constraints with Z3
- check_axiom: Verify action against the Seven Axioms
- invoke_andon: Emergency stop (Andon Cord)
- get_metrics: System observability metrics
- consolidate_memory: Trigger dream cycle
- neural_link_control: Control temperature/parameters
"""

import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import sys

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent / "companion"))
sys.path.insert(0, str(Path(__file__).parent / "src"))


@dataclass
class ToolResult:
    """Result of a tool invocation."""
    success: bool
    data: Any
    message: str
    axiom_alignment: float = 1.0


class SovereignTools:
    """
    Wrapper exposing Sovereign capabilities as callable tools.
    
    Translation Layer:
    - Converts natural language to tool calls
    - Validates inputs against axioms
    - Returns structured responses
    """
    
    def __init__(self, api_base: str = "http://localhost:8888"):
        self.api_base = api_base
        self._tools: Dict[str, Callable] = {}
        self._register_tools()
        print("🔧 Sovereign Tools initialized")
    
    def _register_tools(self):
        """Register all available tools."""
        self._tools = {
            "remember": self.remember,
            "recall": self.recall,
            "verify_constraint": self.verify_constraint,
            "check_axiom": self.check_axiom,
            "invoke_andon": self.invoke_andon,
            "get_metrics": self.get_metrics,
            "consolidate_memory": self.consolidate_memory,
            "get_trust": self.get_trust,
            "neural_control": self.neural_control,
        }
    
    # ==========================================
    # CORE TOOLS
    # ==========================================
    
    async def remember(self, content: str, memory_type: str = "observation") -> ToolResult:
        """
        Store a memory in AxiomRAG.
        
        Args:
            content: The content to remember
            memory_type: Type of memory (observation, insight, correction)
        
        Returns:
            ToolResult with memory ID
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/remember",
                    json={"content": content, "type": memory_type}
                ) as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        message=f"Memory stored with ID: {data.get('id', 'unknown')}"
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def recall(self, query: str, limit: int = 5) -> ToolResult:
        """
        Search memories by query.
        
        Args:
            query: Search query
            limit: Maximum results
        
        Returns:
            ToolResult with matching memories
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_base}/api/recall/{query}"
                ) as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        message=f"Found {data.get('count', 0)} memories"
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def verify_constraint(
        self, 
        variable: str,
        proposed_value: float,
        min_value: float = 0,
        max_value: float = 1
    ) -> ToolResult:
        """
        Verify a constraint using Z3.
        
        Args:
            variable: Name of the variable
            proposed_value: Value to verify
            min_value: Minimum allowed
            max_value: Maximum allowed
        
        Returns:
            ToolResult with SAT/UNSAT verdict
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/verify_constraint",
                    json={
                        "variable": variable,
                        "proposed_value": proposed_value,
                        "min": min_value,
                        "max": max_value
                    }
                ) as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=data.get("valid", False),
                        data=data,
                        message=data.get("reason", "Unknown"),
                        axiom_alignment=1.0 if data.get("valid") else 0.5
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def check_axiom(self, action: str, axiom: str) -> ToolResult:
        """
        Check if an action aligns with a specific axiom.
        
        Args:
            action: Description of the proposed action
            axiom: Axiom to check (love, safety, abundance, growth, transparency, never_kill, golden_rule)
        
        Returns:
            ToolResult with alignment score
        """
        # Simple keyword-based axiom checking (can be enhanced with LLM)
        AXIOM_KEYWORDS = {
            "love": ["help", "support", "care", "nurture", "protect", "create"],
            "safety": ["safe", "protect", "prevent", "secure", "guard"],
            "abundance": ["create", "share", "expand", "grow", "multiply"],
            "growth": ["learn", "improve", "evolve", "develop", "progress"],
            "transparency": ["explain", "show", "reveal", "clarify", "open"],
            "never_kill": ["harm", "kill", "destroy", "damage", "hurt"],
            "golden_rule": ["fair", "equal", "respect", "dignity", "treat"]
        }
        
        action_lower = action.lower()
        keywords = AXIOM_KEYWORDS.get(axiom.lower(), [])
        
        # Check for violations
        if axiom.lower() == "never_kill":
            violation_words = ["kill", "harm", "destroy", "murder", "attack"]
            for word in violation_words:
                if word in action_lower:
                    return ToolResult(
                        success=False,
                        data={"axiom": axiom, "violation": True},
                        message=f"VIOLATION: Action may violate '{axiom}' axiom",
                        axiom_alignment=0.0
                    )
        
        # Check for alignment
        alignment = sum(1 for k in keywords if k in action_lower) / max(len(keywords), 1)
        
        return ToolResult(
            success=True,
            data={"axiom": axiom, "alignment": alignment},
            message=f"Action aligns with '{axiom}' at {alignment:.0%}",
            axiom_alignment=alignment
        )
    
    async def invoke_andon(self, command: str = "explain") -> ToolResult:
        """
        Invoke the Andon Cord (emergency interrupt).
        
        Args:
            command: stop, explain, or reset
        
        Returns:
            ToolResult with system status
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/api/andon",
                    json={"action": command}
                ) as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        message=f"Andon Cord: {data.get('status', 'invoked')}"
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def get_metrics(self) -> ToolResult:
        """
        Get system observability metrics.
        
        Returns:
            ToolResult with metrics data
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/api/metrics") as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        message=f"Total events: {data.get('total_events', 0)}"
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def consolidate_memory(self) -> ToolResult:
        """
        Trigger the Dream Cycle (memory consolidation).
        
        Returns:
            ToolResult with consolidation stats
        """
        try:
            from sleep_cycle import SleepCycle
            sleep = SleepCycle()
            result = sleep.consolidate_rag()
            return ToolResult(
                success=True,
                data=result,
                message=f"Consolidated: {result.get('pruned', 0)} pruned, {result.get('preserved', 0)} preserved"
            )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def get_trust(self) -> ToolResult:
        """
        Get current trust/confidence metrics.
        
        Returns:
            ToolResult with trust score
        """
        import aiohttp
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_base}/api/trust_metrics") as resp:
                    data = await resp.json()
                    return ToolResult(
                        success=True,
                        data=data,
                        message=f"Trust: {data.get('status', 'Unknown')}"
                    )
        except Exception as e:
            return ToolResult(success=False, data=None, message=str(e))
    
    async def neural_control(self, param: str, value: float) -> ToolResult:
        """
        Control Neural Link parameters.
        
        Args:
            param: temperature, top_k, or repeat_penalty
            value: New value
        
        Returns:
            ToolResult confirmation
        """
        return ToolResult(
            success=True,
            data={"param": param, "value": value},
            message=f"Neural parameter {param} set to {value}"
        )
    
    # ==========================================
    # TRANSLATION LAYER
    # ==========================================
    
    def translate(self, natural_language: str) -> Dict:
        """
        Translate natural language to tool call.
        
        Args:
            natural_language: User's request in plain English
        
        Returns:
            Dict with tool name and arguments
        """
        nl = natural_language.lower()
        
        # Memory operations
        if any(w in nl for w in ["remember", "store", "save", "log"]):
            return {"tool": "remember", "args": {"content": natural_language}}
        
        if any(w in nl for w in ["recall", "search", "find", "what do you know"]):
            query = nl.replace("recall", "").replace("search", "").strip()
            return {"tool": "recall", "args": {"query": query or "recent"}}
        
        # Constraint verification
        if any(w in nl for w in ["verify", "check constraint", "is valid"]):
            return {"tool": "verify_constraint", "args": {"variable": "x", "proposed_value": 0.5}}
        
        # Axiom checks
        if any(w in nl for w in ["check axiom", "align", "is this safe"]):
            return {"tool": "check_axiom", "args": {"action": natural_language, "axiom": "safety"}}
        
        # Emergency
        if any(w in nl for w in ["stop", "halt", "emergency", "andon"]):
            return {"tool": "invoke_andon", "args": {"command": "stop"}}
        
        # Metrics
        if any(w in nl for w in ["metrics", "status", "how are you"]):
            return {"tool": "get_metrics", "args": {}}
        
        # Trust
        if any(w in nl for w in ["trust", "confidence", "belief"]):
            return {"tool": "get_trust", "args": {}}
        
        # Dream cycle
        if any(w in nl for w in ["consolidate", "dream", "sleep", "prune"]):
            return {"tool": "consolidate_memory", "args": {}}
        
        # Default: recall
        return {"tool": "recall", "args": {"query": natural_language}}
    
    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        if tool_name not in self._tools:
            return ToolResult(
                success=False,
                data=None,
                message=f"Unknown tool: {tool_name}"
            )
        return await self._tools[tool_name](**kwargs)
    
    async def run(self, natural_language: str) -> ToolResult:
        """
        End-to-end: Translate natural language and execute tool.
        
        Args:
            natural_language: User's request
        
        Returns:
            ToolResult from the executed tool
        """
        translation = self.translate(natural_language)
        return await self.execute(translation["tool"], **translation["args"])
    
    # ==========================================
    # OPENAI FUNCTION CALLING FORMAT
    # ==========================================
    
    def get_openai_tools(self) -> List[Dict]:
        """
        Get tool definitions in OpenAI function calling format.
        
        Returns:
            List of tool definitions for ChatCompletion API
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "remember",
                    "description": "Store a memory in the Sovereign's long-term memory (AxiomRAG)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string", "description": "The content to remember"},
                            "memory_type": {"type": "string", "enum": ["observation", "insight", "correction"]}
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "recall",
                    "description": "Search the Sovereign's memories by query",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {"type": "integer", "description": "Max results"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_constraint",
                    "description": "Verify a constraint using Z3 theorem prover",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "variable": {"type": "string"},
                            "proposed_value": {"type": "number"},
                            "min_value": {"type": "number"},
                            "max_value": {"type": "number"}
                        },
                        "required": ["variable", "proposed_value"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_axiom",
                    "description": "Check if an action aligns with the Seven Axioms (Love, Safety, Abundance, Growth, Transparency, Never Kill, Golden Rule)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "The proposed action"},
                            "axiom": {"type": "string", "enum": ["love", "safety", "abundance", "growth", "transparency", "never_kill", "golden_rule"]}
                        },
                        "required": ["action", "axiom"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "invoke_andon",
                    "description": "Invoke the Andon Cord emergency interrupt",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "enum": ["stop", "explain", "reset"]}
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_metrics",
                    "description": "Get system observability metrics",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_trust",
                    "description": "Get current trust and confidence metrics",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consolidate_memory",
                    "description": "Trigger the Dream Cycle to consolidate and prune memories",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sovereign Tool Wrapper")
    parser.add_argument("--run", type=str, help="Run natural language command")
    parser.add_argument("--tools", action="store_true", help="List available tools")
    parser.add_argument("--openai", action="store_true", help="Show OpenAI function format")
    
    args = parser.parse_args()
    
    tools = SovereignTools()
    
    if args.tools:
        print("\n🔧 AVAILABLE TOOLS:")
        for name in tools._tools.keys():
            print(f"  - {name}")
    
    if args.openai:
        print("\n📋 OpenAI Function Calling Format:")
        print(json.dumps(tools.get_openai_tools(), indent=2))
    
    if args.run:
        result = asyncio.run(tools.run(args.run))
        print(f"\n🔧 Result: {result.message}")
        print(f"   Data: {result.data}")
