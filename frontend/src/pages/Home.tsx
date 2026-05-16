import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import clsx from 'clsx';

/* ─── Data ─────────────────────────────────────────────────────────────── */

const STATS = [
  { number: '7.3M',  label: 'single moms in America',                      source: 'CAP' },
  { number: '75%',   label: 'already working — most full-time',             source: 'CAP' },
  { number: '$40K',  label: 'median income for working single moms',        source: 'CAP' },
  { number: '35%',   label: 'eaten by childcare before anything else',      source: 'Child Care Aware' },
];

const AGENTS = [
  { n: 1, name: 'Profile',              color: '#f59e0b', desc: 'Skills, hours, budget, hard constraints — normalized in seconds.' },
  { n: 2, name: 'Market Scout',         color: '#3b82f6', desc: 'Live Etsy + Bright Data: 6–10 ranked income paths, real evidence.' },
  { n: 3, name: 'Reality & Compliance', color: '#ef4444', desc: 'Blocks illegal paths with the actual cited state statute.' },
  { n: 4, name: 'Launch',               color: '#22c55e', desc: 'Offer + copy + 7-day plan + a real published landing page.' },
  { n: 5, name: 'Memory',               color: '#a855f7', desc: 'Persists trajectory, surfaces a cross-user pattern for the next mom.' },
];

const PRESETS = [
  {
    id: 'jenny',
    emoji: '👩🏽‍🍳',
    name: 'Jenny',
    role: 'Daycare aide · California',
    gap: '$600/mo gap',
    hours: '5 hrs/wk',
    skill: 'Loves cooking',
    arc: 'Tiffin delivery ranks #1 — then gets BLOCKED by CA cottage-food law. Pivots to a legal winner.',
    accentColor: '#f59e0b',
    accentBg: '#fef3c7',
  },
  {
    id: 'jessica',
    emoji: '💻',
    name: 'Jessica',
    role: 'Customer-service rep · Texas',
    gap: '$400/mo gap',
    hours: '3 hrs/wk',
    skill: 'Digital only',
    arc: 'Digital-only world — Etsy printable lunchbox kit wins clean, zero compliance hits.',
    accentColor: '#6366f1',
    accentBg: '#ede9fe',
  },
];

/* ─── Main ──────────────────────────────────────────────────────────────── */

export default function Home() {
  return (
    <div className="bg-white">

      {/* ══════════════════════════════════════════
          HERO — dark, bold, premium
          ══════════════════════════════════════════ */}
      <section className="relative bg-[#0c0a09] overflow-hidden">
        {/* Subtle warm glow top-right */}
        <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full opacity-20 blur-3xl pointer-events-none"
          style={{ background: 'radial-gradient(circle, #f59e0b 0%, transparent 70%)' }} />
        {/* Subtle rose glow bottom-left */}
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full opacity-10 blur-3xl pointer-events-none"
          style={{ background: 'radial-gradient(circle, #fb7185 0%, transparent 70%)' }} />

        <div className="relative max-w-7xl mx-auto px-6 pt-24 pb-28 lg:pt-32 lg:pb-36">
          <div className="grid lg:grid-cols-2 gap-16 items-center">

            {/* Left: headline */}
            <div>
              {/* Live badge */}
              <div className="inline-flex items-center gap-2 mb-8 px-3.5 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-sm">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-[12px] font-semibold text-white/70 tracking-wide">
                  Agent Forge AI Hackathon · SF · May 16, 2026
                </span>
              </div>

              <h1 className="font-serif text-[52px] lg:text-[68px] font-bold leading-[1.05] tracking-tight text-white mb-6">
                The friend every{' '}
                <span className="text-[#f59e0b]">working mom</span>{' '}
                can finally afford.
              </h1>

              <p className="text-[17px] text-white/60 leading-relaxed mb-10 max-w-lg">
                A consultant costs $2,000. Mom's Saheli is the{' '}
                <span className="text-white/90 font-medium">AI agent swarm</span> that does it all —
                live market intel, cited legal checks, and a real published launch page.
              </p>

              <div className="flex flex-wrap gap-3 mb-10">
                <a href="#run" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-[#f59e0b] text-[#0c0a09] font-bold text-[15px] hover:bg-[#fbbf24] transition-colors shadow-lg">
                  Run the swarm
                  <span>→</span>
                </a>
                <a href="#how" className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-white/15 text-white/80 font-semibold text-[15px] hover:bg-white/5 transition-colors">
                  How it works
                </a>
              </div>

              {/* Feature pills */}
              <div className="flex flex-wrap gap-2">
                {['5 AI agents', '9 sponsor tools', 'Cited regulations', 'Real launch pages'].map((f) => (
                  <span key={f} className="px-3 py-1 rounded-full text-[12px] font-medium text-white/50 border border-white/10 bg-white/5">
                    {f}
                  </span>
                ))}
              </div>
            </div>

            {/* Right: product preview card */}
            <div className="relative">
              <div className="absolute -inset-6 rounded-3xl opacity-30 blur-2xl"
                style={{ background: 'radial-gradient(ellipse, #f59e0b 0%, transparent 70%)' }} />
              <div className="relative rounded-2xl border border-white/10 bg-white/5 backdrop-blur-sm overflow-hidden shadow-2xl">
                {/* Card header */}
                <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/10 bg-white/5">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span className="text-[12px] font-semibold text-white/70">live agent run · jenny</span>
                  </div>
                  <span className="text-[11px] font-mono text-white/30">run_a93f1c…</span>
                </div>
                {/* Agent rows */}
                <div className="px-5 py-4 space-y-3">
                  {[
                    { agent: 'Profile Agent',          status: 'done',    label: 'normalized · 5 hr/wk · CA',      color: '#22c55e' },
                    { agent: 'Market Scout',            status: 'done',    label: '6 income paths ranked',          color: '#22c55e' },
                    { agent: 'Reality & Compliance',    status: 'block',   label: '3 BLOCKs · CA H&S §114365',     color: '#ef4444' },
                    { agent: 'Launch Agent',            status: 'running', label: 'generating offer + page…',       color: '#f59e0b' },
                    { agent: 'Memory Agent',            status: 'idle',    label: 'awaiting trajectory',            color: '#52525b' },
                  ].map((row) => (
                    <div key={row.agent} className="flex items-center gap-3">
                      <span className="w-2 h-2 rounded-full shrink-0 shadow-sm"
                        style={{ background: row.color, boxShadow: row.status === 'running' ? `0 0 8px ${row.color}` : undefined }} />
                      <span className="text-[13px] font-semibold text-white/80 w-44 shrink-0">{row.agent}</span>
                      <span className="text-[12px] text-white/40 truncate">{row.label}</span>
                    </div>
                  ))}
                </div>
                {/* Card footer */}
                <div className="px-5 py-3 border-t border-white/10 flex items-center justify-between bg-white/3">
                  <span className="text-[11px] text-white/30">via AgentField</span>
                  <span className="text-[11px] font-mono text-white/50">22.3s elapsed</span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          STATS STRIP — full bleed, warm dark bg
          ══════════════════════════════════════════ */}
      <section className="bg-[#18181b] py-16">
        <div className="max-w-7xl mx-auto px-6">
          <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#71717a] mb-10 text-center">
            The problem, by the numbers — every figure cited
          </p>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-0 divide-x divide-white/10">
            {STATS.map((s) => (
              <div key={s.label} className="px-8 first:pl-0 last:pr-0 py-2">
                <div className="font-serif text-[48px] lg:text-[56px] font-bold leading-none text-[#f59e0b] tabular-nums mb-2">
                  {s.number}
                </div>
                <div className="text-[14px] text-white/70 leading-snug mb-3 font-medium">{s.label}</div>
                <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#52525b]">
                  {s.source}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          HOW IT WORKS — clean white, generous space
          ══════════════════════════════════════════ */}
      <section id="how" className="bg-white py-28 lg:py-36">
        <div className="max-w-7xl mx-auto px-6">

          <div className="max-w-2xl mb-20">
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#a8a29e] mb-4">How it works</p>
            <h2 className="font-serif text-[42px] lg:text-[52px] font-bold text-[#0c0a09] leading-tight tracking-tight mb-5">
              Five agents. One mom.<br />One published page.
            </h2>
            <p className="text-[16px] text-[#78716c] leading-relaxed">
              Each agent does one job. Together they replace the consultant, the lawyer, the marketer, and the bookkeeper.
            </p>
          </div>

          {/* Steps */}
          <div className="relative">
            {/* Connecting line */}
            <div className="hidden lg:block absolute top-8 left-8 right-8 h-px bg-[#e7e5e4]" />

            <div className="grid lg:grid-cols-5 gap-8 lg:gap-4">
              {AGENTS.map((a) => (
                <div key={a.n} className="relative">
                  {/* Number circle */}
                  <div
                    className="relative z-10 w-16 h-16 rounded-2xl flex items-center justify-center font-serif text-[24px] font-bold text-white mb-5 shadow-lg"
                    style={{ background: a.color }}
                  >
                    {a.n}
                  </div>
                  <div className="font-bold text-[15px] text-[#1c1917] mb-2">{a.name}</div>
                  <div className="text-[13px] text-[#78716c] leading-relaxed">{a.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════
          RUN THE SWARM — light gray bg, big CTA
          ══════════════════════════════════════════ */}
      <section id="run" className="bg-[#fafaf9] py-28 lg:py-36 border-t border-[#e7e5e4]">
        <div className="max-w-7xl mx-auto px-6">

          <div className="text-center max-w-2xl mx-auto mb-16">
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#a8a29e] mb-4">Try it now</p>
            <h2 className="font-serif text-[42px] lg:text-[52px] font-bold text-[#0c0a09] leading-tight tracking-tight mb-5">
              Run the swarm.
            </h2>
            <p className="text-[16px] text-[#78716c] leading-relaxed">
              Two real moms. Same five agents. Completely different output.
              Nothing is hardcoded — it's the law, the constraints, and the math doing the work.
            </p>
          </div>

          <PersonaCards />

        </div>
      </section>

      {/* ══════════════════════════════════════════
          TRUST BAR — sponsors
          ══════════════════════════════════════════ */}
      <section className="bg-white border-t border-[#e7e5e4] py-12">
        <div className="max-w-7xl mx-auto px-6 text-center">
          <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-[#a8a29e] mb-8">
            Built on the Agent Forge sponsor stack — every tool load-bearing
          </p>
          <div className="flex flex-wrap justify-center gap-x-10 gap-y-3">
            {[
              'AgentField', 'Bright Data', 'Actionbook', 'Evermind',
              'Butterbase', 'Qwen', 'Z.ai', 'TokenRouter', 'Zeabur',
            ].map((s) => (
              <span key={s} className="text-[13px] font-semibold text-[#a8a29e] hover:text-[#1c1917] transition-colors cursor-default">
                {s}
              </span>
            ))}
          </div>
        </div>
      </section>

    </div>
  );
}

/* ─── Persona cards with run action ─────────────────────────────────────── */

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
      <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
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
                  ? 'border-[#f59e0b] shadow-lg'
                  : 'border-[#e7e5e4] hover:border-[#a8a29e] hover:shadow-lg',
                busy && busy !== p.id ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer',
              )}
            >
              {/* Colored accent top bar */}
              <div className="h-1.5 w-full" style={{ background: p.accentColor }} />

              <div className="p-8">
                {/* Avatar + name row */}
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div
                      className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl shadow-sm shrink-0"
                      style={{ background: p.accentBg }}
                    >
                      {p.emoji}
                    </div>
                    <div>
                      <div className="font-serif text-[22px] font-bold text-[#1c1917] leading-tight">
                        {isBusy ? (
                          <span className="inline-flex items-center gap-2">
                            <Spinner /> Starting…
                          </span>
                        ) : p.name}
                      </div>
                      <div className="text-[12px] text-[#78716c] font-medium mt-0.5">{p.role}</div>
                    </div>
                  </div>

                  {/* Arrow */}
                  <div className={clsx(
                    'w-9 h-9 rounded-full border flex items-center justify-center text-[15px] shrink-0 transition-all',
                    'border-[#e7e5e4] text-[#a8a29e] group-hover:border-[#1c1917] group-hover:text-[#1c1917] group-hover:bg-[#1c1917] group-hover:text-white',
                  )}>
                    →
                  </div>
                </div>

                {/* Chips */}
                <div className="flex flex-wrap gap-2 mb-5">
                  {[p.gap, p.hours, p.skill].map((chip) => (
                    <span
                      key={chip}
                      className="px-3 py-1 rounded-full text-[12px] font-semibold border"
                      style={{ background: p.accentBg, color: p.accentColor, borderColor: `${p.accentColor}30` }}
                    >
                      {chip}
                    </span>
                  ))}
                </div>

                {/* Story arc */}
                <div className="border-t border-[#f5f5f4] pt-5">
                  <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#a8a29e] mb-2">Story arc</div>
                  <p className="text-[13px] text-[#44403c] leading-relaxed">{p.arc}</p>
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {error && (
        <p className="mt-5 text-[14px] text-red-700 bg-red-50 border border-red-200 rounded-xl p-4 max-w-4xl mx-auto">
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
