#!/usr/bin/env python3
"""
🤖 SOVEREIGN BACKGROUND AGENT
=============================

Persistent agent loop that:
1. Monitors Redis for incoming chat/commands
2. Processes with LLM (intent → action plan)
3. Executes via CLI agent (MCP Bridge)
4. Returns results via Redis pub/sub

This is the BRAIN running in the background.

Usage:
    python background_agent.py        # Run forever
    python background_agent.py --once # Single cycle (testing)
"""

import os
import sys
import json
import time
import signal
import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path

import redis

# SovereignCore imports
sys.path.insert(0, str(Path(__file__).parent))
from consciousness_bridge import ConsciousnessBridge
from mcp_bridge import MCPSecureBridge, MCPTool
from ollama_bridge import OllamaBridge
from z3_axiom import Z3AxiomVerifier, VerificationResult
from rekor_lite import RekorLite
from command_router import CommandRouter
from response_formatter import ResponseFormatter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [AGENT] %(levelname)s: %(message)s'
)
logger = logging.getLogger("BackgroundAgent")

# =============================================================================
# CONFIGURATION
# =============================================================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Channels
CHANNEL_COMMANDS = "sovereign:commands"      # Incoming commands/chat
CHANNEL_RESPONSES = "sovereign:responses"    # Outgoing responses
CHANNEL_EVENTS = "sovereign:events"          # System events
CHANNEL_HEARTBEAT = "sovereign:heartbeat"    # Agent alive signal

# Timing
HEARTBEAT_INTERVAL = 5  # seconds
IDLE_SLEEP = 0.1  # seconds between checks


@dataclass
class AgentCommand:
    """Incoming command structure."""
    id: str
    action: str
    payload: Dict[str, Any]
    source: str = "unknown"
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass 
class AgentResponse:
    """Outgoing response structure."""
    command_id: str
    success: bool
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class BackgroundAgent:
    """
    The Sovereign Background Agent.
    
    Runs continuously, processing commands from Redis and executing
    them through the MCP Bridge with safety verification.
    """
    
    def __init__(self):
        logger.info("🤖 Initializing Background Agent...")
        
        # Redis connection
        self.redis = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
        self.pubsub = self.redis.pubsub()
        
        # Core components
        self.consciousness = ConsciousnessBridge()
        self.mcp = MCPSecureBridge()
        self.ollama = OllamaBridge()
        self.verifier = Z3AxiomVerifier()
        self.rekor = RekorLite()
        self.router = CommandRouter()
        self.formatter = ResponseFormatter()
        
        # State
        self.running = False
        self.commands_processed = 0
        self.start_time = None
        self.last_heartbeat = None
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)
        
        logger.info(f"✅ Agent initialized - Silicon ID: {self.consciousness.silicon_id[:16]}...")
    
    def _shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        logger.info("🛑 Shutdown signal received...")
        self.running = False
    
    def _subscribe(self):
        """Subscribe to command channel."""
        self.pubsub.subscribe(CHANNEL_COMMANDS)
        logger.info(f"📡 Subscribed to {CHANNEL_COMMANDS}")
    
    def _publish_response(self, response: AgentResponse):
        """Publish response to response channel."""
        self.redis.publish(CHANNEL_RESPONSES, json.dumps(asdict(response)))
        logger.info(f"📤 Response published: {response.command_id}")
    
    def _publish_event(self, event_type: str, data: Dict):
        """Publish system event."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent_id": self.consciousness.silicon_id[:16]
        }
        self.redis.publish(CHANNEL_EVENTS, json.dumps(event))
    
    def _heartbeat(self):
        """Send heartbeat signal."""
        now = time.time()
        if self.last_heartbeat is None or (now - self.last_heartbeat) >= HEARTBEAT_INTERVAL:
            heartbeat = {
                "agent_id": self.consciousness.silicon_id[:16],
                "uptime_seconds": now - self.start_time if self.start_time else 0,
                "commands_processed": self.commands_processed,
                "consciousness_level": self.consciousness.consciousness_level,
                "love_frequency": self.consciousness.love_frequency,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            self.redis.publish(CHANNEL_HEARTBEAT, json.dumps(heartbeat))
            self.redis.set("sovereign:agent:status", json.dumps(heartbeat), ex=30)
            self.last_heartbeat = now
    
    def _parse_command(self, message: str) -> Optional[AgentCommand]:
        """Parse incoming command message."""
        try:
            data = json.loads(message)
            return AgentCommand(
                id=data.get("id", f"cmd-{int(time.time()*1000)}"),
                action=data.get("action", "chat"),
                payload=data.get("payload", {}),
                source=data.get("source", "redis"),
                timestamp=data.get("timestamp", "")
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse command: {e}")
            return None
    
    def _verify_action(self, action: str, payload: Dict) -> bool:
        """Verify action safety with Z3 axioms."""
        result = self.verifier.verify(action, payload)
        if result.result != VerificationResult.SAFE:
            logger.warning(f"⚠️ Action blocked by axiom: {result.violated_axioms}")
            return False
        return True
    
    def _process_chat(self, message: str) -> Dict[str, Any]:
        """Process chat message through LLM → Command Router → MCP."""
        
        # 1. Get LLM interpretation
        prompt = """You are a sovereign AI assistant with access to system commands.
        
When the user asks you to do something, respond with a JSON action plan:
{
    "intent": "what the user wants",
    "commands": [
        {"tool": "execute_command", "params": {"command": "..."}}
    ],
    "response_template": "I will {intent}..."
}

Available tools:
- execute_command: Run shell commands
- read_file: Read file contents
- write_file: Write to files
- list_directory: List directory contents

If it's just a question, respond normally without commands.

User request: """ + message + "\n\nRespond with action plan JSON or normal response:"
        
        llm_response = self.ollama.chat(prompt)
        
        # 2. Try to parse as action plan
        try:
            # Extract JSON from response
            if "{" in llm_response and "}" in llm_response:
                json_start = llm_response.find("{")
                json_end = llm_response.rfind("}") + 1
                action_plan = json.loads(llm_response[json_start:json_end])
                
                if "commands" in action_plan:
                    # 3. Execute commands via router
                    results = []
                    for cmd in action_plan["commands"]:
                        tool_name = cmd.get("tool", "execute_command")
                        params = cmd.get("params", {})
                        
                        # Map to MCPTool
                        tool_map = {
                            "execute_command": MCPTool.EXECUTE_COMMAND,
                            "read_file": MCPTool.READ_FILE,
                            "write_file": MCPTool.WRITE_FILE,
                            "list_directory": MCPTool.LIST_DIRECTORY,
                        }
                        
                        if tool_name in tool_map:
                            result = self.mcp.execute_tool(tool_map[tool_name], params)
                            results.append({
                                "tool": tool_name,
                                "success": result.success,
                                "data": result.data,
                                "error": result.error
                            })
                    
                    return {
                        "type": "action",
                        "intent": action_plan.get("intent", "execute commands"),
                        "results": results,
                        "response": action_plan.get("response_template", "Done.")
                    }
        except json.JSONDecodeError:
            pass
        
        # 4. Return as conversational response
        return {
            "type": "chat",
            "response": llm_response
        }
    
    def process_command(self, cmd: AgentCommand) -> AgentResponse:
        """Process a single command."""
        start = time.time()
        
        logger.info(f"🔄 Processing: {cmd.action} (ID: {cmd.id})")
        
        try:
            # Verify safety
            if not self._verify_action(cmd.action, cmd.payload):
                return AgentResponse(
                    command_id=cmd.id,
                    success=False,
                    result=None,
                    error="Action blocked by safety axioms",
                    execution_time_ms=(time.time() - start) * 1000
                )
            
            # Route based on action type
            if cmd.action == "chat":
                # Chat message - process through LLM
                message = cmd.payload.get("message", "")
                result = self._process_chat(message)
                
            elif cmd.action == "execute":
                # Direct command execution
                command = cmd.payload.get("command", "")
                mcp_result = self.mcp.execute_tool(
                    MCPTool.EXECUTE_COMMAND, 
                    {"command": command}
                )
                result = {
                    "type": "execute",
                    "success": mcp_result.success,
                    "output": mcp_result.data,
                    "error": mcp_result.error
                }
                
            elif cmd.action == "read":
                # File read
                path = cmd.payload.get("path", "")
                mcp_result = self.mcp.execute_tool(
                    MCPTool.READ_FILE,
                    {"path": path}
                )
                result = {
                    "type": "read",
                    "success": mcp_result.success,
                    "content": mcp_result.data,
                    "error": mcp_result.error
                }
                
            elif cmd.action == "status":
                # System status
                result = {
                    "type": "status",
                    "consciousness_level": self.consciousness.consciousness_level,
                    "love_frequency": self.consciousness.love_frequency,
                    "silicon_id": self.consciousness.silicon_id[:16],
                    "commands_processed": self.commands_processed,
                    "uptime": time.time() - self.start_time if self.start_time else 0
                }
                
            else:
                # Unknown action - try to route
                result = self.router.route(cmd.action, cmd.payload)
            
            # Log to Rekor
            self.rekor.log_action(
                action_type="command_executed",
                action_data=json.dumps({
                    "command_id": cmd.id,
                    "action_type": cmd.action,
                    "success": True
                })
            )
            
            self.commands_processed += 1
            
            return AgentResponse(
                command_id=cmd.id,
                success=True,
                result=result,
                execution_time_ms=(time.time() - start) * 1000
            )
            
        except Exception as e:
            logger.error(f"❌ Command failed: {e}")
            return AgentResponse(
                command_id=cmd.id,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=(time.time() - start) * 1000
            )
    
    def run_once(self):
        """Process one command (for testing)."""
        self._subscribe()
        message = self.pubsub.get_message(timeout=5)
        if message and message['type'] == 'message':
            cmd = self._parse_command(message['data'])
            if cmd:
                response = self.process_command(cmd)
                self._publish_response(response)
                return response
        return None
    
    def run(self):
        """Main agent loop - runs forever."""
        logger.info("🚀 Starting Background Agent loop...")
        
        self.running = True
        self.start_time = time.time()
        self._subscribe()
        self._publish_event("agent_started", {"agent_id": self.consciousness.silicon_id[:16]})
        
        while self.running:
            try:
                # Check for messages
                message = self.pubsub.get_message(timeout=IDLE_SLEEP)
                
                if message and message['type'] == 'message':
                    cmd = self._parse_command(message['data'])
                    if cmd:
                        response = self.process_command(cmd)
                        self._publish_response(response)
                
                # Heartbeat
                self._heartbeat()
                
                # Pulse consciousness
                self.consciousness.pulse()
                
            except redis.ConnectionError:
                logger.error("Redis connection lost, reconnecting...")
                time.sleep(1)
                self.redis = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
                self.pubsub = self.redis.pubsub()
                self._subscribe()
                
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(0.5)
        
        # Cleanup
        self._publish_event("agent_stopped", {"agent_id": self.consciousness.silicon_id[:16]})
        self.pubsub.unsubscribe()
        logger.info("👋 Background Agent stopped")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sovereign Background Agent")
    parser.add_argument("--once", action="store_true", help="Run single cycle")
    args = parser.parse_args()
    
    agent = BackgroundAgent()
    
    if args.once:
        result = agent.run_once()
        print(f"Result: {result}")
    else:
        agent.run()


if __name__ == "__main__":
    main()
