import React, { useState, useEffect, useRef } from 'react'

function AudioPlayer({ src }) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef(null)

  useEffect(() => {
    const audio = audioRef.current
    if (!audio) return

    const onTimeUpdate = () => setCurrentTime(audio.currentTime)
    const onLoadedMetadata = () => setDuration(audio.duration)
    const onEnded = () => {
      setIsPlaying(false)
      setCurrentTime(0)
      if (audioRef.current) {
        audioRef.current.currentTime = 0
      }
    }

    audio.addEventListener('timeupdate', onTimeUpdate)
    audio.addEventListener('loadedmetadata', onLoadedMetadata)
    audio.addEventListener('ended', onEnded)

    setIsPlaying(false)
    setCurrentTime(0)

    return () => {
      audio.removeEventListener('timeupdate', onTimeUpdate)
      audio.removeEventListener('loadedmetadata', onLoadedMetadata)
      audio.removeEventListener('ended', onEnded)
    }
  }, [src])

  const togglePlay = () => {
    if (!audioRef.current) return
    if (isPlaying) {
      audioRef.current.pause()
      setIsPlaying(false)
    } else {
      if (audioRef.current.ended || audioRef.current.currentTime >= audioRef.current.duration) {
        audioRef.current.currentTime = 0
        setCurrentTime(0)
      }
      audioRef.current.play()
      setIsPlaying(true)
    }
  }

  const handleSeek = (e) => {
    const val = parseFloat(e.target.value)
    audioRef.current.currentTime = val
    setCurrentTime(val)
  }

  const formatTime = (secs) => {
    if (isNaN(secs)) return '0:00'
    const m = Math.floor(secs / 60)
    const s = Math.floor(secs % 60).toString().padStart(2, '0')
    return `${m}:${s}`
  }

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      marginTop: '12px',
      padding: '8px 14px',
      background: 'rgba(255, 255, 255, 0.05)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      width: '100%',
      maxWidth: '320px',
      userSelect: 'none'
    }}>
      <audio ref={audioRef} src={src} />
      <button 
        type="button"
        onClick={togglePlay}
        style={{
          background: isPlaying ? '#2563eb' : 'rgba(255, 255, 255, 0.12)',
          border: 'none',
          borderRadius: '50%',
          width: '32px',
          height: '32px',
          minWidth: '32px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          color: '#ffffff',
          transition: 'all 0.15s ease',
          boxShadow: isPlaying ? '0 0 12px rgba(37, 99, 235, 0.6)' : 'none'
        }}
      >
        {isPlaying ? (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
            <rect x="4" y="4" width="4" height="16" rx="1" />
            <rect x="16" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style={{ marginLeft: '2px' }}>
            <polygon points="5,3 19,12 5,21" />
          </svg>
        )}
      </button>
      
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <input 
          type="range"
          min="0"
          max={duration || 0}
          value={currentTime}
          onChange={handleSeek}
          style={{
            width: '100%',
            cursor: 'pointer'
          }}
        />
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '10px',
          fontFamily: 'var(--font-mono)',
          color: '#9ca3af'
        }}>
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  )
}

export default function MessageBubble({ message, streaming }) {
  const { role, content, audio_url, audioUrl, detected_language, confidence, noise_level, original_text } = message
  const isUser = role === 'user'
  const currentAudio = audio_url || audioUrl


  const userStyle = {
    alignSelf: 'flex-end',
    background: 'rgba(37, 99, 235, 0.2)',
    border: '1px solid rgba(59, 130, 246, 0.4)',
    borderRadius: '16px 16px 4px 16px',
    padding: '12px 18px',
    maxWidth: '75%',
    color: '#f3f4f6',
    fontSize: '14px',
    lineHeight: '1.5',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    boxShadow: '0 4px 16px rgba(0, 0, 0, 0.2)'
  }

  const assistantStyle = {
    alignSelf: 'flex-start',
    background: 'rgba(255, 255, 255, 0.04)',
    borderLeft: '3px solid #3b82f6',
    borderTop: '1px solid rgba(255, 255, 255, 0.08)',
    borderRight: '1px solid rgba(255, 255, 255, 0.08)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '4px 16px 16px 16px',
    padding: '14px 20px',
    maxWidth: '85%',
    color: '#f3f4f6',
    fontSize: '14px',
    lineHeight: '1.6',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.25)'
  }

  const metadataRowStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flexWrap: 'wrap',
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: '#9ca3af',
    marginTop: '4px'
  }

  const badgeStyles = {
    hi: {
      background: 'rgba(245, 158, 11, 0.15)',
      color: '#f59e0b',
      border: '1px solid rgba(245, 158, 11, 0.3)'
    },
    en: {
      background: 'rgba(59, 130, 246, 0.15)',
      color: '#60a5fa',
      border: '1px solid rgba(59, 130, 246, 0.3)'
    },
    gu: {
      background: 'rgba(139, 92, 246, 0.15)',
      color: '#a78bfa',
      border: '1px solid rgba(139, 92, 246, 0.3)'
    }
  }

  const getValidLang = (lang) => {
    const norm = (lang || 'en').toLowerCase()
    return (norm === 'hi' || norm === 'gu') ? norm : 'en'
  }

  const badgeStyle = (lang) => {
    const validLang = getValidLang(lang)
    return {
      ...(badgeStyles[validLang]),
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      padding: '2px 8px',
      borderRadius: '20px',
      letterSpacing: '1px',
      textTransform: 'uppercase',
      fontWeight: 500
    }
  }

  const textStyle = {
    fontFamily: 'var(--font-mono)',
    fontSize: '11px',
    color: '#9ca3af'
  }

  return (
    <div className="message" style={{ display: 'flex', flexDirection: 'column', width: '100%' }}>
      {isUser ? (
        <div style={userStyle}>
          <div>{original_text || content}</div>
          {(detected_language || confidence || noise_level || (original_text && original_text !== content)) && (
            <div style={metadataRowStyle}>
              {detected_language && (
                <span style={badgeStyle(detected_language)}>{getValidLang(detected_language)}</span>
              )}
              {confidence !== undefined && confidence !== null && (
                <span style={textStyle}>
                  Conf: {typeof confidence === 'number' ? Math.round(confidence * 100) + '%' : confidence}
                </span>
              )}
              {noise_level && (
                <span style={textStyle}>Noise: {noise_level}</span>
              )}
              {original_text && original_text !== content && (
                <span style={textStyle}>Translation: "{content}"</span>
              )}
            </div>
          )}
        </div>
      ) : (
        <div style={assistantStyle}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div>
              {content}
              {streaming && <span className="cursor">|</span>}
            </div>
            {currentAudio && <AudioPlayer src={currentAudio} />}

          </div>
        </div>
      )}
    </div>
  )
}
