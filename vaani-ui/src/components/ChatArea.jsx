import React, { useEffect, useRef, useState } from 'react'
import MessageBubble from './MessageBubble'
import MicButton from './MicButton'

export default function ChatArea({
  messages,
  streaming,
  recording,
  setRecording,
  config,
  health,
  onSubmitText,
  onAudioTranscribed
}) {
  const [textInput, setTextInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streaming])

  const handleFormSubmit = (e) => {
    e.preventDefault()
    if (!textInput.trim() || streaming || recording) return
    onSubmitText(textInput.trim())
    setTextInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleFormSubmit(e)
    }
  }

  return (
    <div className="glass-panel" style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 32px)',
      margin: '16px 16px 16px 16px',
      borderRadius: '20px',
      overflow: 'hidden',
      position: 'relative'
    }}>
      {/* Warning Banners */}
      {!health?.groq_configured && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.15)',
          borderBottom: '1px solid rgba(239, 68, 68, 0.3)',
          color: '#f87171',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          padding: '8px 24px',
          textAlign: 'center'
        }}>
          Groq not configured — set GROQ_API_KEY in .env to enable chat
        </div>
      )}


      {/* Messages Canvas / Empty Hero */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px 32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        minHeight: 0
      }}>
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            userSelect: 'none'
          }}>
            <div className="mic-hero-glow" style={{
              width: '64px',
              height: '64px',
              borderRadius: '50%',
              background: 'rgba(59, 130, 246, 0.12)',
              border: '1px solid rgba(59, 130, 246, 0.35)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 35px rgba(59, 130, 246, 0.35)'
            }}>
              <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="22"></line>
              </svg>
            </div>
            
            <div style={{ textAlign: 'center' }}>
              <h2 style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '17px',
                fontWeight: 500,
                color: '#ffffff',
                marginBottom: '6px'
              }}>
                Start a conversation.
              </h2>
              <p style={{
                fontFamily: 'var(--font-sans)',
                fontSize: '14px',
                color: '#9ca3af'
              }}>
                Speak in Hindi, English, or Gujarati
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => (
            <MessageBubble
              key={index}
              message={msg}
              streaming={index === messages.length - 1 && streaming && msg.role === 'assistant'}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Docked Bottom Floating Bar */}
      <div style={{
        padding: '0 20px 20px 20px'
      }}>
        <div style={{
          background: 'rgba(20, 27, 44, 0.85)',
          backdropFilter: 'blur(16px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: '30px',
          padding: '6px 8px 6px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)'
        }}>
          <form onSubmit={handleFormSubmit} style={{ display: 'flex', flex: 1, alignItems: 'center' }}>
            <input
              id="tour-input"
              type="text"
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={streaming}
              placeholder="Speak or type to begin..."
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                color: '#ffffff',
                fontFamily: 'var(--font-sans)',
                fontSize: '15px',
                outline: 'none',
                padding: '8px 0'
              }}
            />
            
            <button
              type="submit"
              disabled={!textInput.trim() || streaming}
              style={{
                width: '38px',
                height: '38px',
                borderRadius: '50%',
                background: textInput.trim() ? '#3b82f6' : 'rgba(255, 255, 255, 0.08)',
                border: 'none',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: textInput.trim() && !streaming ? 'pointer' : 'not-allowed',
                opacity: textInput.trim() && !streaming ? 1 : 0.4,
                transition: 'all 0.15s ease',
                marginRight: '6px'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
              </svg>
            </button>
          </form>

          <div id="tour-mic">
            <MicButton
              config={config}
              recording={recording}
              setRecording={setRecording}
              disabled={streaming}
              onTranscription={onAudioTranscribed}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
