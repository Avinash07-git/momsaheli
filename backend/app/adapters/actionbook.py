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


async def execute_activation_action(action: dict, approved: bool, submit_or_post: bool = False) -> dict:
    """Execute an approval-gated activation action.

    This adapter never posts or submits unless:
      - the caller sends approved=true,
      - the action execution mode allows it,
      - Actionbook is configured,
      - and post actions also send submit_or_post=true.
    """
    action_id = str(action.get("id") or "unknown_action")
    execution_mode = action.get("execution_mode") or "draft_only"
    action_type = action.get("type") or "manual_step"

    if not approved:
        return {
            "action_id": action_id,
            "status": "blocked",
            "message": "Blocked: this action needs explicit user approval before anything is prepared.",
        }

    if execution_mode == "draft_only":
        return {
            "action_id": action_id,
            "status": "drafted",
            "message": "Draft marked ready. No external site was opened, posted to, or submitted.",
        }

    if execution_mode == "fill_no_submit":
        if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
            return {
                "action_id": action_id,
                "status": "filled",
                "message": (
                    "Preview only: Actionbook is not configured, so these fields were not filled "
                    "on an external site and nothing was submitted."
                ),
                "actionbook_session_id": f"preview-{action_id}",
            }
        return await _run_activation_actionbook(
            action=action,
            status_on_success="filled",
            submit_or_post=False,
            message_on_success="Actionbook filled a preview only. Nothing was submitted.",
        )

    if execution_mode == "post_after_review":
        if not submit_or_post:
            return {
                "action_id": action_id,
                "status": "blocked",
                "message": "Blocked: posting requires submit_or_post=true after reviewing the exact message.",
            }
        if settings.USE_FIXTURES or not settings.ACTIONBOOK_API_KEY:
            return {
                "action_id": action_id,
                "status": "drafted",
                "message": (
                    "Preview only: Actionbook is not configured, so the approved message was not posted "
                    "or submitted anywhere."
                ),
                "actionbook_session_id": f"preview-{action_id}",
            }
        return await _run_activation_actionbook(
            action=action,
            status_on_success="posted",
            submit_or_post=True,
            message_on_success="Actionbook executed only the approved post action.",
        )

    log.warning("actionbook.activation.unknown_mode", extra={"action_id": action_id, "mode": execution_mode})
    return {
        "action_id": action_id,
        "status": "blocked",
        "message": f"Blocked: unknown execution mode '{execution_mode}'.",
    }


async def _run_activation_actionbook(
    action: dict,
    status_on_success: str,
    submit_or_post: bool,
    message_on_success: str,
) -> dict:
    action_id = str(action.get("id") or "unknown_action")
    try:
        payload = {
            "workspace_id": settings.ACTIONBOOK_WORKSPACE_ID,
            "action": "activation_action",
            "params": {
                "action": action,
                "submit_or_post": submit_or_post,
                "safety": "No private scraping. No unapproved posting. No phone-number collection.",
            },
        }
        headers = {
            "Authorization": f"Bearer {settings.ACTIONBOOK_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{ACTIONBOOK_API_BASE}/sessions/run", json=payload, headers=headers)
            resp.raise_for_status()
            body = resp.json()
        return {
            "action_id": action_id,
            "status": status_on_success,
            "message": message_on_success,
            "proof_url": body.get("proof_url") or body.get("url"),
            "screenshot_url": body.get("screenshot_url"),
            "actionbook_session_id": body.get("session_id"),
        }
    except Exception as e:
        log.warning("actionbook.activation.failed", extra={"action_id": action_id, "err": str(e)[:200]})
        return {
            "action_id": action_id,
            "status": "failed",
            "message": "Actionbook execution failed before any confirmed external action completed.",
            "error": str(e)[:300],
        }


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")


def _load_cache(path: Path) -> dict:
    if not path.exists():
        log.warning("actionbook.cache_missing", extra={"path": str(path)})
        return {"session_id": "missing", "screenshot_url": None, "listings": []}
    return json.loads(path.read_text())
