"""Memory Agent — persists trajectories to Evermind, surfaces cross-user patterns."""
from __future__ import annotations

import logging
from datetime import datetime

from app.adapters import evermind
from app.schemas import ComplianceCheck, CrossUserPattern, MemoryTrajectory, Opportunity, Profile

log = logging.getLogger(__name__)


async def save_run(
    run_id: str,
    profile: Profile,
    winner: Opportunity,
    rejected: list[Opportunity],
    compliance_checks: list[ComplianceCheck],
) -> MemoryTrajectory:
    trajectory = MemoryTrajectory(
        persona_id=profile.persona_id,
        run_id=run_id,
        chosen_opportunity_id=winner.id,
        rejected_opportunity_ids=[o.id for o in rejected],
        block_citations=[c.legal_citation_text for c in compliance_checks if c.legal_citation_text],
        timestamp=datetime.utcnow(),
    )
    await evermind.save_trajectory(trajectory)
    log.info("memory_agent.saved", extra={"run_id": run_id, "persona": profile.persona_id})
    return trajectory


async def surface_cross_user_pattern() -> CrossUserPattern | None:
    pattern = await evermind.query_cross_user_pattern()
    if pattern:
        log.info("memory_agent.pattern", extra={"confidence": pattern.confidence})
    return pattern


async def run_memory_agent(
    run_id: str,
    profile: Profile,
    winner: Opportunity,
    rejected: list[Opportunity],
    compliance_checks: list[ComplianceCheck],
) -> tuple[MemoryTrajectory, CrossUserPattern | None]:
    trajectory = await save_run(run_id, profile, winner, rejected, compliance_checks)
    pattern = await surface_cross_user_pattern()
    return trajectory, pattern
