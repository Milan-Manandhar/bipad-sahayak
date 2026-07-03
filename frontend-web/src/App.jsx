import React, { useState, useEffect } from 'react'

export default function App() {
  const [health, setHealth] = useState(null)
  const [status, setStatus] = useState(null)
  const [alerts, setAlerts] = useState([])
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  
  useEffect(() => {
    // Fetch backend health
    fetch('http://localhost:8000/health')
      .then(res => res.json())
      .then(data => setHealth(data))
      .catch(() => setHealth({ status: 'error', message: 'Backend not connected' }))

    fetch('http://localhost:8000/status')
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(() => {})

    // Mock active alerts
    setAlerts([
      { id: 1, title: "🟠 बाढी चेतावनी", district: "सिन्धुपाल्चोक", severity: "orange" },
      { id: 2, title: "🟡 पहिरो सावधानी", district: "कास्की", severity: "yellow" }
    ])
  }, [])

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Top Bar */}
      <div className="bg-slate-900 border-b border-slate-800 px-8 py-4 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-red-600 rounded-2xl flex items-center justify-center">
            <span className="text-2xl font-bold">बि</span>
          </div>
          <div>
            <div className="font-bold text-2xl">AI बिपद सहायक</div>
            <div className="text-xs text-slate-400">Nepal's AI Disaster Platform</div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="px-4 py-1.5 bg-emerald-900/40 text-emerald-400 rounded-2xl text-sm flex items-center gap-2">
            <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
            LIVE • NEPAL
          </div>
          <div className="text-sm text-slate-400">२०८३ असार १७ • १५:५२</div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto p-8">
        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-900 p-5 rounded-3xl">
            <div className="text-xs text-slate-400">People Under Alert</div>
            <div className="text-4xl font-semibold text-red-400 mt-1">42,180</div>
          </div>
          <div className="bg-slate-900 p-5 rounded-3xl">
            <div className="text-xs text-slate-400">Active Alerts</div>
            <div className="text-4xl font-semibold mt-1">{alerts.length}</div>
          </div>
          <div className="bg-slate-900 p-5 rounded-3xl">
            <div className="text-xs text-slate-400">Rivers Monitored</div>
            <div className="text-4xl font-semibold mt-1 text-emerald-400">22</div>
          </div>
          <div className="bg-slate-900 p-5 rounded-3xl">
            <div className="text-xs text-slate-400">Districts Covered</div>
            <div className="text-4xl font-semibold mt-1">77</div>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-6">
          {/* Left: Alerts */}
          <div className="col-span-2 bg-slate-900 rounded-3xl p-6">
            <div className="flex justify-between items-center mb-5">
              <div className="font-semibold text-xl flex items-center gap-2">
                🔔 सक्रिय अलर्टहरू
              </div>
              <div className="text-xs px-3 py-1 bg-red-600 rounded-full">{alerts.length}</div>
            </div>

            {alerts.map((alert, i) => (
              <div key={i} className="mb-4 p-4 bg-slate-800 rounded-2xl border-l-4 border-orange-500">
                <div className="font-medium">{alert.title}</div>
                <div className="text-sm text-slate-400 mt-1">{alert.district} जिल्ला</div>
                <div className="text-xs text-emerald-400 mt-2">Just now • 12,450 people affected</div>
              </div>
            ))}

            <button 
              onClick={() => alert('Alert creation modal would open here')}
              className="w-full mt-4 py-3 bg-red-600 hover:bg-red-700 rounded-2xl font-medium"
            >
              + नयाँ अलर्ट जारी गर्नुहोस्
            </button>
          </div>

          {/* Right: Map Placeholder + Status */}
          <div className="col-span-3 bg-slate-900 rounded-3xl p-6">
            <div className="font-semibold text-xl mb-4">🗺️ नेपाल नक्सा - जोखिम तह</div>
            
            <div className="bg-slate-950 rounded-2xl h-[380px] flex items-center justify-center relative overflow-hidden">
              <div className="text-center">
                <div className="text-6xl mb-4">🗺️</div>
                <div className="text-xl font-semibold">Interactive Nepal Map</div>
                <div className="text-sm text-slate-400 mt-2">77 districts • Color-coded risk levels</div>
                
                <div className="mt-8 grid grid-cols-4 gap-2 text-xs max-w-xs mx-auto">
                  <div className="bg-emerald-600 py-1 rounded">LOW</div>
                  <div className="bg-yellow-500 py-1 rounded">MEDIUM</div>
                  <div className="bg-orange-600 py-1 rounded">HIGH</div>
                  <div className="bg-red-700 py-1 rounded">CRITICAL</div>
                </div>
              </div>
            </div>

            <div className="mt-4 text-xs text-slate-400 flex justify-between">
              <div>✅ Backend connected: {health?.message}</div>
              <div>22 rivers • 10 DHM stations</div>
            </div>
          </div>
        </div>

        {/* River Status */}
        <div className="mt-8 bg-slate-900 rounded-3xl p-6">
          <div className="font-semibold text-xl mb-4">🌊 नदी स्तर (Real-time)</div>
          <div className="grid grid-cols-4 gap-4">
            {[
              { name: "कोशी", level: "6.82m", status: "WARNING", color: "orange" },
              { name: "बागमती", level: "2.34m", status: "WATCH", color: "yellow" },
              { name: "कर्णाली", level: "5.9m", status: "NORMAL", color: "emerald" },
              { name: "नारायणी", level: "4.1m", status: "NORMAL", color: "emerald" }
            ].map((river, i) => (
              <div key={i} className="bg-slate-800 p-4 rounded-2xl">
                <div className="flex justify-between">
                  <div>
                    <div className="font-medium">{river.name}</div>
                    <div className="text-2xl font-mono mt-1">{river.level}</div>
                  </div>
                  <div className={`text-xs px-3 py-1 h-fit rounded-full bg-${river.color}-600`}>{river.status}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
