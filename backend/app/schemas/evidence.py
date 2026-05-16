"""EvidenceCard — one observed market data point from Etsy/Poshmark/Craigslist/etc."""
from typing import Literal

from pydantic import BaseModel, Field

SourceType = Literal[
    "etsy",            # digital + handmade only
    "poshmark",        # resale + digital downloads
    "craigslist",      # local services
    "nextdoor",        # hyper-local services + food
    "outschool",       # online tutoring
    "facebook_marketplace",
    "facebook_group",  # local home-chef + community groups
    "castiron",        # cottage-food marketplace
    "instagram",       # home-chef DM commerce
]


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
    # Actionbook-provided live session fields — when present, the UI swaps the
    # placeholder BrowserFrame for a real iframe of the live browser session.
    actionbook_session_id: str | None = None
    actionbook_session_url: str | None = Field(
        default=None,
        description="Embeddable URL of the live Actionbook browser session (renders in <iframe>)",
    )
    actionbook_screenshot_url: str | None = None
    # Bright Data provenance — set when this card came from a real live scrape
    # (vs. fixture). UI can render a 'Live ✓' badge.
    live_scrape_ok: bool = False
    live_scrape_provider: str | None = None
