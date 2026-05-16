"""ComplianceCheck — verdict from the Reality & Compliance Agent."""
from typing import Literal

from pydantic import BaseModel, Field

Verdict = Literal["PASS", "BLOCK", "WARN"]


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
