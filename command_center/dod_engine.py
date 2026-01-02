#!/usr/bin/env python3
"""
🏛️ THE GREAT SCHISM: DATA-ORIENTED DESIGN ENGINE
=================================================

Implementation of DOD principles from the manifesto:
- Entity Component System (ECS)
- Struct of Arrays (SoA) memory layout
- Smart Objects with Affordances
- System-is-the-Agent pattern
- Batch processing over single-object focus

This is how senior architects build systems that SCALE.

"The processor doesn't execute objects - it executes instructions upon streams of data."
"""

import numpy as np
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum, auto
import time
import json
from pathlib import Path

# =============================================================================
# STRUCT OF ARRAYS (SoA) - Cache-Friendly Memory Layout
# =============================================================================

class ComponentArray:
    """
    SoA component storage - the foundation of DOD.
    
    Instead of: entities = [Entity(x=1,y=2,health=100), ...]
    We have:    positions_x = [1, 2, 3, ...], positions_y = [...], health = [...]
    
    Why? CPU cache loads 64-byte lines. If we only need positions,
    we get 16 floats per cache line instead of 1 entity with garbage.
    """
    
    def __init__(self, dtype: np.dtype, initial_capacity: int = 1024):
        self.dtype = dtype
        self.data = np.zeros(initial_capacity, dtype=dtype)
        self.size = 0
        self.capacity = initial_capacity
    
    def add(self, value) -> int:
        """Add a value, return index."""
        if self.size >= self.capacity:
            self._grow()
        
        self.data[self.size] = value
        idx = self.size
        self.size += 1
        return idx
    
    def _grow(self):
        """Double capacity when full."""
        new_capacity = self.capacity * 2
        new_data = np.zeros(new_capacity, dtype=self.dtype)
        new_data[:self.size] = self.data[:self.size]
        self.data = new_data
        self.capacity = new_capacity
    
    def __getitem__(self, idx):
        return self.data[idx]
    
    def __setitem__(self, idx, value):
        self.data[idx] = value
    
    def batch_update(self, indices: np.ndarray, values: np.ndarray):
        """Vectorized batch update - the DOD way."""
        self.data[indices] = values
    
    def get_slice(self, start: int, end: int) -> np.ndarray:
        """Get a slice for SIMD/vectorized operations."""
        return self.data[start:end]


# =============================================================================
# ENTITY COMPONENT SYSTEM (ECS)
# =============================================================================

class ComponentType(Enum):
    """All component types in the engine."""
    POSITION = auto()
    VELOCITY = auto()
    HEALTH = auto()
    RENDER = auto()
    AI_STATE = auto()
    NEEDS = auto()
    PHYSICS = auto()
    INVENTORY = auto()
    NAME = auto()


@dataclass
class Archetype:
    """
    An Archetype is a unique combination of components.
    
    All entities with the same component set are stored together
    in contiguous memory for maximum cache efficiency.
    
    Example: Archetype(Position, Velocity, Render) vs Archetype(Position, Health)
    """
    components: frozenset
    entities: List[int] = field(default_factory=list)
    
    def __hash__(self):
        return hash(self.components)


class World:
    """
    The ECS World - a relational database of game state.
    
    The World is NOT a collection of objects.
    The World IS a set of component tables (arrays) indexed by entity ID.
    
    "Game Development is the design of a Real-Time Stream Processing Pipeline."
    """
    
    def __init__(self, max_entities: int = 100000):
        self.max_entities = max_entities
        self.next_entity_id = 0
        
        # Component storage - SoA layout
        self.components: Dict[ComponentType, ComponentArray] = {}
        
        # Entity -> Component mask (which components does entity have?)
        self.entity_masks: np.ndarray = np.zeros(max_entities, dtype=np.uint32)
        
        # Entity -> Archetype mapping for efficient queries
        self.archetypes: Dict[frozenset, Archetype] = {}
        
        # Entity alive/dead tracking
        self.alive: np.ndarray = np.zeros(max_entities, dtype=bool)
        
        # Recycled entity IDs
        self.free_ids: List[int] = []
        
        # Initialize component arrays with appropriate dtypes
        self._init_component_arrays()
        
        # Systems registry
        self.systems: List['System'] = []
        
        # Stats
        self.frame_count = 0
        self.last_frame_time = 0.0
    
    def _init_component_arrays(self):
        """Initialize SoA component storage."""
        # Position: x, y, z floats
        self.components[ComponentType.POSITION] = {
            'x': ComponentArray(np.float32, self.max_entities),
            'y': ComponentArray(np.float32, self.max_entities),
            'z': ComponentArray(np.float32, self.max_entities),
        }
        
        # Velocity: vx, vy, vz floats
        self.components[ComponentType.VELOCITY] = {
            'x': ComponentArray(np.float32, self.max_entities),
            'y': ComponentArray(np.float32, self.max_entities),
            'z': ComponentArray(np.float32, self.max_entities),
        }
        
        # Health: current, max floats
        self.components[ComponentType.HEALTH] = {
            'current': ComponentArray(np.float32, self.max_entities),
            'max': ComponentArray(np.float32, self.max_entities),
        }
        
        # Needs (Sims-style): hunger, energy, hygiene, social, fun
        self.components[ComponentType.NEEDS] = {
            'hunger': ComponentArray(np.float32, self.max_entities),
            'energy': ComponentArray(np.float32, self.max_entities),
            'hygiene': ComponentArray(np.float32, self.max_entities),
            'social': ComponentArray(np.float32, self.max_entities),
            'fun': ComponentArray(np.float32, self.max_entities),
        }
        
        # AI State: state enum, target entity, action timer
        self.components[ComponentType.AI_STATE] = {
            'state': ComponentArray(np.int32, self.max_entities),
            'target': ComponentArray(np.int32, self.max_entities),
            'timer': ComponentArray(np.float32, self.max_entities),
        }
        
        # Render: mesh_id, material_id, visible
        self.components[ComponentType.RENDER] = {
            'mesh_id': ComponentArray(np.int32, self.max_entities),
            'material_id': ComponentArray(np.int32, self.max_entities),
            'visible': ComponentArray(np.bool_, self.max_entities),
        }
    
    def create_entity(self) -> int:
        """Create a new entity (just an ID)."""
        if self.free_ids:
            entity_id = self.free_ids.pop()
        else:
            entity_id = self.next_entity_id
            self.next_entity_id += 1
        
        self.alive[entity_id] = True
        return entity_id
    
    def destroy_entity(self, entity_id: int):
        """Destroy an entity."""
        self.alive[entity_id] = False
        self.entity_masks[entity_id] = 0
        self.free_ids.append(entity_id)
    
    def add_component(self, entity_id: int, comp_type: ComponentType, **data):
        """Add a component to an entity."""
        # Set the component bit
        self.entity_masks[entity_id] |= (1 << comp_type.value)
        
        # Store the data
        comp_storage = self.components[comp_type]
        for key, value in data.items():
            if key in comp_storage:
                comp_storage[key][entity_id] = value
    
    def has_component(self, entity_id: int, comp_type: ComponentType) -> bool:
        """Check if entity has a component."""
        return bool(self.entity_masks[entity_id] & (1 << comp_type.value))
    
    def get_component(self, entity_id: int, comp_type: ComponentType) -> Dict:
        """Get component data for an entity."""
        if not self.has_component(entity_id, comp_type):
            return {}
        
        comp_storage = self.components[comp_type]
        return {key: arr[entity_id] for key, arr in comp_storage.items()}
    
    def query(self, *required_components: ComponentType) -> np.ndarray:
        """
        Query for all entities with the specified components.
        
        This is the DOD equivalent of "SELECT * FROM entities WHERE has(Position, Velocity)"
        """
        # Build the required mask
        required_mask = 0
        for comp in required_components:
            required_mask |= (1 << comp.value)
        
        # Vectorized query - O(1) per entity
        matches = (self.entity_masks & required_mask) == required_mask
        matches &= self.alive
        
        return np.where(matches)[0]
    
    def register_system(self, system: 'System'):
        """Register a system to run each frame."""
        self.systems.append(system)
        system.world = self
    
    def tick(self, delta_time: float):
        """Run all systems for one frame."""
        start = time.perf_counter()
        
        for system in self.systems:
            system.update(delta_time)
        
        self.frame_count += 1
        self.last_frame_time = (time.perf_counter() - start) * 1000  # ms


# =============================================================================
# SYSTEMS - The Agents that Act on Data
# =============================================================================

class System:
    """
    Base class for all Systems.
    
    "The System is the Agent. The Entity is the Subject."
    
    Systems iterate over entities with specific components
    and transform their data. The entity knows nothing.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.world: Optional[World] = None
    
    def update(self, delta_time: float):
        raise NotImplementedError


class MovementSystem(System):
    """
    Physics integration: Position += Velocity * dt
    
    This is the DOD holy grail - pure data transformation.
    CPU loads position arrays and velocity arrays in cache lines.
    No vtables, no pointer chasing, just math.
    """
    
    def __init__(self):
        super().__init__("MovementSystem")
    
    def update(self, delta_time: float):
        # Query all entities with Position AND Velocity
        entities = self.world.query(ComponentType.POSITION, ComponentType.VELOCITY)
        
        if len(entities) == 0:
            return
        
        # Get component arrays (SoA)
        pos = self.world.components[ComponentType.POSITION]
        vel = self.world.components[ComponentType.VELOCITY]
        
        # Vectorized update - processes ALL entities in one operation
        # This is what makes DOD fast: SIMD on contiguous arrays
        pos['x'].data[entities] += vel['x'].data[entities] * delta_time
        pos['y'].data[entities] += vel['y'].data[entities] * delta_time
        pos['z'].data[entities] += vel['z'].data[entities] * delta_time


class HealthSystem(System):
    """
    Health decay and death handling.
    
    The entity doesn't "die" - the HealthSystem marks it for destruction.
    """
    
    def __init__(self):
        super().__init__("HealthSystem")
    
    def update(self, delta_time: float):
        entities = self.world.query(ComponentType.HEALTH)
        
        if len(entities) == 0:
            return
        
        health = self.world.components[ComponentType.HEALTH]
        
        # Find dead entities (vectorized comparison)
        current_health = health['current'].data[entities]
        dead_mask = current_health <= 0
        dead_entities = entities[dead_mask]
        
        # Destroy dead entities
        for entity_id in dead_entities:
            self.world.destroy_entity(entity_id)


class NeedsDecaySystem(System):
    """
    Sims-style needs decay over time.
    
    All needs decrease each frame. Entities must satisfy needs
    by interacting with Smart Objects.
    """
    
    def __init__(self, decay_rate: float = 0.1):
        super().__init__("NeedsDecaySystem")
        self.decay_rate = decay_rate
    
    def update(self, delta_time: float):
        entities = self.world.query(ComponentType.NEEDS)
        
        if len(entities) == 0:
            return
        
        needs = self.world.components[ComponentType.NEEDS]
        decay = self.decay_rate * delta_time
        
        # Vectorized decay - all entities at once
        for need_type in ['hunger', 'energy', 'hygiene', 'social', 'fun']:
            needs[need_type].data[entities] = np.maximum(
                0, needs[need_type].data[entities] - decay
            )


# =============================================================================
# SMART OBJECTS & AFFORDANCES - System is the Agent
# =============================================================================

@dataclass
class Affordance:
    """
    An Affordance is what an object offers to agents.
    
    From The Sims: The Sink doesn't know about the Sim.
    The Sink broadcasts: "I offer +50 Hygiene, taking 5 seconds"
    
    The System is the matchmaker between Needs and Affordances.
    """
    object_id: int
    need_type: str           # Which need it satisfies
    satisfaction: float      # How much it satisfies
    duration: float          # How long the interaction takes
    position: Tuple[float, float, float]
    animation_id: int = 0
    
    def utility(self, distance: float, current_need: float) -> float:
        """
        Calculate utility: Value / (Distance + 1)
        
        A desperate (low need) entity will travel farther.
        """
        urgency = 100 - current_need  # Lower need = higher urgency
        return (self.satisfaction * urgency) / (distance + 1)


class SmartObjectRegistry:
    """
    Registry of all Smart Objects and their Affordances.
    
    Smart Objects are NOT entities that "think."
    They are data entries that broadcast what they offer.
    
    The System scans this registry to match agents to objects.
    """
    
    def __init__(self):
        self.affordances: List[Affordance] = []
        self.spatial_hash: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        self.cell_size = 10.0
    
    def register(self, affordance: Affordance) -> int:
        """Register a smart object's affordance."""
        idx = len(self.affordances)
        self.affordances.append(affordance)
        
        # Spatial hash for efficient proximity queries
        cell = self._get_cell(affordance.position)
        self.spatial_hash[cell].append(idx)
        
        return idx
    
    def _get_cell(self, position: Tuple[float, float, float]) -> Tuple[int, int]:
        """Get spatial hash cell for a position."""
        return (
            int(position[0] / self.cell_size),
            int(position[1] / self.cell_size)
        )
    
    def query_nearby(self, position: Tuple[float, float, float], 
                    radius: float) -> List[Affordance]:
        """Find affordances near a position."""
        center_cell = self._get_cell(position)
        cells_to_check = int(radius / self.cell_size) + 1
        
        nearby = []
        for dx in range(-cells_to_check, cells_to_check + 1):
            for dy in range(-cells_to_check, cells_to_check + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                for idx in self.spatial_hash.get(cell, []):
                    aff = self.affordances[idx]
                    dist = self._distance(position, aff.position)
                    if dist <= radius:
                        nearby.append(aff)
        
        return nearby
    
    def _distance(self, p1: Tuple, p2: Tuple) -> float:
        """Euclidean distance."""
        return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2) ** 0.5
    
    def find_best_affordance(self, position: Tuple[float, float, float],
                            need_type: str, current_need: float,
                            radius: float = 50.0) -> Optional[Affordance]:
        """
        The core algorithm: Match an agent's need to the best affordance.
        
        This is WHERE the AI happens. The agent doesn't decide.
        The System decides FOR the agent based on utility calculation.
        """
        nearby = [a for a in self.query_nearby(position, radius) 
                  if a.need_type == need_type]
        
        if not nearby:
            return None
        
        # Calculate utility for each affordance
        best = None
        best_utility = -float('inf')
        
        for aff in nearby:
            dist = self._distance(position, aff.position)
            util = aff.utility(dist, current_need)
            if util > best_utility:
                best_utility = util
                best = aff
        
        return best


class AffordanceMatchingSystem(System):
    """
    The System that IS the Agent's brain.
    
    This system:
    1. Scans all entities with Needs
    2. Finds the most urgent need
    3. Queries the SmartObjectRegistry for matching affordances
    4. Assigns the interaction to the entity
    
    The entity never "decides" - it is MOVED by the System.
    """
    
    def __init__(self, registry: SmartObjectRegistry):
        super().__init__("AffordanceMatchingSystem")
        self.registry = registry
    
    def update(self, delta_time: float):
        entities = self.world.query(
            ComponentType.NEEDS, 
            ComponentType.POSITION,
            ComponentType.AI_STATE
        )
        
        if len(entities) == 0:
            return
        
        needs = self.world.components[ComponentType.NEEDS]
        pos = self.world.components[ComponentType.POSITION]
        ai = self.world.components[ComponentType.AI_STATE]
        
        need_types = ['hunger', 'energy', 'hygiene', 'social', 'fun']
        
        for entity_id in entities:
            # Skip if already doing something
            if ai['timer'].data[entity_id] > 0:
                ai['timer'].data[entity_id] -= delta_time
                continue
            
            # Find most urgent need
            most_urgent = None
            lowest_value = 100.0
            
            for need_type in need_types:
                value = needs[need_type].data[entity_id]
                if value < lowest_value:
                    lowest_value = value
                    most_urgent = need_type
            
            # If a need is below threshold, find affordance
            if lowest_value < 50.0:
                position = (
                    pos['x'].data[entity_id],
                    pos['y'].data[entity_id],
                    pos['z'].data[entity_id]
                )
                
                affordance = self.registry.find_best_affordance(
                    position, most_urgent, lowest_value
                )
                
                if affordance:
                    # Assign interaction
                    ai['target'].data[entity_id] = affordance.object_id
                    ai['timer'].data[entity_id] = affordance.duration
                    
                    # Satisfy the need
                    needs[most_urgent].data[entity_id] = min(
                        100.0,
                        needs[most_urgent].data[entity_id] + affordance.satisfaction
                    )


# =============================================================================
# DEMO: The Complete DOD Simulation
# =============================================================================

def create_demo_world() -> Tuple[World, SmartObjectRegistry]:
    """Create a demo world with entities and smart objects."""
    
    print("\n" + "="*70)
    print("🏛️ THE GREAT SCHISM: DOD ENGINE DEMO")
    print("   Data is King. The System is the Agent.")
    print("="*70 + "\n")
    
    world = World(max_entities=10000)
    registry = SmartObjectRegistry()
    
    # Register systems (The Agents)
    world.register_system(MovementSystem())
    world.register_system(NeedsDecaySystem(decay_rate=5.0))
    world.register_system(HealthSystem())
    world.register_system(AffordanceMatchingSystem(registry))
    
    print("✅ Systems registered (The Agents):")
    for sys in world.systems:
        print(f"   • {sys.name}")
    
    # Create Smart Objects (NOT entities - just affordances)
    smart_objects = [
        ("Refrigerator", "hunger", 40, 3.0, (10, 10, 0)),
        ("Bed", "energy", 60, 8.0, (5, 20, 0)),
        ("Shower", "hygiene", 50, 5.0, (15, 15, 0)),
        ("TV", "fun", 30, 2.0, (8, 8, 0)),
        ("Phone", "social", 35, 1.0, (12, 12, 0)),
        ("Coffee Machine", "energy", 20, 0.5, (10, 5, 0)),
    ]
    
    print(f"\n✅ Smart Objects registered (The Affordances):")
    for name, need, sat, dur, pos in smart_objects:
        registry.register(Affordance(
            object_id=hash(name) % 10000,
            need_type=need,
            satisfaction=sat,
            duration=dur,
            position=pos
        ))
        print(f"   • {name}: +{sat} {need}")
    
    # Create entities (The Subjects - passive data)
    num_entities = 1000
    print(f"\n✅ Creating {num_entities} entities (The Subjects)...")
    
    for i in range(num_entities):
        entity = world.create_entity()
        
        # Position - random spawn
        world.add_component(entity, ComponentType.POSITION,
            x=np.random.uniform(0, 100),
            y=np.random.uniform(0, 100),
            z=0
        )
        
        # Velocity - slight random movement
        world.add_component(entity, ComponentType.VELOCITY,
            x=np.random.uniform(-1, 1),
            y=np.random.uniform(-1, 1),
            z=0
        )
        
        # Needs - random starting values
        world.add_component(entity, ComponentType.NEEDS,
            hunger=np.random.uniform(30, 100),
            energy=np.random.uniform(30, 100),
            hygiene=np.random.uniform(30, 100),
            social=np.random.uniform(30, 100),
            fun=np.random.uniform(30, 100)
        )
        
        # AI State
        world.add_component(entity, ComponentType.AI_STATE,
            state=0,
            target=-1,
            timer=0
        )
    
    return world, registry


def run_benchmark(world: World, frames: int = 1000):
    """Run a performance benchmark."""
    
    print(f"\n🚀 Running {frames} frame benchmark...")
    print("   (This is where DOD shines)")
    
    delta_time = 1/60  # 60 FPS
    
    start = time.perf_counter()
    
    for _ in range(frames):
        world.tick(delta_time)
    
    total_time = time.perf_counter() - start
    avg_frame = (total_time / frames) * 1000
    
    print(f"\n📊 BENCHMARK RESULTS:")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Avg frame time: {avg_frame:.3f}ms")
    print(f"   FPS potential: {1000/avg_frame:.0f}")
    print(f"   Entities processed: {world.query(ComponentType.POSITION).size}")
    
    # This is the DOD magic:
    # 1000 entities × 1000 frames = 1 MILLION entity updates
    # In Python (not even C++) - still fast because of vectorized numpy ops
    
    if avg_frame < 16.66:
        print(f"\n✅ 60 FPS ACHIEVED! The System is the Agent. 🏛️")
    else:
        print(f"\n⚠️  Below 60 FPS - but this is pure Python!")
        print(f"   In C++/Rust with SIMD, this would be 100x faster.")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    world, registry = create_demo_world()
    run_benchmark(world, frames=500)
    
    print("\n" + "="*70)
    print("🎓 THE LESSONS:")
    print("="*70)
    print("""
1. DATA IS KING
   Components are SoA arrays, not OOP objects.
   The CPU cache loves us.

2. THE SYSTEM IS THE AGENT
   Entities don't "think" or "decide".
   Systems transform data. Entities are subjects.

3. SMART OBJECTS ADVERTISE
   The Sim doesn't know how to use a Sink.
   The Sink advertises what it offers.
   The System matches needs to affordances.

4. BATCH, NOT SINGLE
   MovementSystem processes ALL entities in one vectorized op.
   No for-loops calling virtual methods.

5. COMPOSITION OVER INHERITANCE
   No "class Dog extends Animal extends LivingThing".
   Just: Entity 42 has [Position, Needs, Health].

This is how you build systems that SCALE.
This is The Great Schism. 🏛️
""")
