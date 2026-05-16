"""Profile — the user (mom) input to the swarm."""
from pydantic import BaseModel, Field


class Profile(BaseModel):
    persona_id: str = Field(..., description="jenny | jessica | custom_<uuid>")
    display_name: str = Field(..., description="First name only — no PII")
    day_job: str
    income_gap_monthly_usd: int = Field(..., ge=0, le=10_000)
    hours_per_week_available: int = Field(..., ge=1, le=40)
    skills: list[str] = Field(default_factory=list)
    budget_startup_usd: int = Field(..., ge=0, le=5_000)
    state: str = Field(..., min_length=2, max_length=2, description="2-letter US state")
    city: str | None = None
    hard_constraints: list[str] = Field(
        default_factory=list,
        description="e.g. ['no_nights', 'no_delivery', 'no_commercial_kitchen']",
    )
    notes: str | None = None
