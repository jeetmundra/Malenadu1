'use client'

const SEVERITY_CONFIG = {
  HEALTHY: {
    color: 'var(--status-healthy)',
    glow: 'ring-glow-green',
    bg: 'rgba(16, 185, 129, 0.03)',
    border: 'rgba(16, 185, 129, 0.15)',
    label: 'HEALTHY',
    dot: 'bg-[#10b981]',
  },
  LOW: {
    color: 'var(--status-healthy)',
    glow: 'ring-glow-green',
    bg: 'rgba(16, 185, 129, 0.03)',
    border: 'rgba(16, 185, 129, 0.15)',
    label: 'NORMAL',
    dot: 'bg-[#10b981]',
  },
  MEDIUM: {
    color: 'var(--status-warning)',
    glow: 'ring-glow-yellow',
    bg: 'rgba(245, 158, 11, 0.03)',
    border: 'rgba(245, 158, 11, 0.2)',
    label: 'WATCH',
    dot: 'bg-[#f59e0b]',
  },
  HIGH: {
    color: 'var(--status-high)',
    glow: 'ring-glow-orange',
    bg: 'rgba(249, 115, 22, 0.03)',
    border: 'rgba(249, 115, 22, 0.25)',
    label: 'WARNING',
    dot: 'bg-[#f97316]',
  },
  CRITICAL: {
    color: 'var(--status-critical)',
    glow: 'ring-glow-red',
    bg: 'rgba(239, 68, 68, 0.05)',
    border: 'rgba(239, 68, 68, 0.3)',
    label: 'CRITICAL',
    dot: 'bg-[#ef4444]',
  },
}

export default function MachineCard({ machineId, machineName, type, data, onInjectAnomaly }) {
  const severity = data?.risk?.severity || 'HEALTHY'
  const riskScore = data?.risk?.risk_score || 0
  const reading = data?.reading || {}
  const cfg = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.HEALTHY
  const isCritical = severity === 'CRITICAL'

  return (
    <div
      className={`glass-card glass-card-hover p-6 flex flex-col gap-5 ${isCritical ? 'animate-pulse-critical' : ''} ${cfg.glow}`}
      style={{
        background: cfg.bg,
        borderColor: cfg.border,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center text-[10px] font-black font-mono shadow-inner transition-transform duration-300 group-hover:scale-110"
            style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${cfg.border}`, color: cfg.color }}>
            {machineId}
          </div>
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>{type || 'Industrial Console'}</p>
            <p className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>{machineName || 'Predictive Unit'}</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter shadow-sm border ${cfg.glow}`}
          style={{ background: 'rgba(255,255,255,0.03)', borderColor: cfg.border, color: cfg.color }}>
          <span className={`w-1.5 h-1.5 rounded-full ${cfg.dot} ${isCritical ? 'animate-ping' : ''}`} />
          {cfg.label}
        </div>
      </div>

      {/* Main Gauge */}
      <div className="relative pt-2">
        <div className="flex justify-between items-end mb-2">
          <h4 className="text-[10px] font-black uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Anomaly Probability</h4>
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-black font-mono leading-none tracking-tighter" style={{ color: cfg.color }}>
              {(riskScore * 100).toFixed(0)}
            </span>
            <span className="text-xs font-bold" style={{ color: 'var(--text-muted)' }}>%</span>
          </div>
        </div>
        <div className="h-2 rounded-full bg-white/5 border border-white/5 overflow-hidden shadow-inner">
          <div
            className="h-full rounded-full transition-all duration-1000 cubic-bezier(0.4, 0, 0.2, 1)"
            style={{ 
              width: `${riskScore * 100}%`, 
              background: cfg.color, 
              boxShadow: `0 0 12px ${cfg.color}` 
            }}
          />
        </div>
      </div>

      {/* Sensor Grid (Aligned with Official Schema) */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: 'TEMP', value: reading.temperature_C, unit: '°C', icon: '🌡' },
          { label: 'VIB', value: reading.vibration_mm_s, unit: 'mm/s', icon: '📳' },
          { label: 'LOAD', value: reading.rpm, unit: 'RPM', icon: '⚙️' },
          { label: 'CURR', value: reading.current_A, unit: 'A', icon: '⚡' },
        ].map(({ label, value, unit, icon }) => (
          <div key={label} className="glass-card bg-white/[0.02] border-white/5 p-3 hover:bg-white/[0.05] transition-colors group">
            <p className="text-[10px] font-bold mb-1 tracking-widest flex items-center gap-1.5" style={{ color: 'var(--text-muted)' }}>
              <span>{icon}</span> {label}
            </p>
            <p className="text-sm font-black font-mono truncate" style={{ color: 'var(--text-primary)' }}>
              {value != null ? (typeof value === 'number' ? value.toFixed(1) : value) : '—'}
              <span className="text-[10px] font-bold ml-1" style={{ color: 'var(--text-muted)' }}>{unit}</span>
            </p>
          </div>
        ))}
      </div>

      {/* Agent Reasoning (Sub-models) */}
      <div className="space-y-2 py-2 border-t border-white/5">
        <p className="text-[9px] font-black uppercase tracking-[0.2em]" style={{ color: 'var(--text-muted)' }}>Neural Agent Confidence</p>
        {[
          { label: 'Fusion Model', val: data?.risk?.rf_score },
          { label: 'Anomaly Detector', val: data?.risk?.iso_score },
          { label: 'Statistical Baseline', val: data?.risk?.z_score },
        ].map(({ label, val }) => (
          <div key={label} className="flex items-center gap-3">
            <span className="text-[9px] font-bold w-24 shrink-0" style={{ color: 'var(--text-secondary)' }}>{label}</span>
            <div className="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
              <div className="h-full rounded-full transition-all duration-700"
                style={{ width: `${(val || 0) * 100}%`, background: `${cfg.color}80` }} />
            </div>
          </div>
        ))}
      </div>

      {/* Action Trigger */}
      <button
        onClick={() => onInjectAnomaly && onInjectAnomaly(machineId)}
        className="w-full py-3 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all duration-300 hover:brightness-125 active:scale-[0.97] bg-white/5 border border-white/10 text-white/50 hover:text-white"
      >
        <span>⚡ Test Anomaly Logic</span>
      </button>
    </div>
  )
}
