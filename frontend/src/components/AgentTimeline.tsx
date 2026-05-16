import clsx from 'clsx';
import type { AgentEvent } from '../types';

const AGENTS = [
  { id: 'profile',            label: 'Profile Agent',         emoji: '👤', sponsor: 'Qwen' },
  { id: 'market_scout',       label: 'Market Scout',          emoji: '🔎', sponsor: 'Bright Data + Actionbook' },
  { id: 'reality_compliance', label: 'Reality & Compliance',  emoji: '⚖️', sponsor: 'Bright Data' },
  { id: 'launch',             label: 'Launch Agent',          emoji: '🚀', sponsor: 'Actionbook + Butterbase' },
  { id: 'memory',             label: 'Memory Agent',          emoji: '🧠', sponsor: 'Evermind' },
] as const;

type Status = 'idle' | 'running' | 'done' | 'error';

function statusFor(agentId: string, events: AgentEvent[]): Status {
  const mine = events.filter((e) => e.agent === agentId);
  if (mine.some((e) => e.type === 'agent_error')) return 'error';
  if (mine.length === 0) return 'idle';
  const doneMarker: Record<string, string> = {
    profile: 'profile_ready',
    market_scout: 'opportunities_ranked',
    reality_compliance: 'winner_selected',
    launch: 'launch_published',
    memory: 'memory_pattern',
  };
  const marker = doneMarker[agentId];
  if (marker && mine.some((e) => e.type === marker)) return 'done';
  return 'running';
}

interface Props {
  events: AgentEvent[];
}

export default function AgentTimeline({ events }: Props) {
  return (
    <div className="surface p-5">
      <div className="flex items-center justify-between mb-5">
        <h2 className="serif text-lg font-bold text-ink-900 flex items-center gap-2">
          Agent swarm
        </h2>
        <span className="text-[10px] uppercase tracking-eyebrow font-semibold text-ink-500">
          via AgentField
        </span>
      </div>

      <ol className="relative space-y-1">
        {/* Connector line */}
        <div className="absolute left-[18px] top-3 bottom-3 w-px bg-ink-200" aria-hidden />

        {AGENTS.map((a, i) => {
          const s = statusFor(a.id, events);
          return (
            <li key={a.id} className="relative pl-12 py-2.5 animate-slide-in" style={{ animationDelay: `${i * 60}ms` }}>
              {/* Node marker */}
              <div className={clsx(
                'absolute left-0 top-2.5 grid place-items-center w-9 h-9 rounded-full border-2 text-base bg-white transition-all z-10',
                s === 'idle'    && 'border-ink-200 text-ink-400 grayscale',
                s === 'running' && 'border-brand-400 text-brand-700 animate-pulse-ring shadow-glow-brand',
                s === 'done'    && 'border-emerald-400 text-emerald-700',
                s === 'error'   && 'border-red-400 text-red-700',
              )}>
                {s === 'done' ? '✓' : s === 'error' ? '!' : a.emoji}
              </div>

              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-ink-400">0{i + 1}</span>
                    <span className={clsx('font-semibold text-sm', s === 'idle' ? 'text-ink-500' : 'text-ink-900')}>
                      {a.label}
                    </span>
                  </div>
                  <div className="text-[11px] text-ink-500 mt-0.5">{a.sponsor}</div>
                </div>
                <StatusPill status={s} />
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

function StatusPill({ status }: { status: Status }) {
  if (status === 'idle')    return <span className="pill-neutral">idle</span>;
  if (status === 'running') return (
    <span className="pill-brand inline-flex items-center gap-1.5">
      <span className="w-1.5 h-1.5 rounded-full bg-brand-600 animate-pulse" />
      running
    </span>
  );
  if (status === 'done')    return <span className="pill-success">done</span>;
  return <span className="pill-danger">error</span>;
}
