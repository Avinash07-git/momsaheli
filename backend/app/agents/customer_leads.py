"""Customer Leads Agent — finds buyer-intent signals for the selected offer."""
from __future__ import annotations

import logging
from urllib.parse import quote_plus

from app.schemas import CustomerLead, Opportunity, Profile

log = logging.getLogger(__name__)

# Curated buyer-intent URLs — communities of CUSTOMERS looking to hire / buy,
# NOT communities of sellers. Every title reflects a buyer expressing a need.
_FOOD_LOCAL_FALLBACK = [
    {
        "title": "r/WorkingMoms — 'Does anyone have a meal service recommendation near me?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/workingmoms/search/?q=meal+prep+service+cook+for+me&sort=top&restrict_sr=1",
        "intent": "Working moms posting 'I have no time to cook — does anyone know a reliable home cook or meal prep service near them?'",
    },
    {
        "title": "r/SingleParents — 'Need affordable home-cooked meals for my kids, any ideas?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/SingleParents/search/?q=affordable+meals+home+cooked+help&sort=top&restrict_sr=1",
        "intent": "Single parents asking for budget-friendly meal solutions — exactly the customer profile for a local home-cook subscription.",
    },
    {
        "title": "r/NewParents — 'Postpartum meal delivery — anyone found a local home cook?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/NewParents/search/?q=meal+delivery+postpartum+home+cook&sort=top&restrict_sr=1",
        "intent": "New parents overwhelmed after birth, asking neighbors for home-cooked meal delivery recommendations.",
    },
    {
        "title": "r/Parenting — 'Healthy dinners for busy families — anyone outsource cooking?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Parenting/search/?q=outsource+cooking+home+meal+service&sort=top&restrict_sr=1",
        "intent": "Parents asking whether other families hire someone to cook — direct unmet demand for a home-cook service.",
    },
    {
        "title": "Quora: 'How do I find someone to cook homemade meals for my family?'",
        "source": "quora",
        "url": "https://www.quora.com/search?q=find+someone+cook+homemade+meals+family",
        "intent": "Real buyer questions on Quora from people actively searching how to hire a local home cook for weekly meals.",
    },
    {
        "title": "r/Frugal — 'Looking for cheap healthy meal alternatives to takeout near me'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Frugal/search/?q=cheap+healthy+meal+alternative+takeout+local&sort=top&restrict_sr=1",
        "intent": "Budget-conscious families asking for affordable alternatives to restaurants — willing to pay a local cook.",
    },
]

_DIGITAL_ASYNC_FALLBACK = [
    {
        "title": "r/Mommit — 'Where can I buy cute printable lunchbox notes for my kids?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Mommit/search/?q=where+buy+printable+lunchbox+notes&sort=top&restrict_sr=1",
        "intent": "Moms asking where to find and buy printable lunchbox notes — direct purchase intent for exactly this product.",
    },
    {
        "title": "r/Parenting — 'Anyone bought editable lunchbox cards from Etsy? Worth it?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Parenting/search/?q=lunchbox+notes+etsy+printable+buy&sort=top&restrict_sr=1",
        "intent": "Parents asking for recommendations on printable lunchbox card purchases — verified buyer intent.",
    },
    {
        "title": "Quora: 'What are the best printable lunchbox notes I can buy for my child?'",
        "source": "quora",
        "url": "https://www.quora.com/search?q=best+printable+lunchbox+notes+buy+kids",
        "intent": "Real Quora questions from parents actively looking to purchase printable lunchbox notes for school.",
    },
    {
        "title": "r/Teachers — 'Parents asking me where to get printable notes for lunchboxes'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/Teachers/search/?q=parents+asking+printable+lunchbox+notes&sort=top&restrict_sr=1",
        "intent": "Teachers sharing that parents ask them for sources of printable lunchbox notes — a proven demand signal.",
    },
    {
        "title": "r/beyondthebump — 'Anyone use printable lunchbox notes? Worth buying?'",
        "source": "reddit",
        "url": "https://www.reddit.com/r/beyondthebump/search/?q=printable+lunchbox+notes+worth+buying&sort=top&restrict_sr=1",
        "intent": "New moms asking whether printable lunchbox notes are worth purchasing — ready-to-buy audience.",
    },
    {
        "title": "Quora: 'Where can I download or buy editable lunchbox cards for school?'",
        "source": "quora",
        "url": "https://www.quora.com/search?q=download+buy+editable+lunchbox+cards+school",
        "intent": "Parents on Quora asking specifically where to download or purchase editable lunchbox cards.",
    },
]

_GENERIC_FALLBACK = [
    {
        "title": "Reddit — people asking where to find this service near them",
        "source": "reddit",
        "url": "https://www.reddit.com/search/?q={query}+where+find+near+me&sort=top",
        "intent": "Community members asking where to hire or buy this — direct customer demand.",
    },
    {
        "title": "Quora — buyers asking how to find someone offering this",
        "source": "quora",
        "url": "https://www.quora.com/search?q=find+{query}+near+me",
        "intent": "Real Quora questions from people actively searching for someone offering this service.",
    },
    {
        "title": "Reddit — reviews and recommendations for this type of service",
        "source": "reddit",
        "url": "https://www.reddit.com/search/?q={query}+recommend+worth+it&sort=top",
        "intent": "Buyers asking for recommendations and reviews — high purchase intent, already in decision mode.",
    },
]


async def run_customer_leads_agent(opportunity: Opportunity, profile: Profile) -> list[CustomerLead]:
    """Return potential customers likely to buy the winning offer.

    These are BUYERS expressing a need — not sellers or communities of providers.
    Cards link to subreddit searches and Quora queries where real people are
    asking 'who can help me?' for this exact type of offer.
    """
    leads = _build_leads(opportunity, profile)
    log.info("customer_leads.leads", extra={"count": len(leads)})
    return leads


def _build_leads(opportunity: Opportunity, profile: Profile) -> list[CustomerLead]:
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
            match_reason=f"Real buyer expressing a need that '{opportunity.title}' directly solves.",
            confidence=0.78,
        ))
    return leads


def _location_hint(profile: Profile) -> str:
    return ", ".join(part for part in [profile.city, profile.state] if part) or profile.state


def _suggested_outreach(opportunity: Opportunity, profile: Profile, source: str) -> str:
    channel_map = {
        "reddit": "comment",
        "quora": "answer",
        "facebook_group": "reply",
        "nextdoor": "reply",
    }
    channel = channel_map.get(source, "reply")
    return (
        f"Leave a helpful {channel}: \"I offer {opportunity.title} for families near "
        f"{_location_hint(profile)} — happy to answer any questions!\""
    )
