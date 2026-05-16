import { useEffect, useState } from 'react';
import clsx from 'clsx';

interface Props {
  url: string;
  title: string;
  active: boolean;
  /** When present, renders a live Actionbook session iframe instead of children. */
  liveUrl?: string | null;
  /** Fallback when liveUrl absent: static screenshot URL from Actionbook. */
  screenshotUrl?: string | null;
}

/**
 * Simulated Chromium browser frame — gives the judge that "we're driving a real
 * browser on stage" feeling while we're in fixture/Tavily mode. When Actionbook
 * lands, swap the inner content with a live session iframe.
 */
export default function BrowserFrame({
  url,
  title,
  active,
  liveUrl,
  screenshotUrl,
  children,
}: React.PropsWithChildren<Props>) {
  const [pulse, setPulse] = useState(false);
  useEffect(() => {
    if (active) {
      setPulse(true);
      const t = setTimeout(() => setPulse(false), 1400);
      return () => clearTimeout(t);
    }
  }, [active, url]);

  return (
    <div className={clsx(
      'rounded-2xl border bg-white overflow-hidden transition-all duration-300',
      active
        ? 'border-brand-300 shadow-lift'
        : 'border-ink-200 opacity-80'
    )}>
      {/* Chrome chrome */}
      <div className="bg-gradient-to-b from-ink-100 to-ink-50 border-b border-ink-200 px-3 py-2.5">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-red-400/80 ring-1 ring-red-500/20" />
            <span className="w-3 h-3 rounded-full bg-amber-400/80 ring-1 ring-amber-500/20" />
            <span className="w-3 h-3 rounded-full bg-emerald-400/80 ring-1 ring-emerald-500/20" />
          </div>
          <div className={clsx(
            'flex-1 flex items-center gap-2 bg-white rounded-md px-3 py-1 text-[11px] font-mono truncate transition-all border',
            pulse
              ? 'border-brand-300 bg-brand-50/60 ring-2 ring-brand-200'
              : 'border-ink-200 text-ink-700',
          )}>
            <LockIcon active={active} />
            <span className="truncate">{url}</span>
          </div>
        </div>
        <div className="flex items-center justify-between mt-1.5 text-[10px] text-ink-500">
          <span className="font-semibold uppercase tracking-eyebrow">{title}</span>
          {active && (
            <span className="inline-flex items-center gap-1 text-emerald-700">
              <span className="status-dot-live" />
              live
            </span>
          )}
        </div>
      </div>

      {/* Content viewport — live Actionbook iframe if liveUrl, else screenshot, else children */}
      <div className="relative max-h-72 overflow-hidden bg-white">
        {liveUrl ? (
          <iframe
            src={liveUrl}
            title={`Actionbook live session — ${title}`}
            className="w-full h-72 border-0"
            sandbox="allow-same-origin allow-scripts allow-forms"
            referrerPolicy="no-referrer"
          />
        ) : screenshotUrl ? (
          <img
            src={screenshotUrl}
            alt={`Actionbook session screenshot — ${title}`}
            className="w-full h-72 object-cover object-top"
          />
        ) : (
          <div className="max-h-72 overflow-y-auto scrollbar-thin">
            <div className="p-3 text-sm">{children}</div>
            <div className="pointer-events-none sticky bottom-0 h-6 -mt-6 bg-gradient-to-t from-white to-transparent" />
          </div>
        )}
      </div>
    </div>
  );
}

function LockIcon({ active }: { active: boolean }) {
  return (
    <svg viewBox="0 0 16 16" className={clsx('w-3 h-3 shrink-0', active ? 'text-emerald-600' : 'text-ink-400')} fill="currentColor" aria-hidden>
      <path d="M11 7V5a3 3 0 0 0-6 0v2H4a1 1 0 0 0-1 1v5a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V8a1 1 0 0 0-1-1h-1zm-5 0V5a2 2 0 1 1 4 0v2H6z" />
    </svg>
  );
}
