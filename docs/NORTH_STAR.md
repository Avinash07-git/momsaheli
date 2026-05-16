# 🎯 NORTH STAR — Mom's Saheli @ Agent Forge AI Hackathon

> **The reference doc we open whenever we're digressing.** If a decision can't be justified against this sheet, it's the wrong decision.
>
> Idea is LOCKED (see `PLAN_LOCKED.md`). This file is now: **scoring rubric · kill rules · winner patterns · pre-build allowance · day-of timeline · digression checklist**.

**Event:** Agent Forge AI Hackathon · AI Builders + Beta Fund + Llama Ventures · San Francisco
**Format:** 1 day, solo allowed · ~5 hrs build on-site (10:45 AM → 4:30 PM submit)
**Prize:** $1,000 cash + partner credits
**Mission:** WIN. Hackathon #4 — track record: 1 won, 1 lost, 1 shipped pending.
**Field size:** ~300 attendees — most crowded event we've entered.

---

## 🧭 THE NORTH STAR (memorize)

> **"Painful real workflow + live changing data + agentic action loop + visible demo + one-day buildability + sponsor-native stack."**

If a decision doesn't score 10/10 on every word above → it's the wrong decision.

**The line judges should think in the first 90 seconds:**
> *"Damn, people actually do this manually today, and this agent clearly saves them money, risk, or pain."*

---

## ✅ HARD REQUIREMENTS (non-negotiable)

1. **Deployed live** on Zeabur by 4:30 PM submission.
2. **Uses the partner stack genuinely** — not cosmetically.
3. **Agent does ≥3 of:** gather live data · compare against rule/goal · maintain state · take/prepare action · produce audit trail.
4. **Product hits ≥4 of these 10:** live web intel · browser actions · async/background · memory/state · multi-step reasoning · evidence collection · real user action · audit trail · escalation logic · live deployment.
5. **One shock moment** where judges think *"oh, that's not just a chatbot."*

---

## 🛠 THE STACK (locked)

| Tool | Role | How we use it |
|---|---|---|
| **AgentField** | Multi-agent orchestration + observability | Swarm timeline visible to judges |
| **Actionbook** | Browser actions on real websites | Fills + publishes Mom's Saheli launch page |
| **Bright Data** | Live web scraping | Market comps + live state-law page scrape |
| **Evermind** | Long-term memory OS | Persists Jenny + Jessica trajectories + cross-user pattern |
| **Zeabur** | Live deployment | Submission URL itself + hosted launch pages |
| **Qwen Cloud** | Primary reasoning | Every agent call |
| **Z.ai** | Fallback model | Quota/error cascade |
| **TokenRouter** | Cascade routing | Behind the scenes |
| **Nosana** | ❌ SKIP | No custom GPU need |

**Rule:** every sponsor logo we claim must show up in the demo for ≥3 seconds. Pointable or not claimed.

---

## ❌ KILL RULES (any one = the feature/idea dies)

Reject any idea/feature that:
- Is basically a chatbot
- Depends on private/unavailable data
- Needs too many integrations
- Can't show live evidence
- Takes >30 seconds to explain
- Has no clear before/after demo
- Is a common ChatGPT-generated idea (2-prompts-away test)
- Uses agent tooling cosmetically
- Is morally important but practically un-demoable
- Could be solved by ONE ChatGPT prompt

---

## 🏆 SCORING RUBRIC (out of 100 — score every feature decision)

| Weight | Criterion | What it actually means |
|---|---|---|
| 20 | Real pain | Someone does this manually today, hates it |
| 20 | Agent necessity | Live data + tools + state + actions are TRULY needed |
| 15 | Demo magic | Judges get it in 90 sec, no slide explanation |
| 15 | Buildability | Ships in one day (with pre-build) |
| 10 | Differentiation | Won't be 1 of 10 teams pitching the same thing |
| 10 | Sponsor-stack fit | Partner tools native, not bolted on |
| 10 | Unfair advantage | Avinash's domain/insight makes this sharper |

**<8/10 on either 20-weighter = cut the feature.**

---

## 🏆 PAST WINNERS — TRAITS WE'RE SHAPE-CLONING

| Winner | Event | Shape we steal |
|---|---|---|
| **AegisAgent** (AWS 2nd) | Insurance claims swarm | Evidence + policy + compliance + debate + decision packet w/ citations |
| **EcoLafaek** (AWS 1st) | Waste reports | Citizen signal → classification → geospatial → autonomous action |
| **Nomi** (AWS/NVIDIA grand prize) | Senior care | Live sensors → risk → AI summary → caregiver alert → dashboard |
| **SmartNourish** (AI Tinkerers Seattle) | Prediabetes | Continuous CGM → multimodal → human-in-loop → Instacart action → behavior change |

### The 7 traits ALL winners share — Mom's Saheli must hit ≥5

1. ✅ Multi-agent swarm with named roles that DEBATE *(Market Scout vs Reality & Compliance)*
2. ✅ Live continuous signal source *(Bright Data scrapes)*
3. ✅ Workflow REPLACEMENT not assistance *(Mom's Saheli IS the launch team)*
4. ✅ Concrete intervention not alerts *(live published launch page URL)*
5. 🟡 Multi-stakeholder coordination *(user ↔ market ↔ regulator — light)*
6. ✅ Visible reasoning / debate on screen *(AgentField timeline)*
7. ✅ Tangible final artifact *(2 clickable launch page URLs)*

**Current score: 6/7. Same as AegisAgent.**

### SmartNourish 7-layer bar — Mom's Saheli must hit ≥5

| Layer | Mom's Saheli |
|---|---|
| 1. Continuous signal | ✅ Bright Data per run |
| 2. Multimodal | 🟡 Text + structured (no voice in MVP) |
| 3. Real agent reasoning | ✅ Yes |
| 4. Human-in-loop | ✅ User approves launch packet before publish |
| 5. Real action taken | ✅ Live page published |
| 6. Behavior change | ✅ 90-day roadmap + memory across runs |
| 7. Generative UI | ✅ Output screens adapt to persona |

**Current score: 6/7.**

---

## 🟢 PATTERNS THAT WIN (carry-forward from Hacks #1–#3)

1. Real, named persona in the pitch (Jenny / Jessica)
2. CSV/zero-friction onboarding (preset buttons in our case)
3. Pre-computed AI context — feed LLM insights, not raw rows → zero hallucination
4. AI fallback cascade (Qwen → Z.ai) — demo never breaks on quota
5. Read + draft only, never auto-act on user's behalf without approval — engineer judges sniff lies
6. ONE magic moment, not six
7. Clone the SHAPE of a proven winner (we're cloning AegisAgent shape)
8. Lead with a defensible number, not fake TAM
9. **Submit by NOON, not 4:30**
10. Live agent reasoning visible on screen (AG-UI style)

---

## 🔴 ANTI-PATTERNS (do NOT repeat)

1. ❌ Picking a topic in a crowded category
2. ❌ Using the mandatory tool exactly as designed
3. ❌ Optimistic-render UIs that show empty state first → looks broken on stage
4. ❌ Live-running a long pipeline in a 3-min demo → pitch the OUTCOME
5. ❌ B2B / dev-tooling / engineer-facing
6. ❌ Lifecycle / 3-phase products — ONE thing well, always
7. ❌ Planning around a teammate — solo scope or bust
8. ❌ Defending an idea when Avinash pushes back — level up, don't defend
9. ❌ Walmart blue/spark colors — public hackathon, public design
10. ❌ Ideas that need private data we can't show on stage
11. ❌ **Hardcoding states / cohorts as defensive hedge** — let sponsor tools work live

---

## 🧱 OUR 3-PHASE PROCESS (where we are: ✅ Phase 1 done · ⏭ Phase 2 next)

### **Phase 1 — DECIDE** ✅ COMPLETE
1. ✅ Idea: Mom's Saheli (see `PLAN_LOCKED.md`)
2. ✅ Tools: locked sponsor stack (above)
3. ✅ Architecture: ONE diagram in `ARCHITECTURE.md`

### **Phase 2 — DESIGN** ⏭ NEXT SESSION
- Sketch the ≤4 screens of the demo
- Write the 90-second `DEMO_SCRIPT.md` second-by-second
- Cap component list — 10 max
- Write `SPEC.md` (single source of truth for build)

### **Phase 3 — BUILD** (T-1 to event day)
- **Wave A — Skeleton:** one agent boots · one Actionbook flow · one Bright Data fetch · Zeabur hello-world
- **Wave B — Magic:** ONE shock moment end-to-end with mock data
- **Wave C — Real:** real data + polish + submit by NOON
- Smoke test at every wave boundary. Update `SESSION_HANDOFF.md` at every wave end.

---

## 📅 PRE-BUILD ALLOWANCE (what we CAN do before event day)

The brief permits pre-existing code with disclosure. Use aggressively.

**Pre-event build (before May 16):**
- All scaffolding (FastAPI + React + AgentField setup + Zeabur project)
- API keys obtained + tested for every sponsor tool
- Demo dataset + Jenny + Jessica fixture JSONs
- Schemas + agent definitions
- Full UI shell with mock data
- Smoke test scripts

**Built ON event day (disclose honestly in SUBMISSION.md):**
- Integration glue between agents
- Live data wire-up (real Bright Data calls)
- Real "shock moment" run-through
- Demo video + pitch polish

(Mirror Anchor's honest disclosure pattern.)

---

## ⏰ DAY-OF TIMELINE (Event Day)

| Time | What we do |
|---|---|
| 10:00 AM | Check in. Network. Confirm credits/keys. |
| 10:30 AM | Hackathon intro — listen for hidden judging hints |
| 10:45 AM | Tech workshops — only if stuck on a sponsor tool |
| 11:30 AM | Skip team formation (solo). Open laptop. Pull pre-built repo. |
| 12:30 PM | Lunch — eat fast. Final integration push. |
| 2:00 PM | All features green. Smoke test. |
| 3:00 PM | Polish + record backup demo video. |
| **4:00 PM** | **SUBMIT** (30 min before deadline — never miss). |
| 4:30 PM | Live demos start. Already submitted. Last-mile pitch rehearsal. |
| 5:30 PM | Winners. We're in the running. |

---

## 🚨 "ARE WE DIGRESSING?" CHECKLIST

Before any decision (feature add, tool swap, design change) ask:

- [ ] Serves the **NORTH STAR sentence** at top of this doc?
- [ ] Improves the **ONE shock moment**?
- [ ] Scores ≥7 on **every Scoring Rubric row**?
- [ ] Leaves us **deployed live by 4:00 PM**?
- [ ] Still **solo-scopeable**?

**4+ ✅ → proceed.** **<4 ✅ → drop it.**

---

🐶 — Avi
