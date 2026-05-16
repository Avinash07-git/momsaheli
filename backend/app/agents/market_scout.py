"""Market Scout — gathers evidence (Actionbook + Bright Data) and ranks opportunities (Qwen)."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncIterator

from app.adapters import actionbook, bright_data, llm_cascade
from app.schemas import EvidenceCard, Opportunity, Profile

log = logging.getLogger(__name__)


def _query_for_persona(profile: Profile) -> tuple[str, str]:
    """Pick (etsy_query, poshmark_query) based on persona skills + constraints."""
    skills = " ".join(profile.skills).lower()
    if "no_delivery" in profile.hard_constraints or "fully_async" in profile.hard_constraints:
        return ("kids lunch printable", "digital download printable")
    if "cooking" in skills or "meal" in skills:
        return ("weekend family meal pack", "meal prep containers")
    return ("home craft", "handmade goods")


async def gather_evidence(profile: Profile) -> AsyncIterator[EvidenceCard]:
    """Yields EvidenceCards as they arrive from Actionbook + Bright Data."""
    etsy_q, poshmark_q = _query_for_persona(profile)

    etsy_task = asyncio.create_task(actionbook.live_etsy_search(etsy_q))
    poshmark_task = asyncio.create_task(bright_data.scrape_market_comps(poshmark_q, source="poshmark"))

    # Yield Etsy listings first (the visible "real browser" moment)
    etsy_result = await etsy_task
    for raw in etsy_result.get("listings", []):
        yield EvidenceCard.model_validate(raw)

    # Then yield Poshmark comps
    poshmark_result = await poshmark_task
    for raw in poshmark_result:
        yield EvidenceCard.model_validate(raw)


async def rank_opportunities(profile: Profile, cards: list[EvidenceCard]) -> list[Opportunity]:
    """Use the LLM cascade to synthesize ranked opportunities from raw evidence cards."""
    if not cards:
        return []

    system = (
        "You are Market Scout for Mom's Saheli — an agent that picks the highest-realistic-NET-income "
        "side-income opportunity for a working mom under hard constraints. "
        "Given a profile and evidence cards, output 3-6 ranked Opportunity objects as strict JSON "
        "in the schema: {\"opportunities\": [{\"id\": str, \"title\": str, \"category\": "
        "\"food_local\"|\"digital_async\"|\"service_local\"|\"resale\"|\"tutoring\", "
        "\"evidence_card_ids\": [str], \"rank\": int, \"rationale\": str, "
        "\"estimated_net_monthly_usd\": int, \"requires_permit\": bool}]}. "
        "Rank by realistic NET monthly income that fits her hours/budget/constraints. "
        "Lower rank = better. NEVER recommend something that obviously violates her hard_constraints."
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
