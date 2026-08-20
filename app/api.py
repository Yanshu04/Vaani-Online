from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import numpy as np
import soundfile as sf
import io
import re

from app.config import settings
from app.services.pipeline import VoicePipeline
from app.core.audio_denoiser import reduce_noise, estimate_noise_level
from app.core.voice_synthesizer import TTSGenerator
from app.core.response_generator import LLMResponder
from app.middleware.rate_limit import RateLimitMiddleware

app = FastAPI(title="Vaani API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, max_requests=settings.RATE_LIMIT_MAX_REQUESTS, window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS)


pipeline = None
tts = TTSGenerator()
llm = LLMResponder()

# Fast Groq-powered translation (avoids loading heavy NLLB model in streaming path)
def groq_translate(text: str, target_lang: str) -> str:
    """Translate text to target language using Groq API (fast, no local model needed)."""
    lang_names = {"hi": "Hindi", "gu": "Gujarati"}
    lang_name = lang_names.get(target_lang, target_lang)
    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": f"You are a professional translator. Translate the following English text to {lang_name}. Output ONLY the translated text with no explanation, no quotes, no extra words."},
                {"role": "user", "content": text}
            ],
            temperature=0.1,
            max_tokens=512,
            timeout=10
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return text  # Fallback: return original if translation fails

def get_pipeline():
    global pipeline
    if pipeline is None:
        model_size = settings.WHISPER_MODEL
        if os.getenv("RENDER") or os.getenv("PORT"):
            model_size = os.getenv("VAANI_WHISPER_MODEL", "tiny")
        settings.WHISPER_MODEL = model_size
        print(f"Lazy-initializing VoicePipeline with model '{model_size}'...")
        pipeline = VoicePipeline()
    return pipeline

@app.get("/health")
@app.get("/api/health")
def health():
    groq_ok = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
    return {
        "status": "ok",
        "llm_provider": "groq",
        "groq_configured": groq_ok
    }

@app.get("/ping")
@app.get("/api/ping")
def ping():
    """Lightweight keep-alive endpoint to prevent Render cold starts."""
    return {"pong": True}

@app.get("/voices")
@app.get("/api/voices")
def get_voices():
    try:
        return {"voices": tts.get_available_voices()}
    except:
        return {"voices": []}

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
    detected_lang: str = "en"
    voice_id: Optional[str] = None
    tts_enabled: bool = True
    tts_rate: int = 200
    tts_volume: float = 1.0

@app.post("/chat/stream")
@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    payload = req.history + [{"role": "user", "content": req.message}]
    target_lang = req.detected_lang

    def generate():
        if target_lang == "en":
            # English: stream tokens directly, no translation needed
            for token in llm.generate_response_stream(payload):
                yield token
        else:
            # Non-English: collect full LLM response then translate via Groq API (fast)
            full_response = ""
            for token in llm.generate_response_stream(payload):
                full_response += token
                yield token  # Stream English tokens to show progress immediately
            # After streaming completes, send the translated version as a special marker
            if full_response.strip():
                translated = groq_translate(full_response.strip(), target_lang)
                yield f"\n\n__TRANSLATED__:{translated}"

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/tts")
@app.post("/api/tts")
def text_to_speech(req: ChatRequest):
    try:
        wav_bytes = tts.generate_speech(
            req.message,
            voice_id=req.voice_id,
            rate=req.tts_rate,
            volume=req.tts_volume
        )
        return StreamingResponse(io.BytesIO(wav_bytes), media_type="audio/wav")
    except Exception as e:
        return {"error": str(e)}

@app.post("/transcribe")
@app.post("/api/transcribe")
async def transcribe(
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    whisper_model: str = "tiny"
):
    active_pipe = get_pipeline()



    if file is not None:
        audio_bytes = await file.read()
        audio_array, sr = sf.read(io.BytesIO(audio_bytes))
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)
        audio_array = audio_array.astype(np.float32)

        noise_level = estimate_noise_level(audio_array)
        audio_cleaned = reduce_noise(audio_array, settings.SAMPLE_RATE)

        result = active_pipe.stt_engine.transcribe(audio_cleaned)

        original_text = result["text"]
        detected_lang = result["language"]
        if detected_lang not in ["en", "hi", "gu"]:
            gu_match = any(0x0A80 <= ord(c) <= 0x0AFF for c in original_text)
            hi_match = any(0x0900 <= ord(c) <= 0x097F for c in original_text)
            if gu_match:
                detected_lang = "gu"
            elif hi_match:
                detected_lang = "hi"
            else:
                detected_lang = "en"
        confidence = result["confidence"]

    elif text is not None:
        original_text = text
        # Simple unicode-based language detection
        gu_match = any(0x0A80 <= ord(c) <= 0x0AFF for c in text)
        hi_match = any(0x0900 <= ord(c) <= 0x097F for c in text)
        if gu_match:
            detected_lang = "gu"
        elif hi_match:
            detected_lang = "hi"
        else:
            detected_lang = "en"
        confidence = 1.0
        noise_level = "low"
    else:
        return {"error": "No file or text provided"}

    if detected_lang == "en":
        english_text = original_text
    else:
        english_text = active_pipe.translation_engine.translate_mixed(original_text)


    return {
        "original_text": original_text,
        "english_text": english_text,
        "detected_language": detected_lang,
        "confidence": confidence,
        "noise_level": noise_level
    }
