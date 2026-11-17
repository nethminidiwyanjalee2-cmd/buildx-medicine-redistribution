import React, { useState, useEffect } from 'react'
import Disclaimer from './components/Disclaimer'
import Header from './components/Header'
import KPICards from './components/KPICards'
import StockTable from './components/StockTable'
import ShortageSurplusMatrix from './components/ShortageSurplusMatrix'
import RedistributionPanel from './components/RedistributionPanel'

export default function App() {
  const [activeTab, setActiveTab] = useState('inventory')
  const [inventory, setInventory] = useState([])
  const [facilities, setFacilities] = useState([])
  const [riskSummary, setRiskSummary] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [dbMode, setDbMode] = useState('json_fallback')
  const [loading, setLoading] = useState(true)
  const [isResetting, setIsResetting] = useState(false)
  const [isOptimising, setIsOptimising] = useState(false)
  const [toast, setToast] = useState(null)

  const showToast = (message) => {
    setToast(message)
    setTimeout(() => setToast(null), 4000)
  }

  // Load all foundational data
  const loadData = async () => {
    try {
      setLoading(true)
      const [healthRes, facRes, invRes, riskRes, recoRes] = await Promise.all([
        fetch('/api/health').then((r) => r.json()),
        fetch('/api/facilities').then((r) => r.json()),
        fetch('/api/inventory').then((r) => r.json()),
        fetch('/api/risk/summary').then((r) => r.json()),
        fetch('/api/recommendations').then((r) => r.json()),
      ])

      setDbMode(healthRes.db_mode || 'json_fallback')
      setFacilities(facRes || [])
      setInventory(invRes || [])
      setRiskSummary(riskRes || null)
      setRecommendations(recoRes || [])
    } catch (err) {
      console.error('Failed to fetch data:', err)
      showToast('⚠️ Could not connect to MediStock backend.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  // Action: Dispense medication
  const handleConsume = async (facilityId, medicineId, units) => {
    try {
      const res = await fetch(`/api/inventory/${facilityId}/${medicineId}/consume`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ units: parseFloat(units), reason: 'Routine clinical dispensing' }),
      })
      if (res.ok) {
        showToast(`Dispensed ${units} units at ${facilityId}`)
        await loadData()
      }
    } catch (err) {
      showToast('Dispensing failed')
    }
  }

  // Action: Simulate demand spike
  const handleSpike = async (facilityId, medicineId) => {
    try {
      const res = await fetch(`/api/inventory/${facilityId}/${medicineId}/spike`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ multiplier: 3.0, duration_days: 5, scenario_name: 'Infectious Outbreak' }),
      })
      if (res.ok) {
        const data = await res.json()
        showToast(`⚡ Demand surge simulated: +${data.spike_units_consumed} units consumed!`)
        await loadData()
      }
    } catch (err) {
      showToast('Spike simulation failed')
    }
  }

  // Action: Run optimiser
  const handleRunOptimiser = async (strategy) => {
    try {
      setIsOptimising(true)
      const res = await fetch('/api/recommendations/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ strategy, min_transfer_units: 10 }),
      })
      if (res.ok) {
        const data = await res.json()
        setRecommendations(data.recommendations || [])
        showToast(`Generated ${data.recommendation_count} redistribution routes (${strategy})`)
        setActiveTab('recommendations')
      }
    } catch (err) {
      showToast('Optimiser failed')
    } finally {
      setIsOptimising(false)
    }
  }

  // Action: Execute stock transfer
  const handleExecuteTransfer = async (recommendationId) => {
    try {
      const res = await fetch('/api/recommendations/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ recommendation_id: recommendationId }),
      })
      if (res.ok) {
        const data = await res.json()
        showToast(`✓ Transfer completed: ${data.transferred_units} units moved to ${data.to_facility}!`)
        await loadData()
      } else {
        const err = await res.json()
        showToast(`Transfer failed: ${err.detail}`)
      }
    } catch (err) {
      showToast('Network error executing transfer')
    }
  }

  // Action: Reset seed baseline
  const handleResetSeed = async () => {
    if (!window.confirm('Reset all stock levels and logs to original deterministic seed data?')) return
    try {
      setIsResetting(true)
      const res = await fetch('/api/seed/reset', { method: 'POST' })
      if (res.ok) {
        showToast('Baseline seed data restored successfully')
        await loadData()
      }
    } catch (err) {
      showToast('Reset failed')
    } finally {
      setIsResetting(false)
    }
  }

  return (
    <div className="container">
      {/* Mandatory Non-Clinical Disclaimer Banner */}
      <Disclaimer />

      {/* Header with DB Status & Reset Action */}
      <Header
        dbMode={dbMode}
        onResetSeed={handleResetSeed}
        isResetting={isResetting}
      />

      {/* Executive KPI Summary */}
      <KPICards summary={riskSummary} />

      {/* Navigation Tabs */}
      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          📊 Medicine Stock Monitor ({inventory.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'matrix' ? 'active' : ''}`}
          onClick={() => setActiveTab('matrix')}
        >
          ⚖️ Shortage vs Surplus Balance
        </button>
        <button
          className={`tab-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
          onClick={() => setActiveTab('recommendations')}
        >
          🚚 Redistribution Plan ({recommendations.length})
        </button>
      </div>

      {/* Tab Panels */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Loading healthcare network data…
        </div>
      ) : (
        <>
          {activeTab === 'inventory' && (
            <StockTable
              inventory={inventory}
              facilities={facilities}
              onConsume={handleConsume}
              onSpike={handleSpike}
            />
          )}

          {activeTab === 'matrix' && (
            <ShortageSurplusMatrix summary={riskSummary} />
          )}

          {activeTab === 'recommendations' && (
            <RedistributionPanel
              recommendations={recommendations}
              onRunOptimiser={handleRunOptimiser}
              onExecuteTransfer={handleExecuteTransfer}
              isRunning={isOptimising}
            />
          )}
        </>
      )}

      {/* Toast feedback */}
      {toast && <div className="toast-notice">{toast}</div>}
    </div>
  )
}
