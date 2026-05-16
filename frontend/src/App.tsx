import { Routes, Route } from 'react-router-dom';
import NavBar from './components/NavBar';
import SponsorBar from './components/SponsorBar';
import Home from './pages/Home';
import Run from './pages/Run';
import History from './pages/History';

export default function App() {
  return (
    <div className="min-h-screen flex flex-col">
      <NavBar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/run/:runId" element={<Run />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </main>
      <SponsorBar />
    </div>
  );
}
