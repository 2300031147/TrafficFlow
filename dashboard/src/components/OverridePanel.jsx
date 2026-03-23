import React, { useState, useEffect } from 'react';
import client from '../api/client';
import { useQueryClient } from '@tanstack/react-query';

export default function OverridePanel({ junctionId }) {
  const [selectedPhase, setSelectedPhase] = useState('NS_GREEN');
  const [selectedDuration, setSelectedDuration] = useState(60);
  const [reason, setReason] = useState('');
  const [sending, setSending] = useState(false);
  const [submitError, setSubmitError] = useState('');
  
  const [activeOverride, setActiveOverride] = useState(false);
  const [timeLeft, setTimeLeft] = useState(0);
  
  const queryClient = useQueryClient();

  useEffect(() => {
    let t;
    if (activeOverride && timeLeft > 0) {
      t = setInterval(() => setTimeLeft(prev => Math.max(0, prev - 1)), 1000);
    } else if (timeLeft === 0) {
      setActiveOverride(false);
    }
    return () => clearInterval(t);
  }, [activeOverride, timeLeft]);

  useEffect(() => {
    const fetchActive = async () => {
      try {
        const res = await client.get(`/junctions/${junctionId}/override/active`);
        const data = res.data?.data || res.data;
        if (data && data.cancelled_at === null) {
           const end = new Date(data.created_at).getTime() + (data.duration * 1000);
           const remain = Math.max(0, Math.floor((end - Date.now()) / 1000));
           if (remain > 0) {
              setActiveOverride(true);
              setTimeLeft(remain);
              setSelectedPhase(data.phase);
           }
        }
      } catch (e) {
        console.error(e);
      }
    };
    fetchActive();
  }, [junctionId]);

  const onSubmit = async () => {
    setSending(true);
    setSubmitError('');
    try {
      await client.post(`/junctions/${junctionId}/override`, {
        phase: selectedPhase,
        duration: selectedDuration,
        reason
      });
      setActiveOverride(true);
      setTimeLeft(selectedDuration);
      queryClient.invalidateQueries({ queryKey: ['signals'] });
    } catch (e) {
      setSubmitError(e.response?.data?.detail || 'Override failed — check connection');
    } finally {
      setSending(false);
    }
  };

  const onCancel = async () => {
    try {
      await client.delete(`/junctions/${junctionId}/override`);
      setActiveOverride(false);
      setTimeLeft(0);
      queryClient.invalidateQueries({ queryKey: ['signals'] });
    } catch (e) {
      console.error(e);
    }
  };

  const presets = [
    { label: 'EMERGENCY', d: 60, r: 'Emergency vehicle bypass', p: 'NS_GREEN', color: 'bg-red-500/10 text-red-500 border-red-500/30 hover:bg-red-500/20' },
    { label: 'SCHOOL', d: 45, r: 'School rush', p: 'EW_GREEN', color: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/30 hover:bg-yellow-500/20' },
    { label: 'EVENT', d: 30, r: 'Local event clearing', p: 'NS_GREEN', color: 'bg-purple-500/10 text-purple-500 border-purple-500/30 hover:bg-purple-500/20' },
  ];

  return (
    <div className="bg-[var(--surface-solid)] border border-[var(--border)] rounded-[4px] font-mono flex flex-col overflow-hidden group">
      <div className="px-4 py-3 bg-[rgba(5,8,16,0.5)] border-b border-[var(--border)] flex items-center justify-between">
         <span className="font-rajdhani text-sm font-bold uppercase tracking-widest text-[var(--warning)] flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            Manual System Override
         </span>
      </div>

      {activeOverride && (
        <div className="w-full bg-[var(--danger)]/90 backdrop-blur text-white font-rajdhani font-bold flex justify-between items-center transition-all p-3 z-20 sticky top-0">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-white"></div>
            <span className="tracking-[0.2em]">OVERRIDE ACTIVE [{selectedPhase}]</span>
          </div>
          <span className="text-xl tracking-widest">{timeLeft}s</span>
        </div>
      )}
      
      <div className="p-4 flex flex-col gap-4">
        
        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-[var(--muted)] tracking-widest uppercase mb-1">Target Phase</label>
          <div className="flex items-center gap-2">
            {['NS_GREEN', 'EW_GREEN'].map(ph => (
              <button
                key={ph}
                onClick={() => setSelectedPhase(ph)}
                className={`flex-1 py-3 text-xs tracking-widest border rounded-[4px] transition-all font-bold uppercase ${selectedPhase === ph ? 'bg-[rgba(61,142,248,0.1)] text-[var(--accent)] border-[var(--accent)]' : 'bg-[var(--surface-solid)] text-[var(--muted)] border-[var(--border)] hover:border-[var(--muted)]'}`}
              >
                {ph.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-[10px] text-[var(--muted)] tracking-widest uppercase mb-1">Hold Duration</label>
          <div className="flex items-center gap-2">
            {[15, 30, 45, 60, 90].map(dur => (
              <button
                key={dur}
                onClick={() => setSelectedDuration(dur)}
                className={`flex-1 py-1.5 text-[10px] font-bold border rounded-[4px] transition-all ${selectedDuration === dur ? 'bg-[var(--accent)] text-white border-[var(--accent)]' : 'bg-[var(--surface-solid)] text-[var(--muted)] border-[var(--border)] hover:border-[var(--muted)] hover:text-white'}`}
              >
                {dur}s
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-1 relative">
          <label className="text-[10px] text-[var(--muted)] tracking-widest uppercase mb-1">Authorization Reason</label>
          <input
            type="text"
            maxLength={100}
            placeholder="AWAITING INPUT..."
            value={reason}
            onChange={e => setReason(e.target.value)}
            className="w-full bg-[var(--surface-solid)] border border-[var(--border)] p-3 pl-8 text-xs text-[var(--text)] outline-none focus:border-[var(--warning)] rounded-[4px] font-mono tracking-wide placeholder-[var(--surface-2)] transition-colors"
          />
          <div className="absolute left-3 top-9 text-[var(--warning)]">&gt;</div>
        </div>

        <div className="flex flex-col gap-1 mt-1">
          <label className="text-[10px] text-[var(--muted)] tracking-widest uppercase mb-1">Quick Actions</label>
          <div className="grid grid-cols-3 gap-2">
            {presets.map(p => (
              <button
                key={p.label}
                onClick={() => { setSelectedPhase(p.p); setSelectedDuration(p.d); setReason(p.r); }}
                className={`text-[9px] border py-2 px-1 rounded-[4px] uppercase font-bold tracking-widest transition-all text-center ${p.color}`}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-2">
          {activeOverride ? (
            <button
              onClick={onCancel}
              className="w-full bg-[rgba(239,68,68,0.1)] border border-[var(--danger)] py-4 text-[var(--danger)] font-rajdhani font-bold hover:bg-[var(--danger)] hover:text-white transition-all uppercase tracking-[0.2em] rounded-[4px] relative overflow-hidden group/btn text-lg"
            >
              <div className="absolute inset-0 bg-[var(--danger)] opacity-0 group-hover/btn:opacity-100 transition-opacity"></div>
              <span className="relative z-10 flex items-center justify-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                CANCEL OVERRIDE
              </span>
            </button>
          ) : (
            <button
              onClick={onSubmit}
              disabled={sending}
              className={`w-full py-4 font-rajdhani font-bold text-[var(--surface-solid)] transition-all uppercase tracking-[0.1em] rounded-[4px] relative overflow-hidden group/btn text-lg ${sending ? 'bg-white opacity-50' : 'bg-[var(--warning)] hover:brightness-110'}`}
            >
              <div className="absolute inset-0 bg-white opacity-0 group-hover/btn:opacity-10 transition-opacity"></div>
              <span className="relative z-10 flex items-center justify-center gap-2">
                {sending ? (
                  <>
                    <div className="w-5 h-5 border-2 border-[var(--surface-solid)] border-t-transparent rounded-full animate-spin"></div>
                    TRANSMITTING COMMAND...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                    EXECUTE {selectedPhase.split('_')[0]} GREEN PROTOCOL
                  </>
                )}
              </span>
            </button>
          )}
        </div>

        <div className="text-[9px] text-[var(--muted)] text-center w-full uppercase mt-2 tracking-widest opacity-50 flex items-center justify-center gap-2">
          <span className="w-2 h-px bg-[var(--muted)]"></span>
          AUDIT LOG ENABLED
          <span className="w-2 h-px bg-[var(--muted)]"></span>
        </div>
        {submitError && <div className="text-[var(--danger)] bg-[rgba(239,68,68,0.1)] py-1 font-mono text-xs mt-1 text-center border border-[var(--danger)] rounded">{submitError}</div>}
      </div>
    </div>
  );
}
