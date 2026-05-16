const SPONSORS = [
  { name: 'AgentField',  role: 'Multi-agent orchestration',     url: 'https://agentfield.ai' },
  { name: 'Bright Data', role: 'Live web intelligence',         url: 'https://brightdata.com' },
  { name: 'Actionbook',  role: 'Browser actions on real sites', url: 'https://actionbook.dev' },
  { name: 'Evermind',    role: 'Long-term memory OS',           url: 'https://evermind.ai' },
  { name: 'Butterbase',  role: 'Product backend & hosting',     url: 'https://butterbase.ai' },
  { name: 'Qwen Cloud',  role: 'Primary reasoning LLM',         url: 'https://qwencloud.com' },
  { name: 'Z.ai',        role: 'Fallback LLM (GLM-5.1)',        url: 'https://docs.z.ai' },
  { name: 'TokenRouter', role: 'LLM cascade routing',           url: 'https://tokenrouter.com' },
  { name: 'Zeabur',      role: 'Cloud deployment',              url: 'https://zeabur.com' },
];

export default function SponsorBar() {
  return (
    <footer className="border-t border-ink-100 mt-24 bg-white">
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-3 gap-10 mb-10">
          {/* Brand block */}
          <div>
            <div className="flex items-center gap-3 mb-3">
              <span className="grid place-items-center w-9 h-9 rounded-xl bg-gradient-to-br from-brand-200 to-brand-500 text-xl shadow-soft">
                🌸
              </span>
              <div className="serif text-lg font-bold text-ink-900">Mom's Saheli</div>
            </div>
            <p className="text-sm text-ink-600 leading-relaxed max-w-xs">
              Built for the <strong className="text-ink-900">Agent Forge AI Hackathon</strong> — San Francisco · May 16 2026.
              Solo build. Open source. MIT-licensed.
            </p>
          </div>

          {/* Sponsor stack */}
          <div className="md:col-span-2">
            <div className="eyebrow-muted mb-4">Built on the Agent Forge stack — every tool load-bearing</div>
            <ul className="grid grid-cols-2 md:grid-cols-3 gap-x-6 gap-y-3">
              {SPONSORS.map((s) => (
                <li key={s.name}>
                  <a
                    href={s.url}
                    target="_blank"
                    rel="noreferrer"
                    className="group block"
                  >
                    <div className="text-sm font-semibold text-ink-800 group-hover:text-brand-700 transition-colors">
                      {s.name}
                    </div>
                    <div className="text-[11px] text-ink-500 leading-snug">{s.role}</div>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pt-6 border-t border-ink-100 flex flex-wrap items-center justify-between gap-2 text-xs text-ink-500">
          <span>© 2026 · Built with love for every mom doing the math at 11pm.</span>
          <span className="font-mono">v0.1.0</span>
        </div>
      </div>
    </footer>
  );
}
