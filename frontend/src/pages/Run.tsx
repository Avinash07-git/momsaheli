import { useMemo, useEffect, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import clsx from 'clsx';
import { useAgentStream } from '../hooks/useAgentStream';
import EvidenceCard from '../components/EvidenceCard';
import CustomerLeadCard from '../components/CustomerLeadCard';
import ComplianceBlock from '../components/ComplianceBlock';
import LaunchPacketView from '../components/LaunchPacketView';
import MemoryPanel from '../components/MemoryPanel';
import type {
  AgentEvent,
  ComplianceCheck,
  CrossUserPattern,
  CustomerLead,
  EvidenceCard as EvidenceCardT,
  LaunchPacket,
  Opportunity,
  Profile,
} from '../types';

const PERSONA_META: Record<string, { emoji: string; color: string; bg: string }> = {
  jenny:   { emoji: '👩🏽‍🍳', color: '#d97706', bg: '#fef3c7' },
  jessica: { emoji: '💻',     color: '#6366f1', bg: '#ede9fe' },
  custom:  { emoji: '🧭',     color: '#0f766e', bg: '#ccfbf1' },
};

const AGENTS = [
  { id: 'profile',            label: 'Profile Agent',        doneEvent: 'profile_ready' },
  { id: 'market_scout',       label: 'Market Scout',         doneEvent: 'opportunities_ranked' },
  { id: 'customer_leads',      label: 'Customer Leads',       doneEvent: 'customer_lead' },
  { id: 'reality_compliance', label: 'Reality & Compliance', doneEvent: 'winner_selected' },
  { id: 'launch',             label: 'Launch Agent',         doneEvent: 'launch_published' },
  { id: 'memory',             label: 'Memory Agent',         doneEvent: 'memory_pattern' },
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

type TabId = 'overview' | 'evidence' | 'leads' | 'compliance' | 'launch' | 'memory';

const TABS: { id: TabId; label: string; emoji: string; desc: string; activeColor: string; activeBg: string; idleBg: string; idleColor: string }[] = [
  { id: 'overview',    label: 'Overview',    emoji: '◈', desc: 'Profile & winner',     activeColor: '#18181b', activeBg: '#f4f4f3', idleBg: '#fafafa',  idleColor: '#78716c' },
  { id: 'evidence',   label: 'Evidence',    emoji: '📊', desc: 'Market signals',       activeColor: '#1d4ed8', activeBg: '#dbeafe', idleBg: '#eff6ff',  idleColor: '#3b82f6' },
  { id: 'leads',      label: 'Leads',       emoji: '👥', desc: 'Customer demand',      activeColor: '#047857', activeBg: '#d1fae5', idleBg: '#ecfdf5',  idleColor: '#10b981' },
  { id: 'compliance', label: 'Compliance',  emoji: '⚖️',  desc: 'Legal checks',         activeColor: '#b91c1c', activeBg: '#fee2e2', idleBg: '#fff1f2',  idleColor: '#ef4444' },
  { id: 'launch',     label: 'Launch',      emoji: '🚀', desc: 'Ready-to-ship plan',   activeColor: '#065f46', activeBg: '#d1fae5', idleBg: '#f0fdf4',  idleColor: '#22c55e' },
  { id: 'memory',     label: 'Memory',      emoji: '🧠', desc: 'Cross-user patterns',  activeColor: '#6b21a8', activeBg: '#f3e8ff', idleBg: '#faf5ff',  idleColor: '#a855f7' },
];

export default function Run() {
  const { runId } = useParams<{ runId: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') ?? 'jenny';
  const meta = PERSONA_META[persona] ?? PERSONA_META.jenny;

  const { events, connected, complete, error } = useAgentStream(runId ?? null);
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  const [elapsedMs, setElapsedMs] = useState(0);
  const startEvent    = useMemo(() => events.find((e) => e.type === 'run_started'),  [events]);
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

  const profile       = useMemo<Profile | null>(
    () => events.find((e) => e.type === 'profile_ready')?.data.profile ?? null, [events]);
  const evidenceCards = useMemo<EvidenceCardT[]>(
    () => events.filter((e) => e.type === 'evidence_card').map((e) => e.data.card), [events]);
  const customerLeads = useMemo<CustomerLead[]>(
    () => events.filter((e) => e.type === 'customer_lead').map((e) => e.data.lead), [events]);
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
  const gmailWatch    = useMemo<{ slug: string; live: boolean } | null>(
    () => (events.find((e) => e.type === 'gmail_watching')?.data ?? null) as { slug: string; live: boolean } | null, [events]);

  const winnerOpp = useMemo<Opportunity | null>(() => {
    const passing = checks.find((c) => c.verdict === 'PASS');
    return passing ? (opportunities.find((o) => o.id === passing.opportunity_id) ?? null) : null;
  }, [checks, opportunities]);

  const blockCount = checks.filter((c) => c.verdict === 'BLOCK').length;
  const passCount  = checks.filter((c) => c.verdict === 'PASS').length;
  const elapsedSec = (elapsedMs / 1000).toFixed(1);
  const displayName = profile?.display_name ?? (persona[0].toUpperCase() + persona.slice(1));

  const tabData: Record<TabId, boolean> = {
    overview:   true,
    evidence:   evidenceCards.length > 0,
    leads:      customerLeads.length > 0,
    compliance: checks.length > 0,
    launch:     !!launchPacket,
    memory:     !!pattern,
  };

  return (
    /*
      One natural page scroll.
      On desktop: sidebar is sticky (sticks to viewport), content flows normally.
      No nested overflow containers — the browser's scrollbar is the only one.
    */
    <div className="flex min-h-screen bg-[#f5f5f4]">

      {/* ══════════════════════════════════════════════
          SIDEBAR — sticky, scrolls with the page on desktop
          ══════════════════════════════════════════════ */}
      <aside className="hidden lg:flex flex-col w-[260px] shrink-0 sticky top-0 self-start h-screen bg-white border-r border-[#e7e5e4]">

        {/* Back link */}
        <div className="px-5 py-4 border-b border-[#e7e5e4]">
          <Link
            to="/"
            className="inline-flex items-center gap-2 text-[13px] font-medium text-[#78716c] hover:text-[#1c1917] transition-colors"
          >
            <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
              <path d="M19 12H5M5 12l7-7M5 12l7 7" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Mom's Saheli
          </Link>
        </div>

        {/* Persona */}
        <div className="px-5 py-5 border-b border-[#e7e5e4]">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl mb-3 shadow-sm"
            style={{ background: meta.bg }}
          >
            {meta.emoji}
          </div>
          <div className="text-[10px] font-bold uppercase tracking-[0.14em] mb-1"
            style={{ color: meta.color }}>
            {complete ? 'Run complete' : connected ? 'Running now' : 'Connecting…'}
          </div>
          <h1 className="font-serif text-[22px] font-bold text-[#1c1917] leading-tight">
            {displayName}
          </h1>
          {profile && (
            <p className="text-[12px] text-[#78716c] mt-1 leading-snug">
              {profile.day_job}{profile.city ? ` · ${profile.city}` : ''}, {profile.state}
            </p>
          )}
        </div>

        {/* Key stats */}
        {profile && (
          <div className="px-5 py-4 border-b border-[#e7e5e4] grid grid-cols-2 gap-x-4 gap-y-3">
            <SidebarStat label="Gap" value={`$${profile.income_gap_monthly_usd.toLocaleString()}/mo`} accent />
            <SidebarStat label="Hours" value={`${profile.hours_per_week_available}/wk`} />
            <SidebarStat label="Budget" value={`$${profile.budget_startup_usd}`} />
            <SidebarStat label="Time" value={`${elapsedSec}s`} mono />
          </div>
        )}

        {/* Agent pipeline */}
        <div className="px-5 py-4 flex-1 overflow-y-auto">
          <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#a8a29e] mb-3">
            Agent pipeline
          </div>
          <ol className="space-y-0.5">
            {AGENTS.map((agent, i) => {
              const s = agentStatus(agent.id, events);
              return (
                <li key={agent.id} className="relative">
                  {i < AGENTS.length - 1 && (
                    <span className={clsx(
                      'absolute left-[15px] top-[34px] w-px h-4 z-0',
                      s === 'done' ? 'bg-emerald-300' : 'bg-[#e7e5e4]',
                    )} />
                  )}
                  <div className={clsx(
                    'relative z-10 flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[12px] font-medium transition-colors',
                    s === 'idle'    && 'text-[#a8a29e]',
                    s === 'running' && 'bg-amber-50 text-[#92400e]',
                    s === 'done'    && 'text-[#1c1917]',
                    s === 'error'   && 'text-red-700',
                  )}>
                    <span className={clsx(
                      'w-[26px] h-[26px] rounded-full flex items-center justify-center text-[11px] font-bold shrink-0',
                      s === 'idle'    && 'bg-[#f5f5f4] text-[#a8a29e]',
                      s === 'running' && 'bg-amber-400 text-white animate-pulse',
                      s === 'done'    && 'bg-emerald-500 text-white',
                      s === 'error'   && 'bg-red-500 text-white',
                    )}>
                      {s === 'done' ? '✓' : s === 'error' ? '!' : i + 1}
                    </span>
                    {agent.label}
                  </div>
                </li>
              );
            })}
          </ol>
        </div>

        {/* Winner anchor */}
        {winnerOpp && (
          <div className="m-4 rounded-xl border border-emerald-200 bg-emerald-50 p-4 shrink-0">
            <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-emerald-700 mb-1">
              Recommendation
            </div>
            <div className="font-serif text-[22px] font-bold text-emerald-900 leading-none tabular-nums">
              ${winnerOpp.estimated_net_monthly_usd.toLocaleString()}
              <span className="text-[13px] font-sans font-normal text-emerald-700 ml-1">/mo</span>
            </div>
            <div className="text-[11px] text-emerald-800 mt-1 leading-snug">{winnerOpp.title}</div>
          </div>
        )}
      </aside>

      {/* ══════════════════════════════════════════════
          MAIN — header + big tab bar + content
          No overflow-hidden anywhere. One scroll only.
          ══════════════════════════════════════════════ */}
      <div className="flex-1 min-w-0 flex flex-col">

        {/* Sticky top header */}
        <header className="sticky top-0 z-30 bg-white border-b border-[#e7e5e4]">
          <div className="px-6 lg:px-10 py-3 flex items-center justify-between gap-4">

            {/* Mobile back + name */}
            <div className="flex items-center gap-3 lg:hidden">
              <Link to="/" className="text-[#78716c] hover:text-[#1c1917]">
                <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <path d="M19 12H5M5 12l7-7M5 12l7 7" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </Link>
              <span className="font-semibold text-[#1c1917] text-[15px]">{displayName}</span>
            </div>

            {/* Desktop: run ID + status */}
            <div className="hidden lg:flex items-center gap-3">
              <span className="text-[12px] text-[#a8a29e] font-mono">{runId?.slice(0, 12)}…</span>
              {complete ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold uppercase tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Complete
                </span>
              ) : connected ? (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 text-[11px] font-bold uppercase tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" /> Running
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#f5f5f4] text-[#78716c] text-[11px] font-bold uppercase tracking-wide">
                  Connecting…
                </span>
              )}
            </div>

            {/* Right: live stats */}
            <div className="flex items-center gap-5 ml-auto">
              {evidenceCards.length > 0 && (
                <span className="text-[13px] text-[#78716c]">
                  <span className="font-semibold text-[#1c1917]">{evidenceCards.length}</span> signals
                </span>
              )}
              {customerLeads.length > 0 && (
                <span className="text-[13px] text-[#78716c]">
                  <span className="font-semibold text-emerald-600">{customerLeads.length}</span> leads
                </span>
              )}
              {blockCount > 0 && (
                <span className="text-[13px] text-[#78716c]">
                  <span className="font-semibold text-red-600">{blockCount}</span> blocked
                </span>
              )}
              {passCount > 0 && (
                <span className="text-[13px] text-[#78716c]">
                  <span className="font-semibold text-emerald-600">{passCount}</span> passed
                </span>
              )}
              <span className="font-mono text-[12px] text-[#a8a29e]">{elapsedSec}s</span>
            </div>
          </div>

          {/* ── BIG TAB BAR ── */}
          <div className="px-6 lg:px-10 pb-0 flex gap-1 overflow-x-auto">
            {TABS.map((tab) => {
              const active = activeTab === tab.id;
              const ready  = tabData[tab.id];
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    'group flex flex-col items-start px-5 py-3.5 rounded-t-xl border-b-2 min-w-[120px] transition-all duration-150 whitespace-nowrap',
                    active ? 'border-b-2' : 'border-transparent hover:brightness-95',
                  )}
                  style={{
                    background: active ? tab.activeBg : tab.idleBg,
                    borderBottomColor: active ? tab.activeColor : 'transparent',
                  }}
                >
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="inline-flex items-center justify-center w-7 h-7 rounded-lg text-[14px] bg-white/60 shadow-sm">
                      {tab.emoji}
                    </span>
                    <span
                      className="text-[14px] font-semibold transition-colors"
                      style={{ color: active ? tab.activeColor : tab.idleColor }}
                    >
                      {tab.label}
                    </span>
                    {tab.id === 'evidence' && evidenceCards.length > 0 && (
                      <span className="px-1.5 py-0.5 rounded-full bg-blue-200 text-blue-800 text-[10px] font-bold">
                        {evidenceCards.length}
                      </span>
                    )}
                    {tab.id === 'leads' && customerLeads.length > 0 && (
                      <span className="px-1.5 py-0.5 rounded-full bg-emerald-200 text-emerald-800 text-[10px] font-bold">
                        {customerLeads.length}
                      </span>
                    )}
                    {tab.id === 'compliance' && blockCount > 0 && (
                      <span className="px-1.5 py-0.5 rounded-full bg-red-200 text-red-800 text-[10px] font-bold">
                        {blockCount}
                      </span>
                    )}
                    {!ready && (
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse inline-block"
                        style={{ background: tab.idleColor, opacity: 0.5 }} />
                    )}
                  </div>
                  <span className="text-[11px] font-medium pl-9" style={{ color: tab.idleColor, opacity: active ? 1 : 0.7 }}>
                    {ready ? tab.desc : 'Waiting…'}
                  </span>
                </button>
              );
            })}
          </div>
        </header>

        {/* ── TAB CONTENT — plain page flow, no overflow containers ── */}
        <main className="flex-1 px-6 lg:px-10 py-8">

          {error && (
            <div className="mb-6 rounded-xl bg-red-50 border border-red-200 p-4 text-[14px] text-red-900 flex items-center gap-3">
              <span className="text-lg shrink-0">⚠️</span>
              <span><strong>Stream error — </strong>{error}</span>
            </div>
          )}

          {/* OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="max-w-3xl space-y-8 animate-fade-in">
              {profile ? (
                <>
                  <div>
                    <Eyebrow>Profile</Eyebrow>
                    <SectionTitle>{displayName}'s situation</SectionTitle>
                    <div className="grid sm:grid-cols-3 gap-4 mt-5">
                      <InfoCard label="Income gap" value={`$${profile.income_gap_monthly_usd.toLocaleString()}/mo`} accent />
                      <InfoCard label="Available time" value={`${profile.hours_per_week_available} hrs/wk`} />
                      <InfoCard label="Startup budget" value={`$${profile.budget_startup_usd}`} />
                    </div>
                  </div>

                  <div>
                    <Eyebrow>Hard constraints</Eyebrow>
                    <div className="flex flex-wrap gap-2 mt-3">
                      {profile.hard_constraints.map((c) => (
                        <span key={c} className="px-3 py-1.5 rounded-lg bg-[#1c1917] text-white text-[12px] font-medium">
                          {c.split('_').join(' ')}
                        </span>
                      ))}
                    </div>
                  </div>

                  {profile.skills.length > 0 && (
                    <div>
                      <Eyebrow>Skills</Eyebrow>
                      <div className="flex flex-wrap gap-2 mt-3">
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

              {winnerOpp && (
                <div>
                  <Eyebrow>Recommendation</Eyebrow>
                  <SectionTitle>What she should do</SectionTitle>
                  <div className="mt-5">
                    <WinnerCard opportunity={winnerOpp} />
                  </div>
                </div>
              )}

              {/* Quick-nav cards to other tabs */}
              {profile && (
                <div>
                  <Eyebrow>Explore deeper</Eyebrow>
                  <div className="grid sm:grid-cols-2 gap-3 mt-4">
                    {TABS.filter((t) => t.id !== 'overview').map((tab) => {
                      const ready = tabData[tab.id];
                      return (
                        <button
                          key={tab.id}
                          onClick={() => ready && setActiveTab(tab.id)}
                          disabled={!ready}
                          className={clsx(
                            'text-left p-4 rounded-xl border transition-all',
                            ready
                              ? 'bg-white border-[#e7e5e4] hover:border-[#a8a29e] hover:shadow-sm'
                              : 'bg-[#f5f5f4] border-[#e7e5e4] opacity-50 cursor-not-allowed',
                          )}
                        >
                          <div className="flex items-center gap-2.5 mb-1.5">
                            <span className="text-[18px]">{tab.emoji}</span>
                            <span className="font-semibold text-[14px] text-[#1c1917]">{tab.label}</span>
                          </div>
                          <div className="text-[12px] text-[#78716c]">
                            {ready ? tab.desc : 'Pending…'}
                          </div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {complete && (
                <div className="rounded-2xl border border-emerald-200 bg-gradient-to-r from-emerald-50 to-white p-8 flex items-center gap-6">
                  <div className="w-14 h-14 rounded-2xl bg-emerald-500 text-white text-2xl flex items-center justify-center shrink-0">✓</div>
                  <div className="flex-1 min-w-0">
                    <div className="font-serif text-2xl font-bold text-[#1c1917] mb-1">She has a plan</div>
                    <p className="text-[14px] text-[#78716c]">
                      Five real agents finished in <span className="font-mono font-semibold text-[#1c1917]">{elapsedSec}s</span>.
                      Real LLM. Real citations. Real published page.
                    </p>
                  </div>
                  <Link to="/" className="btn-primary shrink-0 text-[13px]">New run →</Link>
                </div>
              )}
            </div>
          )}

          {/* EVIDENCE */}
          {activeTab === 'evidence' && (
            <div className="animate-fade-in">
              <Eyebrow>Step 1 · Market Scout</Eyebrow>
              <SectionTitle>What's actually selling</SectionTitle>
              <p className="text-[14px] text-[#78716c] mt-2 max-w-xl">
                Real listings from Etsy, Craigslist, Outschool & more. Each card is one live market data point used to rank opportunities.
              </p>
              <div className="mt-3 mb-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-200">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden className="text-blue-500 shrink-0">
                  <path d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <span className="text-[11px] text-blue-700 font-medium">
                  Web scraped by{' '}
                  <a
                    href="https://brightdata.com"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-bold hover:underline"
                  >
                    Bright Data
                  </a>
                  {' '}— all links open real, live sources
                </span>
              </div>
              {evidenceCards.length > 0 ? (
                <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4 max-w-5xl">
                  {evidenceCards.map((c) => <EvidenceCard key={c.id} card={c} />)}
                </div>
              ) : (
                <EmptyTab label="Evidence cards appear as Market Scout scans the web…" />
              )}
            </div>
          )}

          {/* LEADS */}
          {activeTab === 'leads' && (
            <div className="animate-fade-in">
              <Eyebrow success>Step 2 · Customer Leads</Eyebrow>
              <SectionTitle success>Who might buy this</SectionTitle>
              <p className="text-[14px] text-[#78716c] mt-2 mb-4 max-w-xl">
                Evidence shows what similar sellers are doing. Leads show buyer-intent posts and searches from people asking for the thing she can offer.
              </p>
              <p className="inline-flex items-center gap-1.5 text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-full px-3 py-1 mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 shrink-0" />
                Scraped from Reddit · Quora · Facebook · Nextdoor via Bright Data — all links open real, live posts
              </p>
              {customerLeads.length > 0 ? (
                <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-4 max-w-5xl">
                  {customerLeads.map((lead) => <CustomerLeadCard key={lead.id} lead={lead} />)}
                </div>
              ) : (
                <EmptyTab label="Customer leads appear after the winning opportunity is selected…" />
              )}
            </div>
          )}

          {/* COMPLIANCE */}
          {activeTab === 'compliance' && (
            <div className="max-w-3xl animate-fade-in">
              {blockCount > 0 ? (
                <>
                  <Eyebrow danger>Step 2 · Reality & Compliance</Eyebrow>
                  <SectionTitle danger>{blockCount} path{blockCount === 1 ? '' : 's'} blocked by law</SectionTitle>
                  <p className="text-[14px] text-[#78716c] mt-2 mb-6 max-w-xl">
                    Real state statutes cited below. Three compliance dimensions run in parallel per option — state law, IRS, and platform ToS.
                  </p>
                </>
              ) : checks.length > 0 ? (
                <>
                  <Eyebrow success>Step 2 · Reality & Compliance</Eyebrow>
                  <SectionTitle success>All paths clear</SectionTitle>
                  <p className="text-[14px] text-[#78716c] mt-2 mb-6 max-w-xl">
                    Three compliance dimensions checked in parallel for every option.
                  </p>
                </>
              ) : (
                <>
                  <Eyebrow>Step 2 · Reality & Compliance</Eyebrow>
                  <SectionTitle>Compliance checks</SectionTitle>
                </>
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
                <EmptyTab label="Compliance results will appear once Market Scout finishes…" />
              )}
            </div>
          )}

          {/* LAUNCH */}
          {activeTab === 'launch' && (
            <div className="max-w-3xl animate-fade-in">
              <Eyebrow>Step 4 · Launch Agent</Eyebrow>
              <SectionTitle>Ship-ready in 7 days</SectionTitle>
              <p className="text-[14px] text-[#78716c] mt-2 mb-6 max-w-xl">
                Real offer copy, real outreach drafts, real day-by-day plan — written by Gemini and published to the web.
              </p>
              {gmailWatch && (
                <div className="mb-6 flex items-center gap-3 px-4 py-3 rounded-xl bg-white border border-emerald-200 shadow-sm">
                  <span className="text-xl shrink-0">📬</span>
                  <div className="flex-1 min-w-0">
                    <div className="text-[12px] font-bold text-emerald-800 mb-0.5">
                      Actionbook is watching your Gmail
                    </div>
                    <p className="text-[11px] text-emerald-700 leading-snug">
                      When a customer reserves a spot, Actionbook will open your Gmail and send the follow-up from your own account automatically.
                    </p>
                  </div>
                  <span className={`w-2 h-2 rounded-full shrink-0 ${gmailWatch.live ? 'bg-emerald-500 animate-pulse' : 'bg-amber-400'}`} />
                </div>
              )}
              {launchPacket
                ? <LaunchPacketView packet={launchPacket} publishedUrl={publishedUrl} />
                : <EmptyTab label="Launch packet appears once the winner is selected…" />}
            </div>
          )}

          {/* MEMORY */}
          {activeTab === 'memory' && (
            <div className="max-w-3xl animate-fade-in">
              <Eyebrow>Step 5 · Memory Agent</Eyebrow>
              <SectionTitle>Cross-user intelligence</SectionTitle>
              <p className="text-[14px] text-[#78716c] mt-2 mb-6 max-w-xl">
                Each run feeds the swarm's memory. Patterns spotted here help every future mom who runs Mom's Saheli.
              </p>
              {pattern
                ? <MemoryPanel pattern={pattern} />
                : <EmptyTab label="Patterns surface after the run completes…" />}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

/* ─────────────────────────────────────────────────────────────────────────
   Tiny building blocks
   ───────────────────────────────────────────────────────────────────────── */

function Eyebrow({ children, danger, success }: { children: React.ReactNode; danger?: boolean; success?: boolean }) {
  return (
    <div className={clsx(
      'text-[10px] font-bold uppercase tracking-[0.16em] mb-1.5',
      danger ? 'text-red-600' : success ? 'text-emerald-600' : 'text-[#a8a29e]',
    )}>
      {children}
    </div>
  );
}

function SectionTitle({ children, danger, success }: { children: React.ReactNode; danger?: boolean; success?: boolean }) {
  return (
    <h2 className={clsx(
      'font-serif text-[28px] font-bold leading-tight tracking-tight',
      danger ? 'text-red-900' : success ? 'text-emerald-900' : 'text-[#1c1917]',
    )}>
      {children}
    </h2>
  );
}

function SidebarStat({ label, value, accent, mono }: { label: string; value: string; accent?: boolean; mono?: boolean }) {
  return (
    <div>
      <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#a8a29e] mb-0.5">{label}</div>
      <div className={clsx(
        'text-[16px] font-bold leading-none',
        mono ? 'font-mono text-[#78716c]' : 'font-serif',
        accent ? 'text-amber-700' : 'text-[#1c1917]',
      )}>
        {value}
      </div>
    </div>
  );
}

function InfoCard({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className={clsx(
      'rounded-xl p-5 border',
      accent ? 'bg-amber-50 border-amber-200' : 'bg-white border-[#e7e5e4]',
    )}>
      <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#a8a29e] mb-2">{label}</div>
      <div className={clsx(
        'font-serif text-[22px] font-bold leading-none',
        accent ? 'text-amber-800' : 'text-[#1c1917]',
      )}>
        {value}
      </div>
    </div>
  );
}

function WinnerCard({ opportunity }: { opportunity: Opportunity }) {
  return (
    <div className="rounded-2xl border border-emerald-200 bg-white overflow-hidden shadow-sm">
      <div className="h-1 bg-gradient-to-r from-emerald-400 to-emerald-600" />
      <div className="p-8">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-6 mb-5">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-emerald-700 mb-2">
              Recommended path
            </div>
            <h3 className="font-serif text-[24px] font-bold text-[#1c1917] leading-tight">
              {opportunity.title}
            </h3>
          </div>
          <div className="shrink-0 text-right">
            <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#a8a29e] mb-1">Realistic net</div>
            <div className="font-serif text-[48px] font-bold text-emerald-700 leading-none tabular-nums">
              ${opportunity.estimated_net_monthly_usd.toLocaleString()}
            </div>
            <div className="text-[12px] text-[#78716c] mt-1">per month</div>
          </div>
        </div>
        <p className="text-[15px] text-[#44403c] leading-relaxed mb-6">{opportunity.rationale}</p>
        {opportunity.revenue_citations?.length > 0 && (
          <div className="border-t border-[#f5f5f4] pt-5">
            <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#a8a29e] mb-3">Backed by real data</div>
            <div className="space-y-2">
              {opportunity.revenue_citations.slice(0, 3).map((c, i) => (
                <a key={i} href={c.url} target="_blank" rel="noreferrer"
                  className="flex items-center gap-2 text-[13px] text-[#44403c] hover:text-[#1c1917] group">
                  <span className="text-[#a8a29e] font-mono text-[11px] shrink-0 w-4">{i + 1}.</span>
                  <span className="underline decoration-[#e7e5e4] decoration-2 underline-offset-2 group-hover:decoration-[#1c1917] truncate">
                    {c.title || c.url}
                  </span>
                  <span className="text-[#a8a29e] shrink-0 text-[11px]">↗</span>
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
    <div className="rounded-xl border border-dashed border-[#e7e5e4] bg-white p-14 text-center mt-2">
      <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block mb-3" />
      <p className="text-[14px] text-[#78716c] max-w-sm mx-auto">{label}</p>
    </div>
  );
}

function EarlyState() {
  return (
    <div className="py-16 text-center animate-fade-in">
      <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full bg-white border border-[#e7e5e4] shadow-sm mb-4">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block" />
        <span className="text-[13px] font-medium text-[#44403c]">Agents warming up…</span>
      </div>
      <p className="text-[14px] text-[#78716c] max-w-xs mx-auto leading-relaxed">
        First evidence should arrive in a moment. The pipeline is live.
      </p>
    </div>
  );
}
