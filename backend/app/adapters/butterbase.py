"""Butterbase adapter — product backend for Mom's Saheli.

We use Butterbase for two real things in Phase 1:
1. Persist every run summary (so /api/runs and the History screen work).
2. Persist published launch packets (so /launch/{slug} returns the right data).

Phase 1: in-memory dict keyed by slug + cached on disk for restart-resilience.
Phase 2: real Butterbase tables.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import httpx

from app.schemas import LaunchPacket, RunSummary
from app.settings import settings

log = logging.getLogger(__name__)

BUTTERBASE_API_BASE = "https://api.butterbase.ai/v1"

# Local mirror — survives process within the demo and acts as fallback if Butterbase is down.
_LOCAL_DIR = Path(__file__).resolve().parent.parent / "_local_store"
_LOCAL_DIR.mkdir(exist_ok=True)
_RUNS_FILE = _LOCAL_DIR / "runs.json"
_PAGES_DIR = _LOCAL_DIR / "pages"
_PAGES_DIR.mkdir(exist_ok=True)


# ----- Run history -----

async def save_run_summary(summary: RunSummary) -> bool:
    """Save a run summary. Returns True on success."""
    _append_run_locally(summary)

    if settings.USE_FIXTURES or not settings.BUTTERBASE_API_KEY:
        log.info("butterbase.run.local", extra={"run_id": summary.run_id})
        return True

    try:
        payload = {
            "project_id": settings.BUTTERBASE_PROJECT_ID,
            "table": "runs",
            "row": summary.model_dump(mode="json"),
        }
        headers = {
            "Authorization": f"Bearer {settings.BUTTERBASE_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{BUTTERBASE_API_BASE}/rows", json=payload, headers=headers)
            resp.raise_for_status()
        log.info("butterbase.run.ok", extra={"run_id": summary.run_id})
        return True
    except Exception as e:
        log.warning("butterbase.run.fallback", extra={"err": str(e)[:200]})
        return True  # local mirror still saved


async def list_runs(limit: int = 50) -> list[dict]:
    """Return runs, newest first."""
    if settings.USE_FIXTURES or not settings.BUTTERBASE_API_KEY:
        return _read_local_runs(limit)

    try:
        headers = {"Authorization": f"Bearer {settings.BUTTERBASE_API_KEY}"}
        params = {"project_id": settings.BUTTERBASE_PROJECT_ID, "table": "runs", "limit": limit, "order": "-created_at"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUTTERBASE_API_BASE}/rows", params=params, headers=headers)
            resp.raise_for_status()
            return resp.json().get("rows", [])
    except Exception as e:
        log.warning("butterbase.list.fallback", extra={"err": str(e)[:200]})
        return _read_local_runs(limit)


# ----- Launch page hosting -----

async def save_launch_page(slug: str, packet: LaunchPacket, display_name: str) -> str:
    """Persist a published launch packet by slug. Returns the public URL."""
    record = {
        "slug": slug,
        "display_name": display_name,
        "packet": packet.model_dump(mode="json"),
        "published_at": datetime.utcnow().isoformat(),
    }
    _save_page_locally(slug, record)

    public_url = f"{settings.APP_BASE_URL}/launch/{slug}"

    if settings.USE_FIXTURES or not settings.BUTTERBASE_API_KEY:
        log.info("butterbase.page.local", extra={"slug": slug})
        return public_url

    try:
        payload = {
            "project_id": settings.BUTTERBASE_PROJECT_ID,
            "table": "launch_pages",
            "row": record,
        }
        headers = {
            "Authorization": f"Bearer {settings.BUTTERBASE_API_KEY}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{BUTTERBASE_API_BASE}/rows", json=payload, headers=headers)
            resp.raise_for_status()
        log.info("butterbase.page.ok", extra={"slug": slug})
        return public_url
    except Exception as e:
        log.warning("butterbase.page.fallback", extra={"err": str(e)[:200]})
        return public_url


async def get_launch_page(slug: str) -> dict | None:
    """Look up a published page by slug."""
    local = _read_page_locally(slug)
    if local:
        return local

    if settings.USE_FIXTURES or not settings.BUTTERBASE_API_KEY:
        return None

    try:
        headers = {"Authorization": f"Bearer {settings.BUTTERBASE_API_KEY}"}
        params = {"project_id": settings.BUTTERBASE_PROJECT_ID, "table": "launch_pages", "filter": f"slug={slug}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{BUTTERBASE_API_BASE}/rows", params=params, headers=headers)
            resp.raise_for_status()
            rows = resp.json().get("rows", [])
            return rows[0] if rows else None
    except Exception as e:
        log.warning("butterbase.page.get.fallback", extra={"err": str(e)[:200]})
        return None


# ----- Local mirror helpers -----

def _append_run_locally(summary: RunSummary) -> None:
    runs = _read_local_runs(limit=1000)
    runs.insert(0, summary.model_dump(mode="json"))
    _RUNS_FILE.write_text(json.dumps(runs, default=str, indent=2))


def _read_local_runs(limit: int) -> list[dict]:
    if not _RUNS_FILE.exists():
        return []
    runs = json.loads(_RUNS_FILE.read_text())
    return runs[:limit]


def _save_page_locally(slug: str, record: dict) -> None:
    (_PAGES_DIR / f"{slug}.json").write_text(json.dumps(record, default=str, indent=2))


def _read_page_locally(slug: str) -> dict | None:
    p = _PAGES_DIR / f"{slug}.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())
