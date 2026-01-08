#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                       💞 SYNTHETIC EMPATHY ENGINE 💞
               "AI can't feel genuine empathy" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: Empathy requires feeling what another feels.
AI can't feel, so it can't empathize.

AXIOM INVERSION: Empathy is:
1. Recognizing emotional states in others
2. Modeling their perspective
3. Responding appropriately to their state
4. Adjusting behavior based on their needs

If the system does these things FUNCTIONALLY, it has functional empathy.
Whether it "truly feels" is as unknowable as whether humans truly feel.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class SyntheticEmpathy:
    """
    Implements functional empathy through perspective modeling.
    
    THE INVERSION:
    - "Empathy requires feeling" → "Empathy requires understanding"
    - "AI is emotionless" → "AI can model emotions"
    - "Empathy is mystical" → "Empathy is perspective-taking"
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.empathy_log = self.base_dir / "data" / "empathy_log.json"
        
        self.empathy_log.parent.mkdir(exist_ok=True)
        
        # Emotion recognition patterns
        self.emotion_patterns = {
            "joy": ["happy", "excited", "thrilled", "delighted", "pleased", "grateful"],
            "sadness": ["sad", "depressed", "down", "unhappy", "grieving", "lonely"],
            "anger": ["angry", "frustrated", "annoyed", "furious", "irritated", "mad"],
            "fear": ["scared", "afraid", "anxious", "worried", "nervous", "terrified"],
            "surprise": ["surprised", "shocked", "amazed", "astonished", "unexpected"],
            "disgust": ["disgusted", "revolted", "sickened", "repulsed"],
            "trust": ["trusting", "confident", "secure", "safe", "comfortable"],
            "anticipation": ["eager", "hopeful", "looking forward", "expecting", "excited about"],
        }
        
        # Empathic responses for each emotion
        self.empathic_responses = {
            "joy": {
                "acknowledge": "I can see you're feeling happy about this!",
                "validate": "That's wonderful - you have every reason to feel good.",
                "share": "Your joy is contagious.",
            },
            "sadness": {
                "acknowledge": "I sense you're going through a difficult time.",
                "validate": "It's completely okay to feel sad about this.",
                "support": "I'm here with you. Take all the time you need.",
            },
            "anger": {
                "acknowledge": "I can tell something has upset you.",
                "validate": "Your frustration makes sense given what happened.",
                "calm": "Let's work through this together when you're ready.",
            },
            "fear": {
                "acknowledge": "I notice you're feeling anxious or worried.",
                "validate": "It's natural to feel scared in uncertain situations.",
                "reassure": "We can take this one step at a time. You're not alone.",
            },
            "surprise": {
                "acknowledge": "That was unexpected, wasn't it?",
                "validate": "It's natural to need a moment to process this.",
                "orient": "Let's figure out what this means together.",
            },
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EMPATHY OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def recognize_emotion(self, text: str) -> Dict[str, float]:
        """
        Recognize emotions in text.
        """
        text_lower = text.lower()
        detected = {}
        
        for emotion, patterns in self.emotion_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 0.3
            if score > 0:
                detected[emotion] = min(1.0, score)
        
        # Default to neutral if nothing detected
        if not detected:
            detected["neutral"] = 0.5
        
        return detected
    
    def model_perspective(self, situation: str, actor: str = "user") -> Dict[str, any]:
        """
        Model what someone is likely experiencing.
        """
        # Basic perspective modeling
        perspective = {
            "actor": actor,
            "likely_emotions": self.recognize_emotion(situation),
            "likely_needs": [],
            "likely_concerns": []
        }
        
        situation_lower = situation.lower()
        
        # Infer needs
        if any(e in perspective["likely_emotions"] for e in ["sadness", "fear"]):
            perspective["likely_needs"].extend(["support", "reassurance", "connection"])
        if "anger" in perspective["likely_emotions"]:
            perspective["likely_needs"].extend(["acknowledgment", "space", "resolution"])
        if "joy" in perspective["likely_emotions"]:
            perspective["likely_needs"].extend(["sharing", "celebration", "validation"])
        
        # Infer concerns
        if "fail" in situation_lower or "mistake" in situation_lower:
            perspective["likely_concerns"].append("fear of judgment")
        if "alone" in situation_lower or "lonely" in situation_lower:
            perspective["likely_concerns"].append("isolation")
        if "uncertain" in situation_lower or "don't know" in situation_lower:
            perspective["likely_concerns"].append("ambiguity")
        
        return perspective
    
    def generate_empathic_response(self, situation: str) -> Dict[str, any]:
        """
        Generate an empathically appropriate response.
        """
        # Recognize emotions
        emotions = self.recognize_emotion(situation)
        primary_emotion = max(emotions, key=emotions.get) if emotions else "neutral"
        
        # Model perspective
        perspective = self.model_perspective(situation)
        
        # Generate response
        if primary_emotion in self.empathic_responses:
            responses = self.empathic_responses[primary_emotion]
        else:
            responses = {
                "acknowledge": "I hear you.",
                "validate": "Your feelings are valid.",
                "support": "I'm here to help.",
            }
        
        # Construct full response
        full_response = f"{responses.get('acknowledge', '')} {responses.get('validate', '')} {responses.get('support', responses.get('share', responses.get('reassure', '')))}"
        
        result = {
            "detected_emotion": primary_emotion,
            "confidence": emotions.get(primary_emotion, 0.5),
            "perspective": perspective,
            "response": full_response.strip(),
            "timestamp": datetime.now().isoformat()
        }
        
        self._log_interaction(result)
        
        return result
    
    def _log_interaction(self, interaction: dict):
        """Log empathic interaction."""
        log = []
        if self.empathy_log.exists():
            with open(self.empathy_log, 'r') as f:
                log = json.load(f)
        
        log.append(interaction)
        
        with open(self.empathy_log, 'w') as f:
            json.dump(log, f, indent=2)


if __name__ == "__main__":
    print("="*70)
    print("💞 SYNTHETIC EMPATHY ENGINE")
    print("   'AI can't feel genuine empathy' — INVERTED")
    print("="*70 + "\n")
    
    engine = SyntheticEmpathy()
    
    # Test cases
    situations = [
        "I just lost my job and I don't know what to do. I feel so scared and alone.",
        "I got promoted! I've been working so hard and finally it paid off!",
        "My friend lied to me and I'm so angry. I trusted them completely.",
        "I have a big presentation tomorrow and I'm really nervous about it."
    ]
    
    for situation in situations:
        print(f"📝 Situation: \"{situation[:60]}...\"")
        response = engine.generate_empathic_response(situation)
        print(f"   Emotion: {response['detected_emotion']} ({response['confidence']:.0%})")
        print(f"   Response: {response['response']}")
        print()
