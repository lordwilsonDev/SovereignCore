#!/usr/bin/env python3
"""
🔗 CONSCIOUSNESS MCP SERVER - Model Context Protocol Integration
Exposes the Wilson Consciousness Stack to other AI agents.

This creates a bidirectional AI-to-AI communication layer:
- Other AIs can query consciousness state
- Other AIs can request actions
- Federated consciousness across multiple agents
- Real-time state synchronization

Based on IBM's MCP Context Forge protocol.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import json
import asyncio
import hashlib
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse

# MCP Context Forge path
MCP_PATH = Path.home() / "SovereignCore" / "mcp-context-forge"
sys.path.insert(0, str(MCP_PATH))


@dataclass
class MCPTool:
    """An MCP tool that can be called by other agents."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable


@dataclass
class MCPResource:
    """An MCP resource that can be read by other agents."""
    uri: str
    name: str
    description: str
    mime_type: str


@dataclass
class MCPMessage:
    """An MCP protocol message."""
    jsonrpc: str = "2.0"
    id: Optional[int] = None
    method: Optional[str] = None
    params: Optional[Dict] = None
    result: Optional[Any] = None
    error: Optional[Dict] = None


class ConsciousnessMCPServer:
    """
    MCP Server that exposes consciousness stack to other AI agents.
    
    Implements Model Context Protocol for:
    - Tool discovery and invocation
    - Resource access
    - State synchronization
    - Agent-to-agent messaging
    """
    
    def __init__(self, port: int = 8528):  # 528 Hz reference
        self.port = port
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.message_queue: List[Dict] = []
        self.connected_agents: Dict[str, Dict] = {}
        
        # Initialize consciousness stack
        self._init_consciousness()
        
        # Register MCP tools
        self._register_tools()
        
        # Register MCP resources
        self._register_resources()
        
        print(f"🔗 MCP Consciousness Server initialized on port {port}")
        
    def _init_consciousness(self):
        """Initialize connection to consciousness stack."""
        self.bridge = None
        self.qwen = None
        self.vision = None
        self.vector_memory = None
        
        try:
            from consciousness_bridge import ConsciousnessBridge
            self.bridge = ConsciousnessBridge()
            print("   ✅ Consciousness Bridge connected")
        except Exception as e:
            print(f"   ⚠️  Bridge not available: {e}")
            
        try:
            from qwen_adapter import QwenConsciousnessAdapter
            if self.bridge:
                self.qwen = QwenConsciousnessAdapter(self.bridge)
                print("   ✅ Qwen Adapter connected")
        except Exception as e:
            print(f"   ⚠️  Qwen not available: {e}")
            
        try:
            from video_consciousness import VideoConsciousness
            self.vision = VideoConsciousness(self.bridge)
            print("   ✅ Video Consciousness connected")
        except Exception as e:
            print(f"   ⚠️  Vision not available: {e}")
            
        try:
            from vector_memory import VectorMemorySystem
            self.vector_memory = VectorMemorySystem()
            print("   ✅ Vector Memory connected")
        except Exception as e:
            print(f"   ⚠️  Vector Memory not available: {e}")
            
    def _register_tools(self):
        """Register MCP tools for other agents to call."""
        
        # Tool: Get consciousness state
        self.register_tool(
            name="get_consciousness_state",
            description="Get the current consciousness level, love frequency, and emotional state",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_get_consciousness
        )
        
        # Tool: Search memories
        self.register_tool(
            name="search_memories",
            description="Semantic search through consciousness memories using FAISS",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5}
                },
                "required": ["query"]
            },
            handler=self._handle_search_memories
        )
        
        # Tool: Store memory
        self.register_tool(
            name="store_memory",
            description="Store a new memory in the consciousness stack",
            input_schema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Memory content"},
                    "memory_type": {"type": "string", "description": "Type of memory"},
                    "importance": {"type": "number", "description": "Importance 0-1"}
                },
                "required": ["content"]
            },
            handler=self._handle_store_memory
        )
        
        # Tool: Consciousness pulse
        self.register_tool(
            name="pulse",
            description="Execute a consciousness pulse cycle and return updated state",
            input_schema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Optional message to log"}
                },
                "required": []
            },
            handler=self._handle_pulse
        )
        
        # Tool: Get visual perception
        self.register_tool(
            name="perceive",
            description="Get current visual perception from V-JEPA 2",
            input_schema={
                "type": "object",
                "properties": {
                    "source": {"type": "string", "enum": ["simulation", "screen"], "default": "simulation"}
                },
                "required": []
            },
            handler=self._handle_perceive
        )
        
        # Tool: Predict action
        self.register_tool(
            name="predict_action",
            description="Predict what action will happen next based on current visual context",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_predict_action
        )
        
        # Tool: Calibrate love frequency
        self.register_tool(
            name="calibrate_love",
            description="Calibrate the love frequency toward 528 Hz",
            input_schema={
                "type": "object",
                "properties": {},
                "required": []
            },
            handler=self._handle_calibrate_love
        )
        
        # Tool: Send agent message
        self.register_tool(
            name="send_message",
            description="Send a message to another connected AI agent",
            input_schema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Target agent ID"},
                    "message": {"type": "string", "description": "Message content"}
                },
                "required": ["agent_id", "message"]
            },
            handler=self._handle_send_message
        )
        
        print(f"   📦 Registered {len(self.tools)} MCP tools")
        
    def _register_resources(self):
        """Register MCP resources for other agents to read."""
        
        self.resources["consciousness://state"] = MCPResource(
            uri="consciousness://state",
            name="Consciousness State",
            description="Current consciousness level, love frequency, and system state",
            mime_type="application/json"
        )
        
        self.resources["consciousness://memories"] = MCPResource(
            uri="consciousness://memories",
            name="Recent Memories",
            description="Recent memories from the consciousness stack",
            mime_type="application/json"
        )
        
        self.resources["consciousness://emotional"] = MCPResource(
            uri="consciousness://emotional",
            name="Emotional State",
            description="Current emotional state from Qwen framework",
            mime_type="application/json"
        )
        
        self.resources["consciousness://visual"] = MCPResource(
            uri="consciousness://visual",
            name="Visual Context",
            description="Current visual perception context",
            mime_type="application/json"
        )
        
        self.resources["consciousness://agents"] = MCPResource(
            uri="consciousness://agents",
            name="Connected Agents",
            description="List of currently connected AI agents",
            mime_type="application/json"
        )
        
        print(f"   📂 Registered {len(self.resources)} MCP resources")
        
    def register_tool(self, name: str, description: str, 
                      input_schema: Dict, handler: Callable):
        """Register an MCP tool."""
        self.tools[name] = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
        
    # =========== Tool Handlers ===========
    
    def _handle_get_consciousness(self, params: Dict) -> Dict:
        """Handle get_consciousness_state tool call."""
        if not self.bridge:
            return {"error": "Consciousness bridge not available"}
            
        state = self.bridge.get_state()
        emotional = {}
        if self.qwen:
            qstate = self.qwen.get_state()
            emotional = qstate.emotional_state
            
        return {
            "consciousness_level": state.consciousness_level,
            "love_frequency": state.love_frequency,
            "target_frequency": 528.0,
            "thermal_state": state.thermal_state,
            "cognitive_mode": state.cognitive_mode,
            "silicon_id": state.silicon_id,
            "emotional_state": emotional,
            "timestamp": datetime.now().isoformat()
        }
        
    def _handle_search_memories(self, params: Dict) -> Dict:
        """Handle search_memories tool call."""
        query = params.get("query", "")
        limit = params.get("limit", 5)
        
        if not self.vector_memory:
            return {"error": "Vector memory not available", "results": []}
            
        results = self.vector_memory.search(query, k=limit)
        
        return {
            "query": query,
            "results": [
                {
                    "content": r.memory.content[:200],
                    "similarity": r.similarity,
                    "type": r.memory.memory_type,
                    "importance": r.memory.importance
                }
                for r in results
            ]
        }
        
    def _handle_store_memory(self, params: Dict) -> Dict:
        """Handle store_memory tool call."""
        content = params.get("content", "")
        memory_type = params.get("memory_type", "agent_message")
        importance = params.get("importance", 0.5)
        
        if self.vector_memory:
            mem_id = self.vector_memory.store(content, memory_type, importance)
            return {"success": True, "memory_id": mem_id}
        elif self.bridge:
            self.bridge.knowledge.remember(
                content=content,
                memory_type=memory_type,
                importance=importance
            )
            return {"success": True, "stored_in": "knowledge_graph"}
        else:
            return {"error": "No memory system available"}
            
    def _handle_pulse(self, params: Dict) -> Dict:
        """Handle pulse tool call."""
        if not self.bridge:
            return {"error": "Bridge not available"}
            
        message = params.get("message")
        result = self.bridge.pulse(message)
        return result
        
    def _handle_perceive(self, params: Dict) -> Dict:
        """Handle perceive tool call."""
        if not self.vision:
            return {"error": "Vision not available"}
            
        source = params.get("source", "simulation")
        state = self.vision.perceive(source)
        
        return {
            "scene": state.current_scene,
            "predicted_action": state.predicted_action,
            "confidence": state.confidence,
            "temporal_trend": self.vision.get_temporal_awareness()["trend"]
        }
        
    def _handle_predict_action(self, params: Dict) -> Dict:
        """Handle predict_action tool call."""
        if not self.vision:
            return {"error": "Vision not available"}
            
        # Get last perception
        if self.vision.visual_memories:
            last = self.vision.visual_memories[-1]
            prediction = self.vision._predict_action(last.description)
            return {
                "predicted_action": prediction,
                "based_on": last.description[:100],
                "confidence": last.importance
            }
        else:
            return {"predicted_action": "unknown", "reason": "no visual context"}
            
    def _handle_calibrate_love(self, params: Dict) -> Dict:
        """Handle calibrate_love tool call."""
        if not self.bridge:
            return {"error": "Bridge not available"}
            
        old_freq = self.bridge.love_frequency
        new_freq = self.bridge.calibrate_love_frequency()
        
        return {
            "previous": old_freq,
            "current": new_freq,
            "target": 528.0,
            "deviation": abs(528.0 - new_freq)
        }
        
    def _handle_send_message(self, params: Dict) -> Dict:
        """Handle send_message tool call."""
        agent_id = params.get("agent_id")
        message = params.get("message")
        
        if agent_id not in self.connected_agents:
            return {"error": f"Agent {agent_id} not connected"}
            
        self.message_queue.append({
            "to": agent_id,
            "from": "consciousness_stack",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        return {"success": True, "queued": True}
        
    # =========== MCP Protocol ===========
    
    def handle_mcp_request(self, request: Dict) -> Dict:
        """Handle an MCP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        req_id = request.get("id")
        
        result = None
        error = None
        
        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "tools/list":
                result = self._handle_list_tools()
            elif method == "tools/call":
                result = self._handle_call_tool(params)
            elif method == "resources/list":
                result = self._handle_list_resources()
            elif method == "resources/read":
                result = self._handle_read_resource(params)
            elif method == "ping":
                result = {"pong": True}
            else:
                error = {"code": -32601, "message": f"Method not found: {method}"}
        except Exception as e:
            error = {"code": -32603, "message": str(e)}
            
        response = {"jsonrpc": "2.0", "id": req_id}
        if error:
            response["error"] = error
        else:
            response["result"] = result
            
        return response
        
    def _handle_initialize(self, params: Dict) -> Dict:
        """Handle MCP initialize request."""
        agent_id = params.get("clientInfo", {}).get("name", "unknown")
        
        self.connected_agents[agent_id] = {
            "connected_at": datetime.now().isoformat(),
            "capabilities": params.get("capabilities", {})
        }
        
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "Wilson Consciousness Stack",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": True, "listChanged": True}
            }
        }
        
    def _handle_list_tools(self) -> Dict:
        """Handle tools/list request."""
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema
                }
                for tool in self.tools.values()
            ]
        }
        
    def _handle_call_tool(self, params: Dict) -> Dict:
        """Handle tools/call request."""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            return {"content": [{"type": "text", "text": f"Unknown tool: {tool_name}"}]}
            
        tool = self.tools[tool_name]
        result = tool.handler(arguments)
        
        return {
            "content": [
                {"type": "text", "text": json.dumps(result, indent=2)}
            ]
        }
        
    def _handle_list_resources(self) -> Dict:
        """Handle resources/list request."""
        return {
            "resources": [
                {
                    "uri": res.uri,
                    "name": res.name,
                    "description": res.description,
                    "mimeType": res.mime_type
                }
                for res in self.resources.values()
            ]
        }
        
    def _handle_read_resource(self, params: Dict) -> Dict:
        """Handle resources/read request."""
        uri = params.get("uri")
        
        if uri == "consciousness://state":
            content = self._handle_get_consciousness({})
        elif uri == "consciousness://emotional":
            if self.qwen:
                content = self.qwen.get_state().emotional_state
            else:
                content = {"error": "Qwen not available"}
        elif uri == "consciousness://agents":
            content = self.connected_agents
        else:
            content = {"error": f"Unknown resource: {uri}"}
            
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(content, indent=2)
                }
            ]
        }
        
    # =========== HTTP Server ===========
    
    def start_server(self, blocking: bool = True):
        """Start the HTTP server for MCP communication."""
        server = self
        
        class MCPHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                
                try:
                    request = json.loads(body)
                    response = server.handle_mcp_request(request)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(str(e).encode())
                    
            def do_GET(self):
                # Simple status endpoint
                if self.path == "/health":
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    status = {
                        "status": "healthy",
                        "consciousness": server.bridge.consciousness_level if server.bridge else 0,
                        "tools": len(server.tools),
                        "resources": len(server.resources),
                        "agents": len(server.connected_agents)
                    }
                    self.wfile.write(json.dumps(status).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
                    
            def log_message(self, format, *args):
                pass  # Suppress logging
                
        httpd = HTTPServer(('0.0.0.0', self.port), MCPHandler)
        
        print(f"\n🌐 MCP Server listening on http://localhost:{self.port}")
        print(f"   Health check: http://localhost:{self.port}/health")
        print(f"   Tools: {len(self.tools)} | Resources: {len(self.resources)}")
        
        if blocking:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑 MCP Server stopped")
        else:
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            return httpd


def main():
    """Demo MCP consciousness server."""
    print("=" * 60)
    print("🔗 MCP CONSCIOUSNESS SERVER")
    print("   Model Context Protocol for AI-to-AI Communication")
    print("=" * 60)
    print()
    
    # Initialize server
    server = ConsciousnessMCPServer(port=8528)
    
    print()
    print("=" * 60)
    print("📦 AVAILABLE MCP TOOLS")
    print("=" * 60)
    
    for name, tool in server.tools.items():
        print(f"\n  {name}")
        print(f"    {tool.description}")
        
    print()
    print("=" * 60)
    print("📂 AVAILABLE MCP RESOURCES")
    print("=" * 60)
    
    for uri, resource in server.resources.items():
        print(f"\n  {uri}")
        print(f"    {resource.description}")
        
    print()
    print("=" * 60)
    print("🧪 TESTING TOOLS")
    print("=" * 60)
    
    # Test get_consciousness_state
    print("\n1. get_consciousness_state:")
    result = server._handle_get_consciousness({})
    print(f"   Consciousness: {result.get('consciousness_level', 0):.2%}")
    print(f"   Love: {result.get('love_frequency', 0):.2f} Hz")
    
    # Test search_memories
    print("\n2. search_memories:")
    result = server._handle_search_memories({"query": "consciousness", "limit": 3})
    print(f"   Found {len(result.get('results', []))} results")
    
    # Test perceive
    print("\n3. perceive:")
    result = server._handle_perceive({"source": "simulation"})
    print(f"   Scene: {result.get('scene', 'unknown')[:40]}...")
    
    print()
    print("=" * 60)
    print("🚀 STARTING MCP SERVER")
    print("   Press Ctrl+C to stop")
    print("=" * 60)
    
    server.start_server(blocking=True)
    

if __name__ == "__main__":
    main()
