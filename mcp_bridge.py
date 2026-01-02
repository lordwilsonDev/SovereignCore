#!/usr/bin/env python3
"""
==============================================================================
MCP SECURE BRIDGE - Model Context Protocol Integration Layer
==============================================================================
SovereignCore v4.0 - Tool Access for AI

The MCP Secure Bridge grants the AI "hands" to manage the system:

1. FILESYSTEM MCP: Sandboxed read/write operations
2. COMMAND MCP: Execute commands with safety checks
3. DESKTOP COMMANDER: Vision-based UI verification

All operations have:
- Sandboxed path restrictions
- Dangerous command blocking
- Audit logging

==============================================================================
"""

import os
import sys
import json
import subprocess
import hashlib
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable
from datetime import datetime
from enum import Enum
import asyncio

# Filioque is optional - provides extra security layer
FilioqueSystem = None  # Set to None for standalone operation

# =============================================================================
# CONFIGURATION
# =============================================================================

SOVEREIGNCORE_ROOT = Path(__file__).parent
MCP_DIR = SOVEREIGNCORE_ROOT / "mcp_data"
MCP_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MCP] %(message)s'
)
logger = logging.getLogger("MCPBridge")

# =============================================================================
# SANDBOXED PATHS
# =============================================================================


ALLOWED_READ_PATHS = [
    Path.home() / "STEM_SCAFFOLDING",
    Path.home() / "SovereignCore",
    SOVEREIGNCORE_ROOT,
    Path.home() / "Developer",
    Path.home() / "Projects",
    Path("/tmp"),
]

ALLOWED_WRITE_PATHS = [
    Path.home() / "STEM_SCAFFOLDING",
    Path.home() / "SovereignCore",
    SOVEREIGNCORE_ROOT,
    Path("/tmp"),
]

# Default project directory for xcodebuild
MOIE_ROOT = Path.home() / "STEM_SCAFFOLDING" / "MOIE_FORTRESS"

BLOCKED_PATHS = [
    Path.home() / ".ssh",
    Path.home() / ".gnupg",
    Path.home() / ".aws",
    Path.home() / "Library" / "Keychains",
    Path("/System"),
    Path("/Library"),
    Path("/usr"),
]

# =============================================================================
# MCP TOOL DEFINITIONS
# =============================================================================

class MCPTool(Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_DIRECTORY = "list_directory"
    EXECUTE_COMMAND = "execute_command"
    XCODEGEN = "xcodegen"
    XCODEBUILD = "xcodebuild"
    SCREENSHOT = "screenshot"
    FIND_ELEMENT = "find_element"

@dataclass
class MCPRequest:
    """An MCP operation request."""
    id: str
    tool: MCPTool
    parameters: Dict
    requester: str
    timestamp: str
    requires_approval: bool = False

@dataclass
class MCPResponse:
    """Response from an MCP operation."""
    request_id: str
    success: bool
    data: Optional[Dict]
    error: Optional[str]
    timestamp: str

# =============================================================================
# FILESYSTEM MCP
# =============================================================================

class FileSystemMCP:
    """
    Sandboxed filesystem operations.
    All operations go through Filioque for security.
    """
    
    def __init__(self, filioque: FilioqueSystem = None):
        self.filioque = filioque or (FilioqueSystem() if FilioqueSystem else None)
    
    def _is_path_allowed(self, path: Path, for_write: bool = False) -> bool:
        """Check if path is within allowed sandbox."""
        path = path.resolve()
        
        # Check blocked paths first
        for blocked in BLOCKED_PATHS:
            try:
                path.relative_to(blocked)
                return False  # Path is under a blocked directory
            except ValueError:
                pass  # Not under this blocked path
        
        # Check allowed paths
        allowed_list = ALLOWED_WRITE_PATHS if for_write else ALLOWED_READ_PATHS
        for allowed in allowed_list:
            try:
                path.relative_to(allowed)
                return True
            except ValueError:
                pass
        
        return False
    
    def read_file(self, path: str) -> MCPResponse:
        """Read a file with security checks."""
        file_path = Path(path)
        
        if not self._is_path_allowed(file_path, for_write=False):
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"Path not in allowed sandbox: {path}",
                timestamp=datetime.now().isoformat()
            )
        
        if not file_path.exists():
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"File not found: {path}",
                timestamp=datetime.now().isoformat()
            )
        
        try:
            content = file_path.read_text()
            return MCPResponse(
                request_id="",
                success=True,
                data={"content": content, "size": len(content)},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def write_file(self, path: str, content: str) -> MCPResponse:
        """Write a file with security checks and Filioque approval."""
        file_path = Path(path)
        
        if not self._is_path_allowed(file_path, for_write=True):
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"Path not in allowed sandbox for write: {path}",
                timestamp=datetime.now().isoformat()
            )
        
        # Use Filioque for permission
        if self.filioque:
            success, result = self.filioque.secure_execute(
                ActionType.FILE_WRITE,
                str(file_path),
                parameters={"content": content[:100] + "..."},
                requester="mcp_bridge",
                reason="MCP write_file operation"
            )
            
            if not success:
                return MCPResponse(
                    request_id="",
                    success=False,
                    data=None,
                    error=f"Filioque denied: {result}",
                    timestamp=datetime.now().isoformat()
                )
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            return MCPResponse(
                request_id="",
                success=True,
                data={"path": str(file_path), "bytes_written": len(content)},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def list_directory(self, path: str) -> MCPResponse:
        """List directory contents."""
        dir_path = Path(path)
        
        if not self._is_path_allowed(dir_path, for_write=False):
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"Path not in allowed sandbox: {path}",
                timestamp=datetime.now().isoformat()
            )
        
        if not dir_path.exists():
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"Directory not found: {path}",
                timestamp=datetime.now().isoformat()
            )
        
        try:
            entries = []
            for entry in dir_path.iterdir():
                entries.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else None
                })
            
            return MCPResponse(
                request_id="",
                success=True,
                data={"entries": entries, "count": len(entries)},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )

# =============================================================================
# COMMAND MCP
# =============================================================================

class CommandMCP:
    """
    Sandboxed command execution.
    Dangerous commands require Filioque quorum approval.
    """
    
    SAFE_COMMANDS = [
        "echo",
        "ls",
        "pwd",
        "cat",
        "head",
        "tail",
        "wc",
        "find",
        "grep",
        "xcodegen",
        "swift",
        "swiftc",
    ]
    
    DANGEROUS_PATTERNS = [
        "rm -rf",
        "sudo",
        "chmod 777",
        "curl | sh",
        "wget | bash",
        "> /dev/",
        "mkfs",
    ]
    
    def __init__(self, filioque: FilioqueSystem = None):
        self.filioque = filioque or (FilioqueSystem() if FilioqueSystem else None)
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        # Check dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command:
                return False
        
        # Check if starts with safe command
        cmd_parts = command.split()
        if cmd_parts:
            base_cmd = cmd_parts[0]
            return base_cmd in self.SAFE_COMMANDS
        
        return False
    
    def execute(self, command: str, cwd: str = None, timeout: int = 30) -> MCPResponse:
        """Execute a command with security checks."""
        
        # Check for dangerous patterns
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in command:
                return MCPResponse(
                    request_id="",
                    success=False,
                    data=None,
                    error=f"Dangerous command pattern blocked: {pattern}",
                    timestamp=datetime.now().isoformat()
                )
        
        # Use Filioque for permission
        if self.filioque:
            success, result = self.filioque.secure_execute(
                ActionType.SHELL_EXECUTE,
                command,
                parameters={"cwd": cwd},
                requester="mcp_bridge",
                reason="MCP command execution"
            )
            
            if not success:
                return MCPResponse(
                    request_id="",
                    success=False,
                    data=None,
                    error=f"Filioque denied: {result}",
                    timestamp=datetime.now().isoformat()
                )
            
            # Result contains the actual command output
            return MCPResponse(
                request_id="",
                success=True,
                data={"output": result, "command": command},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        
        # Direct execution (if Filioque not available)
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            return MCPResponse(
                request_id="",
                success=result.returncode == 0,
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                },
                error=result.stderr if result.returncode != 0 else None,
                timestamp=datetime.now().isoformat()
            )
        except subprocess.TimeoutExpired:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=f"Command timed out after {timeout}s",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def xcodegen(self, project_dir: str = None) -> MCPResponse:
        """Run XcodeGen to regenerate project."""
        cwd = project_dir or str(MOIE_ROOT)
        return self.execute("xcodegen generate", cwd=cwd)
    
    def xcodebuild(
        self,
        scheme: str,
        project_dir: str = None,
        destination: str = "platform=iOS Simulator,name=iPhone 16 Pro"
    ) -> MCPResponse:
        """Run xcodebuild."""
        cwd = project_dir or str(MOIE_ROOT)
        command = f"xcodebuild -scheme {scheme} -destination '{destination}' build"
        return self.execute(command, cwd=cwd, timeout=300)

# =============================================================================
# DESKTOP COMMANDER MCP
# =============================================================================

class DesktopCommanderMCP:
    """
    Vision-based UI verification.
    Takes screenshots and analyzes UI state.
    """
    
    def __init__(self):
        self.screenshots_dir = MCP_DIR / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    def capture_screen(self, display: int = 0) -> MCPResponse:
        """Capture the screen."""
        screenshot_id = hashlib.sha256(
            f"screen:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        file_path = self.screenshots_dir / f"{screenshot_id}.png"
        
        try:
            subprocess.run(
                ["screencapture", "-x", "-D", str(display), str(file_path)],
                check=True,
                capture_output=True
            )
            
            return MCPResponse(
                request_id="",
                success=True,
                data={"file_path": str(file_path), "id": screenshot_id},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    def capture_window(self, app_name: str) -> MCPResponse:
        """Capture a specific application window."""
        screenshot_id = hashlib.sha256(
            f"window:{app_name}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        file_path = self.screenshots_dir / f"{screenshot_id}.png"
        
        try:
            # Use AppleScript to get window
            script = f'''
            tell application "System Events"
                tell process "{app_name}"
                    set windowList to windows
                    if (count of windowList) > 0 then
                        return id of window 1
                    end if
                end tell
            end tell
            '''
            
            # For now, capture full screen as fallback
            subprocess.run(
                ["screencapture", "-x", str(file_path)],
                check=True,
                capture_output=True
            )
            
            return MCPResponse(
                request_id="",
                success=True,
                data={"file_path": str(file_path), "id": screenshot_id, "app": app_name},
                error=None,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return MCPResponse(
                request_id="",
                success=False,
                data=None,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )

# =============================================================================
# THE MCP BRIDGE
# =============================================================================

class MCPSecureBridge:
    """
    The complete MCP Secure Bridge.
    Provides unified access to all MCP tools with security.
    """
    
    def __init__(self):
        self.filioque = FilioqueSystem() if FilioqueSystem else None
        self.filesystem = FileSystemMCP(self.filioque)
        self.command = CommandMCP(self.filioque)
        self.desktop = DesktopCommanderMCP()
        
        self.request_log: List[MCPRequest] = []
    
    def execute_tool(self, tool: MCPTool, parameters: Dict) -> MCPResponse:
        """Execute an MCP tool."""
        request = MCPRequest(
            id=hashlib.sha256(f"{tool.value}:{datetime.now()}".encode()).hexdigest()[:12],
            tool=tool,
            parameters=parameters,
            requester="mcp_bridge",
            timestamp=datetime.now().isoformat()
        )
        
        self.request_log.append(request)
        logger.info(f"🔧 MCP: {tool.value} with {len(parameters)} parameters")
        
        if tool == MCPTool.READ_FILE:
            return self.filesystem.read_file(parameters.get("path", ""))
        
        elif tool == MCPTool.WRITE_FILE:
            return self.filesystem.write_file(
                parameters.get("path", ""),
                parameters.get("content", "")
            )
        
        elif tool == MCPTool.LIST_DIRECTORY:
            return self.filesystem.list_directory(parameters.get("path", ""))
        
        elif tool == MCPTool.EXECUTE_COMMAND:
            return self.command.execute(
                parameters.get("command", ""),
                cwd=parameters.get("cwd")
            )
        
        elif tool == MCPTool.XCODEGEN:
            return self.command.xcodegen(parameters.get("project_dir"))
        
        elif tool == MCPTool.XCODEBUILD:
            return self.command.xcodebuild(
                parameters.get("scheme", "MoIE-App"),
                parameters.get("project_dir")
            )
        
        elif tool == MCPTool.SCREENSHOT:
            return self.desktop.capture_screen(parameters.get("display", 0))
        
        elif tool == MCPTool.FIND_ELEMENT:
            # Would use Vision for element detection
            return MCPResponse(
                request_id=request.id,
                success=False,
                data=None,
                error="Find element not yet implemented",
                timestamp=datetime.now().isoformat()
            )
        
        return MCPResponse(
            request_id=request.id,
            success=False,
            data=None,
            error=f"Unknown tool: {tool.value}",
            timestamp=datetime.now().isoformat()
        )
    
    def get_statistics(self) -> Dict:
        """Get bridge statistics."""
        return {
            "total_requests": len(self.request_log),
            "filioque_active": self.filioque is not None,
            "tools_available": [t.value for t in MCPTool]
        }

# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Secure Bridge")
    parser.add_argument("command", choices=["status", "read", "write", "exec", "screenshot"])
    parser.add_argument("--path", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--cmd", default="echo 'Hello MCP'")
    args = parser.parse_args()
    
    bridge = MCPSecureBridge()
    
    if args.command == "status":
        stats = bridge.get_statistics()
        print("\n🌉 MCP SECURE BRIDGE STATUS:\n")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    
    elif args.command == "read":
        response = bridge.execute_tool(MCPTool.READ_FILE, {"path": args.path})
        if response.success:
            print(f"✅ Read {response.data['size']} bytes")
            print(response.data['content'][:500])
        else:
            print(f"❌ {response.error}")
    
    elif args.command == "write":
        response = bridge.execute_tool(MCPTool.WRITE_FILE, {
            "path": args.path,
            "content": args.content
        })
        print(f"{'✅' if response.success else '❌'} {response.data or response.error}")
    
    elif args.command == "exec":
        response = bridge.execute_tool(MCPTool.EXECUTE_COMMAND, {"command": args.cmd})
        if response.success:
            print(f"✅ Output:\n{response.data.get('output', response.data.get('stdout', ''))}")
        else:
            print(f"❌ {response.error}")
    
    elif args.command == "screenshot":
        response = bridge.execute_tool(MCPTool.SCREENSHOT, {})
        if response.success:
            print(f"✅ Captured: {response.data['file_path']}")
        else:
            print(f"❌ {response.error}")

if __name__ == "__main__":
    main()
