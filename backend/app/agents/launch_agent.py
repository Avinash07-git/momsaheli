"""Launch Agent — turns the winning opportunity into a shippable launch packet, then publishes it."""
from __future__ import annotations

import json
import logging
import re
from typing import Any

from app.adapters import actionbook, butterbase, llm_cascade
from app.schemas import LaunchPacket, Opportunity, Profile

log = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:60] or "launch"


async def generate_packet(opportunity: Opportunity, profile: Profile) -> LaunchPacket:
    """Use the LLM cascade to draft the launch packet."""
    system = (
        "You are Launch Agent for Mom's Saheli. Take a winning Opportunity + the user's Profile "
        "and output a strict-JSON LaunchPacket with these fields: "
        "opportunity_id, offer_name, offer_tagline, price_usd (number), unit, description_markdown, "
        "target_customer, outreach_drafts (list of {channel:'nextdoor'|'facebook_group'|'text_friends'|"
        "'etsy_listing'|'instagram', subject?, body_markdown}), and day_plan "
        "(list of 7 {day:int 1..7, action:str, estimated_minutes:int}). "
        "Make the copy warm but not saccharine. Concrete numbers. No jargon. No emojis in the offer_name."
    )
    user = json.dumps({
        "opportunity": opportunity.model_dump(mode="json"),
        "profile": profile.model_dump(mode="json"),
    })

    try:
        raw: dict[str, Any] = await llm_cascade.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.5,
        )
        # Some models nest under "launch_packet"; flatten if so
        if "launch_packet" in raw:
            raw = raw["launch_packet"]
        raw.setdefault("opportunity_id", opportunity.id)
        packet = LaunchPacket.model_validate(raw)
        log.info("launch_agent.packet_ok", extra={"offer_name": packet.offer_name})
        return packet
    except Exception as e:
        log.warning("launch_agent.llm_fallback", extra={"err": str(e)[:200]})
        return _fallback_packet(opportunity, profile)


def _fallback_packet(opp: Opportunity, profile: Profile) -> LaunchPacket:
    """Deterministic packet if the LLM fails — ensures the demo never breaks."""
    is_digital = opp.category == "digital_async"
    return LaunchPacket(
        opportunity_id=opp.id,
        offer_name=opp.title,
        offer_tagline="Made with care, on your schedule.",
        price_usd=12.0 if is_digital else 50.0,
        unit="per download" if is_digital else "per pack",
        description_markdown=(
            f"**{opp.title}**\n\n"
            f"A {'digital' if is_digital else 'weekend'} offer built around "
            f"{profile.display_name}'s real schedule "
            f"({profile.hours_per_week_available} hr/wk) and skills "
            f"({', '.join(profile.skills[:3])}).\n\n"
            f"_{opp.rationale}_"
        ),
        target_customer=("Busy parents looking for printable, ready-to-use kits."
                         if is_digital else "Local families wanting home-cooked weekend meals."),
        outreach_drafts=[
            {
                "channel": "nextdoor",
                "subject": None,
                "body_markdown": f"Hi neighbors! I'm starting **{opp.title}** — DM me if you'd like to be on the early-bird list.",
            },
            {
                "channel": "facebook_group",
                "subject": None,
                "body_markdown": f"New on the block: **{opp.title}**. First 10 orders get a thank-you discount.",
            },
            {
                "channel": "text_friends",
                "subject": None,
                "body_markdown": f"Hey! Starting something small — **{opp.title}**. Mind sharing with anyone who'd love it? 🙏",
            },
        ],
        day_plan=[
            {"day": 1, "action": "Take 5 product photos in natural light.", "estimated_minutes": 30},
            {"day": 2, "action": "Post Nextdoor + Facebook group teaser.", "estimated_minutes": 20},
            {"day": 3, "action": "Text 5 friends with the link.", "estimated_minutes": 15},
            {"day": 4, "action": "Collect first orders. Reply within 1 hour.", "estimated_minutes": 30},
            {"day": 5, "action": ("Prep first batch." if not is_digital else "Polish the printable PDF."), "estimated_minutes": 60},
            {"day": 6, "action": ("Deliver / hand-off." if not is_digital else "Email customers the file."), "estimated_minutes": 45},
            {"day": 7, "action": "Ask for a 1-line review. Plan week 2.", "estimated_minutes": 15},
        ],
    )


async def publish(packet: LaunchPacket, profile: Profile) -> str:
    """Save the packet to Butterbase and (optionally) trigger Actionbook to publish the page."""
    slug = f"{profile.persona_id}-{_slugify(packet.offer_name)}"

    public_url = await butterbase.save_launch_page(slug=slug, packet=packet, display_name=profile.display_name)
    actionbook_result = await actionbook.publish_launch_page(slug=slug, landing_url=public_url)
    log.info(
        "launch_agent.published",
        extra={"slug": slug, "url": public_url, "actionbook_ok": actionbook_result.get("ok", False)},
    )
    return public_url


async def run_launch_agent(opportunity: Opportunity, profile: Profile) -> tuple[LaunchPacket, str]:
    packet = await generate_packet(opportunity, profile)
    public_url = await publish(packet, profile)
    return packet, public_url
