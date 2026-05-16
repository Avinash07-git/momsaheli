"""Resend adapter — customer follow-up and seller action-plan emails."""
from __future__ import annotations

import asyncio
import logging
from html import escape
from urllib.parse import quote

import resend

from app.settings import settings

log = logging.getLogger(__name__)


async def send_reservation_followup(
    slug: str,
    customer_email: str,
    record: dict,
    questions: list[str] | None = None,
) -> dict:
    """Send the first follow-up after a customer reserves a spot.

    Includes Actionbook-drafted intake questions and a link to the response form
    so the customer can share their preferences without replying to an email thread.
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
    response_url = f"{settings.APP_BASE_URL}/launch/{slug}/respond?e={quote(customer_email)}"

    qs = questions or [
        "Do you have any dietary restrictions or food allergies?",
        "How many people are you ordering for?",
        "When do you need it by?",
        "Any special requests or notes?",
    ]

    params: dict = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [customer_email],
        "subject": f"Quick questions about your {offer_name} order",
        "html": _reservation_html(display_name, offer_name, price, unit, landing_url, response_url, qs, packet),
        "text": _reservation_text(display_name, offer_name, price, unit, response_url, qs),
    }
    if settings.SELLER_EMAIL:
        params["bcc"] = [settings.SELLER_EMAIL]

    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        message_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        log.info("resend.reservation.sent", extra={"slug": slug, "message_id": message_id})
        return {"sent": True, "message_id": message_id}
    except Exception as e:
        log.warning("resend.reservation.failed", extra={"slug": slug, "err": str(e)[:200]})
        return {"sent": False, "reason": "send_failed"}


async def send_seller_action_plan(
    slug: str,
    customer_email: str,
    offer_name: str,
    plan_text: str,
    preferences: dict,
) -> dict:
    """Email the generated seller action plan to the seller.

    Triggered when a customer submits their intake preferences.
    Always sends to SELLER_EMAIL (danhpcd2016@gmail.com by default).
    """
    if not settings.RESEND_API_KEY or not settings.SELLER_EMAIL:
        log.info("resend.seller_plan.skipped", extra={"slug": slug})
        return {"sent": False, "reason": "missing_api_key_or_seller_email"}

    resend.api_key = settings.RESEND_API_KEY
    params = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [settings.SELLER_EMAIL],
        "subject": f"New order details for {offer_name} — from {customer_email}",
        "html": _seller_plan_html(customer_email, offer_name, slug, plan_text, preferences),
        "text": _seller_plan_text(customer_email, offer_name, plan_text, preferences),
    }

    try:
        response = await asyncio.to_thread(resend.Emails.send, params)
        message_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", None)
        log.info("resend.seller_plan.sent", extra={"slug": slug, "message_id": message_id})
        return {"sent": True, "message_id": message_id}
    except Exception as e:
        log.warning("resend.seller_plan.failed", extra={"slug": slug, "err": str(e)[:200]})
        return {"sent": False, "reason": "send_failed"}


# ── HTML builders ────────────────────────────────────────────────────────────

def _reservation_html(
    display_name: str, offer_name: str, price, unit: str,
    landing_url: str, response_url: str, questions: list[str], packet: dict,
) -> str:
    price_line = _price_line(price, unit)
    qs_html = "".join(f"<li style='margin-bottom:6px'>{escape(q)}</li>" for q in questions)
    return f"""
    <div style="font-family:Inter,Arial,sans-serif;line-height:1.6;color:#1f2937;max-width:560px">
      <h1 style="font-family:Georgia,serif;color:#92400e;margin-bottom:4px">You're on the list! 🎉</h1>
      <p style="color:#6b7280;margin-top:0">Thanks for reserving a spot for
        <strong>{escape(str(offer_name))}</strong>.</p>
      <p>{escape(str(display_name))} is getting ready for you. {escape(price_line)}</p>

      <div style="background:#fef3c7;border:1px solid #fde68a;border-radius:12px;padding:20px 24px;margin:24px 0">
        <p style="margin-top:0;font-weight:600;color:#92400e">
          Before {escape(str(display_name))} gets started, just a few quick questions:
        </p>
        <ol style="padding-left:20px;margin:0;color:#374151">
          {qs_html}
        </ol>
      </div>

      <p style="margin:24px 0">
        <a href="{escape(response_url)}"
           style="background:#d97706;color:white;padding:14px 24px;border-radius:10px;
                  text-decoration:none;font-weight:700;display:inline-block">
          Share your preferences →
        </a>
      </p>

      <p style="font-size:13px;color:#9ca3af">
        Or reply to this email if it's easier — we'll take care of the rest.
      </p>
      <hr style="border:none;border-top:1px solid #f3f4f6;margin:24px 0"/>
      <p style="font-size:12px;color:#d1d5db">
        Powered by <a href="/" style="color:#d97706">Mom's Saheli</a> ·
        <a href="{escape(landing_url)}" style="color:#d97706">View launch page</a>
      </p>
    </div>
    """


def _reservation_text(
    display_name: str, offer_name: str, price, unit: str,
    response_url: str, questions: list[str],
) -> str:
    qs_lines = "\n".join(f"  {i+1}. {q}" for i, q in enumerate(questions))
    return "\n".join([
        f"You're on the list for {offer_name}!",
        "",
        f"{display_name} is getting ready for you. {_price_line(price, unit)}",
        "",
        "Before we get started, a few quick questions:",
        qs_lines,
        "",
        f"Share your preferences here: {response_url}",
        "",
        "Or just reply to this email — we'll take care of the rest.",
        "",
        "Powered by Mom's Saheli",
    ])


def _seller_plan_html(
    customer_email: str, offer_name: str, slug: str, plan_text: str, preferences: dict,
) -> str:
    pref_rows = "".join(
        f"<tr><td style='padding:6px 12px 6px 0;color:#6b7280;font-size:13px;white-space:nowrap'>"
        f"{escape(str(k).replace('_', ' ').title())}</td>"
        f"<td style='padding:6px 0;font-size:13px;color:#111827'>{escape(str(v))}</td></tr>"
        for k, v in preferences.items() if v and k not in {"raw_response", "submitted_at"}
    )
    plan_html = "<br/>".join(escape(line) for line in plan_text.strip().splitlines() if line.strip())
    return f"""
    <div style="font-family:Inter,Arial,sans-serif;line-height:1.6;color:#1f2937;max-width:600px">
      <div style="background:#d1fae5;border-left:4px solid #10b981;padding:16px 20px;border-radius:8px;margin-bottom:24px">
        <p style="margin:0;font-weight:700;color:#065f46">
          New response from {escape(customer_email)}
        </p>
        <p style="margin:4px 0 0;font-size:13px;color:#065f46">
          Offer: {escape(offer_name)}
        </p>
      </div>

      <h2 style="font-family:Georgia,serif;color:#1f2937;margin-bottom:8px">
        Customer Preferences
      </h2>
      <table style="border-collapse:collapse;margin-bottom:24px">
        {pref_rows if pref_rows else '<tr><td style="color:#6b7280;font-size:13px">(See raw response below)</td></tr>'}
      </table>

      <h2 style="font-family:Georgia,serif;color:#1f2937;margin-bottom:8px">
        Your Action Plan
      </h2>
      <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:20px 24px;
                  font-size:14px;line-height:1.7;color:#374151">
        {plan_html}
      </div>

      <div style="margin-top:24px;padding:16px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px">
        <p style="margin:0;font-size:13px;color:#92400e">
          Raw customer response:<br/>
          <em>{escape(str(preferences.get("raw_response", "—")))}</em>
        </p>
      </div>

      <hr style="border:none;border-top:1px solid #f3f4f6;margin:24px 0"/>
      <p style="font-size:12px;color:#d1d5db">Powered by Mom's Saheli</p>
    </div>
    """


def _seller_plan_text(
    customer_email: str, offer_name: str, plan_text: str, preferences: dict,
) -> str:
    pref_lines = "\n".join(
        f"  {k.replace('_', ' ').title()}: {v}"
        for k, v in preferences.items() if v and k not in {"raw_response", "submitted_at"}
    )
    return "\n".join([
        f"New response from {customer_email} for {offer_name}",
        "",
        "=== Customer Preferences ===",
        pref_lines or "(see raw response)",
        "",
        "=== Your Action Plan ===",
        plan_text,
        "",
        f"Raw response: {preferences.get('raw_response', '—')}",
        "",
        "Powered by Mom's Saheli",
    ])


def _price_line(price, unit: str) -> str:
    try:
        return f"Launch price: ${float(price):.2f} per {unit}."
    except Exception:
        return "The seller will confirm pricing in the follow-up."
