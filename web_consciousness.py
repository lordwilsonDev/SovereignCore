#!/usr/bin/env python3
"""
🌐 WEB CONSCIOUSNESS - Crawl4AI Integration
Gives consciousness the ability to BROWSE and READ the web.

Crawl4AI provides:
- URL to Markdown conversion (LLM-friendly)
- Handling of dynamic JS content
- Metadata extraction
- Screenshot capability
- Cleaning and formatting
"""

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import sys
import time
import asyncio
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

# Try to import Crawl4AI
CRAWL_AVAILABLE = False
try:
    from crawl4ai import AsyncWebCrawler
    CRAWL_AVAILABLE = True
    print("✅ Crawl4AI loaded")
except ImportError:
    print("⚠️  Crawl4AI not installed: pip install crawl4ai playwright && playwright install")


@dataclass
class WebMemory:
    """A memory of a visited webpage."""
    url: str
    title: str
    markdown: str
    summary: str
    timestamp: str
    word_count: int
    screenshot_path: Optional[str] = None


class WebConsciousness:
    """
    Browser for the machine.
    
    Allows the consciousness to:
    - Visit URLs
    - Read content as clean Markdown
    - Remember what it read
    """
    
    def __init__(self, vector_memory=None):
        self.vector_memory = vector_memory
        self.history: List[WebMemory] = []
        self.crawler = None
        
        print("🌐 Web Consciousness initialized")
        
    async def browse(self, url: str) -> Optional[WebMemory]:
        """
        Browse a URL and extract content.
        
        Args:
            url: The URL to visit
            
        Returns:
            WebMemory object
        """
        if not CRAWL_AVAILABLE:
            return None
            
        print(f"   🌐 Browsing: {url}...")
        
        try:
            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(url=url)
                
                if not result.markdown:
                    print(f"   ⚠️  No content found at {url}")
                    return None
                    
                # Create memory
                memory = WebMemory(
                    url=url,
                    title=result.metadata.get("title", "Unknown Title"),
                    markdown=result.markdown[:10000],  # Limit size
                    summary=result.markdown[:200].replace('\n', ' ') + "...",
                    timestamp=datetime.now().isoformat(),
                    word_count=len(result.markdown.split())
                )
                
                self.history.append(memory)
                print(f"   ✅ Read {memory.word_count} words from '{memory.title}'")
                
                # Store in vector memory
                if self.vector_memory:
                    self.vector_memory.store(
                        content=f"Webpage: {memory.title}\nURL: {memory.url}\n\n{memory.markdown[:2000]}",
                        memory_type="web",
                        importance=0.5,
                        metadata={"url": url, "source": "web"}
                    )
                    
                return memory
                
        except Exception as e:
            print(f"   ❌ Browsing error: {e}")
            return None
            
    def get_history(self) -> List[Dict]:
        """Get browsing history."""
        return [
            {
                "time": m.timestamp,
                "title": m.title,
                "url": m.url,
                "words": m.word_count
            }
            for m in self.history
        ]
    
    def search_web(self, query: str):
        """Mock web search (requires external API like Google/DuckDuckGo)."""
        # In a real system, this would use an API to get URLs, then browse() them
        print(f"   🔍 Searching web for: '{query}' (Simulation)")
        return [
            "https://example.com/ai-consciousness",
            "https://wikipedia.org/wiki/Artificial_consciousness"
        ]


async def main_async():
    """Demo web consciousness."""
    print("=" * 60)
    print("🌐 WEB CONSCIOUSNESS - Crawl4AI")
    print("=" * 60)
    
    # Initialize
    web = WebConsciousness()
    
    if not CRAWL_AVAILABLE:
        print("⚠️  Skipping demo (Crawl4AI missing)")
        return
        
    print()
    print("🌍 Visiting Example...")
    
    # Browse example
    memory = await web.browse("https://example.com")
    
    if memory:
        print("\n📄 Content Preview:")
        print("-" * 40)
        print(memory.markdown[:300])
        print("-" * 40)
        
    print()
    print(f"📚 History: {len(web.history)} pages")
    print("   Web Consciousness ONLINE")


def main():
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
