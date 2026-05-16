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

export default function Home() {
  return (
    <>
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-100 via-cream to-white" aria-hidden />
        <div className="relative max-w-7xl mx-auto px-6 py-16 md:py-24">
          <div className="max-w-3xl">
            <p className="text-sm uppercase tracking-widest text-brand-700 font-semibold mb-3">
              Agent Forge AI Hackathon · San Francisco · May 16 2026
            </p>
            <h1 className="serif text-5xl md:text-7xl font-bold text-gray-900 leading-tight mb-5">
              The friend every working mom can <span className="text-brand-700">finally</span> afford.
            </h1>
            <p className="text-xl text-gray-700 leading-relaxed mb-8 max-w-2xl">
              A consultant costs $2,000. A bookkeeper, a lawyer, a marketer—each $200/hr.
              Mom's Saheli is the <strong>agent swarm that does all of it</strong>: live market intel,
              live regulatory check, real launch page, cross-user learning. Today: working moms.
              Tomorrow: every constrained earner.
            </p>
            <div className="flex flex-wrap items-center gap-3 text-sm text-gray-700">
              <span className="pill bg-brand-100 text-brand-800">5 agents</span>
              <span className="pill bg-brand-100 text-brand-800">9 sponsor tools</span>
              <span className="pill bg-brand-100 text-brand-800">Real cited regulations</span>
              <span className="pill bg-brand-100 text-brand-800">Live launch pages</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="max-w-7xl mx-auto px-6 py-12">
        <h2 className="serif text-3xl font-bold text-gray-900 mb-2">
          She's not short on effort. She's short on <span className="text-brand-700">margin</span>.
        </h2>
        <p className="text-gray-600 mb-6">Every number below has a source. No inflated TAM.</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {STATS.map((s) => (
            <StatCard key={s.label} {...s} />
          ))}
        </div>
      </section>

      {/* Run the swarm */}
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="max-w-3xl mx-auto">
          <h2 className="serif text-3xl font-bold text-gray-900 mb-2 text-center">
            Run the swarm
          </h2>
          <p className="text-gray-600 mb-8 text-center">
            Two real moms. Same five agents. Completely different output. Proves nothing is hardcoded.
          </p>
          <PresetButtons />
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-7xl mx-auto px-6 py-12">
        <div className="card p-8 bg-gradient-to-br from-white to-brand-50">
          <h2 className="serif text-2xl font-bold text-gray-900 mb-6 text-center">How it works</h2>
          <ol className="grid md:grid-cols-5 gap-4 text-sm">
            {[
              { n: 1, agent: 'Profile', text: 'Normalize skills, hours, budget, hard constraints' },
              { n: 2, agent: 'Market Scout', text: 'Live Etsy + Bright Data: 8 ranked income paths' },
              { n: 3, agent: 'Reality & Compliance', text: 'Block illegal options with real cited law' },
              { n: 4, agent: 'Launch', text: 'Offer + copy + 7-day plan + live published page' },
              { n: 5, agent: 'Memory', text: 'Persist + surface cross-user learned pattern' },
            ].map((s) => (
              <li key={s.n} className="flex flex-col gap-2">
                <div className="text-brand-700 font-bold text-3xl serif">{s.n}</div>
                <div className="font-semibold text-gray-900">{s.agent}</div>
                <div className="text-gray-600 leading-snug">{s.text}</div>
              </li>
            ))}
          </ol>
        </div>
      </section>
    </>
  );
}
