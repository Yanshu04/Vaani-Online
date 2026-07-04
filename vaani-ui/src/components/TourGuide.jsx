import React, { useState, useEffect } from 'react'

const TOUR_STEPS = [
  {
    title: "Welcome to Vaani 🎙",
    text: "Vaani is a private, offline voice assistant. Let's take a quick 1-minute tour to see how to use it!",
    targetId: null
  },
  {
    title: "Whisper Speech Model",
    text: "Select the Speech-to-Text model size. Larger models are slower but more accurate. We recommend 'medium' as the sweet spot for performance and accuracy.",
    targetId: "tour-model"
  },
  {
    title: "Recording Mode",
    text: "Switch between 'Auto' mode (automatically detects when you stop speaking and submits) and 'PTT' (Push-to-Talk, where you click or hold to talk).",
    targetId: "tour-rec-mode"
  },
  {
    title: "Voice & TTS Settings",
    text: "Enable voice output, select from premium local neural voices, and customize the speech speed and volume to your preference.",
    targetId: "tour-tts"
  },
  {
    title: "Ollama Connection Status",
    text: "Shows if the local Ollama LLM server is active. Ensure Ollama is running on your machine to start chatting.",
    targetId: "tour-status"
  },
  {
    title: "Type or Send Text",
    text: "Prefer typing? Type your prompt in Hindi, Gujarati, or English. Non-English text is automatically translated to English for the AI.",
    targetId: "tour-input"
  },
  {
    title: "Speak Offline 🎙",
    text: "Click or hold this button to speak in Hindi, Gujarati, or English. Vaani will filter background noise, transcribe and translate your voice, and reply in the same language!",
    targetId: "tour-mic"
  }
]

export default function TourGuide({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0)
  const [coords, setCoords] = useState(null)

  useEffect(() => {
    const updatePosition = () => {
      const step = TOUR_STEPS[currentStep]
      if (!step.targetId) {
        setCoords(null)
        return
      }

      const el = document.getElementById(step.targetId)
      if (!el) {
        // Retry position calculation after a short delay if DOM hasn't fully updated
        const timer = setTimeout(updatePosition, 100)
        return () => clearTimeout(timer)
      }

      const rect = el.getBoundingClientRect()
      let x = 0
      let y = 0
      let placement = 'right'

      if (
        step.targetId === 'tour-model' ||
        step.targetId === 'tour-rec-mode' ||
        step.targetId === 'tour-tts' ||
        step.targetId === 'tour-status'
      ) {
        x = rect.right + 16
        y = rect.top + rect.height / 2
        placement = 'right'
      } else if (step.targetId === 'tour-input') {
        x = rect.left + rect.width / 2
        y = rect.top - 16
        placement = 'top'
      } else if (step.targetId === 'tour-mic') {
        x = rect.left - 16
        y = rect.bottom
        placement = 'left-bottom'
      }

      setCoords({ x, y, placement })
    }

    updatePosition()
    window.addEventListener('resize', updatePosition)
    return () => window.removeEventListener('resize', updatePosition)
  }, [currentStep])

  const handleNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(prev => prev + 1)
    } else {
      handleClose()
    }
  }

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(prev => prev - 1)
    }
  }

  const handleClose = () => {
    localStorage.setItem('vaani_tour_completed', 'true')
    onComplete()
  }

  const step = TOUR_STEPS[currentStep]

  // Styles for overlay and popover
  const overlayStyle = {
    position: 'fixed',
    inset: 0,
    background: step.targetId ? 'rgba(0, 0, 0, 0.4)' : 'rgba(0, 0, 0, 0.65)',
    zIndex: 99999,
    display: 'flex',
    alignItems: step.targetId ? 'flex-start' : 'center',
    justifyContent: step.targetId ? 'flex-start' : 'center',
    pointerEvents: 'auto',
    transition: 'background 0.3s ease'
  }

  const cardWidth = 320

  const getCardPositionStyle = () => {
    if (!coords) {
      return {
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        width: `${cardWidth}px`,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-strong)',
        animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }
    }

    const { x, y, placement } = coords
    if (placement === 'right') {
      return {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translateY(-50%)',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        width: `${cardWidth}px`,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-strong)',
        animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }
    } else if (placement === 'left') {
      return {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-100%, -50%)',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        width: `${cardWidth}px`,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-strong)',
        animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }
    } else if (placement === 'left-bottom') {
      return {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-100%, -100%)',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        width: `${cardWidth}px`,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-strong)',
        animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }
    } else {
      // placement === 'top'
      return {
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -100%)',
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        width: `${cardWidth}px`,
        boxShadow: '0 20px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-strong)',
        animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
      }
    }
  }

  return (
    <div style={overlayStyle} onClick={(e) => e.stopPropagation()}>
      <div style={getCardPositionStyle()}>
        {/* Step Indicator */}
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '9px',
          letterSpacing: '2px',
          textTransform: 'uppercase',
          color: 'var(--accent)',
          marginBottom: '8px',
          fontWeight: 600
        }}>
          Step {currentStep + 1} of {TOUR_STEPS.length}
        </div>

        {/* Title */}
        <h3 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '18px',
          fontWeight: 600,
          color: 'var(--text)',
          marginBottom: '12px',
          letterSpacing: '-0.3px'
        }}>
          {step.title}
        </h3>

        {/* Text */}
        <p style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '13px',
          lineHeight: 1.6,
          color: 'var(--text-secondary)',
          marginBottom: '24px'
        }}>
          {step.text}
        </p>

        {/* Footer controls */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <button
            type="button"
            onClick={handleClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--muted)',
              fontSize: '12px',
              fontFamily: 'var(--font-sans)',
              cursor: 'pointer',
              outline: 'none',
              padding: '8px 0'
            }}
            onMouseEnter={e => e.target.style.color = 'var(--text-secondary)'}
            onMouseLeave={e => e.target.style.color = 'var(--muted)'}
          >
            Skip Tour
          </button>

          <div style={{ display: 'flex', gap: '8px' }}>
            {currentStep > 0 && (
              <button
                type="button"
                onClick={handleBack}
                style={{
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  color: 'var(--text-secondary)',
                  fontSize: '12px',
                  fontWeight: 500,
                  fontFamily: 'var(--font-sans)',
                  padding: '8px 16px',
                  borderRadius: 'var(--radius-sm)',
                  cursor: 'pointer',
                  outline: 'none',
                  transition: 'background 0.2s'
                }}
                onMouseEnter={e => e.target.style.background = 'var(--surface-2)'}
                onMouseLeave={e => e.target.style.background = 'transparent'}
              >
                Back
              </button>
            )}
            <button
              type="button"
              onClick={handleNext}
              style={{
                background: 'var(--accent)',
                border: 'none',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 600,
                fontFamily: 'var(--font-sans)',
                padding: '8px 20px',
                borderRadius: 'var(--radius-sm)',
                cursor: 'pointer',
                outline: 'none',
                transition: 'background 0.2s'
              }}
              onMouseEnter={e => e.target.style.background = 'var(--accent-hover)'}
              onMouseLeave={e => e.target.style.background = 'var(--accent)'}
            >
              {currentStep === TOUR_STEPS.length - 1 ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>

        {/* Decorative arrow pointing to element */}
        {coords && coords.placement === 'right' && (
          <div style={{
            position: 'absolute',
            left: '-6px',
            top: '50%',
            transform: 'translateY(-50%) rotate(45deg)',
            width: '12px',
            height: '12px',
            background: 'var(--surface)',
            borderLeft: '1px solid var(--border)',
            borderBottom: '1px solid var(--border)',
            zIndex: -1
          }} />
        )}
        {coords && coords.placement === 'left' && (
          <div style={{
            position: 'absolute',
            right: '-6px',
            top: '50%',
            transform: 'translateY(-50%) rotate(45deg)',
            width: '12px',
            height: '12px',
            background: 'var(--surface)',
            borderRight: '1px solid var(--border)',
            borderTop: '1px solid var(--border)',
            zIndex: -1
          }} />
        )}
        {coords && coords.placement === 'left-bottom' && (
          <div style={{
            position: 'absolute',
            right: '-6px',
            bottom: '16px',
            transform: 'rotate(45deg)',
            width: '12px',
            height: '12px',
            background: 'var(--surface)',
            borderRight: '1px solid var(--border)',
            borderTop: '1px solid var(--border)',
            zIndex: -1
          }} />
        )}
        {coords && coords.placement === 'top' && (
          <div style={{
            position: 'absolute',
            left: '50%',
            bottom: '-6px',
            transform: 'translateX(-50%) rotate(45deg)',
            width: '12px',
            height: '12px',
            background: 'var(--surface)',
            borderRight: '1px solid var(--border)',
            borderBottom: '1px solid var(--border)',
            zIndex: -1
          }} />
        )}
      </div>
    </div>
  )
}
