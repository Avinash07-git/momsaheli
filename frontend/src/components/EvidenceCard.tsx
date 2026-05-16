import clsx from 'clsx';
import type { EvidenceCard as EvidenceCardT } from '../types';

const SOURCE_BADGE: Record<string, { label: string; bg: string; text: string }> = {
  etsy: { label: 'Etsy', bg: 'bg-orange-100', text: 'text-orange-800' },
  poshmark: { label: 'Poshmark', bg: 'bg-pink-100', text: 'text-pink-800' },
  craigslist: { label: 'Craigslist', bg: 'bg-purple-100', text: 'text-purple-800' },
  nextdoor: { label: 'Nextdoor', bg: 'bg-green-100', text: 'text-green-800' },
  outschool: { label: 'Outschool', bg: 'bg-blue-100', text: 'text-blue-800' },
  facebook_marketplace: { label: 'FB Marketplace', bg: 'bg-blue-100', text: 'text-blue-800' },
  facebook_group: { label: 'FB Group', bg: 'bg-blue-100', text: 'text-blue-800' },
  castiron: { label: 'Castiron', bg: 'bg-amber-100', text: 'text-amber-900' },
  instagram: { label: 'Instagram', bg: 'bg-fuchsia-100', text: 'text-fuchsia-800' },
};

export default function EvidenceCard({ card }: { card: EvidenceCardT }) {
  const badge = SOURCE_BADGE[card.source] ?? SOURCE_BADGE.etsy;
  return (
    <article className="card card-hover p-4 animate-slide-in">
      <header className="flex items-start justify-between gap-3 mb-2">
        <h3 className="font-semibold text-gray-900 leading-tight">{card.title}</h3>
        <span className={clsx('pill', badge.bg, badge.text)}>{badge.label}</span>
      </header>
      <div className="grid grid-cols-3 gap-3 text-sm mb-2">
        <div>
          <div className="text-xs text-gray-500">Price</div>
          <div className="font-semibold">${card.observed_price_usd.toFixed(0)}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">Est. net / mo</div>
          <div className="font-semibold text-green-700">${card.estimated_net_monthly_usd}</div>
        </div>
        <div>
          <div className="text-xs text-gray-500">First $ in</div>
          <div className="font-semibold">{card.time_to_first_dollar_days}d</div>
        </div>
      </div>
      <div className="text-xs text-gray-600 italic">{card.observed_volume_signal}</div>
      {card.notes && (
        <div className="text-xs text-gray-500 mt-2 border-t border-gray-100 pt-2">{card.notes}</div>
      )}
    </article>
  );
}
