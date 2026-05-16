"""Reality & Compliance Agent — the BLOCKER.

Two checks per opportunity:
1. Constraint math: hours, budget, no-delivery, no-nights, no-commercial-kitchen, etc.
2. Live legal scrape (Bright Data): pull the state's actual cottage-food / permit page.

Emits one ComplianceCheck per opportunity. The winner = first PASS by rank.
"""
from __future__ import annotations

import logging
from typing import AsyncIterator

from app.adapters import bright_data
from app.schemas import ComplianceCheck, Opportunity, Profile

log = logging.getLogger(__name__)


def _hours_required_for_opportunity(opportunity: Opportunity) -> int:
    base = {
        "digital_async": 2,
        "tutoring": 4,
        "resale": 4,
        "food_local": 5,
        "service_local": 6,
    }.get(opportunity.category, 5)
    t = opportunity.title.lower()
    if any(k in t for k in ["daily", "5 days", "subscription", "every day"]):
        base += 6  # daily commitments roughly double the weekly hours requirement
    if "cater" in t:
        base += 3
    return base


def _check_constraints(opportunity: Opportunity, profile: Profile) -> tuple[bool, list[str]]:
    """Pure-function constraint math. No LLM needed — this is the cheap, fast, deterministic check."""
    reasons: list[str] = []
    passed = True

    hours_required = _hours_required_for_opportunity(opportunity)
    if hours_required > profile.hours_per_week_available:
        passed = False
        reasons.append(
            f"needs ~{hours_required} hr/wk; she only has {profile.hours_per_week_available} hr/wk"
        )
    else:
        reasons.append(f"fits {profile.hours_per_week_available} hr/wk")

    if opportunity.category == "food_local" and profile.budget_startup_usd < 50:
        passed = False
        reasons.append(f"needs ~$50 startup; she has ${profile.budget_startup_usd}")
    else:
        reasons.append(f"fits ${profile.budget_startup_usd} budget")

    constraints = set(profile.hard_constraints)
    title_l = opportunity.title.lower()

    if "no_daily_delivery" in constraints and any(k in title_l for k in ["daily", "5 days", "subscription"]):
        passed = False
        reasons.append("requires daily delivery; she said no_daily_delivery")

    if opportunity.category == "service_local" and "no_phone_calls" in constraints:
        passed = False
        reasons.append("service work requires phone coordination; she said no_phone_calls")

    if opportunity.category == "resale" and "no_inventory" in constraints:
        passed = False
        reasons.append("resale requires inventory; she said no_inventory")

    if opportunity.category == "food_local" and "no_delivery" in constraints:
        passed = False
        reasons.append("physical food requires delivery; she said no_delivery")

    return passed, reasons


# Title-level markers that indicate "potentially hazardous food" (TCS) per FDA / state codes
_TCS_MARKERS = (
    "daily tiffin", "tiffin", "hot meal", "hot lunch",
    "daily hot", "lunch box delivery", "lunch delivery",
    "meal subscription", "meal-prep subscription", "refrigerated",
    "catering", "cater", "daily lunch", "5 days/wk", "5 days",
)


async def _check_legal(opportunity: Opportunity, profile: Profile) -> tuple[bool, str | None, str | None, str | None]:
    """Live Bright Data scrape of state cottage-food page when food-related.
    Returns (legal_passed, citation_url, citation_text, block_reason)."""
    if opportunity.category != "food_local":
        return True, None, None, None

    law_data = await bright_data.scrape_state_law(profile.state)

    requires_permit = law_data.get("requires_permit_for_hot_food", True)
    citation_text = law_data.get("citation_text")
    citation_url = law_data.get("source_url")

    title_l = opportunity.title.lower()
    is_potentially_hazardous = any(k in title_l for k in _TCS_MARKERS)

    if requires_permit and is_potentially_hazardous:
        return (
            False,
            citation_url,
            citation_text,
            f"BLOCKED under {profile.state} cottage-food law: this option qualifies as 'potentially hazardous food' "
            f"requiring a Class B Retail Food Facility permit ($300\u2013$700/yr + commercial kitchen inspection). "
            f"Daily prep also exceeds her {profile.hours_per_week_available} hr/wk constraint.",
        )

    # Weekend cottage-food (e.g. baked/preorder meal packs) typically allowed under Class A
    return True, citation_url, citation_text, None


async def run_reality_compliance(
    opportunities: list[Opportunity], profile: Profile
) -> AsyncIterator[ComplianceCheck]:
    """Yields one ComplianceCheck per opportunity, in rank order."""
    for opp in opportunities:
        constraint_passed, constraint_reasons = _check_constraints(opp, profile)
        legal_passed, cite_url, cite_text, block_reason = await _check_legal(opp, profile)

        if not constraint_passed:
            verdict = "BLOCK"
            block_reason = block_reason or "; ".join(r for r in constraint_reasons if "needs" in r or "requires" in r)
        elif not legal_passed:
            verdict = "BLOCK"
        else:
            verdict = "PASS"

        check = ComplianceCheck(
            opportunity_id=opp.id,
            verdict=verdict,
            constraint_math_passed=constraint_passed,
            constraint_math_reasons=constraint_reasons,
            legal_passed=legal_passed,
            legal_citation_source_url=cite_url,
            legal_citation_text=cite_text,
            block_reason=block_reason,
        )
        log.info(
            "reality_compliance.check",
            extra={"opp": opp.id, "verdict": verdict, "title": opp.title},
        )
        yield check
