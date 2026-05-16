import clsx from 'clsx';
import type { ComplianceCheck, Opportunity } from '../types';

interface Props {
  check: ComplianceCheck;
  opportunity?: Opportunity;
}

/**
 * The BLOCK is the demo's shock moment. We give it a courtroom-grade treatment:
 * heavy left rail, bold verdict badge, prominent cited-law card.
 * PASS / WARN get subtler styling — by design, the eye lands on BLOCKs.
 */
export default function ComplianceBlock({ check, opportunity }: Props) {
  const isBlock = check.verdict === 'BLOCK';
  const isWarn  = check.verdict === 'WARN';

  return (
    <article
      className={clsx(
        'relative rounded-2xl border bg-white overflow-hidden animate-slide-in transition-all',
        isBlock && 'border-red-300 shadow-glow-danger ring-1 ring-red-200/60',
        isWarn  && 'border-amber-300 shadow-lift',
        !isBlock && !isWarn && 'border-emerald-200 shadow-soft',
      )}
    >
      {/* Left accent rail */}
      <div className={clsx(
        'absolute left-0 top-0 bottom-0 w-1.5',
        isBlock && 'bg-gradient-to-b from-red-400 to-red-700',
        isWarn  && 'bg-gradient-to-b from-amber-400 to-amber-600',
        !isBlock && !isWarn && 'bg-gradient-to-b from-emerald-400 to-emerald-600',
      )} />

      <div className="p-5 pl-7">
        <header className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-3 min-w-0">
            <VerdictIcon verdict={check.verdict} />
            <div className="min-w-0">
              <div className="flex items-center gap-2 mb-0.5">
                <h3 className={clsx(
                  'font-serif text-lg font-bold tracking-tight',
                  isBlock && 'text-red-800',
                  isWarn  && 'text-amber-800',
                  !isBlock && !isWarn && 'text-emerald-800',
                )}>
                  {check.verdict}
                </h3>
                {isBlock && (
                  <span className="pill bg-red-100 text-red-800 uppercase">illegal</span>
                )}
              </div>
              {opportunity && (
                <p className="text-sm text-ink-800 truncate">
                  <span className="text-ink-500">opportunity:</span> {opportunity.title}
                </p>
              )}
            </div>
          </div>
          <span className="text-[10px] text-ink-400 font-mono shrink-0">{check.opportunity_id}</span>
        </header>

        {check.block_reason && (
          <p className={clsx(
            'text-sm leading-relaxed mb-4',
            isBlock ? 'text-ink-900 font-medium' : 'text-ink-700'
          )}>
            {check.block_reason}
          </p>
        )}

        {/* Cited law — the trophy moment */}
        {check.legal_citation_text && (
          <div className={clsx(
            'rounded-xl border p-4 mb-3',
            isBlock ? 'border-red-200 bg-red-50/50' : 'border-ink-200 bg-ink-50/60'
          )}>
            <div className="flex items-center gap-2 mb-2">
              <CitationIcon />
              <div className="text-[10px] uppercase tracking-eyebrow font-bold text-ink-700">
                Cited law · scraped live via Bright Data
              </div>
            </div>
            <p className="text-sm text-ink-800 leading-relaxed font-serif italic">
              "{check.legal_citation_text}"
            </p>
            {check.legal_citation_source_url && (
              <a
                href={check.legal_citation_source_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 mt-3 text-xs font-semibold text-brand-700 hover:text-brand-900 transition-colors"
              >
                View source page
                <span aria-hidden>↗</span>
              </a>
            )}
          </div>
        )}

        {check.constraint_math_reasons.length > 0 && (
          <div className="mt-3">
            <div className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500 mb-2">
              Constraint math
            </div>
            <ul className="flex flex-wrap gap-1.5">
              {check.constraint_math_reasons.map((r, i) => (
                <li key={i} className="pill-neutral">{r}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}

function VerdictIcon({ verdict }: { verdict: ComplianceCheck['verdict'] }) {
  const isBlock = verdict === 'BLOCK';
  const isWarn  = verdict === 'WARN';
  return (
    <div className={clsx(
      'grid place-items-center w-11 h-11 rounded-xl shrink-0',
      isBlock && 'bg-red-100 text-red-700',
      isWarn  && 'bg-amber-100 text-amber-700',
      !isBlock && !isWarn && 'bg-emerald-100 text-emerald-700',
    )}>
      <svg viewBox="0 0 24 24" className="w-6 h-6" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden>
        {isBlock && (
          <>
            <circle cx="12" cy="12" r="10" />
            <path d="M4.93 4.93l14.14 14.14" />
          </>
        )}
        {isWarn && (
          <>
            <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
            <line x1="12" y1="9" x2="12" y2="13" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </>
        )}
        {!isBlock && !isWarn && (
          <>
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
            <polyline points="22 4 12 14.01 9 11.01" />
          </>
        )}
      </svg>
    </div>
  );
}

function CitationIcon() {
  return (
    <svg viewBox="0 0 24 24" className="w-3.5 h-3.5 text-ink-600" fill="currentColor" aria-hidden>
      <path d="M9 7H6a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h2v.5C8 16 7 17 5 17v2c4 0 6-2.5 6-6V9a2 2 0 0 0-2-2zm10 0h-3a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h2v.5c0 1.5-1 2.5-3 2.5v2c4 0 6-2.5 6-6V9a2 2 0 0 0-2-2z" />
    </svg>
  );
}
