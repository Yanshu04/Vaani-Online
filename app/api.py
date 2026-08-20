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
def health():
    groq_ok = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.strip())
    return {
        "status": "ok",
        "llm_provider": "groq",
        "groq_configured": groq_ok
    }

    }


@app.get("/voices")
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
def chat_stream(req: ChatRequest):
    payload = req.history + [{"role": "user", "content": req.message}]
    target_lang = req.detected_lang

    def generate():
        if target_lang == "en":
            for token in llm.generate_response_stream(payload):
                yield token
        else:
            buffer = ""
            for token in llm.generate_response_stream(payload):
                buffer += token
                
                # Extract completed sentences/paragraphs ending in . ! ? or \n
                matches = list(re.finditer(r'[^.!?\n]*[.!?\n]', buffer))
                if matches:
                    last_match = matches[-1]
                    split_pos = last_match.end()
                    completed = buffer[:split_pos]
                    buffer = buffer[split_pos:]
                    
                    segments = [m.group(0) for m in matches]
                    for segment in segments:
                        if any(c.isalpha() for c in segment):
                            leading_space = segment[:len(segment) - len(segment.lstrip())]
                            trailing_space = segment[len(segment.rstrip()):]
                            inner_text = segment.strip()
                            
                            active_pipe = get_pipeline()
                            translated = active_pipe.translation_engine.translate_to_lang(inner_text, target_lang)
                            yield leading_space + translated + trailing_space
                        else:
                            yield segment
            
            # Translate and yield any remaining text at the end
            if buffer.strip():
                active_pipe = get_pipeline()
                translated = active_pipe.translation_engine.translate_to_lang(buffer.strip(), target_lang)
                leading_space = buffer[:len(buffer) - len(buffer.lstrip())]
                trailing_space = buffer[len(buffer.rstrip()):]
                yield leading_space + translated + trailing_space
            elif buffer:
                yield buffer

    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/tts")
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
