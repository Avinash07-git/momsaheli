> ⚠️ **LEGACY DOC — written before the build.** Implementation has drifted.
> The canonical state lives in [`../../AGENTS.md`](../../AGENTS.md).
> Kept here for design-intent reference only.

# 🔒 PLAN_LOCKED — Mom's Saheli

> **THIS IS THE FROZEN PLAN. Read this first, then ARCHITECTURE.md. Everything else is history.**
>
> Locked: May 15 2026, evening. Pre-event freeze. Folder cleaned of all brainstorm history.

---

## 🎯 The Lock (one sentence)

> **Mom's Saheli turns a working mom's real skills + real constraints into a live-market-validated, compliance-checked, launch-ready income experiment — and publishes the actual launch page on stage.**

## 🏆 Trophy sentence (the line we want judges repeating)

> *"A working mom isn't short on effort. She's short on **margin**. Mom's Saheli helps her choose and launch the highest-realistic-net-income path using live market data, real constraint math, and first-step actions."*

**Backup line for emotional hook:**
> *"She is already working. The math still doesn't work."*

---

## 📊 IMPACT & PAIN POINT (cited — this is NOT gimmick)

> **Use these numbers in the pitch. Every one has a source. No inflation. No "70M women" hand-waving.**

### The affected population is large enough to take seriously
- **~7.3 million single mothers** in the U.S. as of 2023 *(Center for American Progress)*
- **~16 million children under 18** live with their mother only *(CAP)*
- This is not a niche persona — it is roughly the population of New Jersey.

### They are already working — the income still doesn't work
- **~75% of single mothers are working**, most full-time *(CAP)*
- Median income, full-time single mother: **$40,000/yr**
- Compare: single father $57K · married mother $60K · married father $76K *(CAP)*
- **Kills the "why don't they just work harder?" objection cold.**

### Childcare math makes "go earn more" structurally hard
- Average child care cost would consume **35% of a single parent's median income** *(Child Care Aware)*
- Formal child care averages **$13,128 per child per year** *(Bipartisan Policy Center)*
- **28% child care gap** — 4.19M kids with need but no licensed slot available *(BPC)*
- Macro cost of the child care crisis: **$216B–$329B in potential GDP loss** *(BPC)*

### Mental load is real (use carefully, don't lead with sadness)
- **32% of single mothers** experience moderate-to-severe psychological distress · vs 19% of married mothers *(Brookings)*
- Severe distress: **7% single moms vs 2% married moms** *(Brookings)*
- → Justifies why the workflow MUST be simple, action-oriented, no friction. **Not** therapy framing.

### Women ARE starting businesses — picking the right one is the wedge
- **49% of new U.S. businesses in 2024 were started by women**, up 69% from 2019 *(Gusto)*
- **1 in 10 women** started a new business in 2024 *(GEM 2024/2025)*
- Women are **47% more likely than men to close a business for family or personal reasons** *(GEM)*
- → The starting isn't the problem. **Picking a viable path under real constraints is.** That is Mom's Saheli's exact wedge.

### Gig income already helps people survive — but it's unstable
- **31% of gig workers** say without that income they'd struggle to make ends meet *(Federal Reserve)*
- Gig workers are more financially strained; many want **consistent pay over highest gross pay** *(Fed)*
- → Mom's Saheli's framing: *"Don't chase the highest-looking gross. Choose the best **net** path that fits time + care + safety + platform constraints."*

### Honest scenario math (use as illustration, NOT promise)
- If Mom's Saheli helps Jenny earn **$300/mo net** → $3,600/yr → ~**9% income lift** on the $40K single-mom median
- If Mom's Saheli helps her reach **$600/mo net** → $7,200/yr → ~**18% income lift**
- Real household-level impact. No billion-dollar fake TAM math.

**🎯 The frame to repeat to judges:**
> *"This isn't motivation. ~75% of single moms are already working full-time. Their median income is $40K. Childcare alone can eat 35% of that. Random gig work is unstable. Mom's Saheli is the agent swarm that picks the best **net-income path** under their real constraints and ships the launch."*

---

## 👥 THE TWO PERSONAS (same engine, different outputs — proves nothing is hardcoded)

### Persona 1 — Jenny (Local-Service / Food path)
| Field | Value |
|---|---|
| Day job | Daycare aide, already working full-time |
| Income gap | **$600/month** (~18% lift on the $40K single-mom median) |
| Time available | **5 hrs/week** |
| Skills | Home cooking, meal prep |
| Budget | $80 startup |
| Hard constraints | No daily delivery · no night shifts (childcare) · no commercial kitchen |

**One-line intro for pitch:** *"Jenny's a daycare aide. Needs $600 more this month. 5 hours a week. Loves cooking."*

### Persona 2 — Jessica (Digital / Async path)
| Field | Value |
|---|---|
| Day job | Customer service rep, work-from-home, already working full-time |
| Income gap | $400/month (~9% lift on the $40K median) |
| Time available | 3 hrs/week |
| Skills | Meal planning, Canva, kids lunch ideas |
| Budget | $20 startup |
| Hard constraints | No phone calls · no delivery · no inventory · fully async |

**One-line intro for pitch:** *"Jessica's a customer service rep. Needs $400 more. 3 hours a week. Wants something fully digital."*

**Why these two:** functional contrast that proves the engine isn't hardcoded. Jenny = local + physical. Jessica = digital + async. Same 5 agents, completely different output. AegisAgent-shape proof.

**Rule:** Neither name is from Avinash's real family. Both names instantly readable. Zero decoding cost in 90 seconds.

---

## 🤖 THE 5 AGENTS (cut from 6/8 → judges can track in 90 sec)

| # | Agent | What it does | Sponsor it pulls | Replaces |
|---|---|---|---|---|
| 1 | **Profile Agent** | Intake form (text MVP, voice if time). Normalizes skills, constraints, location, budget, hours, income gap into a structured profile. | Qwen (structured output) | Business coach intake |
| 2 | **Market Scout** | Live Bright Data scrapes: Etsy bestsellers + sold comps, Poshmark sold prices, Outschool class demand, local Craigslist/Nextdoor rate scans. Returns 6–10 income options ranked by gross + speed-to-first-dollar. | **Bright Data** | Market analyst |
| 3 | **Reality & Compliance Agent** | TWO checks: (a) constraint math — does the option fit her hours/budget/no-delivery/childcare rules? (b) live legal scrape — for her state + activity, fetches the actual cottage-food / permit / licensing page via Bright Data and cites it. Blocks options live, on screen. | **Bright Data** + Qwen | Small biz attorney + ops consultant |
| 4 | **Launch Agent** | Takes the winning option. Generates the full launch packet (offer, price, copy, outreach drafts, 7-day plan). Then **Actionbook fills and publishes a Mom's Saheli-hosted launch page** — real URL appears on screen. | **Actionbook** + **Zeabur** | Marketing freelancer + launch ops |
| 5 | **Memory Agent** | Saves both personas' trajectories (chosen + rejected). Surfaces ONE cross-user learned pattern out loud: *"Low-hours + no-delivery → digital validation path wins."* This is the "state over time" beat. | **Evermind** | Ongoing mentor / case file |

**Orchestration:** AgentField (visible swarm timeline + audit trail on screen).
**Models:** Qwen Cloud primary → Z.ai fallback → TokenRouter routing.
**Skipping:** Nosana (no custom GPU need).

**Hold-position note:** an earlier draft proposed splitting Reality + Risk + Pricing into separate agents (7 total). Held at 5 on logical grounds: 90-sec demo can't track 7 named agents; Reality + Compliance share input + output shape, so merging is cohesion not violation of SOLID; Pricing is one Qwen call inside Market Scout, not a standalone role.

---

## 💥 THE 90-SECOND DEMO ARC (rehearse to the second)

| Time | What happens on screen |
|---|---|
| 0:00–0:12 | Hook (cited): *"7.3 million single moms in the US. 75% already work full-time. Median income $40K. Childcare alone eats 35% of that. They're not short on effort — they're short on **margin**. Mom's Saheli is the agent swarm that fixes the margin."* |
| 0:12–0:18 | Click **"Run Jenny"** preset. Profile appears: daycare aide, $600 gap, 5 hr/wk, no nights. |
| 0:18–0:28 | **Agent swarm timeline** lights up. Market Scout returns 8 options. Top 3 visible: daily tiffin (high gross), weekend meal-pack preorder, kids party catering. |
| 0:28–0:48 | **SHOCK MOMENT.** Reality & Compliance Agent fires live Bright Data scrape against CA Dept of Public Health cottage-food page. Returns on-screen citation: *"California Health & Safety Code §114365 — daily prepared hot food requires Class B permit, $200 fee, 45-day commercial kitchen inspection. Daily prep also violates her 5 hr/wk constraint. **BLOCKED.**"* Market Scout pivots: **Weekend Family Meal Pack Preorder** — $50/pack × 12 packs/mo ≈ $600/mo. Fits Class A cottage food (no permit). Fits 5 hr/wk. (Scenario math, not promise.) |
| 0:48–0:58 | Launch Agent publishes Jenny's Mom's Saheli-hosted launch page. **Real URL appears on screen.** Offer + price + outreach drafts visible. |
| 0:58–1:04 | Click **"Run Jessica"** preset. |
| 1:04–1:20 | Same 5 agents, completely different output. Market Scout returns digital options. Reality Agent rejects physical Etsy crafts (violates no-delivery). Lands on **Printable Lunchbox Kit + Etsy listing draft**. Second Mom's Saheli page publishes. |
| 1:20–1:30 | **Memory beat (Evermind).** Cross-user pattern surfaces: *"Both Jenny and Jessica had no-delivery constraints. Mom's Saheli now defaults to validating digital paths first for any new user with no-delivery + low-hours."* Close: *"Mom's Saheli doesn't give ideas. It runs live market intelligence, blocks the impossible under real laws and real constraints, ships the actual launch, and learns from every run. A $600/month net path is a ~18% income lift on the single-mom median. That's real."* |

**ONE shock moment.** Compliance Agent killing tiffin with a real cited law. Everything else supports it.

---

## 🛠 SPONSOR STACK (every tool load-bearing — pointable in demo)

| Tool | Exact role | When judges see it |
|---|---|---|
| **AgentField** | Multi-agent orchestration + visible swarm timeline UI | 0:18 onward (timeline lights up) |
| **Bright Data** | (a) market comp scrapes; (b) live state-law scrape for compliance | 0:20 (market), 0:28 (compliance) |
| **Actionbook** | Fills + publishes Mom's Saheli-hosted launch page (our own form, 100% reliable) | 0:48 + 1:15 |
| **Evermind** | Persists both personas, surfaces cross-user learned pattern | 1:20 |
| **Zeabur** | Live deployment URL — both the app AND the launch pages | The submission URL itself |
| **Qwen Cloud** | Primary reasoning + structured output | Every agent call |
| **Z.ai** | Fallback model in cascade | Quota / error fallback |
| **TokenRouter** | Routes between Qwen / Z.ai | Behind the scenes |
| **Nosana** | ❌ Skip | — |

**Rule:** if a sponsor logo isn't pointable to ≥3 sec of demo, we don't claim it.

---

## 🗣 LANGUAGE DISCIPLINE — WHAT WE WILL **NEVER** SAY (pitch hygiene)

| ❌ NEVER SAY | ✅ SAY INSTEAD |
|---|---|
| "70M+ working women earning under $30K" | "7.3M single moms, 75% already working full-time, $40K median (CAP)" |
| "Guaranteed $500–$2,000/month" | "Scenario: $600/mo net = ~18% lift on the single-mom median" |
| "Replaces your compliance attorney" | "Cites the actual state regulation live, on screen" |
| "Publishes directly to Etsy / Outschool" | "Publishes a Mom's Saheli-hosted page. Etsy listing is approval-ready draft." |
| "AI business coach for moms" | "Agent swarm for constraint-aware income decisions" |
| "Women are underconfident" | "The launch infrastructure is broken. Mom's Saheli is that infrastructure." |
| "Solves poverty" | "Closes the margin gap. ~9–18% household income lift in scenario." |
| "Side-hustle helper" | "Economic mobility infrastructure" |

**Operating rule:** if you catch yourself saying any of the left-column phrases in the pitch, stop and restart the sentence.

---

## 🚫 WHAT WE EXPLICITLY CUT (and why)

| Cut | Reason |
|---|---|
| "Replaces $1,500 attorney / coach stack" framing | Legally vulnerable. Engineer-judge will pick at it. |
| Pretending to publish on real Etsy / Outschool seller portals | #1 demo-fail risk. Bot protection, login walls, account bans. Self-hosted Mom's Saheli page is honest AND 100% reliable. |
| Hand-curated 3-state law DB | Lazy defensive hedge. Bright Data scrapes the state page live every run. System is 50-state by default. |
| 8 agents (Profile + Market + Risk + Reality + Pricing + Portfolio + Launch + Memory) | Judges can't track 8 in 90 sec. Merged: Risk+Reality → one agent. Pricing absorbed into Market Scout. Portfolio cut (lifecycle antipattern). |
| "3-lane fast-cash / repeatable / scalable portfolio" output | NORTH_STAR antipattern #6: lifecycle creep. One winning launch beats three half-launches. |
| Voice input in MVP | Nice-to-have. Text intake ships. Voice if time after smoke test. |
| Real-family names (Sushma etc.) | Operating rule. Done. |
| Saturday Craft Club / Pinterest-mom framing | Killed during brainstorm — toy framing, lost industrial gravity. |
| Inflated income claims ($95K type numbers, "70M women") | Operating rule. Replaced with CAP/Brookings/Fed-cited numbers. |

---

## ✅ WIN-TRAIT SCORECARD (need ≥5 of 7)

| Trait | Hit? | How |
|---|---|---|
| Multi-agent swarm with named roles that DEBATE | ✅ | Market Scout vs Reality & Compliance live on screen |
| Live continuous signal source | ✅ | Bright Data scrapes every run, fresh each time |
| Workflow REPLACEMENT not assistance | ✅ | Mom's Saheli IS the launch team |
| Concrete intervention not alerts | ✅ | Live published Mom's Saheli page URL |
| Multi-stakeholder coordination | 🟡 | User ↔ market ↔ regulator (light) |
| Visible reasoning / debate on screen | ✅ | AgentField swarm timeline |
| Tangible final artifact | ✅ | Two clickable launch page URLs |

**6 of 7. Same score as AegisAgent (the AWS 2nd-place winner we're SHAPE-cloning).**

SmartNourish 7-layer: 6/7 (skipping voice in MVP).

---

## ⚠️ HONEST RISKS + MITIGATIONS (no sugarcoating)

| Risk | Severity | Mitigation |
|---|---|---|
| Bright Data scrape fails live on a state law page | HIGH | Cache the CA scrape results from rehearsal day. If live call fails, serve cached. (Honest disclosure in SUBMISSION.md.) |
| Actionbook publish fails | MEDIUM | Mom's Saheli page is OUR form on OUR Zeabur deploy → we control the failure surface entirely. Backup: plain FastAPI POST if Actionbook misbehaves. |
| 90 sec is tight for two personas | MEDIUM | Jenny 48s, Jessica 22s, memory beat 10s, hook 12s. Rehearse 10+ times. |
| Judge asks "does it work in Wyoming?" | LOW | Honest answer: "system is state-agnostic via live scrape; we rehearsed CA. Type in Wyoming, watch it run." |
| Judge asks "isn't this just GPT + Etsy?" | MEDIUM | Counter: *"GPT gives ideas. We pull live market comps, cite real state laws, run net-income math against childcare and time constraints, ship the actual launch page, and learn across users. Show me the GPT prompt that does that."* |
| Judge asks "how do you compete with medical / insurance / supply-chain?" | HIGH | We don't compete on life-or-death stakes. We win on: (1) **demo honesty** — public data + public regulations, no fake portals; (2) **memorability** — "already working, math still doesn't work" sticks; (3) **real agent debate** — Market vs Reality live with cited evidence; (4) **sponsor-stack fit** — every tool load-bearing and pointable. |
| Pitch slides into "sad mom" territory | MEDIUM | Brookings distress data justifies why workflow is simple — but lead with **economics** and **agency**, not sadness. "She's running the numbers. We give her better numbers faster." |
| "Saheli" name not understood by SF judges | RESOLVED | Renamed to **Mom's Saheli**. Instantly readable. Zero decoding cost. |
| Solo 5-hour build | MEDIUM | Aggressive pre-build (see Phase 3 plan). Wave A/B/C structure. |

---

## 🧱 BUILD PLAN OVERVIEW (Phase 3 — for reference, not committed yet)

**Pre-event (before May 16):**
- FastAPI + React scaffolding, Zeabur deploy live with hello-world
- AgentField swarm skeleton (5 agent stubs returning fixtures)
- Bright Data adapter + 1 real test scrape (Etsy comp + CA cottage food page)
- Actionbook adapter + Mom's Saheli page template
- Evermind adapter
- LLM cascade (Qwen primary → Z.ai fallback) wired
- Jenny + Jessica fixture JSONs
- Full UI shell with mock data flowing end-to-end
- Demo script v1 rehearsed

**Event day:**
- Wave A: wire real Bright Data on Market Scout
- Wave B: wire real compliance scrape on Reality Agent
- Wave C: wire real Actionbook publish + Evermind persistence
- Polish + record backup video + submit by NOON

**Honest disclosure in SUBMISSION.md:** all scaffolding pre-built, integrations + live data wire-up done event-day. (Mirrors Anchor pattern.)

---

## 📋 PHASE 1 SIGN-OFF CHECKLIST (need Avinash green-light to move to SPEC.md)

- [x] **Idea locked:** Mom's Saheli
- [x] **Personas locked:** Jenny + Jessica (simple, judge-readable, contrast-driven)
- [x] **Agents locked:** 5 (Profile / Market Scout / Reality & Compliance / Launch / Memory)
- [x] **Sponsor stack locked:** AgentField + Bright Data + Actionbook + Evermind + Zeabur + Qwen→Z.ai cascade
- [x] **Shock moment locked:** Reality Agent blocks tiffin with live-scraped CA law
- [x] **Publish target locked:** Mom's Saheli-hosted launch page (NOT real Etsy/Outschool)
- [x] **Demo arc locked:** 90 sec, two personas, one shock, one memory beat
- [x] **Impact & pain point locked:** Cited sources (CAP / Brookings / Child Care Aware / BPC / Fed / Gusto / GEM)
- [x] **Language discipline locked:** NEVER-SAY list active
- [x] **ARCHITECTURE.md** drawn
- [ ] **Avinash final sign-off** → unlocks Phase 2 (SPEC.md)

---

## 🐶 OPERATING NOTES (Avi to self — don't repeat past failures)

- Plain English. Lead with answer. Devil's advocate baked in.
- **Hold positions on logical grounds.** Don't flip under social pressure.
- No real-family names. No inflated stats. No "perfect idea" pretending.
- Mom-themed + money outcome = non-negotiable.
- Avinash directs, Avi codes. End every reply with "what's the call?"
- **Don't hardcode states / regions / cohorts as a defensive hedge.** If a sponsor tool can do it live, let it do it live.
- **Every claim needs a citable source or it doesn't go in the pitch.**

---

## 📝 CHANGE LOG — v1.1 (May 16 2026, pre-event)

Authorized by Avinash after critical re-evaluation against the updated event description. NOT a re-debate of locks; these are deliberate version bumps.

### Adopted
- **Upgrade 1 — Actionbook drives a real Etsy browser session live in the demo.** Was: cosmetic form-fill on our own page. Now: opens etsy.com mid-demo, runs a search for the persona's category, extracts top sold listings + prices, streams the results into Market Scout's evidence cards. This is the visible "this is using the real internet" moment. Bright Data still does the heavy bulk scrapes (Poshmark, Craigslist) + the compliance scrape; Actionbook does the *visible* browser action on a site judges know.
- **Upgrade 3 — Pitch reframe.** Top-line is now "agent-native economic mobility infrastructure for the underbanked workforce" — moms today, expand to gig workers / immigrants / returning citizens / caregivers tomorrow. Same product, venture-scale framing for SF VC judges.
- **Butterbase added** ($20 credit, code `FUN0516`). Real load-bearing role: product backend for the user-facing app — stores run histories, persists each Profile + run record, hosts the published launch pages with light auth so each mom can return to her data. NOT cosmetic — provably in the repo with a sanity script.

### Deferred (stretch goal — ship only after smoke test)
- **Upgrade 2 — live judge-input 3rd persona.** Back-burner. Adds risk to a tight 90-sec arc. Revisit if Wave C finishes early.

### Updated trophy sentence (NEW)
> *"~7 million single moms in America are already working full-time. Their median income is $40K. Childcare alone eats 35% of that. They're not short on effort — they're short on margin. Mom's Saheli is the agent-native economic mobility layer: live market intel, live regulatory scrape, live launch, cross-user learning. Today: moms. Tomorrow: every constrained earner."*

### Sponsor stack v1.1 — 9 load-bearing tools
| # | Tool | Role |
|---|---|---|
| 1 | **AgentField** | Multi-agent orchestration + visible swarm timeline |
| 2 | **Bright Data** | Bulk market comps (Poshmark/Craigslist) + live state-law scrape for compliance |
| 3 | **Actionbook** | Live Etsy browser session on stage + publishes launch page |
| 4 | **Evermind** | Cross-user memory + learned pattern surfacing |
| 5 | **Butterbase** | Product backend — run history DB + launch page hosting + auth |
| 6 | **Zeabur** | App deploy + demo URL |
| 7 | **Qwen Cloud** | Primary reasoning LLM |
| 8 | **Z.ai** (GLM-5.1) | Long-horizon reasoning fallback |
| 9 | **TokenRouter** | LLM routing + caching between Qwen ↔ Z.ai |

Skip: Nosana (no custom GPU need). Qoder is a builder-side IDE, not part of the product.

### No-faking pact (locked from v1.1 forward)
1. Every claimed sponsor has a real API call in the repo. Env-var named. Request path grep-able.
2. No mock client unless `USE_FIXTURES=true` (offline dev only). Real keys = real calls by default.
3. `backend/scripts/sanity_<sponsor>.py` exists for every claimed sponsor — runnable, prints real API response.
4. If a sponsor doesn't fit or doesn't work, we DROP it from the claim list. We do not fake.
5. `SUBMISSION.md` lists every claimed sponsor with the exact `file:line` of its real API call.

### Hard deadline
Their submission cutoff is **4:30 PM**. Our internal target stays **NOON** (4hr safety buffer for live demo polish + backup video).

---

🐶 — Avi
