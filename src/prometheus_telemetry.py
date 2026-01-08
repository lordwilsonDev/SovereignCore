#!/usr/bin/env python3
"""
Prometheus Telemetry Exporter - Real Metrics for SovereignCore
Exposes metrics at /metrics endpoint for Prometheus scraping.

Usage:
    python3 prometheus_telemetry.py --port 9090

Metrics Exposed:
    - sovereign_fuel_issued_total
    - sovereign_fuel_spent_total
    - sovereign_audit_requests_total
    - sovereign_audit_vetoes_total
    - sovereign_auction_bids_total
    - sovereign_entities_spawned_total
    - sovereign_system_mass
    - sovereign_thermal_level
"""

import time
import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

# Try to import prometheus_client, fallback to manual implementation
try:
    from prometheus_client import Counter, Gauge, Histogram, generate_latest, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("⚠️ prometheus_client not installed. Using manual metrics format.")


class SovereignMetrics:
    """Central metrics registry for SovereignCore."""
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.world_state_path = self.base_dir / "world_state.json"
        self.metrics_path = self.base_dir / "data" / "metrics.json"
        self.metrics_path.parent.mkdir(exist_ok=True)
        
        # Initialize counters (stored in metrics.json)
        self._load_or_init_counters()
        
        if PROMETHEUS_AVAILABLE:
            self._init_prometheus_metrics()
    
    def _load_or_init_counters(self):
        """Load existing counters or initialize fresh."""
        if self.metrics_path.exists():
            with open(self.metrics_path, 'r') as f:
                self.counters = json.load(f)
        else:
            self.counters = {
                "fuel_issued_total": 0.0,
                "fuel_spent_total": 0.0,
                "audit_requests_total": 0,
                "audit_vetoes_total": 0,
                "auction_bids_total": 0,
                "auction_rounds_total": 0,
                "entities_spawned_total": 0,
                "mesh_messages_sent": 0,
                "mesh_messages_received": 0,
                "veto_events_total": 0,
            }
            self._save_counters()
    
    def _save_counters(self):
        with open(self.metrics_path, 'w') as f:
            json.dump(self.counters, f, indent=2)
    
    def _init_prometheus_metrics(self):
        """Initialize prometheus_client metrics."""
        self.prom_fuel_issued = Counter('sovereign_fuel_issued_total', 'Total Fuel tokens issued')
        self.prom_fuel_spent = Counter('sovereign_fuel_spent_total', 'Total Fuel tokens spent')
        self.prom_audit_requests = Counter('sovereign_audit_requests_total', 'Total audit requests')
        self.prom_audit_vetoes = Counter('sovereign_audit_vetoes_total', 'Total vetoed audits')
        self.prom_auction_bids = Counter('sovereign_auction_bids_total', 'Total auction bids placed')
        self.prom_entities = Counter('sovereign_entities_spawned_total', 'Total entities spawned')
        
        self.prom_system_mass = Gauge('sovereign_system_mass', 'Number of evolved Python files')
        self.prom_council_size = Gauge('sovereign_council_size', 'Number of ascended masters')
        self.prom_thermal_level = Gauge('sovereign_thermal_level', 'Current thermal pressure level')
        self.prom_generation = Gauge('sovereign_generation', 'Current evolution generation')
    
    # --- Increment Methods ---
    
    def inc_fuel_issued(self, amount: float):
        self.counters["fuel_issued_total"] += amount
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_fuel_issued.inc(amount)
    
    def inc_fuel_spent(self, amount: float):
        self.counters["fuel_spent_total"] += amount
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_fuel_spent.inc(amount)
    
    def inc_audit_request(self):
        self.counters["audit_requests_total"] += 1
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_audit_requests.inc()
    
    def inc_audit_veto(self):
        self.counters["audit_vetoes_total"] += 1
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_audit_vetoes.inc()
    
    def inc_auction_bid(self):
        self.counters["auction_bids_total"] += 1
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_auction_bids.inc()
    
    def inc_entity_spawned(self):
        self.counters["entities_spawned_total"] += 1
        self._save_counters()
        if PROMETHEUS_AVAILABLE:
            self.prom_entities.inc()
    
    # --- Gauge Methods ---
    
    def read_world_state(self) -> dict:
        """Read current world state for gauge metrics."""
        if self.world_state_path.exists():
            with open(self.world_state_path, 'r') as f:
                return json.load(f)
        return {}
    
    def update_gauges(self):
        """Update gauge metrics from world state."""
        state = self.read_world_state()
        if PROMETHEUS_AVAILABLE:
            self.prom_system_mass.set(state.get("system_mass", 0))
            # ascended_masters can be a list or an int
            ascended = state.get("ascended_masters", 0)
            if isinstance(ascended, list):
                ascended = len(ascended)
            self.prom_council_size.set(ascended)
            self.prom_generation.set(state.get("generation", 0))
    
    # --- Export Methods ---
    
    def get_metrics_text(self) -> str:
        """Generate Prometheus-compatible metrics text."""
        if PROMETHEUS_AVAILABLE:
            self.update_gauges()
            return generate_latest(REGISTRY).decode('utf-8')
        
        # Manual format (OpenMetrics-compatible)
        self.update_gauges_manual()
        state = self.read_world_state()
        
        lines = [
            "# HELP sovereign_fuel_issued_total Total Fuel tokens issued",
            "# TYPE sovereign_fuel_issued_total counter",
            f"sovereign_fuel_issued_total {self.counters['fuel_issued_total']}",
            "",
            "# HELP sovereign_fuel_spent_total Total Fuel tokens spent",
            "# TYPE sovereign_fuel_spent_total counter",
            f"sovereign_fuel_spent_total {self.counters['fuel_spent_total']}",
            "",
            "# HELP sovereign_audit_requests_total Total audit requests",
            "# TYPE sovereign_audit_requests_total counter",
            f"sovereign_audit_requests_total {self.counters['audit_requests_total']}",
            "",
            "# HELP sovereign_audit_vetoes_total Total vetoed audits",
            "# TYPE sovereign_audit_vetoes_total counter",
            f"sovereign_audit_vetoes_total {self.counters['audit_vetoes_total']}",
            "",
            "# HELP sovereign_auction_bids_total Total auction bids",
            "# TYPE sovereign_auction_bids_total counter",
            f"sovereign_auction_bids_total {self.counters['auction_bids_total']}",
            "",
            "# HELP sovereign_entities_spawned_total Total entities spawned",
            "# TYPE sovereign_entities_spawned_total counter",
            f"sovereign_entities_spawned_total {self.counters['entities_spawned_total']}",
            "",
            "# HELP sovereign_system_mass Number of evolved Python files",
            "# TYPE sovereign_system_mass gauge",
            f"sovereign_system_mass {state.get('system_mass', 0)}",
            "",
            "# HELP sovereign_council_size Number of ascended masters",
            "# TYPE sovereign_council_size gauge",
            f"sovereign_council_size {state.get('ascended_masters', 0)}",
            "",
            "# HELP sovereign_generation Current evolution generation",
            "# TYPE sovereign_generation gauge",
            f"sovereign_generation {state.get('generation', 0)}",
            "",
        ]
        
        return "\n".join(lines)
    
    def update_gauges_manual(self):
        """Placeholder for manual gauge update logic."""
        pass


class MetricsHandler(BaseHTTPRequestHandler):
    """HTTP handler for /metrics endpoint."""
    
    metrics_instance = None
    
    def do_GET(self):
        if self.path == '/metrics':
            content = self.metrics_instance.get_metrics_text()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress HTTP logs


def run_metrics_server(port=9090, base_dir=None):
    """Start the Prometheus metrics server."""
    metrics = SovereignMetrics(base_dir)
    MetricsHandler.metrics_instance = metrics
    
    server = HTTPServer(('0.0.0.0', port), MetricsHandler)
    print(f"📊 PROMETHEUS TELEMETRY SERVER")
    print(f"   Endpoint: http://0.0.0.0:{port}/metrics")
    print(f"   Format: {'prometheus_client' if PROMETHEUS_AVAILABLE else 'OpenMetrics (manual)'}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print("Server stopped.")


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Prometheus Telemetry Exporter')
    parser.add_argument('--port', type=int, default=9090, help='Port to serve metrics on')
    parser.add_argument('--test', action='store_true', help='Print metrics once and exit')
    
    args = parser.parse_args()
    
    if args.test:
        metrics = SovereignMetrics()
        print(metrics.get_metrics_text())
    else:
        run_metrics_server(args.port)
