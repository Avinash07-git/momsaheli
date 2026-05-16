import { useNavigate } from 'react-router-dom';
import { useState } from 'react';

interface PresetButtonsProps {
  disabled?: boolean;
}

const PRESETS = [
  {
    id: 'jenny',
    title: 'Run Jenny',
    subtitle: 'Daycare aide · CA · $600/mo gap · 5 hr/wk · loves cooking',
    emoji: '👩🏽\u200d🍳',
  },
  {
    id: 'jessica',
    title: 'Run Jessica',
    subtitle: 'CS rep (WFH) · TX · $400/mo gap · 3 hr/wk · digital + async only',
    emoji: '💻',
  },
];

export default function PresetButtons({ disabled }: PresetButtonsProps) {
  const navigate = useNavigate();
  const [busy, setBusy] = useState<string | null>(null);

  async function go(personaId: string) {
    if (busy) return;
    setBusy(personaId);
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
    } catch (e) {
      console.error(e);
      alert(`Could not start run: ${e}`);
      setBusy(null);
    }
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {PRESETS.map((p) => (
        <button
          key={p.id}
          disabled={disabled || !!busy}
          onClick={() => go(p.id)}
          className="card card-hover p-6 text-left disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          <div className="flex items-center gap-4">
            <div className="text-4xl">{p.emoji}</div>
            <div className="flex-1">
              <div className="serif text-2xl font-bold text-brand-800 group-hover:text-brand-900">
                {busy === p.id ? 'Starting…' : p.title}
              </div>
              <div className="text-sm text-gray-600 mt-1">{p.subtitle}</div>
            </div>
            <div className="text-brand-600 group-hover:translate-x-1 transition-transform" aria-hidden>→</div>
          </div>
        </button>
      ))}
    </div>
  );
}
