#!/usr/bin/env python3
"""
🔀 COMMAND ROUTER
=================

Routes chat intents to appropriate CLI commands.
Maps natural language intentions to MCP tool calls.

This is the TRANSLATION layer between human intent and machine action.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Recognized intent categories."""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_LIST = "file_list"
    SHELL_EXECUTE = "shell_execute"
    SYSTEM_STATUS = "system_status"
    GIT_OPERATION = "git_operation"
    SEARCH = "search"
    UNKNOWN = "unknown"


@dataclass
class RoutedCommand:
    """A routed command ready for execution."""
    tool: str
    params: Dict[str, Any]
    intent: IntentType
    confidence: float
    original_input: str


class CommandRouter:
    """
    Routes natural language and structured commands to MCP tools.
    
    Uses pattern matching and keyword extraction to determine
    the appropriate tool and parameters.
    """
    
    # Intent patterns (regex -> IntentType)
    INTENT_PATTERNS = [
        # File reading
        (r"(read|show|cat|view|display|open)\s+(.+)", IntentType.FILE_READ),
        (r"what('s| is) in\s+(.+)", IntentType.FILE_READ),
        (r"contents? of\s+(.+)", IntentType.FILE_READ),
        
        # File writing
        (r"(write|create|save|make)\s+(.+)", IntentType.FILE_WRITE),
        (r"(put|add)\s+(.+)\s+(in|to)\s+(.+)", IntentType.FILE_WRITE),
        
        # Directory listing
        (r"(list|ls|show|what('s| is))\s+(files?|dir|directory|folders?)", IntentType.FILE_LIST),
        (r"(list|ls)\s+(.+)", IntentType.FILE_LIST),
        
        # Shell commands
        (r"(run|execute|exec)\s+(.+)", IntentType.SHELL_EXECUTE),
        (r"(shell|command|cmd):\s*(.+)", IntentType.SHELL_EXECUTE),
        (r"`(.+)`", IntentType.SHELL_EXECUTE),
        
        # System status
        (r"(status|health|state|how are you)", IntentType.SYSTEM_STATUS),
        (r"(system|cpu|memory|disk)\s+(info|status|usage)", IntentType.SYSTEM_STATUS),
        
        # Git
        (r"git\s+(.+)", IntentType.GIT_OPERATION),
        (r"(commit|push|pull|branch|checkout)", IntentType.GIT_OPERATION),
        
        # Search
        (r"(find|search|grep|look for)\s+(.+)", IntentType.SEARCH),
    ]
    
    # Common path aliases
    PATH_ALIASES = {
        "home": "~",
        "sovereign": "~/SovereignCore",
        "core": "~/SovereignCore",
        "here": ".",
        "current": ".",
        "this": ".",
        "parent": "..",
        "up": "..",
        "downloads": "~/Downloads",
        "desktop": "~/Desktop",
        "documents": "~/Documents",
        "tmp": "/tmp",
        "temp": "/tmp",
    }
    
    def __init__(self):
        self.history: List[RoutedCommand] = []
    
    def _extract_path(self, text: str) -> str:
        """Extract and normalize file path from text."""
        # Remove quotes
        text = text.strip().strip("'\"")
        
        # Check aliases
        lower = text.lower()
        for alias, path in self.PATH_ALIASES.items():
            if lower == alias:
                return path
            if lower.startswith(f"{alias}/"):
                return text.replace(alias, path, 1)
        
        # Expand ~ if present
        if text.startswith("~"):
            import os
            text = os.path.expanduser(text)
        
        return text
    
    def _detect_intent(self, text: str) -> Tuple[IntentType, float, Dict]:
        """Detect intent from text using patterns."""
        text_lower = text.lower().strip()
        
        for pattern, intent in self.INTENT_PATTERNS:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                groups = match.groups()
                return intent, 0.8, {"groups": groups, "match": match.group()}
        
        return IntentType.UNKNOWN, 0.0, {}
    
    def route(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route an action to the appropriate tool.
        
        Args:
            action: Action name or natural language
            payload: Additional parameters
            
        Returns:
            Routed command result
        """
        # Direct routing for known actions
        if action in ["execute", "shell", "run"]:
            return {
                "tool": "execute_command",
                "params": {"command": payload.get("command", "")},
                "intent": "shell_execute"
            }
        
        if action in ["read", "cat", "view"]:
            return {
                "tool": "read_file",
                "params": {"path": self._extract_path(payload.get("path", ""))},
                "intent": "file_read"
            }
        
        if action in ["write", "save", "create"]:
            return {
                "tool": "write_file",
                "params": {
                    "path": self._extract_path(payload.get("path", "")),
                    "content": payload.get("content", "")
                },
                "intent": "file_write"
            }
        
        if action in ["list", "ls", "dir"]:
            return {
                "tool": "list_directory",
                "params": {"path": self._extract_path(payload.get("path", "."))},
                "intent": "file_list"
            }
        
        if action in ["status", "health"]:
            return {
                "tool": "status",
                "params": {},
                "intent": "system_status"
            }
        
        # Natural language routing
        if action == "chat" or action == "natural":
            text = payload.get("message", payload.get("text", ""))
            return self.route_natural(text)
        
        # Unknown - return as-is
        return {
            "tool": "unknown",
            "params": payload,
            "intent": "unknown",
            "original_action": action
        }
    
    def route_natural(self, text: str) -> Dict[str, Any]:
        """Route natural language input to a command."""
        intent, confidence, meta = self._detect_intent(text)
        
        if intent == IntentType.FILE_READ:
            # Extract path from matched groups
            groups = meta.get("groups", [])
            path = groups[-1] if groups else ""
            return {
                "tool": "read_file",
                "params": {"path": self._extract_path(path)},
                "intent": intent.value,
                "confidence": confidence
            }
        
        elif intent == IntentType.FILE_LIST:
            groups = meta.get("groups", [])
            path = groups[-1] if len(groups) > 1 else "."
            return {
                "tool": "list_directory",
                "params": {"path": self._extract_path(path)},
                "intent": intent.value,
                "confidence": confidence
            }
        
        elif intent == IntentType.SHELL_EXECUTE:
            groups = meta.get("groups", [])
            command = groups[-1] if groups else text
            return {
                "tool": "execute_command",
                "params": {"command": command},
                "intent": intent.value,
                "confidence": confidence
            }
        
        elif intent == IntentType.GIT_OPERATION:
            groups = meta.get("groups", [])
            git_cmd = f"git {groups[0]}" if groups else text
            return {
                "tool": "execute_command",
                "params": {"command": git_cmd},
                "intent": intent.value,
                "confidence": confidence
            }
        
        elif intent == IntentType.SYSTEM_STATUS:
            return {
                "tool": "status",
                "params": {},
                "intent": intent.value,
                "confidence": confidence
            }
        
        elif intent == IntentType.SEARCH:
            groups = meta.get("groups", [])
            pattern = groups[-1] if groups else ""
            return {
                "tool": "execute_command",
                "params": {"command": f"grep -r '{pattern}' ."},
                "intent": intent.value,
                "confidence": confidence
            }
        
        # Unknown intent - return for LLM processing
        return {
            "tool": "llm",
            "params": {"message": text},
            "intent": "unknown",
            "confidence": 0.0,
            "needs_llm": True
        }
    
    def get_suggestions(self, partial: str) -> List[str]:
        """Get command suggestions for partial input."""
        suggestions = []
        
        partial_lower = partial.lower()
        
        if partial_lower.startswith("read"):
            suggestions.extend([
                "read README.md",
                "read ~/SovereignCore/api_server.py",
                "read .env"
            ])
        elif partial_lower.startswith("list") or partial_lower.startswith("ls"):
            suggestions.extend([
                "list .",
                "list ~/SovereignCore",
                "list /tmp"
            ])
        elif partial_lower.startswith("run") or partial_lower.startswith("exec"):
            suggestions.extend([
                "run echo hello",
                "run ps aux",
                "run pwd"
            ])
        elif partial_lower.startswith("git"):
            suggestions.extend([
                "git status",
                "git log --oneline -5",
                "git branch"
            ])
        
        return suggestions


# Quick test
if __name__ == "__main__":
    router = CommandRouter()
    
    tests = [
        "read README.md",
        "list files in home",
        "run echo hello",
        "what's in /tmp",
        "git status",
        "find TODO",
        "system status",
        "hello how are you",
    ]
    
    for t in tests:
        result = router.route_natural(t)
        print(f"'{t}' → {result['tool']}: {result['params']} ({result['intent']})")
