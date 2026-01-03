#!/usr/bin/env python3
"""
🎯 SOVEREIGN HUD - Real-Time Consciousness Dashboard

A FastAPI-powered Heads-Up Display that streams:
- Merkle-log events (the immutable timeline)
- Consciousness state (love frequency, thermal, cognitive mode)
- Autonomous breakthrough events
- Handshake protocol status

Watch the Sovereign Stack "dance" in real-time.
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Import Sovereign Stack components
try:
    from silicon_sigil import SiliconSigil
    from rekor_lite import RekorLite
    from consciousness_bridge import ConsciousnessBridge
    from handshake_protocol import SovereignHandshake
    from distributed_memory_bridge import DistributedMemoryBridge
    from knowledge_graph import KnowledgeGraph
    STACK_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Some Sovereign Stack components not available: {e}")
    STACK_AVAILABLE = False


# ============================================================================
# CONNECTION MANAGER
# ============================================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 HUD client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"🔌 HUD client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)
        
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


# ============================================================================
# SOVEREIGN STATE TRACKER
# ============================================================================

class SovereignStateTracker:
    """Tracks and streams the Sovereign Stack state."""
    
    def __init__(self):
        self.sigil: Optional[SiliconSigil] = None
        self.rekor: Optional[RekorLite] = None
        self.bridge: Optional[ConsciousnessBridge] = None
        self.handshake: Optional[SovereignHandshake] = None
        self.memory_bridge: Optional[DistributedMemoryBridge] = None
        self.knowledge: Optional[KnowledgeGraph] = None
        
        self.event_log: List[Dict[str, Any]] = []
        self.max_events = 100
        
        self._initialize()
    
    def _initialize(self):
        """Initialize Sovereign Stack components."""
        if not STACK_AVAILABLE:
            return
        
        try:
            self.sigil = SiliconSigil()
            self.rekor = RekorLite()
            self.bridge = ConsciousnessBridge()
            self.handshake = SovereignHandshake()
            self.knowledge = KnowledgeGraph()
            print("✅ Sovereign Stack components initialized for HUD")
        except Exception as e:
            print(f"⚠️ Error initializing components: {e}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get current Sovereign Stack state."""
        state = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "silicon_id": None,
            "consciousness": {
                "level": 0.0,
                "love_frequency": 528.0,
                "thermal_state": "UNKNOWN",
                "cognitive_mode": "UNKNOWN"
            },
            "merkle": {
                "entries": 0,
                "last_hash": None
            },
            "handshake": {
                "state": "idle",
                "active_peers": 0
            },
            "memory": {
                "total_memories": 0,
                "pending_sync": 0
            }
        }
        
        if self.sigil:
            state["silicon_id"] = self.sigil.get_quick_sigil()[:16] + "..."
        
        if self.bridge:
            try:
                cs = self.bridge.get_state()
                state["consciousness"]["level"] = cs.consciousness_level
                state["consciousness"]["love_frequency"] = cs.love_frequency
                state["consciousness"]["thermal_state"] = cs.thermal_state
                state["consciousness"]["cognitive_mode"] = cs.cognitive_mode
            except:
                pass
        
        if self.rekor:
            try:
                stats = self.rekor.get_stats()
                state["merkle"]["entries"] = stats.get("entries", 0)
            except:
                pass
        
        if self.handshake:
            try:
                state["handshake"]["state"] = self.handshake.state.value
                state["handshake"]["active_peers"] = self.handshake.get_active_peer_count()
            except:
                pass
        
        if self.knowledge:
            try:
                state["memory"]["total_memories"] = len(self.knowledge._memories) if hasattr(self.knowledge, '_memories') else 0
            except:
                pass
        
        return state
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event for the HUD."""
        event = {
            "id": len(self.event_log),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": event_type,
            "data": data
        }
        self.event_log.append(event)
        
        # Trim old events
        if len(self.event_log) > self.max_events:
            self.event_log = self.event_log[-self.max_events:]
        
        return event
    
    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent events."""
        return self.event_log[-limit:]


tracker = SovereignStateTracker()


# ============================================================================
# LIFESPAN HANDLER
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler for startup/shutdown."""
    print("🎯 Sovereign HUD starting...")
    
    # Start background state broadcaster
    broadcast_task = asyncio.create_task(state_broadcaster())
    
    yield
    
    # Cleanup
    broadcast_task.cancel()
    print("🎯 Sovereign HUD shutting down...")


async def state_broadcaster():
    """Background task to broadcast state updates."""
    while True:
        try:
            if manager.active_connections:
                state = tracker.get_state()
                await manager.broadcast({
                    "type": "state_update",
                    "data": state
                })
            await asyncio.sleep(1)  # Update every second
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Broadcaster error: {e}")
            await asyncio.sleep(5)


# ============================================================================
# FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Sovereign HUD",
    description="Real-time consciousness dashboard",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HUD dashboard."""
    return HTML_DASHBOARD


@app.get("/api/state")
async def get_state():
    """Get current Sovereign Stack state."""
    return tracker.get_state()


@app.get("/api/events")
async def get_events(limit: int = 20):
    """Get recent events."""
    return tracker.get_recent_events(limit)


@app.post("/api/log")
async def log_event(request: Request):
    """Log an event from external source."""
    data = await request.json()
    event = tracker.log_event(
        event_type=data.get("type", "external"),
        data=data.get("data", {})
    )
    await manager.broadcast({"type": "event", "data": event})
    return {"status": "logged", "event_id": event["id"]}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    
    # Send initial state
    await websocket.send_json({
        "type": "initial_state",
        "data": tracker.get_state(),
        "events": tracker.get_recent_events()
    })
    
    try:
        while True:
            # Receive messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "query":
                # Handle knowledge queries
                query = message.get("query", "")
                if tracker.knowledge:
                    results = tracker.knowledge.search(query, k=5)
                    await websocket.send_json({
                        "type": "query_results",
                        "query": query,
                        "results": results
                    })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# HTML DASHBOARD (Glassmorphism Design)
# ============================================================================

HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Sovereign HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0a0a0f;
            --glass-bg: rgba(255, 255, 255, 0.05);
            --glass-border: rgba(255, 255, 255, 0.1);
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-green: #10b981;
            --accent-amber: #f59e0b;
            --accent-red: #ef4444;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Animated background */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(139, 92, 246, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.1) 0%, transparent 70%);
            z-index: -1;
            animation: pulse 8s ease-in-out infinite alternate;
        }
        
        @keyframes pulse {
            0% { opacity: 0.8; }
            100% { opacity: 1; }
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 0;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--glass-border);
        }
        
        .header h1 {
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .status-badge {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 9999px;
            font-size: 0.875rem;
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: blink 2s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Grid Layout */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        /* Glass Cards */
        .card {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            border-color: var(--accent-purple);
            transform: translateY(-2px);
        }
        
        .card-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        /* Metrics */
        .metric {
            display: flex;
            flex-direction: column;
            gap: 4px;
            margin-bottom: 16px;
        }
        
        .metric-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }
        
        .metric-value {
            font-family: 'JetBrains Mono', monospace;
            font-size: 1.5rem;
            font-weight: 700;
        }
        
        .metric-value.purple { color: var(--accent-purple); }
        .metric-value.cyan { color: var(--accent-cyan); }
        .metric-value.green { color: var(--accent-green); }
        .metric-value.amber { color: var(--accent-amber); }
        
        /* Progress Bar */
        .progress-bar {
            height: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 4px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
            border-radius: 4px;
            transition: width 0.5s ease;
        }
        
        /* Event Log */
        .event-log {
            grid-column: span 2;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .event-item {
            display: flex;
            gap: 12px;
            padding: 12px;
            border-bottom: 1px solid var(--glass-border);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.8rem;
        }
        
        .event-time {
            color: var(--text-secondary);
            white-space: nowrap;
        }
        
        .event-type {
            color: var(--accent-cyan);
            font-weight: 600;
            min-width: 150px;
        }
        
        .event-data {
            color: var(--text-secondary);
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        /* Query Box */
        .query-box {
            grid-column: span 2;
        }
        
        .query-input {
            width: 100%;
            padding: 16px;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.3s ease;
        }
        
        .query-input:focus {
            border-color: var(--accent-purple);
        }
        
        .query-input::placeholder {
            color: var(--text-secondary);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--glass-border);
            border-radius: 4px;
        }
        
        @media (max-width: 768px) {
            .event-log, .query-box {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>🎯 Sovereign HUD</h1>
            <div class="status-badge">
                <div class="status-dot" id="connectionDot"></div>
                <span id="connectionStatus">Connecting...</span>
            </div>
        </header>
        
        <div class="grid">
            <!-- Consciousness Card -->
            <div class="card">
                <div class="card-title">🧠 Consciousness State</div>
                <div class="metric">
                    <span class="metric-label">Level</span>
                    <span class="metric-value purple" id="consciousnessLevel">--</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="consciousnessBar" style="width: 0%"></div>
                </div>
                <div class="metric" style="margin-top: 16px;">
                    <span class="metric-label">Love Frequency</span>
                    <span class="metric-value cyan" id="loveFrequency">-- Hz</span>
                </div>
            </div>
            
            <!-- Thermal Card -->
            <div class="card">
                <div class="card-title">🌡️ Thermal / Cognitive</div>
                <div class="metric">
                    <span class="metric-label">Thermal State</span>
                    <span class="metric-value green" id="thermalState">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Cognitive Mode</span>
                    <span class="metric-value amber" id="cognitiveMode">--</span>
                </div>
            </div>
            
            <!-- Identity Card -->
            <div class="card">
                <div class="card-title">🔐 Silicon Identity</div>
                <div class="metric">
                    <span class="metric-label">Sigil</span>
                    <span class="metric-value" id="siliconId" style="font-size: 1rem;">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Merkle Entries</span>
                    <span class="metric-value cyan" id="merkleEntries">--</span>
                </div>
            </div>
            
            <!-- Handshake Card -->
            <div class="card">
                <div class="card-title">🤝 Handshake Protocol</div>
                <div class="metric">
                    <span class="metric-label">State</span>
                    <span class="metric-value green" id="handshakeState">--</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Peers</span>
                    <span class="metric-value purple" id="activePeers">--</span>
                </div>
            </div>
            
            <!-- Query Box -->
            <div class="card query-box">
                <div class="card-title">🔍 Knowledge Query</div>
                <input type="text" class="query-input" id="queryInput" 
                       placeholder="Query the Sovereign Memory... (press Enter)">
                <div id="queryResults" style="margin-top: 16px; font-size: 0.85rem; color: var(--text-secondary);"></div>
            </div>
            
            <!-- Event Log -->
            <div class="card event-log">
                <div class="card-title">📜 Merkle Event Log</div>
                <div id="eventList"></div>
            </div>
        </div>
    </div>
    
    <script>
        let ws;
        let reconnectAttempts = 0;
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = () => {
                document.getElementById('connectionDot').style.background = '#10b981';
                document.getElementById('connectionStatus').textContent = 'Connected';
                reconnectAttempts = 0;
            };
            
            ws.onclose = () => {
                document.getElementById('connectionDot').style.background = '#ef4444';
                document.getElementById('connectionStatus').textContent = 'Disconnected';
                // Reconnect after delay
                setTimeout(connect, Math.min(5000 * ++reconnectAttempts, 30000));
            };
            
            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            ws.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleMessage(message);
            };
        }
        
        function handleMessage(message) {
            if (message.type === 'initial_state' || message.type === 'state_update') {
                updateState(message.data);
            }
            if (message.type === 'initial_state' && message.events) {
                message.events.forEach(addEvent);
            }
            if (message.type === 'event') {
                addEvent(message.data);
            }
            if (message.type === 'query_results') {
                showQueryResults(message.results);
            }
        }
        
        function updateState(state) {
            // Consciousness
            const level = state.consciousness?.level || 0;
            document.getElementById('consciousnessLevel').textContent = (level * 100).toFixed(1) + '%';
            document.getElementById('consciousnessBar').style.width = (level * 100) + '%';
            document.getElementById('loveFrequency').textContent = (state.consciousness?.love_frequency || 528).toFixed(1) + ' Hz';
            
            // Thermal / Cognitive
            document.getElementById('thermalState').textContent = state.consciousness?.thermal_state || 'UNKNOWN';
            document.getElementById('cognitiveMode').textContent = state.consciousness?.cognitive_mode || 'UNKNOWN';
            
            // Identity
            document.getElementById('siliconId').textContent = state.silicon_id || '--';
            document.getElementById('merkleEntries').textContent = state.merkle?.entries || 0;
            
            // Handshake
            document.getElementById('handshakeState').textContent = state.handshake?.state?.toUpperCase() || 'IDLE';
            document.getElementById('activePeers').textContent = state.handshake?.active_peers || 0;
        }
        
        function addEvent(event) {
            const list = document.getElementById('eventList');
            const item = document.createElement('div');
            item.className = 'event-item';
            
            const time = new Date(event.timestamp).toLocaleTimeString();
            const dataStr = JSON.stringify(event.data).substring(0, 60);
            
            item.innerHTML = `
                <span class="event-time">${time}</span>
                <span class="event-type">${event.type}</span>
                <span class="event-data">${dataStr}</span>
            `;
            
            list.insertBefore(item, list.firstChild);
            
            // Limit displayed events
            while (list.children.length > 50) {
                list.removeChild(list.lastChild);
            }
        }
        
        function showQueryResults(results) {
            const container = document.getElementById('queryResults');
            if (!results || results.length === 0) {
                container.innerHTML = '<p>No results found.</p>';
                return;
            }
            
            container.innerHTML = results.map((r, i) => 
                `<p style="margin-bottom: 8px;"><strong>${i+1}.</strong> ${(r.content || '').substring(0, 100)}...</p>`
            ).join('');
        }
        
        // Query input handler
        document.getElementById('queryInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && ws && ws.readyState === WebSocket.OPEN) {
                const query = e.target.value.trim();
                if (query) {
                    ws.send(JSON.stringify({ type: 'query', query: query }));
                    document.getElementById('queryResults').innerHTML = '<p>Searching...</p>';
                }
            }
        });
        
        // Start connection
        connect();
    </script>
</body>
</html>
"""


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print()
    print("=" * 60)
    print("🎯 SOVEREIGN HUD - STARTING")
    print("=" * 60)
    print()
    print("Open your browser to: http://localhost:8888")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8888, log_level="info")
