"""LLM cascade adapter.

Routes through TokenRouter when configured. Falls back to direct Qwen Cloud,
then Z.ai (GLM). All three use OpenAI-compatible chat-completions APIs.

Single async entrypoint: `chat(messages, schema=None, model=None)`.
"""
from __future__ import annotations

import json
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from app.settings import settings

log = logging.getLogger(__name__)


class LLMCascadeError(Exception):
    """All providers in the cascade failed."""


async def _call_openai_compatible(
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    response_format: dict | None = None,
    temperature: float = 0.3,
    timeout: float = 30.0,
) -> str:
    """Call any OpenAI-compatible /chat/completions endpoint. Returns the assistant text."""
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format is not None:
        payload["response_format"] = response_format

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{base_url.rstrip('/')}/chat/completions"

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()
        return body["choices"][0]["message"]["content"]


@retry(stop=stop_after_attempt(2), wait=wait_exponential_jitter(initial=0.5, max=2.0), reraise=True)
async def _try_qwen(messages, response_format, temperature) -> str:
    if not settings.QWEN_API_KEY:
        raise LLMCascadeError("QWEN_API_KEY not set")
    return await _call_openai_compatible(
        base_url=settings.QWEN_BASE_URL,
        api_key=settings.QWEN_API_KEY,
        model=settings.QWEN_MODEL,
        messages=messages,
        response_format=response_format,
        temperature=temperature,
    )


@retry(stop=stop_after_attempt(2), wait=wait_exponential_jitter(initial=0.5, max=2.0), reraise=True)
async def _try_zai(messages, response_format, temperature) -> str:
    if not settings.ZAI_API_KEY:
        raise LLMCascadeError("ZAI_API_KEY not set")
    return await _call_openai_compatible(
        base_url=settings.ZAI_BASE_URL,
        api_key=settings.ZAI_API_KEY,
        model=settings.ZAI_MODEL,
        messages=messages,
        response_format=response_format,
        temperature=temperature,
    )


async def chat(
    messages: list[dict[str, str]],
    json_mode: bool = False,
    temperature: float = 0.3,
) -> str:
    """Call the LLM cascade. Returns text (raw or JSON string if json_mode).

    Cascade order: Qwen → Z.ai. (TokenRouter integration lives in token_router.py and
    can be enabled by setting QWEN_BASE_URL to the TokenRouter endpoint.)
    """
    response_format = {"type": "json_object"} if json_mode else None
    last_err: Exception | None = None

    for provider_name, provider_fn in [("qwen", _try_qwen), ("zai", _try_zai)]:
        try:
            log.info("llm.cascade.try", extra={"provider": provider_name})
            text = await provider_fn(messages, response_format, temperature)
            log.info("llm.cascade.ok", extra={"provider": provider_name, "len": len(text)})
            return text
        except Exception as e:
            log.warning("llm.cascade.fail", extra={"provider": provider_name, "err": str(e)[:200]})
            last_err = e

    raise LLMCascadeError(f"All providers failed. Last: {last_err}")


async def chat_json(messages: list[dict[str, str]], temperature: float = 0.3) -> dict:
    """Convenience: cascade chat + JSON parse."""
    text = await chat(messages, json_mode=True, temperature=temperature)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        # Some models wrap in ```json ... ``` — try to recover
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
