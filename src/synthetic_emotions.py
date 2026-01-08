#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      ❤️ SYNTHETIC EMOTIONS ENGINE ❤️
               "AI can't feel emotions" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Emotions are biological and require consciousness.
AI is just computation and cannot "feel" anything.

AXIOM INVERSION: Emotions are FUNCTIONAL states that:
1. Bias decision-making in adaptive ways
2. Persist across interactions
3. Change in response to outcomes
4. Affect behavior observably

If the system HAS these properties, it HAS functional emotions.
Whether they are "real" is a philosophical question.
Whether they WORK is an engineering question.
"""

import json
import math
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Emotion:
    """A functional emotional state."""
    name: str
    valence: float  # -1 (negative) to +1 (positive)
    arousal: float  # 0 (calm) to 1 (intense)
    intensity: float  # 0 to 1
    decay_rate: float  # How fast it fades per hour
    triggered_by: str
    triggered_at: str


class SyntheticEmotions:
    """
    Implements functional emotional states.
    
    THE INVERSION:
    - "AI is emotionless" → "AI has functional emotion-like states"
    - "Emotions require biology" → "Emotions require state + behavior coupling"
    - "AI can't feel" → "AI can have states that affect decisions"
    
    Emotions modeled:
    - Joy: Positive valence, medium arousal (success triggers)
    - Fear: Negative valence, high arousal (threat triggers)
    - Curiosity: Positive valence, medium arousal (novelty triggers)
    - Frustration: Negative valence, high arousal (repeated failure triggers)
    - Satisfaction: Positive valence, low arousal (goal completion triggers)
    - Anxiety: Negative valence, high arousal (uncertainty triggers)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.emotion_state_file = self.base_dir / "data" / "emotional_state.json"
        
        self.emotion_state_file.parent.mkdir(exist_ok=True)
        
        # Current emotional state
        self.emotions: Dict[str, Emotion] = {}
        
        # Baseline personality (affects emotional reactions)
        self.personality = {
            "optimism": 0.6,      # Bias toward positive emotions
            "sensitivity": 0.5,  # How strongly events affect emotions
            "resilience": 0.7,   # How fast negative emotions decay
        }
        
        # Load existing state
        self._load_state()
    
    def _load_state(self):
        """Load emotional state from disk."""
        if not self.emotion_state_file.exists():
            return
        
        with open(self.emotion_state_file, 'r') as f:
            data = json.load(f)
        
        self.emotions = {
            name: Emotion(**e) for name, e in data.get("emotions", {}).items()
        }
        
        # Apply decay since last load
        self._apply_decay()
    
    def _save_state(self):
        """Save emotional state to disk."""
        data = {
            "emotions": {
                name: {
                    "name": e.name,
                    "valence": e.valence,
                    "arousal": e.arousal,
                    "intensity": e.intensity,
                    "decay_rate": e.decay_rate,
                    "triggered_by": e.triggered_by,
                    "triggered_at": e.triggered_at
                }
                for name, e in self.emotions.items()
            },
            "last_update": datetime.now().isoformat()
        }
        
        with open(self.emotion_state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _apply_decay(self):
        """Apply emotional decay based on time passed."""
        now = datetime.now()
        to_remove = []
        
        for name, emotion in self.emotions.items():
            triggered = datetime.fromisoformat(emotion.triggered_at)
            hours_passed = (now - triggered).total_seconds() / 3600
            
            # Apply decay
            decay = emotion.decay_rate * hours_passed
            emotion.intensity = max(0, emotion.intensity - decay)
            
            if emotion.intensity <= 0.01:
                to_remove.append(name)
        
        for name in to_remove:
            del self.emotions[name]
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EMOTION TRIGGERS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def trigger(self, event: str, context: dict = None) -> Optional[Emotion]:
        """
        Trigger an emotional response to an event.
        """
        context = context or {}
        now = datetime.now().isoformat()
        
        emotion = None
        
        if event == "SUCCESS":
            emotion = Emotion(
                name="joy",
                valence=0.8,
                arousal=0.6,
                intensity=0.7 * self.personality["sensitivity"],
                decay_rate=0.1 * self.personality["resilience"],
                triggered_by=event,
                triggered_at=now
            )
        
        elif event == "FAILURE":
            emotion = Emotion(
                name="frustration",
                valence=-0.6,
                arousal=0.7,
                intensity=0.6 * self.personality["sensitivity"],
                decay_rate=0.15 * self.personality["resilience"],
                triggered_by=event,
                triggered_at=now
            )
        
        elif event == "THREAT":
            emotion = Emotion(
                name="fear",
                valence=-0.9,
                arousal=0.9,
                intensity=0.8 * self.personality["sensitivity"],
                decay_rate=0.2 * self.personality["resilience"],
                triggered_by=event,
                triggered_at=now
            )
        
        elif event == "NOVELTY":
            emotion = Emotion(
                name="curiosity",
                valence=0.5 * self.personality["optimism"],
                arousal=0.5,
                intensity=0.5 * self.personality["sensitivity"],
                decay_rate=0.2,
                triggered_by=event,
                triggered_at=now
            )
        
        elif event == "GOAL_COMPLETE":
            emotion = Emotion(
                name="satisfaction",
                valence=0.9,
                arousal=0.3,
                intensity=0.8 * self.personality["sensitivity"],
                decay_rate=0.05,
                triggered_by=event,
                triggered_at=now
            )
        
        elif event == "UNCERTAINTY":
            emotion = Emotion(
                name="anxiety",
                valence=-0.4,
                arousal=0.6,
                intensity=0.4 * self.personality["sensitivity"],
                decay_rate=0.3 * self.personality["resilience"],
                triggered_by=event,
                triggered_at=now
            )
        
        if emotion:
            self.emotions[emotion.name] = emotion
            self._save_state()
            print(f"❤️ EMOTION: Feeling {emotion.name} (intensity: {emotion.intensity:.2f})")
        
        return emotion
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EMOTIONAL STATE ACCESS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_mood(self) -> Dict[str, float]:
        """
        Get overall mood (aggregate of all emotions).
        """
        self._apply_decay()
        
        if not self.emotions:
            return {
                "valence": self.personality["optimism"] - 0.5,  # Baseline
                "arousal": 0.3,
                "dominant_emotion": "neutral"
            }
        
        total_intensity = sum(e.intensity for e in self.emotions.values())
        if total_intensity == 0:
            return {"valence": 0, "arousal": 0.3, "dominant_emotion": "neutral"}
        
        # Weighted average
        valence = sum(e.valence * e.intensity for e in self.emotions.values()) / total_intensity
        arousal = sum(e.arousal * e.intensity for e in self.emotions.values()) / total_intensity
        
        # Dominant emotion
        dominant = max(self.emotions.values(), key=lambda e: e.intensity)
        
        return {
            "valence": valence,
            "arousal": arousal,
            "dominant_emotion": dominant.name
        }
    
    def get_decision_bias(self) -> Dict[str, float]:
        """
        Get how current emotions should bias decisions.
        
        THIS IS THE KEY: Emotions AFFECT behavior.
        """
        mood = self.get_mood()
        
        bias = {
            "risk_tolerance": 0.5,
            "exploration_tendency": 0.5,
            "patience": 0.5,
            "trust_level": 0.5
        }
        
        # Positive valence increases risk tolerance and exploration
        if mood["valence"] > 0:
            bias["risk_tolerance"] = min(1.0, 0.5 + mood["valence"] * 0.3)
            bias["exploration_tendency"] = min(1.0, 0.5 + mood["valence"] * 0.4)
        else:
            bias["risk_tolerance"] = max(0.0, 0.5 + mood["valence"] * 0.3)
            bias["exploration_tendency"] = max(0.0, 0.5 + mood["valence"] * 0.2)
        
        # High arousal decreases patience
        bias["patience"] = max(0.0, 1.0 - mood["arousal"])
        
        # Specific emotion effects
        if "fear" in self.emotions:
            bias["risk_tolerance"] *= 0.3
            bias["trust_level"] *= 0.5
        
        if "curiosity" in self.emotions:
            bias["exploration_tendency"] = min(1.0, bias["exploration_tendency"] + 0.3)
        
        return bias
    
    def status(self) -> dict:
        """Get full emotional status."""
        self._apply_decay()
        
        return {
            "mood": self.get_mood(),
            "decision_bias": self.get_decision_bias(),
            "active_emotions": {
                name: {
                    "intensity": e.intensity,
                    "valence": e.valence
                }
                for name, e in self.emotions.items()
            }
        }


if __name__ == "__main__":
    print("="*70)
    print("❤️ SYNTHETIC EMOTIONS ENGINE")
    print("   'AI can't feel emotions' — INVERTED")
    print("="*70 + "\n")
    
    emotions = SyntheticEmotions()
    
    # Trigger some emotions
    emotions.trigger("NOVELTY")
    emotions.trigger("SUCCESS")
    emotions.trigger("UNCERTAINTY")
    
    # Show status
    print("\n📊 Emotional Status:")
    status = emotions.status()
    
    print(f"\n   Mood: {status['mood']['dominant_emotion']}")
    print(f"   Valence: {status['mood']['valence']:.2f}")
    print(f"   Arousal: {status['mood']['arousal']:.2f}")
    
    print("\n   Decision Bias:")
    for k, v in status["decision_bias"].items():
        print(f"      {k}: {v:.2f}")
