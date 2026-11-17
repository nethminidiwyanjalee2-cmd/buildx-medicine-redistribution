import React, { useState } from 'react'

export default function RedistributionPanel({
  recommendations,
  onRunOptimiser,
  onExecuteTransfer,
  isRunning,
}) {
  const [strategy, setStrategy] = useState('priority_greedy')
  const [executingId, setExecutingId] = useState(null)

  const handleExecute = async (id) => {
    setExecutingId(id)
    await onExecuteTransfer(id)
    setExecutingId(null)
  }

  return (
    <div>
      {/* Strategy Control Bar */}
      <div className="filter-bar" style={{ justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div className="filter-group">
            <label className="filter-label">Optimization Strategy</label>
            <select
              className="filter-select"
              value={strategy}
              onChange={(e) => setStrategy(e.target.value)}
            >
              <option value="priority_greedy">Priority-Greedy Allocation (Urgent First)</option>
              <option value="proportional_fairness">Proportional Fairness (Balanced Sharing)</option>
            </select>
          </div>
          <div style={{ fontSize: '13px', color: 'var(--text-muted)', maxWidth: '420px', marginTop: '16px' }}>
            {strategy === 'priority_greedy'
              ? 'Fulfills the most critical shortages first until donor surplus is exhausted.'
              : 'Shares available donor surplus proportionally across multiple deficit facilities.'}
          </div>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => onRunOptimiser(strategy)}
          disabled={isRunning}
          style={{ height: '40px', alignSelf: 'center' }}
        >
          ⚙️ {isRunning ? 'Computing Routes…' : 'Run Redistribution Optimiser'}
        </button>
      </div>

      {/* Recommendations Cards */}
      {recommendations.length === 0 ? (
        <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '10px', padding: '40px', textAlign: 'center' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>⚖️</div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a', marginBottom: '8px' }}>
            No Active Redistribution Recommendations
          </h3>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', maxWidth: '480px', margin: '0 auto 20px' }}>
            Either all inventories are currently balanced, or the optimiser has not been triggered yet.
            Click the button above to run the multi-facility matching engine.
          </p>
          <button className="btn btn-primary" onClick={() => onRunOptimiser(strategy)}>
            Run Optimiser Now
          </button>
        </div>
      ) : (
        <div className="reco-grid">
          {recommendations.map((rec) => {
            const isUrgent = rec.urgency === 'HIGH'
            const isExecuted = rec.status === 'EXECUTED'

            return (
              <div
                key={rec.id}
                className={`reco-card ${isUrgent && !isExecuted ? 'urgent' : ''}`}
                style={{ opacity: isExecuted ? 0.75 : 1 }}
              >
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
                      {rec.id}
                    </span>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      <span className={`badge ${isUrgent ? 'badge-critical' : 'badge-warning'}`}>
                        {rec.urgency} URGENCY
                      </span>
                      {isExecuted && (
                        <span className="badge badge-ok">✓ EXECUTED</span>
                      )}
                    </div>
                  </div>

                  {/* Visual Route */}
                  <div className="reco-route">
                    <div className="reco-fac-box">
                      <div className="reco-fac-type">DONOR FACILITY</div>
                      <div className="reco-fac-name" style={{ color: '#0369a1' }}>
                        {rec.from_facility_name}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        ID: {rec.from_facility_id}
                      </div>
                    </div>

                    <div className="reco-arrow">
                      ➜
                    </div>

                    <div className="reco-fac-box" style={{ textAlign: 'right' }}>
                      <div className="reco-fac-type">RECIPIENT FACILITY</div>
                      <div className="reco-fac-name" style={{ color: '#dc2626' }}>
                        {rec.to_facility_name}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                        ID: {rec.to_facility_id}
                      </div>
                    </div>
                  </div>

                  {/* Medicine & Quantity Pill */}
                  <div style={{ background: '#f8fafc', border: '1px solid var(--border)', borderRadius: '8px', padding: '12px', marginBottom: '14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>MEDICATION</div>
                      <div style={{ fontSize: '14px', fontWeight: 700 }}>{rec.medicine_name}</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>TRANSFER QUANTITY</div>
                      <div style={{ fontSize: '18px', fontWeight: 800, color: 'var(--primary-dark)' }}>
                        {rec.quantity.toLocaleString()} units
                      </div>
                    </div>
                  </div>

                  {/* Impact Projection */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', marginBottom: '14px', background: '#f0fdf4', padding: '8px 12px', borderRadius: '6px', border: '1px solid #bbf7d0' }}>
                    <div>
                      Recipient Runway Extends To: <strong>~{rec.projected_recipient_days} days</strong>
                    </div>
                    <div>
                      Donor Retains Safe Runway: <strong>~{rec.projected_donor_days} days</strong>
                    </div>
                  </div>

                  {/* Plain Language Reasoning */}
                  <div className="reco-reason">
                    <strong>Algorithmic Rationale:</strong> {rec.reason}
                  </div>
                </div>

                {/* Action button */}
                <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end' }}>
                  {isExecuted ? (
                    <span style={{ fontSize: '13px', color: 'var(--success)', fontWeight: 600 }}>
                      ✓ Stock transfer applied
                    </span>
                  ) : (
                    <button
                      className="btn btn-primary"
                      onClick={() => handleExecute(rec.id)}
                      disabled={executingId === rec.id}
                    >
                      {executingId === rec.id ? 'Applying Transfer…' : 'Approve & Execute Transfer'}
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
