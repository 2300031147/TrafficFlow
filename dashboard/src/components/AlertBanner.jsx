import React from 'react';
import { useAlerts, useResolveAlert } from '../hooks/useAlerts';

export default function AlertBanner() {
  const { data, isPending } = useAlerts();
  const resolveMutation = useResolveAlert();

  const alerts = data?.data || [];
  const unreadCount = data?.unreadCount || 0;

  const getSeverityColor = (severity) => {
    if (severity === 'critical') return 'var(--danger)';
    if (severity === 'warning') return 'var(--warning)';
    return 'var(--accent)';
  };

  const getSeverityBg = (severity) => {
    if (severity === 'critical') return 'rgba(239, 68, 68, 0.1)';
    if (severity === 'warning') return 'rgba(245, 158, 11, 0.1)';
    return 'rgba(61, 142, 248, 0.1)';
  };

  return (
    <div className="flex flex-col h-full bg-transparent p-4 overflow-y-auto">
      <div className="flex justify-between items-center mb-4 pb-2 border-b border-[var(--border)]">
        <h2 className="font-rajdhani text-lg font-bold uppercase tracking-widest text-white flex items-center gap-2">
          <svg className="w-4 h-4 text-[var(--danger)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="square" strokeLinejoin="miter" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          System Alerts
        </h2>
        {unreadCount > 0 && (
          <span className="bg-[var(--danger)] text-white font-mono text-xs px-2 py-0.5 rounded shadow-[0_0_10px_rgba(239,68,68,0.5)] animate-pulse">
            {unreadCount} NEW
          </span>
        )}
      </div>

      <div className="flex flex-col gap-3">
        {isPending ? (
          <div className="text-[var(--muted)] font-mono text-xs text-center py-8 hover-glitch">SCANNING FOR THREATS...</div>
        ) : alerts.length === 0 ? (
          <div className="flex flex-col items-center justify-center p-8 gap-3 opacity-80 h-full">
            <div className="w-16 h-16 rounded-full border border-[var(--success)] flex items-center justify-center bg-[rgba(16,185,129,0.1)] shadow-[0_0_20px_rgba(16,185,129,0.2)]">
              <svg className="w-8 h-8 text-[var(--success)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" /></svg>
            </div>
            <div className="text-[var(--success)] font-rajdhani text-lg font-bold tracking-widest uppercase mt-2">
              All Systems Nominal
            </div>
            <div className="text-xs font-mono text-[var(--muted)]">No active critical alerts.</div>
          </div>
        ) : (
          alerts.map(alert => (
            <div 
              key={alert.id} 
              className="relative p-3 rounded-lg border border-transparent hover:border-[var(--border)] transition-all duration-300 group overflow-hidden"
              style={{ 
                background: getSeverityBg(alert.severity),
              }}
            >
              <div 
                className="absolute left-0 top-0 bottom-0 w-1" 
                style={{ backgroundColor: getSeverityColor(alert.severity) }}
              ></div>
              
              <div className="pl-2">
                <div className="flex justify-between items-start mb-1">
                  <span className="font-rajdhani font-bold text-sm tracking-wider uppercase drop-shadow-sm" style={{ color: getSeverityColor(alert.severity) }}>
                    {alert.type}
                  </span>
                  <span className="font-mono text-[10px] text-[var(--muted)] bg-[var(--surface-solid)] px-1.5 py-0.5 rounded border border-[var(--border)]">
                    {new Date(alert.created_at).toLocaleTimeString()}
                  </span>
                </div>
                
                <div className="font-mono text-xs text-white mb-2 font-bold tracking-wide">
                  {alert.junction_name} <span className="text-[var(--muted)] font-normal text-[10px] ml-1">({alert.city})</span>
                </div>
                
                <div className="font-mono text-[11px] text-[var(--text)] mb-3 leading-relaxed opacity-90">
                  {alert.message}
                </div>
                
                {!alert.resolved_at && (
                  <button 
                    onClick={() => resolveMutation.mutate({ alertId: alert.id, note: 'Resolved via Command Center' })}
                    disabled={resolveMutation.isPending}
                    className="w-full flex justify-center items-center gap-2 font-rajdhani text-xs bg-[var(--surface-solid)] border border-[var(--border)] px-3 py-2 uppercase tracking-widest hover:bg-[var(--surface-2)] text-[var(--text)] hover:text-white hover:border-[var(--accent)] transition-all rounded"
                  >
                    <span>ACKNOWLEDGE</span>
                    {resolveMutation.isPending ? (
                      <div className="w-3 h-3 rounded-full border border-white border-t-transparent animate-spin"></div>
                    ) : (
                      <svg className="w-3 h-3 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                    )}
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
