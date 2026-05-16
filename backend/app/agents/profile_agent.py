"""Profile Agent — normalizes user input into a structured Profile."""
from __future__ import annotations

import logging
import re
from uuid import uuid4

from app.adapters import llm_cascade
from app.schemas import Profile

log = logging.getLogger(__name__)


async def run_profile_agent(raw_profile: dict) -> Profile:
    """Validate + normalize the raw intake into our Profile schema.

    In Phase 1 the presets already match the schema, so this is a validating pass-through.
    In Phase 2 we'd ask Qwen to extract a Profile from free-text intake.
    """
    profile = Profile.model_validate(raw_profile)
    log.info(
        "profile_agent.ok",
        extra={"persona_id": profile.persona_id, "constraints": profile.hard_constraints},
    )
    return profile


async def profile_from_text(query: str) -> Profile:
    """Convert a user's plain-English situation into the Profile schema.

    Use this when the user is not selecting a demo persona. The LLM path handles
    messy natural language; the deterministic fallback keeps the hackathon demo
    usable when model keys are missing or rate-limited.
    """
    query = query.strip()
    if not query:
        raise ValueError("Profile text is empty")

    try:
        result = await llm_cascade.chat_json(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract a Mom's Saheli Profile from plain English. "
                        "Return strict JSON with keys: display_name, day_job, "
                        "income_gap_monthly_usd, hours_per_week_available, skills, "
                        "budget_startup_usd, state, city, hard_constraints, notes. "
                        "Use a 2-letter US state code. Use conservative defaults when "
                        "missing: display_name='Friend', day_job='working mom', "
                        "income_gap_monthly_usd=500, hours_per_week_available=5, "
                        "budget_startup_usd=100, state='CA'. "
                        "Hard constraints should use these tokens when applicable: "
                        "no_nights, no_daily_delivery, no_delivery, no_commercial_kitchen, "
                        "no_permit, weekends_only, child_pickup, fully_async, no_phone_calls, "
                        "no_inventory."
                    ),
                },
                {"role": "user", "content": query},
            ],
            temperature=0.1,
        )
        payload = _coerce_profile_payload(result, query)
        return Profile.model_validate(payload)
    except Exception as e:
        log.warning("profile_from_text.fallback", extra={"err": str(e)[:200]})
        return Profile.model_validate(_fallback_profile_payload(query))


def agent_execution_plan() -> list[dict[str, str]]:
    """The user-facing plan for the swarm run."""
    return [
        {"agent": "Profile Agent", "task": "Normalize the user request into skills, hours, budget, state, and constraints."},
        {"agent": "Market Scout", "task": "Gather live market evidence and rank realistic income paths."},
        {"agent": "Customer Leads", "task": "Find buyer-intent posts and searches from people who might use the offer."},
        {"agent": "Reality & Compliance", "task": "Check each path against time, budget, and state rules with citations."},
        {"agent": "Launch Agent", "task": "Generate the winning offer, pricing, copy, outreach, and 7-day plan."},
        {"agent": "Memory Agent", "task": "Store the trajectory and surface a reusable learning pattern."},
    ]


def _coerce_profile_payload(raw: dict, query: str) -> dict:
    payload = dict(raw)
    payload["persona_id"] = payload.get("persona_id") or f"custom_{uuid4().hex[:8]}"
    display_name = (payload.get("display_name") or "Friend").strip()
    if display_name.lower() in {"friend", "mom", "user"}:
        display_name = _guess_name(query)
    payload["display_name"] = display_name[:40]
    payload["day_job"] = (payload.get("day_job") or "working mom").strip()[:120]
    payload["income_gap_monthly_usd"] = _bounded_int(payload.get("income_gap_monthly_usd"), 500, 0, 10_000)
    payload["hours_per_week_available"] = _bounded_int(payload.get("hours_per_week_available"), 5, 1, 40)
    payload["budget_startup_usd"] = _bounded_int(payload.get("budget_startup_usd"), 100, 0, 5_000)
    payload["state"] = _normalize_state(str(payload.get("state") or "")) or _guess_state(query) or "CA"
    payload["city"] = _clean_city(payload.get("city"), payload["state"]) or _guess_city(query)
    payload["skills"] = _clean_list(payload.get("skills")) or _guess_skills(query)
    payload["hard_constraints"] = _clean_list(payload.get("hard_constraints")) or _guess_constraints(query)
    payload["notes"] = (payload.get("notes") or query)[:500]
    return payload


def _fallback_profile_payload(query: str) -> dict:
    return {
        "persona_id": f"custom_{uuid4().hex[:8]}",
        "display_name": _guess_name(query),
        "day_job": _guess_day_job(query),
        "income_gap_monthly_usd": _guess_money(query, default=500, patterns=[r"\$?\s*(\d{2,5})\s*(?:/|per)?\s*(?:mo|month)", r"income gap\D{0,20}(\d{2,5})"]),
        "hours_per_week_available": _guess_money(query, default=5, patterns=[r"(\d{1,2})\s*(?:hours|hrs|hr|h)\s*(?:/|per)?\s*(?:week|wk)", r"(\d{1,2})\s*(?:hours|hrs|hr|h)\b"]),
        "budget_startup_usd": _guess_money(query, default=100, patterns=[r"budget\D{0,20}\$?\s*(\d{1,5})", r"\$\s*(\d{1,5})\s*(?:budget|to start|startup)"]),
        "state": _guess_state(query) or "CA",
        "city": _guess_city(query),
        "skills": _guess_skills(query),
        "hard_constraints": _guess_constraints(query),
        "notes": query[:500],
    }


def _bounded_int(value, default: int, low: int, high: int) -> int:
    try:
        parsed = int(value)
    except Exception:
        parsed = default
    return max(low, min(high, parsed))


def _clean_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(v).strip() for v in value if str(v).strip()]


def _guess_money(text: str, default: int, patterns: list[str]) -> int:
    for pattern in patterns:
        m = re.search(pattern, text, flags=re.I)
        if m:
            return _bounded_int(m.group(1).replace(",", ""), default, 0, 10_000)
    return default


def _guess_name(text: str) -> str:
    m = re.search(r"(?:my name is|i am|i'm)\s+([A-Z][a-z]{1,30})", text, flags=re.I)
    return m.group(1) if m else "Friend"


def _guess_day_job(text: str) -> str:
    m = re.search(r"(?:work as|working as|job is|i am a|i'm a|i am an|i'm an)\s+([^.,;]{3,80})", text, flags=re.I)
    return m.group(1).strip() if m else "working mom"


_STATES = {
    "california": "CA", "ca": "CA", "texas": "TX", "tx": "TX", "new york": "NY", "ny": "NY",
    "florida": "FL", "fl": "FL", "illinois": "IL", "il": "IL", "georgia": "GA", "ga": "GA",
    "washington": "WA", "wa": "WA", "arizona": "AZ", "az": "AZ", "virginia": "VA", "va": "VA",
    "north carolina": "NC", "nc": "NC", "michigan": "MI", "mi": "MI", "ohio": "OH", "oh": "OH",
}


def _normalize_state(value: str) -> str | None:
    return _STATES.get(value.strip().lower())


def _guess_state(text: str) -> str | None:
    t = text.lower()
    for key, code in sorted(_STATES.items(), key=lambda item: len(item[0]), reverse=True):
        if re.search(rf"\b{re.escape(key)}\b", t):
            return code
    return None


def _guess_city(text: str) -> str | None:
    m = re.search(r"\b(?:in|near|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", text)
    if not m:
        return None
    city = m.group(1)
    state = _guess_state(text)
    return _clean_city(city, state)


def _clean_city(value, state: str | None) -> str | None:
    if not value:
        return None
    city = str(value).strip()
    if not city:
        return None
    if state:
        state_names = [name for name, code in _STATES.items() if code == state and len(name) > 2]
        for name in state_names + [state]:
            city = re.sub(rf"\b{re.escape(name)}\b", "", city, flags=re.I).strip(" ,")
    return city or None


def _guess_skills(text: str) -> list[str]:
    t = text.lower()
    skills: list[str] = []
    keyword_map = [
        ("cooking", ("cook", "cooking", "meal", "tiffin")),
        ("baking", ("bake", "baking", "cookie", "sourdough")),
        ("graphic design", ("design", "canva", "flyer", "logo")),
        ("social media", ("social media", "instagram", "tiktok")),
        ("tutoring", ("tutor", "teach", "homework")),
        ("cleaning", ("clean", "organize", "declutter")),
        ("writing", ("write", "writing", "resume")),
    ]
    for skill, keys in keyword_map:
        if any(k in t for k in keys):
            skills.append(skill)
    return skills or ["organization", "customer service"]


def _guess_constraints(text: str) -> list[str]:
    t = text.lower()
    constraints: list[str] = []
    checks = [
        ("no_nights", ("no nights", "not at night", "evenings are hard")),
        ("no_daily_delivery", ("no daily", "not every day", "weekends only")),
        ("weekends_only", ("weekend", "saturday", "sunday")),
        ("no_delivery", ("no delivery", "no car", "can't drive", "cannot drive")),
        ("no_commercial_kitchen", ("no commercial kitchen",)),
        ("no_permit", ("no permit", "without permit")),
        ("child_pickup", ("pickup", "school pickup", "child pickup")),
        ("fully_async", ("remote", "async", "online only", "from home")),
        ("no_phone_calls", ("no calls", "no phone", "can't talk")),
        ("no_inventory", ("no inventory", "digital only", "nothing physical")),
    ]
    for label, keys in checks:
        if any(k in t for k in keys):
            constraints.append(label)
    return constraints
