import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import clsx from 'clsx';

interface PresetButtonsProps {
  disabled?: boolean;
}

const PRESETS = [
  {
    id: 'jenny',
    emoji: '👩🏽‍🍳',
    title: 'Run Jenny',
    role: 'Daycare aide',
    state: 'California',
    chips: [
      { label: '$600/mo gap', tone: 'brand' as const },
      { label: '5 hr/wk', tone: 'neutral' as const },
      { label: 'loves cooking', tone: 'neutral' as const },
    ],
    arc: 'Daily Tiffin ranks #1 by $ — then gets BLOCKED by California cottage-food law. Pivots to a legal winner.',
  },
  {
    id: 'jessica',
    emoji: '💻',
    title: 'Run Jessica',
    role: 'Customer-service rep (WFH)',
    state: 'Texas',
    chips: [
      { label: '$400/mo gap', tone: 'brand' as const },
      { label: '3 hr/wk', tone: 'neutral' as const },
      { label: 'digital + async only', tone: 'neutral' as const },
    ],
    arc: 'Digital-only world — Etsy printable lunchbox kit wins clean, zero compliance hits.',
  },
];

export default function PresetButtons({ disabled }: PresetButtonsProps) {
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
      console.error(e);
      setError(`Could not start run: ${e?.message ?? e}`);
      setBusy(null);
    }
  }

  return (
    <div>
      <div className="grid md:grid-cols-2 gap-5">
        {PRESETS.map((p) => {
          const isBusy = busy === p.id;
          return (
            <button
              key={p.id}
              disabled={disabled || !!busy}
              onClick={() => go(p.id)}
              className={clsx(
                'surface-lift relative overflow-hidden text-left p-7 group',
                'disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0',
                isBusy && 'shadow-glow-brand'
              )}
            >
              {/* Subtle warm wash on hover */}
              <div className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 bg-mesh-amber" aria-hidden />

              <div className="relative">
                <div className="flex items-start gap-4 mb-4">
                  <div className="grid place-items-center w-14 h-14 rounded-2xl bg-gradient-to-br from-cream to-brand-100 text-3xl shadow-soft shrink-0">
                    {p.emoji}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="eyebrow mb-1">{p.role} · {p.state}</div>
                    <div className="serif text-2xl font-bold text-ink-900 leading-tight">
                      {isBusy ? (
                        <span className="inline-flex items-center gap-2">
                          <Spinner />
                          Starting…
                        </span>
                      ) : p.title}
                    </div>
                  </div>
                  <span
                    className="shrink-0 grid place-items-center w-9 h-9 rounded-full border border-ink-200 text-ink-700 group-hover:bg-ink-900 group-hover:text-white group-hover:border-ink-900 transition-all"
                    aria-hidden
                  >→</span>
                </div>

                <div className="flex flex-wrap gap-1.5 mb-4">
                  {p.chips.map((c) => (
                    <span key={c.label} className={c.tone === 'brand' ? 'pill-brand' : 'pill-neutral'}>
                      {c.label}
                    </span>
                  ))}
                </div>

                <p className="text-sm text-ink-600 leading-relaxed border-t border-ink-100 pt-3">
                  <span className="eyebrow-muted mr-2">Story arc</span>
                  {p.arc}
                </p>
              </div>
            </button>
          );
        })}
      </div>
      {error && (
        <p className="mt-4 text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-3">
          {error}
        </p>
      )}
    </div>
  );
}

function Spinner() {
  return (
    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeOpacity="0.25" strokeWidth="3" />
      <path d="M22 12a10 10 0 0 1-10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
    </svg>
  );
}
