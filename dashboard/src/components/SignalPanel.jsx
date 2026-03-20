import React from 'react';
import { useSignalHistory, useJunction } from '../hooks/useJunctions';
import { useWebSocket } from '../hooks/useWebSocket';

export default function SignalPanel({ junctionId }) {
  const { data: signalHistory } = useSignalHistory(junctionId, 24);
  const { data: junctionData } = useJunction(junctionId);
  
  const city = junctionData?.junction?.city;
  const { lastMessage } = useWebSocket(city);
  
  // Derive latest signal from WebSocket if fresh, otherwise fallback to history
  const historyLatest = signalHistory && signalHistory.length > 0 ? signalHistory[0] : null;
  const latestSignal = (lastMessage && lastMessage.type === 'SIGNAL_UPDATE' && lastMessage.junction_id === junctionId) 
    ? lastMessage.data 
    : historyLatest;

  if (!latestSignal) {
    return (
      <div className="p-8 flex flex-col items-center justify-center bg-[var(--surface-solid)] h-full">
        <div className="text-[var(--danger)] font-mono text-sm tracking-[0.2em] font-bold animate-pulse">NO SIGNAL DATA</div>
        <div className="text-[var(--muted)] text-[10px] mt-2">Awaiting sync from edge node...</div>
      </div>
    );
  }

  const phase = latestSignal?.active_phase || (latestSignal.ns_green > latestSignal.ew_green ? 'NS GREEN' : 'EW GREEN');
  const phaseColor = phase.includes('NS') ? 'var(--success)' : (phase.includes('EW') ? 'var(--accent)' : 'var(--warning)');

  return (
    <div className="p-5 font-mono bg-gradient-to-br from-[var(--surface-solid)] to-[var(--surface-2)] h-full relative group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--accent)] opacity-5 rounded-full blur-2xl group-hover:opacity-10 transition-opacity"></div>
      
      <div className="flex justify-between items-start mb-6 border-b border-[var(--border)] pb-4">
        <div>
          <div className="text-[10px] text-[var(--muted)] tracking-widest uppercase mb-1">CURRENT PHASE</div>
          <div className="font-rajdhani font-bold text-5xl tracking-wide drop-shadow-[0_0_10px_rgba(0,0,0,0.5)]" style={{ color: phaseColor, textShadow: `0 0 15px ${phaseColor}80` }}>
            {phase}
          </div>
        </div>
        <div className="flex flex-col items-end">
          <div className="bg-[var(--surface-solid)] border border-[var(--accent)] px-3 py-1 text-[10px] tracking-widest font-bold rounded shadow-[0_0_10px_rgba(61,142,248,0.2)]" style={{ color: 'var(--accent)' }}>
            CONTROL: {latestSignal.source ? latestSignal.source.toUpperCase() : 'UNKNOWN'}
          </div>
          <div className="text-[9px] text-[var(--muted)] mt-2 italic">CYCLE: {latestSignal.cycle_length || 60}s</div>
        </div>
      </div>
      
      <div className="mb-6 bg-[var(--surface-solid)] p-2 rounded border border-[var(--border)] shadow-inner">
        <div className="flex justify-between text-[10px] font-bold tracking-widest text-[var(--muted)] mb-1 uppercase">
          <span>PHASE PROGRESS</span>
          <span>REMAINING</span>
        </div>
        <div className="h-2 w-full bg-[var(--bg)] rounded-full relative overflow-hidden">
           {/* Note: In a real app, countdown UI would be tied to a local timer based on timestamp */}
           <div key={latestSignal.time || ''} className="absolute top-0 left-0 bottom-0 rounded-full" style={{ background: phaseColor, width: '100%', animation: `countdown-shrink ${latestSignal.cycle_length || 60}s linear forwards` }}></div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-[rgba(0,0,0,0.2)] p-3 rounded-lg border border-[var(--border)] relative overflow-hidden">
          <div className={`absolute left-0 top-0 bottom-0 w-1 ${phase.includes('NS') ? 'bg-[var(--success)] shadow-[0_0_8px_var(--success)]' : 'bg-[var(--border)]'}`}></div>
          <div className="text-[10px] text-[var(--muted)] mb-1 uppercase tracking-widest pl-2">NORTH/SOUTH</div>
          <div className="flex items-end justify-between pl-2">
            <div>
              <div className="text-2xl text-white font-bold">{latestSignal.ns_demand?.toFixed(1) || 0}</div>
              <div className="text-[9px] text-[var(--muted)]">DEMAND</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-rajdhani font-bold text-[var(--success)]">{latestSignal.ns_green || 0}s</div>
              <div className="text-[9px] text-[var(--success)] font-bold">GREEN</div>
            </div>
          </div>
        </div>
        
        <div className="bg-[rgba(0,0,0,0.2)] p-3 rounded-lg border border-[var(--border)] relative overflow-hidden">
          <div className={`absolute left-0 top-0 bottom-0 w-1 ${phase.includes('EW') ? 'bg-[var(--accent)] shadow-[0_0_8px_var(--accent)]' : 'bg-[var(--border)]'}`}></div>
          <div className="text-[10px] text-[var(--muted)] mb-1 uppercase tracking-widest pl-2">EAST/WEST</div>
          <div className="flex items-end justify-between pl-2">
            <div>
              <div className="text-2xl text-white font-bold">{latestSignal.ew_demand?.toFixed(1) || 0}</div>
              <div className="text-[9px] text-[var(--muted)]">DEMAND</div>
            </div>
            <div className="text-right">
              <div className="text-lg font-rajdhani font-bold text-[var(--accent)]">{latestSignal.ew_green || 0}s</div>
              <div className="text-[9px] text-[var(--accent)] font-bold">GREEN</div>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between items-center bg-[var(--surface-solid)] p-3 rounded border border-[var(--border)]">
        {latestSignal.efficiency_gain > 0 ? (
          <div className="flex flex-col">
             <span className="text-[var(--success)] font-bold text-lg flex items-center gap-1">
               <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
               +{latestSignal.efficiency_gain}%
             </span>
             <span className="text-[var(--muted)] text-[9px] tracking-wider uppercase">EFFICIENCY GAIN</span>
          </div>
        ) : (
          <div className="flex flex-col">
             <span className="text-[var(--muted)] font-bold text-lg flex items-center gap-1">0%</span>
             <span className="text-[var(--muted)] text-[9px] tracking-wider uppercase">BASELINE EFFICENCY</span>
          </div>
        )}
        <div className="text-[10px] text-[var(--muted)] italic text-right max-w-[55%] leading-relaxed border-l border-[var(--border)] pl-3">
          {latestSignal.decision_reason || 'Standard Webster calculation applied based on current demand volumes.'}
        </div>
      </div>
    </div>
  );
}
