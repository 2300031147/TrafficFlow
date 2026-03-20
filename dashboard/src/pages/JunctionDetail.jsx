import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useJunction, useSignalHistory } from '../hooks/useJunctions';
import SignalPanel from '../components/SignalPanel';
import TrafficChart from '../components/TrafficChart';
import OverridePanel from '../components/OverridePanel';
import LiveDetectionFeed from '../components/LiveDetectionFeed';
import FestivalBanner from '../components/FestivalBanner';
import PatternInsight from '../components/PatternInsight';

export default function JunctionDetail() {
  const { junction_id } = useParams();
  const navigate = useNavigate();
  const { data, isLoading } = useJunction(junction_id);
  const { data: signalHistory } = useSignalHistory(junction_id, 24);
  
  const junction = data?.junction;
  const latestCounts = data?.latest_counts || [];
  const activeEvent = signalHistory?.[0]?.active_event || null;

  if (isLoading || !junction) {
    return (
      <div className="min-h-screen bg-[var(--bg)] text-[var(--accent)] p-8 flex flex-col items-center justify-center font-mono">
        <div className="w-16 h-16 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin mb-4"></div>
        <div className="tracking-[0.2em] font-bold text-sm hover-glitch">ESTABLISHING DATA LINK...</div>
      </div>
    );
  }

  const getLaneCount = (laneId) => {
    const lane = latestCounts.find(l => l.lane === laneId);
    return lane ? lane.count : 0;
  };

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] flex flex-col font-mono relative overflow-hidden">
      <div className="absolute inset-0 scan-lines pointer-events-none z-50"></div>
      
      <header className="h-16 border-b border-[var(--border)] px-6 flex items-center justify-between bg-[rgba(5,8,16,0.85)] backdrop-blur relative z-40 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
        <div className="flex items-center gap-6">
          <button 
            onClick={() => navigate('/')} 
            className="text-[var(--accent)] hover:text-white flex items-center gap-2 group transition-colors border border-transparent hover:border-[var(--border)] px-3 py-1.5 rounded bg-[var(--surface-solid)]"
          >
            <svg className="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            <span className="text-xs uppercase tracking-widest font-bold">BACK To HQ</span>
          </button>
          
          <div className="flex flex-col border-l border-[var(--border)] pl-6">
            <h1 className="font-rajdhani text-2xl tracking-[0.15em] uppercase leading-none font-bold text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.2)]">
              {junction.name}
            </h1>
            <div className="text-[var(--accent)] text-[10px] mt-1 tracking-widest uppercase flex items-center gap-2">
              <span>{junction.city}</span>
              <span className="w-1 h-1 rounded-full bg-[var(--muted)]"></span>
              <span>NODE: {junction.junction_type}</span>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col items-end justify-center">
           <div className="flex items-center gap-2 px-3 py-1 bg-[var(--surface-solid)] border border-[var(--border)] rounded mb-1">
             <div className="w-2 h-2 rounded-full bg-[var(--success)] pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]"></div>
             <span className="text-[10px] tracking-[0.2em] font-bold text-[var(--success)]">DIRECT LINK</span>
           </div>
           <div className="font-mono text-[9px] text-[var(--muted)] tracking-wider">
             SYNC: {new Date(junction.updated_at).toLocaleTimeString()}
           </div>
        </div>
      </header>

      <main className="flex-1 pb-4 px-4 pt-4 overflow-hidden grid grid-cols-1 lg:grid-cols-[60%_40%] xl:grid-cols-[65%_35%] gap-4 relative z-40 h-[calc(100vh-64px)]">
        
        {/* Left Column: Visuals & Metrics */}
        <div className="flex flex-col gap-4 overflow-y-auto pr-2 custom-scrollbar">
          
          <div className="glass-panel p-2 rounded-xl relative group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--danger)] to-transparent opacity-30 group-hover:opacity-100 transition-opacity duration-1000"></div>
            <LiveDetectionFeed junctionId={junction_id} />
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {['north_in', 'south_in', 'east_in', 'west_in'].map((lane, i) => (
              <div key={lane} className="glass-panel p-4 rounded-xl relative overflow-hidden group hover:-translate-y-1 transition-transform cursor-default" style={{animationDelay: `${i*100}ms`, animation: 'fadeInUp 0.5s ease both'}}>
                <div className="absolute -right-4 -top-4 w-16 h-16 bg-[var(--accent)] opacity-5 rounded-full blur-xl group-hover:opacity-20 transition-opacity"></div>
                <div className="text-[10px] text-[var(--muted)] uppercase tracking-widest mb-1 flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
                  {lane.replace('_', ' ')}
                </div>
                <div className="text-3xl font-rajdhani font-bold text-white drop-shadow-sm group-hover:text-[var(--accent)] transition-colors">
                  {getLaneCount(lane)} <span className="text-[10px] text-[var(--muted)] font-mono font-normal">VEH</span>
                </div>
              </div>
            ))}
          </div>

          <div className="flex-1 glass-panel p-4 rounded-xl min-h-[250px] relative group">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--warning)] to-transparent opacity-30 group-hover:opacity-100 transition-opacity duration-1000"></div>
             <TrafficChart junctionId={junction_id} />
          </div>

        </div>

        {/* Right Column: Controls & Insights */}
        <div className="flex flex-col gap-4 overflow-y-auto pl-2 custom-scrollbar">
          <FestivalBanner activeEvent={activeEvent} />
          
          <div className="glass-panel rounded-xl overflow-hidden shadow-[0_0_20px_rgba(0,0,0,0.5)] border border-[var(--border)]">
            <SignalPanel junctionId={junction_id} />
          </div>
          
          <div className="glass-panel rounded-xl overflow-hidden">
            <PatternInsight junctionId={junction_id} />
          </div>
          
          <div className="glass-panel rounded-xl overflow-hidden mt-auto">
            <OverridePanel junctionId={junction_id} />
          </div>
        </div>
      </main>
      
      <style>{`
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: var(--accent); }
      `}</style>
    </div>
  );
}
