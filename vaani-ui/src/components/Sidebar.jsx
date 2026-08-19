import React from 'react'

export default function Sidebar({ config, setConfig, voices, health, clearChat, startTour }) {
  const updateConfig = (key, val) => {
    setConfig(prev => ({ ...prev, [key]: val }))
  }

  const selectStyle = {
    background: 'rgba(255, 255, 255, 0.06)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
    fontFamily: 'var(--font-sans)',
    fontSize: '13px',
    padding: '9px 12px',
    borderRadius: '8px',
    width: '100%',
    outline: 'none',
    cursor: 'pointer',
    appearance: 'none',
    backgroundImage: `url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' fill='%239ca3af' viewBox='0 0 16 16'><path d='M7.247 11.14 2.451 5.658C1.885 5.013 2.345 4 3.204 4h9.592a1 1 0 0 1 .753 1.659l-4.796 5.48a1 1 0 0 1-1.506 0z'/></svg>")`,
    backgroundRepeat: 'no-repeat',
    backgroundPosition: 'right 12px center'
  }

  const labelStyle = {
    fontFamily: 'var(--font-mono)',
    fontSize: '10px',
    letterSpacing: '1.2px',
    textTransform: 'uppercase',
    color: '#9ca3af',
    marginBottom: '6px',
    marginTop: '18px',
    fontWeight: 500
  }

  return (
    <aside className="glass-panel" style={{
      width: '250px',
      minWidth: '250px',
      height: 'calc(100vh - 32px)',
      margin: '16px 0 16px 16px',
      borderRadius: '20px',
      display: 'flex',
      flexDirection: 'column',
      padding: '22px 18px',
      overflowY: 'auto',
      zIndex: 10
    }}>
      {/* Title & Tour */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px'
      }}>
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '22px',
          fontWeight: 600,
          color: '#ffffff',
          letterSpacing: '-0.3px',
          margin: 0
        }}>Vaani</h1>
        <button 
          type="button"
          onClick={startTour}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#60a5fa',
            fontFamily: 'var(--font-mono)',
            fontSize: '11px',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            fontWeight: 500,
            cursor: 'pointer',
            outline: 'none'
          }}
        >
          TOUR
        </button>
      </div>

      <div style={{ flex: 1 }}>
        {/* Model */}
        <p style={{ ...labelStyle, marginTop: '8px' }}>MODEL</p>
        <select
          id="tour-model"
          style={selectStyle}
          value={config.whisperModel}
          onChange={(e) => updateConfig('whisperModel', e.target.value)}
        >
          <option value="medium" style={{ background: '#101622', color: '#ffffff' }}>medium</option>
          <option value="small" style={{ background: '#101622', color: '#ffffff' }}>small</option>
          <option value="tiny" style={{ background: '#101622', color: '#ffffff' }}>tiny</option>
          <option value="large-v2" style={{ background: '#101622', color: '#ffffff' }}>large-v2</option>
        </select>

        {/* Recording Mode */}
        <p style={labelStyle}>RECORDING MODE</p>
        <div id="tour-rec-mode" style={{
          display: 'flex',
          gap: '4px',
          background: 'rgba(255, 255, 255, 0.05)',
          padding: '3px',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <button
            type="button"
            onClick={() => updateConfig('pttMode', false)}
            style={{
              flex: 1,
              background: !config.pttMode ? '#3b82f6' : 'transparent',
              border: 'none',
              color: '#ffffff',
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              fontWeight: 500,
              padding: '6px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              boxShadow: !config.pttMode ? '0 2px 8px rgba(59, 130, 246, 0.4)' : 'none',
              transition: 'all 0.15s ease'
            }}
          >
            Auto
          </button>
          <button
            type="button"
            onClick={() => updateConfig('pttMode', true)}
            style={{
              flex: 1,
              background: config.pttMode ? '#3b82f6' : 'transparent',
              border: 'none',
              color: config.pttMode ? '#ffffff' : '#9ca3af',
              fontFamily: 'var(--font-sans)',
              fontSize: '12px',
              fontWeight: 500,
              padding: '6px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              transition: 'all 0.15s ease'
            }}
          >
            PTT
          </button>
        </div>

        {/* Enable TTS */}
        <div id="tour-tts" style={{ marginTop: '20px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
              color: '#ffffff',
              userSelect: 'none'
            }}>
              Enable TTS
            </span>
            <label style={{
              position: 'relative',
              display: 'inline-block',
              width: '38px',
              height: '22px',
              cursor: 'pointer'
            }}>
              <input
                id="tts-enabled-checkbox"
                type="checkbox"
                checked={config.ttsEnabled}
                onChange={(e) => updateConfig('ttsEnabled', e.target.checked)}
                style={{ opacity: 0, width: 0, height: 0 }}
              />
              <span style={{
                position: 'absolute',
                inset: 0,
                backgroundColor: config.ttsEnabled ? '#3b82f6' : 'rgba(255, 255, 255, 0.15)',
                transition: '0.2s',
                borderRadius: '20px',
                boxShadow: config.ttsEnabled ? '0 0 10px rgba(59, 130, 246, 0.5)' : 'none'
              }}>
                <span style={{
                  position: 'absolute',
                  height: '16px',
                  width: '16px',
                  left: config.ttsEnabled ? '19px' : '3px',
                  bottom: '3px',
                  backgroundColor: '#ffffff',
                  transition: '0.2s',
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {config.ttsEnabled && (
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  )}
                </span>
              </span>
            </label>
          </div>

          {config.ttsEnabled && (
            <>
              <p style={labelStyle}>VOICE</p>
              <select
                style={selectStyle}
                value={config.voiceId || ''}
                onChange={(e) => updateConfig('voiceId', e.target.value || null)}
              >
                <option value="" style={{ background: '#101622', color: '#ffffff' }}>Default Voice</option>
                {voices.filter(v => v.type === 'edge').length > 0 && (
                  <optgroup label="⚡ Neural Voices (Online)" style={{ background: '#101622', color: '#9ca3af' }}>
                    {voices.filter(v => v.type === 'edge').map(v => (
                      <option key={v.id} value={v.id} style={{ background: '#101622', color: '#ffffff' }}>{v.name}</option>
                    ))}
                  </optgroup>
                )}
                {voices.filter(v => v.type === 'sapi5').length > 0 && (
                  <optgroup label="🔊 Windows SAPI5 Voices (Offline)" style={{ background: '#101622', color: '#9ca3af' }}>
                    {voices.filter(v => v.type === 'sapi5').map(v => (
                      <option key={v.id} value={v.id} style={{ background: '#101622', color: '#ffffff' }}>{v.name}</option>
                    ))}
                  </optgroup>
                )}
              </select>

              {/* Speed */}
              <p style={labelStyle}>SPEED ({config.ttsRate})</p>
              <input
                type="range"
                min="100"
                max="300"
                step="10"
                value={config.ttsRate}
                onChange={(e) => updateConfig('ttsRate', parseInt(e.target.value))}
              />

              {/* Volume */}
              <p style={labelStyle}>VOLUME ({Math.round(config.ttsVolume * 100)}%)</p>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={config.ttsVolume}
                onChange={(e) => updateConfig('ttsVolume', parseFloat(e.target.value))}
              />
            </>
          )}
        </div>
      </div>

      {/* Footer Area */}
      <div style={{ marginTop: '20px', paddingTop: '16px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '13px',
          color: '#9ca3af',
          marginBottom: '14px'
        }}>
          <span>{health?.groq_configured ? 'Groq online' : 'Groq offline'}</span>
          <span style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: health?.groq_configured ? '#22c55e' : '#ef4444',
            boxShadow: health?.groq_configured ? '0 0 8px rgba(34, 197, 94, 0.7)' : 'none'
          }}></span>

        </div>

        <button
          type="button"
          onClick={clearChat}
          style={{
            width: '100%',
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            color: '#ffffff',
            fontFamily: 'var(--font-sans)',
            fontSize: '13px',
            fontWeight: 500,
            padding: '10px',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.15s ease',
            marginBottom: '12px'
          }}
          onMouseEnter={e => e.target.style.background = 'rgba(255, 255, 255, 0.14)'}
          onMouseLeave={e => e.target.style.background = 'rgba(255, 255, 255, 0.08)'}
        >
          Clear chat
        </button>

        <p style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '11px',
          color: '#6b7280',
          textAlign: 'center'
        }}>
          All processing happens locally.
        </p>
      </div>
    </aside>
  )
}
