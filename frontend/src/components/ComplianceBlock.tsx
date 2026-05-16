import clsx from 'clsx';
import type { ComplianceCheck, Opportunity } from '../types';

interface Props {
  check: ComplianceCheck;
  opportunity?: Opportunity;
}

export default function ComplianceBlock({ check, opportunity }: Props) {
  const isBlock = check.verdict === 'BLOCK';
  const isWarn = check.verdict === 'WARN';
  return (
    <article
      className={clsx(
        'rounded-xl p-4 border-2 animate-slide-in shadow-sm',
        isBlock && 'border-red-400 bg-red-50',
        isWarn && 'border-yellow-400 bg-yellow-50',
        !isBlock && !isWarn && 'border-green-300 bg-green-50',
      )}
    >
      <header className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>
            {isBlock ? '🛑' : isWarn ? '⚠️' : '✅'}
          </span>
          <div>
            <h3
              className={clsx(
                'font-bold',
                isBlock && 'text-red-800',
                isWarn && 'text-yellow-800',
                !isBlock && !isWarn && 'text-green-800',
              )}
            >
              {check.verdict}
            </h3>
            {opportunity && (
              <p className="text-sm text-gray-800 mt-0.5">{opportunity.title}</p>
            )}
          </div>
        </div>
        <span className="text-xs text-gray-500 font-mono">{check.opportunity_id}</span>
      </header>

      {check.block_reason && (
        <p className={clsx('text-sm leading-snug mb-3', isBlock ? 'text-red-900' : 'text-gray-700')}>
          {check.block_reason}
        </p>
      )}

      {check.legal_citation_text && (
        <details className="bg-white/70 rounded-lg p-3 mt-2 text-sm">
          <summary className="cursor-pointer font-semibold text-gray-800">
            📜 Cited law (scraped live via Bright Data)
          </summary>
          <p className="mt-2 text-gray-700 leading-relaxed">{check.legal_citation_text}</p>
          {check.legal_citation_source_url && (
            <a
              href={check.legal_citation_source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-block mt-2 text-xs text-brand-700 hover:text-brand-900 underline"
            >
              View source page →
            </a>
          )}
        </details>
      )}

      {check.constraint_math_reasons.length > 0 && (
        <ul className="text-xs text-gray-600 mt-2 flex flex-wrap gap-2">
          {check.constraint_math_reasons.map((r, i) => (
            <li key={i} className="bg-white/60 px-2 py-0.5 rounded">
              {r}
            </li>
          ))}
        </ul>
      )}
    </article>
  );
}
