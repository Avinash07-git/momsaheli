# 🌸 Mom's Saheli

> **The friend she can't afford.** An agent-native economic mobility layer for the underbanked workforce — starting with America's 7 million single moms.

Built at **Agent Forge AI Hackathon** · San Francisco · May 16 2026 · solo.

> 🤖 **AI agents continuing this work:** read **[`AGENTS.md`](./AGENTS.md)** first. It's
> the brain transplant — current state, open decisions, and gotchas. Every other doc
> assumes you've read it.

---

## What it does

Click **Run Jenny** (or **Run Jessica**) and watch 5 AI agents collaborate live:

1. **Profile Agent** normalizes her skills, hours, budget, and hard constraints.
2. **Market Scout** pulls evidence cards (Etsy / Castiron / Nextdoor / FB groups) and asks **real Gemini 2.5 Flash** to rank opportunities by realistic net monthly income.
3. **Reality & Compliance Agent** does a **real Tavily web search** of her state's actual cottage-food / permit law and **blocks** anything illegal — with the live `.gov` citation URL on screen.
4. **Launch Agent** has **real Gemini** generate her offer, copy, price, target customer, and 7-day plan, then publishes a real shareable landing page.
5. **Memory Agent** persists her trajectory and surfaces a cross-user learned pattern.

Same engine, two completely different moms, two completely different launches. Proves nothing is hardcoded.

---

## What's real vs. mocked (honest table)

| Capability | Status | How |
|---|---|---|
| LLM reasoning + copy generation | ✅ **LIVE** | Gemini 2.5 Flash, real JSON-mode calls |
| State law web search + citation | ✅ **LIVE** | Tavily free SERP returning real `.gov` URLs |
| FastAPI backend with SSE streaming | ✅ **LIVE** | Every agent step streams to UI in real time |
| Server-rendered launch pages | ✅ **LIVE** | Jinja2 + Tailwind, real shareable URL |
| Local persistence (runs + pages) | ✅ **LIVE** | File-backed mirror of Butterbase |
| Bright Data scraping | 🟡 Token works, **zone pending** | Will swap from Tavily in 1 line tomorrow |
| Qwen primary LLM | 🟡 Cascade slot ready | Activates on `QWEN_API_KEY` |
| Z.ai GLM fallback | 🟡 Adapter ready | Activates on `ZAI_API_KEY` |
| AgentField orchestrator dashboard | 🟡 SDK installed, refactor next | `:8080` control plane wiring pending |
| Actionbook browser actions | 🟡 Adapter + fixtures | Activates on `ACTIONBOOK_API_KEY` |
| Evermind cross-user memory | 🟡 Local mirror | Activates on `EVERMIND_API_KEY` |
| Butterbase product backend | 🟡 Local mirror | Activates on `BUTTERBASE_API_KEY` |

We don't fake LLM responses or scrape results. If a key isn't set, the adapter falls
back to a cached fixture and clearly labels the path — the demo always works, and
nothing on screen lies to the user.

---

## The numbers (cited)

- ~**7.3M single moms** in the U.S. — most working full-time *(Center for American Progress)*
- Median income for a working single mom: **$40K** *(CAP)*
- Average childcare cost: **~35% of a single parent's median income** *(Child Care Aware)*
- Macro GDP loss from the childcare crisis: **$216B–$329B** *(BPC)*

They're not short on effort. They're short on **margin**. Mom's Saheli closes the margin.

---

## Stack

| Layer | Tool | Status |
|---|---|---|
| Orchestration | [AgentField](https://agentfield.ai) | 🟡 SDK installed |
| Browser actions | [Actionbook](https://actionbook.dev) | 🟡 awaits key |
| Web scraping | [Bright Data](https://brightdata.com) | 🟡 awaits zone |
| Live SERP (today) | [Tavily](https://tavily.com) | ✅ LIVE |
| Memory | [Evermind](https://evermind.ai) | 🟡 awaits key |
| Product backend | [Butterbase](https://butterbase.ai) | 🟡 local mirror |
| LLM (today) | [Gemini 2.5 Flash](https://ai.google.dev) | ✅ LIVE |
| LLM (sponsor primary tomorrow) | [Qwen Cloud](https://qwencloud.com) | 🟡 awaits key |
| LLM (fallback) | [Z.ai GLM-4 Plus](https://docs.z.ai) | 🟡 awaits key |
| LLM routing | [TokenRouter](https://tokenrouter.com) | 🟡 awaits key |
| Deployment | [Zeabur](https://zeabur.com) | planned |

---

## Run locally (other-laptop quickstart)

```bash
# 1. Clone
git clone https://github.com/Avinash07-git/momsaheli.git
cd momsaheli

# 2. Set up env
cp .env.example .env
# Open .env, paste GEMINI_API_KEY (https://aistudio.google.com/apikey)
# and TAVILY_API_KEY (https://tavily.com) — both free, 30 sec each.
# Everything else is optional; missing keys gracefully fall back.

# 3. Backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .          # add Walmart --index-url flags if on Walmart network
uvicorn app.main:app --port 8000 &

# 4. Frontend (new terminal)
cd ../frontend
npm install
npm run dev
```

Visit http://localhost:5173 and click **Run Jenny**. ~38 seconds of real LLM work,
real BLOCKs with real citations, real launch page at the end.

---

## Repo layout

```
momsaheli/
├── AGENTS.md                    # 👈 READ FIRST if you're an AI agent
├── README.md                    # this file
├── .env.example                 # template — copy to .env
├── scripts/setup.sh             # one-command fresh-laptop setup
├── docs/                        # design context (see docs/README.md)
│   ├── ARCHITECTURE.md          #   the 5-agent diagram + sponsor mapping
│   ├── NORTH_STAR.md            #   mission + what we say NO to
│   ├── DEMO_SCRIPT.md           #   90-second stage pitch
│   └── legacy/                  #   pre-build docs (tagged stale)
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + SSE streaming
│   │   ├── settings.py          # Pydantic-settings
│   │   ├── schemas/             # Pydantic models (Profile, Opportunity, etc.)
│   │   ├── adapters/            # one per external service
│   │   │   ├── llm_cascade.py   #   Gemini → Qwen → Z.ai
│   │   │   ├── tavily.py        #   live web search
│   │   │   ├── bright_data.py   #   3-tier fallback
│   │   │   ├── actionbook.py
│   │   │   ├── evermind.py
│   │   │   ├── butterbase.py
│   │   │   └── token_router.py
│   │   ├── agents/              # the 5 agents
│   │   ├── orchestrator/        # SwarmRunner + SSE emits
│   │   ├── fixtures/            # personas + cached scrapes
│   │   └── templates/launch_page.html
│   └── pyproject.toml
└── frontend/
    └── src/
        ├── pages/               # Home, Run, LaunchPage, History
        ├── components/          # Timeline, EvidenceCard, ComplianceCheck, etc.
        └── hooks/useAgentStream.ts   # SSE consumer
```

---

## License

MIT. Built with love for every mom doing the math at 11pm.

🐶 — Avi & Avinash
