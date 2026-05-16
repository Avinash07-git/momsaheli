import { Link } from 'react-router-dom';

export default function NavBar() {
  return (
    <header className="border-b border-brand-100 bg-white/80 backdrop-blur sticky top-0 z-10">
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="text-2xl" aria-hidden>🌸</span>
          <div>
            <div className="serif text-xl font-bold text-brand-800 leading-tight">Mom's Saheli</div>
            <div className="text-xs text-gray-500 -mt-0.5">the friend she can't afford</div>
          </div>
        </Link>
        <nav className="flex items-center gap-6 text-sm">
          <Link to="/" className="text-gray-700 hover:text-brand-700">Home</Link>
          <Link to="/history" className="text-gray-700 hover:text-brand-700">Run history</Link>
          <a href="https://github.com/Avinash07-git/momsaheli" target="_blank" rel="noreferrer"
             className="text-gray-700 hover:text-brand-700">GitHub</a>
        </nav>
      </div>
    </header>
  );
}
