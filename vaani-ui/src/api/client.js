const BASE = '/api'

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
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      const chunk = decoder.decode(value)
      fullText += chunk
      onToken(chunk)
    }
    onDone(fullText)
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
