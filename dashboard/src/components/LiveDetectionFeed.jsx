import React, { useState } from 'react';
import { useJunction } from '../hooks/useJunctions';

export default function LiveDetectionFeed({ junctionId }) {
  const [streamError, setStreamError] = useState(false);
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1').replace(/\/api\/v1$/, '');
  const streamUrl = `${baseUrl}/api/v1/stream/${junctionId}`;
  
  const { data } = useJunction(junctionId);

  return (
    <div className="flex flex-col gap-3">
      {/* Decorative Label */}
      <div className="flex items-center justify-between border-[0.5px] border-[var(--accent)] bg-[rgba(61,142,248,0.1)] px-3 py-1.5 rounded-t-lg">
         <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[var(--danger)] pulse shadow-[0_0_8px_var(--danger)]"></div>
            <span className="text-[10px] text-[var(--danger)] font-bold tracking-[0.2em] uppercase">LIVE SENSOR FEED</span>
         </div>
         <div className="text-[10px] text-[var(--muted)] tracking-widest font-mono">
            NODE: {data?.junction?.camera_count || 4} CAMERAS
         </div>
      </div>

      {/* Main Feed Container */}
      <div className="relative aspect-video bg-[var(--surface-solid)] w-full border border-[var(--border)] overflow-hidden rounded-b-lg shadow-[0_0_30px_rgba(0,0,0,0.4)] group">
        {/* Reticle Brackets */}
        <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-white/50 z-20 pointer-events-none transition-transform group-hover:scale-90"></div>
        <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-white/50 z-20 pointer-events-none transition-transform group-hover:scale-90"></div>
        <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-white/50 z-20 pointer-events-none transition-transform group-hover:scale-90"></div>
        <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-white/50 z-20 pointer-events-none transition-transform group-hover:scale-90"></div>

        {!streamError ? (
          <img 
            src={streamUrl} 
            alt="Live feed"
            onError={() => setStreamError(true)}
            className="w-full h-full object-cover filter contrast-125 saturate-50 sepia-0"
          />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-[var(--surface-solid)]">
            <svg className="w-12 h-12 text-[var(--danger)] mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
            <div className="text-[var(--danger)] font-mono text-sm tracking-widest font-bold">FEED UNAVAILABLE</div>
            <div className="text-[var(--muted)] font-mono text-[9px] mt-2 uppercase">Awaiting connection restablishment</div>
            
            {/* Loading scanbar */}
            <div className="w-32 h-1 bg-[var(--surface-2)] mt-4 rounded overflow-hidden">
               <div className="h-full bg-[var(--danger)] w-1/4 animate-[ping_1.5s_infinite]"></div>
            </div>
          </div>
        )}

        <div className="absolute inset-0 scan-lines pointer-events-none opacity-50 z-10"></div>
        
        {/* Timestamp Overlay */}
        <div className="absolute bottom-3 left-1/2 -translate-x-1/2 bg-[rgba(0,0,0,0.6)] backdrop-blur px-3 py-1 rounded text-[10px] font-mono text-white tracking-widest z-20 border border-white/10">
           REC // {new Date().toISOString().replace('T', ' ').slice(0,19)}
        </div>
      </div>

      {/* Legend Container */}
      <div className="bg-[var(--surface-solid)] border border-[var(--border)] rounded p-2 flex items-center justify-between font-mono text-[9px] tracking-widest px-4">
        <span className="text-[var(--muted)]">DETECTION LEGEND:</span>
        <div className="flex gap-4">
          <div className="flex items-center gap-1.5 hover-glitch cursor-default">
             <div className="w-2.5 h-2.5 bg-green-500 opacity-80 border border-green-400 rounded-sm shadow-[0_0_5px_#22c55e]"></div>
             <span className="text-white">CAR</span>
          </div>
          <div className="flex items-center gap-1.5 hover-glitch cursor-default">
             <div className="w-2.5 h-2.5 bg-orange-500 opacity-80 border border-orange-400 rounded-sm shadow-[0_0_5px_#f97316]"></div>
             <span className="text-white">MOTO</span>
          </div>
          <div className="flex items-center gap-1.5 hover-glitch cursor-default">
             <div className="w-2.5 h-2.5 bg-blue-500 opacity-80 border border-blue-400 rounded-sm shadow-[0_0_5px_#3b82f6]"></div>
             <span className="text-white">BUS</span>
          </div>
          <div className="flex items-center gap-1.5 hover-glitch cursor-default">
             <div className="w-2.5 h-2.5 bg-red-500 opacity-80 border border-red-400 rounded-sm shadow-[0_0_5px_#ef4444]"></div>
             <span className="text-white">TRUCK</span>
          </div>
        </div>
      </div>
    </div>
  );
}
