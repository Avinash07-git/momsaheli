import { useEffect, useState } from 'react';
import clsx from 'clsx';

interface Props {
  url: string;
  title: string;
  active: boolean;
}

/**
 * Simulated browser frame. In Phase 1 this is a faux Chrome chrome around a
 * scrolling list of search results / state-law text — it visually conveys
 * "we are driving a real browser via Actionbook" without needing the live session.
 *
 * Phase 2: replace the inner content with a live Actionbook session iframe
 * or a polled screenshot stream.
 */
export default function BrowserFrame({ url, title, active, children }: React.PropsWithChildren<Props>) {
  const [pulse, setPulse] = useState(false);
  useEffect(() => {
    if (active) {
      setPulse(true);
      const t = setTimeout(() => setPulse(false), 1200);
      return () => clearTimeout(t);
    }
  }, [active, url]);

  return (
    <div className={clsx(
      'rounded-lg border bg-white shadow-sm overflow-hidden transition-all',
      active ? 'border-brand-400 shadow-md' : 'border-gray-200 opacity-70',
    )}>
      {/* Chrome */}
      <div className="bg-gray-100 border-b border-gray-200 px-3 py-2 flex items-center gap-2">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-400" />
          <span className="w-2.5 h-2.5 rounded-full bg-yellow-400" />
          <span className="w-2.5 h-2.5 rounded-full bg-green-400" />
        </div>
        <div className={clsx(
          'flex-1 bg-white rounded px-3 py-1 text-xs font-mono text-gray-700 truncate transition-all',
          pulse && 'bg-brand-50 ring-2 ring-brand-300',
        )}>
          {url}
        </div>
        <span className="text-xs text-gray-500 hidden md:inline">{title}</span>
      </div>
      {/* Content */}
      <div className="p-3 max-h-72 overflow-y-auto bg-white text-sm">
        {children}
      </div>
    </div>
  );
}
