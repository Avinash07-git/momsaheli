"""ComplianceCheck — verdict from the Reality & Compliance Agent."""
from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["PASS", "BLOCK", "WARN"]


class ComplianceDimension(BaseModel):
    """One axis of the multi-vector compliance fan-out (run in parallel via asyncio.gather)."""
    dimension: str = Field(..., description="e.g. 'state_cottage_food', 'irs_self_employment', 'platform_tos'")
    passed: bool
    citation_url: str | None = None
    citation_text: str | None = None
    note: str = ""


class ComplianceCheck(BaseModel):
    opportunity_id: str
    verdict: Verdict
    constraint_math_passed: bool
    constraint_math_reasons: list[str] = Field(
        default_factory=list,
        description="e.g. ['fits 5 hr/wk', 'fits $80 budget']",
    )
    legal_passed: bool
    legal_citation_source_url: str | None = None
    legal_citation_text: str | None = Field(
        default=None,
        description="Full citation, e.g. 'California Health & Safety Code §113758 — Cottage Food Operations…'",
    )
    block_reason: str | None = Field(
        default=None,
        description="Human-readable summary shown in the UI",
    )
    dimensions: list[ComplianceDimension] = Field(
        default_factory=list,
        description="Parallel fan-out: multiple real Tavily checks run via asyncio.gather. Adds technical depth + multi-source citation breadth.",
    )
