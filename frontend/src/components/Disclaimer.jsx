import React from 'react'

// Exact disclaimer text required by the spec
const DISCLAIMER =
  'Decision-support prototype using simulated data. Not for clinical use.'

const styles = {
  banner: {
    background: '#fef3c7',
    border: '1px solid #f59e0b',
    borderLeft: '4px solid #f59e0b',
    borderRadius: '4px',
    padding: '10px 16px',
    marginBottom: '24px',
    fontSize: '14px',
    color: '#92400e',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
}

/**
 * Disclaimer — renders the mandatory clinical disclaimer banner.
 *
 * This component must appear on every page of the application.
 * The exact text is dictated by docs/PROJECT_CONTEXT.md §12.
 */
export default function Disclaimer() {
  return (
    <div style={styles.banner} role="alert" aria-live="polite">
      <span aria-hidden="true">⚠️</span>
      <span>{DISCLAIMER}</span>
    </div>
  )
}
