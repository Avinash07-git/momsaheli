"""AgentField integration — wraps the 5-agent swarm as @reasoner endpoints.

Run this as a standalone process alongside uvicorn:
    python -m app.agentfield_agent

It registers with the AgentField control plane at :8080, making every agent
visible in the dashboard with full execution traces and audit trails.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from agentfield import Agent, AIConfig

from app.agents import (
    run_launch_agent,
    run_market_scout,
    run_memory_agent,
    run_profile_agent,
    run_reality_compliance,
)
from app.adapters import bright_data
from app.settings import settings

log = logging.getLogger(__name__)

af = Agent(
    node_id="moms-saheli-swarm",
    agentfield_server=settings.AGENTFIELD_CONTROL_PLANE_URL,
    version="0.1.0",
    description="5-agent swarm that surfaces realistic side-income opportunities for working moms, checks compliance, and publishes a real launch page.",
    tags=["hackathon", "economic-mobility", "multi-agent", "moms-saheli"],
    ai_config=AIConfig(model=f"google/{settings.GEMINI_MODEL}"),
    api_key=settings.AGENTFIELD_API_KEY or None,
    vc_enabled=False,
    enable_did=False,
)


@af.reasoner(tags=["profile", "normalization"])
async def profile_agent(raw_profile: dict) -> dict:
    """Normalize raw persona JSON into a validated Profile schema."""
    profile = await run_profile_agent(raw_profile)
    return profile.model_dump(mode="json")


@af.reasoner(tags=["market", "ranking", "gemini"])
async def market_scout(raw_profile: dict) -> dict:
    """Pull evidence cards and rank opportunities by realistic net monthly income using Gemini."""
    profile = await run_profile_agent(raw_profile)
    cards, opportunities = await run_market_scout(profile)
    return {
        "evidence_cards": [c.model_dump(mode="json") for c in cards],
        "opportunities": [o.model_dump(mode="json") for o in opportunities],
    }


@af.reasoner(tags=["compliance", "legal", "tavily"])
async def reality_compliance_agent(raw_profile: dict, opportunities: list) -> dict:
    """Check each opportunity against real state cottage-food law via Tavily. BLOCKs with .gov citations."""
    from app.schemas import Opportunity
    profile = await run_profile_agent(raw_profile)
    opps = [Opportunity.model_validate(o) for o in opportunities]
    pre_law = await bright_data.scrape_state_law(profile.state) if profile.state else None
    checks = []
    winner = None
    async for check in run_reality_compliance(opps, profile, pre_fetched_law=pre_law):
        checks.append(check)
        if check.verdict == "PASS" and winner is None:
            winner = next((o for o in opps if o.id == check.opportunity_id), None)
    return {
        "checks": [c.model_dump(mode="json") for c in checks],
        "winner_id": winner.id if winner else None,
    }


@af.reasoner(tags=["launch", "copywriting", "gemini"])
async def launch_agent(raw_profile: dict, opportunity: dict) -> dict:
    """Generate offer name, tagline, price, 7-day plan, and publish a real landing page using Gemini."""
    from app.schemas import Opportunity
    profile = await run_profile_agent(raw_profile)
    opp = Opportunity.model_validate(opportunity)
    packet, launch_url = await run_launch_agent(opp, profile)
    return {
        "packet": packet.model_dump(mode="json"),
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
    """Persist run trajectory and surface cross-user learned patterns."""
    from app.schemas import Opportunity, ComplianceCheck
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


@af.reasoner(tags=["orchestrator", "swarm", "end-to-end"])
async def run_full_swarm(raw_profile: dict) -> dict:
    """Run the complete 5-agent pipeline end-to-end and return the launch URL."""
    from app.orchestrator.runner import SwarmRunner
    runner = SwarmRunner(raw_profile=raw_profile)
    await runner.run()
    return {"run_id": runner.run_id, "status": "complete"}


if __name__ == "__main__":
    af.run(port=8001)
