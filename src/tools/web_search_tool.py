"""
Web Search Tool — lets agents search the web for current information.

Used by agents to:
  - Research similar products and competitors
  - Look up current tech stack benchmarks
  - Find best practices and design patterns
  - Verify technology recommendations with real data

Uses Bing Search API (available through Azure) for web results.
Falls back to a simulated response if the API is not configured,
so the system works without it (just less informed).
"""

import os
from typing import Optional

import httpx
from autogen_core.tools import FunctionTool


async def search_web(query: str) -> str:
    """
    Search the web and return top results as a summary.

    Use this tool when you need current, real-world information such as:
    - Technology comparisons and benchmarks
    - Library popularity and community size
    - Best practices for specific tech stacks
    - Competitor analysis and market research

    Args:
        query: The search query (e.g., "React vs Svelte 2026 performance comparison")

    Returns:
        A text summary of the top search results
    """
    api_key = os.getenv("BING_SEARCH_API_KEY", "")

    if not api_key:
        return (
            f"[Web search unavailable — BING_SEARCH_API_KEY not configured] "
            f"Proceeding with built-in knowledge for query: '{query}'"
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.bing.microsoft.com/v7.0/search",
                headers={"Ocp-Apim-Subscription-Key": api_key},
                params={"q": query, "count": 5, "responseFilter": "Webpages"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

        results = []
        for page in data.get("webPages", {}).get("value", []):
            results.append(f"**{page['name']}**\n{page['snippet']}\nSource: {page['url']}\n")

        if not results:
            return f"No results found for: '{query}'"

        return f"Search results for '{query}':\n\n" + "\n---\n".join(results)

    except Exception as e:
        return f"[Web search failed: {e}] Proceeding with built-in knowledge for query: '{query}'"


# Create the AutoGen-compatible tool
web_search = FunctionTool(
    search_web,
    name="search_web",
    description=(
        "Search the web for current information about technologies, benchmarks, "
        "best practices, competitors, or market research. Use this to ground your "
        "recommendations in real, up-to-date data."
    ),
)
