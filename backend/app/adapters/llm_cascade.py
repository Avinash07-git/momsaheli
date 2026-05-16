"""LLM cascade adapter.

Cascade order (live-key-first):
  1. Gemini 2.5 Flash       — free, fast, our primary today
  2. Qwen Cloud             — our primary tomorrow (sponsor)
  3. Z.ai (GLM)             — fallback

TokenRouter, when configured, takes precedence over all of them.
All provider calls use OpenAI-compatible chat-completions shape
except Gemini which uses the google-generativeai SDK natively.

Single async entrypoint: `chat(messages, json_mode=False)`.
"""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

from app.adapters import token_router
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
async def _try_gemini(messages, response_format, temperature) -> str:
    """Call Google Gemini via the google-generativeai SDK.
    Gemini supports JSON mode natively via generation_config.
    """
    if not settings.GEMINI_API_KEY:
        raise LLMCascadeError("GEMINI_API_KEY not set")

    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    import google.generativeai as genai  # type: ignore

    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Merge system + user messages into one prompt (Gemini Python SDK pattern)
    system_parts = [m["content"] for m in messages if m["role"] == "system"]
    user_parts = [m["content"] for m in messages if m["role"] == "user"]
    system_prompt = "\n\n".join(system_parts) if system_parts else None
    user_prompt = "\n\n".join(user_parts)

    gen_config: dict[str, Any] = {"temperature": temperature}
    if response_format and response_format.get("type") == "json_object":
        gen_config["response_mime_type"] = "application/json"

    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system_prompt,
        generation_config=gen_config,
    )

    # google-generativeai is sync; offload to a thread so we stay non-blocking
    resp = await asyncio.to_thread(model.generate_content, user_prompt)
    return resp.text


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

    Cascade order: Gemini → Qwen → Z.ai. TokenRouter integration lives in
    token_router.py and can be enabled by setting TOKEN_ROUTER_API_KEY.
    """
    response_format = {"type": "json_object"} if json_mode else None
    last_err: Exception | None = None

    if token_router.is_configured():
        try:
            log.info("llm.cascade.try", extra={"provider": "token_router"})
            text = await token_router.chat_via_router(
                messages=messages,
                temperature=temperature,
                json_mode=json_mode,
            )
            log.info("llm.cascade.ok", extra={"provider": "token_router", "len": len(text)})
            return text
        except Exception as e:
            log.warning("llm.cascade.fail", extra={"provider": "token_router", "err": str(e)[:200]})
            last_err = e

    providers: list[tuple[str, Any]] = [
        ("gemini", _try_gemini),
        ("qwen", _try_qwen),
        ("zai", _try_zai),
    ]

    for provider_name, provider_fn in providers:
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
    except json.JSONDecodeError:
        # Some models wrap in ```json ... ``` — try to recover
        cleaned = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
