'use client'

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine, CartesianGrid } from 'recharts'

const COLORS = {
  temperature_C: '#f59e0b',
  vibration_mm_s: '#3b82f6',
  rpm: '#10b981',
  current_A: '#a78bfa',
}

const METRIC_LABELS = {
  temperature_C: 'Temperature',
  vibration_mm_s: 'Vibration',
  rpm: 'Motor RPM',
  current_A: 'Current Draw'
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-card px-4 py-2 border-white/10 shadow-2xl"
        style={{ background: 'rgba(15, 23, 42, 0.9)', color: 'var(--text-secondary)' }}>
        {payload.map((p) => (
          <div key={p.dataKey} className="flex gap-3 items-center">
            <span className="w-2 h-2 rounded-full shadow-[0_0_8px_rgba(255,255,255,0.5)]" style={{ background: p.color }} />
            <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>{METRIC_LABELS[p.dataKey] || p.name}</span>
            <span style={{ color: 'var(--text-primary)' }} className="text-sm font-black font-mono">
              {typeof p.value === 'number' ? p.value.toFixed(2) : p.value}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

export default function SensorChart({ machineId, history, metric = 'temperature_C', threshold }) {
  const data = (history || []).slice(-60).map((r, i) => ({
    t: i,
    value: r[metric],
  }))

  const color = COLORS[metric] || '#3b82f6'
  const label = METRIC_LABELS[metric] || 'Sensor'

  return (
    <div className="glass-card bg-white/[0.01] border-white/5 p-5 flex flex-col gap-4 overflow-hidden relative group">
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-2.5 h-2.5 rounded-full" style={{ background: color, boxShadow: `0 0 12px ${color}` }} />
          <div>
            <span className="text-[10px] font-black uppercase tracking-[0.2em]" style={{ color: 'var(--text-muted)' }}>Metric Focus</span>
            <h3 className="text-sm font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>{label} Telemetry</h3>
          </div>
        </div>
        <div className="text-right">
          <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Real-time</p>
          <span className="text-lg font-black font-mono tracking-tighter" style={{ color }}>
            {data.length > 0 ? (data[data.length - 1]?.value || 0).toFixed(2) : '0.00'}
          </span>
        </div>
      </div>

      <div className="h-24 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id={`gradient-${metric}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3}/>
                <stop offset="95%" stopColor={color} stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.03)" />
            <XAxis dataKey="t" hide />
            <YAxis hide domain={['auto', 'auto']} />
            <Tooltip content={<CustomTooltip />} />
            {threshold && <ReferenceLine y={threshold} stroke="#ef4444" strokeDasharray="4 4" strokeOpacity={0.5} />}
            <Area
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={3}
              fillOpacity={1}
              fill={`url(#gradient-${metric})`}
              isAnimationActive={false}
              name={label}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
