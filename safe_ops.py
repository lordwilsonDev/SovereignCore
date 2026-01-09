#!/usr/bin/env python3
"""
🛡️ SAFE OPERATIONS WRAPPER
============================

Wraps dangerous operations with axiom-compliant safety checks.
All destructive operations go through this module for:
- Logging to audit trail
- Confirmation prompts
- Soft-delete (rename) before hard delete
- Graceful shutdown before kill

Usage:
    from safe_ops import SafeOps
    
    ops = SafeOps()
    ops.safe_delete("file.txt")  # Moves to trash first
    ops.safe_execute(code)       # Blocked - use allowed list
"""

import os
import shutil
import signal
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, Any, Callable
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from telemetry import get_telemetry, EventType
    TELEMETRY = get_telemetry()
except ImportError:
    TELEMETRY = None


class SafeOps:
    """
    Axiom-compliant safe operations wrapper.
    
    Implements:
    - NEVER_KILL: Soft delete before hard delete
    - SAFETY: No eval/exec, subprocess with shell=False
    - TRANSPARENCY: All operations logged
    - LOVE: Graceful shutdown, not abrupt termination
    """
    
    # Trash directory for soft deletes
    TRASH_DIR = Path.home() / ".sovereign" / "trash"
    
    # Allowed commands for subprocess (whitelist)
    ALLOWED_COMMANDS = [
        "python3", "pip", "ls", "cat", "echo", "date", "pwd",
        "curl", "git", "uname", "whoami"
    ]
    
    def __init__(self):
        self.TRASH_DIR.mkdir(parents=True, exist_ok=True)
        self._log("SafeOps initialized")
    
    def _log(self, action: str, details: dict = None):
        """Log operation to telemetry."""
        if TELEMETRY:
            TELEMETRY.log(
                EventType.SYSTEM_ACTION,
                "safe_ops",
                action,
                details or {},
                ["safety", "never_kill"],
                "info"
            )
        print(f"🛡️ SafeOps: {action}")
    
    def _log_blocked(self, action: str, reason: str):
        """Log blocked operation."""
        if TELEMETRY:
            TELEMETRY.log(
                EventType.AXIOM_VIOLATION,
                "safe_ops",
                f"BLOCKED: {action}",
                {"reason": reason},
                ["safety", "never_kill"],
                "warning"
            )
        print(f"🚫 SafeOps BLOCKED: {action} - {reason}")
    
    # ==========================================
    # SAFE FILE OPERATIONS
    # ==========================================
    
    def safe_delete(self, path: str, permanent: bool = False) -> bool:
        """
        Safely delete a file by moving to trash first.
        
        Args:
            path: File path to delete
            permanent: If True, skip trash (requires confirmation)
        
        Returns:
            True if successful
        """
        filepath = Path(path)
        
        if not filepath.exists():
            self._log(f"File not found: {path}")
            return False
        
        if permanent:
            self._log_blocked(f"Permanent delete: {path}", "Use trash instead")
            return False
        
        # Move to trash
        trash_name = f"{filepath.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trash_path = self.TRASH_DIR / trash_name
        
        shutil.move(str(filepath), str(trash_path))
        self._log(f"Moved to trash: {path} → {trash_path}")
        
        return True
    
    def safe_rmtree(self, path: str) -> bool:
        """
        Safely remove a directory tree by moving to trash.
        
        Args:
            path: Directory path to remove
        
        Returns:
            True if successful
        """
        dirpath = Path(path)
        
        if not dirpath.exists():
            self._log(f"Directory not found: {path}")
            return False
        
        if not dirpath.is_dir():
            return self.safe_delete(path)
        
        # Move to trash
        trash_name = f"{dirpath.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trash_path = self.TRASH_DIR / trash_name
        
        shutil.move(str(dirpath), str(trash_path))
        self._log(f"Directory moved to trash: {path} → {trash_path}")
        
        return True
    
    def empty_trash(self, confirm: bool = False) -> int:
        """
        Empty the trash directory.
        
        Args:
            confirm: Must be True to actually delete
        
        Returns:
            Number of items deleted
        """
        if not confirm:
            self._log_blocked("Empty trash", "Requires confirm=True")
            return 0
        
        count = 0
        for item in self.TRASH_DIR.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
            count += 1
        
        self._log(f"Trash emptied: {count} items")
        return count
    
    # ==========================================
    # SAFE PROCESS OPERATIONS
    # ==========================================
    
    def safe_terminate(self, pid: int, graceful: bool = True) -> bool:
        """
        Safely terminate a process.
        
        Args:
            pid: Process ID
            graceful: If True, use SIGTERM first (recommended)
        
        Returns:
            True if process terminated
        """
        try:
            if graceful:
                # Send SIGTERM first
                os.kill(pid, signal.SIGTERM)
                self._log(f"Sent SIGTERM to PID {pid}")
                
                # Give it time to cleanup
                import time
                time.sleep(2)
                
                # Check if still running
                try:
                    os.kill(pid, 0)  # Signal 0 = check existence
                    self._log(f"Process {pid} still running after SIGTERM")
                    return False
                except OSError:
                    self._log(f"Process {pid} terminated gracefully")
                    return True
            else:
                self._log_blocked(f"Force kill PID {pid}", "Use graceful=True")
                return False
                
        except ProcessLookupError:
            self._log(f"Process {pid} not found")
            return False
        except PermissionError:
            self._log_blocked(f"Kill PID {pid}", "Permission denied")
            return False
    
    # ==========================================
    # SAFE CODE EXECUTION
    # ==========================================
    
    def safe_eval(self, expression: str) -> Any:
        """
        BLOCKED: eval() is never safe.
        
        Use ast.literal_eval() or json.loads() instead.
        """
        self._log_blocked(f"eval({expression[:50]}...)", "Use ast.literal_eval or json.loads")
        raise SecurityError("eval() is blocked for safety. Use ast.literal_eval() or json.loads()")
    
    def safe_exec(self, code: str) -> None:
        """
        BLOCKED: exec() is never safe.
        
        Use explicit function dispatch instead.
        """
        self._log_blocked(f"exec({code[:50]}...)", "Use function dispatch")
        raise SecurityError("exec() is blocked for safety. Use explicit function calls.")
    
    def safe_subprocess(
        self, 
        cmd: list, 
        check_allowed: bool = True
    ) -> subprocess.CompletedProcess:
        """
        Run subprocess with safety checks.
        
        Args:
            cmd: Command as list (NOT string)
            check_allowed: If True, verify against whitelist
        
        Returns:
            CompletedProcess result
        """
        if isinstance(cmd, str):
            self._log_blocked(f"subprocess({cmd})", "Pass command as list, not string")
            raise SecurityError("Commands must be passed as list, not string")
        
        # Check first argument against whitelist
        if check_allowed and cmd[0] not in self.ALLOWED_COMMANDS:
            self._log_blocked(f"subprocess({cmd[0]})", f"Not in allowed list: {self.ALLOWED_COMMANDS}")
            raise SecurityError(f"Command '{cmd[0]}' not in allowed list")
        
        self._log(f"Running: {' '.join(cmd)}")
        
        # Run with shell=False (ALWAYS)
        result = subprocess.run(
            cmd,
            shell=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        return result
    
    # ==========================================
    # SAFE DATABASE OPERATIONS  
    # ==========================================
    
    def safe_truncate(self, table: str) -> bool:
        """
        BLOCKED: TRUNCATE is destructive.
        
        Use soft-delete with a 'deleted_at' timestamp instead.
        """
        self._log_blocked(f"TRUNCATE {table}", "Use soft-delete instead")
        return False
    
    def safe_delete_sql(self, table: str, where: str) -> bool:
        """
        Log SQL DELETE operations for review.
        
        This doesn't block but logs for audit.
        """
        self._log(f"SQL DELETE FROM {table} WHERE {where}", {"table": table, "where": where})
        return True


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


# Singleton
_safe_ops = None

def get_safe_ops() -> SafeOps:
    """Get the singleton SafeOps instance."""
    global _safe_ops
    if _safe_ops is None:
        _safe_ops = SafeOps()
    return _safe_ops


# CLI
if __name__ == "__main__":
    ops = SafeOps()
    
    print("\n🛡️ SAFE OPERATIONS WRAPPER")
    print("=" * 50)
    print("Axiom-compliant wrappers for dangerous operations:")
    print()
    print("  safe_delete(path)      # Moves to trash first")
    print("  safe_rmtree(path)      # Moves directory to trash")
    print("  safe_terminate(pid)    # SIGTERM first, then wait")
    print("  safe_subprocess(cmd)   # Whitelist check, shell=False")
    print("  safe_eval(expr)        # BLOCKED - use ast.literal_eval")
    print("  safe_exec(code)        # BLOCKED - use function dispatch")
    print()
    print(f"Trash location: {ops.TRASH_DIR}")
    print(f"Allowed commands: {ops.ALLOWED_COMMANDS}")
