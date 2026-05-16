"""EvidenceCard — one observed market data point from Etsy/Poshmark/Craigslist/etc."""
from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal["etsy", "poshmark", "craigslist", "nextdoor", "outschool", "facebook_marketplace"]


class EvidenceCard(BaseModel):
    id: str
    title: str = Field(..., description="e.g. 'Weekend Family Meal Pack — 4 servings'")
    source: SourceType
    source_url: str
    observed_price_usd: float
    observed_volume_signal: str = Field(..., description="e.g. '12 sold last month'")
    estimated_gross_monthly_usd: int
    estimated_net_monthly_usd: int = Field(..., description="After platform fee + materials")
    time_to_first_dollar_days: int
    notes: str = ""
