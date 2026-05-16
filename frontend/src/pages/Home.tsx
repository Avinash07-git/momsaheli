import PresetButtons from '../components/PresetButtons';
import StatCard from '../components/StatCard';

const STATS = [
  {
    number: '7.3M',
    label: 'single moms in America',
    source: 'Center for American Progress',
    sourceUrl: 'https://www.americanprogress.org/article/single-mothers-and-poverty/',
  },
  {
    number: '75%',
    label: 'are already working — most full-time',
    source: 'CAP',
    sourceUrl: 'https://www.americanprogress.org/article/single-mothers-and-poverty/',
  },
  {
    number: '$40K',
    label: 'median income, working single mom',
    source: 'CAP',
    sourceUrl: 'https://www.americanprogress.org/article/single-mothers-and-poverty/',
  },
  {
    number: '35%',
    label: 'of that income is eaten by childcare',
    source: 'Child Care Aware',
    sourceUrl: 'https://www.childcareaware.org/',
  },
];

const HOW_STEPS = [
  { n: 1, agent: 'Profile',              text: 'Normalize skills, hours, budget, hard constraints.',                        sponsor: 'Qwen' },
  { n: 2, agent: 'Market Scout',         text: 'Live Etsy + Bright Data: 6–10 ranked income paths.',                        sponsor: 'Bright Data + Actionbook' },
  { n: 3, agent: 'Reality & Compliance', text: 'Block illegal options with the actual cited state law.',                    sponsor: 'Bright Data' },
  { n: 4, agent: 'Launch',               text: 'Offer + copy + 7-day plan + a real published landing page.',                sponsor: 'Actionbook + Butterbase' },
  { n: 5, agent: 'Memory',               text: 'Persist trajectory + surface a cross-user pattern.',                         sponsor: 'Evermind' },
];

export default function Home() {
  return (
    <>
      {/* ───────────────────── HERO ───────────────────── */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-hero-warm" aria-hidden />
        {/* Decorative blur orbs */}
        <div className="absolute -top-32 -right-32 w-96 h-96 rounded-full bg-brand-300/30 blur-3xl" aria-hidden />
        <div className="absolute bottom-0 -left-32 w-96 h-96 rounded-full bg-rose-300/20 blur-3xl" aria-hidden />

        <div className="relative max-w-7xl mx-auto px-6 pt-20 pb-24 md:pt-28 md:pb-32">
          <div className="grid lg:grid-cols-12 gap-12 items-center">
            {/* Headline column */}
            <div className="lg:col-span-7 animate-slide-up">
              <div className="inline-flex items-center gap-2 mb-6 px-3 py-1.5 rounded-full bg-white/70 border border-ink-200 backdrop-blur-sm shadow-soft">
                <span className="status-dot-live" />
                <span className="text-xs font-semibold text-ink-700">
                  Live at Agent Forge AI · San Francisco · May 16 2026
                </span>
              </div>

              <h1 className="serif font-bold text-ink-950 mb-6 text-display-md md:text-display-lg">
                The friend every working mom can{' '}
                <span className="text-gradient-warm italic">finally</span>{' '}
                afford.
              </h1>

              <p className="text-xl text-ink-700 leading-relaxed mb-8 max-w-2xl">
                A consultant costs <strong className="text-ink-900">$2,000</strong>. A bookkeeper, a lawyer, a marketer — each $200/hr.
                Mom's Saheli is the <strong className="text-ink-900">agent swarm that does all of it</strong>:
                live market intel, cited regulatory check, a real published launch page, and cross-user learning.
              </p>

              <div className="flex flex-wrap items-center gap-3 mb-8">
                <a href="#run" className="btn-accent">
                  Watch a live run
                  <span aria-hidden>→</span>
                </a>
                <a href="#how" className="btn-outline">How it works</a>
              </div>

              <div className="flex flex-wrap items-center gap-2 text-xs">
                <Badge>5 agents</Badge>
                <Badge>9 sponsor tools</Badge>
                <Badge>Cited regulations</Badge>
                <Badge>Real launch pages</Badge>
              </div>
            </div>

            {/* Preview card column */}
            <div className="lg:col-span-5 animate-slide-up" style={{ animationDelay: '120ms' }}>
              <HeroPreviewCard />
            </div>
          </div>
        </div>
      </section>

      {/* ───────────────────── STATS ───────────────────── */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="max-w-3xl mb-10">
          <div className="eyebrow mb-3">The margin problem</div>
          <h2 className="serif text-display-sm font-bold text-ink-950 leading-tight">
            She's not short on effort. She's short on{' '}
            <span className="text-gradient-warm italic">margin</span>.
          </h2>
          <p className="text-ink-600 mt-4 text-lg max-w-2xl">
            Every number below is cited. No inflated TAM, no marketing math — just the gap.
          </p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-5">
          {STATS.map((s) => (
            <StatCard key={s.label} {...s} />
          ))}
        </div>
      </section>

      {/* ───────────────────── RUN ───────────────────── */}
      <section id="run" className="relative max-w-7xl mx-auto px-6 py-20">
        <div className="max-w-3xl mx-auto text-center mb-12">
          <div className="eyebrow mb-3 justify-center">Try it now</div>
          <h2 className="serif text-display-sm font-bold text-ink-950 leading-tight mb-4">
            Run the swarm.
          </h2>
          <p className="text-ink-600 text-lg leading-relaxed">
            Two real moms. <strong className="text-ink-900">Same five agents.</strong> Completely different output.
            Proves nothing is hardcoded — it's the regulation, the constraints, and the math doing the work.
          </p>
        </div>
        <div className="max-w-4xl mx-auto">
          <PresetButtons />
        </div>
      </section>

      {/* ───────────────────── HOW ───────────────────── */}
      <section id="how" className="max-w-7xl mx-auto px-6 py-20">
        <div className="surface p-10 md:p-14 bg-gradient-to-br from-white to-brand-50/60 relative overflow-hidden">
          <div className="absolute -top-20 -right-20 w-72 h-72 rounded-full bg-brand-200/30 blur-3xl" aria-hidden />
          <div className="relative">
            <div className="max-w-2xl mb-12">
              <div className="eyebrow mb-3">How it works</div>
              <h2 className="serif text-display-sm font-bold text-ink-950 leading-tight">
                Five agents. One mom. <span className="text-gradient-warm italic">One published page.</span>
              </h2>
            </div>

            <ol className="grid md:grid-cols-5 gap-6 md:gap-2 relative">
              {/* connecting line on desktop */}
              <div className="hidden md:block absolute top-6 left-[10%] right-[10%] h-px bg-gradient-to-r from-transparent via-brand-300 to-transparent" aria-hidden />
              {HOW_STEPS.map((s) => (
                <li key={s.n} className="relative flex flex-col items-start">
                  <div className="grid place-items-center w-12 h-12 rounded-2xl serif font-bold text-2xl bg-white border border-brand-200 text-brand-700 shadow-soft mb-4 relative z-10">
                    {s.n}
                  </div>
                  <div className="font-semibold text-ink-900 mb-1">{s.agent}</div>
                  <div className="text-sm text-ink-600 leading-snug mb-2">{s.text}</div>
                  <div className="text-[10px] font-semibold uppercase tracking-eyebrow text-ink-400">
                    {s.sponsor}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>
    </>
  );
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white border border-ink-200 text-ink-700 font-medium shadow-soft">
      <span className="w-1 h-1 rounded-full bg-brand-500" />
      {children}
    </span>
  );
}

/* Tiny preview card on the hero — gives the eye somewhere to land + previews the product */
function HeroPreviewCard() {
  return (
    <div className="relative">
      {/* Floating glow */}
      <div className="absolute -inset-4 bg-gradient-to-br from-brand-200/40 via-rose-200/30 to-transparent blur-2xl rounded-3xl" aria-hidden />
      <div className="relative surface p-5 shadow-lift">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="status-dot-live" />
            <span className="text-xs font-semibold text-ink-700">live agent run · jenny</span>
          </div>
          <span className="text-[10px] font-mono text-ink-400">run_a93f1c…</span>
        </div>
        <ul className="space-y-2.5">
          <PreviewRow agent="Profile"               status="done"    label="normalized · 5 hr/wk · CA" />
          <PreviewRow agent="Market Scout"          status="done"    label="6 opportunities ranked" />
          <PreviewRow agent="Reality & Compliance"  status="block"   label="3 BLOCKs · CA H&S §114365" />
          <PreviewRow agent="Launch"                status="running" label="generating offer + page…" />
          <PreviewRow agent="Memory"                status="idle"    label="awaiting trajectory" />
        </ul>
        <div className="mt-4 pt-4 border-t border-ink-100 flex items-center justify-between text-xs">
          <span className="text-ink-500">via AgentField</span>
          <span className="font-mono text-ink-700">22.3s elapsed</span>
        </div>
      </div>
    </div>
  );
}

function PreviewRow({ agent, status, label }: { agent: string; status: 'idle'|'running'|'done'|'block'; label: string }) {
  const tone =
    status === 'done'    ? 'bg-emerald-500'
  : status === 'running' ? 'bg-brand-500 animate-pulse'
  : status === 'block'   ? 'bg-red-500'
  :                        'bg-ink-300';
  return (
    <li className="flex items-center gap-3 text-sm">
      <span className={`w-2 h-2 rounded-full ${tone}`} />
      <span className="font-semibold text-ink-800 w-44 shrink-0">{agent}</span>
      <span className="text-ink-500 truncate">{label}</span>
    </li>
  );
}
