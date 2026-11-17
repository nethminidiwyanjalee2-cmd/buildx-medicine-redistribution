import React from 'react'

export default function KPICards({ summary }) {
  if (!summary) return null

  return (
    <div className="kpi-grid">
      <div className="kpi-card">
        <div className="kpi-label">Monitored Items</div>
        <div className="kpi-value" style={{ color: '#0f172a' }}>
          {summary.total_monitored_items || 0}
        </div>
        <div className="kpi-desc">Across 4 healthcare facilities</div>
      </div>

      <div className="kpi-card" style={{ borderLeft: '4px solid var(--danger)' }}>
        <div className="kpi-label" style={{ color: 'var(--danger)' }}>Critical Shortages</div>
        <div className="kpi-value" style={{ color: 'var(--danger)' }}>
          {summary.critical_count || 0}
        </div>
        <div className="kpi-desc">&lt; 3.0 days stock remaining</div>
      </div>

      <div className="kpi-card" style={{ borderLeft: '4px solid var(--warning)' }}>
        <div className="kpi-label" style={{ color: 'var(--warning)' }}>Warning Threshold</div>
        <div className="kpi-value" style={{ color: 'var(--warning)' }}>
          {summary.warning_count || 0}
        </div>
        <div className="kpi-desc">&lt; 7.0 days stock remaining</div>
      </div>

      <div className="kpi-card" style={{ borderLeft: '4px solid var(--primary)' }}>
        <div className="kpi-label" style={{ color: 'var(--primary-dark)' }}>Excess Stockpiles</div>
        <div className="kpi-value" style={{ color: 'var(--primary-dark)' }}>
          {summary.excess_count || 0}
        </div>
        <div className="kpi-desc">&gt; 30.0 days transferable surplus</div>
      </div>

      <div className="kpi-card" style={{ borderLeft: '4px solid var(--success)' }}>
        <div className="kpi-label" style={{ color: 'var(--success)' }}>Transferable Surplus</div>
        <div className="kpi-value" style={{ color: 'var(--success)' }}>
          {(summary.total_transferable_surplus_units || 0).toLocaleString()}
        </div>
        <div className="kpi-desc">Units ready for redistribution</div>
      </div>
    </div>
  )
}
