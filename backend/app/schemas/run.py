"""Run-level schemas — summary for History screen + the SSE event envelope."""
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

EventType = Literal[
    "run_started",
    "profile_ready",
    "evidence_card",
    "opportunities_ranked",
    "compliance_check",
    "winner_selected",
    "launch_packet_ready",
    "launch_published",
    "customer_leads_found",
    "activation_plan_ready",
    "action_execution_result",
    "memory_pattern",
    "agent_error",
    "run_complete",
]


class AgentEvent(BaseModel):
    """The envelope every SSE event uses. `data` shape depends on `type`."""

    type: EventType
    agent: str = Field(
        ...,
        description="profile | market_scout | reality_compliance | launch | customer_activation | memory | system",
    )
    run_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: dict[str, Any] = Field(default_factory=dict)


class RunSummary(BaseModel):
    run_id: str
    persona_display_name: str
    winner_offer_name: str | None
    launch_url: str | None
    created_at: datetime
    duration_ms: int
