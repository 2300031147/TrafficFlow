import React, { useState, useEffect } from 'react';
import { useJunctions } from '../hooks/useJunctions';
import CityMap from '../components/CityMap';
import AlertBanner from '../components/AlertBanner';
import { useNavigate } from 'react-router-dom';

export default function CommandCenter() {
  const { data: junctions, isLoading } = useJunctions();
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="relative bg-[var(--bg)] text-[var(--text)] h-screen overflow-hidden flex flex-col font-mono">
      {/* Background Grid & Scanlines */}
      <div className="absolute inset-0 scan-lines pointer-events-none z-50"></div>
      <div className="absolute inset-0 bg-[linear-gradient(rgba(61,142,248,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(61,142,248,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none"></div>

      {/* Top HUD Header */}
      <header className="h-16 border-b border-[var(--border)] bg-[rgba(5,8,16,0.8)] backdrop-blur-md flex items-center justify-between px-6 relative z-40 shadow-[0_4px_20px_rgba(0,0,0,0.5)]">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 rounded border border-[var(--accent)] flex items-center justify-center bg-[var(--surface-solid)] shadow-[0_0_10px_rgba(61,142,248,0.3)]">
            <span className="font-rajdhani text-lg font-bold text-[var(--accent)]">UF</span>
          </div>
          <h1 className="font-rajdhani text-2xl font-bold tracking-[0.2em] uppercase text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.3)]">
            Command Center
          </h1>
        </div>
        
        {/* Center - Clock */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 hidden md:flex items-center gap-6 px-8 py-1 border border-[var(--border)] rounded-full bg-[var(--surface-solid)]">
          <div className="text-[var(--accent)] text-sm tracking-widest">{currentTime.toISOString().split('T')[0]}</div>
          <div className="w-1 h-1 rounded-full bg-[var(--muted)]"></div>
          <div className="text-white text-sm tracking-widest font-bold">{currentTime.toLocaleTimeString('en-US', {hour12: false})}</div>
        </div>

        <div className="flex items-center gap-6">
           <div className="flex items-center gap-3 bg-[var(--surface-solid)] px-4 py-1.5 rounded-full border border-[var(--border)] shadow-[0_0_15px_rgba(16,185,129,0.1)]">
              <div className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--success)] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--success)]"></span>
              </div>
              <span className="text-xs tracking-widest text-[var(--success)] font-bold">SYSTEM ACTIVE</span>
           </div>
           
           <button 
             onClick={() => navigate('/login')}
             className="text-xs uppercase tracking-widest text-[var(--muted)] hover:text-white transition-colors border border-transparent hover:border-[var(--border)] px-3 py-1 rounded"
           >
             Log Out
           </button>
        </div>
      </header>
      
      {/* Main Layout */}
      <main className="flex-1 grid grid-cols-1 lg:grid-cols-[3fr_6fr_3fr] gap-4 p-4 relative z-40 h-[calc(100vh-64px)]">
        
        {/* Left Panel: Assets List */}
        <aside className="glass-panel rounded-xl flex flex-col overflow-hidden relative group">
           <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-1000"></div>
           <div className="p-4 border-b border-[var(--border)] bg-[rgba(15,21,37,0.8)] backdrop-blur">
             <h2 className="font-rajdhani text-lg font-bold uppercase tracking-widest text-white flex items-center gap-2">
               <svg className="w-4 h-4 text-[var(--accent)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="square" strokeLinejoin="miter" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
               City Assets
             </h2>
           </div>
           
           <div className="flex-1 overflow-y-auto p-2 scroll-smooth">
             {isLoading ? (
               <div className="h-full flex flex-col items-center justify-center text-[var(--accent)] gap-4">
                 <div className="w-8 h-8 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin"></div>
                 <div className="text-xs tracking-widest hover-glitch">SCANNING GRID...</div>
               </div>
             ) : (
                <ul className="space-y-2">
                  {junctions?.map((j, idx) => (
                    <li 
                      key={j.id} 
                      onClick={() => navigate(`/junction/${j.id}`)} 
                      className="group/item flex items-center justify-between p-3 rounded-lg border border-transparent hover:border-[var(--border)] hover:bg-[var(--surface-2)] cursor-pointer transition-all duration-300 relative overflow-hidden"
                      style={{ animationDelay: `${idx * 50}ms`, animation: 'fadeInUp 0.5s ease both' }}
                    >
                       <div className="absolute left-0 top-0 bottom-0 w-1 bg-[var(--accent)] scale-y-0 group-hover/item:scale-y-100 transition-transform origin-center duration-300"></div>
                       <div className="flex flex-col ml-2">
                         <span className="font-bold text-sm text-[var(--text)] tracking-wider group-hover/item:text-white transition-colors">{j.name.toUpperCase()}</span>
                         <span className="text-[10px] text-[var(--muted)]">{j.city} • ID:{j.id.slice(0,6)}</span>
                       </div>
                       <div className="flex items-center gap-2">
                         <span className={`text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-sm bg-opacity-20 ${
                           j.status === 'online' ? 'text-[var(--success)] bg-[var(--success)]' : 
                           j.status === 'offline' ? 'text-[var(--danger)] bg-[var(--danger)]' : 
                           'text-[var(--warning)] bg-[var(--warning)]'
                         }`}>
                           {j.status}
                         </span>
                       </div>
                    </li>
                  ))}
                </ul>
             )}
           </div>
        </aside>
        
        {/* Center Panel: Map */}
        <section className="glass-panel rounded-xl overflow-hidden relative min-h-[400px] border border-[var(--border)] shadow-[0_0_30px_rgba(0,0,0,0.5)]">
          <div className="absolute inset-0 ring-1 ring-inset ring-[rgba(255,255,255,0.05)] rounded-xl pointer-events-none z-10"></div>
          {/* Decorative Corner Brackets */}
          <div className="absolute top-0 left-0 w-8 h-8 border-t-2 border-l-2 border-[var(--accent)] rounded-tl-xl z-20 pointer-events-none opacity-50"></div>
          <div className="absolute top-0 right-0 w-8 h-8 border-t-2 border-r-2 border-[var(--accent)] rounded-tr-xl z-20 pointer-events-none opacity-50"></div>
          <div className="absolute bottom-0 left-0 w-8 h-8 border-b-2 border-l-2 border-[var(--accent)] rounded-bl-xl z-20 pointer-events-none opacity-50"></div>
          <div className="absolute bottom-0 right-0 w-8 h-8 border-b-2 border-r-2 border-[var(--accent)] rounded-br-xl z-20 pointer-events-none opacity-50"></div>
          
          <CityMap junctions={junctions} />
          
          {/* Overlay Status */}
          <div className="absolute bottom-4 left-4 z-30 bg-[rgba(5,8,16,0.85)] backdrop-blur border border-[var(--border)] rounded-lg p-3">
             <div className="text-[10px] tracking-widest text-[var(--muted)] mb-1">DATA LINK</div>
             <div className="text-xs font-bold tracking-wider text-[var(--success)] flex items-center gap-2">
               <span className="w-1.5 h-1.5 rounded-full bg-[var(--success)] animate-pulse"></span>
               SECURE CONNECTION
             </div>
          </div>
        </section>
        
        {/* Right Panel: Alerts & Logs */}
        <aside className="flex flex-col gap-4">
          <div className="flex-1 glass-panel rounded-xl overflow-hidden group border border-[var(--border)]">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--danger)] to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-1000"></div>
             <AlertBanner />
          </div>
          <div className="h-[30%] glass-panel rounded-xl overflow-hidden p-4 flex flex-col group relative">
             <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-[var(--accent)] to-transparent opacity-50 group-hover:opacity-100 transition-opacity duration-1000"></div>
             <h2 className="font-rajdhani text-sm font-bold uppercase tracking-widest text-white mb-3 flex items-center gap-2 pb-2 border-b border-[var(--border)]">
               <svg className="w-4 h-4 text-[var(--accent)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="square" strokeLinejoin="miter" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
               System Log
             </h2>
             <div className="flex-1 overflow-y-auto text-[10px] text-[var(--muted)] space-y-1.5 font-mono pr-2">
               <div className="flex items-start gap-2"><span className="text-[var(--accent)]">[{currentTime.toISOString().split('T')[1].slice(0,8)}]</span><span className="text-[var(--text)]">Heartbeat synched.</span></div>
               <div className="flex items-start gap-2"><span className="text-[var(--accent)]">[{currentTime.toISOString().split('T')[1].slice(0,8)}]</span><span className="text-[var(--text)]">Telemetry streams active.</span></div>
               <div className="flex items-start gap-2"><span className="text-[var(--accent)]">[{currentTime.toISOString().split('T')[1].slice(0,8)}]</span><span className="text-[var(--text)]">AI prediction models stabilized.</span></div>
               <div className="flex items-start gap-2 opacity-50"><span className="text-[var(--accent)]">[{new Date(currentTime.getTime() - 60000).toISOString().split('T')[1].slice(0,8)}]</span><span>Background scans completed.</span></div>
               <div className="flex items-start gap-2 opacity-30"><span className="text-[var(--accent)]">[{new Date(currentTime.getTime() - 120000).toISOString().split('T')[1].slice(0,8)}]</span><span>User successfully authenticated.</span></div>
             </div>
          </div>
        </aside>
      </main>
      
      <style>{`
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
