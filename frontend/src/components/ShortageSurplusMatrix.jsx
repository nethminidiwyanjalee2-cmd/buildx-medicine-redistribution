import React from 'react'

export default function ShortageSurplusMatrix({ summary }) {
  if (!summary) return null

  const criticalItems = summary.critical_items || []
  const excessItems = summary.excess_items || []

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
      {/* Deficit Column */}
      <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '10px', padding: '22px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #fee2e2', paddingBottom: '12px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--danger)' }}>
              🚨 Deficit Sites (Immediate Shortage Risk)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Facilities with &lt; 3.0 days supply requiring urgent replenishment
            </p>
          </div>
          <span className="badge badge-critical">{criticalItems.length} Sites</span>
        </div>

        {criticalItems.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', padding: '16px 0' }}>
            No critical stock shortages currently detected across the network.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {criticalItems.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: '#fef2f2',
                  border: '1px solid #fecaca',
                  borderRadius: '8px',
                  padding: '12px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#991b1b', fontSize: '14px' }}>{item.medicine_name}</strong>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--danger)' }}>
                    {item.days_to_depletion.toFixed(1)} days left
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#4b5563', marginTop: '4px' }}>
                  Location: <strong>{item.facility_name}</strong> ({item.facility_id})
                </div>
                <div style={{ fontSize: '12px', color: '#7f1d1d', marginTop: '4px' }}>
                  Current Stock: <strong>{item.current_stock.toLocaleString()} units</strong> · Deficit: <strong>+{item.deficit_units.toLocaleString()} units needed</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Surplus Column */}
      <div style={{ background: '#fff', border: '1px solid var(--border)', borderRadius: '10px', padding: '22px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', borderBottom: '1px solid #e0f2fe', paddingBottom: '12px' }}>
          <div>
            <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--primary-dark)' }}>
              📦 Surplus Stockpiles (Donor Facilities)
            </h3>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Facilities with &gt; 30.0 days supply carrying safe transferable stock
            </p>
          </div>
          <span className="badge badge-excess">{excessItems.length} Sites</span>
        </div>

        {excessItems.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '13px', padding: '16px 0' }}>
            No excess inventories detected available for transfer.
          </p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {excessItems.map((item, idx) => (
              <div
                key={idx}
                style={{
                  background: '#f0f9ff',
                  border: '1px solid #bae6fd',
                  borderRadius: '8px',
                  padding: '12px 14px',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ color: '#0369a1', fontSize: '14px' }}>{item.medicine_name}</strong>
                  <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary-dark)' }}>
                    {item.days_to_depletion.toFixed(1)} days stock
                  </span>
                </div>
                <div style={{ fontSize: '12px', color: '#4b5563', marginTop: '4px' }}>
                  Donor: <strong>{item.facility_name}</strong> ({item.facility_id})
                </div>
                <div style={{ fontSize: '12px', color: '#075985', marginTop: '4px' }}>
                  Total Stock: <strong>{item.current_stock.toLocaleString()} units</strong> · Transferable: <strong>{item.surplus_units.toLocaleString()} units surplus</strong>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
