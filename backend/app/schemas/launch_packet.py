"""LaunchPacket — everything Launch Agent generates for the winning opportunity."""
from typing import Literal

from pydantic import BaseModel, Field

ChannelType = Literal[
    "nextdoor",
    "facebook_group",
    "text_friends",
    "etsy_listing",
    "instagram",
    "whatsapp_group",
    "vendor_form",
    "marketplace_listing",
    "email",
    "manual",
]


class OutreachDraft(BaseModel):
    channel: ChannelType
    subject: str | None = None
    body_markdown: str


class DayPlanItem(BaseModel):
    day: int = Field(..., ge=1, le=7)
    action: str
    estimated_minutes: int


class LaunchPacket(BaseModel):
    opportunity_id: str
    offer_name: str = Field(..., description="e.g. 'Sunday Family Meal Pack'")
    offer_tagline: str
    price_usd: float
    unit: str = Field(..., description="e.g. 'per meal pack', 'per printable'")
    description_markdown: str
    target_customer: str
    outreach_drafts: list[OutreachDraft] = Field(default_factory=list)
    day_plan: list[DayPlanItem] = Field(default_factory=list, description="7-day plan")
