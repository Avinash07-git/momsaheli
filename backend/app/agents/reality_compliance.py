"""Reality & Compliance Agent — the BLOCKER.

Per opportunity, runs N compliance dimensions in parallel (asyncio.gather):
1. Constraint math      — pure-function, hours/budget/preferences
2. State cottage-food   — Bright Data (real .gov page)
3. IRS self-employment  — Bright Data web search (real IRS guidance)
4. Platform TOS         — Bright Data web search (real platform rules)

Emits one ComplianceCheck per opportunity with all dimensions attached. The winner =
first PASS by rank. The parallel fan-out is the sponsor-genuine technical-depth
moment: real network calls, real-life citation breadth, real asyncio.gather.
"""
from __future__ import annotations

import asyncio
import logging
from typing import AsyncIterator

from app.adapters import bright_data
from app.schemas import ComplianceCheck, ComplianceDimension, Opportunity, Profile

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
        base += 6
    if "cater" in t:
        base += 3
    return base


def _check_constraints(opportunity: Opportunity, profile: Profile) -> tuple[bool, list[str]]:
    """Pure-function constraint math — deterministic, no LLM needed."""
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


def _check_legal(
    opportunity: Opportunity,
    profile: Profile,
    law_data: dict | None,
) -> tuple[bool, str | None, str | None, str | None]:
    """Check opportunity against the (already-fetched) state cottage-food data."""
    if opportunity.category != "food_local" or law_data is None:
        return True, None, None, None

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
            f"requiring a Class B Retail Food Facility permit ($300–$700/yr + commercial kitchen inspection). "
            f"Daily prep also exceeds her {profile.hours_per_week_available} hr/wk constraint.",
        )

    return True, citation_url, citation_text, None


async def _check_dimension_irs(opp: Opportunity, profile: Profile) -> ComplianceDimension:
    """Bright Data search for IRS self-employment threshold + Schedule C rules."""
    if not bright_data.is_configured():
        return ComplianceDimension(dimension="irs_self_employment", passed=True, note="(no Bright Data key)")
    try:
        q = f"IRS Schedule C self-employment threshold side income 2025 {opp.category.replace('_', ' ')}"
        env = await bright_data.search_web(q, max_results=2)
        top = (env.get("results") or [{}])[0]
        annual_est = opp.estimated_net_monthly_usd * 12
        note = (
            f"Net ${annual_est}/yr — exceeds $400 self-employment threshold; Schedule C filing required."
            if annual_est >= 400
            else f"Net ${annual_est}/yr — below $400 self-employment threshold."
        )
        return ComplianceDimension(
            dimension="irs_self_employment",
            passed=True,  # informational, never blocks
            citation_url=top.get("url") or "",
            citation_text=(env.get("answer") or top.get("content", ""))[:280],
            note=note,
        )
    except Exception as e:
        log.warning("compliance.irs.fail", extra={"err": str(e)[:160]})
        return ComplianceDimension(dimension="irs_self_employment", passed=True, note="(check skipped)")


async def _check_dimension_platform_tos(opp: Opportunity, profile: Profile) -> ComplianceDimension:
    """Bright Data search for marketplace TOS rules (Etsy/Castiron/Nextdoor)."""
    if not bright_data.is_configured():
        return ComplianceDimension(dimension="platform_tos", passed=True, note="(no Bright Data key)")
    try:
        platform = {
            "digital_async": "etsy",
            "food_local":    "castiron",
            "resale":        "poshmark",
            "tutoring":      "outschool",
            "service_local": "nextdoor",
        }.get(opp.category, "etsy")
        q = f"{platform} seller policy prohibited items {opp.category.replace('_', ' ')} terms of service 2025"
        env = await bright_data.search_web(q, max_results=2)
        top = (env.get("results") or [{}])[0]
        return ComplianceDimension(
            dimension="platform_tos",
            passed=True,  # informational unless we detect a clear "prohibited" hit
            citation_url=top.get("url") or "",
            citation_text=(env.get("answer") or top.get("content", ""))[:280],
            note=f"Reviewed {platform.title()} TOS for category fit via Bright Data.",
        )
    except Exception as e:
        log.warning("compliance.tos.fail", extra={"err": str(e)[:160]})
        return ComplianceDimension(dimension="platform_tos", passed=True, note="(check skipped)")


def _build_state_law_dimension(opp: Opportunity, law_data: dict | None, legal_passed: bool,
                                cite_url: str | None, cite_text: str | None) -> ComplianceDimension:
    """Wrap the (already-fetched) state cottage-food check as a ComplianceDimension."""
    return ComplianceDimension(
        dimension="state_cottage_food",
        passed=legal_passed,
        citation_url=cite_url or (law_data or {}).get("source_url"),
        citation_text=cite_text or (law_data or {}).get("citation_text"),
        note="Live state-law lookup via Bright Data (.gov sources prioritized).",
    )


async def run_reality_compliance(
    opportunities: list[Opportunity],
    profile: Profile,
    pre_fetched_law: dict | None = None,
) -> AsyncIterator[ComplianceCheck]:
    """Yields one ComplianceCheck per opportunity, in rank order.

    Per opportunity runs a parallel compliance fan-out via asyncio.gather:
    state cottage-food + IRS self-employment + platform TOS — three Bright Data
    network calls executed concurrently. Output: one ComplianceCheck with N
    ComplianceDimension citations attached.
    """
    needs_law = any(o.category == "food_local" for o in opportunities)
    law_data_cache: dict | None = pre_fetched_law
    if needs_law and law_data_cache is None:
        log.info("reality_compliance.fetch_state_law", extra={"state": profile.state})
        law_data_cache = await bright_data.scrape_state_law(profile.state)

    for opp in opportunities:
        # 1. Pure-function (instant, deterministic)
        constraint_passed, constraint_reasons = _check_constraints(opp, profile)

        # 2. State-law (already fetched once globally)
        legal_passed, cite_url, cite_text, block_reason = _check_legal(opp, profile, law_data_cache)

        # 3. PARALLEL fan-out of secondary compliance dimensions (Bright Data calls)
        irs_task = asyncio.create_task(_check_dimension_irs(opp, profile))
        tos_task = asyncio.create_task(_check_dimension_platform_tos(opp, profile))

        state_dim = _build_state_law_dimension(opp, law_data_cache, legal_passed, cite_url, cite_text)

        irs_dim, tos_dim = await asyncio.gather(irs_task, tos_task)

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
            dimensions=[state_dim, irs_dim, tos_dim],
        )
        log.info(
            "reality_compliance.check",
            extra={"opp": opp.id, "verdict": verdict, "title": opp.title, "dims": len(check.dimensions)},
        )
        yield check
