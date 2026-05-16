import { useMemo, useEffect, useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import clsx from 'clsx';
import { useAgentStream } from '../hooks/useAgentStream';
import AgentTimeline from '../components/AgentTimeline';
import EvidenceCard from '../components/EvidenceCard';
import ComplianceBlock from '../components/ComplianceBlock';
import LaunchPacketView from '../components/LaunchPacketView';
import MemoryPanel from '../components/MemoryPanel';
import BrowserFrame from '../components/BrowserFrame';
import type {
  ComplianceCheck,
  CrossUserPattern,
  EvidenceCard as EvidenceCardT,
  LaunchPacket,
  Opportunity,
  Profile,
} from '../types';

const PERSONA_META: Record<string, { emoji: string; scrapeUrl: string; scrapeTitle: string; lawUrl: string }> = {
  jenny: {
    emoji: '👩🏽‍🍳',
    scrapeUrl:   'https://castiron.me/search?q=weekend+meal+pack',
    scrapeTitle: 'Bright Data · Castiron',
    lawUrl:      'https://www.cdph.ca.gov/.../CottageFoodOperations.aspx',
  },
  jessica: {
    emoji: '💻',
    scrapeUrl:   'https://www.etsy.com/search?q=kids+lunch+printable',
    scrapeTitle: 'Actionbook · Etsy',
    lawUrl:      'https://www.dshs.texas.gov/.../cottage-food-production-operations',
  },
};

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
  const profile         = useMemo<Profile | null>(() => events.find((e) => e.type === 'profile_ready')?.data.profile ?? null, [events]);
  const evidenceCards   = useMemo<EvidenceCardT[]>(() => events.filter((e) => e.type === 'evidence_card').map((e) => e.data.card), [events]);
  const opportunities   = useMemo<Opportunity[]>(() => events.find((e) => e.type === 'opportunities_ranked')?.data.opportunities ?? [], [events]);
  const checks          = useMemo<ComplianceCheck[]>(() => events.filter((e) => e.type === 'compliance_check').map((e) => e.data.check), [events]);
  const launchPacket    = useMemo<LaunchPacket | null>(() => events.find((e) => e.type === 'launch_packet_ready')?.data.packet ?? null, [events]);
  const publishedUrl    = useMemo<string | null>(() => events.find((e) => e.type === 'launch_published')?.data.url ?? null, [events]);
  const pattern         = useMemo<CrossUserPattern | null>(() => events.find((e) => e.type === 'memory_pattern')?.data.pattern ?? null, [events]);

  const marketBusy     = !!evidenceCards.length && !opportunities.length;
  const complianceBusy = opportunities.length > 0 && !events.some((e) => e.type === 'winner_selected');

  const blockCount = checks.filter((c) => c.verdict === 'BLOCK').length;
  const passCount  = checks.filter((c) => c.verdict === 'PASS').length;

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-8">
      {/* ───── RUN HEADER ───── */}
      <RunHeader
        runId={runId ?? ''}
        persona={persona}
        emoji={meta.emoji}
        profile={profile}
        connected={connected}
        complete={complete}
        elapsedMs={elapsedMs}
        blockCount={blockCount}
        passCount={passCount}
        evidenceCount={evidenceCards.length}
      />

      {error && (
        <div className="rounded-xl bg-red-50 border border-red-200 p-4 mb-6 text-sm text-red-800 flex items-start gap-3">
          <span className="text-lg">⚠️</span>
          <div>
            <div className="font-semibold mb-0.5">Stream error</div>
            {error}
          </div>
        </div>
      )}

      {/* ───── MAIN GRID ───── */}
      <div className="grid lg:grid-cols-12 gap-6">

        {/* LEFT: agent swarm + hard constraints */}
        <aside className="lg:col-span-3 lg:sticky lg:top-24 lg:self-start space-y-5">
          <AgentTimeline events={events} />
          {profile && <ConstraintsCard profile={profile} />}
        </aside>

        {/* CENTER: results */}
        <section className="lg:col-span-6 space-y-8 min-w-0">
          {evidenceCards.length > 0 && (
            <Section
              eyebrow="Market evidence"
              title="Comps from real listings"
              count={evidenceCards.length}
              subtitle="Each row is a real card. Gemini ranks by realistic net monthly income."
            >
              <div className="grid sm:grid-cols-2 gap-3">
                {evidenceCards.map((c) => (
                  <EvidenceCard key={c.id} card={c} />
                ))}
              </div>
            </Section>
          )}

          {checks.length > 0 && (
            <Section
              eyebrow="Reality & compliance"
              title="Verdicts with cited law"
              count={checks.length}
              subtitle="Constraint math is deterministic. State law is scraped live (Tavily today, Bright Data tomorrow)."
            >
              <div className="space-y-3">
                {checks.map((c) => (
                  <ComplianceBlock
                    key={c.opportunity_id}
                    check={c}
                    opportunity={opportunities.find((o) => o.id === c.opportunity_id)}
                  />
                ))}
              </div>
            </Section>
          )}

          {launchPacket && (
            <Section
              eyebrow="Launch packet"
              title="Ship-ready, written by Gemini"
              subtitle="Offer, copy, price, target, outreach drafts, 7-day plan — and a real published page."
            >
              <LaunchPacketView packet={launchPacket} publishedUrl={publishedUrl} />
            </Section>
          )}

          {pattern && (
            <Section eyebrow="Memory" title="Cross-user pattern surfaced">
              <MemoryPanel pattern={pattern} />
            </Section>
          )}

          {complete && (
            <CompleteCard elapsedMs={elapsedMs} />
          )}

          {!evidenceCards.length && !checks.length && (
            <SkeletonStack />
          )}
        </section>

        {/* RIGHT: live browser frames */}
        <aside className="lg:col-span-3 space-y-5 min-w-0">
          <div className="eyebrow-muted">Live browser sessions</div>

          <BrowserFrame
            url={meta.scrapeUrl}
            title={meta.scrapeTitle}
            active={marketBusy || evidenceCards.length > 0}
            liveUrl={evidenceCards.find((c) => c.actionbook_session_url)?.actionbook_session_url ?? null}
            screenshotUrl={evidenceCards.find((c) => c.actionbook_screenshot_url)?.actionbook_screenshot_url ?? null}
          >
            {evidenceCards.length === 0 ? (
              <ScrapeSkeleton label="Scraping market comps…" />
            ) : (
              <ul className="space-y-1.5">
                {evidenceCards.map((c) => (
                  <li key={c.id} className="border-b border-ink-100 pb-1.5 last:border-0">
                    <div className="text-xs font-medium text-ink-900 truncate leading-snug">{c.title}</div>
                    <div className="text-[10px] text-ink-500 font-mono mt-0.5">
                      ${c.observed_price_usd.toFixed(0)} · {c.source}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </BrowserFrame>

          <BrowserFrame
            url={meta.lawUrl}
            title="Bright Data · State law"
            active={complianceBusy || checks.some((c) => !!c.legal_citation_text)}
          >
            {(() => {
              const cited = checks.find((c) => !!c.legal_citation_text);
              if (cited) {
                return (
                  <div className="text-xs text-ink-800 leading-relaxed font-serif italic whitespace-pre-line">
                    "{cited.legal_citation_text}"
                  </div>
                );
              }
              return <ScrapeSkeleton label="Fetching state regulation…" />;
            })()}
          </BrowserFrame>

          {/* Live stream pulse */}
          <div className="surface px-4 py-3 text-xs">
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className={clsx('w-2 h-2 rounded-full', connected ? 'bg-emerald-500 animate-pulse' : 'bg-ink-300')} />
                <span className="font-semibold text-ink-700">
                  {connected ? 'SSE streaming' : 'connecting…'}
                </span>
              </div>
              <span className="font-mono text-ink-500">{events.length} ev</span>
            </div>
            <div className="text-[10px] text-ink-400 font-mono break-all">{runId}</div>
          </div>
        </aside>
      </div>
    </div>
  );
}

/* ───────────────────────────────────────────────────────────────────────── */

function RunHeader(props: {
  runId: string;
  persona: string;
  emoji: string;
  profile: Profile | null;
  connected: boolean;
  complete: boolean;
  elapsedMs: number;
  blockCount: number;
  passCount: number;
  evidenceCount: number;
}) {
  const { persona, emoji, profile, connected, complete, elapsedMs, blockCount, passCount, evidenceCount } = props;
  return (
    <header className="surface p-6 md:p-7 mb-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-mesh-amber opacity-50" aria-hidden />
      <div className="relative flex items-start justify-between gap-6 flex-wrap">
        <div className="flex items-start gap-4 min-w-0">
          <div className="grid place-items-center w-16 h-16 rounded-2xl bg-gradient-to-br from-brand-100 to-brand-300 text-4xl shadow-soft shrink-0">
            {emoji}
          </div>
          <div className="min-w-0">
            <div className="eyebrow mb-1">
              {complete ? '✓ Run complete' : connected ? 'Run in progress' : 'Connecting…'}
            </div>
            <h1 className="serif text-3xl md:text-4xl font-bold text-ink-950 leading-tight tracking-tight">
              {profile?.display_name ?? `${persona[0].toUpperCase()}${persona.slice(1)}`}
              <span className="text-ink-400 font-normal">'s swarm</span>
            </h1>
            {profile && (
              <div className="text-sm text-ink-600 mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1">
                <span>{profile.day_job}</span>
                <span className="text-ink-300">·</span>
                <span>{profile.state}</span>
                <span className="text-ink-300">·</span>
                <span>need <strong className="text-ink-900">${profile.income_gap_monthly_usd}/mo</strong></span>
                <span className="text-ink-300">·</span>
                <span><strong className="text-ink-900">{profile.hours_per_week_available} hr/wk</strong></span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link to="/" className="btn-ghost text-sm">
            <span aria-hidden>←</span>
            Back
          </Link>
        </div>
      </div>

      {/* Live stat strip */}
      <div className="relative grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-ink-100">
        <StatPill label="Elapsed"   value={`${(elapsedMs / 1000).toFixed(1)}s`} mono />
        <StatPill label="Evidence"  value={evidenceCount.toString()} />
        <StatPill label="Blocked"   value={blockCount.toString()} tone={blockCount > 0 ? 'danger' : 'neutral'} />
        <StatPill label="Passed"    value={passCount.toString()}  tone={passCount > 0  ? 'success' : 'neutral'} />
      </div>
    </header>
  );
}

function StatPill({ label, value, tone, mono }: { label: string; value: string; tone?: 'success' | 'danger' | 'neutral'; mono?: boolean }) {
  const valueColor =
    tone === 'success' ? 'text-emerald-700'
  : tone === 'danger'  ? 'text-red-700'
  :                      'text-ink-900';
  return (
    <div className="px-3 py-1">
      <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500 mb-0.5">{label}</div>
      <div className={clsx('font-serif text-2xl font-bold leading-none tabular-nums', mono && 'font-mono', valueColor)}>
        {value}
      </div>
    </div>
  );
}

function Section({ eyebrow, title, count, subtitle, children }: {
  eyebrow: string; title: string; count?: number; subtitle?: string; children: React.ReactNode;
}) {
  return (
    <section className="animate-fade-in">
      <div className="mb-4">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="eyebrow">{eyebrow}</span>
          {count !== undefined && <span className="text-[11px] font-mono text-ink-400">({count})</span>}
        </div>
        <h2 className="serif text-2xl font-bold text-ink-900 leading-tight">{title}</h2>
        {subtitle && <p className="text-sm text-ink-600 mt-1 max-w-2xl">{subtitle}</p>}
      </div>
      {children}
    </section>
  );
}

function ConstraintsCard({ profile }: { profile: Profile }) {
  return (
    <div className="surface p-5">
      <div className="eyebrow mb-2">Hard constraints</div>
      <ul className="flex flex-wrap gap-1.5">
        {profile.hard_constraints.map((c) => (
          <li key={c} className="pill bg-ink-100 text-ink-700">{c}</li>
        ))}
      </ul>
      {profile.skills.length > 0 && (
        <>
          <div className="eyebrow mt-4 mb-2">Skills</div>
          <ul className="flex flex-wrap gap-1.5">
            {profile.skills.map((s) => (
              <li key={s} className="pill bg-brand-50 text-brand-800 border border-brand-200">{s}</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}

function CompleteCard({ elapsedMs }: { elapsedMs: number }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50 via-white to-cream p-6 text-center animate-bounce-in">
      <div className="grid place-items-center w-14 h-14 rounded-full bg-emerald-100 text-emerald-700 text-3xl mx-auto mb-3 shadow-soft">
        ✓
      </div>
      <div className="serif text-2xl font-bold text-ink-900 mb-1">Run complete</div>
      <p className="text-sm text-ink-600 mb-4">
        Swarm finished in <strong className="font-mono text-ink-900">{(elapsedMs / 1000).toFixed(1)}s</strong>.
        Real LLM, real citations, real launch page.
      </p>
      <Link to="/" className="btn-primary text-sm">
        Run another
        <span aria-hidden>→</span>
      </Link>
    </div>
  );
}

function SkeletonStack() {
  return (
    <div className="space-y-3 animate-fade-in">
      <div className="skeleton h-24 rounded-2xl" />
      <div className="skeleton h-24 rounded-2xl" />
      <div className="skeleton h-24 rounded-2xl" />
      <p className="text-center text-xs text-ink-500 pt-2">
        Waiting for first evidence card from Market Scout…
      </p>
    </div>
  );
}

function ScrapeSkeleton({ label }: { label: string }) {
  return (
    <div className="space-y-2 py-3">
      <div className="skeleton h-3 w-3/4" />
      <div className="skeleton h-3 w-1/2" />
      <div className="skeleton h-3 w-2/3" />
      <p className="text-[10px] text-ink-400 italic pt-2">{label}</p>
    </div>
  );
}
