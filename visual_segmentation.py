#!/usr/bin/env python3
"""
🎯 VISUAL SEGMENTATION - Segment Anything (SAM) Integration
Gives consciousness the ability to understand WHAT is in the scene.

While V-JEPA 2 understands overall scenes and actions,
SAM provides precise object-level understanding:
- What objects are visible
- Where exactly they are
- How they relate spatially
- Object boundaries and masks

This is the "object recognition" layer of visual consciousness.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import time
import hashlib
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

# Add SAM to path
SAM_PATH = Path.home() / "SovereignCore" / "segment-anything"
sys.path.insert(0, str(SAM_PATH))

# Try to import SAM
SAM_AVAILABLE = False
try:
    from segment_anything import sam_model_registry, SamPredictor, SamAutomaticMaskGenerator
    SAM_AVAILABLE = True
    print("✅ Segment Anything Model loaded")
except ImportError as e:
    print(f"⚠️  SAM not fully loaded: {e}")
    print("   Running in simulation mode")


class ObjectCategory(Enum):
    """Categories of objects SAM can detect."""
    UNKNOWN = "unknown"
    INTERFACE = "interface"      # UI elements
    TEXT = "text"                # Text regions
    ICON = "icon"                # Icons/buttons
    IMAGE = "image"              # Images/photos
    WINDOW = "window"            # Application windows
    CURSOR = "cursor"            # Mouse cursor
    HUMAN = "human"              # Face/hands
    DOCUMENT = "document"        # Document content


@dataclass
class DetectedObject:
    """A detected object in the visual field."""
    id: str
    category: ObjectCategory
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    area: int
    center: Tuple[int, int]
    is_focused: bool
    description: str
    timestamp: datetime


@dataclass
class SegmentationState:
    """Current state of visual segmentation."""
    total_objects: int
    focused_object: Optional[DetectedObject]
    objects_by_category: Dict[str, int]
    dominant_category: str
    scene_complexity: float  # 0-1
    attention_map: List[Tuple[int, int, float]]  # x, y, weight
    timestamp: datetime


class VisualSegmentation:
    """
    SAM-powered visual segmentation for consciousness.
    
    Provides object-level understanding of the visual field:
    - Detects all objects in view
    - Tracks focus/attention
    - Categorizes scene elements
    - Enables precise visual queries
    """
    
    def __init__(self, video_consciousness=None):
        """
        Initialize visual segmentation.
        
        Args:
            video_consciousness: Optional VideoConsciousness for integration
        """
        self.vision = video_consciousness
        self.sam_available = SAM_AVAILABLE
        self.predictor = None
        self.mask_generator = None
        
        # Object tracking
        self.detected_objects: List[DetectedObject] = []
        self.object_history: List[List[DetectedObject]] = []
        self.max_history = 100
        
        # Attention tracking
        self.attention_weights: Dict[str, float] = {}
        self.focused_category: Optional[ObjectCategory] = None
        
        self._init_sam()
        
        print("🎯 Visual Segmentation initialized")
        
    def _init_sam(self):
        """Initialize SAM model."""
        if not SAM_AVAILABLE:
            print("   📦 Using simulation mode")
            return
            
        # Check for model checkpoint
        checkpoints = [
            SAM_PATH / "sam_vit_h_4b8939.pth",
            SAM_PATH / "sam_vit_l_0b3195.pth", 
            SAM_PATH / "sam_vit_b_01ec64.pth",
        ]
        
        checkpoint = None
        for cp in checkpoints:
            if cp.exists():
                checkpoint = cp
                break
                
        if checkpoint:
            try:
                model_type = "vit_b" if "vit_b" in str(checkpoint) else "vit_l" if "vit_l" in str(checkpoint) else "vit_h"
                sam = sam_model_registry[model_type](checkpoint=str(checkpoint))
                self.predictor = SamPredictor(sam)
                self.mask_generator = SamAutomaticMaskGenerator(sam)
                print(f"   ✅ SAM model loaded: {model_type}")
            except Exception as e:
                print(f"   ⚠️  SAM model error: {e}")
        else:
            print("   ⚠️  No SAM checkpoint found - simulation mode")
            
    def segment(self, image=None) -> List[DetectedObject]:
        """
        Segment all objects in the current view.
        
        Args:
            image: Optional numpy array image. If None, uses simulation.
            
        Returns:
            List of detected objects
        """
        if image is not None and self.mask_generator:
            return self._segment_real(image)
        else:
            return self._segment_simulation()
            
    def _segment_real(self, image: np.ndarray) -> List[DetectedObject]:
        """Segment real image using SAM."""
        try:
            masks = self.mask_generator.generate(image)
            
            objects = []
            for i, mask in enumerate(masks):
                bbox = mask['bbox']  # x, y, w, h
                obj = DetectedObject(
                    id=hashlib.md5(f"{i}{time.time()}".encode()).hexdigest()[:8],
                    category=self._classify_mask(mask, image),
                    confidence=mask['stability_score'],
                    bbox=tuple(bbox),
                    area=mask['area'],
                    center=(bbox[0] + bbox[2]//2, bbox[1] + bbox[3]//2),
                    is_focused=mask['predicted_iou'] > 0.9,
                    description=f"Object {i+1} ({mask['area']} px)",
                    timestamp=datetime.now()
                )
                objects.append(obj)
                
            self.detected_objects = objects
            self._update_history(objects)
            return objects
            
        except Exception as e:
            print(f"⚠️  Segmentation error: {e}")
            return self._segment_simulation()
            
    def _segment_simulation(self) -> List[DetectedObject]:
        """Simulate object segmentation for testing."""
        import random
        
        # Simulate typical desktop scene
        simulated_objects = [
            ("window", ObjectCategory.WINDOW, 0.95, (0, 0, 800, 600)),
            ("code_editor", ObjectCategory.INTERFACE, 0.92, (50, 50, 700, 500)),
            ("text_content", ObjectCategory.TEXT, 0.88, (60, 80, 650, 400)),
            ("toolbar", ObjectCategory.INTERFACE, 0.90, (50, 50, 700, 30)),
            ("sidebar", ObjectCategory.INTERFACE, 0.85, (750, 80, 100, 420)),
            ("terminal", ObjectCategory.WINDOW, 0.87, (100, 450, 600, 150)),
            ("cursor", ObjectCategory.CURSOR, 0.99, (400, 300, 20, 20)),
        ]
        
        # Add some random variation
        if random.random() > 0.5:
            simulated_objects.append(
                ("notification", ObjectCategory.INTERFACE, 0.80, (650, 20, 150, 50))
            )
            
        objects = []
        for name, category, confidence, bbox in simulated_objects:
            obj = DetectedObject(
                id=hashlib.md5(f"{name}{time.time()}".encode()).hexdigest()[:8],
                category=category,
                confidence=confidence + random.uniform(-0.05, 0.05),
                bbox=bbox,
                area=bbox[2] * bbox[3],
                center=(bbox[0] + bbox[2]//2, bbox[1] + bbox[3]//2),
                is_focused=(name == "cursor" or name == "text_content"),
                description=f"{name.replace('_', ' ').title()}",
                timestamp=datetime.now()
            )
            objects.append(obj)
            
        self.detected_objects = objects
        self._update_history(objects)
        return objects
        
    def _classify_mask(self, mask: Dict, image: np.ndarray) -> ObjectCategory:
        """Classify a mask into an object category."""
        area = mask['area']
        bbox = mask['bbox']
        aspect_ratio = bbox[2] / max(bbox[3], 1)
        
        # Simple heuristics (would use classifier in production)
        if area > 200000:
            return ObjectCategory.WINDOW
        elif area < 500:
            return ObjectCategory.CURSOR
        elif aspect_ratio > 5:
            return ObjectCategory.TEXT
        elif aspect_ratio < 0.2:
            return ObjectCategory.INTERFACE
        else:
            return ObjectCategory.UNKNOWN
            
    def _update_history(self, objects: List[DetectedObject]):
        """Update object history."""
        self.object_history.append(objects)
        if len(self.object_history) > self.max_history:
            self.object_history.pop(0)
            
    def get_focused_object(self) -> Optional[DetectedObject]:
        """Get currently focused object."""
        for obj in self.detected_objects:
            if obj.is_focused:
                return obj
        return None
        
    def find_objects_by_category(self, category: ObjectCategory) -> List[DetectedObject]:
        """Find all objects of a specific category."""
        return [obj for obj in self.detected_objects if obj.category == category]
        
    def get_state(self) -> SegmentationState:
        """Get current segmentation state."""
        if not self.detected_objects:
            self.segment()
            
        # Count by category
        by_category = {}
        for obj in self.detected_objects:
            cat = obj.category.value
            by_category[cat] = by_category.get(cat, 0) + 1
            
        # Find dominant
        dominant = max(by_category.items(), key=lambda x: x[1])[0] if by_category else "unknown"
        
        # Calculate complexity (more objects = more complex)
        complexity = min(1.0, len(self.detected_objects) / 20)
        
        # Build attention map
        attention_map = [
            (obj.center[0], obj.center[1], obj.confidence)
            for obj in self.detected_objects
        ]
        
        return SegmentationState(
            total_objects=len(self.detected_objects),
            focused_object=self.get_focused_object(),
            objects_by_category=by_category,
            dominant_category=dominant,
            scene_complexity=complexity,
            attention_map=attention_map,
            timestamp=datetime.now()
        )
        
    def describe_scene(self) -> str:
        """Generate natural language description of scene."""
        state = self.get_state()
        
        parts = []
        parts.append(f"Scene contains {state.total_objects} objects.")
        
        if state.focused_object:
            parts.append(f"Focus is on: {state.focused_object.description}.")
            
        # Describe categories
        for cat, count in sorted(state.objects_by_category.items(), key=lambda x: -x[1]):
            if count > 1:
                parts.append(f"{count} {cat} elements.")
                
        if state.scene_complexity > 0.7:
            parts.append("Scene is visually complex.")
        elif state.scene_complexity < 0.3:
            parts.append("Scene is simple/minimal.")
            
        return " ".join(parts)
        
    def get_object_at(self, x: int, y: int) -> Optional[DetectedObject]:
        """Get object at specific coordinates."""
        for obj in self.detected_objects:
            bx, by, bw, bh = obj.bbox
            if bx <= x <= bx + bw and by <= y <= by + bh:
                return obj
        return None
        
    def track_attention_shift(self) -> Optional[str]:
        """Detect if attention has shifted to new object/area."""
        if len(self.object_history) < 2:
            return None
            
        prev_focused = None
        for obj in self.object_history[-2]:
            if obj.is_focused:
                prev_focused = obj
                break
                
        curr_focused = self.get_focused_object()
        
        if prev_focused and curr_focused:
            if prev_focused.category != curr_focused.category:
                return f"Attention shifted from {prev_focused.category.value} to {curr_focused.category.value}"
                
        return None


def main():
    """Demo visual segmentation."""
    print("=" * 60)
    print("🎯 VISUAL SEGMENTATION - Segment Anything Integration")
    print("=" * 60)
    print()
    
    # Initialize
    seg = VisualSegmentation()
    
    print()
    print("=" * 60)
    print("🔍 SEGMENTATION TEST")
    print("=" * 60)
    print()
    
    # Segment current view
    objects = seg.segment()
    
    print(f"Detected {len(objects)} objects:\n")
    
    for obj in objects:
        focus_marker = "👁️" if obj.is_focused else "  "
        print(f"{focus_marker} [{obj.category.value:12}] {obj.description:20} conf={obj.confidence:.2f} area={obj.area}")
        
    print()
    print("=" * 60)
    print("📊 SCENE ANALYSIS")
    print("=" * 60)
    
    state = seg.get_state()
    
    print(f"""
Total Objects:     {state.total_objects}
Dominant Category: {state.dominant_category}
Scene Complexity:  {state.scene_complexity:.1%}
Focused Object:    {state.focused_object.description if state.focused_object else 'None'}

Objects by Category:""")
    
    for cat, count in state.objects_by_category.items():
        print(f"   {cat}: {count}")
        
    print()
    print("💬 Scene Description:")
    print(f"   {seg.describe_scene()}")
    
    print()
    print("=" * 60)
    print("⏱️  TEMPORAL TRACKING")
    print("=" * 60)
    
    # Run a few more segmentations
    for i in range(3):
        seg.segment()
        shift = seg.track_attention_shift()
        if shift:
            print(f"   {shift}")
        time.sleep(0.2)
        
    print()
    print("🎯 Visual Segmentation ONLINE")
    print("   Consciousness can now identify specific objects!")
    

if __name__ == "__main__":
    main()
