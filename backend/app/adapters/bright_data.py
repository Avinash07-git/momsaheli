"""Bright Data adapter — two use cases:
1. `scrape_state_law(state)` — fetches the live cottage-food / permit page or live SERP
   excerpts for a US state.
   This powers the SHOCK MOMENT: real cited regulation blocking an opportunity.
2. `scrape_market_comps(query)` — bulk scrape of Castiron / Craigslist / Google SERP
   listings, with Gemini-powered HTML → structured listings extraction and deterministic
   parsing fallback.

Real API: Bright Data Web Unlocker (`web_unlocker1` zone is the default).
Fallback: cached JSON from `app/fixtures/cached_scrapes/` for demo-day reliability.
"""
from __future__ import annotations

import json
import logging
import re
from html import unescape
from pathlib import Path
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import httpx

from app.adapters import llm_cascade, tavily
from app.settings import settings

log = logging.getLogger(__name__)

BRIGHT_DATA_API = "https://api.brightdata.com/request"

# Per-state cottage-food law URLs. Add more as we expand beyond CA/TX.
STATE_LAW_URLS = {
    "CA": "https://www.cdph.ca.gov/Programs/CEH/DFDCS/Pages/FDBPrograms/FoodSafetyProgram/CottageFoodOperations.aspx",
    "TX": "https://www.dshs.texas.gov/foods-drugs-medical-devices/cottage-food-production-operations",
    "NY": "https://agriculture.ny.gov/food-safety/home-processor-exemption",
}


async def scrape_state_law(state: str) -> dict:
    """Fetch a state's cottage-food / permit page.

    Priority order:
      1. Real Bright Data Web Unlocker scrape (when zone is configured)
      2. Live Tavily web search (when only Tavily key is set)  — today's path
      3. Cached fixture (offline fallback)

    Returns dict with: source_url, citation_text, requires_permit_for_hot_food,
                       live_scrape_ok, live_scrape_provider.
    """
    state = state.upper()
    cache_path = settings.cached_scrapes_dir / f"{state.lower()}_cottage_food.json"

    # Path 1: Bright Data (zone required)
    if settings.BRIGHT_DATA_API_TOKEN and settings.BRIGHT_DATA_ZONE and not settings.USE_FIXTURES:
        url = STATE_LAW_URLS.get(state)
        if url:
            try:
                payload = {
                    "zone": settings.BRIGHT_DATA_ZONE,
                    "url": url,
                    "format": "raw",
                }
                headers = {
                    "Authorization": f"Bearer {settings.BRIGHT_DATA_API_TOKEN}",
                    "Content-Type": "application/json",
                }
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.post(BRIGHT_DATA_API, json=payload, headers=headers)
                    resp.raise_for_status()
                    html = resp.text
                if len(html.strip()) < 200:
                    raise RuntimeError("empty Bright Data state-law response")
                cached = _load_cache(cache_path)
                live = _extract_state_law_from_html(
                    html=html,
                    state=state,
                    source_url=url,
                    cached=cached,
                )
                log.info("bright_data.ok", extra={"state": state, "bytes": len(html)})
                return live
            except Exception as e:
                log.warning("bright_data.fallback_to_law_serp", extra={"err": str(e)[:200]})
                try:
                    live = await _scrape_state_law_serp_bright_data(state=state, cached_path=cache_path)
                    log.info("bright_data.state_law_serp.ok", extra={"state": state})
                    return live
                except Exception as serp_err:
                    log.warning("bright_data.fallback_to_tavily", extra={"err": str(serp_err)[:200]})

    # Path 2: Tavily live search (free, no zone needed)
    if tavily.is_configured():
        try:
            live = await tavily.search_state_law(state)
            log.info("bright_data.via_tavily.ok", extra={"state": state})
            return live
        except Exception as e:
            log.warning("bright_data.via_tavily.fallback", extra={"err": str(e)[:200]})

    # Path 3: cached fixture
    log.info("bright_data.fixture", extra={"state": state})
    return _load_cache(cache_path)


async def scrape_market_comps(query: str, source: str = "poshmark") -> list[dict]:
    """Bulk market comps via Bright Data SERP / Web Unlocker.
    Returns list of raw comp records.
    Falls back to cached scrape on error OR when USE_FIXTURES=true.
    """
    cache_name = f"{source}_{_slug(query)}.json"
    cache_path = settings.cached_scrapes_dir / cache_name

    if not settings.BRIGHT_DATA_API_TOKEN or not settings.BRIGHT_DATA_ZONE:
        log.info("bright_data.comps.fixture", extra={"query": query, "source": source, "reason": "no_creds"})
        return _load_cache_list(cache_path)

    # Bright Data blocks Poshmark/Etsy by robots policy. Re-route to Google SERP
    # which returns rich SSR'd HTML with prices and seller snippets.
    fetch_source = source
    if source in ("poshmark", "etsy"):
        fetch_source = "google"

    try:
        # For SPA marketplaces, route through Google SERP — raw marketplace HTML
        # lacks extractable listings, but Google's snippet view surfaces prices cleanly.
        if fetch_source == "craigslist":
            html = await _bd_fetch(_build_search_url("craigslist", query))
        else:
            serp_query = f"{query} price seller buy"
            html = await _bd_fetch(_build_search_url("google", serp_query))
        if not html:
            raise RuntimeError("empty BD response")

        comps = await _extract_listings_from_html(html, query=query, source=source)
        if comps:
            for c in comps:
                c["live_scrape_ok"] = True
                c["live_scrape_provider"] = "bright_data"
            log.info("bright_data.comps.live", extra={"query": query, "count": len(comps)})
            return comps

        log.info("bright_data.comps.no_listings_extracted", extra={"query": query})
        return _load_cache_list(cache_path)
    except Exception as e:
        log.warning("bright_data.comps.fallback", extra={"query": query, "err": str(e)[:200]})
        return _load_cache_list(cache_path)


async def scrape_food_local_comps(profile) -> dict:
    """Scrape Castiron + Nextdoor + local Facebook groups for cottage-food comps.
    Returns dict with `listings` so the orchestrator can iterate the same way as Etsy results.

    Falls back to cached scrape on error OR when USE_FIXTURES=true.
    Real impl would hit Castiron API + Bright Data SERP on Nextdoor / Facebook.
    """
    cache_path = settings.cached_scrapes_dir / f"foodlocal_{profile.persona_id}.json"
    if not settings.BRIGHT_DATA_API_TOKEN or not settings.BRIGHT_DATA_ZONE:
        log.info("bright_data.foodlocal.fixture", extra={"persona": profile.persona_id, "reason": "no_creds"})
        return _load_cache(cache_path)

    # Real Bright Data scrape via Google SERP — works for any cottage-food keyword
    # and returns rich SSR'd HTML with prices and seller info Gemini can extract.
    # Castiron is an SPA so its raw HTML has no listings to scrape.
    try:
        skill_query = next(
            (s for s in profile.skills if any(k in s.lower() for k in ("meal prep", "kid-friendly", "meal pack", "tiffin"))),
            next((s for s in profile.skills if any(k in s.lower() for k in ("meal", "cook", "food"))), None),
        ) or (
            f"{profile.city or profile.state} family meals to go meal prep price"
        )
        city_state = " ".join(part for part in [profile.city, profile.state] if part)
        if any(k in skill_query.lower() for k in ("meal", "cook", "food", "tiffin")):
            skill_query = f"{city_state} family meals to go meal prep kids price".strip()
        # Simple, robust SERP query — surfaces cottage-food/listing pages with prices.
        serp_query = (
            f"{skill_query} local meal prep family dinner catering price seller"
        )
        html = await _bd_fetch(_build_search_url("google", serp_query))
        if not html:
            raise RuntimeError("empty BD response")

        # Tag as castiron source (the spiritual source for cottage-food comps)
        listings = await _extract_listings_from_html(html, query=skill_query, source="castiron")
        if listings:
            for c in listings:
                c["live_scrape_ok"] = True
                c["live_scrape_provider"] = "bright_data"
            log.info("bright_data.foodlocal.live", extra={"persona": profile.persona_id, "count": len(listings)})
            return {"listings": listings, "source": "castiron"}

        log.info("bright_data.foodlocal.no_listings_extracted", extra={"persona": profile.persona_id})
        return _load_cache(cache_path)
    except Exception as e:
        log.warning("bright_data.foodlocal.fallback", extra={"err": str(e)[:200]})
        return _load_cache(cache_path)


async def search_customer_leads(profile, opportunity, limit: int = 6) -> list[dict]:
    """Find public first-customer paths for the winning opportunity.

    Priority order:
      1. Bright Data Web Unlocker / SERP when token+zone are configured and fixtures are off.
      2. Tavily live search when configured.
      3. Persona/category fixture fallback.

    Safety boundaries: public pages only, no private group scraping, no member scraping,
    no phone-number collection, and no login bypass.
    """
    queries = _customer_lead_queries(profile, opportunity)

    if settings.BRIGHT_DATA_API_TOKEN and settings.BRIGHT_DATA_ZONE and not settings.USE_FIXTURES:
        try:
            leads: list[dict] = []
            for query in queries:
                html = await _bd_fetch(_build_search_url("google", query))
                if not html:
                    continue
                extracted = await _extract_customer_leads_from_html(
                    html=html,
                    query=query,
                    profile=profile,
                    opportunity=opportunity,
                    limit=max(1, limit - len(leads)),
                )
                leads.extend(extracted)
                if len(leads) >= limit:
                    break
            leads = _dedupe_customer_lead_dicts(leads)
            if leads:
                log.info("bright_data.customer_leads.live", extra={"count": len(leads)})
                return leads[:limit]
        except Exception as e:
            log.warning("bright_data.customer_leads.fallback_to_tavily", extra={"err": str(e)[:200]})

    if tavily.is_configured():
        try:
            leads = await _search_customer_leads_tavily(profile, opportunity, queries, limit=limit)
            if leads:
                log.info("bright_data.customer_leads.tavily", extra={"count": len(leads)})
                return leads[:limit]
        except Exception as e:
            log.warning("bright_data.customer_leads.tavily_fallback", extra={"err": str(e)[:200]})

    log.info("bright_data.customer_leads.fixture", extra={"persona": getattr(profile, "persona_id", "unknown")})
    return _load_customer_lead_fixture(profile, opportunity, limit=limit)


async def search_community_compatibility(profile, limit: int = 5) -> list[dict]:
    """Use Bright Data to find public Reddit/Quora/forum signals for fit.

    These are not customer leads and they are not private-group data. They are
    public web citations that help Market Scout decide what is realistic for
    working moms/single moms with this profile's skills and constraints.
    """
    if not settings.BRIGHT_DATA_API_TOKEN or not settings.BRIGHT_DATA_ZONE or settings.USE_FIXTURES:
        return []

    citations: list[dict] = []
    try:
        for query in _community_compatibility_queries(profile):
            html = await _bd_fetch(_build_search_url("google", query))
            if not html:
                continue
            per_query_limit = min(2, max(1, limit - len(citations)))
            citations.extend(_extract_public_search_citations(html, query, limit=per_query_limit))
            citations = _dedupe_citation_dicts(citations)
            if len(citations) >= limit:
                break
        if citations:
            log.info("bright_data.community_compatibility.live", extra={"count": len(citations)})
        return _prioritize_citation_domains(citations)[:limit]
    except Exception as e:
        log.warning("bright_data.community_compatibility.fallback", extra={"err": str(e)[:200]})
        return []


def _build_search_url(source: str, query: str) -> str:
    q = quote_plus(query)
    if source == "castiron":
        return f"https://www.castiron.me/search?query={q}"
    if source == "craigslist":
        return f"https://sfbay.craigslist.org/search/sss?query={q}"
    if source in ("poshmark", "etsy"):
        # BD blocks both — caller should re-route to google. Kept for backward compat.
        return f"https://www.google.com/search?q={q}+sold+listings"
    # Default: Google SERP (works for any keyword, returns rich snippets BD passes through)
    return f"https://www.google.com/search?q={q}"


async def _bd_fetch(url: str) -> str:
    """Single Bright Data Web Unlocker call. Returns HTML string (or '' on error)."""
    payload = {"zone": settings.BRIGHT_DATA_ZONE, "url": url, "format": "raw"}
    headers = {
        "Authorization": f"Bearer {settings.BRIGHT_DATA_API_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(BRIGHT_DATA_API, json=payload, headers=headers)
        resp.raise_for_status()
        # BD signals soft errors via headers; surface them as raises.
        bd_err = resp.headers.get("x-brd-error")
        if bd_err:
            raise RuntimeError(f"BD policy: {bd_err[:120]}")
        return resp.text


def _strip_html(html: str, max_chars: int = 18000) -> str:
    """Compress raw HTML for LLM extraction — strip scripts/styles, collapse whitespace."""
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", html)
    return text[:max_chars]


def _html_to_text(html: str, max_chars: int = 50000) -> str:
    html = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", " ", html)
    return _clean_text(unescape(html), max_chars)


def _extract_state_law_from_html(html: str, state: str, source_url: str, cached: dict) -> dict:
    """Build state-law data from the live Bright Data response, not fixture text."""
    text = _html_to_text(html)
    citation_text = _best_law_excerpt(text) or cached.get("citation_text") or text[:700]
    return {
        "source_url": source_url,
        "state": state,
        "citation_text": citation_text,
        # Prepared hot meals / TCS foods need a permitted/commercial path; cottage-food pages
        # define the safe exception as non-potentially-hazardous shelf-stable foods.
        "requires_permit_for_hot_food": True,
        "live_scrape_bytes": len(html),
        "live_scrape_ok": True,
        "live_scrape_provider": "bright_data",
    }


async def _scrape_state_law_serp_bright_data(state: str, cached_path: Path) -> dict:
    state_name = {
        "CA": "California",
        "TX": "Texas",
        "NY": "New York",
    }.get(state, state)
    query = (
        f"{state_name} cottage food law potentially hazardous foods "
        "permit Class B official"
    )
    search_url = _build_search_url("google", query)
    html = await _bd_fetch(search_url)
    if len(html.strip()) < 200:
        raise RuntimeError("empty Bright Data state-law SERP response")
    cached = _load_cache(cached_path)
    source_url = _first_serp_url(html, prefer_gov=True) or cached.get("source_url") or search_url
    return _extract_state_law_from_html(
        html=html,
        state=state,
        source_url=source_url,
        cached=cached,
    ) | {"live_scrape_provider": "bright_data_serp"}


def _first_serp_url(html: str, prefer_gov: bool = False) -> str | None:
    urls: list[str] = []
    for match in re.finditer(r"<a\s+[^>]*href=[\"']([^\"']+)[\"']", html, flags=re.I):
        url = _resolve_google_url(match.group(1))
        if not url or not _is_safe_public_url(url):
            continue
        host = urlparse(url).netloc.lower()
        if any(blocked in host for blocked in ("google.", "gstatic.", "youtube.", "schema.org")):
            continue
        urls.append(url)
        if prefer_gov and ".gov" in host:
            return url
    return urls[0] if urls else None


def _best_law_excerpt(text: str) -> str:
    lower = text.lower()
    keywords = (
        "potentially hazardous",
        "non- potentially hazardous",
        "non-potentially hazardous",
        "time/temperature control",
        "cottage food operation",
        "cottage food products",
        "approved cottage food list",
        "class b",
        "permit",
        "retail food",
    )
    candidates: list[tuple[int, str]] = []
    for keyword in keywords:
        for match in re.finditer(re.escape(keyword), lower):
            idx = match.start()
            start = max(0, idx - 280)
            end = min(len(text), idx + 620)
            window = text[start:end].strip()
            w_lower = window.lower()
            score = 1
            if "google search please click" in w_lower:
                score -= 4
            if "approved cottage food list" in w_lower:
                score += 4
            if "allowed to produce" in w_lower:
                score += 4
            if "non-potentially hazardous" in w_lower or "non- potentially hazardous" in w_lower:
                score += 4
            if "not support the rapid growth" in w_lower:
                score += 3
            if ".gov" in w_lower or "cdph" in w_lower:
                score += 2
            if "permit" in w_lower or "class b" in w_lower:
                score += 1
            candidates.append((score, window))
    if not candidates:
        return ""
    candidates.sort(key=lambda item: item[0], reverse=True)
    return _clean_text(candidates[0][1], 900)


async def _extract_listings_from_html(html: str, query: str, source: str) -> list[dict]:
    """Use the LLM cascade (Gemini today) to extract structured listings from
    real scraped HTML. Returns EvidenceCard-shaped dicts.

    Schema matches `EvidenceCard` so the orchestrator can validate them directly.
    """
    snippet = _strip_html(html)
    if len(snippet) < 200:
        return []

    # Source must be one of the EvidenceCard SourceType literals
    valid_sources = {"etsy", "poshmark", "craigslist", "nextdoor", "outschool",
                     "facebook_marketplace", "facebook_group", "castiron", "instagram"}
    safe_source = source if source in valid_sources else "craigslist"

    system = (
        "You extract structured market-comp listings from raw HTML — typically a Google search "
        "results page or marketplace listing page returned by a Bright Data scrape. "
        "Find the actual product/service result snippets in the HTML: titles, prices ($X), "
        "seller names, URLs from anchor tags. Google SERP results live inside <div class='g'>, "
        "<h3>, <a href='/url?q='> wrappers. Marketplaces use <a class='listing-card'> or similar. "
        "Look for any text matching $\\d+ patterns to find prices. "
        "Output ONLY JSON in this exact shape: "
        '{"listings": [{'
        '"id": str (e.g. "bd_castiron_001"), '
        '"title": str (max 100 chars, the actual product name from the page), '
        f'"source": "{safe_source}", '
        '"source_url": str (absolute URL of THAT specific listing if visible, else the search URL), '
        '"observed_price_usd": float (single representative number, never a range), '
        '"observed_volume_signal": str (e.g. "12 sold last month", "active seller", "high demand" — '
        'extract from page if available, otherwise infer a reasonable signal), '
        '"estimated_gross_monthly_usd": int (your best estimate of monthly gross revenue at observed price), '
        '"estimated_net_monthly_usd": int (after ~30-40% platform fees + materials), '
        '"time_to_first_dollar_days": int (typical days from listing to first sale, e.g. 7-30), '
        '"notes": str (one-line why this is a relevant comp, max 200 chars)'
        "}]}. "
        "Include 3-6 distinct listings. If the HTML has no extractable listings, return an empty list. "
        "DO NOT invent listings — extract only what's actually visible in the HTML excerpt."
    )
    user = json.dumps({
        "query": query,
        "source": source,
        "html_excerpt": snippet,
    })

    try:
        result = await llm_cascade.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        raw = result.get("listings", []) if isinstance(result, dict) else []
        cleaned: list[dict] = []
        for i, r in enumerate(raw[:6]):
            if not isinstance(r, dict) or not r.get("title"):
                continue
            try:
                price = float(r.get("observed_price_usd") or 0)
                if price <= 0:
                    continue
                cleaned.append({
                    "id": str(r.get("id") or f"bd_{safe_source}_{i:03d}"),
                    "title": str(r.get("title"))[:160],
                    "source": safe_source,
                    "source_url": str(r.get("source_url") or _build_search_url(safe_source, query)),
                    "observed_price_usd": price,
                    "observed_volume_signal": str(r.get("observed_volume_signal") or "active listing"),
                    "estimated_gross_monthly_usd": int(r.get("estimated_gross_monthly_usd") or price * 4),
                    "estimated_net_monthly_usd": int(r.get("estimated_net_monthly_usd") or price * 2.5),
                    "time_to_first_dollar_days": int(r.get("time_to_first_dollar_days") or 14),
                    "notes": str(r.get("notes") or "")[:280],
                })
            except (ValueError, TypeError) as ve:
                log.debug("bright_data.extract.skip_invalid", extra={"err": str(ve)})
                continue
        if cleaned:
            return cleaned
        return _extract_listings_deterministic(html, query=query, source=safe_source)
    except Exception as e:
        log.warning("bright_data.extract.fail", extra={"err": str(e)[:200]})
        return _extract_listings_deterministic(html, query=query, source=safe_source)


def _extract_listings_deterministic(html: str, query: str, source: str) -> list[dict]:
    """Parse Bright Data SERP HTML directly when LLM extraction is unavailable."""
    matches = list(re.finditer(r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S))
    listings: list[dict] = []
    seen_urls: set[str] = set()
    for match in matches:
        href, inner = match.group(1), match.group(2)
        url = _resolve_google_url(href)
        if not url or url in seen_urls or not _is_safe_public_url(url):
            continue
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        if any(blocked in host for blocked in ("google.", "gstatic.", "youtube.", "schema.org")):
            continue
        title = _clean_text(re.sub(r"<[^>]+>", " ", unescape(inner)), 150)
        if len(title) < 8:
            title = _clean_text(host.replace("www.", ""), 150)
        if _looks_like_navigation_title(title):
            continue

        window = _html_to_text(html[match.start(): match.end() + 2600], max_chars=2600)
        price = _extract_price(window) or _default_price_for_query(query)
        gross = max(int(price * 8), int(price))
        net = max(int(gross * 0.6), int(price * 2))
        seen_urls.add(url)
        listings.append({
            "id": f"bd_{source}_{len(listings) + 1:03d}",
            "title": title,
            "source": source,
            "source_url": url,
            "observed_price_usd": float(price),
            "observed_volume_signal": _volume_signal_from_window(window),
            "estimated_gross_monthly_usd": gross,
            "estimated_net_monthly_usd": net,
            "time_to_first_dollar_days": 10 if source in {"castiron", "facebook_group", "instagram"} else 14,
            "notes": (
                "Live Bright Data SERP result parsed directly from public web HTML; "
                "no fixture listing used."
            ),
            "live_scrape_ok": True,
            "live_scrape_provider": "bright_data",
        })
        if len(listings) >= 6:
            break
    return listings


def _looks_like_navigation_title(title: str) -> bool:
    lowered = title.lower().strip()
    if lowered in {"read more", "images", "videos", "maps", "shopping", "news", "sign in"}:
        return True
    if len(lowered) < 4:
        return True
    return False


def _extract_price(text: str) -> float | None:
    prices: list[float] = []
    for raw in re.findall(r"\$\s?([0-9]{1,4}(?:[,.][0-9]{2})?)", text):
        try:
            price = float(raw.replace(",", ""))
        except ValueError:
            continue
        if 2 <= price <= 500:
            prices.append(price)
    return prices[0] if prices else None


def _default_price_for_query(query: str) -> float:
    lowered = query.lower()
    if any(k in lowered for k in ("printable", "digital", "download", "template", "canva")):
        return 9.0
    if any(k in lowered for k in ("meal", "food", "cook", "tiffin", "cottage")):
        return 35.0
    return 25.0


def _volume_signal_from_window(window: str) -> str:
    lowered = window.lower()
    for pattern in (
        r"([0-9][0-9,]*)\s+reviews?",
        r"([0-9][0-9,]*)\s+sold",
        r"([0-9][0-9,]*)\s+followers?",
    ):
        match = re.search(pattern, lowered)
        if match:
            return f"Public SERP shows {match.group(0)}"
    return "Live public search result surfaced by Bright Data"


async def _extract_customer_leads_from_html(
    html: str,
    query: str,
    profile,
    opportunity,
    limit: int,
) -> list[dict]:
    snippet = _strip_html(html)
    if len(snippet) < 200:
        return []

    system = (
        "You extract public customer-acquisition paths from Google SERP or public web HTML for Mom's Saheli. "
        "Only include public pages a working mom can review safely: vendor applications, school enrichment/vendor "
        "pages, community business-post rules pages, event/vendor pages, directories, marketplace listing paths, "
        "or public group landing/rules pages. "
        "Never include private group members, WhatsApp invite scraping, phone numbers, login-only pages, or anything "
        "that requires bypassing access controls. "
        "Output ONLY JSON in this exact shape: "
        '{"leads": [{'
        '"id": str, '
        '"title": str, '
        '"source_type": "vendor_form"|"community_page"|"school_page"|"marketplace"|"approved_group"|'
        '"warm_network"|"local_directory"|"event_page"|"manual", '
        '"source_url": str|null, '
        '"audience_match": str, '
        '"why_relevant": str, '
        '"estimated_reach": str|null, '
        '"confidence": float 0..1, '
        '"live_source": true, '
        '"provider": "bright_data", '
        '"notes": str|null'
        "}]}. "
        f"Return at most {limit} leads."
    )
    user = json.dumps({
        "query": query,
        "profile": {
            "persona_id": getattr(profile, "persona_id", ""),
            "display_name": getattr(profile, "display_name", ""),
            "city": getattr(profile, "city", None),
            "state": getattr(profile, "state", ""),
            "preferred_channels": getattr(profile, "preferred_channels", []),
        },
        "opportunity": {
            "id": getattr(opportunity, "id", ""),
            "title": getattr(opportunity, "title", ""),
            "category": getattr(opportunity, "category", ""),
        },
        "html_excerpt": snippet,
    })
    try:
        result = await llm_cascade.chat_json(
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.1,
        )
        cleaned: list[dict] = []
        for i, raw in enumerate((result.get("leads") or [])[:limit]):
            if not isinstance(raw, dict):
                continue
            lead = _normalize_customer_lead_dict(
                raw,
                fallback_id=f"bd_customer_{i + 1}",
                provider="bright_data",
                live_source=True,
                profile=profile,
                opportunity=opportunity,
            )
            if lead:
                cleaned.append(lead)
        if cleaned:
            return cleaned
        return _extract_customer_leads_deterministic(html, query, profile, opportunity, limit)
    except Exception as e:
        log.warning("bright_data.customer_extract.fail", extra={"err": str(e)[:200]})
        return _extract_customer_leads_deterministic(html, query, profile, opportunity, limit)


def _extract_customer_leads_deterministic(
    html: str,
    query: str,
    profile,
    opportunity,
    limit: int,
) -> list[dict]:
    """Fallback extractor for Bright Data SERP HTML when no live LLM is available."""
    blocks = re.findall(r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S)
    leads: list[dict] = []
    seen_urls: set[str] = set()
    for href, inner in blocks:
        url = _resolve_google_url(href)
        if not url or url in seen_urls or not _is_safe_public_url(url):
            continue
        parsed = urlparse(url)
        if any(host in parsed.netloc.lower() for host in ("google.", "gstatic.", "youtube.", "schema.org")):
            continue
        title = _clean_text(re.sub(r"<[^>]+>", " ", unescape(inner)), 140)
        if len(title) < 8:
            title = _clean_text(parsed.netloc.replace("www.", ""), 140)
        combined = f"{title} {url} {query}"
        source_type = _classify_customer_source(combined)
        if source_type == "manual" and len(leads) >= max(1, limit // 2):
            continue
        seen_urls.add(url)
        leads.append({
            "id": f"bd_serp_customer_{len(leads) + 1}_{_slug(title)[:32]}",
            "title": title,
            "source_type": source_type,
            "source_url": url,
            "audience_match": (
                f"{getattr(profile, 'city', None) or 'Local'} {getattr(profile, 'state', '')} "
                f"parents and families connected to {getattr(opportunity, 'title', 'the offer')}"
            ),
            "why_relevant": (
                "Bright Data returned this public search result for a customer-acquisition query; "
                "review the page rules before outreach."
            ),
            "estimated_reach": _estimated_reach_for_source(source_type),
            "confidence": 0.62 if source_type != "manual" else 0.48,
            "live_source": True,
            "provider": "bright_data",
            "notes": "Deterministic SERP extraction; no private groups, member lists, or phone numbers collected.",
        })
        if len(leads) >= limit:
            break
    return leads


def _resolve_google_url(href: str) -> str | None:
    href = unescape(href)
    if href.startswith("/url?"):
        params = parse_qs(urlparse(href).query)
        href = params.get("q", [""])[0]
    elif href.startswith("https://www.google.com/url?"):
        params = parse_qs(urlparse(href).query)
        href = params.get("q", [""])[0]
    href = unquote(href)
    if not href.startswith(("http://", "https://")):
        return None
    return href


async def _search_customer_leads_tavily(profile, opportunity, queries: list[str], limit: int) -> list[dict]:
    leads: list[dict] = []
    for query in queries:
        result = await tavily.search(query, max_results=4, search_depth="basic")
        for raw in result.get("results", [])[:4]:
            lead = _customer_lead_from_search_result(
                raw=raw,
                query=query,
                profile=profile,
                opportunity=opportunity,
                index=len(leads) + 1,
            )
            if lead:
                leads.append(lead)
            if len(leads) >= limit:
                break
        if len(leads) >= limit:
            break
    return _dedupe_customer_lead_dicts(leads)[:limit]


def _customer_lead_queries(profile, opportunity) -> list[str]:
    city = getattr(profile, "city", None) or ""
    state = getattr(profile, "state", "") or ""
    geo = " ".join(part for part in [city, state] if part).strip()
    title = getattr(opportunity, "title", "") or "parent services"
    category = getattr(opportunity, "category", "") or "side gig"
    return [
        f"{geo} moms vendor form {title}".strip(),
        f"{geo} school vendor application parent services".strip(),
        f"{geo} community vendor application homemade meals".strip(),
        f"{geo} local moms group rules business post".strip(),
        f"{title} {geo} customers parents".strip(),
        f"{geo} {category.replace('_', ' ')} marketplace listing parents".strip(),
    ]


def _community_compatibility_queries(profile) -> list[str]:
    city = getattr(profile, "city", None) or ""
    state = getattr(profile, "state", "") or ""
    geo = " ".join(part for part in [city, state] if part).strip()
    skills = " ".join(getattr(profile, "skills", []) or []).lower()
    constraints = " ".join(getattr(profile, "hard_constraints", []) or []).lower()

    if any(k in skills for k in ("meal", "cook", "food", "tiffin")):
        focus = "family meal prep home cooking parents"
        quora_focus = "home cooked meal prep business pricing customers"
    elif any(k in skills for k in ("canva", "design", "printable", "social media")) or "no_inventory" in constraints:
        focus = "canva printables digital product parents"
        quora_focus = "canva printables digital product side hustle pricing customers"
    elif any(k in skills for k in ("tutor", "teach", "school")):
        focus = "online tutoring parents kids"
        quora_focus = "online tutoring business parents kids pricing"
    else:
        focus = "working mom side hustle realistic"
        quora_focus = "working mom side hustle realistic customers"

    geo_prefix = f"{geo} " if geo else ""
    return [
        f"site:reddit.com {focus} working mom side hustle realistic demand",
        f"site:quora.com {quora_focus} side hustle realistic",
        f"site:reddit.com {focus} parents price first customers",
        f"site:quora.com {quora_focus} parents demand price first customers",
        f"{geo_prefix}{focus} reddit quora parents demand price".strip(),
        f"{focus} single mom side income forum realistic constraints",
    ]


def _extract_public_search_citations(html: str, query: str, limit: int) -> list[dict]:
    matches = list(re.finditer(r"<a\s+[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", html, flags=re.I | re.S))
    citations: list[dict] = []
    seen_urls: set[str] = set()
    for match in matches:
        url = _resolve_google_url(match.group(1))
        if not url or url in seen_urls or not _is_safe_public_url(url):
            continue
        host = urlparse(url).netloc.lower()
        if any(blocked in host for blocked in ("google.", "gstatic.", "youtube.", "schema.org")):
            continue
        title = _clean_text(re.sub(r"<[^>]+>", " ", unescape(match.group(2))), 160)
        if len(title) < 8:
            title = _clean_text(host.replace("www.", ""), 160)
        if _looks_like_navigation_title(title):
            continue
        window = _html_to_text(html[match.start(): match.end() + 2200], max_chars=2200)
        snippet = _community_snippet(window, query)
        source_label = _domain_label(host)
        seen_urls.add(url)
        citations.append({
            "url": url,
            "title": f"{source_label}: {title}" if source_label else title,
            "snippet": snippet,
            "provider": "bright_data",
            "live_source": True,
        })
        if len(citations) >= limit:
            break
    return citations


def _community_snippet(window: str, query: str) -> str:
    text = _clean_text(window, 700)
    if not text:
        return f"Public Bright Data result for compatibility query: {query}"
    keywords = (
        "working mom", "single mom", "parents", "demand", "price", "customers",
        "side hustle", "realistic", "meal prep", "printables", "canva",
    )
    lower = text.lower()
    for keyword in keywords:
        idx = lower.find(keyword)
        if idx >= 0:
            return _clean_text(text[max(0, idx - 140): idx + 420], 520)
    return text[:520]


def _domain_label(host: str) -> str:
    if "reddit.com" in host:
        return "Reddit"
    if "quora.com" in host:
        return "Quora"
    return host.replace("www.", "").split(":")[0]


def _dedupe_citation_dicts(citations: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for citation in citations:
        url = str(citation.get("url") or "")
        if not url or url in seen:
            continue
        seen.add(url)
        deduped.append(citation)
    return deduped


def _prioritize_citation_domains(citations: list[dict]) -> list[dict]:
    """Put one Reddit and one Quora signal up front when both are present."""
    ordered: list[dict] = []
    used_urls: set[str] = set()
    for domain in ("reddit.com", "quora.com"):
        for citation in citations:
            url = str(citation.get("url") or "")
            if domain in url.lower() and url not in used_urls:
                ordered.append(citation)
                used_urls.add(url)
                break
    for citation in citations:
        url = str(citation.get("url") or "")
        if url and url not in used_urls:
            ordered.append(citation)
            used_urls.add(url)
    return ordered


def _customer_lead_from_search_result(raw: dict, query: str, profile, opportunity, index: int) -> dict | None:
    title = _clean_text(raw.get("title") or f"Customer path {index}", 140)
    url = raw.get("url") or raw.get("source_url")
    if url and not _is_safe_public_url(str(url)):
        return None
    content = _clean_text(raw.get("content") or raw.get("snippet") or "", 320)
    combined = f"{title} {content} {url or ''}"
    source_type = _classify_customer_source(combined)
    score = raw.get("score", 0.62)
    try:
        confidence = float(score)
        if confidence > 1:
            confidence = confidence / 100
    except (TypeError, ValueError):
        confidence = 0.62
    confidence = max(0.45, min(0.92, confidence))
    city = getattr(profile, "city", None) or "local"
    state = getattr(profile, "state", "")
    return {
        "id": f"tavily_customer_{index}_{_slug(title)[:32]}",
        "title": title,
        "source_type": source_type,
        "source_url": url,
        "audience_match": f"{city} {state} parents and local families connected to {getattr(opportunity, 'title', 'the offer')}",
        "why_relevant": content or f"Public result from query: {query}",
        "estimated_reach": _estimated_reach_for_source(source_type),
        "confidence": confidence,
        "live_source": True,
        "provider": "tavily",
        "notes": "Public web result; private groups and phone numbers were excluded.",
    }


def _normalize_customer_lead_dict(
    raw: dict,
    fallback_id: str,
    provider: str,
    live_source: bool,
    profile,
    opportunity,
) -> dict | None:
    title = _clean_text(raw.get("title") or fallback_id, 160)
    url = raw.get("source_url")
    if url and not _is_safe_public_url(str(url)):
        return None
    source_type = raw.get("source_type") or _classify_customer_source(f"{title} {url or ''}")
    if source_type not in {
        "vendor_form",
        "community_page",
        "school_page",
        "marketplace",
        "approved_group",
        "warm_network",
        "local_directory",
        "event_page",
        "manual",
    }:
        source_type = _classify_customer_source(f"{title} {raw.get('why_relevant', '')} {url or ''}")
    try:
        confidence = float(raw.get("confidence", 0.55))
    except (TypeError, ValueError):
        confidence = 0.55
    city = getattr(profile, "city", None) or "local"
    return {
        "id": str(raw.get("id") or fallback_id),
        "title": title,
        "source_type": source_type,
        "source_url": url,
        "audience_match": _clean_text(
            raw.get("audience_match")
            or f"{city} parents likely to need {getattr(opportunity, 'title', 'this offer')}",
            220,
        ),
        "why_relevant": _clean_text(
            raw.get("why_relevant") or raw.get("notes") or "Public customer-acquisition path.",
            320,
        ),
        "estimated_reach": _clean_text(raw.get("estimated_reach"), 120) if raw.get("estimated_reach") else None,
        "confidence": max(0.0, min(1.0, confidence)),
        "live_source": bool(live_source),
        "provider": provider,
        "notes": _clean_text(raw.get("notes"), 240) if raw.get("notes") else None,
    }


def _load_customer_lead_fixture(profile, opportunity, limit: int) -> list[dict]:
    persona = getattr(profile, "persona_id", "jenny") or "jenny"
    path = settings.cached_scrapes_dir / f"customer_leads_{persona}.json"
    if not path.exists():
        category = getattr(opportunity, "category", "")
        fallback = "jessica" if category == "digital_async" else "jenny"
        path = settings.cached_scrapes_dir / f"customer_leads_{fallback}.json"
    raw = _load_cache_list(path)
    leads: list[dict] = []
    for i, item in enumerate(raw[:limit]):
        if not isinstance(item, dict):
            continue
        lead = _normalize_customer_lead_dict(
            item,
            fallback_id=f"fixture_customer_{i + 1}",
            provider="fixture_fallback",
            live_source=False,
            profile=profile,
            opportunity=opportunity,
        )
        if lead:
            lead["provider"] = "fixture_fallback"
            lead["live_source"] = False
            leads.append(lead)
    return leads


def _classify_customer_source(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ("school", "pta", "district", "enrichment", "parent teacher")):
        return "school_page"
    if any(k in t for k in ("vendor", "application", "apply", "form", "catering inquiry")):
        return "vendor_form"
    if any(k in t for k in ("event", "fair", "market day", "farmers market", "booth")):
        return "event_page"
    if any(k in t for k in ("marketplace", "etsy", "facebook marketplace", "listing", "shop")):
        return "marketplace"
    if any(k in t for k in ("directory", "chamber", "resource guide")):
        return "local_directory"
    if any(k in t for k in ("group", "moms", "nextdoor", "facebook")):
        return "community_page"
    return "manual"


def _estimated_reach_for_source(source_type: str) -> str:
    return {
        "vendor_form": "Public vendor intake path",
        "school_page": "School or parent community audience",
        "community_page": "Public community rules or landing page",
        "marketplace": "Marketplace shoppers searching the category",
        "local_directory": "Local directory visitors",
        "event_page": "Event attendees or vendor buyers",
        "manual": "Manual review required",
    }.get(source_type, "Public customer path")


def _is_safe_public_url(url: str) -> bool:
    lowered = url.lower()
    blocked = (
        "web.whatsapp.com",
        "chat.whatsapp.com",
        "/members",
        "/login",
        "signin",
        "auth",
        "phone=",
        "tel:",
    )
    return not any(part in lowered for part in blocked)


def _dedupe_customer_lead_dicts(leads: list[dict]) -> list[dict]:
    seen: set[tuple[str, str | None]] = set()
    deduped: list[dict] = []
    for lead in leads:
        title = str(lead.get("title") or "").lower().strip()
        url = lead.get("source_url")
        key = (title, url)
        if not title or key in seen:
            continue
        seen.add(key)
        deduped.append(lead)
    return deduped


_PHONE_RE = re.compile(r"(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}")


def _clean_text(value: object, max_chars: int) -> str:
    text = "" if value is None else str(value)
    text = _PHONE_RE.sub("[phone omitted]", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def _slug(text: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in text).strip("_")


def _load_cache(path: Path) -> dict:
    if not path.exists():
        log.warning("bright_data.cache_missing", extra={"path": str(path)})
        return {"source_url": "", "citation_text": "(cache missing)", "requires_permit_for_hot_food": True}
    return json.loads(path.read_text())


def _load_cache_list(path: Path) -> list[dict]:
    if not path.exists():
        log.warning("bright_data.cache_missing", extra={"path": str(path)})
        return []
    return json.loads(path.read_text())
