"""Tavily adapter — real live web search.

Used as a free stand-in for Bright Data today. The instant we have a Bright Data
zone tomorrow, the calling adapters (`bright_data.py`) just swap to the BD path.

Tavily is purpose-built for AI agents: returns clean JSON with title/url/content/score
instead of raw HTML, which means we don't need a separate HTML-parse pass.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from app.settings import settings

log = logging.getLogger(__name__)


def is_configured() -> bool:
    return bool(settings.TAVILY_API_KEY)


async def search(query: str, max_results: int = 5, search_depth: str = "basic") -> dict[str, Any]:
    """Live Tavily web search.

    Returns: {"query": str, "results": [{"title", "url", "content", "score"}], "answer": str | None}
    Raises on error (caller should fall back to fixtures).
    """
    if not settings.TAVILY_API_KEY:
        raise RuntimeError("TAVILY_API_KEY not set")

    from tavily import TavilyClient  # type: ignore

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    def _do() -> dict[str, Any]:
        return client.search(
            query=query,
            max_results=max_results,
            search_depth=search_depth,
            include_answer=True,
        )

    log.info("tavily.search", extra={"query": query, "max": max_results})
    result = await asyncio.to_thread(_do)
    log.info("tavily.ok", extra={"count": len(result.get("results", []))})
    return result


async def search_state_law(state: str) -> dict[str, Any]:
    """Specialized: find the live state cottage-food page.
    Returns a citation-shaped dict matching what bright_data.scrape_state_law returns,
    so callers can swap without rewrite.
    """
    state = state.upper()
    state_name = _state_to_name(state)
    query = (
        f"{state_name} cottage food law requirements permit "
        f"potentially hazardous food daily meal delivery"
    )
    result = await search(query, max_results=3, search_depth="advanced")

    # Pick the top .gov result if available, else the first
    gov_results = [r for r in result.get("results", []) if ".gov" in r.get("url", "")]
    top = gov_results[0] if gov_results else (result.get("results") or [{}])[0]

    # Tavily's "answer" field is a synthesized summary — perfect for citation_text
    citation_text = result.get("answer") or top.get("content", "")[:600]

    return {
        "source_url": top.get("url", ""),
        "state": state,
        "citation_text": citation_text,
        "live_scrape_ok": True,
        "live_scrape_provider": "tavily",
        # We still flag potentially-hazardous foods as needing a permit — that's universal across states
        "requires_permit_for_hot_food": True,
        "raw_top_results": [
            {"title": r.get("title"), "url": r.get("url"), "score": r.get("score")}
            for r in result.get("results", [])[:3]
        ],
    }


async def search_revenue_benchmarks(persona_category_hint: str, state: str = "") -> dict[str, Any]:
    """Real web search for income-benchmark data backing the revenue estimates.

    Used by Market Scout to ground its ranking in REAL published numbers (Etsy seller
    revenue reports, cottage-food shop revenue, freelance tutoring rates, etc.) instead
    of letting Gemini hallucinate a $/mo figure from thin air.

    Returns the same Tavily envelope: { results: [...], answer: str }. Caller picks
    the 1-3 strongest results and feeds them to Gemini as grounding evidence.
    """
    geo = f" in {_state_to_name(state.upper())}" if state else ""
    query = (
        f"average monthly revenue {persona_category_hint} side income working mom 2025{geo} "
        f"earnings benchmark survey data report"
    )
    return await search(query, max_results=5, search_depth="advanced")


_STATE_NAMES = {
    "CA": "California", "TX": "Texas", "NY": "New York", "FL": "Florida",
    "IL": "Illinois", "PA": "Pennsylvania", "OH": "Ohio", "GA": "Georgia",
    "NC": "North Carolina", "MI": "Michigan", "NJ": "New Jersey",
    "VA": "Virginia", "WA": "Washington", "AZ": "Arizona", "MA": "Massachusetts",
}


def _state_to_name(code: str) -> str:
    return _STATE_NAMES.get(code.upper(), code)
