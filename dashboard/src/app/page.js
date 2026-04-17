'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import Navbar from '@/components/Navbar'
import MachineCard from '@/components/MachineCard'
import SensorChart from '@/components/SensorChart'
import AlertFeed from '@/components/AlertFeed'
import AlertHistory from '@/components/AlertHistory'
import { useSensorStream } from '@/hooks/useSensorStream'

const MACHINES = [
  { id: 'CNC_01', name: 'CNC Mill - 01', type: 'Bearing Wear Focus' },
  { id: 'CNC_02', name: 'CNC Lathe - 02', type: 'Thermal Runaway Focus' },
  { id: 'PUMP_03', name: 'Hydraulic Pump - 03', type: 'Cavitation Focus' },
  { id: 'CONVEYOR_04', name: 'System Conveyor - 04', type: 'Baseline Unit' },
]

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ─── Local Simulation (Aligned with Official Schema) ──────────────────────────
function generateReading(machineId, injectAnomaly = false) {
  const base = {
    machine_id: machineId,
    timestamp: new Date().toISOString(),
    temperature_C: 60 + Math.random() * 20,
    vibration_mm_s: 0.2 + Math.random() * 0.3,
    rpm: 1400 + Math.random() * 200,
    current_A: 4.5 + Math.random() * 2,
    status: 'running'
  }
  if (injectAnomaly) {
    base.temperature_C = 95 + Math.random() * 15
    base.vibration_mm_s = 5.0 + Math.random() * 4.0
    base.status = 'warning'
  }
  return base
}

// ─── Main Dashboard Page ──────────────────────────────────────────────────────
export default function DashboardPage() {
  const [machineData, setMachineData]   = useState({})
  const [history, setHistory]           = useState({})
  const [alerts, setAlerts]             = useState([])
  const [connected, setConnected]       = useState(false)
  const [useBackend, setUseBackend]     = useState(false)
  const [anomalyMachines, setAnomalyMachines] = useState(new Set())
  const [selectedMachine, setSelectedMachine] = useState('CNC_01')
  const [selectedMetric, setSelectedMetric]   = useState('temperature_C')

  // SSE Streams for all 4 official units
  const streamCNC1 = useSensorStream('CNC_01')
  const streamCNC2 = useSensorStream('CNC_02')
  const streamPUMP3 = useSensorStream('PUMP_03')
  const streamCONV4 = useSensorStream('CONVEYOR_04')

  const handleInjectAnomaly = useCallback((machineId) => {
    setAnomalyMachines(prev => new Set([...prev, machineId]))
    setTimeout(() => {
      setAnomalyMachines(prev => {
        const next = new Set(prev)
        next.delete(machineId)
        return next
      })
    }, 8000)
  }, [])

  // Check Backend Connectivity
  useEffect(() => {
    const tryConnect = async () => {
      try {
        const res = await fetch(`${API_BASE}/alerts?limit=1`)
        if (res.ok) setUseBackend(true)
        setConnected(true)
      } catch {
        setConnected(true)
      }
    }
    tryConnect()
    const timer = setInterval(tryConnect, 10000)
    return () => clearInterval(timer)
  }, [])

  // Sync Backend Streams
  useEffect(() => {
    if (useBackend) {
      const streams = { 
        CNC_01: streamCNC1, 
        CNC_02: streamCNC2, 
        PUMP_03: streamPUMP3, 
        CONVEYOR_04: streamCONV4 
      }
      
      MACHINES.forEach(({ id }) => {
        const data = streams[id]
        if (data && data.reading) {
          setMachineData(prev => ({ ...prev, [id]: data }))
          setHistory(prev => ({
            ...prev,
            [id]: [...(prev[id] || []).slice(-120), data.reading],
          }))
          
          if (data.risk?.severity !== 'LOW') {
             setAlerts(prev => {
               const exists = prev.some(a => a.timestamp === data.reading.timestamp && a.machine_id === id)
               if (exists) return prev
               return [{
                 machine_id: id,
                 severity: data.risk.severity,
                 risk_score: data.risk.risk_score,
                 reason: data.risk.reason || 'Telemetry deviation detected',
                 timestamp: new Date(data.reading.timestamp).getTime()
               }, ...prev].slice(0, 50)
             })
          }
        }
      })
    }
  }, [useBackend, streamCNC1, streamCNC2, streamPUMP3, streamCONV4])

  // Simulation Loop (Fallback)
  useEffect(() => {
    let interval
    if (!useBackend) {
      interval = setInterval(() => {
        MACHINES.forEach(({ id }) => {
          const inject = anomalyMachines.has(id)
          const reading = generateReading(id, inject)
          
          setMachineData(prev => ({ 
            ...prev, 
            [id]: { 
              reading, 
              risk: { severity: inject ? 'HIGH' : 'LOW', risk_score: inject ? 0.85 : 0.05 } 
            } 
          }))
          
          setHistory(prev => ({
            ...prev,
            [id]: [...(prev[id] || []).slice(-120), reading],
          }))

          if (inject) {
            setAlerts(prev => [{
              machine_id: id,
              severity: 'HIGH',
              risk_score: 0.85,
              reason: 'Simulated Anomaly: Critical telemetry threshold breached.',
              timestamp: Date.now(),
            }, ...prev].slice(0, 50))
          }
        })
      }, 1000)
    }
    return () => clearInterval(interval)
  }, [useBackend, anomalyMachines])

  const healthyCount = Object.values(machineData).filter(d => !d?.risk || d?.risk?.severity === 'LOW').length

  return (
    <div className="min-h-screen">
      <Navbar connected={connected} machineCount={MACHINES.length} />

      <main className="px-6 py-6 pb-20 max-w-[1700px] mx-auto animate-fade-in-up">

        {/* Overview Stats */}
        <section className="mb-8 grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'System Logic', value: 'ACTIVE', icon: '🧠', color: 'var(--accent-blue)', sub: 'Neural Engine Online' },
            { label: 'Asset Health', value: `${(healthyCount/MACHINES.length * 100).toFixed(0)}%`, icon: '🌡️', color: 'var(--status-healthy)', sub: `${healthyCount}/${MACHINES.length} Normal` },
            { label: 'Network', value: useBackend ? 'BACKEND' : 'SIMULATED', icon: '📡', color: useBackend ? 'var(--status-healthy)' : 'var(--status-high)', sub: 'Data Source' },
            { label: 'Active Alerts', value: alerts.length, icon: '🚨', color: alerts.length > 0 ? 'var(--status-critical)' : 'var(--text-muted)', sub: 'Pending Review' },
          ].map(({ label, value, icon, color, sub }) => (
            <div key={label} className="glass-card p-5 relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 font-mono text-3xl opacity-10 group-hover:scale-125 transition-transform duration-500">{icon}</div>
              <p className="text-[10px] font-black uppercase tracking-widest mb-1" style={{ color: 'var(--text-muted)' }}>{label}</p>
              <p className="text-2xl font-black tracking-tighter mb-0.5" style={{ color }}>{value}</p>
              <p className="text-[10px] font-bold uppercase tracking-tighter opacity-60">{sub}</p>
            </div>
          ))}
        </section>

        {/* Machine Grid */}
        <section className="mb-10">
          <div className="flex items-center gap-3 mb-4">
             <div className="w-2 h-6 bg-purple-500 rounded-full shadow-[0_0_12px_rgba(139,92,246,0.5)]"></div>
             <h2 className="text-xs font-black uppercase tracking-[0.3em]" style={{ color: 'var(--text-muted)' }}>Official Asset Cluster</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {MACHINES.map(m => (
              <MachineCard
                key={m.id}
                machineId={m.id}
                machineName={m.name}
                type={m.type}
                data={machineData[m.id]}
                onInjectAnomaly={() => handleInjectAnomaly(m.id)}
              />
            ))}
          </div>
        </section>

        {/* Analytics & Alerts */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 items-start">
          <div className="xl:col-span-2 space-y-6">
            <div className="glass-card p-6 min-h-[500px] flex flex-col">
              <header className="flex flex-wrap items-center justify-between gap-4 mb-8">
                <div>
                   <h2 className="text-lg font-black tracking-tight flex items-center gap-3">
                     <span className="animate-spin-slow">📡</span> Predictive Analytics Node
                   </h2>
                   <p className="text-[10px] font-bold uppercase tracking-widest mt-1" style={{ color: 'var(--text-muted)' }}>
                     UNIT: {selectedMachine} | TELEMETRY: {selectedMetric}
                   </p>
                </div>

                <div className="flex gap-2 p-1.5 rounded-xl bg-white/5 border border-white/5">
                  {MACHINES.map(m => (
                    <button key={m.id} onClick={() => setSelectedMachine(m.id)}
                      className={`px-4 py-1.5 rounded-lg text-xs font-black transition-all ${
                        selectedMachine === m.id ? 'bg-blue-500 text-white shadow-[0_0_12px_rgba(59,130,246,0.4)]' : 'text-muted-foreground hover:bg-white/5'
                      }`}>
                      {m.id}
                    </button>
                  ))}
                </div>
              </header>

              <div className="flex-1 min-h-[300px] rounded-2xl bg-black/20 border border-white/5 p-4 mb-6">
                <SensorChart
                  machineId={selectedMachine}
                  history={history[selectedMachine] || []}
                  metric={selectedMetric}
                />
              </div>

              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                {['temperature_C', 'vibration_mm_s', 'rpm', 'current_A'].map(m => (
                  <button key={m} onClick={() => setSelectedMetric(m)}
                    className={`p-4 rounded-xl border transition-all relative overflow-hidden group ${
                      selectedMetric === m ? 'border-purple-500/50 bg-purple-500/10' : 'border-white/5 bg-white/[0.02] hover:bg-white/[0.04]'
                    }`}>
                    <span className={`text-[10px] font-black uppercase tracking-widest block mb-2 ${selectedMetric === m ? 'text-purple-400' : 'text-muted-foreground'}`}>{m.replace('_', ' ')}</span>
                    <p className="text-xl font-black font-mono tracking-tighter relative z-10">
                      {(history[selectedMachine]?.slice(-1)[0]?.[m] || 0).toFixed(1)}
                    </p>
                  </button>
                ))}
              </div>
            </div>

            <div className="glass-card p-6">
               <h2 className="text-xs font-black uppercase tracking-[0.3em] mb-6" style={{ color: 'var(--text-muted)' }}>Historical Performance log</h2>
               <AlertHistory />
            </div>
          </div>

          <div className="xl:col-span-1 glass-card p-6 sticky top-24 self-start">
             <div className="flex items-center justify-between mb-6">
                <h2 className="text-xs font-black uppercase tracking-[0.3em]" style={{ color: 'var(--text-primary)' }}>Live Incident Stream</h2>
                <span className="text-[10px] font-black font-mono px-2 py-0.5 rounded bg-white/5 text-muted-foreground">{alerts.length}</span>
             </div>
             <AlertFeed alerts={alerts} />
          </div>
        </div>

      </main>

      {!useBackend && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 rounded-2xl glass-card bg-orange-500/10 border-orange-500/30 flex items-center gap-4 animate-float">
          <span className="text-2xl">🧪</span>
          <div>
            <p className="text-xs font-black tracking-tight text-orange-400">OFFLINE SIMULATION ACTIVE</p>
            <p className="text-[9px] font-bold uppercase tracking-widest text-orange-400/60">Using fallback telemetry generator</p>
          </div>
        </div>
      )}
    </div>
  )
}
