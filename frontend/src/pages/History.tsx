import { useEffect, useState } from 'react';
import type { RunSummary } from '../types';

export default function History() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/runs')
      .then((r) => r.json())
      .then((d) => setRuns(d.runs ?? []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <header className="mb-6">
        <h1 className="serif text-3xl font-bold text-gray-900">Run history</h1>
        <p className="text-gray-600 mt-1">
          Persisted via <strong>Butterbase</strong>. Every run is auditable.
        </p>
      </header>

      {loading && <p className="text-gray-500">Loading…</p>}

      {!loading && runs.length === 0 && (
        <div className="card p-8 text-center">
          <p className="text-gray-600 mb-3">No runs yet.</p>
          <a href="/" className="text-brand-700 font-semibold hover:underline">Start with Jenny →</a>
        </div>
      )}

      {runs.length > 0 && (
        <div className="card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-brand-50 text-left">
              <tr>
                <th className="px-4 py-3 font-semibold">When</th>
                <th className="px-4 py-3 font-semibold">Persona</th>
                <th className="px-4 py-3 font-semibold">Winner</th>
                <th className="px-4 py-3 font-semibold">Launch page</th>
                <th className="px-4 py-3 font-semibold">Duration</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {runs.map((r) => (
                <tr key={r.run_id} className="hover:bg-brand-50/40">
                  <td className="px-4 py-3 text-gray-600 font-mono text-xs">
                    {new Date(r.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 font-semibold">{r.persona_display_name}</td>
                  <td className="px-4 py-3 text-gray-700">{r.winner_offer_name ?? '—'}</td>
                  <td className="px-4 py-3">
                    {r.launch_url ? (
                      <a
                        href={r.launch_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-brand-700 hover:text-brand-900 hover:underline"
                      >
                        View →
                      </a>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">{(r.duration_ms / 1000).toFixed(1)}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
