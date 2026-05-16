# 🎬 DEMO_SCRIPT — Mom's Saheli (90 seconds)

> Second-by-second pitch. Bracketed lines = what Avinash says out loud. Italic = what's on screen. Bold = the moment that earns the trophy.
>
> Rehearse 10+ times. Time the rehearsals. Cut anything that pushes past 95 seconds.

---

## 🎯 The trophy sentence (memorize, open with this)

> **"~7 million single moms in America are already working full-time. Their median income is $40K. Childcare alone eats 35% of that. They're not short on effort — they're short on margin. Mom's Saheli is the agent-native economic mobility layer."**

## 🏁 The closing line (memorize, end with this)

> **"Today: moms. Tomorrow: every constrained earner. Mom's Saheli is the infrastructure."**

---

## ⏱ SECOND-BY-SECOND ARC

| Time | On screen | Avinash says (verbatim or paraphrase) |
|---|---|---|
| **0:00–0:12** | *Title card: "Mom's Saheli — the friend she can't afford." Cited stats fade in: 7.3M · 75% · $40K · 35%.* | **"~7 million single moms in America. 75% already work full-time. Median income $40K. Childcare alone eats 35%. They're not short on effort — they're short on margin. Mom's Saheli is the agent-native economic mobility layer."** |
| **0:12–0:18** | *Click "Run Jenny" preset. Profile card appears: daycare aide · $600/mo gap · 5 hr/wk · no nights · loves cooking.* | "Meet Jenny. Daycare aide. Already full-time. Needs $600 more a month. 5 hours a week. Loves cooking." |
| **0:18–0:32** | ***Agent swarm timeline lights up (AgentField).*** *Market Scout fires. **A live Etsy browser tab opens in a side panel — URL bar visible, real etsy.com — searches "weekend family meal pack," top sold listings stream in as Evidence Cards.** Bright Data cards stream in parallel from Poshmark + Craigslist. 8 ranked options appear.* | "The Market Scout agent is live — Actionbook is driving a real Etsy browser session right now, Bright Data is pulling Poshmark and Craigslist comps. 8 options ranked by realistic net income. Top three: daily tiffin, weekend meal pack, kids party catering." |
| **0:32–0:50** | ***SHOCK MOMENT.*** *Reality & Compliance Agent fires. **A second browser frame opens — Bright Data hits the California Department of Public Health cottage food page live.** The card flips red: **"BLOCKED — California Health & Safety Code §114365: daily prepared hot food requires Class B permit, $200 fee, 45-day commercial kitchen inspection. Also violates the 5 hr/wk constraint."** Citation link clickable.* | **"Watch this. The Reality & Compliance Agent just scraped California's actual cottage food law live. Daily tiffin is BLOCKED — not because we hardcoded it, because the regulation is real and so are her hours. Market Scout pivots."** |
| **0:50–1:00** | *Winner card highlights: **Weekend Family Meal Pack Preorder — $50/pack × 12/mo ≈ $600/mo. Fits Class A cottage food (no permit). Fits 5 hr/wk.** Launch Agent fires. Actionbook fills the publish form. Butterbase URL pops up: `momssaheli.app/launch/jenny-meal-pack`. Offer copy + 7-day plan visible.* | "Launch Agent generates the offer, copy, price, outreach drafts, and a 7-day plan. Actionbook publishes the page to Butterbase. **Real URL. Live. Right now.**" |
| **1:00–1:06** | *Click "Run Jessica" preset.* | "Same five agents. Completely different mom — Jessica, customer service, 3 hours, no delivery, fully async." |
| **1:06–1:20** | *Swarm fires again. Evidence cards stream from Etsy (this time "kids lunch printable") + Poshmark. Reality Agent rejects physical Etsy crafts (no-delivery violation). Lands on **Printable Lunchbox Kit + Etsy listing draft**. Second Butterbase launch page publishes: `momssaheli.app/launch/jessica-lunchbox-kit`.* | "Engine isn't hardcoded. Same agents, different constraints, different winner. Printable digital product. Second launch page published." |
| **1:20–1:30** | ***Memory beat.*** *Evermind panel surfaces: **"Cross-user pattern detected: low-hours + no-delivery → digital-first validation wins. Defaulting future runs."** Side-by-side: Jenny's page + Jessica's page + the cross-user pattern card.* | "And the Memory Agent surfaces a real cross-user pattern from Evermind. **Today: moms. Tomorrow: every constrained earner. Mom's Saheli is the infrastructure.**" |

**Total: 90 seconds. Rehearsal budget: ≤95s. If you go over, cut the Jessica intro narration, not the shock moment.**

---

## 🎤 OPENING (first 12 seconds is everything)

**Do this:**
- Start with the trophy sentence at conversational pace. No "hey everyone" warmup.
- Stand up. One hand on the laptop trackpad, ready to click.
- Look at the judges, not the screen, during the stats.

**Don't do this:**
- ❌ "Hi I'm Avinash and today I want to talk about…"
- ❌ Apologize for being solo / first / nervous.
- ❌ Open with the persona name (no one cares about Jenny yet — they care about the *number*).

---

## 🔥 THE SHOCK MOMENT (0:32–0:50) — protect this with your life

This is the ONE beat the trophy depends on. Three things must work:

1. **The browser frame for the Bright Data law-page scrape must be visibly opening live.** Pre-warmed but not pre-clicked.
2. **The BLOCK card must say "California Health & Safety Code §114365"** — verbatim, link clickable.
3. **The pivot to the surviving option must happen within 4 seconds of the BLOCK.** No dead air.

**Fallback (only if live scrape fails):** the cached-scrape fallback kicks in transparently — the card still shows the citation. You say: *"This is running against a cached snapshot of the CA page from this morning — same outcome, the system is state-agnostic via live scrape in production."* Honest disclosure.

---

## 🎬 LAUNCH PAGE REVEAL (0:50–1:00 + 1:14–1:20)

When the URL pops up, **say the URL out loud**. Judges who didn't catch the visual catch the audio. *"momssaheli.app/launch/jenny-meal-pack — live, right now."*

If a judge has a phone out, that URL gets typed. That's the closest a hackathon comes to a viral demo moment.

---

## 🧠 MEMORY BEAT (1:20–1:30)

The weakest beat in our demo (we already know this from the SWOT). Three rules to keep it from looking like a hardcoded heuristic:

1. **Phrase it as a query, not a result.** Avinash says: *"The Memory Agent queries Evermind across both runs and surfaces…"* — emphasizes the query is happening live, not pre-baked.
2. **Show the Evermind API call latency on screen** if possible (even just a "querying…" → "→ pattern found" 200ms blink).
3. **Frame it forward, not backward.** Not "we learned" → "future Mom's Saheli users with the same constraint shape will skip the wrong recommendations from minute one."

---

## ❓ Q&A PREP (judges will ask 1–3 of these)

| Likely question | One-sentence answer |
|---|---|
| "Isn't this just GPT + Etsy scrape?" | *"GPT gives ideas. We pull live market comps via Actionbook on real Etsy, cite real state regulation via Bright Data, run net-income math against childcare + time constraints, ship the actual launch page via Butterbase, and learn across users via Evermind. Show me the GPT prompt that does that."* |
| "Does it work in Wyoming?" | *"State-agnostic via live Bright Data scrape. We rehearsed CA. Type Wyoming, watch it run."* |
| "How is this venture-scale?" | *"7M moms is the wedge. The pattern — constrained-earner economic mobility — extends to gig workers, immigrants, returning citizens, caregivers. Same agent shape, different vertical regulation graph."* |
| "How do you actually monetize?" | *"B2B2C: state workforce agencies, women's economic empowerment NGOs, financial inclusion fintechs. Per-launched-mom pricing. The agent infrastructure is the product."* |
| "What stops a mom from doing this herself with ChatGPT?" | *"The compliance scrape, the cross-user pattern memory, and the published launch page. ChatGPT will confidently tell her she can sell daily tiffin in California. Reality Agent won't."* |
| "What happens if Bright Data / Actionbook breaks?" | *"Cached-scrape fallback kicks in transparently. We disclose this in SUBMISSION.md. The system is honest about its failure modes — that's the only way you trust an agent with real money decisions."* |

---

## 🚨 OPERATING RULES DURING THE PITCH

1. **Never apologize for skipping a sponsor.** If something doesn't fire on stage, narrate the next thing — don't draw attention to what didn't fire.
2. **Don't read the screen aloud.** Judges can read. Your voice carries the narrative the screen can't.
3. **One pause is OK. Two pauses is a loss.** If you blank, click the next preset — the screen carries you.
4. **End on the closing sentence verbatim.** Don't improvise the last line.

---

## 📦 BACKUP VIDEO (record by 3:00 PM event day)

- 60 sec, no audio, no cuts.
- Captured on the actual Zeabur deploy with real keys.
- Uploaded to a public Loom + linked in `SUBMISSION.md`.
- Purpose: if WiFi/projector/Bright Data dies live, we still have proof.

---

## ✅ DEMO READINESS CHECKLIST (run morning of event)

- [ ] Both presets (Jenny + Jessica) complete a full run end-to-end with real API calls in <25 sec each
- [ ] CA cottage food page scrape returns the §114365 citation
- [ ] Both Butterbase launch pages load on a fresh browser tab (URL shareable)
- [ ] Evermind cross-user pattern query returns a non-empty result after 2 runs
- [ ] Cached-fallback toggle works (kill WiFi, run again, demo still completes)
- [ ] Backup Loom uploaded + URL in `SUBMISSION.md`
- [ ] Pitched to a stranger and rehearsed under 95 seconds, 3 times in a row, without choking

---

🐶 — Avi
