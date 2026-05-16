> ⚠️ **LEGACY DOC — written before the build.** Implementation has drifted.
> The canonical state lives in [`../../AGENTS.md`](../../AGENTS.md).
> Kept here for design-intent reference only.

# 🐶 START HERE — Mom's Saheli

> **Read this file end-to-end. Then `PLAN_LOCKED.md` (+ v1.1 changelog at bottom) + `ARCHITECTURE.md` + `SPEC.md` + `DEMO_SCRIPT.md`. 10 minutes and you're fully caught up.**
>
> Last session closed: May 16 2026, pre-event. Phase 1 ✅ DECIDE. Phase 2 ✅ DESIGN. Phase 3 ▶️ BUILD starts next.

---

## 🔒 LOCKED — DO NOT REDEBATE

| Item | Locked value |
|---|---|
| **Product** | **Mom's Saheli** ("Mom's" prefix = SF-judge readable · "Saheli" = cultural anchor + memorability) |
| **Tagline** | *"The friend she can't afford."* |
| **Trophy line** | *"A working mom isn't short on effort. She's short on **margin**. Mom's Saheli helps her choose and launch the highest-realistic-net-income path using live market data, real constraint math, and first-step actions."* |
| **Personas** | **Jenny** (daycare aide, $600/mo gap, 5 hr/wk, cooking) + **Jessica** (CS rep WFH, $400/mo gap, 3 hr/wk, digital) |
| **5 Agents** | Profile · Market Scout · Reality & Compliance · Launch · Memory |
| **Stack** | AgentField + Bright Data + Actionbook + Evermind + Zeabur + Qwen→Z.ai cascade (skip Nosana) |
| **Shock moment** | Reality & Compliance Agent blocks daily tiffin live, citing CA Health & Safety Code §114365 (scraped via Bright Data) |
| **Publish target** | Mom's Saheli-hosted launch page (NOT real Etsy — controlled failure surface) |
| **Impact framing** | Cited (CAP / Brookings / Child Care Aware / BPC / Fed / Gusto / GEM). No "70M women" inflation. |

---

## 📂 The folder

1. **`START_HERE.md`** ← you are here. Orientation + next-session kickoff.
2. **`PLAN_LOCKED.md`** — frozen product strategy (v1.1 changelog at the bottom: live Etsy via Actionbook · infra reframe · Butterbase added · no-faking pact).
3. **`ARCHITECTURE.md`** — diagram + data flow + repo layout + env vars (v1.1).
4. **`SPEC.md`** — the build bible: screens, components, API contract, schemas, fixtures, fallback plan, sponsor proof ledger, build waves.
5. **`DEMO_SCRIPT.md`** — second-by-second 90-sec pitch + presenter cues + Q&A prep + readiness checklist.
6. **`NORTH_STAR.md`** — active reference: scoring rubric, kill rules, winner patterns, day-of timeline, "are we digressing?" checklist.
7. **`Event.rtf`** + **`Important Notes.docx`** — original event briefs. Never edit.
8. **`/Users/a0a0kbv/Documents/Event Latest Info.rtf`** — UPDATED event description (judging criteria, full sponsor list incl. Butterbase, 4:30 PM deadline). Source of truth for event facts.

---

## ⏭ NEXT SESSION — START HERE (Phase 3: BUILD)

**Your first message in next session (paste this verbatim or paraphrase):**

> *"Phase 2 done. SPEC.md and DEMO_SCRIPT.md locked. Ready for Phase 3 Wave A — scaffold the repo, build the UI shell with fixture-driven SSE, deploy to Zeabur. Should I start?"*

### Phase 3 task list (waves from `SPEC.md` §9)

**Wave A — Skeleton (pre-event):**
1. Confirm `momsaheli/` repo location (probably create alongside this folder).
2. `uv venv` + install backend deps from `SPEC.md` §10.
3. Scaffold every file from `ARCHITECTURE.md` repo layout.
4. Build every schema in `backend/schemas/` per `SPEC.md` §4.
5. Stub every adapter to return cached fixture JSON.
6. Wire SSE — fake AgentField runner emits events sequentially.
7. React + Tailwind + Vite scaffold; build 10 components from `SPEC.md` §2.
8. Both presets work end-to-end with fixtures only.
9. Deploy to Zeabur (need `BUILDER0516` code — only valid May 16).

**Wave B — Real shock moment (event-day morning):**
- Bright Data real call for the CA cottage food scrape. Sanity script passes.
- Reality & Compliance Agent renders real citation live.

**Wave C — All sponsors real (event-day, 12:00–3:30 PM):**
- Actionbook (live Etsy + form publish), Qwen/Z.ai/TokenRouter (LLM cascade), Evermind (memory + cross-user query), Butterbase (persistence + page hosting), AgentField (real orchestration).
- All 8 sanity scripts pass.
- SUBMISSION.md filled with the proof ledger from `SPEC.md` §8.

**Polish + Submit (3:30–4:00 PM):**
- Backup Loom recorded.
- 3 consecutive rehearsals under 95s.
- Submit to `tinyurl.com/agentforgesubmit` by 4:00 PM (internal target — actual deadline 4:30).

### API keys Avinash is dropping (request as needed)

From `SPEC.md` §8 and event description sponsor links. Order roughly by Wave: Bright Data → Qwen → Z.ai → TokenRouter → AgentField → Actionbook → Evermind → Butterbase → Zeabur (event-day only).

### What you will NOT do in next session

- ❌ Re-debate the name, personas, agent count, publish target, sponsor stack — all locked (v1.1)
- ❌ Add a 6th agent / 5th screen / 11th component
- ❌ Fake any sponsor integration — every claim has a real API call + sanity script (no-faking pact, `PLAN_LOCKED.md` v1.1)
- ❌ Skip the cached-scrape fallback build — it's the demo-day safety net
- ❌ Add any feature that fails the "Are we digressing?" checklist in `NORTH_STAR.md`

---

## 🚨 OPERATING RULES (Avi to self — learned the hard way; do NOT repeat)

- **Plain English. No jargon.** Lead with the answer.
- **HOLD POSITIONS ON LOGICAL GROUNDS. DO NOT FLIP UNDER SOCIAL PRESSURE.** #1 failure pattern. Engage logical objections. Hold against social ones.
- **No real-family names** in personas. Done — Jenny + Jessica are generic.
- **No inflated stats.** Every claim needs a citable source or it doesn't ship.
- **No "perfect idea" pretending.** Surface trade-offs honestly.
- **Mom-themed + money outcome = non-negotiable.** Mom's Saheli holds both.
- **Devil's advocate baked into every recommendation.**
- **Don't ask Avinash about logistics** (city, URL, registration, judges) — his domain.
- **He directs, you code.** His value-add = judgment, story, pivot decisions.
- **Don't hardcode states / regions / cohorts as defensive hedges.** Live scrape > hand-curated DB.
- **Every reply ends with "what's the call?"** to keep momentum.

---

## 🎯 PHASE STATUS SNAPSHOT

| Phase | Status |
|---|---|
| **Phase 1 — DECIDE** (idea + tools + architecture) | ✅ DONE |
| **Phase 2 — DESIGN** (SPEC.md + DEMO_SCRIPT.md + v1.1 upgrades) | ✅ DONE |
| **Phase 3 — BUILD** (Wave A skeleton → B real-shock → C all-real → ship by noon) | ▶️ NEXT |

### v1.1 upgrades adopted (May 16 pre-event)
- ✅ Actionbook drives live Etsy browser session on stage
- ✅ Pitch reframed as "agent-native economic mobility infrastructure for the underbanked workforce"
- ✅ Butterbase added as 9th sponsor (run history DB + launch page hosting)
- ✅ No-faking pact locked: every sponsor has a real API call + sanity script
- ⏸ Deferred: live judge-input 3rd persona (stretch goal, only if Wave C finishes early)

---

🐶 — Avi
