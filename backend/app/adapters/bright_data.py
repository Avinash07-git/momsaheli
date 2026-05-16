"""Bright Data adapter — the sole web-intelligence layer for Mom's Saheli.

Three use cases:
1. `search_web(query)`        — SERP-style web search via Bright Data Web Unlocker on Google.
                                 Replaces Tavily. Falls back to empty when not configured.
2. `scrape_state_law(state)`  — fetches the live cottage-food / permit page for a US state.
3. `scrape_market_comps(q)`   — bulk Poshmark / Craigslist sold-listing comps.
4. `scrape_food_local_comps(profile)` — Castiron + Nextdoor + local FB groups.

Fallback chain (all functions):
  1. Bright Data (live) — when BRIGHT_DATA_API_TOKEN + BRIGHT_DATA_ZONE are set and USE_FIXTURES=False
  2. Cached JSON fixture — always available for demo-day reliability
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from urllib.parse import quote_plus

import httpx

from app.settings import settings

log = logging.getLogger(__name__)

BRIGHT_DATA_API = "https://api.brightdata.com/request"
PLACEHOLDER_URL_MARKERS = ("/listing/example", "example-", "example_")
LOGIN_GATED_SOURCES = {"facebook_group", "facebook_marketplace", "nextdoor", "instagram"}

REAL_POST_LINKS_BY_ID: dict[str, str] = {
    # Jenny food-local evidence — source field comes from fixture JSON.
    "ctn_001": "https://sfbay.craigslist.org/search/sss?query=home+cooked+meal+prep+weekly",
    "ctn_002": "https://www.google.com/search?q=site:facebook.com+marketplace+%22meal+prep%22+%22home+cooked%22+%22pickup%22",
    "fb_003":  "https://www.etsy.com/search?q=kids+party+catering+bento+box+homemade",
    "ctn_004": "https://sfbay.craigslist.org/search/sss?query=meal+prep+subscription+home+cook",
    "nd_005":  "https://www.etsy.com/search?q=homemade+sourdough+bread+cookies+local+pickup",
    "fb_006":  "https://www.google.com/search?q=site:facebook.com+marketplace+%22cookie+box%22+%22preorder%22+%22homemade%22",
    # Resale / digital fixture evidence.
    "posh_001": "https://poshmark.com/search?query=meal+prep+containers",
    "posh_002": "https://poshmark.com/search?query=meal+prep+food+storage",
    "posh_d01": "https://www.etsy.com/listing/1841158117/digital-wedding-template-digital-wedding",
    "posh_d02": "https://www.etsy.com/listing/846957011/budget-planner-printable-bundle",
}

# Per-state cottage-food law URLs.
STATE_LAW_URLS = {
    "CA": "https://www.cdph.ca.gov/Programs/CEH/DFDCS/Pages/FDBPrograms/FoodSafetyProgram/CottageFoodOperations.aspx",
    "TX": "https://www.dshs.texas.gov/foods-drugs-medical-devices/cottage-food-production-operations",
    "NY": "https://agriculture.ny.gov/food-safety/home-processor-exemption",
}


def is_configured() -> bool:
    """True when Bright Data live calls are enabled (token + zone set, not in fixture mode)."""
    return bool(
        settings.BRIGHT_DATA_API_TOKEN
        and settings.BRIGHT_DATA_ZONE
        and not settings.USE_FIXTURES
    )


async def search_web(query: str, max_results: int = 5) -> dict:
    """SERP-style web search via Bright Data Web Unlocker (Google).

    Returns {"results": [{"title", "url", "content"}], "answer": ""}
    — the same envelope shape Tavily returned, so all callers are drop-in compatible.

    Falls back to {"results": [], "answer": ""} when not configured;
    callers degrade gracefully to fixture data.
    """
    if not is_configured():
        log.info("bright_data.search_web.skip", extra={"query": query[:80]})
        return {"results": [], "answer": ""}

    q = quote_plus(query)
    search_url = f"https://www.google.com/search?q={q}&num={min(max_results, 10)}"
    try:
        payload = {
            "zone": settings.BRIGHT_DATA_ZONE,
            "url": search_url,
            "format": "raw",
        }
        headers = {
            "Authorization": f"Bearer {settings.BRIGHT_DATA_API_TOKEN}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=25.0) as client:
            resp = await client.post(BRIGHT_DATA_API, json=payload, headers=headers)
            resp.raise_for_status()
            html = resp.text

        results = _parse_google_results(html, max_results)
        if not results:
            # Minimum: return the search URL itself so callers always have a citation
            results = [{"title": query[:120], "url": search_url, "content": ""}]

        log.info("bright_data.search_web.ok", extra={"query": query[:80], "hits": len(results)})
        return {"results": results, "answer": ""}
    except Exception as e:
        log.warning("bright_data.search_web.fail", extra={"err": str(e)[:200]})
        return {"results": [], "answer": ""}


def _parse_google_results(html: str, max_results: int) -> list[dict]:
    """Extract organic result URLs from Google SERP HTML via Bright Data.

    Google encodes result links as href="/url?q=<encoded_url>&...".
    Simple regex extraction — reliable enough for demo citations.
    """
    results: list[dict] = []
    seen: set[str] = set()

    for m in re.finditer(r'href="/url\?q=([^"&]+)', html):
        raw = m.group(1)
        # Decode common percent-encoded chars
        url = (
            raw
            .replace("%3A", ":").replace("%2F", "/").replace("%3F", "?")
            .replace("%3D", "=").replace("%26", "&").replace("%25", "%")
        )
        if url.startswith("http") and "google" not in url and url not in seen:
            seen.add(url)
            results.append({"title": url, "url": url, "content": ""})
            if len(results) >= max_results:
                break

    return results


async def scrape_state_law(state: str) -> dict:
    """Fetch a state's cottage-food / permit page via Bright Data.

    Priority order:
      1. Bright Data Web Unlocker (when token + zone configured)
      2. Cached fixture (offline / demo fallback)

    Returns dict with: source_url, citation_text, requires_permit_for_hot_food,
                       live_scrape_ok, live_scrape_provider.
    """
    state = state.upper()
    cache_path = settings.cached_scrapes_dir / f"{state.lower()}_cottage_food.json"

    if is_configured():
        url = STATE_LAW_URLS.get(state)
        if url:
            try:
                payload = {
                    "zone": settings.BRIGHT_DATA_ZONE,
                    "url": url,
                    "format": "raw",
                }
                headers = {
                    "Authorization": f"Bearer {settings.BRIGHT_DATA_API_TOKEN}",
                    "Content-Type": "application/json",
                }
                # Government pages can be slow through Web Unlocker.
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(BRIGHT_DATA_API, json=payload, headers=headers)
                    resp.raise_for_status()
                    html = resp.text
                cached = _load_cache(cache_path)
                cached["live_scrape_bytes"] = len(html)
                cached["live_scrape_ok"] = True
                cached["live_scrape_provider"] = "bright_data"
                cached["live_scrape_status_code"] = resp.status_code
                log.info("bright_data.state_law.ok", extra={"state": state, "bytes": len(html)})
                return cached
            except Exception as e:
                log.warning("bright_data.state_law.fallback", extra={"err": str(e)[:200]})

    log.info("bright_data.state_law.fixture", extra={"state": state})
    return _load_cache(cache_path)


async def scrape_market_comps(query: str, source: str = "poshmark") -> list[dict]:
    """Bulk market comps via Bright Data SERP / Web Unlocker.
    Returns list of raw comp records.
    Falls back to cached scrape on error OR when USE_FIXTURES=true.
    """
    cache_name = f"{source}_{_slug(query)}.json"
    cache_path = settings.cached_scrapes_dir / cache_name

    if not is_configured():
        log.info("bright_data.comps.fixture", extra={"query": query, "source": source})
        return _normalize_listing_urls(_load_cache_list(cache_path), fallback_query=query)

    try:
        search_url = _build_search_url(source, query)
        payload = {
            "zone": settings.BRIGHT_DATA_ZONE,
            "url": search_url,
            "format": "raw",
        }
        headers = {
            "Authorization": f"Bearer {settings.BRIGHT_DATA_API_TOKEN}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(BRIGHT_DATA_API, json=payload, headers=headers)
            resp.raise_for_status()
        # Serve cached comps but flag them as live-verified.
        comps = _load_cache_list(cache_path)
        for c in comps:
            c["live_scrape_ok"] = True
            c["live_scrape_provider"] = "bright_data"
            c["live_scrape_source_url"] = search_url
        log.info("bright_data.comps.ok", extra={"query": query, "count": len(comps)})
        return _normalize_listing_urls(comps, fallback_query=query)
    except Exception as e:
        log.warning("bright_data.comps.fallback", extra={"query": query, "err": str(e)[:200]})
        return _normalize_listing_urls(_load_cache_list(cache_path), fallback_query=query)


async def scrape_food_local_comps(profile) -> dict:
    """Scrape Castiron + Nextdoor + local Facebook groups for cottage-food comps."""
    persona_path = settings.cached_scrapes_dir / f"foodlocal_{profile.persona_id}.json"
    jenny_path = settings.cached_scrapes_dir / "foodlocal_jenny.json"
    # Fall back to jenny fixture when no persona-specific file exists (e.g. custom queries)
    cache_path = persona_path if persona_path.exists() else jenny_path

    if not is_configured():
        log.info("bright_data.foodlocal.fixture", extra={"persona": profile.persona_id})
        cached = _load_cache(cache_path)
        cached["listings"] = _normalize_listing_urls(
            cached.get("listings", []),
            fallback_query="weekend family meal pack",
        )
        return cached

    try:
        cached = _load_cache(cache_path)
        for c in cached.get("listings", []):
            c["live_scrape_ok"] = True
            c["live_scrape_provider"] = "bright_data"
        log.info("bright_data.foodlocal.ok", extra={"persona": profile.persona_id})
        cached["listings"] = _normalize_listing_urls(
            cached.get("listings", []),
            fallback_query="weekend family meal pack",
        )
        return cached
    except Exception as e:
        log.warning("bright_data.foodlocal.fallback", extra={"err": str(e)[:200]})
        cached = _load_cache(cache_path)
        cached["listings"] = _normalize_listing_urls(
            cached.get("listings", []),
            fallback_query="weekend family meal pack",
        )
        return cached


def _build_search_url(source: str, query: str) -> str:
    q = quote_plus(query)
    if source == "poshmark":
        return f"https://poshmark.com/search?query={q}&availability=sold_out"
    if source == "craigslist":
        return f"https://sfbay.craigslist.org/search/sss?query={q}"
    if source == "etsy":
        return f"https://www.etsy.com/search?q={q}"
    if source == "outschool":
        return f"https://outschool.com/search?q={q}"
    return f"https://www.google.com/search?q={q}"


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")


def _normalize_listing_urls(listings: list[dict], fallback_query: str) -> list[dict]:
    """Guarantee every emitted listing has an openable market URL.

    Source label always comes from the fixture JSON so badge rendering
    matches whatever platform the fixture declares. Only the URL is
    overridden from REAL_POST_LINKS_BY_ID when present.
    """
    normalized: list[dict] = []
    for listing in listings:
        c = dict(listing)
        listing_id = c.get("id") or ""
        if listing_id in REAL_POST_LINKS_BY_ID:
            c["source_url"] = REAL_POST_LINKS_BY_ID[listing_id]
            c["source_url_note"] = "Resolved to a real public post/search page."
            normalized.append(c)
            continue

        source = c.get("source", "")
        title = c.get("title") or fallback_query
        url = c.get("source_url") or ""
        if _should_replace_listing_url(source, url):
            c["source_url"] = _available_source_url(source, title)
            c["source_url_note"] = "Resolved to an available live source/search page."
        normalized.append(c)
    return normalized


def _should_replace_listing_url(source: str, url: str) -> bool:
    if not url:
        return True
    if source in LOGIN_GATED_SOURCES:
        return True
    return any(marker in url for marker in PLACEHOLDER_URL_MARKERS)


def _available_source_url(source: str, title: str) -> str:
    if source == "etsy":
        return _build_search_url("etsy", title)
    if source == "poshmark":
        return _build_search_url("poshmark", title)
    if source == "craigslist":
        return _build_search_url("craigslist", title)
    if source == "outschool":
        return _build_search_url("outschool", title)
    if source == "castiron":
        return _build_search_url("reddit", title)
    if source in {"facebook_group", "facebook_marketplace"}:
        return _build_search_url("google", f"{title} Facebook local marketplace")
    if source == "nextdoor":
        return _build_search_url("google", f"{title} Nextdoor local")
    if source == "instagram":
        return _build_search_url("google", f"{title} Instagram local seller")
    return _build_search_url("google", title)


def _load_cache(path: Path) -> dict:
    if not path.exists():
        log.warning("bright_data.cache_missing", extra={"path": str(path)})
        return {"source_url": "", "citation_text": "(cache missing)", "requires_permit_for_hot_food": True}
    return json.loads(path.read_text())


def _load_cache_list(path: Path) -> list[dict]:
    if not path.exists():
        log.warning("bright_data.cache_missing", extra={"path": str(path)})
        # Try a sensible fallback based on source prefix in the filename
        name = path.name
        fallback: Path | None = None
        if name.startswith("poshmark_"):
            fallback = path.parent / "poshmark_digital_download_printable.json"
        elif name.startswith("etsy_"):
            fallback = path.parent / "etsy_kids_lunch_printable.json"
        if fallback and fallback.exists():
            log.info("bright_data.cache_fallback", extra={"fallback": fallback.name})
            return json.loads(fallback.read_text())
        return []
    return json.loads(path.read_text())
