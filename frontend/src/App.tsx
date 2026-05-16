import { Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import SponsorBar from './components/SponsorBar';
import Home from './pages/Home';
import Run from './pages/Run';
import History from './pages/History';

export default function App() {
  return (
    <Routes>
      {/* Full-screen experience — no NavBar or SponsorBar chrome on the live run page */}
      <Route path="/run/:runId" element={<Run />} />
      {/* Every other route gets the standard shell */}
      <Route path="/*" element={<ShellLayout />} />
    </Routes>
  );
}

function ShellLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
      <SponsorBar />
    </div>
  );
}
