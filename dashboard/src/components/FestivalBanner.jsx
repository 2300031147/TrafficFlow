import React from 'react';

export default function FestivalBanner({ activeEvent }) {
  if (!activeEvent) return null;

  return (
    <div 
      className="bg-[rgba(245,158,11,0.1)] p-4 border border-[var(--border)] flex items-center gap-4 rounded-xl relative overflow-hidden group shadow-[0_0_15px_rgba(245,158,11,0.1)]"
    >
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-[var(--warning)] shadow-[0_0_10px_var(--warning)]"></div>
      
      <div className="text-[var(--warning)] text-2xl animate-[spin_3s_linear_infinite] opacity-80">
        <svg fill="currentColor" viewBox="0 0 20 20" className="w-8 h-8 drop-shadow-[0_0_5px_var(--warning)]"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"></path></svg>
      </div>
      
      <div className="flex-1 ml-2">
        <div className="font-rajdhani font-bold text-white uppercase text-xl tracking-[0.1em] drop-shadow-md">
          {activeEvent}
        </div>
        <div className="font-mono text-[10px] text-[var(--warning)] uppercase tracking-widest flex items-center gap-2 mt-1 font-bold">
          <span className="w-1.5 h-1.5 rounded-full bg-[var(--warning)] animate-ping"></span>
          EVENT ACTIVE TODAY
        </div>
      </div>
      
      <div className="text-right font-mono text-[var(--warning)] text-[10px] border border-[var(--warning)] px-3 py-1.5 bg-[rgba(245,158,11,0.15)] rounded font-bold tracking-[0.2em] shadow-[inset_0_0_8px_rgba(245,158,11,0.2)] hover:bg-[var(--warning)] hover:text-white transition-colors cursor-default">
        AI SYNC ACTIVE
      </div>
    </div>
  );
}
