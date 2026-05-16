"""Resend adapter for launch-page customer follow-up emails."""
from __future__ import annotations

import asyncio
import logging
from html import escape

import resend

from app.settings import settings

log = logging.getLogger(__name__)


async def send_reservation_followup(slug: str, customer_email: str, record: dict) -> dict:
    """Send the first follow-up after a customer reserves a spot.

    Resend's Python SDK is synchronous, so this runs in a worker thread to keep
    FastAPI responsive. If the API key is absent or sending fails, the lead has
    already been persisted and the caller can still return a useful response.
    """
    if not settings.RESEND_API_KEY:
        log.info("resend.skipped", extra={"slug": slug})
        return {"sent": False, "reason": "missing_api_key"}

    resend.api_key = settings.RESEND_API_KEY
    packet = record.get("packet", {})
    display_name = record.get("display_name") or "the seller"
    offer_name = packet.get("offer_name") or "this offer"
    price = packet.get("price_usd")
    unit = packet.get("unit") or "order"
    landing_url = f"{settings.APP_BASE_URL}/launch/{slug}"

    params = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [customer_email],
        "subject": f"You're on the list for {offer_name}",
        "html": _customer_html(display_name, offer_name, price, unit, landing_url, packet),
        "text": _customer_text(display_name, offer_name, price, unit, landing_url, packet),
    }
    if settings.RESEND_OWNER_EMAIL:
        params["bcc"] = [settings.RESEND_OWNER_EMAIL]

    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        message_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        log.info("resend.sent", extra={"slug": slug, "message_id": message_id})
        return {"sent": True, "message_id": message_id}
    except Exception as e:
        log.warning("resend.failed", extra={"slug": slug, "err": str(e)[:200]})
        return {"sent": False, "reason": "send_failed"}


def _customer_html(display_name: str, offer_name: str, price, unit: str, landing_url: str, packet: dict) -> str:
    price_line = _price_line(price, unit)
    plan_items = packet.get("day_plan") or []
    plan_html = "".join(
        f"<li><strong>Day {escape(str(item.get('day', '')))}:</strong> {escape(str(item.get('action', '')))}</li>"
        for item in plan_items[:3]
        if isinstance(item, dict)
    )
    return f"""
    <div style="font-family:Inter,Arial,sans-serif;line-height:1.6;color:#1f2937;max-width:560px">
      <h1 style="font-family:Georgia,serif;color:#92400e">You're on the list.</h1>
      <p>Thanks for reserving a spot for <strong>{escape(str(offer_name))}</strong>.</p>
      <p>{escape(str(display_name))} will follow up with the next details. {escape(price_line)}</p>
      <p style="margin:24px 0">
        <a href="{escape(landing_url)}" style="background:#d97706;color:white;padding:12px 18px;border-radius:8px;text-decoration:none;font-weight:700">
          View the launch page
        </a>
      </p>
      {"<h2 style='font-size:18px'>What happens next</h2><ul>" + plan_html + "</ul>" if plan_html else ""}
      <p style="font-size:13px;color:#6b7280">Powered by Mom's Saheli.</p>
    </div>
    """


def _customer_text(display_name: str, offer_name: str, price, unit: str, landing_url: str, packet: dict) -> str:
    plan_items = packet.get("day_plan") or []
    plan_lines = []
    for item in plan_items[:3]:
        if isinstance(item, dict):
            plan_lines.append(f"Day {item.get('day')}: {item.get('action')}")
    return "\n".join([
        "You're on the list.",
        "",
        f"Thanks for reserving a spot for {offer_name}.",
        f"{display_name} will follow up with the next details. {_price_line(price, unit)}",
        "",
        "What happens next:",
        *plan_lines,
        "",
        f"View the launch page: {landing_url}",
    ])


def _price_line(price, unit: str) -> str:
    try:
        return f"The current launch price is ${float(price):.2f} per {unit}."
    except Exception:
        return "The seller will confirm pricing in the follow-up."
