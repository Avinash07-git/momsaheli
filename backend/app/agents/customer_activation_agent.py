"""Customer Activation Agent — plans the approval-gated first-customer move."""
from __future__ import annotations

import logging
from typing import Any

from app.adapters import bright_data
from app.schemas import LaunchPacket, Opportunity, Profile
from app.schemas.action import ActionCandidate, ActivationPlan, ApprovedChannel, CustomerLead

log = logging.getLogger(__name__)

SAFETY_NOTES = [
    "No post or submission happens without explicit approval.",
    "Private group members are never scraped.",
    "Public demand posts are review links, not permission to contact private people.",
    "Fixture fallback leads are labeled as fallback.",
]


async def run_customer_activation_agent(
    profile: Profile,
    winner: Opportunity,
    launch_packet: LaunchPacket,
) -> ActivationPlan:
    """Plan first-customer acquisition without executing external actions."""
    raw_leads: list[dict[str, Any]] = []
    try:
        raw_leads = await bright_data.search_customer_leads(profile, winner, limit=6)
    except Exception as e:  # noqa: BLE001 - this agent must never dead-end a run
        log.warning("customer_activation.search_fallback_empty", extra={"err": str(e)[:200]})

    leads = _normalize_public_leads(raw_leads)
    leads.extend(_approved_channel_leads(profile, existing_ids={lead.id for lead in leads}))
    leads = _dedupe_leads(leads)
    if not leads:
        leads.append(_manual_lead(profile, winner))

    messages = _build_messages(profile, winner, launch_packet)
    actions = _build_actions(profile, winner, launch_packet, leads, messages)
    if not actions:
        actions = [_manual_action(profile, winner, launch_packet, messages)]

    recommended_id = max(actions, key=lambda a: a.priority_score).id if actions else None
    used_live_search = any(lead.live_source for lead in leads)

    return ActivationPlan(
        opportunity_id=winner.id,
        mom_display_name=profile.display_name,
        summary=(
            f"{profile.display_name}'s fastest safe path is to start with warm, permissioned "
            f"customer access for {launch_packet.offer_name}, then use public vendor or "
            "marketplace paths as the next layer."
        ),
        recommended_first_action_id=recommended_id,
        leads=leads,
        actions=actions,
        launch_message_short=messages["short"],
        launch_message_friendly=messages["friendly"],
        launch_message_formal=messages["formal"],
        safety_notes=SAFETY_NOTES,
        used_live_search=used_live_search,
    )


def _normalize_public_leads(raw_leads: list[dict[str, Any]]) -> list[CustomerLead]:
    leads: list[CustomerLead] = []
    for i, raw in enumerate(raw_leads):
        if not isinstance(raw, dict):
            continue
        try:
            prepared = dict(raw)
            prepared.setdefault("id", f"customer_lead_{i + 1}")
            prepared["confidence"] = _clamp(float(prepared.get("confidence", 0.55)))
            leads.append(CustomerLead.model_validate(prepared))
        except Exception as e:  # noqa: BLE001 - skip malformed adapter result
            log.debug("customer_activation.skip_bad_lead", extra={"err": str(e)[:160]})
    return leads


def _approved_channel_leads(profile: Profile, existing_ids: set[str]) -> list[CustomerLead]:
    leads: list[CustomerLead] = []
    for channel in profile.approved_channels:
        lead_id = channel.id or f"approved_{channel.type}_{len(leads) + 1}"
        if lead_id in existing_ids:
            continue
        source_type = "warm_network" if channel.type in {"friends_text", "email"} else "approved_group"
        audience = channel.audience or f"{profile.display_name}'s approved {channel.type.replace('_', ' ')}"
        leads.append(CustomerLead(
            id=lead_id,
            title=channel.name,
            source_type=source_type,
            source_url=channel.url,
            audience_match=audience,
            why_relevant="The mom has explicitly approved this channel for first-customer outreach.",
            estimated_reach=audience,
            confidence=0.92 if channel.user_approved else 0.58,
            live_source=False,
            provider="profile_approved_channel",
            notes=channel.rules_summary,
        ))
    return leads


def _dedupe_leads(leads: list[CustomerLead]) -> list[CustomerLead]:
    seen: set[tuple[str, str | None]] = set()
    deduped: list[CustomerLead] = []
    for lead in leads:
        key = (lead.title.lower().strip(), lead.source_url)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(lead)
    return deduped


def _dedupe_actions(actions: list[ActionCandidate]) -> list[ActionCandidate]:
    seen: set[tuple[str, str, str | None]] = set()
    deduped: list[ActionCandidate] = []
    for action in actions:
        key = (action.type, action.destination_name.lower().strip(), action.linked_lead_id)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(action)
    return deduped


def _build_messages(profile: Profile, winner: Opportunity, packet: LaunchPacket) -> dict[str, str]:
    city = f" in {profile.city}" if profile.city else ""
    price = f"${packet.price_usd:.0f} {packet.unit}"
    short = (
        f"{packet.offer_name}: {packet.offer_tagline} {price}. "
        "Reply if you want the first opening."
    )
    friendly = (
        f"Hi! I'm {profile.display_name}, a working mom{city}. I'm starting a small, realistic side gig: "
        f"{packet.offer_name} for {packet.target_customer.lower()}. "
        f"It's {price}, and I'm taking a few early requests first so I can keep it manageable. "
        "Message me if this would help your family or someone you know."
    )
    formal = (
        f"Hello, I'm {profile.display_name}{city}. I'm launching {packet.offer_name}, "
        f"a {winner.category.replace('_', ' ')} offer for {packet.target_customer.lower()}. "
        f"The first offer is {price}. Please let me know whether this is a fit for your vendor, "
        "community, or parent resource process."
    )
    return {"short": short, "friendly": friendly, "formal": formal}


def _build_actions(
    profile: Profile,
    winner: Opportunity,
    packet: LaunchPacket,
    leads: list[CustomerLead],
    messages: dict[str, str],
) -> list[ActionCandidate]:
    actions: list[ActionCandidate] = []
    lead_by_id = {lead.id: lead for lead in leads}

    for channel in profile.approved_channels:
        action = _action_from_channel(channel, profile, packet, messages, lead_by_id)
        if action:
            actions.append(action)

    for lead in leads:
        if lead.source_type in {"approved_group", "warm_network"}:
            continue
        action = _action_from_public_lead(lead, profile, packet, messages)
        if action:
            actions.append(action)

    if winner.category == "digital_async":
        has_digital_listing = any(a.type in {"marketplace_listing", "instagram_post"} for a in actions)
        if not has_digital_listing:
            preferred = set(profile.preferred_channels)
            action_type = "instagram_post" if "instagram" in preferred else "marketplace_listing"
            title = "Draft an Instagram launch post" if action_type == "instagram_post" else "Draft a marketplace listing"
            action = _candidate(
                action_type=action_type,
                title=title,
                destination_name="Preferred digital launch channel",
                destination_url=None,
                linked_lead=None,
                effort_minutes=20,
                risk_level="low",
                execution_mode="draft_only",
                draft_text=messages["friendly"] if action_type == "instagram_post" else messages["formal"],
                form_fields=None,
                profile=profile,
                reason_detail="Digital offers can be tested asynchronously without inventory or delivery.",
            )
            actions.append(action)

    return sorted(_dedupe_actions(actions), key=lambda a: a.priority_score, reverse=True)


def _action_from_channel(
    channel: ApprovedChannel,
    profile: Profile,
    packet: LaunchPacket,
    messages: dict[str, str],
    lead_by_id: dict[str, CustomerLead],
) -> ActionCandidate | None:
    lead = lead_by_id.get(channel.id)
    if channel.type == "whatsapp_group" and channel.user_approved:
        return _candidate(
            action_type="whatsapp_post",
            title=f"Post one approved intro in {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=5,
            risk_level="medium",
            execution_mode="post_after_review",
            draft_text=messages["friendly"],
            form_fields=None,
            profile=profile,
            user_approved=True,
            reason_detail="Approved local mom groups have high audience match and fast feedback.",
        )
    if channel.type == "friends_text" and channel.user_approved:
        return _candidate(
            action_type="warm_text",
            title=f"Send a warm draft to {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=8,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["short"],
            form_fields=None,
            profile=profile,
            user_approved=True,
            reason_detail="Warm parent contacts are likely to reply or refer without public posting.",
        )
    if channel.type == "email" and channel.user_approved:
        return _candidate(
            action_type="email",
            title=f"Draft an email for {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=12,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["formal"],
            form_fields=None,
            profile=profile,
            user_approved=True,
            reason_detail="Email keeps the outreach reviewable and asynchronous.",
        )
    if channel.type == "vendor_form" and channel.user_approved:
        return _candidate(
            action_type="vendor_form_fill",
            title=f"Preview vendor form fields for {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=25,
            risk_level="medium",
            execution_mode="fill_no_submit",
            draft_text=None,
            form_fields=_form_fields(profile, packet, messages["formal"]),
            profile=profile,
            user_approved=True,
            reason_detail="Vendor forms can create a concrete sales path without submitting anything yet.",
        )
    if channel.type == "marketplace" and channel.user_approved:
        return _candidate(
            action_type="marketplace_listing",
            title=f"Draft listing copy for {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=20,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["formal"],
            form_fields=None,
            profile=profile,
            user_approved=True,
            reason_detail="Marketplace listing drafts fit async validation without inventory commitments.",
        )
    if channel.type == "instagram" and channel.user_approved:
        return _candidate(
            action_type="instagram_post",
            title=f"Draft an Instagram post for {channel.name}",
            destination_name=channel.name,
            destination_url=channel.url,
            linked_lead=lead,
            effort_minutes=15,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["friendly"],
            form_fields=None,
            profile=profile,
            user_approved=True,
            reason_detail="Instagram stays draft-only here so the mom reviews the exact public copy first.",
        )
    return None


def _action_from_public_lead(
    lead: CustomerLead,
    profile: Profile,
    packet: LaunchPacket,
    messages: dict[str, str],
) -> ActionCandidate | None:
    if lead.source_type in {"vendor_form", "school_page", "event_page"}:
        return _candidate(
            action_type="vendor_form_fill",
            title=f"Preview form fields for {lead.title}",
            destination_name=lead.title,
            destination_url=lead.source_url,
            linked_lead=lead,
            effort_minutes=30,
            risk_level="medium",
            execution_mode="fill_no_submit",
            draft_text=None,
            form_fields=_form_fields(profile, packet, messages["formal"]),
            profile=profile,
            reason_detail="Public vendor paths are designed for inbound business requests.",
        )
    if lead.source_type == "marketplace":
        return _candidate(
            action_type="marketplace_listing",
            title=f"Draft listing for {lead.title}",
            destination_name=lead.title,
            destination_url=lead.source_url,
            linked_lead=lead,
            effort_minutes=25,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["formal"],
            form_fields=None,
            profile=profile,
            reason_detail="Marketplace paths can validate demand without private scraping.",
        )
    if lead.source_type in {"community_page", "public_demand_post", "local_directory", "manual"}:
        return _candidate(
            action_type="manual_step",
            title=f"Review public customer path: {lead.title}",
            destination_name=lead.title,
            destination_url=lead.source_url,
            linked_lead=lead,
            effort_minutes=15,
            risk_level="low",
            execution_mode="draft_only",
            draft_text=messages["short"],
            form_fields=None,
            profile=profile,
            reason_detail=(
                "This is a public demand signal or path to review manually; "
                "it does not authorize scraping or direct contact."
            ),
        )
    return None


def _candidate(
    action_type: str,
    title: str,
    destination_name: str,
    destination_url: str | None,
    linked_lead: CustomerLead | None,
    effort_minutes: int,
    risk_level: str,
    execution_mode: str,
    draft_text: str | None,
    form_fields: dict[str, str] | None,
    profile: Profile,
    reason_detail: str,
    user_approved: bool = False,
) -> ActionCandidate:
    score, factors = _score_action(
        action_type=action_type,
        lead=linked_lead,
        effort_minutes=effort_minutes,
        execution_mode=execution_mode,
        profile=profile,
        user_approved=user_approved,
    )
    reason = (
        f"{reason_detail} Score uses audience {factors['audience_match']:.2f}, "
        f"first-customer likelihood {factors['first_customer_likelihood']:.2f}, "
        f"permission {factors['permission_confidence']:.2f}, speed {factors['speed']:.2f}, "
        f"and effort {factors['low_effort']:.2f}."
    )
    return ActionCandidate(
        id=f"act_{action_type}_{linked_lead.id if linked_lead else _slug(destination_name)}",
        type=action_type,  # type: ignore[arg-type]
        title=title,
        destination_name=destination_name,
        destination_url=destination_url,
        linked_lead_id=linked_lead.id if linked_lead else None,
        priority_score=score,
        reason=reason,
        expected_outcome=_expected_outcome(action_type),
        effort_minutes=effort_minutes,
        risk_level=risk_level,  # type: ignore[arg-type]
        execution_mode=execution_mode,  # type: ignore[arg-type]
        draft_text=draft_text,
        form_fields=form_fields,
    )


def _score_action(
    action_type: str,
    lead: CustomerLead | None,
    effort_minutes: int,
    execution_mode: str,
    profile: Profile,
    user_approved: bool,
) -> tuple[float, dict[str, float]]:
    audience_match = lead.confidence if lead else 0.65
    if lead and lead.source_type in {"approved_group", "warm_network"}:
        audience_match = max(audience_match, 0.88)

    likelihood_by_type = {
        "whatsapp_post": 0.88,
        "warm_text": 0.84,
        "email": 0.72,
        "vendor_form_fill": 0.70,
        "marketplace_listing": 0.64,
        "instagram_post": 0.58,
        "facebook_group_post": 0.70,
        "nextdoor_post": 0.66,
        "manual_step": 0.50,
    }
    first_customer_likelihood = likelihood_by_type.get(action_type, 0.55)

    if user_approved:
        permission_confidence = 0.95
    elif execution_mode == "draft_only":
        permission_confidence = 0.82
    elif execution_mode == "fill_no_submit":
        permission_confidence = 0.78
    else:
        permission_confidence = 0.60

    if profile.marketing_permission_level == "post_after_review":
        permission_confidence = min(1.0, permission_confidence + 0.03)

    speed = 0.95 if effort_minutes <= 5 else 0.85 if effort_minutes <= 15 else 0.70 if effort_minutes <= 30 else 0.50
    low_effort = _clamp(1 - (effort_minutes / 75))
    score = (
        0.30 * audience_match
        + 0.25 * first_customer_likelihood
        + 0.20 * permission_confidence
        + 0.15 * speed
        + 0.10 * low_effort
    )
    factors = {
        "audience_match": audience_match,
        "first_customer_likelihood": first_customer_likelihood,
        "permission_confidence": permission_confidence,
        "speed": speed,
        "low_effort": low_effort,
    }
    return round(score, 3), factors


def _form_fields(profile: Profile, packet: LaunchPacket, message: str) -> dict[str, str]:
    city_state = ", ".join(part for part in [profile.city, profile.state] if part)
    return {
        "contact_name": profile.display_name,
        "city_state": city_state,
        "offer_name": packet.offer_name,
        "offer_price": f"${packet.price_usd:.0f} {packet.unit}",
        "offer_summary": packet.description_markdown[:500],
        "customer_fit": packet.target_customer,
        "message": message,
    }


def _manual_action(
    profile: Profile,
    winner: Opportunity,
    packet: LaunchPacket,
    messages: dict[str, str],
) -> ActionCandidate:
    lead = _manual_lead(profile, winner)
    return _candidate(
        action_type="manual_step",
        title="Review the first customer draft manually",
        destination_name="Manual review",
        destination_url=None,
        linked_lead=lead,
        effort_minutes=10,
        risk_level="low",
        execution_mode="draft_only",
        draft_text=messages["short"],
        form_fields=None,
        profile=profile,
        reason_detail=f"This keeps {packet.offer_name} moving without using any private source.",
    )


def _manual_lead(profile: Profile, winner: Opportunity) -> CustomerLead:
    return CustomerLead(
        id="manual_first_customer_path",
        title="Manual first-customer review",
        source_type="manual",
        source_url=None,
        audience_match=f"{profile.display_name}'s known parent/customer network",
        why_relevant=f"No live public customer path was found for {winner.title}, so start with reviewed draft outreach.",
        estimated_reach=None,
        confidence=0.50,
        live_source=False,
        provider="fixture_fallback",
        notes="Fallback manual step; no external source was scraped.",
    )


def _expected_outcome(action_type: str) -> str:
    return {
        "whatsapp_post": "A small number of local moms can reply or refer the first customer.",
        "warm_text": "A trusted contact can reply, refer, or sanity-check the offer.",
        "email": "A reviewed email can start a low-pressure customer conversation.",
        "vendor_form_fill": "The mom gets a completed preview before any vendor submission.",
        "marketplace_listing": "The offer gets marketplace-ready copy for async validation.",
        "instagram_post": "The mom gets exact public post copy to review first.",
        "manual_step": "The mom reviews one public customer path before taking action.",
    }.get(action_type, "The mom gets one approval-gated next step.")


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")[:60] or "target"


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))
