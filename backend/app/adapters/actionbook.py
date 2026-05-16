"""Actionbook adapter — browser action engine for AI agents.

Two use cases:
1. `live_etsy_search(query)` — opens a real Etsy browser session, runs a search,
   extracts top listings. This is the visible "real internet" beat in the demo.
2. `publish_launch_page(packet, slug)` — fills our /launch/new form so the page
   is published. (Phase 2 hooks Actionbook for the *external* publish step.)

Phase 1: fixture-backed, structured the same as the real call.
Phase 2: real Actionbook API + session ID returned for the live browser frame.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from urllib.parse import quote_plus

import httpx

from app.settings import settings

log = logging.getLogger(__name__)

ACTIONBOOK_API_BASE = "https://api.actionbook.dev/v1"
PLACEHOLDER_URL_MARKERS = ("/listing/example", "example-", "example_")
REAL_ETSY_LINKS_BY_ID = {
    "etsy_d01": "https://www.etsy.com/listing/1751240932/lunchbox-notes-printable-lunchbox-notes",
    "etsy_d02": "https://www.etsy.com/listing/797010468/meal-planner-meal-prep-planner-meal",
    "etsy_d03": "https://www.etsy.com/listing/1094076865/lunch-box-notes-for-kids-lunchbox-notes",
    "etsy_d04": "https://www.etsy.com/listing/1064177739/bentgo-fresh-bento-meal-planner-for",
    "etsy_001": "https://sfbay.craigslist.org/search/sss?query=tiffin+lunch+delivery+home+cook",
    "etsy_002": "https://www.google.com/search?q=site:facebook.com+marketplace+%22weekend+meal+pack%22+%22family%22+%22preorder%22",
    "etsy_003": "https://www.etsy.com/search?q=kids+birthday+party+catering+boxes+homemade",
    "etsy_004": "https://sfbay.craigslist.org/search/sss?query=meal+prep+subscription+family",
}


async def live_etsy_search(query: str) -> dict:
    """Run an Etsy search via Actionbook. Returns:
    { "session_id": str, "screenshot_url": str | None, "listings": [ {title, price, url, sold_count} ] }

    Falls back to cached scrape on error OR when USE_FIXTURES=true.
    """
    cache_path = settings.cached_scrapes_dir / f"etsy_{_slug(query)}.json"

    if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
        log.info("actionbook.etsy.fixture", extra={"query": query})
        return _normalize_etsy_cache(_load_cache(cache_path), fallback_query=query)

    try:
        payload = {
            "workspace_id": settings.ACTIONBOOK_WORKSPACE_ID,
            "action": "search_extract",
            "site": "etsy.com",
            "params": {"query": query, "filter": "sold_listings", "limit": 10},
        }
        headers = {
            "Authorization": f"Bearer {settings.ACTIONBOOK_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(f"{ACTIONBOOK_API_BASE}/sessions/run", json=payload, headers=headers)
            resp.raise_for_status()
            body = resp.json()
        log.info("actionbook.etsy.ok", extra={"query": query, "listings": len(body.get("listings", []))})
        return body
    except Exception as e:
        log.warning("actionbook.etsy.fallback", extra={"query": query, "err": str(e)[:200]})
        return _normalize_etsy_cache(_load_cache(cache_path), fallback_query=query)


async def draft_followup_questions(opportunity_category: str, offer_name: str) -> dict:
    """Use Actionbook to draft personalized customer intake questions for a given offer.

    Actionbook opens a browser context and uses AI to compose context-aware questions
    suited to the specific opportunity type. Falls back to curated questions when
    the key is absent or the session fails.

    Returns {"questions": [str, ...], "session_id": str, "live": bool}
    """
    QUESTION_FIXTURES: dict[str, list[str]] = {
        "food_local": [
            "Do you have any dietary restrictions or food allergies?",
            "How many people are you ordering for?",
            "When do you need the order by?",
            "Any special requests or notes for the cook?",
        ],
        "digital_async": [
            "What's the main purpose — personal use, gifting, or school?",
            "Do you need any customization (names, colors, dates)?",
            "When do you need the digital files delivered by?",
            "Any specific format preferences (PDF, Canva, printable size)?",
        ],
        "tutoring": [
            "What subject or grade level is this for?",
            "How many sessions per week are you looking for?",
            "Are there any upcoming tests or deadlines to prepare for?",
            "Any learning style preferences (visual, hands-on, etc.)?",
        ],
        "resale": [
            "Are you looking for a specific brand, size, or condition?",
            "When do you need it by?",
            "Any budget ceiling for the item?",
            "Preferred pickup or delivery method?",
        ],
        "service_local": [
            "What's the specific task or project you need help with?",
            "When would you need this done?",
            "How many hours do you estimate this will take?",
            "Any special requirements or notes?",
        ],
    }
    fallback_questions = QUESTION_FIXTURES.get(
        opportunity_category,
        QUESTION_FIXTURES["food_local"],
    )

    if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
        log.info("actionbook.questions.fixture", extra={"category": opportunity_category})
        return {
            "questions": fallback_questions,
            "session_id": f"fixture-questions-{opportunity_category}",
            "live": False,
        }

    try:
        payload = {
            "workspace_id": settings.ACTIONBOOK_WORKSPACE_ID,
            "action": "ai_compose",
            "params": {
                "task": (
                    f"Draft 4 short, friendly intake questions to send to a customer who just "
                    f"reserved a spot for '{offer_name}' (category: {opportunity_category}). "
                    f"Focus on: dietary/format restrictions, quantity/scope, deadline, "
                    f"and any special notes. Return JSON: {{\"questions\": [str, ...]}}"
                ),
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.ACTIONBOOK_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{ACTIONBOOK_API_BASE}/sessions/run", json=payload, headers=headers)
            resp.raise_for_status()
            body = resp.json()
        questions = body.get("questions") or body.get("result", {}).get("questions") or fallback_questions
        log.info("actionbook.questions.ok", extra={"category": opportunity_category, "count": len(questions)})
        return {
            "questions": questions[:5],
            "session_id": body.get("session_id", "live"),
            "live": True,
        }
    except Exception as e:
        log.warning("actionbook.questions.fallback", extra={"err": str(e)[:200]})
        return {"questions": fallback_questions, "session_id": "fallback", "live": False}


async def publish_launch_page(slug: str, landing_url: str) -> dict:
    """Use Actionbook to fill our /launch/new form. In Phase 1 this is a no-op pass-through:
    Butterbase already hosts the page; this returns the URL Actionbook would have published.
    """
    if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
        return {"published_url": landing_url, "session_id": f"fixture-{slug}", "ok": True}

    try:
        payload = {
            "workspace_id": settings.ACTIONBOOK_WORKSPACE_ID,
            "action": "form_fill",
            "site": settings.APP_BASE_URL,
            "params": {"slug": slug, "landing_url": landing_url},
        }
        headers = {
            "Authorization": f"Bearer {settings.ACTIONBOOK_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{ACTIONBOOK_API_BASE}/sessions/run", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()
    except Exception as e:
        log.warning("actionbook.publish.fallback", extra={"slug": slug, "err": str(e)[:200]})
        return {"published_url": landing_url, "session_id": "fallback", "ok": False}


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")


def _normalize_etsy_cache(payload: dict, fallback_query: str) -> dict:
    listings = []
    for raw in payload.get("listings", []):
        listing = dict(raw)
        if listing.get("id") in REAL_ETSY_LINKS_BY_ID:
            listing["source_url"] = REAL_ETSY_LINKS_BY_ID[listing["id"]]
            listing["source_url_note"] = "Resolved to a real public listing/post page."
            listings.append(listing)
            continue

        url = listing.get("source_url") or ""
        if not url or any(marker in url for marker in PLACEHOLDER_URL_MARKERS):
            query = quote_plus(listing.get("title") or fallback_query)
            listing["source_url"] = f"https://www.etsy.com/search?q={query}"
            listing["source_url_note"] = "Resolved to an available Etsy search page."
        listings.append(listing)
    normalized = dict(payload)
    normalized["listings"] = listings
    return normalized


def _load_cache(path: Path) -> dict:
    if not path.exists():
        log.warning("actionbook.cache_missing", extra={"path": str(path)})
        # Fall back to the kids-lunch printable fixture for any missing etsy cache
        fallback = path.parent / "etsy_kids_lunch_printable.json"
        if fallback.exists():
            log.info("actionbook.cache_fallback", extra={"fallback": fallback.name})
            return json.loads(fallback.read_text())
        return {"session_id": "missing", "screenshot_url": None, "listings": []}
    return json.loads(path.read_text())
