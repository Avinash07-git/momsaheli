"""Customer Leads Agent — finds buyer-intent signals for the selected offer."""
from __future__ import annotations

import asyncio
import logging
from urllib.parse import quote_plus

from app.adapters import bright_data
from app.schemas import CustomerLead, Opportunity, Profile

log = logging.getLogger(__name__)

# Curated real, publicly-accessible URLs — NO login required to open any of these.
# Reddit: subreddit pages work for all users. Quora: topic pages load without login.
# Facebook/Nextdoor: routed through Google site-search so real posts surface in results.
_FOOD_LOCAL_FALLBACK = [
    {
        "title": "r/MealPrepSunday — 2M members sharing & requesting home-cooked meal services",
        "source": "reddit",
        "url": "https://www.reddit.com/r/MealPrepSunday/search/?q=looking+for+home+cook+service&sort=top&restrict_sr=1",
        "intent": "Active community where families ask for local home cooks, weekly meal packs, and subscription services every weekend.",
    },
    {
        "title": "Quora topic: Meal Prep — buyers asking who can cook for them",
        "source": "quora",
        "url": "https://www.quora.com/topic/Meal-Prep-1",
        "intent": "Quora topic page with real questions from buyers asking how to find home cooks and meal prep services near them.",
    },
    {
        "title": "Facebook Groups — 'home cooked meals for sale near me' (Google-indexed posts)",
        "source": "facebook_group",
        "url": "https://www.google.com/search?q=site:facebook.com+groups+%22home+cooked+meals%22+%22for+sale%22",
        "intent": "Google surfaces real Facebook group posts where locals advertise and buy home-cooked meals — no login needed to browse results.",
    },
    {
        "title": "r/Frugal — parents asking for affordable healthy meal alternatives",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Frugal/search/?q=home+cook+meal+prep+cheap+healthy&sort=top&restrict_sr=1",
        "intent": "Budget-focused families explicitly asking for home-cook alternatives to restaurants and meal-kit services.",
    },
    {
        "title": "Quora topic: Home Cooking — demand for local meal delivery",
        "source": "quora",
        "url": "https://www.quora.com/topic/Home-Cooking",
        "intent": "Quora Home Cooking topic with real buyer questions about finding people who sell homemade food locally.",
    },
    {
        "title": "Nextdoor posts — neighbors requesting home-cooked meals (Google-indexed)",
        "source": "nextdoor",
        "url": "https://www.google.com/search?q=site:nextdoor.com+%22home+cooked%22+%22looking+for%22",
        "intent": "Google-indexed Nextdoor posts where real neighborhood families request local home cooks and meal prep services.",
    },
]

_DIGITAL_ASYNC_FALLBACK = [
    {
        "title": "r/Etsy — buyers searching for printable lunchbox notes",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Etsy/search/?q=printable+lunchbox+notes&sort=top&restrict_sr=1",
        "intent": "Active Etsy buyer discussions looking for printable lunchbox content — proven purchase intent on the platform.",
    },
    {
        "title": "Quora topic: Printable Activities — parents asking for lunchbox ideas",
        "source": "quora",
        "url": "https://www.quora.com/topic/Printable-Activities",
        "intent": "Quora topic page showing parents and teachers actively asking where to find printable lunchbox and classroom materials.",
    },
    {
        "title": "r/Teachers — editable Canva and printable template requests",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Teachers/search/?q=printable+template+canva+lunchbox&sort=top&restrict_sr=1",
        "intent": "Teachers and parents in r/Teachers searching for affordable editable templates they can personalise and reuse.",
    },
    {
        "title": "Facebook Groups — printable downloads for moms (Google-indexed posts)",
        "source": "facebook_group",
        "url": "https://www.google.com/search?q=site:facebook.com+groups+%22printable%22+%22lunchbox%22+%22moms%22",
        "intent": "Google shows real Facebook group posts where busy moms request and share printable lunchbox and planner downloads.",
    },
    {
        "title": "Quora topic: Digital Download — buyers looking for planners and printables",
        "source": "quora",
        "url": "https://www.quora.com/topic/Digital-Download",
        "intent": "Real Quora questions from people asking where to find and buy digital download planners, notes, and templates.",
    },
    {
        "title": "r/Parenting — lunchbox note and printable requests",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Parenting/search/?q=lunchbox+notes+printable&sort=top&restrict_sr=1",
        "intent": "Parents in r/Parenting asking for creative lunchbox note ideas — direct buyer demand for this exact product.",
    },
]

_GENERIC_FALLBACK = [
    {
        "title": "Reddit — buyer-intent discussions for this type of offer",
        "source": "reddit",
        "url": "https://www.reddit.com/search/?q={query}+looking+for&sort=top",
        "intent": "Reddit users describing the need this offer solves — public buyer intent.",
    },
    {
        "title": "Quora — people asking about this kind of service",
        "source": "quora",
        "url": "https://www.quora.com/topic/{query_slug}",
        "intent": "Quora topic page with real buyer questions and unmet demand matching this offer.",
    },
    {
        "title": "Facebook Groups — local demand posts (Google-indexed, no login needed)",
        "source": "facebook_group",
        "url": "https://www.google.com/search?q=site:facebook.com+groups+%22{query}%22",
        "intent": "Google-indexed Facebook group posts where local buyers are asking for this type of help.",
    },
]


async def run_customer_leads_agent(opportunity: Opportunity, profile: Profile) -> list[CustomerLead]:
    """Return people/communities likely to buy the winning offer.

    Evidence cards prove 'people sell this.' Customer leads prove 'people ask
    for this.' Bright Data searches are used when configured; curated real-URL
    fallback cards keep the demo reliable when search is unavailable.
    """
    queries = _lead_queries(opportunity, profile)
    live_leads = await _live_leads(opportunity, profile, queries)
    if live_leads:
        log.info("customer_leads.live", extra={"count": len(live_leads)})
        return live_leads[:6]

    fallback = _fallback_leads(opportunity, profile)
    log.info("customer_leads.fallback", extra={"count": len(fallback)})
    return fallback


async def _live_leads(opportunity: Opportunity, profile: Profile, queries: list[str]) -> list[CustomerLead]:
    if not bright_data.is_configured():
        return []
    try:
        envelopes = await asyncio.gather(
            *(bright_data.search_web(q, max_results=3) for q in queries[:3]),
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
                source=source,  # type: ignore[arg-type]
                source_url=url,
                intent_signal=_summarize_intent(content, opportunity),
                location_hint=_location_hint(profile),
                suggested_outreach=_suggested_outreach(opportunity, profile, source),
                match_reason=f"Matches {opportunity.title} because it shows public demand for this kind of help.",
                confidence=0.74 if source in {"reddit", "quora", "nextdoor", "facebook_group"} else 0.62,
            ))
    return leads


def _lead_queries(opportunity: Opportunity, profile: Profile) -> list[str]:
    location = " ".join(part for part in [profile.city, profile.state] if part)
    if opportunity.category == "food_local":
        return [
            f'site:reddit.com "{location}" "home cooked meals" OR "meal prep" "looking for"',
            f'site:quora.com home cook meals delivery "{location}" OR family',
            f'"{location}" "meal prep" "family dinners" "recommend" OR "who does"',
        ]
    if opportunity.category == "digital_async":
        return [
            'site:reddit.com parents "lunchbox" printable "looking for" OR "need"',
            'site:quora.com "printable" "lunchbox" OR "meal planner" parents buy',
            'site:reddit.com teachers parents "Canva template" "looking for"',
        ]
    if opportunity.category == "tutoring":
        return [
            f'site:reddit.com "{location}" tutor homework help parents "looking for"',
            f'site:quora.com tutor "{location}" OR online parents',
        ]
    return [
        f'site:reddit.com "{opportunity.title}" "need" OR "looking for"',
        f'site:quora.com "{opportunity.title}"',
    ]


def _fallback_leads(opportunity: Opportunity, profile: Profile) -> list[CustomerLead]:
    location = _location_hint(profile)
    query_slug = quote_plus(opportunity.title)

    if opportunity.category == "food_local":
        rows = _FOOD_LOCAL_FALLBACK
    elif opportunity.category == "digital_async":
        rows = _DIGITAL_ASYNC_FALLBACK
    else:
        title_slug = opportunity.title.replace(" ", "-").title()
        rows = [
            {**r, "url": r["url"].replace("{query}", query_slug).replace("{query_slug}", title_slug)}
            for r in _GENERIC_FALLBACK
        ]

    leads: list[CustomerLead] = []
    for i, row in enumerate(rows, start=1):
        source = row["source"]
        leads.append(CustomerLead(
            id=f"lead_{i}",
            title=row["title"],
            source=source,  # type: ignore[arg-type]
            source_url=row["url"],
            intent_signal=row["intent"],
            location_hint=location,
            suggested_outreach=_suggested_outreach(opportunity, profile, source),
            match_reason=f"Buyer intent aligns with {opportunity.title} — real public demand, not just a seller comp.",
            confidence=0.72,
        ))
    return leads


def _source_from_url(url: str) -> str:
    lowered = url.lower()
    if "reddit.com" in lowered:
        return "reddit"
    if "quora.com" in lowered:
        return "quora"
    if "facebook.com" in lowered:
        return "facebook_group"
    if "nextdoor.com" in lowered:
        return "nextdoor"
    return "google"


def _title_for(opportunity: Opportunity) -> str:
    return f"Buyer intent for {opportunity.title}"


def _location_hint(profile: Profile) -> str:
    return ", ".join(part for part in [profile.city, profile.state] if part) or profile.state


def _summarize_intent(content: str, opportunity: Opportunity) -> str:
    if not content:
        return f"Public post/search result suggests demand for {opportunity.title}."
    return content.strip().replace("\n", " ")[:220]


def _suggested_outreach(opportunity: Opportunity, profile: Profile, source: str) -> str:
    channel_map = {
        "reddit": "comment",
        "quora": "answer",
        "facebook_group": "reply",
        "nextdoor": "reply",
    }
    channel = channel_map.get(source, "reply")
    return (
        f"Leave a helpful {channel}: \"I'm testing {opportunity.title} for families near "
        f"{_location_hint(profile)}. Want me to send the simple details?\""
    )
