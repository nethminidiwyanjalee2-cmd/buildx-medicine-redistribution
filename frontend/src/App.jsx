import React, { useState, useEffect } from 'react'
import Disclaimer from './components/Disclaimer'

const styles = {
  container: {
    maxWidth: '860px',
    margin: '0 auto',
    padding: '32px 20px',
  },
  header: {
    marginBottom: '32px',
    borderBottom: '2px solid #e2e8f0',
    paddingBottom: '16px',
  },
  h1: {
    fontSize: '28px',
    fontWeight: '700',
    color: '#0f172a',
    marginBottom: '4px',
  },
  subtitle: {
    color: '#64748b',
    fontSize: '15px',
  },
  section: {
    background: '#ffffff',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '20px 24px',
    marginBottom: '20px',
  },
  h2: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#334155',
    marginBottom: '12px',
  },
  pre: {
    background: '#f1f5f9',
    border: '1px solid #cbd5e1',
    borderRadius: '4px',
    padding: '12px 16px',
    fontSize: '13px',
    overflowX: 'auto',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
    color: '#1e293b',
    fontFamily: "'Cascadia Code', 'Fira Code', 'Consolas', monospace",
  },
  status_ok: {
    display: 'inline-block',
    background: '#dcfce7',
    color: '#166534',
    borderRadius: '4px',
    padding: '2px 10px',
    fontSize: '13px',
    fontWeight: '600',
    marginBottom: '12px',
  },
  status_err: {
    display: 'inline-block',
    background: '#fee2e2',
    color: '#991b1b',
    borderRadius: '4px',
    padding: '2px 10px',
    fontSize: '13px',
    fontWeight: '600',
    marginBottom: '12px',
  },
  loading: {
    color: '#94a3b8',
    fontSize: '14px',
  },
  badge: {
    display: 'inline-block',
    background: '#dbeafe',
    color: '#1e40af',
    borderRadius: '999px',
    padding: '2px 10px',
    fontSize: '12px',
    fontWeight: '500',
    marginLeft: '8px',
  },
}

export default function App() {
  const [health, setHealth] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/health')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => {
        setHealth(data)
        setLoading(false)
      })
      .catch((e) => {
        setError(e.message)
        setLoading(false)
      })
  }, [])

  return (
    <div style={styles.container}>
      {/* Mandatory disclaimer — must appear on every page */}
      <Disclaimer />

      <header style={styles.header}>
        <h1 style={styles.h1}>
          MediStock
          <span style={styles.badge}>Phase 0</span>
        </h1>
        <p style={styles.subtitle}>
          Intelligent Medicine Stock Monitoring and Redistribution
          &nbsp;·&nbsp; BuildX 0.1 — Challenge 03
        </p>
      </header>

      <section style={styles.section}>
        <h2 style={styles.h2}>Backend Health Check</h2>
        {loading && <p style={styles.loading}>Checking backend…</p>}
        {error && (
          <>
            <span style={styles.status_err}>Unreachable</span>
            <p style={{ color: '#dc2626', fontSize: '14px' }}>
              Could not reach <code>/api/health</code>: {error}
            </p>
            <p style={{ color: '#64748b', fontSize: '13px', marginTop: '8px' }}>
              Make sure the backend is running:{' '}
              <code>uvicorn app.main:app --reload --port 8000</code>
            </p>
          </>
        )}
        {health && (
          <>
            <span style={styles.status_ok}>● {health.status}</span>
            <pre style={styles.pre}>{JSON.stringify(health, null, 2)}</pre>
          </>
        )}
      </section>

      <section style={styles.section}>
        <h2 style={styles.h2}>What comes next</h2>
        <ul style={{ paddingLeft: '20px', fontSize: '14px', color: '#475569', lineHeight: '2' }}>
          <li>
            <strong>Phase 1:</strong> Inventory table per facility with
            colour-coded risk levels and days-to-depletion
          </li>
          <li>
            <strong>Phase 2:</strong> Redistribution recommendation panel with
            plain-language reasons
          </li>
          <li>
            <strong>Phase 3:</strong> Expiry tracking, demand-spike simulation,
            comparative strategy analysis
          </li>
        </ul>
      </section>
    </div>
  )
}
