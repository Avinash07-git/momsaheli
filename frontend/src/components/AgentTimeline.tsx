import clsx from 'clsx';
import type { AgentEvent } from '../types';

const AGENTS = [
  { id: 'profile', label: 'Profile Agent', emoji: '👤', sponsor: 'Qwen' },
  { id: 'market_scout', label: 'Market Scout', emoji: '🔎', sponsor: 'Bright Data + Actionbook' },
  { id: 'reality_compliance', label: 'Reality & Compliance', emoji: '⚖️', sponsor: 'Bright Data' },
  { id: 'launch', label: 'Launch Agent', emoji: '🚀', sponsor: 'Actionbook + Butterbase' },
  { id: 'memory', label: 'Memory Agent', emoji: '🧠', sponsor: 'Evermind' },
] as const;

type Status = 'idle' | 'running' | 'done' | 'error';

function statusFor(agentId: string, events: AgentEvent[]): Status {
  const mine = events.filter((e) => e.agent === agentId);
  if (mine.some((e) => e.type === 'agent_error')) return 'error';
  if (mine.length === 0) return 'idle';
  // Done markers per agent
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
    <div className="card p-5">
      <h2 className="serif text-lg font-bold mb-4 text-gray-900 flex items-center gap-2">
        🤖 Agent swarm
        <span className="text-xs font-normal text-gray-500">(via AgentField)</span>
      </h2>
      <ol className="space-y-3">
        {AGENTS.map((a, i) => {
          const s = statusFor(a.id, events);
          return (
            <li
              key={a.id}
              className={clsx(
                'flex items-start gap-3 p-3 rounded-lg border transition-all',
                s === 'idle' && 'border-gray-100 bg-gray-50/50',
                s === 'running' && 'border-brand-300 bg-brand-50 shadow-sm',
                s === 'done' && 'border-green-200 bg-green-50/50',
                s === 'error' && 'border-red-300 bg-red-50',
              )}
            >
              <div className="text-2xl leading-none">{a.emoji}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-400 font-mono">{i + 1}</span>
                  <span className="font-semibold text-gray-900">{a.label}</span>
                </div>
                <div className="text-xs text-gray-500 mt-0.5">{a.sponsor}</div>
              </div>
              <span
                className={clsx(
                  'pill',
                  s === 'idle' && 'pill-idle',
                  s === 'running' && 'pill-running',
                  s === 'done' && 'pill-done',
                  s === 'error' && 'pill-error',
                )}
              >
                {s === 'running' && <span className="w-1.5 h-1.5 bg-brand-600 rounded-full" />}
                {s}
              </span>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
