import clsx from 'clsx';
import type { EvidenceCard as EvidenceCardT } from '../types';

const SOURCE_BADGE: Record<string, { label: string; bg: string; text: string }> = {
  etsy:                 { label: 'Etsy',           bg: 'bg-orange-100',   text: 'text-orange-800' },
  poshmark:             { label: 'Poshmark',       bg: 'bg-pink-100',     text: 'text-pink-800' },
  craigslist:           { label: 'Craigslist',     bg: 'bg-purple-100',   text: 'text-purple-800' },
  nextdoor:             { label: 'Nextdoor',       bg: 'bg-emerald-100',  text: 'text-emerald-800' },
  outschool:            { label: 'Outschool',      bg: 'bg-sky-100',      text: 'text-sky-800' },
  facebook_marketplace: { label: 'FB Marketplace', bg: 'bg-blue-100',     text: 'text-blue-800' },
  facebook_group:       { label: 'FB Group',       bg: 'bg-blue-100',     text: 'text-blue-800' },
  castiron:             { label: 'Castiron',       bg: 'bg-amber-100',    text: 'text-amber-900' },
  instagram:            { label: 'Instagram',      bg: 'bg-fuchsia-100',  text: 'text-fuchsia-800' },
};

export default function EvidenceCard({ card }: { card: EvidenceCardT }) {
  const badge = SOURCE_BADGE[card.source] ?? SOURCE_BADGE.etsy;
  return (
    <article className="surface-lift p-5 animate-slide-in group">
      <header className="flex items-start justify-between gap-3 mb-4">
        <h3 className="font-semibold text-ink-900 leading-snug">{card.title}</h3>
        <div className="flex flex-col items-end gap-1 shrink-0">
          <span className={clsx('pill', badge.bg, badge.text)}>{badge.label}</span>
          {card.live_scrape_ok && (
            <span className="pill bg-emerald-100 text-emerald-800">
              Live {card.live_scrape_provider ?? 'web'}
            </span>
          )}
        </div>
      </header>

      <div className="grid grid-cols-3 gap-3 mb-3">
        <Metric label="Listed price"  value={`$${card.observed_price_usd.toFixed(0)}`} />
        <Metric label="Est. net / mo" value={`$${card.estimated_net_monthly_usd}`} accent />
        <Metric label="First $ in"    value={`${card.time_to_first_dollar_days}d`} />
      </div>

      <div className="text-xs text-ink-600 italic">{card.observed_volume_signal}</div>

      {card.notes && (
        <div className="text-xs text-ink-500 mt-3 pt-3 border-t border-ink-100 leading-relaxed">
          {card.notes}
        </div>
      )}

      {card.source_url && (
        <a
          href={card.source_url}
          target="_blank"
          rel="noreferrer"
          className="inline-flex mt-3 text-xs font-semibold text-brand-700 hover:text-brand-900"
        >
          View live source
        </a>
      )}
    </article>
  );
}

function Metric({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500 mb-1">
        {label}
      </div>
      <div className={clsx(
        'font-serif text-lg font-bold tabular-nums',
        accent ? 'text-emerald-700' : 'text-ink-900'
      )}>
        {value}
      </div>
    </div>
  );
}
