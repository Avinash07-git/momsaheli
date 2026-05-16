import type { CrossUserPattern } from '../types';

export default function MemoryPanel({ pattern }: { pattern: CrossUserPattern }) {
  const confidencePct = Math.round(pattern.confidence * 100);
  return (
    <article className="relative overflow-hidden rounded-2xl border border-brand-200 bg-gradient-to-br from-brand-50 via-cream to-white p-6 shadow-lift animate-slide-in">
      <div className="absolute -top-12 -right-12 w-48 h-48 bg-brand-200/30 rounded-full blur-3xl" aria-hidden />

      <header className="relative flex items-start gap-3 mb-4">
        <div className="grid place-items-center w-11 h-11 rounded-xl bg-gradient-to-br from-brand-200 to-brand-400 text-xl shadow-soft">
          🧠
        </div>
        <div className="flex-1">
          <h3 className="font-serif text-lg font-bold text-ink-900 leading-tight">
            Cross-user pattern detected
          </h3>
          <p className="text-[11px] uppercase tracking-eyebrow font-semibold text-ink-500 mt-0.5">
            surfaced live via Evermind query
          </p>
        </div>
      </header>

      <blockquote className="relative text-base text-ink-800 leading-relaxed mb-5 font-serif italic border-l-2 border-brand-300 pl-4">
        "{pattern.pattern_text}"
      </blockquote>

      <div className="relative">
        <div className="flex items-center justify-between text-xs mb-2">
          <span className="font-semibold uppercase tracking-eyebrow text-ink-600">
            Confidence
          </span>
          <span className="font-mono font-bold text-ink-900 tabular-nums">{confidencePct}%</span>
        </div>
        <div className="h-2 bg-white/80 rounded-full overflow-hidden border border-ink-100 shadow-inner">
          <div
            className="h-full bg-gradient-to-r from-brand-300 via-brand-500 to-brand-700 transition-all duration-700"
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>

      {pattern.supporting_run_ids.length > 0 && (
        <div className="relative mt-4 pt-4 border-t border-brand-100">
          <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500 mb-1.5">
            Supporting runs
          </div>
          <div className="flex flex-wrap gap-1.5">
            {pattern.supporting_run_ids.slice(0, 6).map((id) => (
              <span key={id} className="text-[11px] font-mono bg-white border border-ink-200 px-2 py-0.5 rounded-md text-ink-700">
                {id.slice(-8)}
              </span>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
