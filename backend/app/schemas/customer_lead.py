"""CustomerLead — one buyer-intent signal for the selected opportunity."""
from typing import Literal

from pydantic import BaseModel, Field

LeadSourceType = Literal["reddit", "facebook_group", "nextdoor", "google", "local_search", "quora"]


class CustomerLead(BaseModel):
    id: str
    title: str = Field(..., description="Human-readable buyer-intent post/search title")
    source: LeadSourceType
    source_url: str
    intent_signal: str = Field(..., description="What the customer appears to need")
    location_hint: str | None = None
    suggested_outreach: str = Field(..., description="Simple, non-spammy reply or DM")
    match_reason: str = Field(..., description="Why this lead matches the selected opportunity")
    confidence: float = Field(default=0.65, ge=0, le=1)
