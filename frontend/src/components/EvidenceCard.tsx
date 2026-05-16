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

const PLACEHOLDER_URL_MARKERS = [
  '/listing/example',
  'example-',
  'example_',
];

export default function EvidenceCard({ card }: { card: EvidenceCardT }) {
  const badge = SOURCE_BADGE[card.source] ?? SOURCE_BADGE.etsy;
  const sourceLink = getAvailableSourceLink(card);
  const CardTag = sourceLink ? 'a' : 'article';

  return (
    <CardTag
      {...(sourceLink
        ? {
            href: sourceLink.url,
            target: '_blank',
            rel: 'noopener noreferrer',
            title: sourceLink.title,
          }
        : {})}
      className={clsx(
        'surface-lift block p-5 animate-slide-in group',
        sourceLink && 'cursor-pointer focus-visible:ring-2 focus-visible:ring-brand-400 focus-visible:ring-offset-2'
      )}
    >
      <header className="flex items-start justify-between gap-3 mb-4">
        <h3 className={clsx(
          'font-semibold text-ink-900 leading-snug transition-colors',
          sourceLink && 'group-hover:text-brand-700'
        )}>
          {card.title}
        </h3>
        <span className={clsx('pill shrink-0', badge.bg, badge.text)}>{badge.label}</span>
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

      {sourceLink && (
        <span
          className="mt-4 inline-flex items-center gap-1.5 text-xs font-semibold text-brand-700 hover:text-brand-900"
        >
          {sourceLink.label}
          <span aria-hidden>↗</span>
        </span>
      )}
    </CardTag>
  );
}

function getAvailableSourceLink(card: EvidenceCardT): { url: string; label: string; title: string } | null {
  const originalUrl = card.source_url?.trim();
  if (originalUrl && !isPlaceholderUrl(originalUrl)) {
    return {
      url: originalUrl,
      label: 'Open listing',
      title: 'Open original market source',
    };
  }

  const query = encodeURIComponent(card.title);
  const sourceQuery = encodeURIComponent(`${card.title} ${SOURCE_BADGE[card.source]?.label ?? card.source}`);

  const searchUrlBySource: Record<EvidenceCardT['source'], string> = {
    etsy: `https://www.etsy.com/search?q=${query}`,
    poshmark: `https://poshmark.com/search?query=${query}`,
    craigslist: `https://sfbay.craigslist.org/search/sss?query=${query}`,
    nextdoor: `https://www.google.com/search?q=${sourceQuery}`,
    outschool: `https://outschool.com/search?q=${query}`,
    facebook_marketplace: `https://www.google.com/search?q=${sourceQuery}`,
    facebook_group: `https://www.google.com/search?q=${sourceQuery}`,
    castiron: `https://www.google.com/search?q=${sourceQuery}`,
    instagram: `https://www.google.com/search?q=${sourceQuery}`,
  };

  return {
    url: searchUrlBySource[card.source],
    label: 'Search live source',
    title: 'Open a live search for this market signal',
  };
}

function isPlaceholderUrl(url: string): boolean {
  return PLACEHOLDER_URL_MARKERS.some((marker) => url.includes(marker));
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
