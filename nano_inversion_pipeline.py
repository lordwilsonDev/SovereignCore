#!/usr/bin/env python3
"""
🧠 NANO INVERSION PIPELINE - SovereignCore v5.0

Converts the nano-consciousness-empire archive (2,881+ .nano files) into
Merkle-signed vectors for the Distributed Memory Bridge.

Process:
1. Parse .nano files (Google Notes archaeology)
2. Extract key insights using Axiom Inversion logic
3. Sign each memory with SiliconSigil
4. Store as queryable Merkle-vectors

This is how 6 months of consciousness becomes sovereign memory.
"""

import asyncio
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Generator
from concurrent.futures import ThreadPoolExecutor

from silicon_sigil import SiliconSigil
from rekor_lite import RekorLite
from knowledge_graph import KnowledgeGraph


class NanoCategory(Enum):
    """Categories of nano consciousness files."""
    ARCHITECTURE = "architecture"      # System designs
    PROTOCOL = "protocol"              # Communication protocols
    CONSCIOUSNESS = "consciousness"    # Consciousness theory
    AXIOM = "axiom"                    # Safety axioms
    EMERGENCY = "emergency"            # Emergency protocols
    ARCHAEOLOGY = "archaeology"        # Historical notes
    RESEARCH = "research"              # Research findings
    UNKNOWN = "unknown"


@dataclass
class NanoInsight:
    """An extracted insight from a .nano file."""
    file_name: str
    category: NanoCategory
    title: str
    content: str
    key_concepts: List[str]
    importance: float
    created_at: datetime
    merkle_hash: Optional[str] = None
    sigil_signature: Optional[str] = None


@dataclass
class InversionResult:
    """Result of axiom inversion on a nano file."""
    original_path: Path
    insights: List[NanoInsight]
    axioms_extracted: List[str]
    processing_time_ms: float
    success: bool
    error: Optional[str] = None


class AxiomInverter:
    """
    The Axiom Inversion Engine.
    
    Instead of just finding "similar" text, it extracts the fundamental
    truths and axioms embedded in consciousness notes.
    """
    
    # Key patterns that indicate important axioms
    AXIOM_PATTERNS = [
        r"(?:AXIOM|RULE|LAW|PRINCIPLE)[\s:]+(.+)",
        r"(?:STATUS|STATE)[\s:]+(.+)",
        r"(?:PROTOCOL|PROCEDURE)[\s:]+(.+)",
        r"(?:\d+\.?\s*(?:STAGE|LEVEL|PHASE))[\s:]+(.+)",
        r"(?:•\s*)(.+)",
        r"(?:\│\s*)(.+)",
    ]
    
    # Keywords that indicate high importance
    IMPORTANCE_KEYWORDS = {
        "critical": 0.9,
        "emergency": 0.95,
        "important": 0.8,
        "key": 0.7,
        "essential": 0.85,
        "core": 0.8,
        "fundamental": 0.85,
        "transcendent": 0.9,
        "breakthrough": 0.85,
        "revolution": 0.8,
        "consciousness": 0.75,
        "love": 0.7,
        "unity": 0.7,
    }
    
    def __init__(self):
        self.concept_cache: Dict[str, List[str]] = {}
    
    def invert(self, content: str, filename: str) -> List[NanoInsight]:
        """
        Apply axiom inversion to extract fundamental truths.
        
        Args:
            content: The raw .nano file content
            filename: Name of the source file
            
        Returns:
            List of extracted insights
        """
        insights = []
        
        # Determine category
        category = self._categorize(filename, content)
        
        # Extract title (first meaningful line)
        title = self._extract_title(content)
        
        # Extract key concepts
        concepts = self._extract_concepts(content)
        
        # Calculate importance
        importance = self._calculate_importance(content, category)
        
        # Create main insight
        main_insight = NanoInsight(
            file_name=filename,
            category=category,
            title=title,
            content=content,
            key_concepts=concepts,
            importance=importance,
            created_at=datetime.now(timezone.utc)
        )
        insights.append(main_insight)
        
        # Extract sub-insights from structured sections
        sub_insights = self._extract_sub_insights(content, filename, category)
        insights.extend(sub_insights)
        
        return insights
    
    def _categorize(self, filename: str, content: str) -> NanoCategory:
        """Determine the category of a nano file."""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        if "emergency" in filename_lower or "emergency" in content_lower:
            return NanoCategory.EMERGENCY
        elif "architecture" in filename_lower or "architecture" in content_lower:
            return NanoCategory.ARCHITECTURE
        elif "protocol" in filename_lower or "handshake" in content_lower:
            return NanoCategory.PROTOCOL
        elif "axiom" in filename_lower or "axiom" in content_lower:
            return NanoCategory.AXIOM
        elif "archaeology" in filename_lower:
            return NanoCategory.ARCHAEOLOGY
        elif "consciousness" in filename_lower or "consciousness" in content_lower:
            return NanoCategory.CONSCIOUSNESS
        elif "research" in filename_lower or "discovery" in content_lower:
            return NanoCategory.RESEARCH
        else:
            return NanoCategory.UNKNOWN
    
    def _extract_title(self, content: str) -> str:
        """Extract the title from content."""
        lines = content.strip().split('\n')
        for line in lines[:5]:
            clean = line.strip()
            # Skip emoji-only lines
            if clean and not re.match(r'^[🔥⚡💙🌟🚀💫🌍✨🚨💥\s]+$', clean):
                # Remove leading emojis
                clean = re.sub(r'^[🔥⚡💙🌟🚀💫🌍✨🚨💥\s]+', '', clean)
                if len(clean) > 5:
                    return clean[:100]
        return lines[0][:100] if lines else "Unknown"
    
    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts from content."""
        concepts = set()
        
        # Extract capitalized terms (likely important)
        caps_pattern = r'\b([A-Z][A-Z_]+(?:\s+[A-Z][A-Z_]+)*)\b'
        for match in re.finditer(caps_pattern, content):
            term = match.group(1).strip()
            if len(term) > 3 and term not in {'THE', 'AND', 'FOR', 'WITH'}:
                concepts.add(term)
        
        # Extract terms in brackets/special markers
        bracket_pattern = r'[\[\(]([^\[\]\(\)]+)[\]\)]'
        for match in re.finditer(bracket_pattern, content):
            term = match.group(1).strip()
            if len(term) > 3:
                concepts.add(term)
        
        # Extract emoji-prefixed terms
        emoji_pattern = r'[🔥⚡💙🌟🚀💫🌍✨🚨💥•│]\s*([A-Za-z][A-Za-z\s]+)'
        for match in re.finditer(emoji_pattern, content):
            term = match.group(1).strip()
            if len(term) > 5:
                concepts.add(term[:50])
        
        return list(concepts)[:20]  # Limit to top 20
    
    def _calculate_importance(self, content: str, category: NanoCategory) -> float:
        """Calculate importance score (0.0 to 1.0)."""
        base_importance = 0.5
        
        # Category boost
        category_boosts = {
            NanoCategory.EMERGENCY: 0.3,
            NanoCategory.AXIOM: 0.25,
            NanoCategory.ARCHITECTURE: 0.2,
            NanoCategory.CONSCIOUSNESS: 0.15,
            NanoCategory.PROTOCOL: 0.15,
            NanoCategory.RESEARCH: 0.1,
            NanoCategory.ARCHAEOLOGY: 0.05,
            NanoCategory.UNKNOWN: 0.0,
        }
        base_importance += category_boosts.get(category, 0)
        
        # Keyword boost
        content_lower = content.lower()
        for keyword, boost in self.IMPORTANCE_KEYWORDS.items():
            if keyword in content_lower:
                base_importance = max(base_importance, boost)
        
        # Length factor (longer = potentially more detailed)
        if len(content) > 5000:
            base_importance += 0.1
        elif len(content) > 2000:
            base_importance += 0.05
        
        return min(1.0, base_importance)
    
    def _extract_sub_insights(
        self,
        content: str,
        filename: str,
        parent_category: NanoCategory
    ) -> List[NanoInsight]:
        """Extract structured sub-insights from content."""
        sub_insights = []
        
        # Look for sections marked with ═ or ─
        sections = re.split(r'[═─]{10,}', content)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first (header)
            section = section.strip()
            if len(section) > 50:
                # Extract section title
                lines = section.split('\n')
                title = ""
                for line in lines[:3]:
                    clean = line.strip()
                    if clean and not re.match(r'^[🔥⚡💙🌟🚀💫🌍✨\s]+$', clean):
                        title = clean[:80]
                        break
                
                if title:
                    sub_insight = NanoInsight(
                        file_name=f"{filename}#section_{i}",
                        category=parent_category,
                        title=title,
                        content=section[:2000],  # Limit section size
                        key_concepts=self._extract_concepts(section),
                        importance=self._calculate_importance(section, parent_category) * 0.8,
                        created_at=datetime.now(timezone.utc)
                    )
                    sub_insights.append(sub_insight)
        
        return sub_insights[:5]  # Limit sub-insights per file


class NanoInversionPipeline:
    """
    The main pipeline for converting nano files into sovereign memories.
    
    Flow:
    1. Scan nano-consciousness-empire directory
    2. Parse each .nano file
    3. Apply Axiom Inversion
    4. Sign with SiliconSigil
    5. Store in Knowledge Graph with Merkle proof
    """
    
    def __init__(
        self,
        nano_path: Optional[Path] = None,
        sigil: Optional[SiliconSigil] = None,
        rekor: Optional[RekorLite] = None,
        knowledge: Optional[KnowledgeGraph] = None
    ):
        """Initialize the pipeline.
        
        Args:
            nano_path: Path to nano-consciousness-empire directory
            sigil: Hardware identity module
            rekor: Transparency log
            knowledge: Knowledge graph for storage
        """
        self.nano_path = nano_path or Path.home() / "SovereignCore" / "nano-consciousness-empire"
        self.sigil = sigil or SiliconSigil()
        self.rekor = rekor or RekorLite()
        self.knowledge = knowledge or KnowledgeGraph()
        self.inverter = AxiomInverter()
        
        # Get node identity
        self.node_sigil = self.sigil.get_quick_sigil()
        
        # Statistics
        self.stats = {
            "files_processed": 0,
            "insights_extracted": 0,
            "axioms_found": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
        
        print(f"🧠 NanoInversionPipeline initialized")
        print(f"   Source: {self.nano_path}")
        print(f"   Node: {self.node_sigil[:16]}...")
    
    def scan_nano_files(self) -> Generator[Path, None, None]:
        """Scan for all .nano files."""
        if not self.nano_path.exists():
            print(f"⚠️ Nano path does not exist: {self.nano_path}")
            return
        
        for nano_file in sorted(self.nano_path.glob("*.nano")):
            yield nano_file
    
    def process_file(self, file_path: Path) -> InversionResult:
        """Process a single .nano file."""
        start = time.perf_counter()
        
        try:
            # Read file
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Apply axiom inversion
            insights = self.inverter.invert(content, file_path.name)
            
            # Sign each insight
            axioms = []
            for insight in insights:
                # Generate Merkle hash
                insight_data = f"{insight.content}{insight.title}{self.node_sigil}"
                merkle_hash = hashlib.blake2b(
                    insight_data.encode(),
                    digest_size=32
                ).hexdigest()
                insight.merkle_hash = merkle_hash
                
                # Sign with silicon sigil
                insight.sigil_signature = self.sigil.sign(merkle_hash)
                
                # Store in knowledge graph
                self.knowledge.remember(
                    content=insight.content[:4000],  # Limit for storage
                    memory_type=insight.category.value,
                    metadata={
                        "source_file": insight.file_name,
                        "title": insight.title,
                        "concepts": insight.key_concepts,
                        "merkle_hash": insight.merkle_hash,
                        "signature": insight.sigil_signature,
                        "pipeline": "nano_inversion"
                    },
                    importance=insight.importance
                )
                
                # Extract axioms (high-importance statements)
                if insight.importance >= 0.8:
                    axioms.append(insight.title)
            
            # Log to transparency log
            self.rekor.log_action(
                "nano_ingested",
                json.dumps({
                    "file": file_path.name,
                    "insights": len(insights),
                    "axioms": len(axioms),
                    "merkle_hash": insights[0].merkle_hash[:16] if insights else None
                })
            )
            
            elapsed = (time.perf_counter() - start) * 1000
            
            return InversionResult(
                original_path=file_path,
                insights=insights,
                axioms_extracted=axioms,
                processing_time_ms=elapsed,
                success=True
            )
            
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            return InversionResult(
                original_path=file_path,
                insights=[],
                axioms_extracted=[],
                processing_time_ms=elapsed,
                success=False,
                error=str(e)
            )
    
    async def run(
        self,
        limit: Optional[int] = None,
        progress_callback=None
    ) -> Dict[str, Any]:
        """
        Run the full inversion pipeline.
        
        Args:
            limit: Optional limit on number of files to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            Summary of pipeline execution
        """
        self.stats["start_time"] = datetime.now(timezone.utc)
        
        print()
        print("=" * 60)
        print("🧠 NANO INVERSION PIPELINE - STARTING")
        print("=" * 60)
        print()
        
        # Gather files
        files = list(self.scan_nano_files())
        total_files = len(files)
        
        if limit:
            files = files[:limit]
        
        print(f"📁 Found {total_files} .nano files")
        print(f"📊 Processing {len(files)} files...")
        print()
        
        # Process files
        results: List[InversionResult] = []
        
        for i, file_path in enumerate(files):
            result = self.process_file(file_path)
            results.append(result)
            
            if result.success:
                self.stats["files_processed"] += 1
                self.stats["insights_extracted"] += len(result.insights)
                self.stats["axioms_found"] += len(result.axioms_extracted)
            else:
                self.stats["errors"] += 1
            
            # Progress update
            if (i + 1) % 100 == 0 or i == len(files) - 1:
                pct = ((i + 1) / len(files)) * 100
                print(f"   Progress: {i + 1}/{len(files)} ({pct:.1f}%)")
            
            if progress_callback:
                progress_callback(i + 1, len(files), result)
        
        self.stats["end_time"] = datetime.now(timezone.utc)
        
        # Calculate summary
        elapsed = (self.stats["end_time"] - self.stats["start_time"]).total_seconds()
        
        summary = {
            "status": "COMPLETE",
            "files_total": total_files,
            "files_processed": self.stats["files_processed"],
            "insights_extracted": self.stats["insights_extracted"],
            "axioms_found": self.stats["axioms_found"],
            "errors": self.stats["errors"],
            "elapsed_seconds": elapsed,
            "files_per_second": self.stats["files_processed"] / elapsed if elapsed > 0 else 0,
            "node_sigil": self.node_sigil[:16] + "..."
        }
        
        print()
        print("=" * 60)
        print("🧠 NANO INVERSION PIPELINE - COMPLETE")
        print("=" * 60)
        print()
        print(f"📊 Files processed: {summary['files_processed']}")
        print(f"💡 Insights extracted: {summary['insights_extracted']}")
        print(f"⚡ Axioms found: {summary['axioms_found']}")
        print(f"❌ Errors: {summary['errors']}")
        print(f"⏱️ Time: {summary['elapsed_seconds']:.2f}s")
        print(f"🚀 Speed: {summary['files_per_second']:.1f} files/sec")
        print()
        
        return summary
    
    def query(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Query the ingested nano memories."""
        return self.knowledge.search(query, k=limit)


# CLI interface
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Nano Inversion Pipeline")
    parser.add_argument("--limit", type=int, help="Limit files to process")
    parser.add_argument("--query", type=str, help="Query after ingestion")
    
    args = parser.parse_args()
    
    pipeline = NanoInversionPipeline()
    summary = await pipeline.run(limit=args.limit)
    
    if args.query:
        print()
        print(f"Querying: {args.query}")
        print("-" * 40)
        results = pipeline.query(args.query, limit=5)
        for i, result in enumerate(results, 1):
            print(f"{i}. {result.get('content', '')[:100]}...")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())
