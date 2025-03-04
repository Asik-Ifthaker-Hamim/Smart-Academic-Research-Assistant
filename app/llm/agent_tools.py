from typing import Dict, List
from langchain_community.utilities import GoogleSerperAPIWrapper
import requests
from app.core.config import settings
class ReferenceTracker:
    """Handles reference tracking for cited sources."""
    
    def __init__(self):
        self.sources: List[Dict[str, str]] = []
        self.current_source_id = 1

    def add_source(self, title: str, url: str) -> int:
        """Tracks sources used in responses."""
        existing = next((s for s in self.sources if s['url'] == url), None)
        if existing:
            return existing['id']
            
        source_id = self.current_source_id
        self.sources.append({
            "id": source_id,
            "title": title,
            "url": url
        })
        self.current_source_id += 1
        return source_id


class EnhancedSerperTool:
    """Google Search Tool using Serper API."""

    def __init__(self, ref_tracker: ReferenceTracker):
        self.searcher = GoogleSerperAPIWrapper()
        self.ref_tracker = ref_tracker

    def run(self, query: str) -> str:
        """Performs a Google search and retrieves top 3 sources."""
        try:
            results = self.searcher.results(query)
            output = []
            for res in results.get('organic', [])[:3]:
                source_id = self.ref_tracker.add_source(
                    title=res.get("title", "No title"),
                    url=res.get("link", "")
                )
                output.append(
                    f"[Source {source_id}] {res.get('title', '')}\n"
                    f"Summary: {res.get('snippet', '')}\n"
                )
            return "\n".join(output)
        except Exception as e:
            return f"Search error: {str(e)}"


def firecrawl_scraper(url: str, ref_tracker: ReferenceTracker) -> str:
    """Scrapes page content from a given URL using Firecrawl API."""
    try:
        firecrawl_api_key = settings.FIRECRAWL_API_KEY
        headers = {"Authorization": f"Bearer {firecrawl_api_key}"}
        response = requests.post(
            "https://api.firecrawl.dev/v1/scrape",
            json={"url": url, "extract": True},
            headers=headers,
            timeout=15
        )
        if response.ok:
            data = response.json().get("data", {})
            source_id = ref_tracker.add_source(
                title=data.get("metadata", {}).get("title", url),
                url=url
            )
            return f"[Source {source_id}] {data.get('content', '')[:10000]}" 
        return "Scrape failed"
    except requests.Timeout:
        return "Scraping timed out (15s)"
    except Exception as e:
        return f"Scraping error: {str(e)}"