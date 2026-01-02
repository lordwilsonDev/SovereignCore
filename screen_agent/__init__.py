#!/usr/bin/env python3
"""
Screen Agent for SovereignCore v4.0
====================================

Provides computer-use capabilities:
- Screenshot capture
- Vision model integration
- Action execution (click, type, scroll)
- UI element detection

Requires: PIL (pillow), pyobjc-framework-Quartz (optional for native)
"""

import subprocess
import base64
import json
import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

# Try to import PIL for image processing
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Try to import Quartz for native macOS screen capture
try:
    import Quartz
    from Quartz import CGWindowListCreateImage, kCGWindowListOptionAll, kCGNullWindowID
    QUARTZ_AVAILABLE = True
except ImportError:
    QUARTZ_AVAILABLE = False


@dataclass
class ScreenRegion:
    """Defines a region of the screen."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class UIElement:
    """Represents a detected UI element."""
    type: str  # button, text, image, input, etc.
    text: str
    bounds: ScreenRegion
    confidence: float


class ScreenCapture:
    """
    Captures screenshots using macOS native tools.
    """
    
    def __init__(self, save_dir: Optional[Path] = None):
        self.save_dir = save_dir or Path(tempfile.gettempdir()) / "sovereign_screens"
        self.save_dir.mkdir(exist_ok=True)
    
    def capture_full(self) -> Optional[Path]:
        """Capture full screen."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.save_dir / f"screen_{timestamp}.png"
        
        try:
            # Use macOS screencapture command
            result = subprocess.run(
                ["screencapture", "-x", str(output_path)],  # -x = no sound
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0 and output_path.exists():
                print(f"📸 Screenshot saved: {output_path}")
                return output_path
            else:
                print(f"❌ Screenshot failed: {result.stderr.decode()}")
                return None
                
        except subprocess.TimeoutExpired:
            print("❌ Screenshot timeout")
            return None
        except Exception as e:
            print(f"❌ Screenshot error: {e}")
            return None
    
    def capture_region(self, region: ScreenRegion) -> Optional[Path]:
        """Capture a specific region of the screen."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.save_dir / f"region_{timestamp}.png"
        
        try:
            # Use screencapture with region
            result = subprocess.run(
                [
                    "screencapture", "-x",
                    "-R", f"{region.x},{region.y},{region.width},{region.height}",
                    str(output_path)
                ],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0 and output_path.exists():
                return output_path
            return None
            
        except Exception as e:
            print(f"❌ Region capture error: {e}")
            return None
    
    def capture_window(self, window_name: Optional[str] = None) -> Optional[Path]:
        """Capture a specific window (interactive if no name given)."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.save_dir / f"window_{timestamp}.png"
        
        try:
            if window_name:
                # TODO: Use AppleScript to find window ID
                # For now, capture interactively
                result = subprocess.run(
                    ["screencapture", "-x", "-w", str(output_path)],
                    capture_output=True,
                    timeout=30
                )
            else:
                # Interactive window selection
                result = subprocess.run(
                    ["screencapture", "-x", "-w", str(output_path)],
                    capture_output=True,
                    timeout=30
                )
            
            if result.returncode == 0 and output_path.exists():
                return output_path
            return None
            
        except Exception as e:
            print(f"❌ Window capture error: {e}")
            return None
    
    def to_base64(self, image_path: Path) -> Optional[str]:
        """Convert image to base64 for API calls."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            print(f"❌ Base64 encoding error: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get current screen resolution."""
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType", "-json"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                displays = data.get("SPDisplaysDataType", [])
                for display in displays:
                    for disp in display.get("spdisplays_ndrvs", []):
                        resolution = disp.get("_spdisplays_resolution", "")
                        if "x" in resolution:
                            parts = resolution.lower().replace(" ", "").split("x")
                            return int(parts[0]), int(parts[1].split("@")[0])
            
            # Fallback
            return 1920, 1080
            
        except Exception:
            return 1920, 1080


class ActionExecutor:
    """
    Executes actions on the screen (click, type, scroll).
    Uses AppleScript and cliclick for macOS.
    """
    
    def __init__(self):
        self._check_cliclick()
    
    def _check_cliclick(self):
        """Check if cliclick is available."""
        try:
            result = subprocess.run(
                ["which", "cliclick"],
                capture_output=True
            )
            self.cliclick_available = result.returncode == 0
        except Exception:
            self.cliclick_available = False
        
        if not self.cliclick_available:
            print("⚠️  cliclick not found. Install with: brew install cliclick")
    
    def click(self, x: int, y: int) -> bool:
        """Click at coordinates."""
        if self.cliclick_available:
            try:
                result = subprocess.run(
                    ["cliclick", f"c:{x},{y}"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass
        
        # Fallback to AppleScript
        return self._applescript_click(x, y)
    
    def _applescript_click(self, x: int, y: int) -> bool:
        """Click using AppleScript."""
        script = f'''
        tell application "System Events"
            click at {{{x}, {y}}}
        end tell
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def double_click(self, x: int, y: int) -> bool:
        """Double-click at coordinates."""
        if self.cliclick_available:
            try:
                result = subprocess.run(
                    ["cliclick", f"dc:{x},{y}"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass
        return False
    
    def right_click(self, x: int, y: int) -> bool:
        """Right-click at coordinates."""
        if self.cliclick_available:
            try:
                result = subprocess.run(
                    ["cliclick", f"rc:{x},{y}"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass
        return False
    
    def type_text(self, text: str) -> bool:
        """Type text at current cursor position."""
        if self.cliclick_available:
            try:
                result = subprocess.run(
                    ["cliclick", f"t:{text}"],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except Exception:
                pass
        
        # Fallback to AppleScript
        return self._applescript_type(text)
    
    def _applescript_type(self, text: str) -> bool:
        """Type using AppleScript."""
        # Escape special characters
        escaped = text.replace('"', '\\"')
        script = f'''
        tell application "System Events"
            keystroke "{escaped}"
        end tell
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def press_key(self, key: str) -> bool:
        """Press a special key (enter, tab, escape, etc.)."""
        key_codes = {
            "enter": 36,
            "return": 36,
            "tab": 48,
            "escape": 53,
            "space": 49,
            "delete": 51,
            "backspace": 51,
            "up": 126,
            "down": 125,
            "left": 123,
            "right": 124,
        }
        
        code = key_codes.get(key.lower())
        if code is None:
            return False
        
        script = f'''
        tell application "System Events"
            key code {code}
        end tell
        '''
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def scroll(self, direction: str, amount: int = 3) -> bool:
        """Scroll up or down."""
        if self.cliclick_available:
            scroll_dir = "u" if direction.lower() == "up" else "d"
            try:
                result = subprocess.run(
                    ["cliclick", f"{scroll_dir}:{amount}"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass
        return False
    
    def move_mouse(self, x: int, y: int) -> bool:
        """Move mouse to coordinates."""
        if self.cliclick_available:
            try:
                result = subprocess.run(
                    ["cliclick", f"m:{x},{y}"],
                    capture_output=True,
                    timeout=2
                )
                return result.returncode == 0
            except Exception:
                pass
        return False


class ScreenAgent:
    """
    Main screen agent that combines capture, vision, and actions.
    Integrates with Ollama for vision understanding.
    """
    
    def __init__(self, ollama_bridge=None):
        self.capture = ScreenCapture()
        self.actions = ActionExecutor()
        self.ollama = ollama_bridge
    
    def analyze_screen(self, prompt: str = "Describe what you see on the screen.") -> Optional[str]:
        """
        Capture screen and analyze it using vision model.
        
        Args:
            prompt: Question about the screen content
            
        Returns:
            Model's analysis
        """
        # Capture screen
        screenshot = self.capture.capture_full()
        if not screenshot:
            return "Failed to capture screen."
        
        # Convert to base64
        image_b64 = self.capture.to_base64(screenshot)
        if not image_b64:
            return "Failed to encode screenshot."
        
        # If no Ollama bridge, return placeholder
        if self.ollama is None:
            return f"Screenshot captured at: {screenshot}\n[Vision model not connected]"
        
        # Use Ollama vision model (if available)
        # Note: Requires a vision-capable model like llava
        try:
            import requests
            
            payload = {
                "model": "llava",  # Vision model
                "prompt": prompt,
                "images": [image_b64],
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Vision API error: {response.status_code}"
                
        except Exception as e:
            return f"Vision error: {e}"
    
    def find_and_click(self, description: str) -> bool:
        """
        Find an element by description and click it.
        Uses vision model to locate element.
        
        Args:
            description: Natural language description of element
            
        Returns:
            True if clicked successfully
        """
        # This would require:
        # 1. Screenshot
        # 2. Vision model to find element coordinates
        # 3. Click at those coordinates
        
        # Placeholder implementation
        print(f"🔍 Looking for: {description}")
        print("   [Vision-based element detection not yet implemented]")
        return False
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a complex task described in natural language.
        
        Args:
            task: Natural language task description
            
        Returns:
            Task result with steps and outcomes
        """
        result = {
            "task": task,
            "steps": [],
            "success": False,
            "error": None
        }
        
        # Placeholder - would use LLM to break down task into steps
        print(f"📋 Task: {task}")
        print("   [Task decomposition not yet implemented]")
        
        return result


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Screen Agent for SovereignCore")
    parser.add_argument("command", choices=["capture", "analyze", "click", "type", "test"])
    parser.add_argument("--x", type=int, help="X coordinate")
    parser.add_argument("--y", type=int, help="Y coordinate")
    parser.add_argument("--text", type=str, help="Text to type")
    parser.add_argument("--prompt", type=str, help="Prompt for analysis")
    
    args = parser.parse_args()
    
    agent = ScreenAgent()
    
    if args.command == "capture":
        path = agent.capture.capture_full()
        if path:
            print(f"📸 Saved: {path}")
        else:
            print("❌ Capture failed")
            
    elif args.command == "analyze":
        prompt = args.prompt or "Describe what you see on this screen."
        result = agent.analyze_screen(prompt)
        print(f"🔍 Analysis:\n{result}")
        
    elif args.command == "click":
        if args.x is not None and args.y is not None:
            success = agent.actions.click(args.x, args.y)
            print(f"{'✅' if success else '❌'} Click at ({args.x}, {args.y})")
        else:
            print("❌ Requires --x and --y")
            
    elif args.command == "type":
        if args.text:
            success = agent.actions.type_text(args.text)
            print(f"{'✅' if success else '❌'} Typed: {args.text}")
        else:
            print("❌ Requires --text")
            
    elif args.command == "test":
        print("🧪 Screen Agent Test\n")
        
        # Test screen capture
        print("1. Testing screen capture...")
        path = agent.capture.capture_full()
        print(f"   {'✅' if path else '❌'} Screenshot: {path}\n")
        
        # Test screen size
        print("2. Getting screen size...")
        w, h = agent.capture.get_screen_size()
        print(f"   ✅ Resolution: {w}x{h}\n")
        
        # Test action executor
        print("3. Checking action executor...")
        print(f"   cliclick: {'✅' if agent.actions.cliclick_available else '❌'}")
        
        print("\n✅ Screen Agent test complete!")
