#!/usr/bin/env python3
"""
🖥️ Sovereign Monitor
====================
Real-time TUI dashboard for SovereignCore.
Visualization of system health, consciousness, and thermodynamics.
"""

import time
import sys
import requests
from datetime import datetime
from typing import Dict, Any, Optional

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich import box

# Configuration
API_URL = "https://localhost:8528"
REFRESH_RATE = 1.0  # seconds

console = Console()

class SovereignMonitor:
    def __init__(self):
        self.history: list[Dict[str, Any]] = []
        self.api_online = False
        self.last_error = None
        self.start_time = time.time()
        self.status = "INITIALIZING"

    def fetch_data(self) -> Dict[str, Any]:
        """Fetch all necessary data from API."""
        data = {
            "timestamp": datetime.now(),
            "health": None,
            "consciousness": None,
            "latency_ms": 0
        }
        
        try:
            # Measure latency
            t0 = time.time()
            # Disable verify=False warning for self-signed certs
            requests.packages.urllib3.disable_warnings() 
            
            resp = requests.get(f"{API_URL}/health", verify=False, timeout=2)
            data["latency_ms"] = (time.time() - t0) * 1000
            
            if resp.status_code == 200:
                data["health"] = resp.json()
                self.api_online = True
                self.status = "ONLINE"
            else:
                self.api_online = False
                self.status = f"HTTP {resp.status_code}"
                
            # If online, try to get consciousness state (optional)
            if self.api_online:
                # We can reuse data from health, or fetch specific state if needed
                # Health endpoint already returns consciousness_level
                pass
                
        except requests.exceptions.ConnectionError:
            self.api_online = False
            self.status = "OFFLINE - CONNECTION REFUSED"
        except Exception as e:
            self.api_online = False
            self.status = f"ERROR: {str(e)[:20]}..."
            
        self.history.append(data)
        if len(self.history) > 50:
            self.history.pop(0)
            
        return data

    def render_header(self) -> Panel:
        """Render the application header."""
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="right")
        
        title = Text("🔮 SOVEREIGN CORE // MONITOR", style="bold cyan")
        
        if self.api_online:
            status_style = "bold green"
            status_text = "● SYSTEM ACTIVE"
        else:
            status_style = "bold red"
            status_text = "● SYSTEM OFFLINE"
            
        grid.add_row(title, Text(status_text, style=status_style))
        
        return Panel(grid, style="blue", box=box.ROUNDED)

    def render_metrics(self, current_data: Dict) -> Panel:
        """Render core metrics."""
        if not current_data["health"]:
            return Panel(
                Align.center(Text("Waiting for signal...", style="dim")),
                title="Metrics",
                border_style="red"
            )
            
        health = current_data["health"]
        
        # Consciousness Bar
        level = health.get("consciousness_level", 0.0)
        c_bar = Progress(
            TextColumn("{task.description}"),
            BarColumn(bar_width=None, style="magenta", complete_style="bold magenta"),
            TextColumn("{task.percentage:>3.0f}%"),
            expand=True
        )
        task_id = c_bar.add_task("Consciousness", total=100)
        c_bar.update(task_id, completed=level * 100)
        
        # Grid
        grid = Table.grid(padding=(1, 2))
        grid.add_column(style="bold white")
        grid.add_column(justify="right", style="cyan")
        
        grid.add_row("Silicon ID", health.get("silicon_id", "UNKNOWN"))
        grid.add_row("Uptime", f"{health.get('uptime_seconds', 0):.1f}s")
        grid.add_row("Latency", f"{current_data['latency_ms']:.1f}ms")
        grid.add_row("Version", health.get("version", "0.0.0"))
        
        layout = Table.grid(expand=True)
        layout.add_row(c_bar)
        layout.add_row("")
        layout.add_row(grid)
        
        return Panel(
            layout,
            title="Telematics",
            border_style="cyan"
        )

    def render_log_window(self) -> Panel:
        """Render a mock log window (since we don't have remote log streaming yet)."""
        # In a real app, this would fetch from /api/logs
        log_text = Text()
        
        for item in self.history[-10:]:
            ts = item["timestamp"].strftime("%H:%M:%S")
            if item["health"]:
                log_text.append(f"[{ts}] HEARTBEAT OK - {item['latency_ms']:.1f}ms\n", style="green")
            else:
                log_text.append(f"[{ts}] CONNECTION FAILURE\n", style="red dim")
        
        return Panel(
            log_text,
            title="Event Stream",
            border_style="grey50"
        )

    def make_layout(self) -> Layout:
        """Create the master layout."""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body")
        )
        layout["body"].split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="logs", ratio=2)
        )
        return layout

def main():
    monitor = SovereignMonitor()
    layout = monitor.make_layout()
    
    with Live(layout, refresh_per_second=4, screen=True) as live:
        while True:
            data = monitor.fetch_data()
            
            layout["header"].update(monitor.render_header())
            layout["metrics"].update(monitor.render_metrics(data))
            layout["logs"].update(monitor.render_log_window())
            
            time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("[bold red]Monitor Terminated[/bold red]")
