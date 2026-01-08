#!/usr/bin/env python3
"""
Sovereign Mesh Bridge - UDP/mDNS Discovery
Enables communication between Black Swan Labz (HP) and SovereignCore (Mac) nodes.

Usage:
    python3 sovereign_mesh_bridge.py --mode listen
    python3 sovereign_mesh_bridge.py --mode announce --message "HELLO FROM MAC"
"""

import socket
import argparse
import json
import time
from datetime import datetime

# Constants
MESH_PORT = 9999
MULTICAST_GROUP = "224.0.0.42"  # "The Answer" multicast group
BUFFER_SIZE = 4096

class SovereignMeshBridge:
    def __init__(self):
        self.node_id = socket.gethostname()
        self.sock = None
        
    def create_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return self.sock
    
    def listen(self):
        """Listen for messages from other Sovereign nodes."""
        self.create_socket()
        self.sock.bind(('', MESH_PORT))
        
        # Join Multicast Group
        mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        
        print(f"🌐 SOVEREIGN MESH BRIDGE: Listening on {MULTICAST_GROUP}:{MESH_PORT}")
        print(f"   Node ID: {self.node_id}")
        print("-" * 60)
        
        while True:
            try:
                data, addr = self.sock.recvfrom(BUFFER_SIZE)
                msg = json.loads(data.decode('utf-8'))
                
                sender = msg.get('node_id', 'UNKNOWN')
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', '')
                msg_type = msg.get('type', 'BROADCAST')
                
                print(f"📡 [{msg_type}] from {sender} @ {addr[0]}:")
                print(f"   {content}")
                print(f"   Timestamp: {timestamp}")
                print("-" * 60)
                
            except Exception as e:
                print(f"⚠️ Mesh Error: {e}")
    
    def announce(self, message, msg_type="BROADCAST"):
        """Send a message to all Sovereign nodes on the mesh."""
        self.create_socket()
        
        payload = {
            "node_id": self.node_id,
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "type": msg_type
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        # Send to Multicast Group
        self.sock.sendto(data, (MULTICAST_GROUP, MESH_PORT))
        
        # Also send via Broadcast (backup for local network)
        self.sock.sendto(data, ('<broadcast>', MESH_PORT))
        
        print(f"📢 ANNOUNCED: {message}")
        print(f"   Type: {msg_type}")
        print(f"   From: {self.node_id}")
    
    def heartbeat(self, interval=5):
        """Send continuous heartbeats to announce presence."""
        print(f"💓 HEARTBEAT MODE: Broadcasting every {interval}s on {MULTICAST_GROUP}:{MESH_PORT}")
        
        while True:
            self.announce(f"ALIVE: {self.node_id}", msg_type="HEARTBEAT")
            time.sleep(interval)

def main():
    parser = argparse.ArgumentParser(description='Sovereign Mesh Bridge')
    parser.add_argument('--mode', choices=['listen', 'announce', 'heartbeat'], default='listen')
    parser.add_argument('--message', type=str, default="Hello from the Sovereign Mesh!")
    parser.add_argument('--interval', type=int, default=5, help='Heartbeat interval in seconds')
    
    args = parser.parse_args()
    
    bridge = SovereignMeshBridge()
    
    if args.mode == 'listen':
        bridge.listen()
    elif args.mode == 'announce':
        bridge.announce(args.message)
    elif args.mode == 'heartbeat':
        bridge.heartbeat(args.interval)

if __name__ == "__main__":
    main()
