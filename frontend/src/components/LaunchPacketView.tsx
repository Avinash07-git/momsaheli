import type { LaunchPacket } from '../types';

interface Props {
  packet: LaunchPacket;
  publishedUrl?: string | null;
}

export default function LaunchPacketView({ packet, publishedUrl }: Props) {
  return (
    <article className="card p-6 animate-slide-in">
      <header className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="serif text-2xl font-bold text-brand-800">{packet.offer_name}</h2>
          <p className="text-gray-600 mt-1">{packet.offer_tagline}</p>
        </div>
        <div className="text-right shrink-0">
          <div className="text-2xl font-bold text-brand-700">${packet.price_usd.toFixed(2)}</div>
          <div className="text-xs text-gray-500">{packet.unit}</div>
        </div>
      </header>

      {publishedUrl && (
        <a
          href={publishedUrl}
          target="_blank"
          rel="noreferrer"
          className="block bg-brand-50 border border-brand-300 rounded-lg p-3 mb-4 hover:bg-brand-100 transition"
        >
          <div className="text-xs text-brand-700 font-semibold uppercase tracking-wide mb-1">
            🌐 Live launch page (Butterbase-hosted)
          </div>
          <div className="font-mono text-sm text-brand-900 break-all">{publishedUrl}</div>
        </a>
      )}

      <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-line mb-4">
        {packet.description_markdown}
      </div>

      <div className="bg-brand-50/60 border border-brand-100 rounded-lg p-3 mb-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-brand-800 mb-1">
          Target customer
        </div>
        <div className="text-sm text-gray-800">{packet.target_customer}</div>
      </div>

      <details className="mb-3">
        <summary className="cursor-pointer font-semibold text-gray-900">
          📣 Outreach drafts ({packet.outreach_drafts.length})
        </summary>
        <ul className="mt-2 space-y-2">
          {packet.outreach_drafts.map((d, i) => (
            <li key={i} className="bg-gray-50 rounded p-3">
              <div className="text-xs uppercase tracking-wide text-gray-500 mb-1">{d.channel}</div>
              {d.subject && <div className="text-sm font-semibold mb-1">{d.subject}</div>}
              <div className="text-sm text-gray-700 whitespace-pre-line">{d.body_markdown}</div>
            </li>
          ))}
        </ul>
      </details>

      <details>
        <summary className="cursor-pointer font-semibold text-gray-900">
          📅 7-day launch plan
        </summary>
        <ol className="mt-2 space-y-1">
          {packet.day_plan.map((item) => (
            <li key={item.day} className="flex items-start gap-3 text-sm bg-gray-50 rounded p-2">
              <div className="font-bold text-brand-700 shrink-0 w-12">Day {item.day}</div>
              <div className="flex-1 text-gray-800">{item.action}</div>
              <div className="text-xs text-gray-500 shrink-0">{item.estimated_minutes}m</div>
            </li>
          ))}
        </ol>
      </details>
    </article>
  );
}
