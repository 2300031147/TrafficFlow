import React from 'react';
import { useSignalHistory } from '../hooks/useJunctions';

export default function PatternInsight({ junctionId }) {
  const { data: signalHistory } = useSignalHistory(junctionId, 24);

  if (!signalHistory || signalHistory.length === 0) return null;

  const latest = signalHistory[0];
  const conf = latest.pattern_confidence || 0;
  
  let confColor = 'var(--danger)';
  if (conf >= 0.7) confColor = 'var(--success)';
  else if (conf >= 0.3) confColor = 'var(--warning)';

  let confText = 'LEARNING — PREDICTIVE OFFLINE';
  if (conf >= 0.7) confText = 'PATTERN ACTIVE — PREDICTIVE MODE';
  else if (conf >= 0.3) confText = 'PATTERN DEVELOPING';

  const calcPeak = (hist) => {
    if (!hist || hist.length === 0) return { hour: '00:00', val: 0 };
    let max = 0;
    let peakStr = '00:00';
    hist.forEach(h => {
      const dem = (h.ns_demand || 0) + (h.ew_demand || 0);
      if (dem > max) {
         max = dem;
         const d = new Date(h.time);
         peakStr = `${d.getHours().toString().padStart(2, '0')}:00`;
      }
    });
    return { hour: peakStr, val: Math.round(max) };
  };

  const peakData = calcPeak(signalHistory);
  
  // Compare first third vs last third of available data window
  const third = Math.max(1, Math.floor(signalHistory.length / 3));
  const currentAvg = signalHistory.slice(0, third).reduce((a,b) => a + (b.ns_demand||0) + (b.ew_demand||0), 0) / third || 1;
  const olderAvg = signalHistory.slice(-third).reduce((a,b) => a + (b.ns_demand||0) + (b.ew_demand||0), 0) / third || 1;
  const rawDiff = ((currentAvg - olderAvg) / olderAvg) * 100;
  const percDiff = rawDiff > 0 ? `+${rawDiff.toFixed(1)}%` : `${rawDiff.toFixed(1)}%`;
  const diffArrow = rawDiff > 0 ? '↑' : '↓';
  const diffColor = rawDiff > 0 ? 'var(--danger)' : 'var(--success)';

  return (
    <div className="p-4 rounded-xl font-mono bg-gradient-to-br from-[var(--surface-solid)] to-[rgba(15,21,37,0.4)] border border-[var(--border)] relative overflow-hidden group">
      <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition-opacity">
        <svg className="w-12 h-12 text-[var(--accent)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>
      </div>

      <div className="text-[10px] text-[var(--accent)] tracking-widest uppercase mb-4 flex items-center gap-2 font-bold">
        <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)]"></span>
        Pattern Intelligence
      </div>
      
      <div className="grid grid-cols-2 gap-4 mb-5 pb-5 border-b border-[var(--border)]">
        <div className="bg-[var(--surface-solid)] p-3 rounded border border-[var(--border)]">
          <div className="text-[9px] text-[var(--muted)] uppercase tracking-wider mb-2 flex items-center gap-1 group/tooltip items-start">
             TREND
          </div>
          <div className="text-2xl font-rajdhani font-bold flex items-center gap-2" style={{ color: diffColor }}>
            <span>{diffArrow}</span> 
            <span>{percDiff}</span>
          </div>
        </div>
        <div className="bg-[var(--surface-solid)] p-3 rounded border border-[var(--border)]">
          <div className="text-[9px] text-[var(--muted)] uppercase tracking-wider mb-2">
             TODAY'S PEAK
          </div>
          <div className="flex items-end gap-2">
            <div className="text-2xl font-rajdhani font-bold text-white">{peakData.hour}</div>
            <div className="text-[10px] text-[var(--muted)] mb-1">{peakData.val} VEHS</div>
          </div>
        </div>
      </div>

      <div className="bg-[rgba(0,0,0,0.2)] p-3 rounded border border-[var(--border)]">
         <div className="flex justify-between items-center mb-2">
           <div className="text-[10px] uppercase tracking-widest text-white font-bold">Prediction Confidence</div>
           <div className="text-[10px] font-bold" style={{ color: confColor }}>{(conf * 100).toFixed(0)}%</div>
         </div>
         <div className="h-2 w-full bg-[var(--surface-solid)] rounded-full overflow-hidden mb-2 shadow-inner">
            <div 
               className="h-full rounded-full relative" 
               style={{ 
                  width: `${conf * 100}%`, 
                  background: `linear-gradient(90deg, transparent, ${confColor})`, 
                  transition: 'width 1.5s cubic-bezier(0.22, 1, 0.36, 1)' 
               }}
            >
               <div className="absolute right-0 top-0 bottom-0 w-2 bg-white opacity-50 shadow-[0_0_8px_white]"></div>
            </div>
         </div>
         <div className="flex items-center gap-2 text-[10px] text-[var(--muted)] italic tracking-wide">
           <span className="w-1 h-1 rounded-full animate-ping" style={{ backgroundColor: confColor }}></span>
           {confText}
         </div>
      </div>
    </div>
  );
}
