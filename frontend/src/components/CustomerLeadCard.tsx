import clsx from 'clsx';
import type { CustomerLead } from '../types';

const SOURCE_BADGE: Record<CustomerLead['source'], { label: string; bg: string; text: string }> = {
  reddit:         { label: 'Reddit',       bg: 'bg-orange-100',  text: 'text-orange-800' },
  facebook_group: { label: 'FB Group',     bg: 'bg-blue-100',    text: 'text-blue-800' },
  nextdoor:       { label: 'Nextdoor',     bg: 'bg-emerald-100', text: 'text-emerald-800' },
  google:         { label: 'Search',       bg: 'bg-amber-100',   text: 'text-amber-900' },
  local_search:   { label: 'Local Search', bg: 'bg-teal-100',    text: 'text-teal-800' },
};

export default function CustomerLeadCard({ lead }: { lead: CustomerLead }) {
  const badge = SOURCE_BADGE[lead.source] ?? SOURCE_BADGE.google;
  const confidence = Math.round(lead.confidence * 100);

  return (
    <a
      href={lead.source_url}
      target="_blank"
      rel="noopener noreferrer"
      title="Open customer demand source"
      className="surface-lift block p-5 animate-slide-in group focus-visible:ring-2 focus-visible:ring-emerald-400 focus-visible:ring-offset-2"
    >
      <header className="flex items-start justify-between gap-3 mb-4">
        <div className="min-w-0">
          <h3 className="font-semibold text-ink-900 leading-snug group-hover:text-emerald-700 transition-colors">
            {lead.title}
          </h3>
          {lead.location_hint && (
            <div className="mt-1 text-[11px] font-medium text-ink-500">{lead.location_hint}</div>
          )}
        </div>
        <span className={clsx('pill shrink-0', badge.bg, badge.text)}>{badge.label}</span>
      </header>

      <div className="rounded-xl bg-emerald-50 border border-emerald-100 p-3 mb-3">
        <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-emerald-700 mb-1">
          Buyer intent
        </div>
        <p className="text-[13px] text-emerald-950 leading-relaxed">{lead.intent_signal}</p>
      </div>

      <div className="space-y-3">
        <Detail label="Why it matches" value={lead.match_reason} />
        <Detail label="Suggested outreach" value={lead.suggested_outreach} />
      </div>

      <div className="mt-4 pt-3 border-t border-ink-100 flex items-center justify-between text-xs">
        <span className="font-semibold text-emerald-700">Open lead source ↗</span>
        <span className="font-mono text-ink-500">{confidence}% match</span>
      </div>
    </a>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500 mb-1">{label}</div>
      <p className="text-xs text-ink-600 leading-relaxed">{value}</p>
    </div>
  );
}
