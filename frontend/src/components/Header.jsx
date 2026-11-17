import React from 'react'

export default function Header({ dbMode, onResetSeed, isResetting }) {
  return (
    <header className="app-header">
      <div>
        <h1 className="brand-title">
          <span>MediStock</span>
          <span className="brand-badge">BuildX 0.1 · Challenge 03</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '13px', marginTop: '2px' }}>
          Intelligent Medicine Stock Monitoring, Forecasting & Multi-Facility Redistribution
        </p>
      </div>

      <div className="header-meta">
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', background: '#ffffff', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#16a34a' }}></span>
          <span style={{ color: 'var(--text-muted)' }}>Storage Mode:</span>
          <strong>{dbMode || 'json_fallback'}</strong>
        </div>

        <button
          className="btn btn-secondary"
          onClick={onResetSeed}
          disabled={isResetting}
          title="Reset all facilities, inventory, and consumption to deterministic seed baseline"
        >
          🔄 {isResetting ? 'Resetting…' : 'Reset Seed Data'}
        </button>
      </div>
    </header>
  )
}
