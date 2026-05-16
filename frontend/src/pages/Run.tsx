import { useMemo } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
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

const ETSY_URLS: Record<string, string> = {
  jenny: 'https://www.etsy.com/search?q=weekend+family+meal+pack&order=most_relevant',
  jessica: 'https://www.etsy.com/search?q=kids+lunch+printable&order=most_relevant',
};

const LAW_URLS: Record<string, string> = {
  jenny: 'https://www.cdph.ca.gov/.../CottageFoodOperations.aspx',
  jessica: 'https://www.dshs.texas.gov/.../cottage-food-production-operations',
};

export default function Run() {
  const { runId } = useParams<{ runId: string }>();
  const [params] = useSearchParams();
  const persona = params.get('persona') ?? 'jenny';

  const { events, connected, complete, error } = useAgentStream(runId ?? null);

  // Derive structured views from the event log
  const profile = useMemo<Profile | null>(
    () => events.find((e) => e.type === 'profile_ready')?.data.profile ?? null,
    [events],
  );

  const evidenceCards = useMemo<EvidenceCardT[]>(
    () => events.filter((e) => e.type === 'evidence_card').map((e) => e.data.card),
    [events],
  );

  const opportunities = useMemo<Opportunity[]>(
    () => events.find((e) => e.type === 'opportunities_ranked')?.data.opportunities ?? [],
    [events],
  );

  const checks = useMemo<ComplianceCheck[]>(
    () => events.filter((e) => e.type === 'compliance_check').map((e) => e.data.check),
    [events],
  );

  const launchPacket = useMemo<LaunchPacket | null>(
    () => events.find((e) => e.type === 'launch_packet_ready')?.data.packet ?? null,
    [events],
  );

  const publishedUrl = useMemo<string | null>(
    () => events.find((e) => e.type === 'launch_published')?.data.url ?? null,
    [events],
  );

  const pattern = useMemo<CrossUserPattern | null>(
    () => events.find((e) => e.type === 'memory_pattern')?.data.pattern ?? null,
    [events],
  );

  const marketBusy = !!evidenceCards.length && !opportunities.length;
  const complianceBusy =
    opportunities.length > 0 && !events.some((e) => e.type === 'winner_selected');

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Run header */}
      <header className="flex items-start justify-between gap-4 mb-6">
        <div>
          <p className="text-xs text-gray-500 font-mono">{runId}</p>
          <h1 className="serif text-3xl font-bold text-gray-900">
            {profile?.display_name ? `${profile.display_name}'s run` : 'Starting swarm…'}
          </h1>
          {profile && (
            <p className="text-sm text-gray-600 mt-1">
              {profile.day_job} · {profile.state} · need <strong>${profile.income_gap_monthly_usd}</strong>/mo ·
              {' '}<strong>{profile.hours_per_week_available} hr/wk</strong>
            </p>
          )}
        </div>
        <Link to="/" className="text-sm text-brand-700 hover:text-brand-900">← Back</Link>
      </header>

      {error && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-3 mb-4 text-sm text-red-800">
          {error}
        </div>
      )}

      <div className="grid lg:grid-cols-12 gap-6">
        {/* Left: agent timeline */}
        <aside className="lg:col-span-3">
          <AgentTimeline events={events} />
          {profile && (
            <div className="card p-4 mt-4 text-sm">
              <h3 className="font-semibold mb-2 text-gray-900">Hard constraints</h3>
              <ul className="flex flex-wrap gap-1.5">
                {profile.hard_constraints.map((c) => (
                  <li key={c} className="pill bg-gray-100 text-gray-700">{c}</li>
                ))}
              </ul>
            </div>
          )}
        </aside>

        {/* Center: evidence + compliance + launch */}
        <section className="lg:col-span-6 space-y-6">
          {evidenceCards.length > 0 && (
            <div>
              <h2 className="serif text-xl font-bold mb-3 text-gray-900">
                📊 Market evidence ({evidenceCards.length})
              </h2>
              <div className="space-y-2">
                {evidenceCards.map((c) => (
                  <EvidenceCard key={c.id} card={c} />
                ))}
              </div>
            </div>
          )}

          {checks.length > 0 && (
            <div>
              <h2 className="serif text-xl font-bold mb-3 text-gray-900">
                ⚖️ Compliance verdicts ({checks.length})
              </h2>
              <div className="space-y-3">
                {checks.map((c) => (
                  <ComplianceBlock
                    key={c.opportunity_id}
                    check={c}
                    opportunity={opportunities.find((o) => o.id === c.opportunity_id)}
                  />
                ))}
              </div>
            </div>
          )}

          {launchPacket && (
            <div>
              <h2 className="serif text-xl font-bold mb-3 text-gray-900">🚀 Launch packet</h2>
              <LaunchPacketView packet={launchPacket} publishedUrl={publishedUrl} />
            </div>
          )}

          {pattern && (
            <div>
              <h2 className="serif text-xl font-bold mb-3 text-gray-900">🧠 Memory</h2>
              <MemoryPanel pattern={pattern} />
            </div>
          )}

          {complete && (
            <div className="card p-4 text-center bg-green-50 border-green-200">
              <p className="text-green-800 font-semibold">✅ Run complete</p>
              <Link to="/" className="text-sm text-brand-700 hover:underline">Run another</Link>
            </div>
          )}
        </section>

        {/* Right: live browser frames */}
        <aside className="lg:col-span-3 space-y-4">
          <h2 className="serif text-lg font-bold text-gray-900">🌐 Live browser sessions</h2>
          <BrowserFrame
            url={ETSY_URLS[persona] ?? ETSY_URLS.jenny}
            title="Actionbook · Etsy"
            active={marketBusy || evidenceCards.length > 0}
          >
            {evidenceCards.filter((c) => c.source === 'etsy').length === 0 ? (
              <p className="text-gray-400 italic">Waiting for Actionbook session…</p>
            ) : (
              <ul className="space-y-1.5">
                {evidenceCards
                  .filter((c) => c.source === 'etsy')
                  .map((c) => (
                    <li key={c.id} className="border-b border-gray-100 pb-1.5">
                      <div className="text-sm font-medium text-gray-800 truncate">{c.title}</div>
                      <div className="text-xs text-gray-500">
                        ${c.observed_price_usd.toFixed(0)} · {c.observed_volume_signal}
                      </div>
                    </li>
                  ))}
              </ul>
            )}
          </BrowserFrame>

          <BrowserFrame
            url={LAW_URLS[persona] ?? LAW_URLS.jenny}
            title="Bright Data · State law"
            active={complianceBusy || checks.some((c) => c.legal_citation_text)}
          >
            {checks.find((c) => c.legal_citation_text) ? (
              <div className="text-xs text-gray-700 whitespace-pre-line leading-relaxed">
                {checks.find((c) => c.legal_citation_text)?.legal_citation_text}
              </div>
            ) : (
              <p className="text-gray-400 italic">Waiting for compliance scrape…</p>
            )}
          </BrowserFrame>

          <div className="card p-3 text-xs text-gray-500">
            <div className="flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-300'}`} />
              <span>{connected ? 'streaming via SSE' : 'connecting…'}</span>
            </div>
            <div className="font-mono mt-1">{events.length} events</div>
          </div>
        </aside>
      </div>
    </div>
  );
}
