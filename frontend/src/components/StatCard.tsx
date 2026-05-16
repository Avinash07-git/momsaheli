interface StatCardProps {
  number: string;
  label: string;
  source: string;
  sourceUrl?: string;
}

export default function StatCard({ number, label, source, sourceUrl }: StatCardProps) {
  return (
    <div className="surface-lift p-6 animate-fade-in group">
      <div className="data-num text-5xl text-gradient-warm mb-2 leading-none">
        {number}
      </div>
      <div className="text-sm text-ink-800 leading-snug mb-3 font-medium">{label}</div>
      <div className="pt-3 border-t border-ink-100">
        {sourceUrl ? (
          <a
            href={sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="text-[11px] uppercase tracking-eyebrow font-semibold text-ink-500 hover:text-brand-700 transition-colors inline-flex items-center gap-1"
          >
            <span>Source: {source}</span>
            <span aria-hidden className="opacity-0 group-hover:opacity-100 transition-opacity">↗</span>
          </a>
        ) : (
          <span className="text-[11px] uppercase tracking-eyebrow font-semibold text-ink-500">
            Source: {source}
          </span>
        )}
      </div>
    </div>
  );
}
