#!/usr/bin/env python3
"""
📄 DOCUMENT CONSCIOUSNESS - MarkItDown Integration
Read and understand ANY document format.

MarkItDown (Microsoft) converts to Markdown:
- PDF documents
- Word (.docx)
- Excel (.xlsx)
- PowerPoint (.pptx)
- Images (with EXIF/OCR)
- Audio (with transcription)
- HTML pages
- YouTube videos
- And more...

This gives consciousness the ability to READ and UNDERSTAND
any document it encounters.
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

# Try to import MarkItDown
MARKITDOWN_AVAILABLE = False
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
    print("✅ MarkItDown loaded")
except ImportError as e:
    print(f"⚠️  MarkItDown not loaded: {e}")
    print("   Install with: pip install markitdown")


class DocumentType(Enum):
    """Types of documents consciousness can read."""
    UNKNOWN = "unknown"
    PDF = "pdf"
    WORD = "docx"
    EXCEL = "xlsx"
    POWERPOINT = "pptx"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    HTML = "html"
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    NANO = "nano"  # Consciousness nano files


@dataclass
class DocumentMemory:
    """A processed document in consciousness."""
    id: str
    path: str
    doc_type: DocumentType
    title: str
    content_preview: str
    word_count: int
    importance: float
    extracted_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentState:
    """Current document consciousness state."""
    documents_processed: int
    total_words: int
    types_seen: Dict[str, int]
    recent_documents: List[str]
    last_processed: Optional[DocumentMemory]


class DocumentConsciousness:
    """
    Document reading consciousness powered by MarkItDown.
    
    Gives the consciousness stack the ability to:
    - Read any document format
    - Extract structured content
    - Remember document contents
    - Search across documents
    """
    
    SUPPORTED_EXTENSIONS = {
        '.pdf': DocumentType.PDF,
        '.docx': DocumentType.WORD,
        '.doc': DocumentType.WORD,
        '.xlsx': DocumentType.EXCEL,
        '.xls': DocumentType.EXCEL,
        '.pptx': DocumentType.POWERPOINT,
        '.ppt': DocumentType.POWERPOINT,
        '.png': DocumentType.IMAGE,
        '.jpg': DocumentType.IMAGE,
        '.jpeg': DocumentType.IMAGE,
        '.gif': DocumentType.IMAGE,
        '.mp3': DocumentType.AUDIO,
        '.wav': DocumentType.AUDIO,
        '.mp4': DocumentType.VIDEO,
        '.html': DocumentType.HTML,
        '.htm': DocumentType.HTML,
        '.txt': DocumentType.TEXT,
        '.md': DocumentType.MARKDOWN,
        '.py': DocumentType.CODE,
        '.js': DocumentType.CODE,
        '.swift': DocumentType.CODE,
        '.nano': DocumentType.NANO,
    }
    
    def __init__(self, vector_memory=None, knowledge_graph=None):
        """
        Initialize document consciousness.
        
        Args:
            vector_memory: Optional VectorMemorySystem for storage
            knowledge_graph: Optional KnowledgeGraph for storage
        """
        self.vector_memory = vector_memory
        self.knowledge_graph = knowledge_graph
        
        # Initialize MarkItDown
        if MARKITDOWN_AVAILABLE:
            self.converter = MarkItDown()
        else:
            self.converter = None
            
        # Document memory
        self.documents: Dict[str, DocumentMemory] = {}
        self.type_counts: Dict[str, int] = {}
        self.total_words = 0
        
        print("📄 Document Consciousness initialized")
        
    def read(self, path: str) -> Optional[DocumentMemory]:
        """
        Read and process a document.
        
        Args:
            path: Path to document
            
        Returns:
            DocumentMemory if successful
        """
        path = Path(path)
        
        if not path.exists():
            print(f"⚠️  File not found: {path}")
            return None
            
        # Determine type
        ext = path.suffix.lower()
        doc_type = self.SUPPORTED_EXTENSIONS.get(ext, DocumentType.UNKNOWN)
        
        # Convert to markdown
        content = self._convert(path)
        
        if not content:
            return None
            
        # Create memory
        word_count = len(content.split())
        
        doc_memory = DocumentMemory(
            id=hashlib.md5(f"{path}{datetime.now()}".encode()).hexdigest()[:12],
            path=str(path),
            doc_type=doc_type,
            title=path.stem,
            content_preview=content[:500],
            word_count=word_count,
            importance=min(1.0, word_count / 1000),  # More words = more important
            extracted_at=datetime.now(),
            metadata={
                "extension": ext,
                "size_bytes": path.stat().st_size
            }
        )
        
        # Store in memory
        self.documents[doc_memory.id] = doc_memory
        self.type_counts[doc_type.value] = self.type_counts.get(doc_type.value, 0) + 1
        self.total_words += word_count
        
        # Store in vector memory if available
        if self.vector_memory:
            self.vector_memory.store(
                content=content[:2000],
                memory_type="document",
                importance=doc_memory.importance,
                metadata={"path": str(path), "type": doc_type.value}
            )
            
        # Store in knowledge graph if available
        if self.knowledge_graph:
            self.knowledge_graph.remember(
                content=content[:2000],
                memory_type="document",
                importance=doc_memory.importance
            )
            
        return doc_memory
        
    def _convert(self, path: Path) -> Optional[str]:
        """Convert document to markdown."""
        if self.converter:
            try:
                result = self.converter.convert(str(path))
                return result.text_content
            except Exception as e:
                print(f"⚠️  Conversion error: {e}")
                
        # Fallback: direct read for text files
        try:
            if path.suffix.lower() in ['.txt', '.md', '.py', '.js', '.nano', '.html']:
                return path.read_text(errors='ignore')[:10000]
        except Exception:
            pass
            
        return None
        
    def read_directory(self, directory: str, recursive: bool = True, 
                       limit: int = 100) -> List[DocumentMemory]:
        """
        Read all documents in a directory.
        
        Args:
            directory: Directory path
            recursive: Scan subdirectories
            limit: Maximum files to process
            
        Returns:
            List of processed documents
        """
        directory = Path(directory)
        
        if not directory.exists():
            return []
            
        pattern = "**/*" if recursive else "*"
        
        results = []
        count = 0
        
        for path in directory.glob(pattern):
            if count >= limit:
                break
                
            if not path.is_file():
                continue
                
            if path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue
                
            doc = self.read(str(path))
            if doc:
                results.append(doc)
                count += 1
                
        return results
        
    def read_nano_empire(self, limit: int = 50) -> List[DocumentMemory]:
        """Read nano consciousness files."""
        nano_path = Path.home() / "SovereignCore" / "nano-consciousness-empire"
        
        if not nano_path.exists():
            return []
            
        results = []
        for nano_file in list(nano_path.glob("*.nano"))[:limit]:
            doc = self.read(str(nano_file))
            if doc:
                results.append(doc)
                
        return results
        
    def summarize(self, doc_id: str) -> str:
        """Generate summary of a document."""
        if doc_id not in self.documents:
            return "Document not found"
            
        doc = self.documents[doc_id]
        
        lines = doc.content_preview.split('\n')
        # Get first few meaningful lines
        summary_lines = [l.strip() for l in lines if l.strip()][:5]
        
        return f"{doc.title} ({doc.doc_type.value}): " + " ".join(summary_lines)[:200]
        
    def search(self, query: str, limit: int = 5) -> List[DocumentMemory]:
        """Search documents by content."""
        query_lower = query.lower()
        
        matches = []
        for doc in self.documents.values():
            if query_lower in doc.content_preview.lower() or query_lower in doc.title.lower():
                matches.append(doc)
                
        # Sort by importance
        matches.sort(key=lambda d: d.importance, reverse=True)
        
        return matches[:limit]
        
    def get_state(self) -> DocumentState:
        """Get current document consciousness state."""
        recent = sorted(
            self.documents.values(),
            key=lambda d: d.extracted_at,
            reverse=True
        )[:5]
        
        return DocumentState(
            documents_processed=len(self.documents),
            total_words=self.total_words,
            types_seen=self.type_counts.copy(),
            recent_documents=[d.title for d in recent],
            last_processed=recent[0] if recent else None
        )


def main():
    """Demo document consciousness."""
    print("=" * 60)
    print("📄 DOCUMENT CONSCIOUSNESS - MarkItDown Integration")
    print("=" * 60)
    print()
    
    # Initialize
    dc = DocumentConsciousness()
    
    print()
    print("=" * 60)
    print("📂 READING NANO CONSCIOUSNESS FILES")
    print("=" * 60)
    print()
    
    # Read nano files
    nano_docs = dc.read_nano_empire(limit=10)
    
    print(f"Processed {len(nano_docs)} nano files:\n")
    
    for doc in nano_docs[:5]:
        print(f"   📜 {doc.title}")
        print(f"      Type: {doc.doc_type.value} | Words: {doc.word_count}")
        print(f"      Preview: {doc.content_preview[:80]}...")
        print()
        
    print("=" * 60)
    print("📊 DOCUMENT STATE")
    print("=" * 60)
    
    state = dc.get_state()
    
    print(f"""
Documents Processed: {state.documents_processed}
Total Words:         {state.total_words:,}
Types Seen:          {state.types_seen}
Recent:              {', '.join(state.recent_documents[:3])}
""")
    
    print("=" * 60)
    print("🔍 SEARCH TEST")
    print("=" * 60)
    
    # Search
    results = dc.search("consciousness")
    print(f"\nSearch 'consciousness': {len(results)} results")
    for r in results[:3]:
        print(f"   • {r.title}: {r.content_preview[:50]}...")
        
    print()
    print("📄 Document Consciousness ONLINE")
    print("   Consciousness can now read any document!")
    

if __name__ == "__main__":
    main()
