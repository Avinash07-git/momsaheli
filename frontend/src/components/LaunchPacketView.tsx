import type { LaunchPacket } from '../types';

interface Props {
  packet: LaunchPacket;
  publishedUrl?: string | null;
}

export default function LaunchPacketView({ packet, publishedUrl }: Props) {
  return (
    <article className="relative rounded-2xl overflow-hidden bg-white border border-ink-200 shadow-lift animate-slide-up">
      {/* Hero band */}
      <div className="relative overflow-hidden bg-gradient-to-br from-brand-50 via-cream to-rose-50 p-6 md:p-8 border-b border-brand-100">
        <div className="absolute -top-16 -right-16 w-64 h-64 bg-brand-200/40 rounded-full blur-3xl" aria-hidden />
        <div className="absolute -bottom-16 -left-16 w-64 h-64 bg-rose-200/30 rounded-full blur-3xl" aria-hidden />

        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <span className="pill bg-white/70 backdrop-blur text-brand-800 border border-brand-200">
              🚀 Launch packet
            </span>
            <span className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500">
              written by Gemini · ready to ship
            </span>
          </div>

          <div className="flex items-start justify-between gap-6 flex-wrap">
            <div className="min-w-0 max-w-2xl">
              <h2 className="serif text-3xl md:text-4xl font-bold text-ink-950 leading-tight tracking-tight">
                {packet.offer_name}
              </h2>
              <p className="text-ink-700 mt-2 text-lg leading-relaxed">
                {packet.offer_tagline}
              </p>
            </div>
            <div className="text-right shrink-0">
              <div className="serif text-5xl font-bold text-gradient-warm tabular-nums leading-none">
                ${packet.price_usd.toFixed(0)}
              </div>
              <div className="text-xs text-ink-500 mt-1 uppercase tracking-eyebrow font-semibold">
                {packet.unit}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Published URL (HERO) */}
      {publishedUrl && (
        <a
          href={publishedUrl}
          target="_blank"
          rel="noreferrer"
          className="block bg-ink-950 text-white p-5 group hover:bg-ink-900 transition-colors"
        >
          <div className="flex items-center justify-between gap-4">
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <span className="status-dot-live" />
                <span className="text-[10px] uppercase tracking-eyebrow font-bold text-brand-300">
                  Live landing page · Butterbase-hosted
                </span>
              </div>
              <div className="font-mono text-sm text-white break-all leading-tight">
                {publishedUrl}
              </div>
            </div>
            <span className="grid place-items-center w-10 h-10 rounded-full bg-white/10 group-hover:bg-brand-500 group-hover:text-ink-950 transition-all shrink-0">
              ↗
            </span>
          </div>
        </a>
      )}

      {/* Body */}
      <div className="p-6 md:p-8 space-y-6">
        <div className="prose prose-sm max-w-none text-ink-700 whitespace-pre-line leading-relaxed">
          {packet.description_markdown}
        </div>

        <div className="rounded-xl bg-cream border border-brand-100 p-4">
          <div className="eyebrow mb-1">Target customer</div>
          <div className="text-sm text-ink-800 leading-relaxed">{packet.target_customer}</div>
        </div>

        <details className="rounded-xl border border-ink-200 overflow-hidden group">
          <summary className="flex items-center justify-between gap-3 px-4 py-3 cursor-pointer bg-ink-50 hover:bg-ink-100 transition-colors list-none">
            <span className="font-semibold text-ink-900 inline-flex items-center gap-2">
              📣 Outreach drafts
              <span className="pill-neutral">{packet.outreach_drafts.length}</span>
            </span>
            <span className="text-ink-400 group-open:rotate-180 transition-transform">▾</span>
          </summary>
          <ul className="divide-y divide-ink-100">
            {packet.outreach_drafts.map((d, i) => (
              <li key={i} className="p-4">
                <div className="eyebrow-muted mb-1.5">{d.channel.replace(/_/g, ' ')}</div>
                {d.subject && <div className="text-sm font-semibold text-ink-900 mb-1.5">{d.subject}</div>}
                <div className="text-sm text-ink-700 whitespace-pre-line leading-relaxed">{d.body_markdown}</div>
              </li>
            ))}
          </ul>
        </details>

        <details className="rounded-xl border border-ink-200 overflow-hidden group">
          <summary className="flex items-center justify-between gap-3 px-4 py-3 cursor-pointer bg-ink-50 hover:bg-ink-100 transition-colors list-none">
            <span className="font-semibold text-ink-900 inline-flex items-center gap-2">
              📅 7-day launch plan
              <span className="pill-neutral">{packet.day_plan.length} days</span>
            </span>
            <span className="text-ink-400 group-open:rotate-180 transition-transform">▾</span>
          </summary>
          <ol className="divide-y divide-ink-100">
            {packet.day_plan.map((item) => (
              <li key={item.day} className="flex items-start gap-4 p-3.5">
                <div className="grid place-items-center w-10 h-10 rounded-lg bg-brand-50 text-brand-700 font-serif font-bold shrink-0 text-sm border border-brand-100">
                  D{item.day}
                </div>
                <div className="flex-1 text-sm text-ink-800 leading-snug">{item.action}</div>
                <div className="text-xs text-ink-500 font-mono shrink-0">{item.estimated_minutes}m</div>
              </li>
            ))}
          </ol>
        </details>
      </div>
    </article>
  );
}
