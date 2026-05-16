# 🏗 ARCHITECTURE — Mom's Saheli (v1.1)

> One diagram. Five agents. Nine sponsor tools, each with a pointable role.
> Companion to `PLAN_LOCKED.md`. v1.1 adds Butterbase + repositions Actionbook to drive a real Etsy browser session live in the demo.

---

## 🗺 THE DIAGRAM

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          USER (Jenny or Jessica)                          │
│              Income gap · Skills · Hours · Budget · Constraints           │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │  (Text intake, MVP)
                                   ▼
                  ┌────────────────────────────────────┐
                  │       FRONTEND (React + Tailwind)  │
                  │   • Intake screen                  │
                  │   • Agent swarm timeline (SSE)     │
                  │   • Market evidence cards          │
                  │   • Compliance BLOCK panel         │
                  │   • Launch packet preview          │
                  │   • Memory panel                   │
                  └────────────────┬───────────────────┘
                                   │  REST + SSE
                                   ▼
        ┌──────────────────────────────────────────────────────────┐
        │           BACKEND  (FastAPI on Zeabur)                    │
        │                                                            │
        │   POST /api/run            → kicks off swarm               │
        │   GET  /api/stream/{run_id} → live agent events (SSE)      │
        │   POST /api/publish        → triggers Launch Agent         │
        │   GET  /api/memory         → Evermind trajectories         │
        │   GET  /api/runs           → run history (Butterbase)      │
        │   GET  /launch/{slug}      → public Mom's Saheli page      │
        └────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
        ┌──────────────────────────────────────────────────────────┐
        │           AgentField  ─  Orchestrator + Audit Trail       │
        │       (visible swarm timeline · streamed to frontend)     │
        └────┬──────────┬──────────┬──────────┬──────────┬─────────┘
             │          │          │          │          │
             ▼          ▼          ▼          ▼          ▼
        ┌────────┐ ┌──────────┐ ┌──────────────┐ ┌────────┐ ┌──────────┐
        │Profile │ │ Market   │ │ Reality &    │ │ Launch │ │ Memory   │
        │ Agent  │ │ Scout    │ │ Compliance   │ │ Agent  │ │ Agent    │
        └───┬────┘ └────┬─────┘ └──────┘ └───┬────┘ └────┬─────┘
            │           │              │             │           │
            │           ▼              ▼             ▼           ▼
            │   ┌──────────────┐ ┌──────────┐  ┌──────────┐ ┌──────────┐
            │   │  ACTIONBOOK  │ │  BRIGHT  │  │ACTIONBOOK│ │ EVERMIND │
            │   │  (live Etsy  │ │   DATA   │  │ (publish │ │ (cross-  │
            │   │   browser    │ │ (state-  │  │  launch  │ │  user    │
            │   │   on stage)  │ │  law     │  │  page    │ │  pattern │
            │   │  +           │ │  scrape  │  │  via     │ │  surface)│
            │   │  BRIGHT DATA │ │  per     │  │  form    │ │          │
            │   │  (bulk comps:│ │  persona)│  │  fill)   │ │          │
            │   │   Poshmark,  │ │          │  │          │ │          │
            │   │   Craigslist)│ │          │  │          │ │          │
            │   └──────────────┘ └──────────┘  └────┬─────┘ └──────────┘
            │                                       │
            │                                       ▼
            │                            ┌─────────────────────┐
            │                            │  Mom's Saheli Page  │
            │                            │  (hosted on         │
            │                            │   BUTTERBASE,       │
            │                            │   public URL,       │
            │                            │   shareable)        │
            │                            └─────────────────────┘
            │
            ▼
       ┌────────────────────────────────────────────────────────────────┐
       │   PERSISTENCE LAYER                                             │
       │   ┌────────────────┐   ┌────────────────┐   ┌──────────────┐   │
       │   │  BUTTERBASE    │   │   EVERMIND     │   │  LOCAL CACHE │   │
       │   │  (run history, │   │  (semantic     │   │  (fixture +  │   │
       │   │   profiles,    │   │   memory       │   │   fallback   │   │
       │   │   launch pages,│   │   across runs, │   │   scrapes    │   │
       │   │   light auth)  │   │   pattern      │   │   for demo   │   │
       │   │                │   │   discovery)   │   │   reliability)│  │
       │   └────────────────┘   └────────────────┘   └──────────────┘   │
       └────────────────────────────────────────────────────────────────┘
            │
            ▼
       ┌────────────────────────────────────────────────────────────────┐
       │     LLM CASCADE  ─  every agent calls through TokenRouter      │
       │     TokenRouter → Qwen Cloud (primary) → Z.ai GLM-5.1 (fallback)│
       └────────────────────────────────────────────────────────────────┘
```

---

## 🔁 DATA FLOW (the 90-second story, end to end)

1. **User picks preset** (Jenny or Jessica) on the intake screen.
2. Frontend → `POST /api/run` with profile JSON.
3. Backend creates `run_id`, persists profile to **Butterbase**, opens SSE stream, kicks AgentField swarm.
4. **Profile Agent** (Qwen via TokenRouter) normalizes input → emits `profile_ready` event.
5. **Market Scout** fires evidence-gathering in parallel:
   - **Actionbook** opens a live Etsy browser session, searches the persona's category (e.g. "kids lunch printable" for Jessica, "weekend meal pack" for Jenny), extracts top 10 sold listings with prices. **Visible on screen — the URL bar shows etsy.com.**
   - **Bright Data** runs bulk scrapes on Poshmark sold prices + local Craigslist/Nextdoor rate scans.
   - Each result streams in as an `EvidenceCard` event as it arrives.
6. **Market Scout** (Qwen) synthesizes 6–10 ranked options → emits `opportunities_ranked`.
7. **Reality & Compliance Agent** runs in parallel for the top 3:
   - Constraint math (hours, budget, no-delivery, no-nights, childcare).
   - **Bright Data** live scrape of the `{state}` permit / cottage-food page.
   - Emits `compliance_check` events (BLOCK with citation OR PASS).
8. UI shows the **BLOCK** card with the actual cited regulation. **Shock moment.**
9. **Reality Agent** returns the surviving winner option.
10. **Launch Agent** (Qwen) generates the packet — offer copy, price, outreach drafts, 7-day plan.
11. **Launch Agent** calls **Actionbook** a second time → fills `/launch/new` form on a **Butterbase-hosted** Mom's Saheli page → publishes → returns the public URL.
12. UI shows live launch page preview + clickable URL.
13. **Memory Agent** writes the trajectory to **Evermind** (chosen path + rejected paths + citations).
14. After the second persona run, Memory Agent surfaces the cross-user learned pattern via an Evermind query.
15. Run complete. SSE stream closes. Run summary committed to Butterbase for the history page.

---

## 🧩 KEY DESIGN DECISIONS

| Decision | Why |
|---|---|
| **Actionbook drives REAL Etsy live on stage** | Sponsor used for what it's built for (browser actions on real sites). Visible URL bar = judges see "real internet" not "another chatbot." Bright Data still does heavy scraping; the two have complementary roles. |
| **Bright Data for compliance scrape** | Law pages are public, structured, and ideal for scrape SDK. Compliance is where "live state-aware" matters most — never hardcode a state DB. |
| **Streaming SSE for agent events** | Judges must SEE the swarm fire, not see a 30-sec spinner end with a result. AG-UI pattern. |
| **Butterbase hosts launch pages + run history + auth** | Genuine BaaS role. Each mom owns her data. Sponsor pointable. We control the failure surface (not Etsy seller portal). |
| **Reality & Compliance merged into ONE agent** | Both checks share input (profile + option) and output (BLOCK / PASS + reason). Same logical responsibility (gatekeeping). |
| **AgentField for orchestration** | Sponsor-stack genuine use + free observability UI for the swarm timeline. |
| **TokenRouter → Qwen → Z.ai cascade** | Quota safety. Skip Nosana (no custom GPU). All LLM traffic visible/billable in one place. |
| **5 agents (not 6, not 8)** | 90-sec demo can't track more. SOLID: each agent has one clear responsibility. |
| **Pre-computed fixtures cached** | If live Bright Data / Actionbook fails on stage, fallback to cached real responses. Honest disclosure in SUBMISSION.md. |

---

## 📁 REPO LAYOUT (planned for build — v1.1)

```
momsaheli/
├── backend/
│   ├── main.py                         # FastAPI app, SSE endpoints
│   ├── settings.py                     # env loader (pydantic-settings)
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── profile_agent.py
│   │   ├── market_scout.py
│   │   ├── reality_compliance.py
│   │   ├── launch_agent.py
│   │   └── memory_agent.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── actionbook.py               # live Etsy + form publish
│   │   ├── bright_data.py              # state law + bulk comps
│   │   ├── evermind.py                 # memory writes + queries
│   │   ├── butterbase.py               # run history + page hosting + auth
│   │   ├── token_router.py             # LLM cascade (Qwen→Z.ai)
│   │   └── llm_cascade.py              # thin wrapper used by all agents
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── agentfield_runner.py        # swarm definition + event emit
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── profile.py
│   │   ├── opportunity.py
│   │   ├── evidence.py
│   │   ├── compliance.py
│   │   ├── launch_packet.py
│   │   └── memory.py
│   ├── fixtures/
│   │   ├── jenny.json
│   │   ├── jessica.json
│   │   └── cached_scrapes/             # demo-day fallback
│   │       ├── ca_cottage_food.json
│   │       ├── etsy_kids_lunch.json
│   │       └── poshmark_meal_prep.json
│   ├── templates/
│   │   └── launch_page.html            # rendered into Butterbase-hosted page
│   └── scripts/
│       ├── sanity_qwen.py              # one per sponsor — prove the call works
│       ├── sanity_zai.py
│       ├── sanity_token_router.py
│       ├── sanity_bright_data.py
│       ├── sanity_actionbook.py
│       ├── sanity_evermind.py
│       ├── sanity_butterbase.py
│       └── sanity_agentfield.py
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx                # intake + preset buttons (Jenny/Jessica)
│   │   │   ├── Run.tsx                 # swarm timeline + evidence + compliance
│   │   │   ├── LaunchPage.tsx          # public Mom's Saheli launch page renderer
│   │   │   └── History.tsx             # past runs (Butterbase-backed)
│   │   ├── components/
│   │   │   ├── AgentTimeline.tsx
│   │   │   ├── EvidenceCard.tsx
│   │   │   ├── ComplianceBlock.tsx
│   │   │   ├── LaunchPacket.tsx
│   │   │   ├── MemoryPanel.tsx
│   │   │   └── PresetButtons.tsx
│   │   └── hooks/
│   │       └── useAgentStream.ts       # SSE consumer
│   ├── tailwind.config.js
│   └── package.json
├── tests/
│   ├── test_schemas.py
│   ├── test_agents_unit.py             # uses USE_FIXTURES=true
│   └── e2e_jenny_jessica.py            # full run-through, asserts events
├── .env.example                        # every sponsor key listed
├── zeabur.json                         # deploy config
├── PLAN_LOCKED.md                      # the strategy (v1.1)
├── ARCHITECTURE.md                     # this file
├── SPEC.md                             # screens, schemas, endpoints, fixtures
├── DEMO_SCRIPT.md                      # second-by-second pitch + presenter cues
├── SUBMISSION.md                       # honest disclosure + sponsor proof
└── README.md
```

---

## 🔑 ENV VARS (the .env contract)

```
# LLM cascade
TOKEN_ROUTER_API_KEY=
QWEN_API_KEY=
QWEN_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
ZAI_API_KEY=
ZAI_BASE_URL=https://api.z.ai/api/paas/v4

# Web intel
BRIGHT_DATA_API_TOKEN=
BRIGHT_DATA_ZONE=
ACTIONBOOK_API_KEY=
ACTIONBOOK_WORKSPACE_ID=

# Memory + backend
EVERMIND_API_KEY=
EVERMIND_NAMESPACE=moms-saheli
BUTTERBASE_API_KEY=
BUTTERBASE_PROJECT_ID=

# Orchestration
AGENTFIELD_API_KEY=
AGENTFIELD_PROJECT=moms-saheli

# Runtime
APP_BASE_URL=https://moms-saheli.zeabur.app
USE_FIXTURES=false   # true only for offline dev / demo fallback
```

---

## ✅ ARCHITECTURE SIGN-OFF CHECKLIST

- [x] 5 named agents with single responsibilities (SOLID)
- [x] Each of 9 sponsor tools has a clear, pointable role
- [x] No hidden hardcoded state / region / persona
- [x] Failure surface is OURS (Butterbase-hosted page) not external (Etsy seller portal)
- [x] Live streaming UI for visible swarm beat
- [x] Memory beat is genuine (cross-user pattern via Evermind query, not save+show)
- [x] Repo layout supports solo 5-hour build with sponsor-proof scripts
- [x] No-faking pact baked into repo structure (sanity scripts per sponsor)

---

🐶 — Avi
