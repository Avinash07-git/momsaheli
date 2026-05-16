> ⚠️ **LEGACY DOC — written before the build.** Implementation has drifted.
> The canonical state lives in [`../../AGENTS.md`](../../AGENTS.md).
> Kept here for design-intent reference only.

# 📐 SPEC — Mom's Saheli (v1.0)

> The single source of truth for the build.
> If a thing isn't in this file, it doesn't ship for the hackathon.
> Companion to: `PLAN_LOCKED.md` (strategy), `ARCHITECTURE.md` (system), `DEMO_SCRIPT.md` (pitch).

---

## 0. SCOPE LOCK

**In scope (must ship):**
- 4 screens: Home (intake + presets) · Run (swarm + evidence + compliance) · Launch Page (public) · History (Butterbase-backed)
- 5 agents wired end-to-end with real sponsor APIs
- 2 personas (Jenny, Jessica) with full fixture JSONs
- SSE-based live agent event streaming
- Cached fallback for every external call
- Sanity-check script per sponsor

**Out of scope (NOT shipping):**
- Voice intake
- 3rd live judge-input persona (stretch goal — only if Wave C finishes early)
- User signup flow (Butterbase auth is single-tenant for the demo)
- Email/SMS outreach actually firing (drafts only — read-only output)
- Mobile-responsive polish past Tailwind defaults

---

## 1. SCREEN INVENTORY (4 max)

### Screen 1 — `Home` (`/`)
Purpose: get a profile in front of the swarm in <5 seconds.

Layout:
- Hero: trophy sentence + 4 cited stats (7.3M · 75% · $40K · 35%)
- Two giant preset buttons: **Run Jenny** · **Run Jessica**
- Below the fold: collapsible "Custom profile" form (intake form for the deferred 3rd-persona stretch goal — disabled by default but rendered)
- Footer: sponsor logo bar (9 logos, each linking to its role in the architecture)

### Screen 2 — `Run` (`/run/{run_id}`)
Purpose: the 90-second demo lives here.

Layout (3 columns):
- **Left (25%):** `AgentTimeline` — vertical list of the 5 agents with status pills (idle · running · done · blocked). Each item shows the latest event timestamp.
- **Center (50%):** event stream — `EvidenceCard`s and `ComplianceBlock`s render top-to-bottom as they arrive via SSE. The compliance BLOCK card is visually distinct (red border, citation link).
- **Right (25%):** live browser frames panel — embedded `<iframe>` or screenshot stream from Actionbook's session for the Etsy live search, and a second frame for the Bright Data law-page scrape. (If live frames are blocked by X-Frame-Options, fall back to a screenshot polled every 500ms — the visual effect is the same.)
- Sticky bottom bar: `LaunchPacket` preview button → expands when Launch Agent finishes.

### Screen 3 — `LaunchPage` (`/launch/{slug}`)
Purpose: the public, shareable Mom's Saheli launch page. Hosted on Butterbase.

Layout (single column, mobile-first):
- Hero: offer name + tagline + price
- "About the maker" block (persona-shaped, no real PII)
- Offer details: what you get, when, how to order
- "Order" CTA button (form-fills into Butterbase, single field: email)
- Footer: "Powered by Mom's Saheli" + back-link

### Screen 4 — `History` (`/history`)
Purpose: prove the Butterbase persistence is real. Demo-day this is a "look, judges, all the past runs are queryable" panel.

Layout:
- Table: run_id · persona name · winner option · launch URL · created_at · "View" link
- Filter by persona (Jenny / Jessica / custom)
- Empty state seeds a "Run Jenny" prompt

---

## 2. COMPONENT INVENTORY (10 max)

| # | Component | Lives in | Notes |
|---|---|---|---|
| 1 | `PresetButtons` | Home | Two giant buttons. Owns the `POST /api/run` call. |
| 2 | `StatCard` | Home | Renders one cited stat + source link. Used 4x. |
| 3 | `AgentTimeline` | Run | Vertical list of 5 agents w/ status pills. SSE-driven. |
| 4 | `EvidenceCard` | Run | One market option. Shows source (Etsy/Poshmark/Craigslist), price, est. net income. |
| 5 | `ComplianceBlock` | Run | Red-bordered card for a BLOCK. Shows citation, link to source, constraint reason. |
| 6 | `LaunchPacket` | Run | Expandable preview of the offer / copy / 7-day plan + the published URL. |
| 7 | `MemoryPanel` | Run | Cross-user pattern surfaced via Evermind query. Appears after run completes. |
| 8 | `BrowserFrame` | Run | Right-column live browser/screenshot view from Actionbook + Bright Data. |
| 9 | `SponsorBar` | Home + Run footer | 9 sponsor logos. Each link goes to a hover-tooltip explaining the role. |
| 10 | `LaunchPageView` | LaunchPage | The public landing template. Rendered from `LaunchPacket` data. |

**No 11th component without dropping one of the above.**

---

## 3. API CONTRACT

### `POST /api/run`
Kicks off a new swarm run.

**Request:**
```json
{
  "profile": { /* Profile schema, see §4 */ },
  "use_fixtures": false
}
```

**Response (immediate):**
```json
{ "run_id": "run_01HXYZ...", "stream_url": "/api/stream/run_01HXYZ..." }
```

The swarm is fired async; events stream over SSE.

---

### `GET /api/stream/{run_id}` (SSE)
Server-Sent Events. Each event is a JSON-encoded object with `type` and `data`.

**Event types (in expected order):**
- `profile_ready` — Profile Agent done. `data: { profile: Profile }`
- `evidence_card` — Market Scout streams one option in. `data: { card: EvidenceCard }`
- `opportunities_ranked` — Market Scout done. `data: { top_3_ids: string[] }`
- `compliance_check` — Reality Agent rules on one option. `data: { check: ComplianceCheck }`
- `winner_selected` — Reality Agent's surviving winner. `data: { opportunity_id: string }`
- `launch_packet_ready` — Launch Agent finished generation. `data: { packet: LaunchPacket }`
- `launch_published` — Actionbook + Butterbase published the page. `data: { url: string, slug: string }`
- `memory_pattern` — Memory Agent's cross-user query result. `data: { pattern: MemoryTrajectory }`
- `run_complete` — terminal event. `data: { run_id, duration_ms, summary }`
- `agent_error` — soft failure on a single agent. `data: { agent: string, error: string, fallback_used: boolean }`

---

### `POST /api/publish`
Manual trigger for Launch Agent (useful if user wants to re-publish with edits). The swarm normally calls this internally.

**Request:** `{ run_id, packet_edits?: Partial<LaunchPacket> }`
**Response:** `{ url, slug }`

---

### `GET /api/memory?persona={jenny|jessica|all}`
Queries Evermind for trajectories. Returns the cross-user pattern.

**Response:** `{ trajectories: MemoryTrajectory[], cross_user_pattern: string | null }`

---

### `GET /api/runs`
Lists past runs from Butterbase for the History screen.

**Response:** `{ runs: RunSummary[] }`

---

### `GET /launch/{slug}`
Public launch page. Served by Butterbase (or FastAPI rendering Butterbase data).

Returns HTML. No auth.

---

## 4. DATA SCHEMAS

All schemas are Pydantic models in `backend/schemas/`. JSON-serializable.

### `Profile`
```python
class Profile(BaseModel):
    persona_id: str                      # "jenny" | "jessica" | "custom_<uuid>"
    display_name: str                    # "Jenny" — for UI only, not PII
    day_job: str
    income_gap_monthly_usd: int
    hours_per_week_available: int
    skills: list[str]
    budget_startup_usd: int
    state: str                           # 2-letter, e.g. "CA"
    city: str | None = None
    hard_constraints: list[str]          # ["no_nights", "no_delivery", "no_phone_calls", ...]
    notes: str | None = None
```

### `EvidenceCard`
```python
class EvidenceCard(BaseModel):
    id: str
    title: str                           # "Weekend Family Meal Pack — 4 servings"
    source: Literal["etsy", "poshmark", "craigslist", "nextdoor", "outschool"]
    source_url: str
    observed_price_usd: float
    observed_volume_signal: str          # "12 sold last month", "4 active listings"
    estimated_gross_monthly_usd: int
    estimated_net_monthly_usd: int       # after platform fee + materials
    time_to_first_dollar_days: int
    notes: str
```

### `Opportunity`
```python
class Opportunity(BaseModel):
    id: str
    title: str
    category: Literal["food_local", "digital_async", "service_local", "resale"]
    evidence_card_ids: list[str]
    rank: int                            # 1 = best fit
    rationale: str                       # 1-2 sentences from Market Scout
    estimated_net_monthly_usd: int
    requires_permit: bool                # initial guess; Reality Agent confirms
```

### `ComplianceCheck`
```python
class ComplianceCheck(BaseModel):
    opportunity_id: str
    verdict: Literal["PASS", "BLOCK", "WARN"]
    constraint_math_passed: bool
    constraint_math_reasons: list[str]   # ["fits 5 hr/wk", "fits $80 budget"]
    legal_passed: bool
    legal_citation_source_url: str | None
    legal_citation_text: str | None      # "California Health & Safety Code §114365: …"
    block_reason: str | None             # human-readable summary
```

### `LaunchPacket`
```python
class LaunchPacket(BaseModel):
    opportunity_id: str
    offer_name: str
    offer_tagline: str
    price_usd: float
    unit: str                            # "per meal pack", "per printable"
    description_markdown: str
    target_customer: str
    outreach_drafts: list[OutreachDraft]
    day_plan: list[DayPlanItem]          # 7 items

class OutreachDraft(BaseModel):
    channel: Literal["nextdoor", "facebook_group", "text_friends", "etsy_listing"]
    subject: str | None
    body_markdown: str

class DayPlanItem(BaseModel):
    day: int                             # 1..7
    action: str
    estimated_minutes: int
```

### `MemoryTrajectory`
```python
class MemoryTrajectory(BaseModel):
    persona_id: str
    run_id: str
    chosen_opportunity_id: str
    rejected_opportunity_ids: list[str]
    block_citations: list[str]           # legal_citation_text values
    timestamp: datetime

class CrossUserPattern(BaseModel):
    pattern_text: str                    # "low-hours + no-delivery → digital-first"
    supporting_run_ids: list[str]
    confidence: float                    # 0-1, from Evermind query
```

### `RunSummary` (for History screen)
```python
class RunSummary(BaseModel):
    run_id: str
    persona_display_name: str
    winner_offer_name: str
    launch_url: str | None
    created_at: datetime
    duration_ms: int
```

---

## 5. FIXTURE JSONs

Two persona fixtures live in `backend/fixtures/`. These are the ONLY hardcoded profiles. Real custom-profile intake works via the same schema.

### `jenny.json`
```json
{
  "persona_id": "jenny",
  "display_name": "Jenny",
  "day_job": "Daycare aide (full-time)",
  "income_gap_monthly_usd": 600,
  "hours_per_week_available": 5,
  "skills": ["home cooking", "meal prep", "kid-friendly meals"],
  "budget_startup_usd": 80,
  "state": "CA",
  "city": "Fresno",
  "hard_constraints": ["no_nights", "no_daily_delivery", "no_commercial_kitchen"],
  "notes": "Has weekends for prep. Two kids under 10. Owns standard home kitchen."
}
```

### `jessica.json`
```json
{
  "persona_id": "jessica",
  "display_name": "Jessica",
  "day_job": "Customer service rep (WFH, full-time)",
  "income_gap_monthly_usd": 400,
  "hours_per_week_available": 3,
  "skills": ["meal planning", "Canva", "kids lunch ideas", "writing"],
  "budget_startup_usd": 20,
  "state": "TX",
  "city": "Austin",
  "hard_constraints": ["no_phone_calls", "no_delivery", "no_inventory", "fully_async"],
  "notes": "Wants something purely digital. One school-age kid. Comfortable on a laptop after work."
}
```

### Cached scrape fixtures (`backend/fixtures/cached_scrapes/`)
For demo-day reliability. Each is a real captured response from rehearsal day.

- `ca_cottage_food.json` — Bright Data response for the CA Health & Safety Code §114365 page (the BLOCK source-of-truth)
- `etsy_kids_lunch.json` — Actionbook captured response for an Etsy search "kids lunch printable" (Jessica path)
- `etsy_meal_pack.json` — Actionbook captured response for "weekend family meal pack" (Jenny path)
- `poshmark_meal_prep.json` — Bright Data Poshmark sold-listings dump
- `tx_cottage_food.json` — TX cottage food law page (Jessica safety net even though she's digital)

The adapter layer auto-falls-back to the cached version on any timeout/error AND when `USE_FIXTURES=true`.

---

## 6. LAUNCH PAGE TEMPLATE

`backend/templates/launch_page.html` — Jinja2, single file, Tailwind via CDN, no JS framework. Renders from a `LaunchPacket` + the persona's `display_name`.

Sections (top-to-bottom):
1. Hero (offer_name, offer_tagline, price + unit, big CTA)
2. "About the maker" — display_name + short story (Qwen-generated, 1 paragraph, no PII)
3. "What you get" — description_markdown rendered
4. "How to order" — single email-capture form → POSTs to Butterbase
5. Footer: "Powered by Mom's Saheli" + privacy note + back-link

Accessibility: WCAG 2.2 AA (per Walmart rules). 4.5:1 text contrast. Semantic HTML. Keyboard-navigable form.

**No Walmart blue/spark colors** (public hackathon, per NORTH_STAR anti-pattern #9). Use a warm palette: `#f59e0b` accent (amber), `#1f2937` text, off-white bg.

---

## 7. FALLBACK PLAN (demo-day reliability)

Tiered, automatic:

| Failure | Detection | Fallback |
|---|---|---|
| Qwen Cloud quota/error | TokenRouter returns non-200 within 5s | Z.ai GLM-5.1 (cascade auto) |
| Z.ai also down | TokenRouter exhausts cascade | `USE_FIXTURES=true` warning banner appears; agent returns pre-baked JSON for the persona |
| Bright Data scrape times out | >8s per request | Serve from `cached_scrapes/` matching the URL pattern |
| Actionbook session fails to start | Init error or >10s no response | Use cached Etsy screenshot + cached EvidenceCard JSON |
| Butterbase publish fails | Non-200 from publish endpoint | FastAPI renders launch page directly from `templates/launch_page.html` and serves on `/launch/{slug}` |
| Evermind query empty/errors | >3s timeout | Hardcoded fallback cross-user pattern shown with `(seed pattern)` label — honestly disclosed in SUBMISSION.md |
| Full WiFi loss | Network detection | Backup Loom video plays (final last resort) |

All fallbacks are non-silent: the UI shows a small `⚠ fallback active: <reason>` pill in the corner. **Honesty over magic.**

---

## 8. SPONSOR PROOF (no-faking ledger)

For SUBMISSION.md, every claimed sponsor needs: env var name, file path of the real API call, line range, and sanity script.

| Sponsor | Env var | Real call lives in | Sanity script |
|---|---|---|---|
| AgentField | `AGENTFIELD_API_KEY` | `backend/orchestrator/agentfield_runner.py` | `backend/scripts/sanity_agentfield.py` |
| Actionbook | `ACTIONBOOK_API_KEY` | `backend/adapters/actionbook.py` | `backend/scripts/sanity_actionbook.py` |
| Bright Data | `BRIGHT_DATA_API_TOKEN` | `backend/adapters/bright_data.py` | `backend/scripts/sanity_bright_data.py` |
| Evermind | `EVERMIND_API_KEY` | `backend/adapters/evermind.py` | `backend/scripts/sanity_evermind.py` |
| Butterbase | `BUTTERBASE_API_KEY` | `backend/adapters/butterbase.py` | `backend/scripts/sanity_butterbase.py` |
| Qwen Cloud | `QWEN_API_KEY` | `backend/adapters/llm_cascade.py` (via TokenRouter) | `backend/scripts/sanity_qwen.py` |
| Z.ai | `ZAI_API_KEY` | `backend/adapters/llm_cascade.py` (via TokenRouter) | `backend/scripts/sanity_zai.py` |
| TokenRouter | `TOKEN_ROUTER_API_KEY` | `backend/adapters/token_router.py` | `backend/scripts/sanity_token_router.py` |
| Zeabur | (deploy) | `zeabur.json` + deploy URL in SUBMISSION.md | (deploy URL responds 200) |

Each sanity script: ~10–20 lines. Hits the real API with the real key. Prints the response. Exit 0 on success, 1 on failure. CI-friendly.

---

## 9. BUILD WAVES (Phase 3)

### Wave A — Skeleton (pre-event, T-1 day)
**Goal:** every API path returns a fixture-based response. Frontend renders the full UI shell with mock streamed events.

Tasks:
1. `uv venv` + FastAPI + pydantic-settings + sse-starlette + jinja2
2. Define every schema in `backend/schemas/`
3. Stub every adapter to return cached fixture JSON
4. Wire `POST /api/run` → fake AgentField runner that emits all SSE events sequentially with 500ms delays
5. React + Tailwind + Vite scaffold; build all 10 components with mock data
6. `useAgentStream` hook consumes the SSE; the whole timeline animates
7. Both presets work end-to-end with fixtures only
8. Zeabur deploy live with the fixture-only build

**Wave A success criterion:** Click "Run Jenny" on the Zeabur URL → see the full 90-sec demo run with fake (fixture) data. No real API calls yet. Backup video already possible.

### Wave B — One real shock-moment path (event-day morning)
**Goal:** the CA cottage food scrape is REAL via Bright Data. Everything else stays on fixtures.

Tasks:
1. Bright Data adapter: real implementation. Sanity script passes.
2. Reality & Compliance Agent: real Bright Data call, real citation rendered.
3. Toggle `USE_FIXTURES=false` for Bright Data path only (other adapters still fixture-only).
4. Smoke test: Jenny run → real BLOCK card with real citation.

**Wave B success criterion:** the SHOCK MOMENT is real. Even if nothing else is, we have a real-data demo.

### Wave C — All sponsors real (event-day, 12:00–3:30 PM)
**Goal:** every sponsor's real API is called in at least one run.

Tasks (parallelizable):
- Actionbook: real Etsy live session + real publish form-fill
- Qwen / Z.ai / TokenRouter: real LLM cascade behind every agent
- Evermind: real write + real cross-user query after 2 runs
- Butterbase: real run-history persist + real launch page hosting
- AgentField: real swarm orchestration (replaces the fake runner)
- All sanity scripts pass
- SUBMISSION.md filled with proof ledger

**Wave C success criterion:** `USE_FIXTURES=false` for everything; full Jenny + Jessica runs complete with all real APIs.

### Polish + Submit (3:30–4:00 PM)
- Record backup Loom
- Rehearse 3x consecutively under 95s
- Submit to `tinyurl.com/agentforgesubmit` (by 4:00 PM, not 4:30)
- Push final commit to GitHub
- Open WiFi-free fallback test one more time

---

## 10. DEPENDENCIES (pinned, installed via uv)

### Backend (`pyproject.toml`)
```
fastapi
uvicorn[standard]
sse-starlette
pydantic
pydantic-settings
httpx
jinja2
python-multipart
tenacity                # retry/backoff
structlog               # JSON logs for Zeabur observability
```

Optional / per-sponsor (added as adapters land):
```
agentfield              # if there's a Python SDK; else httpx-direct
brightdata-sdk          # if available; else httpx
openai                  # Qwen + Z.ai both support OpenAI-compatible API
```

### Frontend (`package.json`)
```
react ^18
react-dom ^18
react-router-dom ^6
tailwindcss ^3
vite ^5
typescript ^5
@microsoft/fetch-event-source   # SSE client
clsx
```

---

## 11. AVINASH SIGN-OFF (before Phase 3 starts)

Read this whole file end-to-end. Confirm:

- [ ] Scope lock §0 is what we're shipping
- [ ] 4 screens / 10 components is enough — no 5th screen sneaking in
- [ ] Schemas in §4 cover the demo's data needs
- [ ] Fixture JSONs in §5 match the locked personas
- [ ] Fallback plan in §7 is acceptably honest (we surface fallbacks visibly)
- [ ] Sponsor proof ledger §8 is the no-faking contract you wanted
- [ ] Build waves in §9 are realistic for solo+pre-build

**Sign-off unlocks Phase 3 — Wave A starts.** No code touched until this is green.

---

🐶 — Avi
