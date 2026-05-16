const SPONSORS = [
  { name: 'AgentField', role: 'Orchestration', url: 'https://agentfield.ai' },
  { name: 'Bright Data', role: 'Live web scraping', url: 'https://brightdata.com' },
  { name: 'Actionbook', role: 'Browser actions', url: 'https://actionbook.dev' },
  { name: 'Evermind', role: 'Memory OS', url: 'https://evermind.ai' },
  { name: 'Butterbase', role: 'Product backend', url: 'https://butterbase.ai' },
  { name: 'Qwen Cloud', role: 'Primary LLM', url: 'https://qwencloud.com' },
  { name: 'Z.ai', role: 'Fallback LLM (GLM-5.1)', url: 'https://docs.z.ai' },
  { name: 'TokenRouter', role: 'LLM routing', url: 'https://tokenrouter.com' },
  { name: 'Zeabur', role: 'Deployment', url: 'https://zeabur.com' },
];

export default function SponsorBar() {
  return (
    <footer className="border-t border-brand-100 mt-12 py-8 bg-white/60">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-xs uppercase tracking-widest text-gray-500 mb-3 text-center">
          Built on the Agent Forge stack — every tool load-bearing
        </div>
        <ul className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
          {SPONSORS.map((s) => (
            <li key={s.name}>
              <a
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="text-sm text-gray-600 hover:text-brand-700"
                title={s.role}
              >
                {s.name}
              </a>
            </li>
          ))}
        </ul>
        <p className="text-xs text-center text-gray-400 mt-4">
          Mom's Saheli · Agent Forge AI Hackathon · San Francisco · May 16 2026
        </p>
      </div>
    </footer>
  );
}
