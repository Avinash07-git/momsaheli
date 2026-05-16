"""Opportunity — a ranked income path synthesized by Market Scout from evidence."""
from typing import Literal

from pydantic import BaseModel, Field

CategoryType = Literal["food_local", "digital_async", "service_local", "resale", "tutoring"]


class Opportunity(BaseModel):
    id: str
    title: str
    category: CategoryType
    evidence_card_ids: list[str] = Field(default_factory=list)
    rank: int = Field(..., ge=1, description="1 = best fit")
    rationale: str = Field(..., description="1-2 sentences from Market Scout")
    estimated_net_monthly_usd: int
    requires_permit: bool = False
