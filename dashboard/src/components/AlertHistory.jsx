'use client'

import { useState, useEffect } from 'react'

const SEV_STYLE = {
  LOW:      { bg: 'rgba(16,185,129,0.03)', border: 'rgba(16,185,129,0.15)', color: '#10b981', icon: '🟢', glow: 'ring-glow-green' },
  MEDIUM:   { bg: 'rgba(245,158,11,0.03)', border: 'rgba(245,158,11,0.2)', color: '#f59e0b', icon: '🟡', glow: 'ring-glow-yellow' },
  HIGH:     { bg: 'rgba(249,115,22,0.03)', border: 'rgba(249,115,22,0.25)', color: '#f97316', icon: '🟠', glow: 'ring-glow-orange' },
  CRITICAL: { bg: 'rgba(239,68,68,0.05)',  border: 'rgba(239,68,68,0.3)', color: '#ef4444', icon: '🔴', glow: 'ring-glow-red' },
}

export default function AlertHistory() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  const fetchHistory = async () => {
    try {
      const res = await fetch('http://localhost:8000/alerts?limit=20')
      const data = await res.json()
      setHistory(data)
    } catch (err) {
      console.error('Failed to fetch history:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
    const interval = setInterval(fetchHistory, 10000)
    return () => clearInterval(interval)
  }, [])

  if (loading && history.length === 0) {
    return (
      <div className="space-y-4 pr-2">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="h-20 rounded-2xl glass-card shimmer-bg"></div>
        ))}
      </div>
    )
  }

  if (history.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center opacity-40">
        <p className="text-sm font-black uppercase tracking-[0.2em]" style={{ color: 'var(--text-muted)' }}>
          Historical Archives Empty
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3 pr-2 custom-scrollbar max-h-[600px] overflow-y-auto pt-2">
      {history.map((alert, i) => {
        const sev = alert.severity || 'LOW'
        const cfg = SEV_STYLE[sev] || SEV_STYLE.LOW
        const date = new Date(alert.created_at)

        return (
          <div key={alert.alert_id || i}
            className={`glass-card p-4 transition-all duration-300 hover:bg-white/[0.03] group ${cfg.glow}`}
            style={{ background: cfg.bg, borderColor: cfg.border }}>
            <div className="flex items-center gap-5">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl shadow-inner animate-float"
                style={{ background: 'rgba(255,255,255,0.03)', border: `1px solid ${cfg.border}` }}>
                {cfg.icon}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded shadow-sm" 
                          style={{ background: cfg.bg, border: `1px solid ${cfg.border}`, color: cfg.color }}>{sev}</span>
                    <h4 className="text-sm font-black tracking-tight" style={{ color: 'var(--text-primary)' }}>
                      UNIT-{alert.machine_id}
                    </h4>
                  </div>
                  <div className="flex flex-col items-end">
                    <span className="text-[10px] font-black font-mono uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Event Timestamp</span>
                    <span className="text-[11px] font-bold font-mono" style={{ color: 'var(--text-secondary)' }}>
                      {date.toLocaleDateString()} {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false })}
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                  <p className="text-[11px] font-medium italic opacity-80" style={{ color: 'var(--text-secondary)' }}>
                    “{alert.reason?.replace('•', '')?.trim() || 'Anomaly detected in predictive telemetry engine'}”
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-black uppercase tracking-widest text-muted" style={{ color: 'var(--text-muted)' }}>Confidence</span>
                    <span className="text-[11px] font-black font-mono" style={{ color: cfg.color }}>
                   {((alert.risk_score || 0) * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
