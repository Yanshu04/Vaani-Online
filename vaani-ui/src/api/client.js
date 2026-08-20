const API_BASE = import.meta.env.VITE_API_BASE_URL || ''
const BASE = API_BASE

// Keep Render backend warm — ping every 4 minutes to prevent 50-second cold starts
setInterval(() => {
  fetch(`${BASE}/ping`).catch(() => {})
}, 4 * 60 * 1000)

export async function getHealth() {
  const r = await fetch(`${BASE}/health`)
  return r.json()
}

export async function getVoices() {
  const r = await fetch(`${BASE}/voices`)
  return r.json()
}

export async function streamChat(payload, onToken, onDone, onError) {
  try {
    const r = await fetch(`${BASE}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
    const reader = r.body.getReader()
    const decoder = new TextDecoder()
    let fullText = ''
    let translatedText = null
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value)
      fullText += chunk
      // Check for translated marker in accumulated text
      const markerIdx = fullText.indexOf('\n\n__TRANSLATED__:')
      if (markerIdx !== -1) {
        translatedText = fullText.slice(markerIdx + '\n\n__TRANSLATED__:'.length).trim()
        // Only stream the English part before the marker
        const englishPart = fullText.slice(0, markerIdx)
        const newChars = chunk.replace(/\n\n__TRANSLATED__:.*/, '')
        if (newChars) onToken(newChars)
      } else {
        onToken(chunk)
      }
    }
    // If we got a translation, use that as the final display text
    onDone(translatedText || fullText)
  } catch (e) {
    onError(e)
  }
}

export async function getTTS(text, voiceId, rate, volume) {
  const r = await fetch(`${BASE}/tts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: text, voice_id: voiceId, tts_rate: rate, tts_volume: volume })
  })
  return r.blob()
}

export async function transcribeAudio(audioBlob, whisperModel) {
  const form = new FormData()
  form.append('file', audioBlob, 'audio.wav')
  form.append('whisper_model', whisperModel)
  const r = await fetch(`${BASE}/transcribe`, { method: 'POST', body: form })
  return r.json()
}

export async function translateText(text, whisperModel) {
  const form = new FormData()
  form.append('text', text)
  form.append('whisper_model', whisperModel)
  const r = await fetch(`${BASE}/transcribe`, { method: 'POST', body: form })
  return r.json()
}
