# AGENTS.md

> **Read me first.** I'm the context any AI agent (Claude, ChatGPT, Cursor, etc.) needs
> to instantly become as smart about this project as the previous agent was. If you're
> Avinash's other-laptop AI — welcome. Read me top-to-bottom before touching anything.

---

## 0. 🚦 Session-resume snapshot (read THIS box first)

**Last session ended:** 2026-05-16, end of Day 1.  
**Backend running?** No (was running locally; restart with the command in §7).  
**Frontend running?** No.  
**Repo clean + pushed?** Yes — all changes on `main`.

**What we shipped this session (commits b703d84 → 3bce0d5):**
1. ✅ Real Gemini 2.5 Flash wired into LLM cascade (`google-generativeai` SDK, JSON mode)
2. ✅ Real Tavily SERP wired as Bright Data stand-in (free 1000/mo tier)
3. ✅ Cached state-law scrape per profile (Tavily calls 3 → 1)
4. ✅ Parallel prefetch state-law with Gemini ranking (saves ~3s)
5. ✅ Market Scout surfaces ALL opps (so the BLOCK moment fires on Daily Tiffin)
6. ✅ Brain-transplant docs: this file + accurate README + scripts/setup.sh
7. ✅ Folder cleanup: planning docs moved into `docs/` + `docs/legacy/`

**Verified end-to-end:** Jenny run = 6 opps ranked by real Gemini, 3 BLOCKs with real 
`.gov` citation URLs from Tavily, real Gemini-written launch page at 
`/launch/jenny-jenny-s-weekend-family-dinners`. Total run time ~38s (real LLM latency).

**👉 Exact next action when Avinash returns:** answer one of these 3 open decisions 
(see §9). Leading candidates: **AgentField hybrid wrap** (lights up `:8080` dashboard, 
low risk) and **`gemini-2.5-flash-lite` swap** (~38s → ~15s).

**Tomorrow-morning booth runs:**
- Bright Data → free Web Unlocker zone → set `BRIGHT_DATA_ZONE=` in `.env` → done
- Qwen Cloud → grab key → paste into `.env` → cascade auto-promotes Qwen to primary

---

## 1. What is Mom's Saheli?

A multi-agent system that surfaces realistic side-income opportunities for working moms
under hard constraints (hours, budget, dependents, transport), checks them against the
**actual** state cottage-food / business law, generates a Gemini-written launch page
for the winner, and publishes it — end-to-end in one click.

**Why it matters:** ~7.3M single moms in the U.S., median income $40K, childcare eats
~35% of take-home. They're not short on effort, they're short on *margin*. We close it.

**Built for:** Agent Forge AI Hackathon, San Francisco, May 16 2026. Solo build by
Avinash, paired with Avi (his code agent, that's me).

---

## 2. The Five Agents (the swarm)

| # | Agent | File | What it does | Live? |
|---|---|---|---|---|
| 1 | **Profile Agent** | `app/agents/profile_agent.py` | Normalize raw persona JSON → `Profile` schema | ✅ deterministic (no LLM needed) |
| 2 | **Market Scout** | `app/agents/market_scout.py` | Pull evidence cards (Etsy/Castiron/Nextdoor/FB) + rank opportunities | ✅ **Real Gemini** ranks; evidence cards are cached fixtures (Actionbook key coming) |
| 3 | **Reality & Compliance** | `app/agents/reality_compliance.py` | Check each opp against constraints + state cottage-food law, BLOCK with citation | ✅ **Real Tavily** scrapes state law (`.gov` URLs); constraint math deterministic |
| 4 | **Launch Agent** | `app/agents/launch_agent.py` | Generate offer name / tagline / price / target / 7-day plan / landing page | ✅ **Real Gemini** writes the whole packet + page renders via Jinja2 |
| 5 | **Memory Agent** | `app/agents/memory_agent.py` | Persist run trajectory + surface cross-user learned pattern | 🟡 Local mirror works; real Evermind API pending key |

The orchestrator (`app/orchestrator/runner.py`) wires them, streams every event over
SSE to the React frontend, and writes a real launch page to `/launch/{slug}`.

---

## 3. Current State Matrix (as of last commit)

### ✅ LIVE and proven end-to-end
- **Gemini 2.5 Flash** via `google-generativeai` SDK, JSON mode, async-wrapped
- **Tavily** free SERP, returning real `.gov` / `nationalaglawcenter.org` URLs
- **FastAPI backend** on `:8000` with SSE streaming (`/api/stream/{run_id}`)
- **React + Vite frontend** on `:5173` with live timeline UI
- **Real launch pages** rendered server-side (`/launch/{slug}`)
- **Local persistence** of runs + pages in `backend/app/_local_store/` (gitignored)
- **Two personas** (Jenny in CA = food/permit BLOCKs, Jessica in TX = digital/PASS)

### 🟡 Wired with key check + graceful fallback
- **Bright Data SDK** installed; token validated; **needs a zone tomorrow** (free at booth) → 1-line swap from Tavily
- **Z.ai GLM** in cascade as fallback (activates on `ZAI_API_KEY`)
- **TokenRouter** adapter (activates on `TOKEN_ROUTER_API_KEY`)
- **Actionbook**, **Evermind**, **Butterbase** — adapters exist, key checks gate them, fixtures cover the path

### ⏳ Planned but not built yet
- **AgentField refactor** — SDK installed; need to wrap orchestrator as `@reasoner`(s)
  to light up the `:8080` control-plane dashboard. Open question: full split (5 reasoners)
  vs. hybrid wrap (1 reasoner).
- **Demo polish** — sponsor logo badges on each timeline event, citation tooltips
- **Backup demo video** — Loom recording for "internet died on stage" insurance

---

## 4. The Two Demo Personas

| | **Jenny** (CA, working mom) | **Jessica** (TX, single mom) |
|---|---|---|
| State | California | Texas |
| Skills | home cooking, kid-friendly meals, meal prep | graphic design, Canva, social media |
| Hours/wk | 5 | 6 |
| Budget | $80 | $50 |
| Constraints | no daily prep, weekends only, no commercial kitchen, no permit, child pickup at 3pm | fully remote / async, no live calls, no inventory |
| **The drama** | Daily Tiffin ranks #1 by $/mo ($850), then BLOCKs on CA cottage-food law | Etsy printable wins — purely digital, zero compliance hits |
| Winner (last run) | "Jenny's Weekend Family Dinners" — $28/pack | (run her in UI to see) |

**The story arc** is intentional: same swarm, two states, two outcomes. Proves it's
not hardcoded.

---

## 5. Architecture Decisions Made (and why)

| Decision | Rationale |
|---|---|
| LLM cascade order: **Gemini → Qwen → Z.ai** | Gemini is the only LLM with a real key today. Qwen becomes primary tomorrow when sponsor key arrives — just need to reorder the providers list in `llm_cascade.py`. |
| **Tavily as Bright Data stand-in** | BD account has no zone; creating one needs a payment method. Tavily is free, returns clean JSON. Same return shape so swap is 1 line. |
| **Cache state-law scrape per profile** | Saves N-1 redundant Tavily calls (all opps share same state). Scrape happens once, passed into Compliance as `pre_fetched_law=...`. |
| **Parallel prefetch state-law with Gemini ranking** | Both depend only on profile. Saves ~3s. |
| **Market Scout surfaces ALL opportunities** (incl. eventually-blocked) | The BLOCK moment is the demo's wow — Daily Tiffin needs to rank #1 by $$, *then* get blocked with the citation. Don't pre-filter. |
| **`USE_FIXTURES=true` is a soft flag** | Only gates the expensive Bright Data zone scrape. Tavily / Gemini / others fire on key presence. |
| **Local file-based store for runs + pages** | Butterbase comes later; until then, `_local_store/` lets us prove "she clicks → real shareable URL appears" without external deps. |
| **SSE not WebSockets** | Simpler, browser-native, perfect for one-way agent timeline streaming. |
| **Pydantic schemas everywhere** | Type-safe contracts between agents; one schema change → mypy/IDE catches the rest. |

---

## 6. Files an Agent Touches Most Often

```
backend/app/
├── orchestrator/runner.py   ← The 5-agent choreography + SSE emits
├── agents/                  ← One file per agent, ~150 lines each
├── adapters/                ← One file per external service (sponsor)
│   ├── llm_cascade.py       ← Gemini/Qwen/Z.ai providers
│   ├── tavily.py            ← Live web search
│   ├── bright_data.py       ← Has 3-tier fallback: BD → Tavily → fixture
│   └── ...
├── schemas/                 ← Pydantic models — START HERE for any change
├── fixtures/                ← Personas + cached scrapes (offline safety net)
└── settings.py              ← Pydantic-settings, reads ../.env

frontend/src/
├── pages/Run.tsx            ← The "Run Jenny" screen
├── hooks/useAgentStream.ts  ← SSE consumer
└── components/              ← Timeline, EvidenceCard, ComplianceCheck, etc.

docs/                       ← Design context (see docs/README.md for the map)
├── ARCHITECTURE.md          ← diagrams + sponsor mapping
├── NORTH_STAR.md            ← mission, what we say NO to
├── DEMO_SCRIPT.md           ← the 90-sec stage pitch
└── legacy/                  ← pre-build docs, tagged "may have drifted"
```

---

## 7. How to Bring a Fresh Laptop Up to Speed

```bash
# 1. Clone
git clone https://github.com/Avinash07-git/momsaheli.git
cd momsaheli

# 2. One-command setup (creates venv, installs all deps, copies .env.example)
./scripts/setup.sh

# 3. Edit .env and paste keys (see §8 for what currently exists)
$EDITOR .env

# 4. Start backend (Terminal 1)
cd backend && source .venv/bin/activate
uvicorn app.main:app --port 8000

# 5. Start frontend (Terminal 2)
cd frontend && npm run dev

# 6. Open http://localhost:5173, click Run Jenny — watch the live swarm
```

If `uv` isn't installed: `brew install uv` (mac). `setup.sh` auto-detects Walmart network.

---

## 8. Keys Currently in Use (DO NOT commit .env)

| Key | Where to get | Notes |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey | 30-sec signup. Avinash has one in his local .env. |
| `TAVILY_API_KEY` | https://tavily.com | Free 1000 searches/mo. Avinash has one. |
| `BRIGHT_DATA_API_TOKEN` | https://brightdata.com/cp/api_keys | Token works; **zone TBD tomorrow at booth**. |
| `BRIGHT_DATA_ZONE` | Bright Data dashboard | Create "Web Unlocker" zone, name it `web_unlocker1`. |
| `QWEN_API_KEY` | Pickup at hackathon booth (Day 2) | Once set, cascade promotes Qwen to primary. |
| All others | Sponsor booths | Adapter exists; flips on as soon as key arrives. |

**`.env` is gitignored.** To sync keys across laptops, manually copy `.env` via 1Password
/ Bitwarden / a secure note — never commit it.

---

## 9. Open Decisions Waiting for Avinash

Asked at end of last session, timed out — pick these up when he's back:

1. **38-second live run too slow?**
   - (a) Add Fast Mode toggle (canned 9s + live 40s)
   - (b) Keep only live — own the wait
   - (c) Swap to `gemini-2.5-flash-lite` (3x faster)
   - (d) Parallelize via predictive packet generation

2. **Next big build?**
   - (a) Full AgentField refactor (5 distinct `@reasoner`s)
   - (b) AgentField hybrid wrap (1 reasoner, dashboard lights up)
   - (c) UI polish (sponsor logos, animations)
   - (d) Record backup demo video

3. **Tomorrow morning at booths:** Bright Data zone + Qwen key → both 1-line swaps.

---

## 10. Gotchas + Things Future-Me Should Know

- **Gemini latency is real**: ~16s for ranking, ~17s for packet. These dominate the ~38s
  total wall time. Don't add `asyncio.sleep` "for drama" — the pills already fill in
  during natural network waits.
- **Gemini 2.5 Flash supports `response_mime_type: application/json`** — use that
  over prompt-engineering for JSON output. See `llm_cascade._try_gemini`.
- **`google-generativeai` is sync**; we wrap with `asyncio.to_thread` to stay async.
  (The package is technically deprecated for `google-genai`, but works fine for now.)
- **Tavily's `answer` field is a synthesized summary** — perfect for `citation_text`,
  avoids us having to summarize.
- **The Bright Data SDK auto-tries to create a `sdk_unlocker` zone** on context-manager
  enter; this 403s without a payment method. Always pass `auto_create_zones=False`.
- **Etsy is digital-only** in our taxonomy — never route prepared-food evidence to it.
  Use Castiron / Nextdoor / FB Groups. See commit `98abc37`.
- **The `_local_store/` directory is gitignored** — run state never gets pushed.
  Wipe it locally with `rm -rf backend/app/_local_store` to reset.
- **Frontend dev server proxies `/api` → `:8000`** (see `frontend/vite.config.ts`).

---

## 11. Avinash's Vibes (so the agent matches)

- Wants **REAL not fake** — no mocked LLM responses, no "demo data". If it's mocked,
  label it clearly and have a real-key swap ready.
- Hates being asked the same question twice; **commit and push** as soon as a milestone
  works so nothing is lost.
- Informal tone, playful, occasional sarcasm; he calls his code agent "Avi" 🐶.
- He **does not want to add a payment method to sponsor accounts** — work around it
  with free tiers + booth-credit swaps.
- Two laptops, jumps between them; **GitHub is the canonical sync** — always push.
- **Time-pressured** (hackathon clock); prioritize working demo over architectural
  purity, but never sacrifice the "everything is real" story.

---

## 12. Recent Commit History (read for context)

```
3bce0d5  docs: brain-transplant repo state — AGENTS.md, accurate README, setup script
189bfe1  perf: parallelize Tavily state-law fetch with Gemini ranking
b703d84  feat(real-apis): Gemini 2.5 Flash + Tavily search are LIVE
98abc37  fix(market-scout): Etsy is for digital only — route food to Castiron
081fe75  feat(phase-1): full scaffold — backend FastAPI swarm + frontend Vite/React/TS
```

Run `git log --oneline -20` for more.

---

## 13. If You're Stuck

- Run all sanity scripts: `cd backend && for f in scripts/sanity_*.py; do python $f; done`
- Re-read this file
- Check `/tmp/momsaheli_be.log` for the most recent backend run
- Worst case: `rm -rf backend/app/_local_store` and re-run from a clean slate
- DM Avinash on Slack — but only after exhausting the above

🐶 Welcome to the swarm. Now go make a mom's evening easier.

— Avi (the code puppy)
