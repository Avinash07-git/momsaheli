# 🌸 Mom's Saheli

> **The friend she can't afford.** An agent-native economic mobility layer for the underbanked workforce — starting with America's 7 million single moms.

Built at **Agent Forge AI Hackathon** · San Francisco · May 16 2026 · solo.

---

## What it does

Click **Run Jenny** (or **Run Jessica**) and watch 5 AI agents collaborate live:

1. **Profile Agent** normalizes her skills, hours, budget, and hard constraints.
2. **Market Scout** pulls live comps from Etsy, Poshmark, Craigslist (via Bright Data + Actionbook).
3. **Reality & Compliance Agent** scrapes her state's actual permit / cottage-food law and **blocks** anything illegal — with the citation on screen.
4. **Launch Agent** generates her offer, copy, price, outreach drafts, and a 7-day plan, then publishes a real shareable landing page.
5. **Memory Agent** persists her trajectory and surfaces a cross-user learned pattern.

Same engine, two completely different moms, two completely different launches. Proves nothing is hardcoded.

---

## The numbers (cited)

- ~**7.3M single moms** in the U.S. — most working full-time *(Center for American Progress)*
- Median income for a working single mom: **$40K** *(CAP)*
- Average childcare cost: **~35% of a single parent's median income** *(Child Care Aware)*
- Macro GDP loss from the childcare crisis: **$216B–$329B** *(BPC)*

They're not short on effort. They're short on **margin**. Mom's Saheli closes the margin.

---

## Stack

| Layer | Tool |
|---|---|
| Orchestration | [AgentField](https://agentfield.ai) |
| Browser actions | [Actionbook](https://actionbook.dev) |
| Web scraping | [Bright Data](https://brightdata.com) |
| Memory | [Evermind](https://evermind.ai) |
| Product backend | [Butterbase](https://butterbase.ai) |
| LLM (primary) | [Qwen Cloud](https://qwencloud.com) |
| LLM (fallback) | [Z.ai GLM-5.1](https://docs.z.ai) |
| LLM routing | [TokenRouter](https://tokenrouter.com) |
| Deployment | [Zeabur](https://zeabur.com) |

Every sponsor has a real, traceable API call in the repo. See `SUBMISSION.md` for the proof ledger.

---

## Run locally

```bash
# backend
cd backend
uv venv
source .venv/bin/activate
uv pip install -e .
cp ../.env.example ../.env   # then fill keys (or leave empty + USE_FIXTURES=true)
uvicorn app.main:app --reload --port 8000

# frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173 and click **Run Jenny**.

---

## Repo layout

```
momsaheli/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── settings.py
│   │   ├── schemas/             # Pydantic models
│   │   ├── adapters/            # one per sponsor
│   │   ├── agents/              # 5 agents
│   │   ├── orchestrator/        # AgentField runner
│   │   ├── fixtures/            # personas + cached scrapes
│   │   └── templates/launch_page.html
│   └── scripts/                 # sanity_<sponsor>.py per sponsor
├── frontend/
│   └── src/
│       ├── pages/               # Home, Run, LaunchPage, History
│       ├── components/          # 10 components
│       └── hooks/useAgentStream.ts
└── README.md
```

---

## License

MIT. Built with love for every mom doing the math at 11pm.

🐶 — Avi
