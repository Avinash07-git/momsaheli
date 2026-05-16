import { useMemo, useState } from 'react';
import clsx from 'clsx';
import type { ActionCandidate, ActionExecutionResult, ActivationPlan } from '../types';

interface Props {
  plan: ActivationPlan | null;
  runId?: string;
}

export default function ActivationPlanView({ plan, runId }: Props) {
  const [result, setResult] = useState<ActionExecutionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const recommended = useMemo(() => {
    if (!plan) return null;
    return (
      plan.actions.find((a) => a.id === plan.recommended_first_action_id)
      ?? plan.actions[0]
      ?? null
    );
  }, [plan]);

  if (!plan) {
    return (
      <div className="rounded-xl border border-dashed border-[#e7e5e4] bg-white p-14 text-center mt-2">
        <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse inline-block mb-3" />
        <p className="text-[14px] text-[#78716c] max-w-sm mx-auto">
          Customer leads and approval-gated actions appear after Launch finishes...
        </p>
      </div>
    );
  }

  async function execute(action: ActionCandidate) {
    if (!runId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const response = await fetch(`/api/runs/${runId}/actions/${action.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approved: true,
          submit_or_post: action.execution_mode === 'post_after_review',
        }),
      });
      if (!response.ok) {
        throw new Error(await response.text());
      }
      setResult(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <article className="rounded-2xl bg-white border border-ink-200 shadow-lift overflow-hidden animate-slide-up">
      <div className="p-6 md:p-8 border-b border-ink-100 bg-gradient-to-br from-emerald-50 via-white to-amber-50">
        <div className="flex items-center gap-2 mb-3">
          <span className="pill bg-white/80 text-emerald-800 border border-emerald-200">
            Customer Activation
          </span>
          <span className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500">
            approval gated
          </span>
        </div>
        <h2 className="serif text-3xl md:text-4xl font-bold text-ink-950 leading-tight tracking-tight">
          First customer path
        </h2>
        <p className="text-ink-700 mt-2 text-sm leading-relaxed max-w-2xl">
          {plan.summary}
        </p>
      </div>

      <div className="p-6 md:p-8 space-y-6">
        {recommended && (
          <section className="rounded-xl border border-emerald-200 bg-emerald-50/70 p-5">
            <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
              <div className="min-w-0">
                <div className="eyebrow mb-1">Recommended first customer move</div>
                <h3 className="font-serif text-2xl font-bold text-emerald-950 leading-tight">
                  {recommended.title}
                </h3>
                <p className="text-sm text-emerald-900 mt-1">
                  {recommended.destination_name}
                </p>
              </div>
              <div className="flex flex-wrap items-center gap-2 shrink-0">
                <ExecutionBadge mode={recommended.execution_mode} />
                <span className="pill bg-white text-emerald-800 border border-emerald-200">
                  {(recommended.priority_score * 100).toFixed(0)} score
                </span>
              </div>
            </div>

            <div className="grid sm:grid-cols-3 gap-3 mb-4">
              <MiniStat label="Expected" value={recommended.expected_outcome} />
              <MiniStat label="Effort" value={`${recommended.effort_minutes} min`} />
              <MiniStat label="Risk" value={recommended.risk_level} />
            </div>

            <div className="rounded-xl bg-white border border-emerald-100 p-4 mb-4">
              <div className="eyebrow-muted mb-1">Why this action won</div>
              <p className="text-sm text-ink-800 leading-relaxed">{recommended.reason}</p>
            </div>

            {recommended.draft_text && (
              <div className="rounded-xl bg-white border border-ink-200 p-4 mb-4">
                <div className="eyebrow-muted mb-2">Draft message</div>
                <p className="text-sm text-ink-800 whitespace-pre-line leading-relaxed">
                  {recommended.draft_text}
                </p>
              </div>
            )}

            {recommended.form_fields && (
              <div className="rounded-xl bg-white border border-ink-200 p-4 mb-4">
                <div className="eyebrow-muted mb-2">Form fields preview</div>
                <dl className="divide-y divide-ink-100">
                  {Object.entries(recommended.form_fields).map(([key, value]) => (
                    <div key={key} className="py-2 grid sm:grid-cols-[150px_1fr] gap-2 text-sm">
                      <dt className="font-semibold text-ink-600">{key.replace(/_/g, ' ')}</dt>
                      <dd className="text-ink-800 leading-relaxed">{value}</dd>
                    </div>
                  ))}
                </dl>
              </div>
            )}

            <div className="flex flex-col sm:flex-row sm:items-center gap-3">
              <button
                type="button"
                disabled={!runId || loading}
                onClick={() => execute(recommended)}
                className={clsx(
                  'btn-primary text-[13px] justify-center',
                  (!runId || loading) && 'opacity-60 cursor-not-allowed',
                )}
              >
                {loading ? 'Working...' : buttonLabel(recommended.execution_mode)}
              </button>
              {recommended.destination_url && (
                <a
                  href={recommended.destination_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs font-semibold text-emerald-800 hover:text-emerald-950"
                >
                  Review destination
                </a>
              )}
            </div>

            {result && (
              <div className="mt-4 rounded-xl border border-ink-200 bg-white p-4">
                <div className="eyebrow-muted mb-1">Action result</div>
                <p className="text-sm text-ink-800 leading-relaxed">
                  <span className="font-semibold uppercase">{result.status}</span> - {result.message}
                </p>
                {result.actionbook_session_id && (
                  <p className="font-mono text-xs text-ink-500 mt-2">{result.actionbook_session_id}</p>
                )}
                {result.error && <p className="text-xs text-red-700 mt-2">{result.error}</p>}
              </div>
            )}

            {error && (
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900">
                {error}
              </div>
            )}
          </section>
        )}

        <section>
          <div className="flex items-center justify-between gap-3 mb-3">
            <div>
              <div className="eyebrow mb-1">Customer leads</div>
              <h3 className="font-serif text-xl font-bold text-ink-950">Public paths and approved channels</h3>
            </div>
            <span className="pill-neutral">{plan.leads.length}</span>
          </div>
          <div className="space-y-3">
            {plan.leads.map((lead) => (
              <div key={lead.id} className="rounded-xl border border-ink-200 bg-white p-4">
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="min-w-0">
                    <div className="font-semibold text-ink-900 leading-snug">{lead.title}</div>
                    <div className="text-xs text-ink-500 mt-0.5">
                      {lead.source_type.replace(/_/g, ' ')} · {lead.provider}
                    </div>
                  </div>
                  <span className={clsx(
                    'pill shrink-0',
                    lead.live_source
                      ? 'bg-emerald-100 text-emerald-800'
                      : 'bg-amber-100 text-amber-800',
                  )}>
                    {lead.live_source ? 'live' : 'fallback'}
                  </span>
                </div>
                <p className="text-sm text-ink-700 leading-relaxed">{lead.why_relevant}</p>
                <p className="text-xs text-ink-500 mt-2">{lead.audience_match}</p>
                {lead.source_url && (
                  <a
                    href={lead.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex mt-2 text-xs font-semibold text-brand-700 hover:text-brand-900"
                  >
                    Open public source
                  </a>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-ink-200 bg-ink-50 p-4">
          <div className="eyebrow-muted mb-2">Safety notes</div>
          <ul className="space-y-1.5">
            {plan.safety_notes.map((note) => (
              <li key={note} className="text-sm text-ink-700 leading-relaxed">
                {note}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </article>
  );
}

function ExecutionBadge({ mode }: { mode: ActionCandidate['execution_mode'] }) {
  const label = {
    draft_only: 'Draft only',
    fill_no_submit: 'Fill, do not submit',
    post_after_review: 'Post after review',
  }[mode];
  return (
    <span className={clsx(
      'pill border',
      mode === 'draft_only' && 'bg-white text-ink-700 border-ink-200',
      mode === 'fill_no_submit' && 'bg-amber-100 text-amber-900 border-amber-200',
      mode === 'post_after_review' && 'bg-rose-100 text-rose-900 border-rose-200',
    )}>
      {label}
    </span>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white border border-emerald-100 p-3">
      <div className="text-[10px] font-bold uppercase tracking-[0.12em] text-ink-400 mb-1">
        {label}
      </div>
      <div className="text-sm text-ink-800 leading-snug">{value}</div>
    </div>
  );
}

function buttonLabel(mode: ActionCandidate['execution_mode']) {
  return {
    draft_only: 'Mark draft ready',
    fill_no_submit: 'Approve form fill preview',
    post_after_review: 'Approve this exact message',
  }[mode];
}
