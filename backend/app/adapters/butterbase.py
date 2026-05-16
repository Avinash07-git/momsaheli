"""Butterbase adapter — product backend for Mom's Saheli.

Two persistence layers (defence in depth):
1. **Real Butterbase** via MCP (`insert_row` / `select_rows`) when BUTTERBASE_API_KEY
   and BUTTERBASE_PROJECT_ID are set. Hits Postgres tables `saheli_runs` and
   `saheli_launch_pages` defined in the app schema.
2. **Local mirror** — always written first as a safety net so the demo never
   loses a run even if Butterbase is briefly unavailable.

The local mirror also acts as the read source for `/launch/{slug}` so the
demo stays fast and offline-resilient.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import httpx

from app.schemas import LaunchPacket, RunSummary
from app.settings import settings

log = logging.getLogger(__name__)

BUTTERBASE_MCP_URL = "https://api.butterbase.ai/mcp"
_RUNS_TABLE = "saheli_runs"
_PAGES_TABLE = "saheli_launch_pages"
_LEADS_TABLE = "saheli_launch_leads"

# Local mirror — survives process restarts within the demo.
_LOCAL_DIR = Path(__file__).resolve().parent.parent / "_local_store"
_LOCAL_DIR.mkdir(exist_ok=True)
_RUNS_FILE = _LOCAL_DIR / "runs.json"
_PAGES_DIR = _LOCAL_DIR / "pages"
_PAGES_DIR.mkdir(exist_ok=True)
_LEADS_FILE = _LOCAL_DIR / "launch_leads.json"


# ─────────────────────────────────────────────────────────────────────────────
# MCP transport — Butterbase exposes its product backend as an MCP server,
# not a REST API. We speak JSON-RPC 2.0 over HTTP+SSE.
# ─────────────────────────────────────────────────────────────────────────────
_MCP_ID = 0


def _next_id() -> int:
    global _MCP_ID
    _MCP_ID += 1
    return _MCP_ID


async def _mcp_call(tool: str, arguments: dict[str, Any], timeout: float = 15.0) -> dict | None:
    """Call a Butterbase MCP tool. Returns the parsed result text as JSON, or None on error."""
    if not settings.BUTTERBASE_API_KEY:
        return None
    payload = {
        "jsonrpc": "2.0",
        "id": _next_id(),
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
    }
    headers = {
        "Authorization": f"Bearer {settings.BUTTERBASE_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(BUTTERBASE_MCP_URL, json=payload, headers=headers)
            resp.raise_for_status()
            body = resp.text
            if body.startswith("event:"):
                # SSE framing — pull the `data: ...` line.
                for line in body.splitlines():
                    if line.startswith("data: "):
                        body = line[len("data: "):]
                        break
            envelope = json.loads(body)
            if envelope.get("error") or envelope.get("result", {}).get("isError"):
                log.warning("butterbase.mcp.err", extra={"tool": tool, "body": body[:300]})
                return None
            text = envelope["result"]["content"][0]["text"]
            return json.loads(text)
    except Exception as e:
        log.warning("butterbase.mcp.fallback", extra={"tool": tool, "err": str(e)[:200]})
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Run history
# ─────────────────────────────────────────────────────────────────────────────
async def save_run_summary(summary: RunSummary) -> bool:
    _append_run_locally(summary)

    if not settings.BUTTERBASE_PROJECT_ID:
        log.info("butterbase.run.local_only", extra={"run_id": summary.run_id})
        return True

    row = summary.model_dump(mode="json")
    # Strip our internal id-shaped fields so they don't collide with Butterbase's auto `id`.
    bb_row = {
        "run_id": row["run_id"],
        "persona_display_name": row.get("persona_display_name"),
        "winner_offer_name": row.get("winner_offer_name"),
        "launch_url": row.get("launch_url"),
        "duration_ms": row.get("duration_ms"),
    }
    result = await _mcp_call("insert_row", {
        "app_id": settings.BUTTERBASE_PROJECT_ID,
        "table": _RUNS_TABLE,
        "data": bb_row,
    })
    if result is not None:
        log.info("butterbase.run.ok", extra={"run_id": summary.run_id})
    return True  # local mirror is the source of truth for the demo


async def list_runs(limit: int = 50) -> list[dict]:
    # Local mirror is authoritative for the demo (low latency, no network).
    return _read_local_runs(limit)


# ─────────────────────────────────────────────────────────────────────────────
# Launch page hosting
# ─────────────────────────────────────────────────────────────────────────────
async def save_launch_page(slug: str, packet: LaunchPacket, display_name: str) -> str:
    record = {
        "slug": slug,
        "display_name": display_name,
        "packet": packet.model_dump(mode="json"),
        "published_at": datetime.utcnow().isoformat(),
    }
    _save_page_locally(slug, record)
    public_url = f"{settings.APP_BASE_URL}/launch/{slug}"

    if not settings.BUTTERBASE_PROJECT_ID:
        log.info("butterbase.page.local_only", extra={"slug": slug})
        return public_url

    result = await _mcp_call("insert_row", {
        "app_id": settings.BUTTERBASE_PROJECT_ID,
        "table": _PAGES_TABLE,
        "data": {
            "slug": slug,
            "display_name": display_name,
            "packet_json": packet.model_dump(mode="json"),
        },
    })
    if result is not None:
        log.info("butterbase.page.ok", extra={"slug": slug})
    return public_url


async def get_launch_page(slug: str) -> dict | None:
    # Local mirror first — fast and works offline.
    return _read_page_locally(slug)


async def save_launch_lead(slug: str, email: str, record: dict) -> bool:
    """Persist a customer reservation before any email send is attempted.

    The local write is the demo-safe source of truth. Butterbase is attempted
    only when configured, so a sponsor API outage never drops a real lead.
    """
    lead = {
        "slug": slug,
        "email": email,
        "offer_name": record.get("packet", {}).get("offer_name"),
        "display_name": record.get("display_name"),
        "created_at": datetime.utcnow().isoformat(),
    }
    _append_lead_locally(lead)

    if not settings.BUTTERBASE_PROJECT_ID:
        log.info("butterbase.lead.local_only", extra={"slug": slug})
        return True

    result = await _mcp_call("insert_row", {
        "app_id": settings.BUTTERBASE_PROJECT_ID,
        "table": _LEADS_TABLE,
        "data": lead,
    })
    if result is not None:
        log.info("butterbase.lead.ok", extra={"slug": slug})
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Local mirror helpers
# ─────────────────────────────────────────────────────────────────────────────
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


def _append_lead_locally(lead: dict) -> None:
    leads = _read_local_leads()
    leads.insert(0, lead)
    _LEADS_FILE.write_text(json.dumps(leads, default=str, indent=2))


def _read_local_leads() -> list[dict]:
    if not _LEADS_FILE.exists():
        return []
    return json.loads(_LEADS_FILE.read_text())
