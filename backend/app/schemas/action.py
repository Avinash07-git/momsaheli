"""Customer activation schemas.

These models describe the approval-gated path from a launch packet to a first
customer action. They intentionally model drafts and previews separately from
external posting/submission so the app can stay safe by default.
"""
from typing import Literal

from pydantic import BaseModel, Field


ApprovedChannelType = Literal[
    "whatsapp_group",
    "facebook_group",
    "nextdoor",
    "instagram",
    "friends_text",
    "email",
    "vendor_form",
    "marketplace",
    "manual",
]

AllowedActionType = Literal["draft", "fill", "submit", "post"]


class ApprovedChannel(BaseModel):
    id: str
    type: ApprovedChannelType
    name: str
    audience: str | None = None
    url: str | None = None
    rules_summary: str | None = None
    user_approved: bool = False
    allowed_actions: list[AllowedActionType] = Field(default_factory=list)


class CustomerLead(BaseModel):
    id: str
    title: str
    source_type: Literal[
        "vendor_form",
        "community_page",
        "school_page",
        "marketplace",
        "approved_group",
        "warm_network",
        "public_demand_post",
        "local_directory",
        "event_page",
        "manual",
    ]
    source_url: str | None = None
    audience_match: str
    why_relevant: str
    estimated_reach: str | None = None
    confidence: float
    live_source: bool
    provider: str
    notes: str | None = None
    posted_at: str | None = None
    recency: str | None = None
    demand_signal: str | None = None


class ActionCandidate(BaseModel):
    id: str
    type: Literal[
        "whatsapp_post",
        "facebook_group_post",
        "nextdoor_post",
        "warm_text",
        "email",
        "vendor_form_fill",
        "marketplace_listing",
        "instagram_post",
        "manual_step",
    ]
    title: str
    destination_name: str
    destination_url: str | None = None
    linked_lead_id: str | None = None
    priority_score: float
    reason: str
    expected_outcome: str
    effort_minutes: int
    risk_level: Literal["low", "medium", "high"]
    execution_mode: Literal["draft_only", "fill_no_submit", "post_after_review"]
    requires_user_approval: bool = True
    draft_text: str | None = None
    form_fields: dict[str, str] | None = None
    actionbook_session_id: str | None = None
    actionbook_screenshot_url: str | None = None


class ActivationPlan(BaseModel):
    opportunity_id: str
    mom_display_name: str
    summary: str
    recommended_first_action_id: str | None = None
    leads: list[CustomerLead]
    actions: list[ActionCandidate]
    launch_message_short: str
    launch_message_friendly: str
    launch_message_formal: str
    safety_notes: list[str]
    used_live_search: bool


class ActionExecutionRequest(BaseModel):
    approved: bool
    submit_or_post: bool = False


class ActionExecutionResult(BaseModel):
    action_id: str
    status: Literal["drafted", "filled", "posted", "submitted", "blocked", "failed"]
    message: str
    proof_url: str | None = None
    screenshot_url: str | None = None
    actionbook_session_id: str | None = None
    error: str | None = None
