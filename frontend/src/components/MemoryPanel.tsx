import type { CrossUserPattern } from '../types';

export default function MemoryPanel({ pattern }: { pattern: CrossUserPattern }) {
  const confidencePct = Math.round(pattern.confidence * 100);
  return (
    <article className="card p-5 border-brand-200 bg-gradient-to-br from-brand-50 to-white animate-slide-in">
      <header className="flex items-center gap-2 mb-3">
        <span className="text-2xl">🧠</span>
        <div>
          <h3 className="font-bold text-gray-900">Cross-user pattern</h3>
          <p className="text-xs text-gray-500">surfaced live via Evermind query</p>
        </div>
      </header>
      <p className="text-sm text-gray-800 leading-relaxed mb-4">
        {pattern.pattern_text}
      </p>
      <div>
        <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
          <span>Confidence</span>
          <span className="font-mono">{confidencePct}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-brand-400 to-brand-600 transition-all"
            style={{ width: `${confidencePct}%` }}
          />
        </div>
      </div>
      {pattern.supporting_run_ids.length > 0 && (
        <div className="text-xs text-gray-500 mt-3">
          From runs: {pattern.supporting_run_ids.slice(0, 4).map((id) => (
            <span key={id} className="font-mono bg-white px-1.5 py-0.5 rounded ml-1">{id.slice(-6)}</span>
          ))}
        </div>
      )}
    </article>
  );
}
