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
from pathlib import Path
from typing import Any

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sse_starlette.sse import EventSourceResponse

from app.adapters import actionbook, butterbase, evermind
from app.orchestrator import ACTIVATION_PLANS, EVENT_BUS, SwarmRunner
from app.schemas import AgentEvent
from app.schemas.action import ActionExecutionRequest, ActionExecutionResult
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


@app.post("/api/runs/{run_id}/actions/{action_id}/execute")
async def execute_activation_action(
    run_id: str,
    action_id: str,
    body: ActionExecutionRequest,
) -> ActionExecutionResult:
    plan = ACTIVATION_PLANS.get(run_id)
    if not plan:
        raise HTTPException(404, "Activation plan not found for this run")

    action = next((a for a in plan.actions if a.id == action_id), None)
    if not action:
        raise HTTPException(404, "Action not found")

    if not body.approved:
        result = ActionExecutionResult(
            action_id=action_id,
            status="blocked",
            message="Blocked: no action can run until the user approves it.",
        )
    else:
        raw = await actionbook.execute_activation_action(
            action=action.model_dump(mode="json"),
            approved=body.approved,
            submit_or_post=body.submit_or_post,
        )
        raw.setdefault("action_id", action_id)
        result = ActionExecutionResult.model_validate(raw)

    await EVENT_BUS.publish(AgentEvent(
        type="action_execution_result",
        agent="customer_activation",
        run_id=run_id,
        data={"result": result.model_dump(mode="json")},
    ))
    return result


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


# ----- Frontend static files (production) -----
# In dev the Vite dev-server handles this. In production (Zeabur) we serve
# the built frontend from frontend/dist/ which lives two directories up.
_DIST = Path(os.environ.get(
    "FRONTEND_DIST",
    str(Path(__file__).resolve().parents[2] / "frontend" / "dist"),
))

if _DIST.exists():
    # Serve /assets/* directly
    _assets = _DIST / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/vite.svg", include_in_schema=False)
    async def vite_svg():
        f = _DIST / "vite.svg"
        return FileResponse(str(f)) if f.exists() else JSONResponse({}, status_code=404)

    # SPA catch-all — serve index.html for every non-API route
    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # Let API / launch / health routes fall through (handled above)
        _reserved = ("api/", "launch/", "health", "docs", "openapi.json")
        if any(full_path.startswith(r) for r in _reserved):
            raise HTTPException(404, "Not found")
        index = _DIST / "index.html"
        if index.exists():
            return FileResponse(str(index))
        raise HTTPException(404, "index.html not built")
else:
    # Dev-mode root — just a status JSON
    @app.get("/")
    async def root() -> JSONResponse:
        return JSONResponse({
            "name": "Mom's Saheli",
            "version": "0.1.0",
            "docs": "/docs",
            "frontend": "http://localhost:5173 (run npm run dev)",
        })
