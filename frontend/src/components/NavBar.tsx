import { useEffect, useState } from 'react';
import { Link, NavLink } from 'react-router-dom';
import clsx from 'clsx';

interface Health {
  status: string;
  sponsors_configured?: { agentfield?: boolean };
}

// Convention: AgentField control plane dashboard. Override via env if needed.
const AF_DASHBOARD_URL =
  (import.meta as any).env?.VITE_AGENTFIELD_DASHBOARD_URL ?? 'http://localhost:8080/ui/';

export default function NavBar() {
  const [agentFieldLive, setAgentFieldLive] = useState(false);

  useEffect(() => {
    let alive = true;
    fetch('/health')
      .then((r) => (r.ok ? r.json() : null))
      .then((h: Health | null) => {
        if (alive && h?.sponsors_configured?.agentfield) setAgentFieldLive(true);
      })
      .catch(() => { /* silent — link just stays hidden */ });
    return () => { alive = false; };
  }, []);

  return (
    <header className="sticky top-0 z-30 border-b border-ink-100 bg-cream/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-6">
        {/* Logomark */}
        <Link to="/" className="flex items-center gap-3 group">
          <span
            className="grid place-items-center w-11 h-11 rounded-2xl bg-gradient-to-br from-brand-200 via-brand-300 to-brand-500 shadow-soft text-2xl group-hover:shadow-glow-brand transition-shadow"
            aria-hidden
          >
            🌸
          </span>
          <div className="leading-tight">
            <div className="serif text-xl font-bold text-ink-900 tracking-tight">
              Mom's Saheli
            </div>
            <div className="text-[11px] text-ink-500 font-medium">
              the friend every working mom can afford
            </div>
          </div>
        </Link>

        {/* Nav */}
        <nav className="hidden md:flex items-center gap-1 text-sm">
          <NavItem to="/" end>Home</NavItem>
          <NavItem to="/history">Run history</NavItem>

          {agentFieldLive && (
            <a
              href={AF_DASHBOARD_URL}
              target="_blank"
              rel="noreferrer"
              className="btn-ghost text-sm group"
              title="Live nested-execution waterfall via AgentField"
            >
              <span className="status-dot-live" />
              <span>Live workflow</span>
              <span className="text-ink-400 group-hover:text-ink-700 transition-colors" aria-hidden>↗</span>
            </a>
          )}

          <a
            href="https://github.com/Avinash07-git/momsaheli"
            target="_blank"
            rel="noreferrer"
            className="btn-ghost text-sm"
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="currentColor" aria-hidden>
              <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.92.58.11.79-.25.79-.55v-2.16c-3.2.7-3.88-1.37-3.88-1.37-.52-1.32-1.27-1.67-1.27-1.67-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.18 1.76 1.18 1.02 1.75 2.68 1.25 3.34.96.1-.74.4-1.25.72-1.54-2.55-.29-5.24-1.28-5.24-5.7 0-1.26.45-2.29 1.18-3.1-.12-.29-.51-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11.04 11.04 0 0 1 5.78 0c2.2-1.49 3.17-1.18 3.17-1.18.62 1.59.23 2.76.11 3.05.74.81 1.18 1.84 1.18 3.1 0 4.44-2.69 5.4-5.26 5.69.41.35.78 1.05.78 2.11v3.13c0 .31.21.67.8.55A11.5 11.5 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z" />
            </svg>
            GitHub
          </a>
        </nav>
      </div>
    </header>
  );
}

function NavItem({ to, end, children }: { to: string; end?: boolean; children: React.ReactNode }) {
  return (
    <NavLink
      to={to}
      end={end}
      className={({ isActive }) =>
        clsx(
          'px-3 py-1.5 rounded-lg font-medium transition-colors',
          isActive
            ? 'text-ink-950 bg-ink-100/80'
            : 'text-ink-600 hover:text-ink-900 hover:bg-ink-100/60'
        )
      }
    >
      {children}
    </NavLink>
  );
}
