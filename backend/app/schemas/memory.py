"""Memory schemas — trajectories persisted to Evermind + cross-user patterns surfaced."""
from datetime import datetime

from pydantic import BaseModel, Field


class MemoryTrajectory(BaseModel):
    persona_id: str
    run_id: str
    chosen_opportunity_id: str
    rejected_opportunity_ids: list[str] = Field(default_factory=list)
    block_citations: list[str] = Field(
        default_factory=list,
        description="Full legal_citation_text values from BLOCK verdicts",
    )
    timestamp: datetime


class CrossUserPattern(BaseModel):
    pattern_text: str = Field(
        ...,
        description="e.g. 'low-hours + no-delivery → digital-first validation wins'",
    )
    supporting_run_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
