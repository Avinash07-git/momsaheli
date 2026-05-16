"""Profile Agent — normalizes user input into a structured Profile."""
from __future__ import annotations

import logging

from app.schemas import Profile

log = logging.getLogger(__name__)


async def run_profile_agent(raw_profile: dict) -> Profile:
    """Validate + normalize the raw intake into our Profile schema.

    In Phase 1 the presets already match the schema, so this is a validating pass-through.
    In Phase 2 we'd ask Qwen to extract a Profile from free-text intake.
    """
    profile = Profile.model_validate(raw_profile)
    log.info(
        "profile_agent.ok",
        extra={"persona_id": profile.persona_id, "constraints": profile.hard_constraints},
    )
    return profile
