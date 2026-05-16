import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import type { RunSummary } from '../types';

export default function History() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/runs')
      .then((r) => r.json())
      .then((d) => setRuns(d.runs ?? []))
      .catch((e) => setError(e?.message ?? 'load failed'))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-12">
      <header className="mb-10">
        <div className="eyebrow mb-3">Audit trail</div>
        <h1 className="serif text-display-sm font-bold text-ink-950 leading-tight">
          Run history
        </h1>
        <p className="text-ink-600 mt-3 text-lg max-w-2xl">
          Every run is persisted via <strong className="text-ink-900">Butterbase</strong>. The launch pages stay live —
          shareable URLs, real artifacts.
        </p>
      </header>

      {loading && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="skeleton h-16 rounded-xl" />
          ))}
        </div>
      )}

      {error && !loading && (
        <div className="surface p-6 text-center text-red-700 bg-red-50 border-red-200">
          <p className="font-semibold mb-1">Couldn't load runs</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {!loading && !error && runs.length === 0 && (
        <div className="surface p-12 text-center">
          <div className="grid place-items-center w-16 h-16 rounded-full bg-brand-100 text-brand-700 text-3xl mx-auto mb-4">
            🌱
          </div>
          <p className="text-ink-700 mb-2 text-lg font-semibold">No runs yet.</p>
          <p className="text-sm text-ink-500 mb-5">Start with one of the two preset moms.</p>
          <Link to="/" className="btn-accent">
            Start with Jenny
            <span aria-hidden>→</span>
          </Link>
        </div>
      )}

      {runs.length > 0 && (
        <div className="surface overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left bg-ink-50 border-b border-ink-100">
                  <Th>When</Th>
                  <Th>Persona</Th>
                  <Th>Winner offer</Th>
                  <Th>Launch page</Th>
                  <Th className="text-right">Duration</Th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-100">
                {runs.map((r) => (
                  <tr key={r.run_id} className="hover:bg-brand-50/40 transition-colors">
                    <td className="px-5 py-4 text-ink-600 font-mono text-xs whitespace-nowrap">
                      {new Date(r.created_at).toLocaleString()}
                    </td>
                    <td className="px-5 py-4 font-semibold text-ink-900">{r.persona_display_name}</td>
                    <td className="px-5 py-4 text-ink-700">{r.winner_offer_name ?? <em className="text-ink-400">—</em>}</td>
                    <td className="px-5 py-4">
                      {r.launch_url ? (
                        <a
                          href={r.launch_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-brand-700 hover:text-brand-900 font-semibold"
                        >
                          View page
                          <span aria-hidden>↗</span>
                        </a>
                      ) : <em className="text-ink-400">—</em>}
                    </td>
                    <td className="px-5 py-4 text-right text-ink-500 text-xs font-mono whitespace-nowrap">
                      {(r.duration_ms / 1000).toFixed(1)}s
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function Th({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th className={`px-5 py-3 font-semibold text-[11px] uppercase tracking-eyebrow text-ink-600 ${className}`}>
      {children}
    </th>
  );
}
