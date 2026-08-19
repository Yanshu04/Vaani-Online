import React, { useRef, useState, useEffect } from 'react'
import { transcribeAudio } from '../api/client'

export default function MicButton({
  config,
  recording,
  setRecording,
  disabled,
  onTranscription
}) {
  const [isHovered, setIsHovered] = useState(false)
  const mediaRecorder = useRef(null)
  const chunks = useRef([])
  const streamRef = useRef(null)
  const timeoutRef = useRef(null)
  const audioContextRef = useRef(null)
  const analyserRef = useRef(null)
  const animationFrameRef = useRef(null)

  const idleStyle = {
    width: '38px',
    height: '38px',
    borderRadius: '50%',
    background: isHovered ? '#3b82f6' : '#2563eb',
    border: 'none',
    color: '#ffffff',
    fontSize: '16px',
    cursor: disabled ? 'not-allowed' : 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.15s ease',
    outline: 'none',
    boxShadow: isHovered ? '0 0 16px rgba(59, 130, 246, 0.6)' : '0 2px 10px rgba(37, 99, 235, 0.4)',
    opacity: disabled ? 0.5 : 1
  }

  const recordingStyle = {
    width: '38px',
    height: '38px',
    borderRadius: '50%',
    background: '#ef4444',
    border: 'none',
    color: '#ffffff',
    fontSize: '16px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    outline: 'none',
    boxShadow: '0 0 20px rgba(239, 68, 68, 0.7)',
    animation: 'pulseGlow 1.2s infinite'
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      mediaRecorder.current = new MediaRecorder(stream)
      chunks.current = []
      
      mediaRecorder.current.ondataavailable = e => {
        if (e.data && e.data.size > 0) {
          chunks.current.push(e.data)
        }
      }

      mediaRecorder.current.onstop = async () => {
        setRecording(false)
        
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(t => t.stop())
          streamRef.current = null
        }

        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current)
        }
        if (audioContextRef.current) {
          audioContextRef.current.close()
          audioContextRef.current = null
        }

        if (chunks.current.length > 0) {
          const blob = new Blob(chunks.current, { type: 'audio/wav' })
          try {
            const result = await transcribeAudio(blob, config.whisperModel)
            onTranscription(result)
          } catch (err) {
            console.error('Transcription failed:', err)
          }
        }
      }

      mediaRecorder.current.start()
      setRecording(true)

      timeoutRef.current = setTimeout(() => {
        stopRecording()
      }, 10000)

      if (!config.pttMode) {
        setupSilenceDetection(stream)
      }

    } catch (err) {
      console.error('Failed to start recording:', err)
    }
  }

  function setupSilenceDetection(stream) {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(stream)
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 512
      source.connect(analyser)

      audioContextRef.current = audioContext
      analyserRef.current = analyser

      const bufferLength = analyser.fftSize
      const dataArray = new Uint8Array(bufferLength)

      let lastSpeechTime = Date.now()
      const silenceThreshold = 10
      const silenceDuration = 1500

      function checkSilence() {
        if (!mediaRecorder.current || mediaRecorder.current.state === 'inactive') return

        analyser.getByteTimeDomainData(dataArray)

        let sum = 0
        for (let i = 0; i < bufferLength; i++) {
          const val = (dataArray[i] - 128) / 128
          sum += val * val
        }
        const rms = Math.sqrt(sum / bufferLength) * 100

        if (rms > silenceThreshold) {
          lastSpeechTime = Date.now()
        } else {
          if (Date.now() - lastSpeechTime > silenceDuration) {
            stopRecording()
            return
          }
        }

        animationFrameRef.current = requestAnimationFrame(checkSilence)
      }

      setTimeout(() => {
        checkSilence()
      }, 500)

    } catch (e) {
      console.error('Error setting up Web Audio silence detection:', e)
    }
  }

  function stopRecording() {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    if (mediaRecorder.current && mediaRecorder.current.state !== 'inactive') {
      mediaRecorder.current.stop()
    }
    setRecording(false)
  }

  const handleClick = () => {
    if (config.pttMode) return
    if (recording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const handleMouseDown = () => {
    if (!config.pttMode) return
    startRecording()
  }

  const handleMouseUp = () => {
    if (!config.pttMode) return
    stopRecording()
  }

  return (
    <div style={{ position: 'relative', display: 'inline-flex' }}>
      {recording && (
        <>
          <span style={{
            position: 'absolute', inset: -4,
            borderRadius: '50%',
            background: 'rgba(239, 68, 68, 0.4)',
            animation: 'ripple 1.5s ease-out infinite',
            zIndex: 0
          }}/>
        </>
      )}
      <button
        type="button"
        style={recording ? recordingStyle : idleStyle}
        onClick={handleClick}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onTouchStart={handleMouseDown}
        onTouchEnd={handleMouseUp}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        disabled={disabled}
        title={config.pttMode ? "Hold to speak" : "Click to speak"}
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          <line x1="12" y1="19" x2="12" y2="22"></line>
        </svg>
      </button>
    </div>
  )
}
