import React, { useState } from 'react'

export default function StockTable({
  inventory,
  facilities,
  onConsume,
  onSpike,
}) {
  const [selectedFacility, setSelectedFacility] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [selectedRisk, setSelectedRisk] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  // Unique categories
  const categories = Array.from(new Set(inventory.map((i) => i.category))).filter(Boolean)

  const filteredItems = inventory.filter((item) => {
    if (selectedFacility && item.facility_id !== selectedFacility) return false
    if (selectedCategory && item.category !== selectedCategory) return false
    if (selectedRisk && item.risk_level !== selectedRisk) return false
    if (searchTerm) {
      const q = searchTerm.toLowerCase()
      const med = (item.medicine_name || '').toLowerCase()
      const fac = (item.facility_name || '').toLowerCase()
      const cat = (item.category || '').toLowerCase()
      if (!med.includes(q) && !fac.includes(q) && !cat.includes(q)) return false
    }
    return true
  })

  const getRiskBadge = (level) => {
    switch (level) {
      case 'CRITICAL':
        return <span className="badge badge-critical">● Critical</span>
      case 'WARNING':
        return <span className="badge badge-warning">▲ Warning</span>
      case 'EXCESS':
        return <span className="badge badge-excess">★ Excess</span>
      default:
        return <span className="badge badge-ok">✓ Stable</span>
    }
  }

  const getTrendIcon = (trend) => {
    if (trend === 'increasing') return <span title="Increasing consumption" style={{ color: 'var(--danger)' }}>↗ Rising</span>
    if (trend === 'decreasing') return <span title="Decreasing consumption" style={{ color: 'var(--success)' }}>↘ Falling</span>
    return <span title="Stable trend" style={{ color: 'var(--text-muted)' }}>→ Stable</span>
  }

  return (
    <div>
      {/* Filter Toolbar */}
      <div className="filter-bar">
        <div className="filter-group">
          <label className="filter-label">Healthcare Facility</label>
          <select
            className="filter-select"
            value={selectedFacility}
            onChange={(e) => setSelectedFacility(e.target.value)}
          >
            <option value="">All Facilities ({facilities.length})</option>
            {facilities.map((f) => (
              <option key={f.id} value={f.id}>
                {f.name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Therapeutic Category</label>
          <select
            className="filter-select"
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
          >
            <option value="">All Categories ({categories.length})</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label className="filter-label">Risk Classification</label>
          <select
            className="filter-select"
            value={selectedRisk}
            onChange={(e) => setSelectedRisk(e.target.value)}
          >
            <option value="">All Risk Levels</option>
            <option value="CRITICAL">Critical Shortage (&lt;3d)</option>
            <option value="WARNING">Low Stock Warning (&lt;7d)</option>
            <option value="OK">Stable Stock</option>
            <option value="EXCESS">Excess Stockpile (&gt;30d)</option>
          </select>
        </div>

        <div className="filter-group" style={{ flex: '1 1 200px' }}>
          <label className="filter-label">Quick Search</label>
          <input
            type="text"
            className="filter-input"
            style={{ width: '100%' }}
            placeholder="Search medicine, category, or facility…"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {(selectedFacility || selectedCategory || selectedRisk || searchTerm) && (
          <button
            className="btn btn-secondary"
            style={{ alignSelf: 'flex-end', height: '36px' }}
            onClick={() => {
              setSelectedFacility('')
              setSelectedCategory('')
              setSelectedRisk('')
              setSearchTerm('')
            }}
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Table Container */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Facility</th>
              <th>Medicine</th>
              <th>Category</th>
              <th>Stock On Hand</th>
              <th>Burn Rate</th>
              <th>Runway</th>
              <th>Risk Status</th>
              <th>Trend</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredItems.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '32px', color: 'var(--text-muted)' }}>
                  No inventory records matching active filter criteria.
                </td>
              </tr>
            ) : (
              filteredItems.map((item) => {
                const isCrit = item.risk_level === 'CRITICAL'
                const isWarn = item.risk_level === 'WARNING'
                const days = item.days_to_depletion

                return (
                  <tr key={`${item.facility_id}-${item.medicine_id}`}>
                    <td>
                      <div style={{ fontWeight: 600 }}>{item.facility_name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.facility_id}</div>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: '#0f172a' }}>{item.medicine_name}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.dosage_form}</div>
                    </td>
                    <td>
                      <span style={{ fontSize: '12px', background: '#f1f5f9', padding: '2px 8px', borderRadius: '4px' }}>
                        {item.category}
                      </span>
                    </td>
                    <td>
                      <strong>{(item.current_stock || 0).toLocaleString()}</strong>{' '}
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{item.unit}</span>
                      {item.deficit_units > 0 && (
                        <div style={{ fontSize: '11px', color: 'var(--danger)', fontWeight: 600 }}>
                          Deficit: -{item.deficit_units}
                        </div>
                      )}
                      {item.surplus_units > 0 && (
                        <div style={{ fontSize: '11px', color: 'var(--primary-dark)', fontWeight: 600 }}>
                          Surplus: +{item.surplus_units}
                        </div>
                      )}
                    </td>
                    <td>
                      <span>{item.avg_daily_consumption}</span>{' '}
                      <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>/day</span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 700, fontSize: '13px', color: isCrit ? 'var(--danger)' : isWarn ? 'var(--warning)' : 'inherit' }}>
                          {days >= 900 ? '∞' : `${days.toFixed(1)}d`}
                        </span>
                      </div>
                      <div style={{ width: '80px', height: '5px', background: '#e2e8f0', borderRadius: '3px', overflow: 'hidden', marginTop: '3px' }}>
                        <div
                          style={{
                            width: `${Math.min(100, (days / 30) * 100)}%`,
                            height: '100%',
                            background: isCrit ? 'var(--danger)' : isWarn ? 'var(--warning)' : days > 30 ? 'var(--primary)' : 'var(--success)',
                          }}
                        />
                      </div>
                    </td>
                    <td>{getRiskBadge(item.risk_level)}</td>
                    <td style={{ fontSize: '12px' }}>{getTrendIcon(item.trend)}</td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '6px' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          title="Record medication dispensing"
                          onClick={() => onConsume(item.facility_id, item.medicine_id, item.avg_daily_consumption || 15)}
                        >
                          - Dispense
                        </button>
                        <button
                          className="btn btn-secondary btn-sm"
                          title="Simulate sudden demand spike (outbreak surge)"
                          style={{ color: '#d97706' }}
                          onClick={() => onSpike(item.facility_id, item.medicine_id)}
                        >
                          ⚡ Spike
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
