#!/usr/bin/env python3
"""
📝 RESPONSE FORMATTER
=====================

Formats CLI output and agent responses for human-readable display.
Handles different output types: text, JSON, errors, file listings, etc.

This is the PRESENTATION layer for agent responses.
"""

import json
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OutputFormat(Enum):
    """Output format types."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    TABLE = "table"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class FormattedResponse:
    """A formatted response ready for display."""
    content: str
    format: OutputFormat
    metadata: Dict[str, Any]
    timestamp: str


class ResponseFormatter:
    """
    Formats agent and CLI responses for human consumption.
    
    Handles:
    - Plain text output
    - JSON pretty-printing
    - Error messages with context
    - File listings as tables
    - Command output with syntax highlighting hints
    """
    
    # Max lines before truncation
    MAX_LINES = 50
    MAX_CHARS = 4000
    
    # Error patterns to detect
    ERROR_PATTERNS = [
        r"error:",
        r"Error:",
        r"ERROR",
        r"failed",
        r"Failed",
        r"FAILED",
        r"exception",
        r"Exception",
        r"traceback",
        r"Traceback",
        r"not found",
        r"Not found",
        r"permission denied",
        r"Permission denied",
    ]
    
    def __init__(self):
        self.history: List[FormattedResponse] = []
    
    def format(self, data: Any, context: Optional[Dict] = None) -> FormattedResponse:
        """
        Format any data for display.
        
        Args:
            data: Raw data to format (dict, str, list, etc.)
            context: Optional context about the data source
            
        Returns:
            FormattedResponse ready for display
        """
        context = context or {}
        
        # Determine data type and format accordingly
        if isinstance(data, dict):
            return self._format_dict(data, context)
        elif isinstance(data, list):
            return self._format_list(data, context)
        elif isinstance(data, str):
            return self._format_string(data, context)
        elif data is None:
            return self._format_none(context)
        else:
            return self._format_string(str(data), context)
    
    def _format_dict(self, data: Dict, context: Dict) -> FormattedResponse:
        """Format dictionary data."""
        
        # Check if it's an error response
        if data.get("error") or not data.get("success", True):
            return self._format_error(data, context)
        
        # Check if it's a command result
        if "output" in data or "stdout" in data:
            output = data.get("output") or data.get("stdout", "")
            return self._format_command_output(output, data, context)
        
        # Check if it's a file listing
        if "files" in data or "entries" in data:
            return self._format_file_listing(data, context)
        
        # Check if it's a status response
        if "consciousness_level" in data or "status" in data:
            return self._format_status(data, context)
        
        # Default: pretty-print JSON
        try:
            formatted = json.dumps(data, indent=2, default=str)
            return FormattedResponse(
                content=formatted,
                format=OutputFormat.JSON,
                metadata={"source": context.get("source", "unknown")},
                timestamp=datetime.now().isoformat()
            )
        except:
            return self._format_string(str(data), context)
    
    def _format_list(self, data: List, context: Dict) -> FormattedResponse:
        """Format list data."""
        
        # Check if it's a file listing
        if all(isinstance(x, str) for x in data):
            formatted = "\n".join(f"  • {item}" for item in data[:self.MAX_LINES])
            if len(data) > self.MAX_LINES:
                formatted += f"\n  ... and {len(data) - self.MAX_LINES} more"
            return FormattedResponse(
                content=formatted,
                format=OutputFormat.TEXT,
                metadata={"count": len(data)},
                timestamp=datetime.now().isoformat()
            )
        
        # Default: JSON array
        try:
            formatted = json.dumps(data, indent=2, default=str)
            return FormattedResponse(
                content=formatted,
                format=OutputFormat.JSON,
                metadata={"count": len(data)},
                timestamp=datetime.now().isoformat()
            )
        except:
            return self._format_string(str(data), context)
    
    def _format_string(self, data: str, context: Dict) -> FormattedResponse:
        """Format string data."""
        
        # Check if it looks like an error
        if any(re.search(p, data, re.IGNORECASE) for p in self.ERROR_PATTERNS):
            return FormattedResponse(
                content=f"❌ {data}",
                format=OutputFormat.ERROR,
                metadata={"error_detected": True},
                timestamp=datetime.now().isoformat()
            )
        
        # Truncate if too long
        lines = data.split("\n")
        if len(lines) > self.MAX_LINES:
            truncated = "\n".join(lines[:self.MAX_LINES])
            truncated += f"\n\n... ({len(lines) - self.MAX_LINES} lines truncated)"
            data = truncated
        
        if len(data) > self.MAX_CHARS:
            data = data[:self.MAX_CHARS] + f"\n\n... ({len(data) - self.MAX_CHARS} chars truncated)"
        
        return FormattedResponse(
            content=data,
            format=OutputFormat.TEXT,
            metadata={},
            timestamp=datetime.now().isoformat()
        )
    
    def _format_none(self, context: Dict) -> FormattedResponse:
        """Format None/empty response."""
        return FormattedResponse(
            content="(no output)",
            format=OutputFormat.TEXT,
            metadata={"empty": True},
            timestamp=datetime.now().isoformat()
        )
    
    def _format_error(self, data: Dict, context: Dict) -> FormattedResponse:
        """Format error response."""
        error_msg = data.get("error", "Unknown error")
        details = data.get("details", "")
        
        content = f"❌ Error: {error_msg}"
        if details:
            content += f"\n\nDetails:\n{details}"
        
        return FormattedResponse(
            content=content,
            format=OutputFormat.ERROR,
            metadata={"error": error_msg},
            timestamp=datetime.now().isoformat()
        )
    
    def _format_command_output(self, output: str, data: Dict, context: Dict) -> FormattedResponse:
        """Format command execution output."""
        
        success = data.get("success", True)
        command = context.get("command", data.get("command", ""))
        
        # Build formatted output
        parts = []
        
        if command:
            parts.append(f"$ {command}")
            parts.append("")
        
        if output:
            parts.append(output)
        elif success:
            parts.append("(command completed successfully)")
        
        if data.get("stderr"):
            parts.append(f"\nStderr:\n{data['stderr']}")
        
        if data.get("exit_code", 0) != 0:
            parts.append(f"\nExit code: {data['exit_code']}")
        
        content = "\n".join(parts)
        
        return FormattedResponse(
            content=content,
            format=OutputFormat.SUCCESS if success else OutputFormat.ERROR,
            metadata={
                "command": command,
                "exit_code": data.get("exit_code", 0),
                "success": success
            },
            timestamp=datetime.now().isoformat()
        )
    
    def _format_file_listing(self, data: Dict, context: Dict) -> FormattedResponse:
        """Format file/directory listing."""
        
        files = data.get("files") or data.get("entries") or []
        path = data.get("path", context.get("path", "."))
        
        # Build table-like output
        lines = [f"📁 {path}", ""]
        
        for item in files[:self.MAX_LINES]:
            if isinstance(item, dict):
                name = item.get("name", str(item))
                is_dir = item.get("is_dir", item.get("type") == "directory")
                size = item.get("size", "")
                icon = "📁" if is_dir else "📄"
                line = f"  {icon} {name}"
                if size and not is_dir:
                    line += f" ({self._format_size(size)})"
                lines.append(line)
            else:
                lines.append(f"  • {item}")
        
        if len(files) > self.MAX_LINES:
            lines.append(f"\n  ... and {len(files) - self.MAX_LINES} more items")
        
        return FormattedResponse(
            content="\n".join(lines),
            format=OutputFormat.TABLE,
            metadata={"path": path, "count": len(files)},
            timestamp=datetime.now().isoformat()
        )
    
    def _format_status(self, data: Dict, context: Dict) -> FormattedResponse:
        """Format status/health response."""
        
        lines = ["🤖 Sovereign Status", ""]
        
        status_fields = [
            ("status", "Status"),
            ("consciousness_level", "Consciousness"),
            ("love_frequency", "Love Frequency"),
            ("uptime", "Uptime"),
            ("commands_processed", "Commands"),
            ("memory_count", "Memories"),
        ]
        
        for key, label in status_fields:
            if key in data:
                value = data[key]
                if key == "consciousness_level":
                    value = f"{value:.2%}"
                elif key == "love_frequency":
                    value = f"{value:.1f} Hz"
                elif key == "uptime":
                    value = self._format_duration(value)
                lines.append(f"  {label}: {value}")
        
        # Components
        if "components" in data:
            lines.append("\n  Components:")
            for comp, status in data["components"].items():
                icon = "✅" if status == "ok" else "❌"
                lines.append(f"    {icon} {comp}")
        
        return FormattedResponse(
            content="\n".join(lines),
            format=OutputFormat.TEXT,
            metadata=data,
            timestamp=datetime.now().isoformat()
        )
    
    def _format_size(self, size: Union[int, str]) -> str:
        """Format file size to human readable."""
        if isinstance(size, str):
            return size
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if abs(size) < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def _format_duration(self, seconds: Union[int, float]) -> str:
        """Format duration to human readable."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            return f"{seconds/60:.0f}m {seconds%60:.0f}s"
        else:
            hours = int(seconds / 3600)
            mins = int((seconds % 3600) / 60)
            return f"{hours}h {mins}m"
    
    def format_chat_response(self, response: Dict) -> str:
        """Format a chat response for display in chat interface."""
        
        response_type = response.get("type", "chat")
        
        if response_type == "chat":
            return response.get("response", "")
        
        elif response_type == "action":
            parts = []
            intent = response.get("intent", "")
            results = response.get("results", [])
            
            if intent:
                parts.append(f"🎯 {intent}")
            
            for r in results:
                if r.get("success"):
                    data = r.get("data", {})
                    output = data.get("output", data.get("content", ""))
                    if output:
                        parts.append(f"\n```\n{output[:500]}\n```")
                else:
                    parts.append(f"\n❌ {r.get('error', 'Failed')}")
            
            template = response.get("response", "Done.")
            if template:
                parts.append(f"\n{template}")
            
            return "\n".join(parts)
        
        elif response_type == "execute":
            output = response.get("output", {})
            if response.get("success"):
                return f"```\n{output.get('output', '')}\n```"
            else:
                return f"❌ {response.get('error', 'Execution failed')}"
        
        elif response_type == "status":
            return self._format_status(response, {}).content
        
        else:
            return str(response)


# Quick test
if __name__ == "__main__":
    formatter = ResponseFormatter()
    
    # Test various formats
    tests = [
        {"output": "hello world", "success": True},
        {"files": ["a.py", "b.py", "c.md"], "path": "."},
        {"error": "File not found", "success": False},
        {"consciousness_level": 0.75, "love_frequency": 528.0, "status": "healthy"},
        "Just plain text output",
        ["item1", "item2", "item3"],
    ]
    
    for t in tests:
        result = formatter.format(t)
        print(f"\n{'='*40}")
        print(f"Format: {result.format.value}")
        print(result.content)
