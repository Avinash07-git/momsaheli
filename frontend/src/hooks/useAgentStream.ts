import { useEffect, useRef, useState } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import type { AgentEvent } from '../types';

export interface SwarmState {
  events: AgentEvent[];
  connected: boolean;
  complete: boolean;
  error: string | null;
}

/**
 * Consumes the /api/stream/{run_id} SSE endpoint and accumulates events.
 * Returns the running event log + connection state.
 */
export function useAgentStream(runId: string | null): SwarmState {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [complete, setComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const aborter = useRef<AbortController | null>(null);

  useEffect(() => {
    if (!runId) return;
    setEvents([]);
    setConnected(false);
    setComplete(false);
    setError(null);

    const ctrl = new AbortController();
    aborter.current = ctrl;

    fetchEventSource(`/api/stream/${runId}`, {
      signal: ctrl.signal,
      openWhenHidden: true,
      onopen: async (res) => {
        if (res.ok) {
          setConnected(true);
        } else {
          setError(`stream opened with ${res.status}`);
        }
      },
      onmessage: (msg) => {
        if (!msg.data) return;
        try {
          const parsed = JSON.parse(msg.data) as AgentEvent;
          setEvents((prev) => [...prev, parsed]);
          if (parsed.type === 'run_complete') {
            setComplete(true);
            ctrl.abort();
          }
        } catch (e) {
          console.warn('bad event', msg.data, e);
        }
      },
      onerror: (err) => {
        setError(String(err));
        throw err; // stops retries
      },
    }).catch(() => {
      // expected on abort
    });

    return () => ctrl.abort();
  }, [runId]);

  return { events, connected, complete, error };
}
