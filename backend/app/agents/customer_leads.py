"""Customer Leads Agent — finds buyer-intent signals for the selected offer."""
from __future__ import annotations

import asyncio
import logging
from urllib.parse import quote_plus

from app.adapters import tavily
from app.schemas import CustomerLead, Opportunity, Profile

log = logging.getLogger(__name__)


async def run_customer_leads_agent(opportunity: Opportunity, profile: Profile) -> list[CustomerLead]:
    """Return people/communities likely to buy the winning offer.

    Evidence cards prove "people sell this." Customer leads prove "people ask
    for this." Live Tavily searches are used when configured; deterministic
    fallback cards keep the demo reliable when search is rate-limited.
    """
    queries = _lead_queries(opportunity, profile)
    live_leads = await _live_leads(opportunity, profile, queries)
    if live_leads:
        log.info("customer_leads.live", extra={"count": len(live_leads)})
        return live_leads[:6]

    fallback = _fallback_leads(opportunity, profile, queries)
    log.info("customer_leads.fallback", extra={"count": len(fallback)})
    return fallback


async def _live_leads(opportunity: Opportunity, profile: Profile, queries: list[str]) -> list[CustomerLead]:
    if not tavily.is_configured():
        return []
    try:
        envelopes = await asyncio.gather(
            *(tavily.search(q, max_results=3, search_depth="basic") for q in queries[:2]),
            return_exceptions=True,
        )
    except Exception as e:
        log.warning("customer_leads.search.fail", extra={"err": str(e)[:200]})
        return []

    leads: list[CustomerLead] = []
    seen: set[str] = set()
    for env in envelopes:
        if isinstance(env, Exception) or not isinstance(env, dict):
            continue
        for result in env.get("results", [])[:3]:
            url = result.get("url") or ""
            if not url or url in seen:
                continue
            seen.add(url)
            source = _source_from_url(url)
            content = result.get("content") or result.get("title") or ""
            leads.append(CustomerLead(
                id=f"lead_{len(leads) + 1}",
                title=(result.get("title") or _title_for(opportunity))[:140],
                source=source,
                source_url=url,
                intent_signal=_summarize_intent(content, opportunity),
                location_hint=_location_hint(profile),
                suggested_outreach=_suggested_outreach(opportunity, profile, source),
                match_reason=f"Matches {opportunity.title} because it shows public demand for this kind of help.",
                confidence=0.74 if source in {"reddit", "nextdoor", "facebook_group"} else 0.62,
            ))
    return leads


def _lead_queries(opportunity: Opportunity, profile: Profile) -> list[str]:
    location = " ".join(part for part in [profile.city, profile.state] if part)
    if opportunity.category == "food_local":
        return [
            f'site:reddit.com "{location}" "home cooked meals" "looking for"',
            f'"{location}" "meal prep" "family dinners" "recommend"',
            f'"{location}" "who makes meals" "subscribe"',
        ]
    if opportunity.category == "digital_async":
        return [
            'site:reddit.com parents "lunchbox ideas" printable "need"',
            'site:reddit.com teachers parents "Canva template" "looking for"',
            'parents "printable planner" "where can I buy"',
        ]
    if opportunity.category == "tutoring":
        return [
            f'site:reddit.com "{location}" tutor homework help parents',
            f'"{location}" "looking for tutor" parents',
        ]
    return [
        f'"{location}" "looking for help" "{opportunity.title}"',
        f'site:reddit.com "{opportunity.title}" "need"',
    ]


def _fallback_leads(opportunity: Opportunity, profile: Profile, queries: list[str]) -> list[CustomerLead]:
    location = _location_hint(profile)
    if opportunity.category == "food_local":
        rows = [
            ("Reddit parents asking for easy weekly family dinners", "reddit", queries[0], "Parents asking for home-cooked meal help and recurring dinner ideas."),
            ("Neighborhood search for meal-prep subscriptions", "nextdoor", queries[1], "Local families looking for reliable prepared meals near them."),
            ("Facebook group search for home cooks taking orders", "facebook_group", queries[2], "Community buyers asking who can cook meals for pickup or preorder."),
        ]
    elif opportunity.category == "digital_async":
        rows = [
            ("Reddit parents asking for lunchbox ideas", "reddit", queries[0], "Parents looking for a simple printable solution they can use today."),
            ("Parent groups searching for editable school templates", "facebook_group", queries[1], "Busy parents asking for low-cost digital tools."),
            ("Google demand search for printable planners", "google", queries[2], "Search demand around buying a downloadable planner or template."),
        ]
    else:
        rows = [
            ("Reddit buyer-intent search for this offer", "reddit", queries[0], "People describing the need this offer solves."),
            ("Local community search for likely customers", "local_search", queries[-1], "Nearby customers asking for practical help."),
        ]

    leads: list[CustomerLead] = []
    for i, (title, source, query, intent) in enumerate(rows, start=1):
        leads.append(CustomerLead(
            id=f"lead_{i}",
            title=title,
            source=source,  # type: ignore[arg-type]
            source_url=_search_url(source, query),
            intent_signal=intent,
            location_hint=location,
            suggested_outreach=_suggested_outreach(opportunity, profile, source),
            match_reason=f"Buyer intent aligns with {opportunity.title}, not just a seller comp.",
            confidence=0.68,
        ))
    return leads


def _source_from_url(url: str) -> str:
    lowered = url.lower()
    if "reddit.com" in lowered:
        return "reddit"
    if "facebook.com" in lowered:
        return "facebook_group"
    if "nextdoor.com" in lowered:
        return "nextdoor"
    return "google"


def _search_url(source: str, query: str) -> str:
    q = quote_plus(query)
    if source == "reddit":
        return f"https://www.reddit.com/search/?q={q}"
    return f"https://www.google.com/search?q={q}"


def _title_for(opportunity: Opportunity) -> str:
    return f"Buyer intent for {opportunity.title}"


def _location_hint(profile: Profile) -> str:
    return ", ".join(part for part in [profile.city, profile.state] if part) or profile.state


def _summarize_intent(content: str, opportunity: Opportunity) -> str:
    if not content:
        return f"Public post/search result suggests demand for {opportunity.title}."
    return content.strip().replace("\n", " ")[:220]


def _suggested_outreach(opportunity: Opportunity, profile: Profile, source: str) -> str:
    channel = "comment" if source == "reddit" else "reply"
    return (
        f"Leave a helpful {channel}: \"I am testing {opportunity.title} for families near "
        f"{_location_hint(profile)}. Want me to send the simple details?\""
    )
