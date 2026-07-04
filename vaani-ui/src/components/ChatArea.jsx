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
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      overflow: 'hidden',
      background: 'var(--bg)'
    }}>
      {!health?.groq_configured && (
        <div style={{
          background: 'rgba(239,68,68,0.1)',
          borderBottom: '1px solid rgba(239,68,68,0.3)',
          color: 'var(--danger)',
          fontFamily: 'var(--font-mono)',
          fontSize: '11px',
          padding: '10px 32px',
          textAlign: 'center',
          letterSpacing: '1px'
        }}>
          Groq not configured — set GROQ_API_KEY to enable chat
        </div>
      )}

      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '32px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        minHeight: 0
      }}>
        {messages.length === 0 ? (
          <div style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px'
          }}>
            <div style={{
              width: '52px', height: '52px', borderRadius: '50%',
              background: 'var(--accent-glow)',
              border: '1px solid var(--accent)',
              display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: '22px'
            }}>🎙</div>
            <p style={{
              fontFamily: 'var(--font-display)',
              fontSize: '18px', fontWeight: 600,
              color: 'var(--text)'
            }}>Start a conversation</p>
            <p style={{
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
              color: 'var(--text-secondary)'
            }}>Speak in Hindi, English, or Gujarati</p>
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

      <div style={{
        borderTop: '1px solid var(--border)',
        padding: '16px 32px',
        background: 'var(--surface)',
        display: 'flex',
        gap: '12px',
        alignItems: 'center'
      }}>
        <form onSubmit={handleFormSubmit} style={{ display: 'flex', flex: 1, gap: '12px', alignItems: 'center' }}>
          <textarea
            id="tour-input"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={streaming}
            placeholder="Speak or type to begin..."
            rows={1}
            style={{
              flex: 1,
              background: 'var(--surface-2)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--text)',
              fontFamily: 'var(--font-sans)',
              fontSize: '14px',
              padding: '12px 16px',
              resize: 'none',
              outline: 'none',
              lineHeight: 1.5,
              transition: 'border-color 0.15s'
            }}
            onFocus={e => e.target.style.borderColor = 'var(--accent)'}
            onBlur={e => e.target.style.borderColor = 'var(--border)'}
          />
          <button
            type="submit"
            disabled={streaming}
            style={{
              background: 'var(--accent)',
              border: 'none',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontFamily: 'var(--font-sans)',
              fontSize: '13px',
              fontWeight: 500,
              padding: '10px 18px',
              cursor: streaming ? 'not-allowed' : 'pointer',
              opacity: streaming ? 0.5 : 1,
              transition: 'background 0.15s'
            }}
            onMouseEnter={e => !streaming && (e.target.style.background = 'var(--accent-hover)')}
            onMouseLeave={e => e.target.style.background = 'var(--accent)'}
          >
            Send
          </button>
        </form>
        <div id="tour-mic" style={{ display: 'inline-flex' }}>
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
  )
}
