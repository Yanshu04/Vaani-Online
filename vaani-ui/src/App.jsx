import React, { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar'
import ChatArea from './components/ChatArea'
import { getHealth, getVoices, getTTS, translateText } from './api/client'
import { useStream } from './hooks/useStream'
import './App.css'
import TourGuide from './components/TourGuide'

export default function App() {
  const [health, setHealth] = useState(null)
  const [voices, setVoices] = useState([])
  const [messages, setMessages] = useState([])
  const [recording, setRecording] = useState(false)
  const audioRef = useRef(null)

  const [config, setConfig] = useState({
    whisperModel: 'medium',
    pttMode: false,
    ttsEnabled: true,
    voiceId: null,
    ttsRate: 200,
    ttsVolume: 1.0
  })

  const { streaming, sendMessage } = useStream()
  const [showTour, setShowTour] = useState(false)

  // Start tour automatically on first visit
  useEffect(() => {
    const completed = localStorage.getItem('vaani_tour_completed')
    if (!completed) {
      setShowTour(true)
    }
  }, [])

  // Poll health every 5 seconds
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const h = await getHealth()
        setHealth(h)
      } catch (e) {
        setHealth({ status: 'error', llm_provider: 'local', ollama_connected: false, groq_configured: false })
      }
    }

    fetchHealth()
    const timer = setInterval(fetchHealth, 5000)
    return () => clearInterval(timer)
  }, [])

  // Fetch voices on load
  useEffect(() => {
    const fetchVoices = async () => {
      try {
        const v = await getVoices()
        if (v && v.voices) {
          setVoices(v.voices)
        }
      } catch (e) {
        console.error('Error fetching voices:', e)
      }
    }
    fetchVoices()
  }, [])

  const playAudioBlob = (blob) => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    audio.volume = config.ttsVolume
    audioRef.current = audio
    audio.play()
    audio.onended = () => {
      URL.revokeObjectURL(url)
    }
    audio.onerror = () => {
      URL.revokeObjectURL(url)
    }
  }

  const handleTextSubmit = async (text) => {
    if (streaming || recording) return

    // 1. Detect language
    const guRegex = /[\u0A80-\u0AFF]/
    const hiRegex = /[\u0900-\u097F]/
    const isGujarati = guRegex.test(text)
    const isHindi = hiRegex.test(text)
    const detectedLang = isGujarati ? 'gu' : (isHindi ? 'hi' : 'en')

    let translatedText = text
    let result = {
      original_text: text,
      english_text: text,
      detected_language: detectedLang,
      confidence: 1.0,
      noise_level: 'N/A'
    }

    if (detectedLang !== 'en') {
      try {
        const res = await translateText(text, config.whisperModel)
        if (res && !res.error) {
          result = {
            ...result,
            english_text: res.english_text,
            detected_language: res.detected_language,
            confidence: res.confidence || 1.0,
            noise_level: res.noise_level || 'N/A'
          }
          translatedText = res.english_text
        }
      } catch (err) {
        console.error('Translation failed:', err)
      }
    }

    // 2. Add user message
    const userMsg = {
      role: 'user',
      content: translatedText,
      original_text: result.original_text,
      detected_language: result.detected_language,
      confidence: result.confidence,
      noise_level: result.noise_level
    }

    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)

    // 3. Add empty assistant message placeholder
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    // Build history
    const history = nextMessages.map(m => ({ role: m.role, content: m.content }))

    // 4. Call sendMessage
    try {
      await sendMessage({
        message: translatedText,
        history: history.slice(0, -1),
        detected_lang: result.detected_language,
        voice_id: config.voiceId,
        tts_enabled: config.ttsEnabled,
        tts_rate: config.ttsRate,
        tts_volume: config.ttsVolume
      }, (token) => {
        setMessages(prev => {
          if (prev.length === 0) return prev
          const last = prev[prev.length - 1]
          if (last && last.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + token }
            ]
          }
          return prev
        })
      }, async (fullText) => {
        if (config.ttsEnabled && fullText) {
          try {
            const blob = await getTTS(fullText, config.voiceId, config.ttsRate, config.ttsVolume)
            const audioUrl = URL.createObjectURL(blob)
            setMessages(prev => {
              const updated = [...prev]
              if (updated.length > 0 && updated[updated.length - 1].role === 'assistant') {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  audioUrl: audioUrl
                }
              }
              return updated
            })
            playAudioBlob(blob)
          } catch (e) {
            console.error('TTS Generation failed:', e)
          }
        }
      }, (err) => {
        console.error('Streaming failed:', err)
      })
    } catch (e) {
      console.error(e)
    }
  }

  const handleAudioTranscribed = async (result) => {
    if (!result || result.error) {
      console.error('Audio transcription error:', result?.error)
      return
    }

    const userMsg = {
      role: 'user',
      content: result.english_text,
      original_text: result.original_text,
      detected_language: result.detected_language,
      confidence: result.confidence,
      noise_level: result.noise_level
    }

    const nextMessages = [...messages, userMsg]
    setMessages(nextMessages)

    // Add empty assistant message placeholder
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    // Build history
    const history = nextMessages.map(m => ({ role: m.role, content: m.content }))

    try {
      await sendMessage({
        message: result.english_text,
        history: history.slice(0, -1),
        detected_lang: result.detected_language,
        voice_id: config.voiceId,
        tts_enabled: config.ttsEnabled,
        tts_rate: config.ttsRate,
        tts_volume: config.ttsVolume
      }, (token) => {
        setMessages(prev => {
          if (prev.length === 0) return prev
          const last = prev[prev.length - 1]
          if (last && last.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + token }
            ]
          }
          return prev
        })
      }, async (fullText) => {
        if (config.ttsEnabled && fullText) {
          try {
            const blob = await getTTS(fullText, config.voiceId, config.ttsRate, config.ttsVolume)
            const audioUrl = URL.createObjectURL(blob)
            setMessages(prev => {
              const updated = [...prev]
              if (updated.length > 0 && updated[updated.length - 1].role === 'assistant') {
                updated[updated.length - 1] = {
                  ...updated[updated.length - 1],
                  audioUrl: audioUrl
                }
              }
              return updated
            })
            playAudioBlob(blob)
          } catch (e) {
            console.error('TTS Generation failed:', e)
          }
        }
      }, (err) => {
        console.error('Streaming failed:', err)
      })
    } catch (e) {
      console.error(e)
    }
  }

  const clearChat = () => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
    setMessages([])
  }

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
      <Sidebar
        config={config}
        setConfig={setConfig}
        voices={voices}
        health={health}
        clearChat={clearChat}
        startTour={() => setShowTour(true)}
      />
      <ChatArea
        messages={messages}
        streaming={streaming}
        recording={recording}
        setRecording={setRecording}
        config={config}
        health={health}
        onSubmitText={handleTextSubmit}
        onAudioTranscribed={handleAudioTranscribed}
      />
      {showTour && <TourGuide onComplete={() => setShowTour(false)} />}
    </div>
  )
}
