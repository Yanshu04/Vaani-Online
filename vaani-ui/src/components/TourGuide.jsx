import React, { useState, useEffect } from 'react'

const TOUR_STEPS = [
  {
    title: "Welcome to Vaani 🎙",
    text: "Vaani is a private voice assistant powered by local AI and Groq Cloud. Let's take a quick 1-minute tour to see how to use it!",
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
    text: "Enable voice output, select from neural voices, and customize the speech speed and volume to your preference.",
    targetId: "tour-tts"
  },
  {
    title: "Groq Cloud API Status",
    text: "Shows if the Groq Cloud API is connected. Set GROQ_API_KEY in your .env file to enable fast online AI responses.",
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

  const overlayStyle = {
    position: 'fixed',
    inset: 0,
    background: step.targetId ? 'rgba(8, 12, 20, 0.45)' : 'rgba(8, 12, 20, 0.75)',
    backdropFilter: 'blur(4px)',
    WebkitBackdropFilter: 'blur(4px)',
    zIndex: 99999,
    display: 'flex',
    alignItems: step.targetId ? 'flex-start' : 'center',
    justifyContent: step.targetId ? 'flex-start' : 'center',
    pointerEvents: 'auto',
    transition: 'all 0.3s ease'
  }

  const cardWidth = 320

  const getCardPositionStyle = () => {
    const baseGlass = {
      background: 'rgba(18, 26, 44, 0.92)',
      backdropFilter: 'blur(24px)',
      WebkitBackdropFilter: 'blur(24px)',
      border: '1px solid rgba(255, 255, 255, 0.12)',
      borderRadius: '16px',
      padding: '24px',
      width: `${cardWidth}px`,
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6), 0 0 25px rgba(59, 130, 246, 0.25)',
      animation: 'fadeUp 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
    }

    if (!coords) {
      return baseGlass
    }

    const { x, y, placement } = coords
    if (placement === 'right') {
      return {
        ...baseGlass,
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translateY(-50%)'
      }
    } else if (placement === 'left') {
      return {
        ...baseGlass,
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-100%, -50%)'
      }
    } else if (placement === 'left-bottom') {
      return {
        ...baseGlass,
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-100%, -100%)'
      }
    } else {
      return {
        ...baseGlass,
        position: 'absolute',
        left: `${x}px`,
        top: `${y}px`,
        transform: 'translate(-50%, -100%)'
      }
    }
  }

  return (
    <div style={overlayStyle} onClick={(e) => e.stopPropagation()}>
      <div style={getCardPositionStyle()}>
        {/* Step Indicator */}
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          letterSpacing: '1.5px',
          textTransform: 'uppercase',
          color: '#60a5fa',
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
          color: '#ffffff',
          marginBottom: '10px',
          letterSpacing: '-0.3px'
        }}>
          {step.title}
        </h3>

        {/* Text */}
        <p style={{
          fontFamily: 'var(--font-sans)',
          fontSize: '13px',
          lineHeight: 1.6,
          color: '#9ca3af',
          marginBottom: '22px'
        }}>
          {step.text}
        </p>

        {/* Footer Controls */}
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
              color: '#6b7280',
              fontSize: '12px',
              fontFamily: 'var(--font-sans)',
              cursor: 'pointer',
              outline: 'none',
              padding: '6px 0',
              transition: 'color 0.15s ease'
            }}
            onMouseEnter={e => e.target.style.color = '#ffffff'}
            onMouseLeave={e => e.target.style.color = '#6b7280'}
          >
            Skip Tour
          </button>

          <div style={{ display: 'flex', gap: '8px' }}>
            {currentStep > 0 && (
              <button
                type="button"
                onClick={handleBack}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  color: '#d1d5db',
                  fontSize: '12px',
                  fontWeight: 500,
                  fontFamily: 'var(--font-sans)',
                  padding: '7px 14px',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  outline: 'none',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={e => e.target.style.background = 'rgba(255, 255, 255, 0.15)'}
                onMouseLeave={e => e.target.style.background = 'rgba(255, 255, 255, 0.08)'}
              >
                Back
              </button>
            )}
            <button
              type="button"
              onClick={handleNext}
              style={{
                background: '#3b82f6',
                border: 'none',
                color: '#ffffff',
                fontSize: '12px',
                fontWeight: 600,
                fontFamily: 'var(--font-sans)',
                padding: '7px 18px',
                borderRadius: '8px',
                cursor: 'pointer',
                outline: 'none',
                boxShadow: '0 2px 10px rgba(59, 130, 246, 0.4)',
                transition: 'all 0.15s ease'
              }}
              onMouseEnter={e => e.target.style.background = '#2563eb'}
              onMouseLeave={e => e.target.style.background = '#3b82f6'}
            >
              {currentStep === TOUR_STEPS.length - 1 ? 'Finish' : 'Next'}
            </button>
          </div>
        </div>

        {/* Decorative Pointer Arrow */}
        {coords && coords.placement === 'right' && (
          <div style={{
            position: 'absolute',
            left: '-6px',
            top: '50%',
            transform: 'translateY(-50%) rotate(45deg)',
            width: '12px',
            height: '12px',
            background: 'rgba(18, 26, 44, 0.92)',
            borderLeft: '1px solid rgba(255, 255, 255, 0.12)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
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
            background: 'rgba(18, 26, 44, 0.92)',
            borderRight: '1px solid rgba(255, 255, 255, 0.12)',
            borderTop: '1px solid rgba(255, 255, 255, 0.12)',
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
            background: 'rgba(18, 26, 44, 0.92)',
            borderRight: '1px solid rgba(255, 255, 255, 0.12)',
            borderTop: '1px solid rgba(255, 255, 255, 0.12)',
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
            background: 'rgba(18, 26, 44, 0.92)',
            borderRight: '1px solid rgba(255, 255, 255, 0.12)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
            zIndex: -1
          }} />
        )}
      </div>
    </div>
  )
}
