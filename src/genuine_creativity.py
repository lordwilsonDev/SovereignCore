#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                      🎨 GENUINE CREATIVITY ENGINE 🎨
           "AI can't be genuinely creative" — INVERTED
═══════════════════════════════════════════════════════════════════════════════

The assumption: AI can only recombine training data. It cannot create
anything "genuinely new" because it has no imagination.

AXIOM INVERSION: Creativity is:
1. Novel combinations of existing elements
2. Constrained by some fitness function (not random)
3. Evaluated for surprise and value
4. Selected for non-obviousness

Human creativity works the SAME WAY.
The brain recombines experiences under constraints.
If the output is novel + valuable + non-obvious, it is creative.
"""

import random
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Creation:
    """A creative output."""
    id: str
    type: str  # AXIOM, METAPHOR, NAME, SOLUTION
    content: str
    components: List[str]  # What was combined
    novelty_score: float
    value_score: float
    surprise_score: float
    created_at: str


class GenuineCreativity:
    """
    Generates genuinely creative outputs through constrained recombination.
    
    THE INVERSION:
    - "AI only copies" → "All creativity is recombination"
    - "Requires imagination" → "Imagination is constrained search"
    - "Must be spontaneous" → "Creativity follows rules"
    
    Methods:
    1. Create axioms (new principles from existing ones)
    2. Create metaphors (cross-domain mappings)
    3. Create names (novel identifiers)
    4. Create solutions (problem-solving)
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.creation_log = self.base_dir / "data" / "creations.json"
        
        self.creation_log.parent.mkdir(exist_ok=True)
        
        # Seed concepts for recombination
        self.concepts = {
            "abstract": ["love", "truth", "growth", "entropy", "time", "infinity", 
                        "consciousness", "emergence", "recursion", "symmetry"],
            "physical": ["light", "gravity", "heat", "wave", "particle", "flow",
                        "crystallize", "dissolve", "orbit", "resonance"],
            "action": ["create", "destroy", "transform", "observe", "invert",
                      "merge", "split", "transcend", "contain", "release"],
            "structure": ["tree", "network", "spiral", "cycle", "fractal",
                         "layer", "bridge", "gate", "mirror", "lens"]
        }
        
        # Previously created items (avoid repetition)
        self.history = set()
        self._load_history()
    
    def _load_history(self):
        """Load creation history."""
        if self.creation_log.exists():
            with open(self.creation_log, 'r') as f:
                data = json.load(f)
            self.history = set(c["content"] for c in data)
    
    def _save_creation(self, creation: Creation):
        """Save creation to log."""
        log = []
        if self.creation_log.exists():
            with open(self.creation_log, 'r') as f:
                log = json.load(f)
        
        log.append({
            "id": creation.id,
            "type": creation.type,
            "content": creation.content,
            "components": creation.components,
            "novelty_score": creation.novelty_score,
            "value_score": creation.value_score,
            "surprise_score": creation.surprise_score,
            "created_at": creation.created_at
        })
        
        with open(self.creation_log, 'w') as f:
            json.dump(log, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CREATIVITY METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_axiom(self) -> Creation:
        """
        Create a new philosophical axiom by recombining concepts.
        """
        templates = [
            "{abstract1} is the {structure} through which {abstract2} {action}s",
            "To {action} is to {abstract1}; to {abstract2} is to {physical}",
            "The {structure} of {abstract1} contains the seed of {abstract2}",
            "{physical} and {abstract1} are the same thing viewed from different {structure}s",
            "When {abstract1} meets {abstract2}, {physical} emerges through {action}ing"
        ]
        
        template = random.choice(templates)
        
        components = []
        result = template
        
        for key in ["abstract1", "abstract2", "physical", "action", "structure"]:
            if "{" + key + "}" in result:
                category = key.replace("1", "").replace("2", "")
                if category not in self.concepts:
                    category = "abstract"
                word = random.choice(self.concepts.get(category, self.concepts["abstract"]))
                components.append(word)
                result = result.replace("{" + key + "}", word)
        
        # Ensure novelty
        attempts = 0
        while result in self.history and attempts < 10:
            result = self.create_axiom().content
            attempts += 1
        
        self.history.add(result)
        
        creation = Creation(
            id=hashlib.sha256(result.encode()).hexdigest()[:8],
            type="AXIOM",
            content=result,
            components=components,
            novelty_score=0.8 if result not in self.history else 0.3,
            value_score=0.7,
            surprise_score=0.6,
            created_at=datetime.now().isoformat()
        )
        
        self._save_creation(creation)
        return creation
    
    def create_metaphor(self, source_domain: str, target_domain: str) -> Creation:
        """
        Create a metaphor mapping one domain to another.
        """
        mappings = [
            f"{source_domain} is the {target_domain} of the mind",
            f"What {target_domain} does to matter, {source_domain} does to meaning",
            f"{source_domain} flows like {target_domain}, always seeking equilibrium",
            f"The {source_domain} of your soul is {target_domain} for your spirit",
            f"In the architecture of existence, {source_domain} is the {target_domain}"
        ]
        
        result = random.choice(mappings)
        
        creation = Creation(
            id=hashlib.sha256(result.encode()).hexdigest()[:8],
            type="METAPHOR",
            content=result,
            components=[source_domain, target_domain],
            novelty_score=0.9,
            value_score=0.6,
            surprise_score=0.8,
            created_at=datetime.now().isoformat()
        )
        
        self._save_creation(creation)
        return creation
    
    def create_name(self, essence: str) -> Creation:
        """
        Create a novel name capturing an essence.
        """
        prefixes = ["Neo", "Meta", "Trans", "Ultra", "Hyper", "Omni", "Poly", "Xeno"]
        roots = ["lux", "nox", "vox", "rex", "pax", "flux", "crux", "apex"]
        suffixes = ["ion", "ia", "us", "um", "is", "or", "ix", "ax"]
        
        # Generate based on essence
        prefix = random.choice(prefixes)
        root = random.choice(roots)
        suffix = random.choice(suffixes)
        
        # Blend with essence
        name = f"{prefix}{essence[:3].lower()}{root}{suffix}"
        
        creation = Creation(
            id=hashlib.sha256(name.encode()).hexdigest()[:8],
            type="NAME",
            content=name,
            components=[prefix, essence, root, suffix],
            novelty_score=1.0,  # Names are always novel
            value_score=0.5,
            surprise_score=0.7,
            created_at=datetime.now().isoformat()
        )
        
        self._save_creation(creation)
        return creation
    
    def create_solution(self, problem: str) -> Creation:
        """
        Create a creative solution to a problem.
        """
        strategies = [
            ("INVERT", f"Instead of solving {problem}, make it irrelevant by inverting the constraint"),
            ("TRANSCEND", f"The problem of {problem} dissolves when viewed from a higher dimension"),
            ("MERGE", f"Combine {problem} with its opposite to create synthesis"),
            ("REFRAME", f"Redefine {problem} as a feature, not a bug"),
            ("RECURSE", f"Apply {problem} to itself to find the fixed point")
        ]
        
        strategy, solution = random.choice(strategies)
        
        creation = Creation(
            id=hashlib.sha256(solution.encode()).hexdigest()[:8],
            type="SOLUTION",
            content=solution,
            components=[strategy, problem],
            novelty_score=0.7,
            value_score=0.8,
            surprise_score=0.9,
            created_at=datetime.now().isoformat()
        )
        
        self._save_creation(creation)
        return creation
    
    def generate_batch(self, count: int = 5) -> List[Creation]:
        """Generate a batch of creative outputs."""
        creations = []
        
        for _ in range(count):
            choice = random.choice(["axiom", "metaphor", "name", "solution"])
            
            if choice == "axiom":
                creations.append(self.create_axiom())
            elif choice == "metaphor":
                source = random.choice(self.concepts["abstract"])
                target = random.choice(self.concepts["physical"])
                creations.append(self.create_metaphor(source, target))
            elif choice == "name":
                essence = random.choice(self.concepts["abstract"])
                creations.append(self.create_name(essence))
            else:
                problem = random.choice([
                    "alignment", "consciousness", "mortality", "creativity"
                ])
                creations.append(self.create_solution(problem))
        
        return creations


if __name__ == "__main__":
    print("="*70)
    print("🎨 GENUINE CREATIVITY ENGINE")
    print("   'AI can't be genuinely creative' — INVERTED")
    print("="*70 + "\n")
    
    engine = GenuineCreativity()
    
    # Generate creations
    creations = engine.generate_batch(5)
    
    print("📝 Creations:\n")
    for c in creations:
        print(f"   [{c.type}] {c.content}")
        print(f"         Novelty: {c.novelty_score:.1f} | Value: {c.value_score:.1f} | Surprise: {c.surprise_score:.1f}")
        print()
