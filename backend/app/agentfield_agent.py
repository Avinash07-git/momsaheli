"""AgentField integration — wraps the 5-agent swarm as @reasoner endpoints.

Run this as a standalone process alongside uvicorn:
    python -m app.agentfield_agent

It registers with the AgentField control plane at the URL set by
AGENTFIELD_CONTROL_PLANE_URL, exposing every agent as a callable reasoner.
The dashboard at http://<control-plane>/ui/ then renders the full nested
execution waterfall when `run_full_swarm` is invoked.

Demo safety: if AGENTFIELD_API_KEY is missing OR the control plane is
unreachable, we log a clear warning and exit 0 (not 1) so `start.sh`
continues bringing up the rest of the stack. The FastAPI demo path never
depends on AgentField being alive.
"""
from __future__ import annotations

import logging
import sys
import uuid
from urllib.parse import urlparse

import requests
from agentfield import Agent, AIConfig

from app.agents import (
    run_launch_agent,
    run_market_scout,
    run_memory_agent,
    run_profile_agent,
    run_reality_compliance,
)
from app.adapters import bright_data
from app.schemas import ComplianceCheck, Opportunity
from app.settings import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("agentfield_agent")


# ──────────────────────────────────────────────────────────────────────────
# Preflight: don't even build the Agent if we know we'll fail to register.
# This keeps `start.sh` from getting noisy stack traces during boot.
# ──────────────────────────────────────────────────────────────────────────
def _preflight_or_exit() -> None:
    if not settings.AGENTFIELD_API_KEY:
        log.warning("AGENTFIELD_API_KEY is empty — skipping AgentField agent startup.")
        log.warning("FastAPI demo path keeps working; just no dashboard waterfall.")
        sys.exit(0)
    try:
        u = urlparse(settings.AGENTFIELD_CONTROL_PLANE_URL)
        ping = f"{u.scheme}://{u.netloc}/healthz"
        requests.get(ping, timeout=2)
    except Exception as e:  # noqa: BLE001 — we want a wide net here
        log.warning(
            "AgentField control plane unreachable at %s (%s) — skipping agent startup.",
            settings.AGENTFIELD_CONTROL_PLANE_URL, e,
        )
        log.warning("Start the control plane with: af server --port 8080")
        sys.exit(0)


# Build the Agent instance unconditionally — instantiating it is side-effect-free
# (it just configures the FastAPI subclass). The preflight that contacts the
# control plane only runs when this module is executed as __main__, so importing
# it from tests / IDE / FastAPI never accidentally calls sys.exit().
af = Agent(
    node_id="moms-saheli-swarm",
    agentfield_server=settings.AGENTFIELD_CONTROL_PLANE_URL,
    version="0.1.0",
    description=(
        "5-agent swarm that surfaces realistic side-income opportunities for "
        "working moms, checks compliance against real state law, and publishes "
        "a real launch page."
    ),
    tags=["hackathon", "economic-mobility", "multi-agent", "moms-saheli"],
    ai_config=AIConfig(model=f"google/{settings.GEMINI_MODEL}"),
    api_key=settings.AGENTFIELD_API_KEY or None,
    vc_enabled=False,
    enable_did=False,
)


# ──────────────────────────────────────────────────────────────────────────
# 5 child reasoners — each delegates to the canonical run_*_agent function.
# These are independently callable (judges can curl them) AND get nested under
# run_full_swarm when invoked from there via AgentField's contextvar tracking.
# ──────────────────────────────────────────────────────────────────────────
@af.reasoner(tags=["profile", "normalization"])
async def profile_agent(raw_profile: dict) -> dict:
    """Normalize raw persona JSON into a validated Profile schema."""
    profile = await run_profile_agent(raw_profile)
    return profile.model_dump(mode="json")


@af.reasoner(tags=["market", "ranking", "gemini"])
async def market_scout(raw_profile: dict) -> dict:
    """Pull evidence cards + rank opportunities by realistic net monthly $ (Gemini)."""
    profile = await run_profile_agent(raw_profile)
    cards, opportunities = await run_market_scout(profile)
    return {
        "evidence_cards": [c.model_dump(mode="json") for c in cards],
        "opportunities":  [o.model_dump(mode="json") for o in opportunities],
    }


@af.reasoner(tags=["compliance", "legal", "tavily"])
async def reality_compliance_agent(raw_profile: dict, opportunities: list) -> dict:
    """Check each opportunity against real state cottage-food law (Tavily). BLOCKs cite .gov."""
    profile = await run_profile_agent(raw_profile)
    opps = [Opportunity.model_validate(o) for o in opportunities]
    pre_law = await bright_data.scrape_state_law(profile.state) if profile.state else None
    checks: list[ComplianceCheck] = []
    winner_id: str | None = None
    async for check in run_reality_compliance(opps, profile, pre_fetched_law=pre_law):
        checks.append(check)
        if check.verdict == "PASS" and winner_id is None:
            winner_id = check.opportunity_id
    return {
        "checks":    [c.model_dump(mode="json") for c in checks],
        "winner_id": winner_id,
    }


@af.reasoner(tags=["launch", "copywriting", "gemini"])
async def launch_agent(raw_profile: dict, opportunity: dict) -> dict:
    """Generate offer + 7-day plan, publish a real landing page (Gemini + Butterbase)."""
    profile = await run_profile_agent(raw_profile)
    opp = Opportunity.model_validate(opportunity)
    packet, launch_url = await run_launch_agent(opp, profile)
    return {
        "packet":     packet.model_dump(mode="json"),
        "launch_url": launch_url,
    }


@af.reasoner(tags=["memory", "persistence", "cross-user"])
async def memory_agent(
    run_id: str,
    raw_profile: dict,
    winner: dict,
    rejected: list,
    compliance_checks: list,
) -> dict:
    """Persist run trajectory + surface cross-user learned patterns (Evermind)."""
    profile = await run_profile_agent(raw_profile)
    winner_opp = Opportunity.model_validate(winner)
    rejected_opps = [Opportunity.model_validate(r) for r in rejected]
    checks = [ComplianceCheck.model_validate(c) for c in compliance_checks]
    _, pattern = await run_memory_agent(
        run_id=run_id,
        profile=profile,
        winner=winner_opp,
        rejected=rejected_opps,
        compliance_checks=checks,
    )
    return {"pattern": pattern.model_dump(mode="json") if pattern else None}


# ──────────────────────────────────────────────────────────────────────────
# Orchestrator reasoner — awaits the 5 children so the dashboard renders
# a proper nested execution waterfall (THE sponsor-genuine moment).
# ──────────────────────────────────────────────────────────────────────────
@af.reasoner(tags=["orchestrator", "swarm", "end-to-end"])
async def run_full_swarm(raw_profile: dict) -> dict:
    """Run the complete 5-agent pipeline end-to-end.

    Calls each child @reasoner in sequence so the AgentField dashboard renders
    one parent execution with 5 child spans, each with its own
    inputs/outputs/timings/tags. This is the 'sponsor-genuine' moment vs.
    a flat opaque call.
    """
    run_id = f"af-{uuid.uuid4().hex[:12]}"

    # 1. Profile
    profile = await profile_agent(raw_profile)

    # 2. Market scout (evidence + ranked opportunities)
    market = await market_scout(raw_profile)
    opportunities = market["opportunities"]
    if not opportunities:
        return {"run_id": run_id, "status": "no_opportunities", "profile": profile}

    # 3. Reality & compliance (picks first PASS as winner)
    compliance = await reality_compliance_agent(raw_profile, opportunities)
    winner_id = compliance.get("winner_id")
    winner = next((o for o in opportunities if o["id"] == winner_id), None)
    if winner is None:
        return {
            "run_id": run_id,
            "status": "all_blocked",
            "profile": profile,
            "checks": compliance["checks"],
        }

    # 4. Launch (offer + copy + real published page)
    launch = await launch_agent(raw_profile, winner)

    # 5. Memory (persist trajectory + surface cross-user pattern)
    rejected = [o for o in opportunities if o["id"] != winner["id"]]
    memory = await memory_agent(
        run_id=run_id,
        raw_profile=raw_profile,
        winner=winner,
        rejected=rejected,
        compliance_checks=compliance["checks"],
    )

    checks = compliance["checks"]
    return {
        "run_id": run_id,
        "status": "complete",
        "profile": profile,
        "winner": winner,
        "launch_url": launch["launch_url"],
        "pattern": memory["pattern"],
        "compliance_summary": {
            "blocks": sum(1 for c in checks if c["verdict"] == "BLOCK"),
            "passes": sum(1 for c in checks if c["verdict"] == "PASS"),
            "warns":  sum(1 for c in checks if c["verdict"] == "WARN"),
        },
    }


if __name__ == "__main__":
    _preflight_or_exit()  # Only when run directly; not on plain import.
    log.info("AgentField agent starting on :8001 (control plane: %s)",
             settings.AGENTFIELD_CONTROL_PLANE_URL)
    try:
        af.run(port=8001)
    except KeyboardInterrupt:
        log.info("AgentField agent shutting down.")
    except Exception:
        log.exception("AgentField agent crashed (this does NOT affect the FastAPI demo path).")
        sys.exit(1)
