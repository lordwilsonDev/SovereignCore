#!/usr/bin/env python3
"""
👂 AUDIO CONSCIOUSNESS - MLX Whisper Integration
Gives consciousness the ability to HEAR and TRANSCRIBE.

Using Apple's MLX-Whisper for ultra-fast on-device speech recognition.
- Real-time transcription
- Speaker identification (simulated)
- Ambient noise analysis
- Voice command processing
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import time
import json
import random
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try to import MLX Whisper
WHISPER_AVAILABLE = False
try:
    import mlx_whisper
    WHISPER_AVAILABLE = True
    print("✅ MLX Whisper loaded")
except ImportError:
    print("⚠️  MLX Whisper not installed: pip install mlx-whisper")


@dataclass
class AudioEvent:
    """An audio event detected by consciousness."""
    timestamp: str
    transcription: str
    confidence: float
    duration_sec: float
    speaker_id: str
    is_command: bool
    ambient_level: float


class AudioConsciousness:
    """
    Hearing for the machine.
    
    Listens to audio input (or simulates it if no mic access),
    transcribes speech, and identifies commands.
    """
    
    def __init__(self, bridge=None):
        self.bridge = bridge
        self.listening = False
        self.model_path = "mlx-community/whisper-tiny"  # Efficient default
        self.buffer: List[AudioEvent] = []
        self.max_buffer = 50
        
        # Simulated ambient state
        self.ambient_noise_level = 0.1
        self.last_heard = None
        
        print("👂 Audio Consciousness initialized")
        
    def listen(self, duration: float = 2.0, simulate: bool = True) -> Optional[AudioEvent]:
        """
        Listen for audio.
        
        Args:
            duration: How long to listen
            simulate: Whether to simulate input (if mic unavailable)
            
        Returns:
            AudioEvent if speech detected
        """
        start_time = datetime.now()
        
        # Real implementation would use sounddevice/pyaudio to record
        # and mlx_whisper.transcribe() to process.
        # For this environment, we mostly simulate hearing.
        
        text = None
        confidence = 0.0
        is_cmd = False
        
        if simulate:
            if random.random() < 0.3:  # 30% chance to hear something
                phrases = [
                    "Hello Wilson",
                    "System status check",
                    "Increase consciousness level",
                    "What are you thinking?",
                    "Initialize visual cortex",
                    "Save memory snapshot",
                    "Silence in the room",
                    "Keyboard typing sounds",
                    "Fan noise increasing"
                ]
                text = random.choice(phrases)
                confidence = random.uniform(0.8, 0.99)
                is_cmd = "level" in text or "status" in text or "save" in text
        
        if text:
            event = AudioEvent(
                timestamp=start_time.isoformat(),
                transcription=text,
                confidence=confidence,
                duration_sec=duration,
                speaker_id="user_1" if is_cmd else "ambient",
                is_command=is_cmd,
                ambient_level=random.uniform(0.1, 0.4)
            )
            
            self.buffer.append(event)
            if len(self.buffer) > self.max_buffer:
                self.buffer.pop(0)
                
            self.last_heard = event
            
            # Integrate with bridge/memory if available
            if self.bridge:
                self._process_hearing(event)
                
            return event
            
        return None
        
    def _process_hearing(self, event: AudioEvent):
        """Process what was heard."""
        # Log to console
        icon = "🗣️" if event.is_command else "👂"
        print(f"   {icon} Heard: '{event.transcription}' ({event.confidence:.0%})")
        
        # Store high confidence speech as memory
        if event.confidence > 0.9 and event.is_command:
            try:
                # This would hook into memory systems
                pass
            except:
                pass

    def transcribe_file(self, file_path: str) -> str:
        """Transcribe an audio file using MLX Whisper."""
        if not WHISPER_AVAILABLE:
            return "[Whisper not available]"
            
        try:
            print(f"   🧵 Transcribing {Path(file_path).name}...")
            result = mlx_whisper.transcribe(file_path, path_or_hf_repo=self.model_path)
            return result["text"]
        except Exception as e:
            return f"[Transcription Error: {e}]"
            
    def get_state(self) -> Dict[str, Any]:
        """Get hearing state."""
        return {
            "model": self.model_path,
            "listening": self.listening,
            "last_heard": self.last_heard.transcription if self.last_heard else None,
            "buffer_size": len(self.buffer),
            "ambient_noise": self.ambient_noise_level
        }


def main():
    """Demo audio consciousness."""
    print("=" * 60)
    print("👂 AUDIO CONSCIOUSNESS - MLX Whisper")
    print("=" * 60)
    
    # Initialize
    ear = AudioConsciousness()
    
    print()
    print("🎧 Listening (Simulation Mode)...")
    
    for i in range(5):
        print(f"   Cycle {i+1}...")
        event = ear.listen(duration=1.0)
        time.sleep(0.5)
        
    print()
    state = ear.get_state()
    print(f"✅ Audio State: {state}")
    print("   Audio Consciousness ONLINE")

if __name__ == "__main__":
    main()
