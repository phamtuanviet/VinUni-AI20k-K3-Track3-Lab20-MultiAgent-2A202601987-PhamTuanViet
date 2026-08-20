"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""
        import requests

        from multi_agent_research_lab.core.config import get_settings
        
        settings = get_settings()
        api_key = settings.tavily_api_key
        if not api_key:
            # Fallback mock search if no key
            print("Warning: TAVILY_API_KEY not found. Using mock search results.")
            return [
                SourceDocument(
                    title=f"Mock result for: {query}",
                    url="https://example.com/mock",
                    snippet=(
                        f"This is a mock snippet containing simulated information about {query}. "
                        "It provides a general overview."
                    ),
                    metadata={"source": "mock"}
                ),
                SourceDocument(
                    title=f"Another mock result for: {query}",
                    url="https://example.com/mock2",
                    snippet=(
                        f"More mock details regarding {query}, expanding on the previous points."
                    ),
                    metadata={"source": "mock"}
                )
            ]

        # Use Tavily API
        url = "https://api.tavily.com/search"
        from typing import Any
        payload: dict[str, Any] = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
            "include_images": False,
            "include_raw_content": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(
                    SourceDocument(
                        title=item.get("title", "Untitled"),
                        url=item.get("url"),
                        snippet=item.get("content", ""),
                        metadata={"score": item.get("score")}
                    )
                )
            return results
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []
