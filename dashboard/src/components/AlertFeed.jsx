'use client'

const SEV_STYLE = {
  LOW:      { bg: 'rgba(16,185,129,0.05)', border: 'rgba(16,185,129,0.2)', color: '#10b981', icon: '🟢' },
  MEDIUM:   { bg: 'rgba(245,158,11,0.05)', border: 'rgba(245,158,11,0.25)', color: '#f59e0b', icon: '🟡' },
  HIGH:     { bg: 'rgba(249,115,22,0.05)', border: 'rgba(249,115,22,0.3)', color: '#f97316', icon: '🟠' },
  CRITICAL: { bg: 'rgba(239,68,68,0.08)',  border: 'rgba(239,68,68,0.35)', color: '#ef4444', icon: '🔴' },
}

export default function AlertFeed({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center glass-card border-dashed border-white/5 opacity-60">
        <div className="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center text-2xl mb-4 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.1)]">
          🛡️
        </div>
        <p className="text-xs font-black uppercase tracking-[0.2em] text-emerald-400">System Nominal</p>
        <p className="text-[10px] uppercase font-bold mt-1" style={{ color: 'var(--text-muted)' }}>Security Protocol Active</p>
      </div>
    )
  }

  return (
    <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
      {alerts.map((alert, i) => {
        const sev = alert.severity || 'LOW'
        const cfg = SEV_STYLE[sev] || SEV_STYLE.LOW

        return (
          <div key={i}
            className="glass-card p-4 animate-slide-in relative overflow-hidden group hover:bg-white/[0.03] transition-all"
            style={{ background: cfg.bg, borderColor: cfg.border }}>
            <div className="flex items-start gap-4 relative z-10">
              <span className="text-xl mt-0.5 animate-float">{cfg.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-black uppercase tracking-widest" style={{ color: cfg.color }}>{sev}</span>
                    <span className="text-xs font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                      UNIT-{alert.machine_id}
                    </span>
                  </div>
                  <span className="text-[10px] font-black font-mono" style={{ color: 'var(--text-muted)' }}>
                    RISK <span style={{ color: cfg.color }}>{((alert.risk_score || 0) * 100).toFixed(0)}%</span>
                  </span>
                </div>
                {alert.reason && (
                  <p className="text-[11px] leading-relaxed font-medium mb-2 pr-4" style={{ color: 'var(--text-secondary)' }}>
                    {alert.reason.split('\n').filter(l => l.includes('•'))[0]?.replace('•', '→') || alert.reason.slice(0, 100)}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1.5 grayscale opacity-50 group-hover:grayscale-0 group-hover:opacity-100 transition-all">
                    <span className="w-1 h-1 rounded-full bg-blue-500"></span>
                    <span className="text-[9px] font-bold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Automated ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</span>
                  </div>
                  <p className="text-[10px] font-black font-mono" style={{ color: 'var(--text-muted)' }}>
                    {new Date(alert.timestamp || Date.now()).toLocaleTimeString([], { hour12: false })}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
