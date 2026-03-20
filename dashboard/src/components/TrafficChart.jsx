import React from 'react';
import { useCountHistory } from '../hooks/useJunctions';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

export default function TrafficChart({ junctionId }) {
  const { data: countsHistory, isLoading } = useCountHistory(junctionId, 60);

  if (isLoading || !countsHistory) {
    return (
      <div className="h-full w-full flex items-center justify-center">
        <div className="text-[var(--muted)] font-mono text-sm tracking-widest pulse">CHART DATA SYNCING...</div>
      </div>
    );
  }

  const timeMap = {};
  countsHistory.forEach(row => {
    const timeKey = new Date(row.time).getTime();
    if (!timeMap[timeKey]) timeMap[timeKey] = { time: row.time, timeKey };
    timeMap[timeKey][row.lane] = row.count;
  });

  const chartData = Object.values(timeMap).sort((a, b) => a.timeKey - b.timeKey);

  const colors = {
    north_in: '#10b981', // success
    south_in: '#3d8ef8', // accent
    east_in: '#f59e0b', // warning
    west_in: '#a855f7'   // purple
  };

  const statCards = ['north_in', 'south_in', 'east_in', 'west_in'].map(lane => {
    const values = countsHistory.filter(r => r.lane === lane).map(r => r.count);
    const avg = values.length ? (values.reduce((a,b) => a+b, 0) / values.length).toFixed(1) : 0;
    const peak = values.length ? Math.max(...values) : 0;
    return { lane, avg, peak };
  });

  return (
    <div className="flex flex-col h-full gap-4">
      <div className="flex items-center justify-between z-10">
         <div className="flex items-center gap-2">
            <svg className="w-4 h-4 text-[var(--accent)]" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="square" strokeLinejoin="miter" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
            <span className="font-rajdhani text-sm uppercase tracking-widest font-bold text-white">Traffic Volume <span className="text-[10px] text-[var(--muted)] font-mono">(LAST 60 MINS)</span></span>
         </div>
      </div>
      
      <div className="flex-1 min-h-[150px] w-full z-10">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 5, right: 5, left: -25, bottom: 0 }}>
            <CartesianGrid stroke="var(--border)" strokeDasharray="2 4" vertical={false} />
            <XAxis 
              dataKey="time" 
              tickFormatter={(t) => format(new Date(t), 'HH:mm')}
              tick={{ fill: 'var(--muted)', fontSize: 9, fontFamily: 'JetBrains Mono' }}
              stroke="transparent"
              dy={10}
            />
            <YAxis 
              tick={{ fill: 'var(--muted)', fontSize: 9, fontFamily: 'JetBrains Mono' }}
              stroke="transparent"
              tickLine={false}
              axisLine={false}
            />
            <Tooltip 
              contentStyle={{ background: 'rgba(15,21,37,0.9)', border: '1px solid var(--border)', borderRadius: '8px', boxShadow: '0 4px 20px rgba(0,0,0,0.5)', fontFamily: 'JetBrains Mono', fontSize: '10px' }}
              labelFormatter={(label) => format(new Date(label), 'HH:mm:ss')}
              itemStyle={{ fontSize: '12px', fontWeight: 'bold' }}
            />
            {['north_in', 'south_in', 'east_in', 'west_in'].map(lane => (
              <Line 
                key={lane}
                type="monotone"
                dataKey={lane}
                name={lane.replace('_', ' ').toUpperCase()}
                stroke={colors[lane]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4, fill: colors[lane], stroke: 'white', strokeWidth: 1 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 font-mono z-10 pt-2 border-t border-[var(--border)] mt-2">
        {statCards.map(stat => (
          <div key={stat.lane} className="bg-[rgba(0,0,0,0.2)] border border-[var(--border)] p-2 rounded-lg relative overflow-hidden group hover:border-[var(--accent)] transition-colors">
            <div className="absolute left-0 top-0 bottom-0 w-0.5" style={{ backgroundColor: colors[stat.lane] }}></div>
            <div className="text-[9px] uppercase tracking-widest mb-2 pl-1 font-bold" style={{ color: colors[stat.lane] }}>
              {stat.lane.replace('_', ' ')}
            </div>
            <div className="flex flex-col gap-1 pl-1">
              <div className="flex justify-between items-baseline">
                 <span className="text-[9px] text-[var(--muted)]">AVG</span>
                 <span className="text-sm font-bold text-white">{stat.avg}</span>
              </div>
              <div className="flex justify-between items-baseline">
                 <span className="text-[9px] text-[var(--muted)]">PEAK</span>
                 <span className="text-sm font-bold text-white">{stat.peak}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
