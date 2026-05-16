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

import httpx

from app.settings import settings

log = logging.getLogger(__name__)

ACTIONBOOK_API_BASE = "https://api.actionbook.dev/v1"


async def live_etsy_search(query: str) -> dict:
    """Run an Etsy search via Actionbook. Returns:
    { "session_id": str, "screenshot_url": str | None, "listings": [ {title, price, url, sold_count} ] }

    Falls back to cached scrape on error OR when USE_FIXTURES=true.
    """
    cache_path = settings.cached_scrapes_dir / f"etsy_{_slug(query)}.json"

    if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
        log.info("actionbook.etsy.fixture", extra={"query": query})
        return _load_cache(cache_path)

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
        return _load_cache(cache_path)


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


def _load_cache(path: Path) -> dict:
    if not path.exists():
        log.warning("actionbook.cache_missing", extra={"path": str(path)})
        return {"session_id": "missing", "screenshot_url": None, "listings": []}
    return json.loads(path.read_text())
