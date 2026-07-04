import React from 'react'

export default function Sidebar({ config, setConfig, voices, health, clearChat, startTour }) {
  const updateConfig = (key, val) => {
    setConfig(prev => ({ ...prev, [key]: val }))
  }

  const controlStyle = {
    background: 'var(--surface-2)',
    border: '1px solid var(--border)',
    color: 'var(--text)',
    fontFamily: 'var(--font-sans)',
    fontSize: '13px',
    padding: '8px 12px',
    borderRadius: 'var(--radius-sm)',
    width: '100%',
    outline: 'none',
    transition: 'border-color 0.15s'
  }

  const labelStyle = {
    fontFamily: 'var(--font-mono)',
    fontSize: '10px',
    letterSpacing: '2px',
    textTransform: 'uppercase',
    color: 'var(--muted)',
    marginBottom: '8px',
    marginTop: '20px'
  }

  const activeToggleStyle = {
    flex: 1,
    background: 'var(--accent)',
    border: '1px solid var(--accent)',
    color: '#fff',
    fontFamily: 'var(--font-sans)',
    fontSize: '12px',
    padding: '7px',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer'
  }

  const inactiveToggleStyle = {
    flex: 1,
    background: 'transparent',
    border: '1px solid var(--border)',
    color: 'var(--muted)',
    fontFamily: 'var(--font-sans)',
    fontSize: '12px',
    padding: '7px',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer'
  }

  return (
    <aside style={{
      width: '260px',
      minWidth: '260px',
      height: '100vh',
      background: 'var(--surface)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 16px',
      overflowY: 'auto'
    }}>
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ alignSelf: 'center' }}>
              <rect x="2" y="9" width="2" height="6" rx="1" fill="url(#wave-grad)" />
              <rect x="6" y="6" width="2" height="12" rx="1" fill="url(#wave-grad)" style={{ opacity: 0.8 }} />
              <rect x="10" y="3" width="2" height="18" rx="1" fill="url(#wave-grad)" />
              <rect x="14" y="5" width="2" height="14" rx="1" fill="url(#wave-grad)" />
              <rect x="18" y="8" width="2" height="8" rx="1" fill="url(#wave-grad)" style={{ opacity: 0.8 }} />
              <rect x="22" y="10" width="2" height="4" rx="1" fill="url(#wave-grad)" style={{ opacity: 0.6 }} />
              <defs>
                <linearGradient id="wave-grad" x1="2" y1="3" x2="22" y2="21" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="var(--cyan)" />
                  <stop offset="50%" stopColor="var(--accent)" />
                  <stop offset="100%" stopColor="var(--badge-gu)" />
                </linearGradient>
              </defs>
            </svg>
            <h1 style={{
              fontFamily: 'var(--font-display)',
              fontSize: '22px',
              fontWeight: 600,
              color: 'var(--text)',
              letterSpacing: '-0.3px',
              margin: 0
            }}>Vaani</h1>
          </div>
          <button 
            type="button"
            onClick={startTour}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--accent)',
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              cursor: 'pointer',
              outline: 'none',
              padding: '4px 8px',
              borderRadius: 'var(--radius-sm)',
              transition: 'all 0.2s'
            }}
            onMouseEnter={e => e.target.style.color = 'var(--text)'}
            onMouseLeave={e => e.target.style.color = 'var(--accent)'}
          >
            ℹ Tour
          </button>
        </div>
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          color: 'var(--muted)',
          letterSpacing: '2px',
          textTransform: 'uppercase',
          marginTop: '4px'
        }}>Private AI · Offline</p>
      </div>

      <div>
        {/* Whisper Model */}
        <p style={labelStyle}>Model</p>
        <select
          id="tour-model"
          style={controlStyle}
          value={config.whisperModel}
          onChange={(e) => updateConfig('whisperModel', e.target.value)}
          onFocus={e => e.target.style.borderColor = 'var(--accent)'}
          onBlur={e => e.target.style.borderColor = 'var(--border)'}
        >
          <option value="tiny">tiny</option>
          <option value="small">small</option>
          <option value="medium">medium</option>
          <option value="large-v2">large-v2</option>
        </select>

        {/* Recording Mode */}
        <p style={labelStyle}>Recording Mode</p>
        <div id="tour-rec-mode" style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => updateConfig('pttMode', false)}
            style={!config.pttMode ? activeToggleStyle : inactiveToggleStyle}
          >
            Auto
          </button>
          <button
            onClick={() => updateConfig('pttMode', true)}
            style={config.pttMode ? activeToggleStyle : inactiveToggleStyle}
          >
            PTT
          </button>
        </div>

        {/* TTS Enabled & settings */}
        <div id="tour-tts">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '24px' }}>
            <input
              id="tts-enabled-checkbox"
              type="checkbox"
              checked={config.ttsEnabled}
              onChange={(e) => updateConfig('ttsEnabled', e.target.checked)}
              style={{ width: '16px', height: '16px', cursor: 'pointer', accentColor: 'var(--accent)' }}
            />
            <label
              htmlFor="tts-enabled-checkbox"
              style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '13px',
                color: 'var(--text)',
                cursor: 'pointer',
                userSelect: 'none'
              }}
            >
              Enable TTS
            </label>
          </div>

          {config.ttsEnabled && (
            <>
              <p style={labelStyle}>Voice</p>
              <select
                style={controlStyle}
                value={config.voiceId || ''}
                onChange={(e) => updateConfig('voiceId', e.target.value || null)}
                onFocus={e => e.target.style.borderColor = 'var(--accent)'}
                onBlur={e => e.target.style.borderColor = 'var(--border)'}
              >
                <option value="">Default Voice</option>
                {voices.map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>

              {/* Speech speed */}
              <p style={labelStyle}>Speed ({config.ttsRate})</p>
              <input
                type="range"
                min="100"
                max="300"
                step="10"
                value={config.ttsRate}
                onChange={(e) => updateConfig('ttsRate', parseInt(e.target.value))}
                style={{ accentColor: 'var(--accent)', width: '100%' }}
              />

              {/* Volume */}
              <p style={labelStyle}>Volume ({Math.round(config.ttsVolume * 100)}%)</p>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={config.ttsVolume}
                onChange={(e) => updateConfig('ttsVolume', parseFloat(e.target.value))}
                style={{ accentColor: 'var(--accent)', width: '100%' }}
              />
            </>
          )}
        </div>
      </div>

      <div style={{
        marginTop: 'auto',
        paddingTop: '20px',
        borderTop: '1px solid var(--border)'
      }}>
        <div id="tour-status" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '50%',
            background: (health?.llm_provider === 'groq' ? health?.groq_configured : health?.ollama_connected) ? 'var(--success)' : 'var(--danger)',
            boxShadow: (health?.llm_provider === 'groq' ? health?.groq_configured : health?.ollama_connected) ? '0 0 6px var(--success)' : '0 0 6px var(--danger)'
          }}/>
          <span style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            color: 'var(--muted)'
          }}>
            {health?.llm_provider === 'groq' 
              ? (health?.groq_configured ? 'Groq online' : 'Groq offline') 
              : (health?.ollama_connected ? 'Ollama connected' : 'Ollama offline')}
          </span>
        </div>
        <button
          onClick={clearChat}
          style={{
            width: '100%',
            background: 'transparent',
            border: '1px solid var(--border)',
            color: 'var(--muted)',
            fontFamily: 'var(--font-sans)',
            fontSize: '12px',
            padding: '8px 12px',
            borderRadius: 'var(--radius-sm)',
            cursor: 'pointer',
            marginBottom: '12px',
            transition: 'border-color 0.15s, color 0.15s'
          }}
          onMouseEnter={e => { e.target.style.borderColor = 'var(--danger)'; e.target.style.color = 'var(--danger)' }}
          onMouseLeave={e => { e.target.style.borderColor = 'var(--border)'; e.target.style.color = 'var(--muted)' }}
        >
          Clear chat
        </button>
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          color: 'var(--muted)',
          lineHeight: 1.6
        }}>🔒 All processing happens locally.</p>
      </div>
    </aside>
  )
}
