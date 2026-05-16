# 🌸 Mom's Saheli

> **The friend every working mom can finally afford.**
> A 6-agent swarm that surfaces real income paths for the underbanked workforce —
> starting with America's 7 million single moms.

**Agent Forge AI Hackathon** · San Francisco · May 16 2026 · solo build.

[![Live workflow](https://img.shields.io/badge/AgentField-nested%20waterfall-fcd34d?style=flat-square)](https://agentfield.ai)
[![Real LLM](https://img.shields.io/badge/Gemini%202.5%20Flash-live-b45309?style=flat-square)](https://ai.google.dev)
[![Real citations](https://img.shields.io/badge/state%20law-cited%20live-15803d?style=flat-square)](https://tavily.com)
[![License: MIT](https://img.shields.io/badge/license-MIT-18181b?style=flat-square)](./LICENSE)

> 🤖 **AI agents continuing this work:** read **[`AGENTS.md`](./AGENTS.md)** first.
> It's the brain transplant — current state, open decisions, lane assignments.
> Every other doc assumes you've read it.

---

## 🎯 The problem

A consultant costs **$2,000**. A bookkeeper, a lawyer, a marketer — each **$200/hr**.

Single moms can't afford any of them. But they're the ones who need them most:

| Number | Meaning | Source |
|---|---|---|
| **7.3M** | single moms in America | [Center for American Progress](https://www.americanprogress.org/article/single-mothers-and-poverty/) |
| **75%** | are already working, most full-time | CAP |
| **$40K** | median income, working single mom | CAP |
| **35%** | of that income eaten by childcare | [Child Care Aware](https://www.childcareaware.org/) |
| **$216–$329B** | macro GDP loss from the childcare crisis | [BPC](https://bipartisanpolicy.org/) |

They're not short on effort. They're short on **margin**. Mom's Saheli closes the margin.

---

## ✨ What it does

Click **Run Jenny** (or **Run Jessica**) and watch 6 AI agents collaborate live:

| # | Agent | What it does | Sponsor |
|---|---|---|---|
| 1 | **Profile** | Normalize skills, hours, budget, hard constraints | Pydantic |
| 2 | **Market Scout** | Pull evidence cards (Etsy / Castiron / FB groups), rank by realistic net monthly $ via Gemini | Bright Data + Actionbook + Gemini |
| 3 | **Reality & Compliance** | Web-search the state's actual cottage-food law, **block illegal options with the live `.gov` citation on screen** | Tavily / Bright Data |
| 4 | **Launch** | Write the offer, copy, price, target customer + 7-day plan; publish a real shareable landing page | Gemini + Actionbook + Butterbase |
| 5 | **Customer Activation** | Find public customer paths, include approved mom channels, rank approval-gated first-customer actions | Bright Data / Tavily + Actionbook |
| 6 | **Memory** | Persist trajectory + surface a cross-user learned pattern | Evermind |

**Two real moms. Same six agents. Completely different output.**
Jenny's #1 ranked option gets BLOCKED by California cottage-food law → pivots to a legal winner.
Jenny then gets a local, mom-network first-customer move; Jessica gets async, draft-only digital actions.
Proves nothing is hardcoded — it's the regulation, the constraints, and the math doing the work.

---

## 🎬 The demo

```bash
git clone https://github.com/Avinash07-git/momsaheli.git
cd momsaheli
cp .env.example .env
# paste GEMINI_API_KEY (free, 30s at https://aistudio.google.com/apikey)
# paste TAVILY_API_KEY (free, 30s at https://tavily.com)
./scripts/start.sh
```

That boots **4 processes** with auto-fallbacks:

| Process | Port | Skipped if… |
|---|---|---|
| AgentField control plane | `:8080` | `af` CLI not installed (just shows install hint) |
| FastAPI backend (SSE streaming) | `:8000` | never — the demo path |
| AgentField agent (7 reasoners) | `:8001` | `AGENTFIELD_API_KEY` empty OR `:8080` unreachable |
| React frontend | `:5173` | never |

Then visit **http://localhost:5173** and click **Run Jenny**.
~38 seconds of real LLM work, real BLOCKs with real `.gov` citations, real launch page at `/launch/{slug}`.

For judges: hop to **http://localhost:8080/ui/** to see the **AgentField nested execution waterfall** — one parent (`run_full_swarm`) with 6 child spans, each with its own inputs/outputs/timings.

---

## 🏗 Architecture

```
                    ┌─────────────────────────────────────────┐
                    │     React frontend (Vite, :5173)        │
                    │  Home · Run · History · LaunchPage      │
                    └────────────┬────────────────────────────┘
                                 │  SSE (one stream per run_id)
                    ┌────────────▼────────────────────────────┐
                    │     FastAPI backend (:8000)             │
                    │  ┌───────────────────────────────────┐  │
                    │  │  SwarmRunner — orchestrates 6     │  │
                    │  │  agents, emits SSE per step       │  │
                    │  └────┬──────────────────────────────┘  │
                    └───────┼─────────────────────────────────┘
                            │
       ┌────────────────────┼────────────────────────────────┐
       │                    │                                │
  ┌────▼─────┐  ┌──────────▼──────────┐  ┌─────────────────▼────────┐
  │ Profile  │→ │  Market Scout       │→ │ Reality & Compliance     │
  │ (pydantic│  │ (Gemini ranks comps │  │ (Tavily live SERP +      │
  │  pass)   │  │  from real listings)│  │  Gemini verdict)         │
  └──────────┘  └─────────────────────┘  └─────────────────┬────────┘
                                                           │
                          ┌────────────────────────────────┘
                          ▼
                   ┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐
                   │   Launch    │ →  │ Customer         │ →  │     Memory       │
                   │ (Gemini +   │    │ Activation       │    │ (Evermind cross  │
                   │  Butterbase │    │ (public leads +  │    │  -user pattern)  │
                   │  publish)   │    │  approvals)      │    └──────────────────┘
                   └─────────────┘    └──────────────────┘

                  ┌─────────────────────────────────────────┐
                  │ AgentField agent (:8001)                │
                  │ 6 @reasoner endpoints; nested waterfall │
                  │ visible at http://localhost:8080/ui/    │
                  └─────────────────────────────────────────┘
                  (Same code as above — exposed for observability)
```

Full architecture doc: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md).

---

## ✅ Real vs. mocked (honest table)

| Capability | Status | How |
|---|---|---|
| LLM reasoning + copy generation | ✅ **LIVE** | Gemini 2.5 Flash, real JSON-mode calls |
| State law web search + citation | ✅ **LIVE** | Tavily free SERP returning real `.gov` URLs |
| Constraint math (BLOCK logic) | ✅ **LIVE** | Deterministic Python, not LLM-hallucinated |
| FastAPI backend + SSE streaming | ✅ **LIVE** | Every agent step streams to UI in real time |
| AgentField 7-reasoner nested waterfall | ✅ **LIVE** | One parent, 6 nested child spans in dashboard |
| Server-rendered launch pages | ✅ **LIVE** | Jinja2 + Tailwind, real shareable URL |
| Local persistence (runs + pages) | ✅ **LIVE** | File-backed mirror of Butterbase contract |
| Customer Activation Agent | ✅ **LIVE** | Deterministic action ranking with live lead logic + fixture fallback |
| Customer Lead Search | 🟡 Live when configured | Bright Data/Tavily when configured, fixture fallback otherwise |
| Actionbook Activation | 🟡 Approval-gated | Preview/fallback when key missing; no post or submit without explicit approval |
| Bright Data scraping | 🟡 Token works, zone pending | Will swap from Tavily in 1 line at booth |
| Actionbook browser actions | 🟡 Adapter ready | Activates on `ACTIONBOOK_API_KEY` |
| Qwen future cascade slot | 🟡 Cascade-ready sponsor slot | Activates on `QWEN_API_KEY`; Gemini remains current active LLM |
| Z.ai GLM fallback | 🟡 Adapter ready | Activates on `ZAI_API_KEY` |
| Evermind cross-user memory | 🟡 Local mirror | Activates on `EVERMIND_API_KEY` |
| Butterbase product backend | 🟡 Local mirror | Activates on `BUTTERBASE_API_KEY` |

**Our integrity rule:** we don't fake LLM responses or scrape results. If a key isn't set,
the adapter falls back to a labeled fixture — the demo always works, and nothing on
screen lies to the user.

---

## 🛠 Sponsor stack — every tool load-bearing

| Layer | Tool | Why we chose it |
|---|---|---|
| **Orchestration** | [AgentField](https://agentfield.ai) | Nested execution traces — judges see the *actual* swarm waterfall live |
| **Browser actions** | [Actionbook](https://actionbook.dev) | Drive real Etsy/Castiron sessions, not screenshots |
| **Web scraping** | [Bright Data](https://brightdata.com) | Bypass anti-bot for genuine state-law `.gov` pages |
| **Live SERP (today)** | [Tavily](https://tavily.com) | Free, instant — proves the law-citation flow now |
| **Memory** | [Evermind](https://evermind.ai) | Cross-user pattern surfacing, not single-session |
| **Product backend** | [Butterbase](https://butterbase.ai) | Hosts the actual published launch pages |
| **LLM (today)** | [Gemini 2.5 Flash](https://ai.google.dev) | Free + fast + reliable JSON mode |
| **LLM (future cascade slot)** | [Qwen Cloud](https://qwencloud.com) | Cascade-ready sponsor slot when key lands |
| **LLM (fallback)** | [Z.ai GLM-4 Plus](https://docs.z.ai) | Final cascade tier |
| **LLM routing** | [TokenRouter](https://tokenrouter.com) | Smart cost-per-token routing |
| **Deployment** | [Zeabur](https://zeabur.com) | Promo code `BUILDER0516` — one-click stack deploy |

Deployment stays on the existing `zbpack.toml`: build the Vite frontend, install the FastAPI backend, and start `uvicorn`.

---

## 📂 Repo layout

```
momsaheli/
├── AGENTS.md                        # 👈 READ FIRST if you're an AI agent
├── README.md                        # this file
├── .env.example                     # template — copy to .env
├── scripts/
│   ├── setup.sh                     # one-command fresh-laptop setup
│   └── start.sh                     # boots all 4 processes; Ctrl+C kills all
├── docs/
│   ├── ARCHITECTURE.md              # the agent diagram + sponsor mapping
│   ├── NORTH_STAR.md                # mission + what we say NO to
│   ├── DEMO_SCRIPT.md               # 90-second stage pitch
│   └── legacy/                      # pre-build docs (tagged stale)
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI app + SSE streaming
│       ├── agentfield_agent.py      # 6 @reasoner endpoints + nested orchestrator
│       ├── settings.py              # Pydantic-settings, all env
│       ├── schemas/                 # Pydantic models
│       ├── adapters/                # one per external service
│       │   ├── llm_cascade.py       #   Gemini → Qwen → Z.ai
│       │   ├── tavily.py            #   live web search
│       │   ├── bright_data.py       #   3-tier fallback
│       │   ├── actionbook.py
│       │   ├── evermind.py
│       │   ├── butterbase.py
│       │   └── token_router.py
│       ├── agents/                  # the 6 agents
│       ├── orchestrator/            # SwarmRunner + SSE emits
│       ├── fixtures/                # personas (jenny, jessica) + cached scrapes
│       └── templates/launch_page.html
└── frontend/
    └── src/
        ├── pages/                   # Home, Run, LaunchPage, History
        ├── components/              # Timeline, EvidenceCard, ComplianceBlock, LaunchPacketView, …
        ├── hooks/useAgentStream.ts  # SSE consumer
        ├── index.css                # design system (surface, btn-*, pill-*, eyebrow, …)
        └── tailwind.config.js       # ink + brand palettes, display type scale, custom shadows
```

---

## 🎨 Design system

Warm-editorial visual language built for the working-mom story but rigorous enough for an engineering demo:

- **Type:** Fraunces (variable-axis serif display) + Inter (body) + JetBrains Mono (data/IDs)
- **Palette:** warm amber accent (`brand-50 → brand-950`) on a deep ink neutral (`ink-50 → ink-950`), cream canvas (`#fdf8f0`)
- **Status colors:** semantic only — `success` (#15803d), `warn` (#b45309), `danger` (#b91c1c)
- **Surfaces:** `surface` / `surface-lift` / `surface-console` — layered shadows, never flat
- **The BLOCK moment** gets its own courtroom-grade treatment: red glow ring + accent rail + cited-law card in serif italic. This is the demo's shock beat.

All tokens live in [`frontend/tailwind.config.js`](./frontend/tailwind.config.js) +
[`frontend/src/index.css`](./frontend/src/index.css). Change once, propagates everywhere.

---

## 🚦 Demo safety

Built on the assumption that **everything will break on stage**:

- **Graceful key fallback** — every adapter degrades to a labeled fixture if its key is missing.
- **AgentField crash isolation** — runs in a separate process (`:8001`); if it dies, FastAPI + SSE + demo button all keep working.
- **Preflight** — `agentfield_agent` self-skips with a clear log line if `AGENTFIELD_API_KEY` is empty or `:8080` is down. `start.sh` notices and reports.
- **Portable `start.sh`** — auto-detects `npm` across homebrew / nvm / system / `/tmp/node-*`. No hardcoded paths.
- **Single `Ctrl+C`** kills all 4 processes cleanly.

---

## 📜 License

MIT. Built with love for every mom doing the math at 11pm.

🐶 — Avi (the puppy) & Avinash (the human)
