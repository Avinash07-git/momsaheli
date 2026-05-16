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
   Persona config
   ───────────────────────────────────────────────────────────────────────── */
const PERSONA_META: Record<string, { emoji: string; color: string }> = {
  jenny:   { emoji: '👩🏽‍🍳', color: '#f59e0b' },
  jessica: { emoji: '💻',     color: '#6366f1' },
};

/* ─────────────────────────────────────────────────────────────────────────
   Agent steps — used in sidebar
   ───────────────────────────────────────────────────────────────────────── */
const AGENTS = [
  { id: 'profile',            label: 'Profile Agent',          icon: '👤', doneEvent: 'profile_ready' },
  { id: 'market_scout',       label: 'Market Scout',           icon: '🔍', doneEvent: 'opportunities_ranked' },
  { id: 'reality_compliance', label: 'Reality & Compliance',   icon: '⚖️',  doneEvent: 'winner_selected' },
  { id: 'launch',             label: 'Launch Agent',           icon: '🚀', doneEvent: 'launch_published' },
  { id: 'memory',             label: 'Memory Agent',           icon: '🧠', doneEvent: 'memory_pattern' },
] as const;

type StepStatus = 'idle' | 'running' | 'done' | 'error';

function agentStatus(agentId: string, events: AgentEvent[]): StepStatus {
  const mine = events.filter((e) => e.agent === agentId);
  if (mine.some((e) => e.type === 'agent_error')) return 'error';
  if (mine.length === 0) return 'idle';
  const agent = AGENTS.find((a) => a.id === agentId);
  if (agent && mine.some((e) => e.type === agent.doneEvent)) return 'done';
  return 'running';
}

/* ─────────────────────────────────────────────────────────────────────────
   Tabs
   ───────────────────────────────────────────────────────────────────────── */
type TabId = 'overview' | 'evidence' | 'compliance' | 'launch' | 'memory';

const TABS: { id: TabId; label: string; icon: string }[] = [
  { id: 'overview',    label: 'Overview',    icon: '◈' },
  { id: 'evidence',   label: 'Evidence',    icon: '📊' },
  { id: 'compliance', label: 'Compliance',  icon: '✓' },
  { id: 'launch',     label: 'Launch',      icon: '🚀' },
  { id: 'memory',     label: 'Memory',      icon: '🧠' },
];

/* ─────────────────────────────────────────────────────────────────────────
   Main component
   ───────────────────────────────────────────────────────────────────────── */
export default function Run() {
  const { runId } = useParams<{ runId: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') ?? 'jenny';
  const meta = PERSONA_META[persona] ?? PERSONA_META.jenny;

  const { events, connected, complete, error } = useAgentStream(runId ?? null);

  const [activeTab, setActiveTab] = useState<TabId>('overview');

  /* Elapsed timer — guard against negative values if clocks differ */
  const [elapsedMs, setElapsedMs] = useState(0);
  const startEvent   = useMemo(() => events.find((e) => e.type === 'run_started'),  [events]);
  const completeEvent = useMemo(() => events.find((e) => e.type === 'run_complete'), [events]);

  useEffect(() => {
    if (!startEvent) return;
    const start = new Date(startEvent.timestamp).getTime();
    if (completeEvent) {
      setElapsedMs(Math.max(0, new Date(completeEvent.timestamp).getTime() - start));
      return;
    }
    const id = setInterval(() => setElapsedMs(Math.max(0, Date.now() - start)), 200);
    return () => clearInterval(id);
  }, [startEvent, completeEvent]);

  /* Derived state */
  const profile       = useMemo<Profile | null>(
    () => events.find((e) => e.type === 'profile_ready')?.data.profile ?? null, [events]);
  const evidenceCards = useMemo<EvidenceCardT[]>(
    () => events.filter((e) => e.type === 'evidence_card').map((e) => e.data.card), [events]);
  const opportunities = useMemo<Opportunity[]>(
    () => events.find((e) => e.type === 'opportunities_ranked')?.data.opportunities ?? [], [events]);
  const checks        = useMemo<ComplianceCheck[]>(
    () => events.filter((e) => e.type === 'compliance_check').map((e) => e.data.check), [events]);
  const launchPacket  = useMemo<LaunchPacket | null>(
    () => events.find((e) => e.type === 'launch_packet_ready')?.data.packet ?? null, [events]);
  const publishedUrl  = useMemo<string | null>(
    () => events.find((e) => e.type === 'launch_published')?.data.url ?? null, [events]);
  const pattern       = useMemo<CrossUserPattern | null>(
    () => events.find((e) => e.type === 'memory_pattern')?.data.pattern ?? null, [events]);

  const winnerOpp = useMemo<Opportunity | null>(() => {
    const passing = checks.find((c) => c.verdict === 'PASS');
    return passing ? (opportunities.find((o) => o.id === passing.opportunity_id) ?? null) : null;
  }, [checks, opportunities]);

  const blockCount = checks.filter((c) => c.verdict === 'BLOCK').length;
  const passCount  = checks.filter((c) => c.verdict === 'PASS').length;
  const elapsedSec = (elapsedMs / 1000).toFixed(1);

  const displayName = profile?.display_name ?? (persona[0].toUpperCase() + persona.slice(1));

  /* Auto-advance to tab when new data arrives */
  useEffect(() => {
    if (complete && activeTab === 'overview') return;
    if (launchPacket && activeTab === 'overview') setActiveTab('launch');
  }, [launchPacket, complete]);

  return (
    /* Full-viewport shell: sidebar + content */
    <div className="flex h-screen bg-[#f8f8f7] overflow-hidden">

      {/* ══════════════════════════════════════════
          SIDEBAR — 280px fixed, scrolls independently
          ══════════════════════════════════════════ */}
      <aside className="hidden lg:flex flex-col w-[280px] shrink-0 bg-white border-r border-[#e5e5e3] overflow-y-auto">

        {/* Logo / back link */}
        <div className="px-6 py-5 border-b border-[#e5e5e3]">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-[13px] font-semibold text-[#71717a] hover:text-[#18181b] transition-colors"
          >
            <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M19 12H5M5 12l7-7M5 12l7 7" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Mom's Saheli
          </Link>
        </div>

        {/* Persona card */}
        <div className="px-6 py-6 border-b border-[#e5e5e3]">
          <div
            className="w-14 h-14 rounded-2xl flex items-center justify-center text-3xl mb-4 shadow-sm"
            style={{ background: `${meta.color}18` }}
          >
            {meta.emoji}
          </div>
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#a1a1a0] mb-1">
            {complete ? 'Run complete' : connected ? 'Running now' : 'Connecting…'}
          </div>
          <h1 className="font-serif text-2xl font-bold text-[#18181b] leading-tight mb-2">
            {displayName}
          </h1>
          {profile && (
            <p className="text-[13px] text-[#71717a] leading-relaxed">
              {profile.day_job}<br />{profile.city ? `${profile.city}, ` : ''}{profile.state}
            </p>
          )}
        </div>

        {/* Key numbers */}
        {profile && (
          <div className="px-6 py-5 border-b border-[#e5e5e3] grid grid-cols-2 gap-4">
            <StatCell
              label="Income gap"
              value={`$${profile.income_gap_monthly_usd.toLocaleString()}`}
              sub="/mo"
            />
            <StatCell
              label="Hours free"
              value={`${profile.hours_per_week_available}`}
              sub="/ wk"
            />
            <StatCell
              label="Budget"
              value={`$${profile.budget_startup_usd}`}
              sub="startup"
            />
            <StatCell
              label="Elapsed"
              value={`${elapsedSec}s`}
              mono
            />
          </div>
        )}

        {/* Agent progress */}
        <div className="px-6 py-5 flex-1">
          <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#a1a1a0] mb-4">
            Agent pipeline
          </div>
          <ol className="space-y-1">
            {AGENTS.map((agent, i) => {
              const s = agentStatus(agent.id, events);
              return (
                <li key={agent.id} className="relative">
                  {i < AGENTS.length - 1 && (
                    <span className={clsx(
                      'absolute left-[15px] top-8 w-px h-5',
                      s === 'done' ? 'bg-emerald-300' : 'bg-[#e5e5e3]',
                    )} />
                  )}
                  <div className={clsx(
                    'flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium transition-all',
                    s === 'idle'    && 'text-[#a1a1a0]',
                    s === 'running' && 'bg-amber-50 text-amber-900',
                    s === 'done'    && 'text-[#18181b]',
                    s === 'error'   && 'text-red-700',
                  )}>
                    <span className={clsx(
                      'w-[30px] h-[30px] rounded-full flex items-center justify-center text-[12px] font-bold shrink-0',
                      s === 'idle'    && 'bg-[#f4f4f3] text-[#a1a1a0]',
                      s === 'running' && 'bg-amber-400 text-white animate-pulse',
                      s === 'done'    && 'bg-emerald-500 text-white',
                      s === 'error'   && 'bg-red-500 text-white',
                    )}>
                      {s === 'done' ? '✓' : s === 'error' ? '!' : i + 1}
                    </span>
                    <span>{agent.label}</span>
                    {s === 'running' && (
                      <span className="ml-auto w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse shrink-0" />
                    )}
                  </div>
                </li>
              );
            })}
          </ol>
        </div>

        {/* Winner summary in sidebar (when done) */}
        {winnerOpp && (
          <div className="mx-4 mb-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
            <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-emerald-700 mb-1">
              Winner
            </div>
            <div className="font-serif text-xl font-bold text-emerald-900 leading-tight mb-1">
              ${winnerOpp.estimated_net_monthly_usd.toLocaleString()}
              <span className="text-sm font-sans font-normal text-emerald-700"> /mo</span>
            </div>
            <div className="text-[12px] text-emerald-800 leading-snug">
              {winnerOpp.title}
            </div>
          </div>
        )}
      </aside>

      {/* ══════════════════════════════════════════
          MAIN PANEL — tabs + scrollable content
          ══════════════════════════════════════════ */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">

        {/* Top header bar */}
        <header className="bg-white border-b border-[#e5e5e3] px-6 lg:px-8 py-4 shrink-0">
          <div className="flex items-center justify-between">
            {/* Mobile: back + persona */}
            <div className="flex items-center gap-3 lg:hidden">
              <Link to="/" className="text-[#71717a] hover:text-[#18181b]">
                <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M19 12H5M5 12l7-7M5 12l7 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </Link>
              <span className="font-semibold text-[#18181b]">{displayName}</span>
            </div>
            {/* Desktop: run info */}
            <div className="hidden lg:flex items-center gap-3">
              <span className="text-[13px] text-[#71717a] font-mono">{runId?.slice(0, 8)}…</span>
              {complete ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block" />
                  Complete
                </span>
              ) : connected ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-[11px] font-semibold">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 inline-block animate-pulse" />
                  Running
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#f4f4f3] text-[#71717a] text-[11px] font-semibold">
                  Connecting…
                </span>
              )}
            </div>
            {/* Stats row */}
            <div className="flex items-center gap-6 text-[13px]">
              <span className="hidden sm:block text-[#71717a]">
                <span className="font-semibold text-[#18181b]">{evidenceCards.length}</span> signals
              </span>
              <span className="hidden sm:block text-[#71717a]">
                <span className="font-semibold text-red-600">{blockCount}</span> blocked
              </span>
              <span className="hidden sm:block text-[#71717a]">
                <span className="font-semibold text-emerald-600">{passCount}</span> passed
              </span>
              <span className="font-mono text-[#a1a1a0] text-[12px]">{elapsedSec}s</span>
            </div>
          </div>
        </header>

        {/* Tab bar */}
        <nav className="bg-white border-b border-[#e5e5e3] px-6 lg:px-8 shrink-0">
          <div className="flex gap-0 -mb-px overflow-x-auto scrollbar-thin">
            {TABS.map((tab) => {
              const hasData =
                tab.id === 'overview'    ? true :
                tab.id === 'evidence'    ? evidenceCards.length > 0 :
                tab.id === 'compliance'  ? checks.length > 0 :
                tab.id === 'launch'      ? !!launchPacket :
                tab.id === 'memory'      ? !!pattern :
                false;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  disabled={!hasData && tab.id !== 'overview'}
                  className={clsx(
                    'flex items-center gap-2 px-4 py-3.5 text-[13px] font-medium border-b-2 whitespace-nowrap transition-all',
                    activeTab === tab.id
                      ? 'border-[#18181b] text-[#18181b]'
                      : hasData
                        ? 'border-transparent text-[#71717a] hover:text-[#18181b] hover:border-[#e5e5e3]'
                        : 'border-transparent text-[#d4d4d1] cursor-not-allowed',
                  )}
                >
                  <span className="text-[15px]">{tab.icon}</span>
                  {tab.label}
                  {tab.id === 'evidence' && evidenceCards.length > 0 && (
                    <span className="ml-0.5 px-1.5 py-0.5 rounded-full bg-[#f4f4f3] text-[#71717a] text-[10px] font-semibold">
                      {evidenceCards.length}
                    </span>
                  )}
                  {tab.id === 'compliance' && blockCount > 0 && (
                    <span className="ml-0.5 px-1.5 py-0.5 rounded-full bg-red-100 text-red-700 text-[10px] font-semibold">
                      {blockCount} blocked
                    </span>
                  )}
                </button>
              );
            })}
          </div>
        </nav>

        {/* Scrollable content area */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="m-6 rounded-xl bg-red-50 border border-red-200 p-4 text-[14px] text-red-900 flex items-center gap-3">
              <span className="text-lg shrink-0">⚠️</span>
              <div>
                <span className="font-semibold">Stream error — </span>
                {error}
              </div>
            </div>
          )}

          {/* ── OVERVIEW TAB ── */}
          {activeTab === 'overview' && (
            <div className="px-6 lg:px-10 py-8 max-w-4xl">
              {/* Profile summary */}
              {profile ? (
                <>
                  <SectionHeader
                    eyebrow="Profile"
                    title={`${displayName}'s situation`}
                  />
                  <div className="grid sm:grid-cols-3 gap-4 mb-10">
                    <InfoCard label="Income gap" value={`$${profile.income_gap_monthly_usd.toLocaleString()}/mo`} highlight />
                    <InfoCard label="Available time" value={`${profile.hours_per_week_available} hrs/wk`} />
                    <InfoCard label="Startup budget" value={`$${profile.budget_startup_usd}`} />
                  </div>

                  {/* Constraints */}
                  <div className="mb-10">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#a1a1a0] mb-3">
                      Hard constraints
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {profile.hard_constraints.map((c) => (
                        <span key={c} className="px-3 py-1.5 rounded-lg bg-[#18181b] text-white text-[12px] font-medium">
                          {c.split('_').join(' ')}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Skills */}
                  {profile.skills.length > 0 && (
                    <div className="mb-10">
                      <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#a1a1a0] mb-3">
                        Skills
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {profile.skills.map((s) => (
                          <span key={s} className="px-3 py-1.5 rounded-lg bg-amber-100 text-amber-900 text-[12px] font-medium border border-amber-200">
                            {s}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <EarlyState />
              )}

              {/* Winner card — hero of the overview */}
              {winnerOpp && (
                <div className="mb-10">
                  <SectionHeader
                    eyebrow="Recommendation"
                    title="What she should do"
                  />
                  <WinnerCard opportunity={winnerOpp} />
                </div>
              )}

              {/* Quick nav to other tabs */}
              {profile && (
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
                  {TABS.filter((t) => t.id !== 'overview').map((tab) => {
                    const count =
                      tab.id === 'evidence'   ? evidenceCards.length :
                      tab.id === 'compliance' ? checks.length :
                      tab.id === 'launch'     ? (launchPacket ? 1 : 0) :
                      tab.id === 'memory'     ? (pattern ? 1 : 0) : 0;
                    return (
                      <button
                        key={tab.id}
                        onClick={() => count > 0 && setActiveTab(tab.id)}
                        disabled={count === 0}
                        className={clsx(
                          'text-left p-4 rounded-xl border transition-all',
                          count > 0
                            ? 'bg-white border-[#e5e5e3] hover:border-[#a1a1a0] hover:shadow-sm cursor-pointer'
                            : 'bg-[#f8f8f7] border-[#e5e5e3] opacity-50 cursor-not-allowed',
                        )}
                      >
                        <div className="text-xl mb-2">{tab.icon}</div>
                        <div className="text-[13px] font-semibold text-[#18181b] mb-0.5">{tab.label}</div>
                        <div className="text-[12px] text-[#71717a]">
                          {count > 0 ? `${count} item${count === 1 ? '' : 's'} ready` : 'Pending…'}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}

              {/* Complete banner */}
              {complete && (
                <div className="mt-8 rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-50 to-white p-8 flex items-center gap-6">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-500 text-white text-2xl flex items-center justify-center shrink-0 shadow-sm">
                    ✓
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="font-serif text-2xl font-bold text-[#18181b] mb-1">
                      She has a plan
                    </div>
                    <p className="text-[14px] text-[#71717a]">
                      Five real agents finished in{' '}
                      <span className="font-mono font-semibold text-[#18181b]">{elapsedSec}s</span>.
                      Real LLM. Real citations. Real published page.
                    </p>
                  </div>
                  <Link to="/" className="btn-primary shrink-0 text-[13px]">
                    New run →
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* ── EVIDENCE TAB ── */}
          {activeTab === 'evidence' && (
            <div className="px-6 lg:px-10 py-8 max-w-5xl">
              <SectionHeader
                eyebrow="Step 1 · Market Scout"
                title="What's actually selling"
                sub="Real listings pulled from Etsy, Craigslist, Outschool & more. Each card is one real-market data point."
              />
              {evidenceCards.length > 0 ? (
                <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {evidenceCards.map((c) => (
                    <EvidenceCard key={c.id} card={c} />
                  ))}
                </div>
              ) : (
                <EmptyTab label="Evidence cards will appear here as Market Scout scans the web…" />
              )}
            </div>
          )}

          {/* ── COMPLIANCE TAB ── */}
          {activeTab === 'compliance' && (
            <div className="px-6 lg:px-10 py-8 max-w-3xl">
              {blockCount > 0 ? (
                <SectionHeader
                  eyebrow="Step 2 · Reality & Compliance"
                  title={`${blockCount} path${blockCount === 1 ? '' : 's'} blocked by law`}
                  sub="Real state statutes cited below. This is the work an agent does that a friend cannot."
                  danger
                />
              ) : checks.length > 0 ? (
                <SectionHeader
                  eyebrow="Step 2 · Reality & Compliance"
                  title="All paths clear"
                  sub="Three compliance dimensions checked in parallel for every option: state law, IRS, platform ToS."
                  success
                />
              ) : (
                <SectionHeader
                  eyebrow="Step 2 · Reality & Compliance"
                  title="Compliance checks"
                />
              )}
              {checks.length > 0 ? (
                <div className="space-y-4">
                  {checks.map((c) => (
                    <ComplianceBlock
                      key={c.opportunity_id}
                      check={c}
                      opportunity={opportunities.find((o) => o.id === c.opportunity_id)}
                    />
                  ))}
                </div>
              ) : (
                <EmptyTab label="Compliance results will appear here…" />
              )}
            </div>
          )}

          {/* ── LAUNCH TAB ── */}
          {activeTab === 'launch' && (
            <div className="px-6 lg:px-10 py-8 max-w-3xl">
              <SectionHeader
                eyebrow="Step 4 · Launch Agent"
                title="Ship-ready in 7 days"
                sub="Real offer copy, real outreach drafts, real day-by-day plan. Written by Gemini. Published to the web."
              />
              {launchPacket ? (
                <LaunchPacketView packet={launchPacket} publishedUrl={publishedUrl} />
              ) : (
                <EmptyTab label="Launch packet will appear once the winner is selected…" />
              )}
            </div>
          )}

          {/* ── MEMORY TAB ── */}
          {activeTab === 'memory' && (
            <div className="px-6 lg:px-10 py-8 max-w-3xl">
              <SectionHeader
                eyebrow="Step 5 · Memory Agent"
                title="Cross-user intelligence"
                sub="Each run feeds the swarm's memory. Patterns spotted here help every future mom who runs Mom's Saheli."
              />
              {pattern ? (
                <MemoryPanel pattern={pattern} />
              ) : (
                <EmptyTab label="Cross-user patterns will surface here after the run completes…" />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Sub-components
   ───────────────────────────────────────────────────────────────────────── */

function SectionHeader({
  eyebrow, title, sub, danger, success,
}: {
  eyebrow: string;
  title: string;
  sub?: string;
  danger?: boolean;
  success?: boolean;
}) {
  return (
    <div className="mb-8">
      <div className={clsx(
        'text-[11px] font-semibold uppercase tracking-[0.12em] mb-2',
        danger ? 'text-red-600' : success ? 'text-emerald-600' : 'text-[#a1a1a0]',
      )}>
        {eyebrow}
      </div>
      <h2 className={clsx(
        'font-serif text-3xl font-bold leading-tight tracking-tight mb-2',
        danger ? 'text-red-900' : success ? 'text-emerald-900' : 'text-[#18181b]',
      )}>
        {title}
      </h2>
      {sub && (
        <p className="text-[14px] text-[#71717a] leading-relaxed max-w-xl">{sub}</p>
      )}
    </div>
  );
}

function StatCell({
  label, value, sub, mono,
}: {
  label: string;
  value: string;
  sub?: string;
  mono?: boolean;
}) {
  return (
    <div>
      <div className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[#a1a1a0] mb-1">
        {label}
      </div>
      <div className={clsx(
        'text-[22px] font-bold text-[#18181b] leading-none',
        mono ? 'font-mono' : 'font-serif',
      )}>
        {value}
        {sub && <span className="text-[12px] font-normal text-[#71717a] ml-1">{sub}</span>}
      </div>
    </div>
  );
}

function InfoCard({
  label, value, highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div className={clsx(
      'rounded-xl p-5 border',
      highlight
        ? 'bg-amber-50 border-amber-200'
        : 'bg-white border-[#e5e5e3]',
    )}>
      <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#a1a1a0] mb-2">
        {label}
      </div>
      <div className={clsx(
        'font-serif text-2xl font-bold leading-none',
        highlight ? 'text-amber-800' : 'text-[#18181b]',
      )}>
        {value}
      </div>
    </div>
  );
}

function WinnerCard({ opportunity }: { opportunity: Opportunity }) {
  return (
    <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm">
      {/* Green accent bar */}
      <div className="h-1 bg-gradient-to-r from-emerald-400 to-emerald-600" />
      <div className="p-8">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6 mb-6">
          <div>
            <div className="text-[11px] font-semibold uppercase tracking-[0.12em] text-emerald-700 mb-2">
              Recommended path
            </div>
            <h3 className="font-serif text-2xl font-bold text-[#18181b] leading-tight">
              {opportunity.title}
            </h3>
          </div>
          <div className="shrink-0 text-right">
            <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#a1a1a0] mb-1">
              Realistic net
            </div>
            <div className="font-serif text-5xl font-bold text-emerald-700 leading-none tabular-nums">
              ${opportunity.estimated_net_monthly_usd.toLocaleString()}
            </div>
            <div className="text-[13px] text-[#71717a] mt-1">per month</div>
          </div>
        </div>

        <p className="text-[15px] text-[#3f3f46] leading-relaxed mb-6 max-w-2xl">
          {opportunity.rationale}
        </p>

        {opportunity.revenue_citations && opportunity.revenue_citations.length > 0 && (
          <div className="border-t border-[#f4f4f3] pt-5">
            <div className="text-[11px] font-semibold uppercase tracking-[0.1em] text-[#a1a1a0] mb-3">
              Backed by real data
            </div>
            <div className="space-y-2">
              {opportunity.revenue_citations.slice(0, 3).map((c, i) => (
                <a
                  key={i}
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center gap-2.5 text-[13px] text-[#3f3f46] hover:text-[#18181b] group"
                >
                  <span className="text-[#a1a1a0] font-mono text-[11px] shrink-0 w-4">{i + 1}.</span>
                  <span className="underline decoration-[#e5e5e3] decoration-2 underline-offset-3 group-hover:decoration-[#18181b] truncate">
                    {c.title || c.url}
                  </span>
                  <span className="text-[#a1a1a0] shrink-0 text-[11px]">↗</span>
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function EmptyTab({ label }: { label: string }) {
  return (
    <div className="rounded-xl border border-dashed border-[#e5e5e3] bg-white p-12 text-center">
      <div className="w-10 h-10 rounded-full bg-[#f4f4f3] flex items-center justify-center mx-auto mb-3">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block" />
      </div>
      <p className="text-[14px] text-[#71717a] max-w-sm mx-auto">{label}</p>
    </div>
  );
}

function EarlyState() {
  return (
    <div className="py-20 text-center animate-fade-in">
      <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-white border border-[#e5e5e3] shadow-sm mb-5">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block" />
        <span className="text-[13px] font-medium text-[#3f3f46]">Agents warming up…</span>
      </div>
      <p className="text-[14px] text-[#71717a] max-w-xs mx-auto leading-relaxed">
        First evidence should arrive in a moment. The pipeline is live.
      </p>
    </div>
  );
}
