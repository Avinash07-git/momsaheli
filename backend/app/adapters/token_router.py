"""TokenRouter adapter — unified LLM routing + caching across providers.

TokenRouter exposes an OpenAI-compatible endpoint that internally routes to
Qwen / Z.ai / others based on smart caching + cost optimization rules.

When TOKEN_ROUTER_API_KEY is set, this becomes the *preferred* path for all
LLM calls. Otherwise we fall through to the direct llm_cascade.
"""
from __future__ import annotations

import logging

import httpx

from app.settings import settings

log = logging.getLogger(__name__)

TOKEN_ROUTER_BASE_URL = "https://api.tokenrouter.com/v1"


async def chat_via_router(
    messages: list[dict[str, str]],
    model: str = "auto",
    temperature: float = 0.3,
    json_mode: bool = False,
    timeout: float = 30.0,
) -> str:
    """Call TokenRouter's OpenAI-compatible endpoint. Raises if not configured."""
    if not settings.TOKEN_ROUTER_API_KEY:
        raise RuntimeError("TOKEN_ROUTER_API_KEY not set")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    headers = {
        "Authorization": f"Bearer {settings.TOKEN_ROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{TOKEN_ROUTER_BASE_URL}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        body = resp.json()
        log.info("token_router.ok", extra={"model": body.get("model", model)})
        return body["choices"][0]["message"]["content"]


def is_configured() -> bool:
    return bool(settings.TOKEN_ROUTER_API_KEY)
