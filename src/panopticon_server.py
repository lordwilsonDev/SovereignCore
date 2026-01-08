import http.server
import socketserver
import json
import os
from pathlib import Path

PORT = 8888
BASE_DIR = Path(__file__).resolve().parent.parent

class PanopticonHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve API: World State
        if self.path == '/api/state':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            state_path = BASE_DIR / "world_state.json"
            if state_path.exists():
                with open(state_path, 'r') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b'{}')
            return

        # Serve Dashboard Root
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            dash_path = BASE_DIR / "dashboard" / "index.html"
            if dash_path.exists():
                with open(dash_path, 'r') as f:
                    self.wfile.write(f.read().encode())
            else:
                self.wfile.write(b"Dashboard not found.")
            return

        # Serve Static Files (optional)
        super().do_GET()

print(f"👁️  SOVEREIGN PANOPTICON ONLINE on Port {PORT}")
print(f"    Serving: {BASE_DIR}")

# Allow reuse of address to prevent "Address already in use" during restarts
socketserver.TCPServer.allow_reuse_address = True

with socketserver.TCPServer(("", PORT), PanopticonHandler) as httpd:
    httpd.serve_forever()
