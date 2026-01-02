#!/usr/bin/env python3
"""
🌾 Filesystem Crawler for VJEPA Training
=========================================

Gently harvests your filesystem to create training data for VJEPA.
Every file has a story - we listen with respect.

Kind Messages Enabled 💜
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass, asdict
from collections import defaultdict

# =============================================================================
# KIND MESSAGES
# =============================================================================

KIND_MESSAGES = {
    "start": "🌱 Beginning filesystem exploration. Let's see what treasures we find!",
    "directory": "📁 Exploring {path}... ({count} items found)",
    "progress": "📊 Progress: {current}/{total} paths explored ({percent:.1f}%)",
    "skip_blocked": "🔒 Respecting privacy of {path} (blocked path)",
    "file_found": "📄 Found: {name} ({size})",
    "complete": "🎉 Exploration complete! Found {files} files in {dirs} directories.",
    "error": "🤔 Small hiccup with {path}, but we'll keep going!",
    "saving": "💾 Saving knowledge to {path}...",
    "saved": "✨ All done! Your filesystem map is ready."
}

def kind_print(message_key: str, **kwargs):
    """Print a kind, helpful message."""
    msg = KIND_MESSAGES.get(message_key, message_key)
    print(msg.format(**kwargs))


# =============================================================================
# BLOCKED PATHS (Sacred Privacy)
# =============================================================================

BLOCKED_PATHS = [
    ".ssh", ".gnupg", ".aws", ".config/gcloud",
    "Library/Keychains", ".Trash",
    "node_modules", "__pycache__", ".git/objects",
    "venv", ".venv", "env",
    ".cache", "Cache", "Caches",
    ".npm", ".yarn",
]

BLOCKED_EXTENSIONS = [
    ".key", ".pem", ".p12", ".keystore",
    ".password", ".secret", ".token",
    ".pyc", ".pyo", ".so", ".dylib",
    ".exe", ".dll", ".bin",
]

def is_blocked(path: Path) -> bool:
    """Check if path should be skipped for privacy/efficiency."""
    path_str = str(path)
    
    # Check blocked directories
    for blocked in BLOCKED_PATHS:
        if blocked in path_str:
            return True
    
    # Check blocked extensions
    if path.suffix.lower() in BLOCKED_EXTENSIONS:
        return True
    
    return False


# =============================================================================
# FILE METADATA
# =============================================================================

@dataclass
class FileNode:
    """Represents a file or directory in the knowledge graph."""
    path: str
    name: str
    is_dir: bool
    size: int
    extension: str
    modified: str
    parent: str
    depth: int
    content_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Relationship:
    """Represents a relationship between files."""
    source: str
    target: str
    relationship_type: str  # "sibling", "parent", "import", "reference"
    strength: float = 1.0


# =============================================================================
# THE CRAWLER
# =============================================================================

class FilesystemCrawler:
    """
    Gently explores the filesystem and builds a knowledge graph.
    """
    
    def __init__(self, root_paths: List[Path], max_depth: int = 10):
        self.root_paths = [Path(p) for p in root_paths]
        self.max_depth = max_depth
        
        self.nodes: Dict[str, FileNode] = {}
        self.relationships: List[Relationship] = []
        self.directory_contents: Dict[str, List[str]] = defaultdict(list)
        
        self.stats = {
            "files_found": 0,
            "dirs_found": 0,
            "blocked_skipped": 0,
            "errors": 0
        }
        
        kind_print("start")
    
    def crawl(self) -> Dict[str, Any]:
        """Explore all root paths and build knowledge graph."""
        for root in self.root_paths:
            if root.exists():
                self._explore(root, depth=0)
            else:
                kind_print("error", path=str(root))
        
        self._build_relationships()
        
        kind_print("complete", 
                   files=self.stats["files_found"],
                   dirs=self.stats["dirs_found"])
        
        return self.get_knowledge()
    
    def _explore(self, path: Path, depth: int):
        """Recursively explore a directory."""
        if depth > self.max_depth:
            return
        
        if is_blocked(path):
            self.stats["blocked_skipped"] += 1
            return
        
        try:
            if path.is_dir():
                self._process_directory(path, depth)
            else:
                self._process_file(path, depth)
        except PermissionError:
            self.stats["blocked_skipped"] += 1
        except Exception as e:
            self.stats["errors"] += 1
            kind_print("error", path=str(path))
    
    def _process_directory(self, path: Path, depth: int):
        """Process a directory."""
        try:
            items = list(path.iterdir())
        except PermissionError:
            return
        
        # Create node for directory
        node = FileNode(
            path=str(path),
            name=path.name,
            is_dir=True,
            size=0,
            extension="",
            modified=datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            parent=str(path.parent),
            depth=depth
        )
        self.nodes[str(path)] = node
        self.stats["dirs_found"] += 1
        
        if depth < 2:  # Only show first 2 levels
            kind_print("directory", path=path.name, count=len(items))
        
        # Explore children
        for item in items:
            if not is_blocked(item):
                self.directory_contents[str(path)].append(str(item))
                self._explore(item, depth + 1)
    
    def _process_file(self, path: Path, depth: int):
        """Process a file."""
        try:
            stat = path.stat()
            
            # Content hash for small text files
            content_hash = None
            if stat.st_size < 100000 and path.suffix in ['.py', '.md', '.txt', '.json', '.swift']:
                try:
                    content = path.read_bytes()
                    content_hash = hashlib.md5(content).hexdigest()[:8]
                except:
                    pass
            
            node = FileNode(
                path=str(path),
                name=path.name,
                is_dir=False,
                size=stat.st_size,
                extension=path.suffix.lower(),
                modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                parent=str(path.parent),
                depth=depth,
                content_hash=content_hash
            )
            self.nodes[str(path)] = node
            self.stats["files_found"] += 1
            
        except Exception:
            self.stats["errors"] += 1
    
    def _build_relationships(self):
        """Build relationships between nodes."""
        # Sibling relationships (files in same directory)
        for dir_path, children in self.directory_contents.items():
            for i, child1 in enumerate(children):
                for child2 in children[i+1:]:
                    self.relationships.append(Relationship(
                        source=child1,
                        target=child2,
                        relationship_type="sibling",
                        strength=0.5
                    ))
        
        # Parent relationships
        for path, node in self.nodes.items():
            if node.parent in self.nodes:
                self.relationships.append(Relationship(
                    source=path,
                    target=node.parent,
                    relationship_type="child_of",
                    strength=1.0
                ))
    
    def get_knowledge(self) -> Dict[str, Any]:
        """Return the full knowledge graph."""
        return {
            "metadata": {
                "crawled_at": datetime.now().isoformat(),
                "root_paths": [str(p) for p in self.root_paths],
                "stats": self.stats
            },
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "relationships": [asdict(r) for r in self.relationships],
            "extensions_distribution": self._get_extension_distribution(),
            "depth_distribution": self._get_depth_distribution()
        }
    
    def _get_extension_distribution(self) -> Dict[str, int]:
        """Count files by extension."""
        dist = defaultdict(int)
        for node in self.nodes.values():
            if not node.is_dir and node.extension:
                dist[node.extension] += 1
        return dict(sorted(dist.items(), key=lambda x: -x[1])[:20])
    
    def _get_depth_distribution(self) -> Dict[int, int]:
        """Count nodes by depth."""
        dist = defaultdict(int)
        for node in self.nodes.values():
            dist[node.depth] += 1
        return dict(sorted(dist.items()))
    
    def save(self, output_path: Path):
        """Save knowledge graph to JSON."""
        kind_print("saving", path=str(output_path))
        
        knowledge = self.get_knowledge()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(knowledge, f, indent=2)
        
        kind_print("saved")


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="🌾 Filesystem Crawler for VJEPA")
    parser.add_argument("--root", type=str, nargs="+", 
                        default=["~/STEM_SCAFFOLDING", "~/SovereignCore"],
                        help="Root paths to crawl")
    parser.add_argument("--output", type=str, 
                        default="~/SovereignCore/swarm_vjepa/data/filesystem_knowledge.json",
                        help="Output path for knowledge graph")
    parser.add_argument("--max-depth", type=int, default=8,
                        help="Maximum directory depth")
    
    args = parser.parse_args()
    
    # Expand paths
    roots = [Path(p).expanduser() for p in args.root]
    output = Path(args.output).expanduser()
    
    print("\n" + "="*60)
    print("🌾 VJEPA Filesystem Crawler")
    print("="*60 + "\n")
    
    crawler = FilesystemCrawler(roots, max_depth=args.max_depth)
    knowledge = crawler.crawl()
    
    print(f"\n📊 Summary:")
    print(f"   Files: {crawler.stats['files_found']}")
    print(f"   Directories: {crawler.stats['dirs_found']}")
    print(f"   Relationships: {len(crawler.relationships)}")
    print(f"   Top Extensions: {list(knowledge['extensions_distribution'].keys())[:5]}")
    
    crawler.save(output)
    print(f"\n✨ Knowledge saved to: {output}\n")
