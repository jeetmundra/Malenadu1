'use client'

import { useState, useEffect } from 'react'

export default function Navbar({ connected, machineCount }) {
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  return (
    <nav className="sticky top-0 z-50 px-6 py-4 flex items-center justify-between glass-card"
      style={{
        borderRadius: '0 0 1rem 1rem',
        borderTop: 'none',
        background: 'rgba(6, 10, 20, 0.7)',
        backdropFilter: 'blur(24px)',
      }}>

      {/* Logo & Brand */}
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg animate-float"
          style={{ 
            background: 'var(--gradient-brand)', 
            boxShadow: '0 0 20px rgba(59,130,246,0.3)',
            border: '1px solid rgba(255,255,255,0.1)'
          }}>
          <span className="animate-pulse-slow">⚡</span>
        </div>
        <div>
          <h1 className="text-lg font-black tracking-tight gradient-text">PredictAI</h1>
          <p className="text-[10px] uppercase tracking-[0.2em] font-bold" style={{ color: 'var(--text-muted)' }}>
            Agentic Monitoring Suite
          </p>
        </div>
      </div>

      {/* Center — Real-time Stats */}
      <div className="hidden lg:flex items-center gap-6 px-6 py-2 rounded-2xl glass-card border-none bg-white/5">
        <div className="flex flex-col items-center">
          <span className="text-[10px] font-bold text-muted uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>System Time</span>
          <span className="text-sm font-mono font-bold">{time.toLocaleTimeString([], { hour12: false })}</span>
        </div>
        <div className="w-px h-6 bg-white/10" />
        <div className="flex flex-col items-center">
          <span className="text-[10px] font-bold text-muted uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Active Nodes</span>
          <span className="text-sm font-mono font-bold text-[#3b82f6]">{machineCount || 4} units</span>
        </div>
      </div>

      {/* Right — Connection Status & Team */}
      <div className="flex items-center gap-6">
        <div className="hidden md:flex flex-col items-end">
          <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: 'var(--text-muted)' }}>Operator</span>
          <span className="text-xs font-semibold text-secondary">beyondminus</span>
        </div>
        
        <div className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-black uppercase tracking-tighter transition-all duration-500 ${
          connected ? 'ring-glow-green bg-emerald-500/10 text-emerald-400' : 'ring-glow-red bg-red-500/10 text-red-500'
        }`}>
          <span className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400 animate-ping' : 'bg-red-500'}`} />
          {connected ? 'Network Live' : 'Link Broken'}
        </div>
      </div>
    </nav>
  )
}
