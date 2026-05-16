import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import clsx from 'clsx';

/* ─── Data ─────────────────────────────────────────────────────────────── */

const STATS = [
  { number: '7.3M',  label: 'single moms in America',                  source: 'CAP' },
  { number: '75%',   label: 'already working — most full-time',         source: 'CAP' },
  { number: '$40K',  label: 'median income, working single mom',        source: 'CAP' },
  { number: '35%',   label: 'eaten by childcare before anything else',  source: 'Child Care Aware' },
];

/* Agent colors: muted, desaturated — like Linear's step palette */
const AGENTS = [
  { n: 1, name: 'Profile',              color: '#64748b', desc: 'Skills, hours, budget, hard constraints — normalized in seconds.' },
  { n: 2, name: 'Market Scout',         color: '#3b82f6', desc: 'Live Etsy + Bright Data: 6–10 ranked income paths, real evidence.' },
  { n: 3, name: 'Reality & Compliance', color: '#ef4444', desc: 'Blocks illegal paths with the actual cited state statute.' },
  { n: 4, name: 'Launch',               color: '#10b981', desc: 'Offer + copy + 7-day plan + a real published landing page.' },
  { n: 5, name: 'Memory',               color: '#8b5cf6', desc: 'Persists trajectory, surfaces a cross-user pattern for the next mom.' },
];

const PRESETS = [
  {
    id: 'jenny',
    emoji: '👩🏽‍🍳',
    name: 'Jenny',
    role: 'Daycare aide · California',
    chips: ['$600/mo gap', '5 hrs/wk', 'Loves cooking'],
    arc: 'Tiffin delivery ranks #1 — then gets BLOCKED by CA cottage-food law. Pivots to a legal winner.',
  },
  {
    id: 'jessica',
    emoji: '💻',
    name: 'Jessica',
    role: 'Customer-service rep · Texas',
    chips: ['$400/mo gap', '3 hrs/wk', 'Digital only'],
    arc: 'Digital-only world — Etsy printable lunchbox kit wins clean, zero compliance hits.',
  },
];

/* ─── Main ──────────────────────────────────────────────────────────────── */

export default function Home() {
  return (
    <div className="bg-white">

      {/* ══════════════════════════════════════════
          HERO — near-black, white type, one blue accent
          ══════════════════════════════════════════ */}
      <section className="relative bg-[#09090b] overflow-hidden">
        {/* Subtle blue glow top-right — not gold, just a cool haze */}
        <div className="absolute top-0 right-0 w-[700px] h-[500px] opacity-[0.07] blur-3xl pointer-events-none rounded-full"
          style={{ background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)' }} />

        <div className="relative max-w-7xl mx-auto px-6 pt-24 pb-28 lg:pt-32 lg:pb-36">
          <div className="grid lg:grid-cols-2 gap-16 items-center">

            {/* Left: headline */}
            <div>
              {/* Event badge */}
              <div className="inline-flex items-center gap-2 mb-8 px-3.5 py-1.5 rounded-full border border-white/10 bg-white/[0.04]">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span className="text-[12px] font-medium text-white/50 tracking-wide">
                  Agent Forge AI Hackathon · SF · May 16, 2026
                </span>
              </div>

              <h1 className="font-serif text-[50px] lg:text-[64px] font-bold leading-[1.06] tracking-tight text-white mb-6">
                The friend every<br />
                working mom can<br />
                <span className="text-white/90 italic">finally</span> afford.
              </h1>

              <p className="text-[16px] text-white/50 leading-relaxed mb-10 max-w-md">
                A consultant costs $2,000. Mom's Saheli is the AI agent swarm that does it all —
                live market intel, cited legal checks, and a real published launch page.
              </p>

              <div className="flex flex-wrap gap-3 mb-10">
                <a href="#run"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white text-[#09090b] font-semibold text-[14px] hover:bg-white/90 transition-colors shadow-lg">
                  Run the swarm →
                </a>
                <a href="#how"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-white/10 text-white/60 font-medium text-[14px] hover:bg-white/[0.05] hover:text-white/80 transition-colors">
                  How it works
                </a>
              </div>

              <div className="flex flex-wrap gap-2">
                {['5 AI agents', '9 sponsor tools', 'Cited regulations', 'Real launch pages'].map((f) => (
                  <span key={f} className="px-3 py-1 rounded-full text-[11px] font-medium text-white/30 border border-white/[0.08]">
                    {f}
                  </span>
                ))}
              </div>
            </div>

            {/* Right: product preview card — dark glass */}
            <div className="relative">
              <div className="rounded-2xl border border-white/[0.08] bg-white/[0.03] overflow-hidden">
                {/* Card header */}
                <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/[0.06]">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-[12px] font-medium text-white/50">live agent run · jenny</span>
                  </div>
                  <span className="text-[11px] font-mono text-white/20">run_a93f1c…</span>
                </div>
                {/* Agent rows */}
                <div className="px-5 py-5 space-y-3.5">
                  {[
                    { agent: 'Profile Agent',         status: 'done',    label: 'normalized · 5 hr/wk · CA',   dot: '#10b981' },
                    { agent: 'Market Scout',           status: 'done',    label: '6 income paths ranked',        dot: '#10b981' },
                    { agent: 'Reality & Compliance',   status: 'block',   label: '3 BLOCKs · CA H&S §114365',  dot: '#ef4444' },
                    { agent: 'Launch Agent',           status: 'running', label: 'generating offer + page…',    dot: '#6366f1' },
                    { agent: 'Memory Agent',           status: 'idle',    label: 'awaiting trajectory',         dot: '#3f3f46' },
                  ].map((row) => (
                    <div key={row.agent} className="flex items-center gap-3">
                      <span className="w-1.5 h-1.5 rounded-full shrink-0"
                        style={{ background: row.dot }} />
                      <span className="text-[13px] font-medium text-white/70 w-44 shrink-0">{row.agent}</span>
                      <span className="text-[12px] text-white/30 truncate">{row.label}</span>
                    </div>
                  ))}
                </div>
                {/* Footer */}
                <div className="px-5 py-3 border-t border-white/[0.06] flex items-center justify-between">
                  <span className="text-[11px] text-white/20">via AgentField</span>
                  <span className="text-[11px] font-mono text-white/30">22.3s elapsed</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          STATS — dark bg, white numbers, clean
          ══════════════════════════════════════════ */}
      <section className="bg-[#0f0f11] border-t border-white/[0.06] py-16">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-white/20 mb-10 text-center">
            The problem, by the numbers — every figure cited
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 divide-x divide-white/[0.06]">
            {STATS.map((s) => (
              <div key={s.label} className="px-8 first:pl-0 last:pr-0 py-2">
                <div className="font-serif text-[48px] lg:text-[56px] font-bold leading-none text-white tabular-nums mb-2">
                  {s.number}
                </div>
                <div className="text-[13px] text-white/40 leading-snug mb-3">{s.label}</div>
                <div className="text-[10px] font-semibold uppercase tracking-[0.14em] text-white/20">{s.source}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          HOW IT WORKS — white, clean, spacious
          ══════════════════════════════════════════ */}
      <section id="how" className="bg-white py-28 lg:py-36">
        <div className="max-w-7xl mx-auto px-6">

          <div className="max-w-xl mb-20">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#a1a1aa] mb-4">How it works</p>
            <h2 className="font-serif text-[40px] lg:text-[50px] font-bold text-[#09090b] leading-tight tracking-tight mb-5">
              Five agents.<br />One mom.<br />One published page.
            </h2>
            <p className="text-[15px] text-[#71717a] leading-relaxed">
              Each agent does one job. Together they replace the consultant, the lawyer, the marketer, and the bookkeeper.
            </p>
          </div>

          {/* Connecting line + steps */}
          <div className="relative">
            <div className="hidden lg:block absolute top-7 left-7 right-7 h-px bg-[#e4e4e7]" />
            <div className="grid lg:grid-cols-5 gap-8 lg:gap-4">
              {AGENTS.map((a) => (
                <div key={a.n} className="relative">
                  <div
                    className="relative z-10 w-14 h-14 rounded-2xl flex items-center justify-center font-serif text-[22px] font-bold text-white mb-5 shadow-sm"
                    style={{ background: a.color }}
                  >
                    {a.n}
                  </div>
                  <div className="font-semibold text-[14px] text-[#18181b] mb-1.5">{a.name}</div>
                  <div className="text-[13px] text-[#71717a] leading-relaxed">{a.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          RUN THE SWARM — off-white bg
          ══════════════════════════════════════════ */}
      <section id="run" className="bg-[#fafafa] border-t border-[#f4f4f5] py-28 lg:py-36">
        <div className="max-w-7xl mx-auto px-6">

          <div className="text-center max-w-xl mx-auto mb-16">
            <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#a1a1aa] mb-4">Try it live</p>
            <h2 className="font-serif text-[40px] lg:text-[50px] font-bold text-[#09090b] leading-tight tracking-tight mb-5">
              Run the swarm.
            </h2>
            <p className="text-[15px] text-[#71717a] leading-relaxed">
              Two real moms. Same five agents. Completely different output. Nothing is hardcoded —
              it's the law, the constraints, and the math doing the work.
            </p>
          </div>

          <PersonaCards />
        </div>
      </section>

      {/* ══════════════════════════════════════════
          SPONSOR BAR — white, minimal
          ══════════════════════════════════════════ */}
      <section className="bg-white border-t border-[#f4f4f5] py-14">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-[#a1a1aa] mb-8">
            Built on the Agent Forge sponsor stack — every tool load-bearing
          </p>
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-3">
            {['AgentField', 'Bright Data', 'Actionbook', 'Evermind', 'Butterbase', 'Qwen', 'Z.ai', 'TokenRouter', 'Zeabur'].map((s) => (
              <span key={s} className="text-[13px] font-medium text-[#a1a1aa] hover:text-[#18181b] transition-colors cursor-default">
                {s}
              </span>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
}

/* ─── Persona cards ─────────────────────────────────────────────────────── */

function PersonaCards() {
  const navigate = useNavigate();
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function go(personaId: string) {
    if (busy) return;
    setBusy(personaId);
    setError(null);
    try {
      const profileRes = await fetch(`/api/fixtures/${personaId}`);
      if (!profileRes.ok) throw new Error(`fixture ${personaId} not found`);
      const profile = await profileRes.json();
      const runRes = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile }),
      });
      const { run_id } = await runRes.json();
      navigate(`/run/${run_id}?persona=${personaId}`);
    } catch (e: any) {
      setError(`Could not start run: ${e?.message ?? e}`);
      setBusy(null);
    }
  }

  return (
    <div>
      <div className="grid md:grid-cols-2 gap-5 max-w-4xl mx-auto">
        {PRESETS.map((p) => {
          const isBusy = busy === p.id;
          return (
            <button
              key={p.id}
              disabled={!!busy}
              onClick={() => go(p.id)}
              className={clsx(
                'text-left rounded-2xl border bg-white transition-all duration-200 overflow-hidden group',
                isBusy
                  ? 'border-[#6366f1] shadow-lg'
                  : 'border-[#e4e4e7] hover:border-[#a1a1aa] hover:shadow-md',
                busy && busy !== p.id ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer',
              )}
            >
              {/* Top accent bar — subtle gray, not colorful */}
              <div className="h-px w-full bg-[#e4e4e7] group-hover:bg-[#6366f1] transition-colors" />

              <div className="p-8">
                {/* Avatar + name */}
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 rounded-2xl bg-[#f4f4f5] flex items-center justify-center text-2xl shrink-0">
                      {p.emoji}
                    </div>
                    <div>
                      <div className="font-serif text-[22px] font-bold text-[#09090b] leading-tight">
                        {isBusy ? (
                          <span className="inline-flex items-center gap-2 text-[#6366f1]">
                            <Spinner /> Starting…
                          </span>
                        ) : p.name}
                      </div>
                      <div className="text-[12px] text-[#71717a] font-medium mt-0.5">{p.role}</div>
                    </div>
                  </div>
                  <div className={clsx(
                    'w-8 h-8 rounded-full border flex items-center justify-center text-[13px] shrink-0 transition-all mt-1',
                    'border-[#e4e4e7] text-[#a1a1aa]',
                    'group-hover:border-[#09090b] group-hover:bg-[#09090b] group-hover:text-white',
                  )}>
                    →
                  </div>
                </div>

                {/* Chips */}
                <div className="flex flex-wrap gap-2 mb-5">
                  {p.chips.map((c) => (
                    <span key={c} className="px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-[#f4f4f5] text-[#52525b]">
                      {c}
                    </span>
                  ))}
                </div>

                {/* Story arc */}
                <div className="border-t border-[#f4f4f5] pt-5">
                  <div className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#a1a1aa] mb-2">Story arc</div>
                  <p className="text-[13px] text-[#52525b] leading-relaxed">{p.arc}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {error && (
        <p className="mt-5 text-[13px] text-red-700 bg-red-50 border border-red-200 rounded-xl p-4 max-w-4xl mx-auto">
          {error}
        </p>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
