import { useMemo, useEffect, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import clsx from 'clsx';
import { useAgentStream } from '../hooks/useAgentStream';
import EvidenceCard from '../components/EvidenceCard';
import ComplianceBlock from '../components/ComplianceBlock';
import LaunchPacketView from '../components/LaunchPacketView';
import MemoryPanel from '../components/MemoryPanel';
import type {
  AgentEvent,
  ComplianceCheck,
  CrossUserPattern,
  EvidenceCard as EvidenceCardT,
  LaunchPacket,
  Opportunity,
  Profile,
} from '../types';

/* ─────────────────────────────────────────────────────────────────────────
   Persona styling. Avatar emoji + warm name banner.
   ───────────────────────────────────────────────────────────────────────── */
const PERSONA_META: Record<string, { emoji: string }> = {
  jenny:   { emoji: '👩🏽‍🍳' },
  jessica: { emoji: '💻' },
};

/* ─────────────────────────────────────────────────────────────────────────
   The 5 agents — used for the horizontal stepper at the top.
   ───────────────────────────────────────────────────────────────────────── */
const STEPS = [
  { id: 'profile',            short: 'Profile',     full: 'Profile Agent' },
  { id: 'market_scout',       short: 'Market',      full: 'Market Scout' },
  { id: 'reality_compliance', short: 'Compliance',  full: 'Reality & Compliance' },
  { id: 'launch',             short: 'Launch',      full: 'Launch Agent' },
  { id: 'memory',             short: 'Memory',      full: 'Memory Agent' },
] as const;

type StepStatus = 'idle' | 'running' | 'done' | 'error';

function statusFor(agentId: string, events: AgentEvent[]): StepStatus {
  const mine = events.filter((e) => e.agent === agentId);
  if (mine.some((e) => e.type === 'agent_error')) return 'error';
  if (mine.length === 0) return 'idle';
  const doneMarker: Record<string, string> = {
    profile: 'profile_ready',
    market_scout: 'opportunities_ranked',
    reality_compliance: 'winner_selected',
    launch: 'launch_published',
    memory: 'memory_pattern',
  };
  const marker = doneMarker[agentId];
  if (marker && mine.some((e) => e.type === marker)) return 'done';
  return 'running';
}

/* ───────────────────────────────────────────────────────────────────────── */

export default function Run() {
  const { runId } = useParams<{ runId: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') ?? 'jenny';
  const meta = PERSONA_META[persona] ?? PERSONA_META.jenny;

  const { events, connected, complete, error } = useAgentStream(runId ?? null);

  /* Live elapsed timer */
  const [elapsedMs, setElapsedMs] = useState(0);
  const startEvent = useMemo(() => events.find((e) => e.type === 'run_started'), [events]);
  const completeEvent = useMemo(() => events.find((e) => e.type === 'run_complete'), [events]);

  useEffect(() => {
    if (!startEvent) return;
    const start = new Date(startEvent.timestamp).getTime();
    if (completeEvent) {
      setElapsedMs(new Date(completeEvent.timestamp).getTime() - start);
      return;
    }
    const id = setInterval(() => setElapsedMs(Date.now() - start), 100);
    return () => clearInterval(id);
  }, [startEvent, completeEvent]);

  /* Derived views */
  const profile       = useMemo<Profile | null>(() => events.find((e) => e.type === 'profile_ready')?.data.profile ?? null, [events]);
  const evidenceCards = useMemo<EvidenceCardT[]>(() => events.filter((e) => e.type === 'evidence_card').map((e) => e.data.card), [events]);
  const opportunities = useMemo<Opportunity[]>(() => events.find((e) => e.type === 'opportunities_ranked')?.data.opportunities ?? [], [events]);
  const checks        = useMemo<ComplianceCheck[]>(() => events.filter((e) => e.type === 'compliance_check').map((e) => e.data.check), [events]);
  const launchPacket  = useMemo<LaunchPacket | null>(() => events.find((e) => e.type === 'launch_packet_ready')?.data.packet ?? null, [events]);
  const publishedUrl  = useMemo<string | null>(() => events.find((e) => e.type === 'launch_published')?.data.url ?? null, [events]);
  const pattern       = useMemo<CrossUserPattern | null>(() => events.find((e) => e.type === 'memory_pattern')?.data.pattern ?? null, [events]);

  const winnerOpp = useMemo<Opportunity | null>(() => {
    const passing = checks.find((c) => c.verdict === 'PASS');
    return passing ? opportunities.find((o) => o.id === passing.opportunity_id) ?? null : null;
  }, [checks, opportunities]);

  const blockCount = checks.filter((c) => c.verdict === 'BLOCK').length;
  const passCount  = checks.filter((c) => c.verdict === 'PASS').length;

  return (
    <div className="min-h-screen bg-cream">
      {/* ═══════════════════════════════════════════════════════════════
          HERO — calm, generous, single focus on the persona
          ═══════════════════════════════════════════════════════════════ */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-hero-warm" aria-hidden />
        <div className="relative max-w-5xl mx-auto px-6 md:px-10 pt-10 pb-14">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-sm font-medium text-ink-700 hover:text-ink-900 transition-colors"
          >
            <span aria-hidden>←</span>
            Back to home
          </Link>

          <div className="mt-8 flex flex-col md:flex-row md:items-center gap-7">
            {/* Persona avatar */}
            <div className="grid place-items-center w-24 h-24 md:w-28 md:h-28 rounded-3xl bg-white shadow-lift text-6xl shrink-0">
              {meta.emoji}
            </div>

            {/* Name + meta */}
            <div className="min-w-0 flex-1">
              <div className="text-xs font-semibold uppercase tracking-eyebrow text-brand-700 mb-2">
                {complete ? '✓ Run complete' : connected ? 'Run in progress' : 'Connecting…'}
              </div>
              <h1 className="font-serif text-5xl md:text-6xl font-bold text-ink-950 leading-[1.05] tracking-tight">
                Meet {profile?.display_name ?? persona[0].toUpperCase() + persona.slice(1)}
              </h1>
              {profile && (
                <p className="mt-4 text-lg md:text-xl text-ink-700 leading-relaxed max-w-2xl">
                  {profile.day_job} in {profile.state}.
                  She needs <strong className="text-ink-950 font-semibold">${profile.income_gap_monthly_usd.toLocaleString()}/mo</strong>{' '}
                  more — and has just <strong className="text-ink-950 font-semibold">{profile.hours_per_week_available} hours a week</strong> to find it.
                </p>
              )}
            </div>
          </div>

          {/* Headline stats — quietly typeset, generous spacing */}
          <div className="mt-10 grid grid-cols-2 md:grid-cols-4 gap-x-6 gap-y-5 pt-8 border-t border-ink-200/60">
            <HeroStat label="Elapsed"  value={`${(elapsedMs / 1000).toFixed(1)}s`} mono />
            <HeroStat label="Evidence" value={evidenceCards.length.toString()} />
            <HeroStat label="Blocked"  value={blockCount.toString()} tone={blockCount > 0 ? 'danger' : 'neutral'} />
            <HeroStat label="Passed"   value={passCount.toString()}  tone={passCount > 0 ? 'success' : 'neutral'} />
          </div>
        </div>
      </header>

      {/* ═══════════════════════════════════════════════════════════════
          STEPPER — single horizontal row, always visible, easy to scan
          ═══════════════════════════════════════════════════════════════ */}
      <div className="sticky top-0 z-20 bg-white/95 backdrop-blur-md border-b border-ink-200/70 shadow-soft">
        <div className="max-w-5xl mx-auto px-6 md:px-10 py-4">
          <Stepper events={events} />
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════════
          BODY — single readable column, generous vertical rhythm
          ═══════════════════════════════════════════════════════════════ */}
      <main className="max-w-5xl mx-auto px-6 md:px-10 py-16 md:py-20 space-y-20 md:space-y-24">

        {error && (
          <div className="rounded-2xl bg-red-50 border border-red-200 p-5 text-base text-red-900 flex items-start gap-3">
            <span className="text-xl shrink-0">⚠️</span>
            <div>
              <div className="font-semibold mb-1">Stream error</div>
              <div className="text-sm">{error}</div>
            </div>
          </div>
        )}

        {/* === Constraints === */}
        {profile && (
          <Beat
            eyebrow="What she said"
            title="Her hard constraints"
            lede="Every opportunity must clear ALL of these. We do not negotiate."
          >
            <div className="surface p-7 md:p-8">
              <ul className="flex flex-wrap gap-2.5">
                {profile.hard_constraints.map((c) => (
                  <li key={c} className="pill-lg bg-ink-900 text-cream">
                    {c.split('_').join(' ')}
                  </li>
                ))}
              </ul>
              {profile.skills.length > 0 && (
                <>
                  <div className="text-xs font-semibold uppercase tracking-eyebrow text-ink-500 mt-7 mb-3">
                    Her skills
                  </div>
                  <ul className="flex flex-wrap gap-2.5">
                    {profile.skills.map((s) => (
                      <li key={s} className="pill-lg bg-brand-100 text-brand-900 border border-brand-200">
                        {s}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </div>
          </Beat>
        )}

        {/* === Evidence === */}
        {evidenceCards.length > 0 && (
          <Beat
            eyebrow="Step 1 · Market evidence"
            title="What's actually selling"
            lede="Real listings, pulled live. Each card is one data point Gemini will rank against her constraints."
          >
            <div className="grid sm:grid-cols-2 gap-4">
              {evidenceCards.map((c) => (
                <EvidenceCard key={c.id} card={c} />
              ))}
            </div>
          </Beat>
        )}

        {/* === Compliance — THE drama beat === */}
        {checks.length > 0 && (
          <Beat
            eyebrow="Step 2 · Reality check"
            title={blockCount > 0 ? "Wait — some of these are illegal" : "All paths clear compliance"}
            lede={
              blockCount > 0
                ? `${blockCount} option${blockCount === 1 ? '' : 's'} blocked by real state law (cited below). This is the work an agent does that a friend cannot.`
                : "No legal blocks. The system runs three real compliance dimensions in parallel for every option."
            }
            dramatic={blockCount > 0}
          >
            <div className="space-y-4">
              {checks.map((c) => (
                <ComplianceBlock
                  key={c.opportunity_id}
                  check={c}
                  opportunity={opportunities.find((o) => o.id === c.opportunity_id)}
                />
              ))}
            </div>
          </Beat>
        )}

        {/* === Winner === */}
        {winnerOpp && (
          <Beat
            eyebrow="Step 3 · Recommendation"
            title="Here's what she should actually do"
            lede="Highest realistic monthly income that clears every constraint and every compliance check."
            celebrate
          >
            <WinnerCard opportunity={winnerOpp} />
          </Beat>
        )}

        {/* === Launch packet === */}
        {launchPacket && (
          <Beat
            eyebrow="Step 4 · Launch packet"
            title="Ship-ready, written by Gemini"
            lede="Real published page. Real offer copy. Real 7-day plan she can start tomorrow."
          >
            <LaunchPacketView packet={launchPacket} publishedUrl={publishedUrl} />
          </Beat>
        )}

        {/* === Memory === */}
        {pattern && (
          <Beat
            eyebrow="Step 5 · What we learned"
            title="Cross-user pattern surfaced"
            lede="Each run feeds the swarm's memory. Future moms benefit from this one."
          >
            <MemoryPanel pattern={pattern} />
          </Beat>
        )}

        {/* === Complete === */}
        {complete && <CompleteCard elapsedMs={elapsedMs} />}

        {/* === Empty state === */}
        {!evidenceCards.length && !checks.length && <EarlyState />}
      </main>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Building blocks
   ───────────────────────────────────────────────────────────────────────── */

function HeroStat({
  label, value, tone, mono,
}: { label: string; value: string; tone?: 'success' | 'danger' | 'neutral'; mono?: boolean }) {
  const valueColor =
    tone === 'success' ? 'text-emerald-700' :
    tone === 'danger'  ? 'text-red-700' :
                         'text-ink-950';
  return (
    <div>
      <div className="text-[11px] font-semibold uppercase tracking-eyebrow text-ink-500 mb-1.5">
        {label}
      </div>
      <div className={clsx(
        'text-3xl md:text-4xl font-bold leading-none tabular-nums',
        mono ? 'font-mono' : 'font-serif',
        valueColor,
      )}>
        {value}
      </div>
    </div>
  );
}

function Stepper({ events }: { events: AgentEvent[] }) {
  return (
    <ol className="flex items-center gap-2 overflow-x-auto scrollbar-thin">
      {STEPS.map((step, i) => {
        const s = statusFor(step.id, events);
        return (
          <li key={step.id} className="flex items-center gap-2 shrink-0">
            <div className={clsx(
              'flex items-center gap-2.5 px-3 py-2 rounded-full text-sm font-semibold transition-all',
              s === 'idle'    && 'bg-ink-100 text-ink-500',
              s === 'running' && 'bg-brand-100 text-brand-900 ring-2 ring-brand-300 shadow-glow-brand animate-pulse-soft',
              s === 'done'    && 'bg-emerald-50 text-emerald-800 ring-1 ring-emerald-200',
              s === 'error'   && 'bg-red-100 text-red-800 ring-1 ring-red-300',
            )}>
              <span className={clsx(
                'inline-flex items-center justify-center w-5 h-5 rounded-full text-[11px] font-bold',
                s === 'idle'    && 'bg-ink-200 text-ink-500',
                s === 'running' && 'bg-brand-400 text-white',
                s === 'done'    && 'bg-emerald-500 text-white',
                s === 'error'   && 'bg-red-500 text-white',
              )}>
                {s === 'done' ? '✓' : s === 'error' ? '!' : i + 1}
              </span>
              <span className="whitespace-nowrap hidden sm:inline">{step.full}</span>
              <span className="whitespace-nowrap sm:hidden">{step.short}</span>
            </div>
            {i < STEPS.length - 1 && (
              <span className={clsx(
                'h-px w-4 sm:w-6 transition-colors',
                s === 'done' ? 'bg-emerald-300' : 'bg-ink-200',
              )} />
            )}
          </li>
        );
      })}
    </ol>
  );
}

function Beat({
  eyebrow, title, lede, dramatic, celebrate, children,
}: {
  eyebrow: string;
  title: string;
  lede?: string;
  dramatic?: boolean;
  celebrate?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className="animate-fade-in">
      <div className="mb-7 md:mb-8 max-w-3xl">
        <div className={clsx(
          'text-xs font-semibold uppercase tracking-eyebrow mb-3',
          dramatic ? 'text-red-700' : celebrate ? 'text-emerald-700' : 'text-brand-700',
        )}>
          {eyebrow}
        </div>
        <h2 className={clsx(
          'font-serif font-bold tracking-tight leading-[1.1]',
          dramatic
            ? 'text-3xl md:text-4xl text-red-900'
            : celebrate
              ? 'text-3xl md:text-4xl text-emerald-900'
              : 'text-3xl md:text-4xl text-ink-950',
        )}>
          {title}
        </h2>
        {lede && (
          <p className="mt-4 text-base md:text-lg text-ink-700 leading-relaxed">
            {lede}
          </p>
        )}
      </div>
      {children}
    </section>
  );
}

function WinnerCard({ opportunity }: { opportunity: Opportunity }) {
  return (
    <article className="relative overflow-hidden rounded-3xl border border-emerald-200 bg-white shadow-lift">
      <div className="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r from-emerald-300 via-emerald-500 to-brand-400" />
      <div className="p-7 md:p-10">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-6 mb-6">
          <div className="min-w-0">
            <div className="text-xs font-semibold uppercase tracking-eyebrow text-emerald-700 mb-2">
              The winner
            </div>
            <h3 className="font-serif text-3xl md:text-4xl font-bold text-ink-950 leading-tight tracking-tight">
              {opportunity.title}
            </h3>
          </div>
          <div className="text-right shrink-0">
            <div className="text-xs font-semibold uppercase tracking-eyebrow text-ink-500 mb-1">
              Realistic net
            </div>
            <div className="font-serif text-5xl md:text-6xl font-bold text-emerald-700 leading-none tabular-nums">
              ${opportunity.estimated_net_monthly_usd.toLocaleString()}
            </div>
            <div className="text-sm text-ink-500 mt-1">/ month</div>
          </div>
        </div>

        <p className="text-base md:text-lg text-ink-800 leading-relaxed mb-6">
          {opportunity.rationale}
        </p>

        {opportunity.revenue_citations && opportunity.revenue_citations.length > 0 && (
          <div className="border-t border-ink-100 pt-5">
            <div className="text-xs font-semibold uppercase tracking-eyebrow text-ink-500 mb-3">
              Income data backed by
            </div>
            <ul className="space-y-2">
              {opportunity.revenue_citations.slice(0, 3).map((c, i) => (
                <li key={i}>
                  <a
                    href={c.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-start gap-2 text-sm text-brand-800 hover:text-brand-900 transition-colors"
                  >
                    <span className="text-ink-400 font-mono shrink-0 mt-0.5">{i + 1}.</span>
                    <span className="underline decoration-brand-300 decoration-2 underline-offset-4 hover:decoration-brand-700">
                      {c.title || c.url}
                    </span>
                    <span aria-hidden className="text-ink-400 shrink-0">↗</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}

function CompleteCard({ elapsedMs }: { elapsedMs: number }) {
  return (
    <div className="relative overflow-hidden rounded-3xl border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-cream p-10 md:p-14 text-center animate-bounce-in">
      <div className="grid place-items-center w-16 h-16 rounded-full bg-emerald-500 text-white text-3xl mx-auto mb-5 shadow-lift">
        ✓
      </div>
      <div className="font-serif text-3xl md:text-4xl font-bold text-ink-950 mb-3 tracking-tight">
        She has a plan
      </div>
      <p className="text-base md:text-lg text-ink-700 mb-7 max-w-md mx-auto leading-relaxed">
        Five real agents finished in <strong className="font-mono text-ink-950">{(elapsedMs / 1000).toFixed(1)}s</strong>.
        Real LLM. Real citations. Real published page.
      </p>
      <Link to="/" className="btn-primary text-base">
        Run another mom
        <span aria-hidden>→</span>
      </Link>
    </div>
  );
}

function EarlyState() {
  return (
    <div className="text-center py-16 md:py-24 animate-fade-in">
      <div className="inline-flex items-center gap-3 px-4 py-2.5 rounded-full bg-white border border-ink-200 shadow-soft mb-7">
        <span className="status-dot-live" />
        <span className="text-sm font-semibold text-ink-700">Swarm is warming up</span>
      </div>
      <p className="text-base md:text-lg text-ink-600 max-w-md mx-auto leading-relaxed">
        The agents are talking. First evidence should arrive in a moment.
      </p>
    </div>
  );
}
