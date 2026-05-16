"""Market Scout — gathers evidence (Actionbook + Bright Data) and ranks opportunities (Qwen)."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from app.adapters import actionbook, bright_data, llm_cascade
from app.schemas import EvidenceCard, Opportunity, Profile

log = logging.getLogger(__name__)


def _persona_sources(profile: Profile) -> list[tuple[str, str, str]]:
    """Pick (adapter, source_slug, query) tuples appropriate for the persona.

    Etsy is for DIGITAL/HANDMADE only. Food goes to Castiron / Nextdoor /
    local Facebook groups — those are the *real* marketplaces home cooks use.
    """
    constraints = set(profile.hard_constraints)
    skills = " ".join(profile.skills).lower()

    is_digital_first = (
        "no_delivery" in constraints
        or "fully_async" in constraints
        or "no_inventory" in constraints
    )

    if is_digital_first:
        # Etsy + Poshmark are correct for digital products
        return [
            ("actionbook_etsy", "etsy", "kids lunch printable"),
            ("brightdata_comps", "poshmark", "digital download printable"),
        ]

    if "cooking" in skills or "meal" in skills:
        # Food: Castiron/Nextdoor/FB groups via Bright Data; NO Etsy
        return [
            ("foodlocal", "castiron", "weekend family meal pack"),
        ]

    # Generic fallback
    return [
        ("actionbook_etsy", "etsy", "home craft"),
        ("brightdata_comps", "poshmark", "handmade goods"),
    ]


async def gather_evidence(profile: Profile) -> AsyncIterator[EvidenceCard]:
    """Yields EvidenceCards as they arrive from the persona-appropriate adapters."""
    source_plan = _persona_sources(profile)

    tasks: list = []
    for adapter, source_slug, query in source_plan:
        if adapter == "actionbook_etsy":
            tasks.append((source_slug, asyncio.create_task(actionbook.live_etsy_search(query))))
        elif adapter == "brightdata_comps":
            tasks.append((source_slug, asyncio.create_task(bright_data.scrape_market_comps(query, source=source_slug))))
        elif adapter == "foodlocal":
            tasks.append((source_slug, asyncio.create_task(bright_data.scrape_food_local_comps(profile))))

    for source_slug, task in tasks:
        result = await task
        listings = result.get("listings", []) if isinstance(result, dict) else result
        for raw in listings:
            yield EvidenceCard.model_validate(raw)


async def rank_opportunities(profile: Profile, cards: list[EvidenceCard]) -> list[Opportunity]:
    """Use the LLM cascade to synthesize ranked opportunities from raw evidence cards."""
    if not cards:
        return []

    system = (
        "You are Market Scout for Mom's Saheli — an agent that surfaces income opportunities "
        "for a working mom from observed market evidence. "
        "\n\n"
        "CRITICAL: Surface ALL distinct opportunities from the evidence cards — including "
        "high-revenue options that may later fail the compliance check. The Reality & "
        "Compliance agent that runs AFTER you is responsible for blocking unsafe / illegal / "
        "constraint-violating options with cited law. DO NOT pre-filter for compliance — "
        "surfacing the high-paying option that ultimately gets BLOCKED is how the user sees "
        "the system protect her from financially-tempting but illegal paths."
        "\n\n"
        "Output strict JSON: {\"opportunities\": [{\"id\": str, \"title\": str, \"category\": "
        "\"food_local\"|\"digital_async\"|\"service_local\"|\"resale\"|\"tutoring\", "
        "\"evidence_card_ids\": [str], \"rank\": int, \"rationale\": str, "
        "\"estimated_net_monthly_usd\": int, \"requires_permit\": bool}]}. "
        "Include one Opportunity per evidence card (so the user sees the full picture). "
        "Rank by realistic NET monthly income (highest first; lower rank number = better). "
        "Set requires_permit=true for any food category involving prepared meals or daily delivery."
    )
    user = json.dumps({
        "profile": profile.model_dump(mode="json"),
        "evidence_cards": [c.model_dump(mode="json") for c in cards],
    })

    try:
        result = await llm_cascade.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.2,
        )
        opps = [Opportunity.model_validate(o) for o in result.get("opportunities", [])]
        opps.sort(key=lambda o: o.rank)
        log.info("market_scout.ranked", extra={"count": len(opps)})
        return opps
    except Exception as e:
        log.warning("market_scout.llm_fallback", extra={"err": str(e)[:200]})
        # Fallback: heuristic ranking on net income alone
        opps = []
        sorted_cards = sorted(cards[:6], key=lambda c: c.estimated_net_monthly_usd, reverse=True)
        for i, c in enumerate(sorted_cards):
            opps.append(Opportunity(
                id=f"opp_{i+1}",
                title=c.title,
                category=_guess_category(c.title),
                evidence_card_ids=[c.id],
                rank=i + 1,
                rationale=f"Based on {c.source} comp at ${c.observed_price_usd}. {c.observed_volume_signal}.",
                estimated_net_monthly_usd=c.estimated_net_monthly_usd,
                requires_permit=_guess_requires_permit(c.title),
            ))
        return opps


FOOD_KEYWORDS = ("meal", "food", "tiffin", "lunch delivery", "cater", "bake", "cook", "meal pack", "meal-pack", "meal prep", "daily", "subscription")
DIGITAL_KEYWORDS = ("printable", "digital", "download", "pdf", "template", "planner", "canva", "editable")
RESALE_KEYWORDS = ("container", "resale", "used", "set of", "pre-owned")


def _guess_category(title: str) -> str:
    t = title.lower()
    if any(k in t for k in DIGITAL_KEYWORDS):
        return "digital_async"
    if any(k in t for k in FOOD_KEYWORDS):
        return "food_local"
    if any(k in t for k in RESALE_KEYWORDS):
        return "resale"
    return "service_local"


def _guess_requires_permit(title: str) -> bool:
    return _guess_category(title) == "food_local"


async def run_market_scout(profile: Profile) -> tuple[list[EvidenceCard], list[Opportunity]]:
    """Full Market Scout pipeline: gather evidence, then rank opportunities."""
    cards: list[EvidenceCard] = []
    async for card in gather_evidence(profile):
        cards.append(card)
    opportunities = await rank_opportunities(profile, cards)
    return cards, opportunities
