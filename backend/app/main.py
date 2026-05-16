"""FastAPI app — Mom's Saheli backend.

Routes:
  POST /api/run               kick off a swarm run
  GET  /api/stream/{run_id}   SSE event stream
  GET  /api/runs              list past runs (Butterbase)
  GET  /api/fixtures/{name}   read a fixture (jenny | jessica)
  GET  /launch/{slug}         public Mom's Saheli launch page (HTML)
  GET  /health                liveness
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sse_starlette.sse import EventSourceResponse

from app.adapters import actionbook, butterbase, evermind, resend_email
from app.adapters.llm_cascade import chat_json as llm_chat_json
from app.agents.profile_agent import agent_execution_plan, profile_from_text
from app.orchestrator import EVENT_BUS, SwarmRunner
from app.settings import settings

# ----- Logging -----
logging.basicConfig(level=settings.LOG_LEVEL, format="%(asctime)s %(levelname)s %(name)s %(message)s")
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()

# ----- App -----
app = FastAPI(title="Mom's Saheli", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Optional bundled frontend -----
def _resolve_frontend_dist_dir() -> Path | None:
    configured = os.getenv("FRONTEND_DIST_DIR") or os.getenv("FRONTEND_DIST")
    if configured:
        return Path(configured).expanduser().resolve()

    repo_root_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    return repo_root_dist if repo_root_dist.exists() else None


FRONTEND_DIST_DIR = _resolve_frontend_dist_dir()
FRONTEND_INDEX = FRONTEND_DIST_DIR / "index.html" if FRONTEND_DIST_DIR else None

if FRONTEND_DIST_DIR and (FRONTEND_DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="frontend-assets")

# ----- Jinja env for launch page template -----
_jinja = Environment(
    loader=FileSystemLoader(str(settings.templates_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


# ----- Health -----
@app.get("/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "use_fixtures": settings.USE_FIXTURES,
        "sponsors_configured": {
            "qwen": bool(settings.QWEN_API_KEY),
            "zai": bool(settings.ZAI_API_KEY),
            "token_router": bool(settings.TOKEN_ROUTER_API_KEY),
            "bright_data": bool(settings.BRIGHT_DATA_API_TOKEN),
            "actionbook": bool(settings.ACTIONBOOK_API_KEY),
            "evermind": bool(settings.EVERMIND_API_KEY),
            "butterbase": bool(settings.BUTTERBASE_API_KEY),
            "agentfield": bool(settings.AGENTFIELD_API_KEY),
            "resend": bool(settings.RESEND_API_KEY),
        },
    }


# ----- Fixtures -----
@app.get("/api/fixtures/{name}")
async def get_fixture(name: str) -> dict[str, Any]:
    if name not in {"jenny", "jessica"}:
        raise HTTPException(404, "Unknown fixture")
    path = settings.fixtures_dir / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, f"Fixture file not found: {path}")
    return json.loads(path.read_text())


# ----- Run kick-off -----
@app.post("/api/run")
async def start_run(payload: dict[str, Any], background_tasks: BackgroundTasks) -> dict[str, str]:
    raw_profile = payload.get("profile")
    if not raw_profile:
        raise HTTPException(400, "Missing 'profile' in body")

    runner = SwarmRunner(raw_profile=raw_profile)
    # Fire-and-forget; SSE consumer attaches to EVENT_BUS via run_id
    background_tasks.add_task(_run_safely, runner)
    return {"run_id": runner.run_id, "stream_url": f"/api/stream/{runner.run_id}"}


@app.post("/api/run-text")
async def start_run_from_text(payload: dict[str, Any], background_tasks: BackgroundTasks) -> dict[str, Any]:
    query = str(payload.get("query") or "").strip()
    if len(query) < 12:
        raise HTTPException(400, "Describe the situation in at least one sentence")

    profile = await profile_from_text(query)
    runner = SwarmRunner(raw_profile=profile.model_dump(mode="json"))
    background_tasks.add_task(_run_safely, runner)
    return {
        "run_id": runner.run_id,
        "stream_url": f"/api/stream/{runner.run_id}",
        "profile": profile.model_dump(mode="json"),
        "plan": agent_execution_plan(),
    }


async def _run_safely(runner: SwarmRunner) -> None:
    try:
        await runner.run()
    except Exception:
        log.exception("runner.crashed", run_id=runner.run_id)


# ----- SSE stream -----
@app.get("/api/stream/{run_id}")
async def stream(run_id: str, request: Request):
    async def event_gen():
        try:
            async for event in EVENT_BUS.stream(run_id):
                if await request.is_disconnected():
                    break
                yield {
                    "event": event.type,
                    "data": event.model_dump_json(),
                }
        except asyncio.CancelledError:
            return

    return EventSourceResponse(event_gen())


# ----- Run history -----
@app.get("/api/runs")
async def list_runs(limit: int = 20) -> dict[str, Any]:
    runs = await butterbase.list_runs(limit=limit)
    return {"runs": runs, "count": len(runs)}


@app.get("/api/memory")
async def get_memory() -> dict[str, Any]:
    pattern = await evermind.query_cross_user_pattern()
    return {
        "trajectories": evermind.trajectories_for_history(),
        "cross_user_pattern": pattern.model_dump(mode="json") if pattern else None,
    }


# ----- Public launch page -----
@app.get("/launch/{slug}", response_class=HTMLResponse)
async def launch_page(slug: str) -> HTMLResponse:
    record = await butterbase.get_launch_page(slug)
    if not record:
        raise HTTPException(404, "Launch page not found")
    template = _jinja.get_template("launch_page.html")
    html = template.render(
        slug=slug,
        display_name=record["display_name"],
        packet=record["packet"],
        published_at=record.get("published_at"),
    )
    return HTMLResponse(html)


@app.post("/api/launch/{slug}/reserve")
async def reserve_launch_spot(slug: str, payload: dict[str, Any]) -> dict[str, Any]:
    email = str(payload.get("email") or "").strip().lower()
    if not _looks_like_email(email):
        raise HTTPException(400, "Enter a valid email address")

    record = await butterbase.get_launch_page(slug)
    if not record:
        raise HTTPException(404, "Launch page not found")

    # Use Actionbook to draft personalized intake questions for this offer's category
    packet = record.get("packet", {})
    category = packet.get("category") or "food_local"
    offer_name = packet.get("offer_name") or "this offer"
    questions_result = await actionbook.draft_followup_questions(category, offer_name)
    questions = questions_result.get("questions", [])

    await butterbase.save_launch_lead(slug=slug, email=email, record=record)

    # Try Actionbook Gmail first — sends from the seller's own Gmail account
    # (requires Actionbook extension installed and ACTIONBOOK_API_KEY set)
    display_name = record.get("display_name") or "the seller"
    gmail_result = await actionbook.send_via_gmail(
        customer_email=email,
        offer_name=offer_name,
        questions=questions,
        seller_name=display_name,
    )

    # Fall back to Resend if Actionbook Gmail send didn't go live
    email_result: dict = {"sent": False, "message_id": None}
    if not gmail_result.get("live"):
        email_result = await resend_email.send_reservation_followup(
            slug=slug, customer_email=email, record=record, questions=questions,
        )

    sent = gmail_result.get("sent") or email_result.get("sent", False)
    return {
        "ok": True,
        "stored": True,
        "email_sent": sent,
        "email_provider": gmail_result.get("provider") if gmail_result.get("sent") else "resend",
        "message_id": email_result.get("message_id"),
        "questions_source": questions_result.get("session_id"),
        "actionbook_session": gmail_result.get("session_id"),
    }


@app.get("/launch/{slug}/respond", response_class=HTMLResponse)
async def customer_response_page(slug: str, e: str = "") -> HTMLResponse:
    """Form page where the customer fills out their intake preferences."""
    record = await butterbase.get_launch_page(slug)
    if not record:
        raise HTTPException(404, "Launch page not found")

    packet = record.get("packet", {})
    category = packet.get("category") or "food_local"
    offer_name = packet.get("offer_name") or "this offer"
    display_name = record.get("display_name") or "the seller"

    questions_result = await actionbook.draft_followup_questions(category, offer_name)
    questions = questions_result.get("questions", [])

    template = _jinja.get_template("customer_response.html")
    html = template.render(
        slug=slug,
        customer_email=e,
        offer_name=offer_name,
        display_name=display_name,
        questions=questions,
    )
    return HTMLResponse(html)


@app.post("/api/launch/{slug}/customer-response")
async def submit_customer_response(
    slug: str, payload: dict[str, Any], background_tasks: BackgroundTasks,
) -> dict[str, Any]:
    """Process a customer's intake response.

    1. Parse preferences from the submitted answers
    2. Store preferences in Evermind (memory by customer email)
    3. Generate a seller action plan via LLM
    4. Email the plan to the seller (SELLER_EMAIL)
    """
    email = str(payload.get("email") or "").strip().lower()
    raw_response = str(payload.get("response") or "").strip()
    if not raw_response:
        raise HTTPException(400, "Response cannot be empty")

    record = await butterbase.get_launch_page(slug)
    if not record:
        raise HTTPException(404, "Launch page not found")

    packet = record.get("packet", {})
    offer_name = packet.get("offer_name") or "this offer"
    display_name = record.get("display_name") or "the seller"

    # Parse structured preferences from the free-text response
    preferences = await _parse_customer_preferences(raw_response, email)

    # Save to Evermind — memory keyed by customer email
    background_tasks.add_task(evermind.save_customer_preference, email, slug, preferences)

    # Generate seller action plan
    plan_text = await _generate_seller_plan(offer_name, display_name, preferences, packet)

    # Email the plan to the seller
    email_result = await resend_email.send_seller_action_plan(
        slug=slug,
        customer_email=email or "anonymous customer",
        offer_name=offer_name,
        plan_text=plan_text,
        preferences=preferences,
    )

    return {
        "ok": True,
        "plan_sent": bool(email_result.get("sent")),
        "message_id": email_result.get("message_id"),
    }


async def _parse_customer_preferences(raw_response: str, email: str) -> dict[str, Any]:
    """Extract structured preferences from free-text customer response via LLM."""
    try:
        result = await llm_chat_json(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You parse a customer's free-text response into structured fields. "
                        "Return JSON with these keys (use null if not mentioned): "
                        "{\"dietary_restrictions\": str|null, \"quantity\": str|null, "
                        "\"deadline\": str|null, \"special_requests\": str|null}"
                    ),
                },
                {"role": "user", "content": raw_response},
            ],
            temperature=0.1,
        )
    except Exception:
        result = {}

    from datetime import datetime
    return {
        "raw_response": raw_response,
        "email": email,
        "dietary_restrictions": result.get("dietary_restrictions"),
        "quantity": result.get("quantity"),
        "deadline": result.get("deadline"),
        "special_requests": result.get("special_requests"),
        "submitted_at": datetime.utcnow().isoformat(),
    }


async def _generate_seller_plan(
    offer_name: str, display_name: str, preferences: dict, packet: dict
) -> str:
    """Generate a concrete action plan for the seller based on the customer's response."""
    day_plan = packet.get("day_plan") or []
    day_plan_text = "\n".join(
        f"  Day {item.get('day')}: {item.get('action')} (~{item.get('estimated_minutes', 30)} min)"
        for item in day_plan[:5]
        if isinstance(item, dict)
    )
    try:
        result = await llm_chat_json(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write a short, actionable seller action plan in plain text (no markdown). "
                        "Keep it under 250 words. Use bullet points with a dash. "
                        "Return JSON: {\"plan\": str}"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Seller: {display_name}\n"
                        f"Offer: {offer_name}\n"
                        f"Customer dietary restrictions: {preferences.get('dietary_restrictions') or 'none stated'}\n"
                        f"Quantity: {preferences.get('quantity') or 'not specified'}\n"
                        f"Deadline: {preferences.get('deadline') or 'flexible'}\n"
                        f"Special requests: {preferences.get('special_requests') or 'none'}\n"
                        f"Existing day plan:\n{day_plan_text}\n\n"
                        "Write a clear action plan for the seller to fulfill this specific customer order."
                    ),
                },
            ],
            temperature=0.3,
        )
        return str(result.get("plan") or "").strip()
    except Exception:
        # Deterministic fallback
        deadline = preferences.get("deadline") or "as soon as possible"
        restr = preferences.get("dietary_restrictions") or "none"
        qty = preferences.get("quantity") or "standard amount"
        return (
            f"Action plan for {offer_name}:\n"
            f"- Customer deadline: {deadline}\n"
            f"- Dietary restrictions: {restr}\n"
            f"- Quantity: {qty}\n"
            f"- Special requests: {preferences.get('special_requests') or 'none'}\n"
            f"- Next step: Confirm the order details and begin prep.\n"
            f"- Reach out to the customer at {preferences.get('email', 'their email')} to confirm."
        )


def _looks_like_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))


# ----- Root -----
@app.get("/", response_model=None)
async def root():
    if FRONTEND_INDEX and FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)

    return JSONResponse({
        "name": "Mom's Saheli",
        "version": "0.1.0",
        "tagline": "The friend she can't afford.",
        "docs": "/docs",
        "frontend": "http://localhost:5173",
    })


@app.get("/{full_path:path}", include_in_schema=False)
async def frontend_spa_fallback(full_path: str) -> FileResponse:
    """Serve React routes from the bundled frontend without masking backend APIs."""
    backend_paths = {"health", "docs", "redoc", "openapi.json"}
    if full_path in backend_paths or full_path.startswith(("api/", "launch/")):
        raise HTTPException(404, "Not found")
    if FRONTEND_INDEX and FRONTEND_INDEX.exists():
        return FileResponse(FRONTEND_INDEX)
    raise HTTPException(404, "Frontend build not found")
