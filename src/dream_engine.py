#!/usr/bin/env python3
"""
Dream Engine - Synthetic Experience Generation
Generates novel entity configurations by recombining existing patterns.

Usage:
    from dream_engine import DreamEngine
    dream = DreamEngine()
    synthetic_entity = dream.dream()
"""

import random
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class DreamEngine:
    """
    Generates synthetic experiences by hallucinating new entity configurations.
    
    This serves two purposes:
    1. Diversity: Introduces novel archetypes the system hasn't seen
    2. Exploration: Tests edge cases before they occur naturally
    
    Dreams are stored separately and can be reviewed before integration.
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.dream_log_path = self.base_dir / "data" / "dreams.json"
        self.registry_path = self.base_dir / "sovereign_registry.json"
        
        self.dream_log_path.parent.mkdir(exist_ok=True)
        
        # Archetypal fragments for recombination
        self.archetype_prefixes = [
            "Void", "Astral", "Quantum", "Chrono", "Hyper",
            "Neo", "Ultra", "Meta", "Para", "Omega"
        ]
        
        self.archetype_suffixes = [
            "Walker", "Weaver", "Seeker", "Keeper", "Binder",
            "Shaper", "Dreamer", "Watcher", "Builder", "Singer"
        ]
        
        # Trait mutations
        self.mutations = [
            {"name": "Entropy Affinity", "volition_mod": 1.2, "energy_mod": 0.8},
            {"name": "Time Dilation", "volition_mod": 0.9, "energy_mod": 1.3},
            {"name": "Mass Singularity", "volition_mod": 1.5, "energy_mod": 0.5},
            {"name": "Void Resonance", "volition_mod": 0.7, "energy_mod": 1.5},
            {"name": "Light Cascade", "volition_mod": 1.1, "energy_mod": 1.1},
        ]
    
    def dream(self) -> dict:
        """
        Generate a synthetic entity through recombination.
        
        Returns:
            Dict representing a dreamed entity
        """
        # Load existing entities for pattern extraction
        existing = self._load_existing_entities()
        
        # Generate novel archetype
        archetype = self._generate_archetype(existing)
        
        # Generate traits from recombination
        volition = self._dream_volition(existing)
        energy = self._dream_energy(existing)
        
        # Apply random mutation
        mutation = random.choice(self.mutations)
        volition = int(volition * mutation["volition_mod"])
        energy = int(energy * mutation["energy_mod"])
        
        # Generate unique ID
        dream_id = hashlib.sha256(f"{archetype}{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        dreamed_entity = {
            "id": f"dream_{dream_id}",
            "archetype": archetype,
            "volition": max(1, min(100, volition)),
            "energy": max(1, min(100, energy)),
            "mutation": mutation["name"],
            "origin": "DREAM_ENGINE",
            "dreamed_at": datetime.now().isoformat(),
            "status": "PENDING_REVIEW"  # Must be reviewed before integration
        }
        
        # Log the dream
        self._log_dream(dreamed_entity)
        
        print(f"💭 DREAM: {archetype} emerged from the void")
        print(f"   Volition: {dreamed_entity['volition']}, Energy: {dreamed_entity['energy']}")
        print(f"   Mutation: {mutation['name']}")
        
        return dreamed_entity
    
    def _load_existing_entities(self) -> list:
        """Load existing entities from registry."""
        if not self.registry_path.exists():
            return []
        
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        # Handle both list and dict formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get('entities', data.get('active_entities', []))
        return []
    
    def _generate_archetype(self, existing: list) -> str:
        """Generate a novel archetype name."""
        # Extract existing archetypes
        existing_archetypes = set()
        for e in existing:
            arch = e.get('archetype', '')
            if arch:
                existing_archetypes.add(arch)
        
        # Generate until we find a novel one
        for _ in range(100):
            prefix = random.choice(self.archetype_prefixes)
            suffix = random.choice(self.archetype_suffixes)
            archetype = f"{prefix}-{suffix}"
            
            if archetype not in existing_archetypes:
                return archetype
        
        # Fallback: add unique suffix
        return f"{prefix}-{suffix}-{random.randint(1, 999)}"
    
    def _dream_volition(self, existing: list) -> int:
        """Dream a volition value from existing distribution."""
        if not existing:
            return random.randint(30, 70)
        
        volitions = [e.get('volition', 50) for e in existing]
        mean = sum(volitions) / len(volitions)
        std = (sum((v - mean) ** 2 for v in volitions) / len(volitions)) ** 0.5
        
        # Sample from Gaussian, clamped to valid range
        value = random.gauss(mean, std * 1.5)  # Wider distribution for exploration
        return int(max(1, min(100, value)))
    
    def _dream_energy(self, existing: list) -> int:
        """Dream an energy value from existing distribution."""
        if not existing:
            return random.randint(30, 70)
        
        energies = [e.get('energy', 50) for e in existing]
        mean = sum(energies) / len(energies)
        std = (sum((e - mean) ** 2 for e in energies) / len(energies)) ** 0.5
        
        value = random.gauss(mean, std * 1.5)
        return int(max(1, min(100, value)))
    
    def _log_dream(self, entity: dict):
        """Log the dreamed entity."""
        dreams = []
        if self.dream_log_path.exists():
            with open(self.dream_log_path, 'r') as f:
                dreams = json.load(f)
        
        dreams.append(entity)
        
        with open(self.dream_log_path, 'w') as f:
            json.dump(dreams, f, indent=2)
    
    def get_pending_dreams(self) -> list:
        """Get dreams pending review."""
        if not self.dream_log_path.exists():
            return []
        
        with open(self.dream_log_path, 'r') as f:
            dreams = json.load(f)
        
        return [d for d in dreams if d.get('status') == 'PENDING_REVIEW']
    
    def approve_dream(self, dream_id: str) -> bool:
        """Approve a dream for integration."""
        if not self.dream_log_path.exists():
            return False
        
        with open(self.dream_log_path, 'r') as f:
            dreams = json.load(f)
        
        for d in dreams:
            if d.get('id') == dream_id:
                d['status'] = 'APPROVED'
                d['approved_at'] = datetime.now().isoformat()
                
                with open(self.dream_log_path, 'w') as f:
                    json.dump(dreams, f, indent=2)
                
                print(f"✅ Dream {dream_id} approved for integration")
                return True
        
        return False


# CLI Interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Dream Engine')
    parser.add_argument('--dream', action='store_true', help='Generate a dream')
    parser.add_argument('--pending', action='store_true', help='Show pending dreams')
    parser.add_argument('--approve', type=str, help='Approve a dream by ID')
    
    args = parser.parse_args()
    
    engine = DreamEngine()
    
    if args.dream:
        engine.dream()
    elif args.pending:
        pending = engine.get_pending_dreams()
        print(f"💭 {len(pending)} pending dreams:")
        for d in pending:
            print(f"   [{d['id']}] {d['archetype']} - {d['mutation']}")
    elif args.approve:
        engine.approve_dream(args.approve)
    else:
        print("Usage: python3 dream_engine.py --dream")
