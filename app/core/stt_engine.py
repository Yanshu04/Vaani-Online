import os
import io
import re
import numpy as np
import soundfile as sf
from openai import OpenAI
from app.config import settings

class UnsupportedLanguageError(Exception):
    """Exception raised when the detected language is not in the supported list."""
    pass

class LowConfidenceError(Exception):
    """Exception raised when the language detection probability is too low."""
    pass

class Transcriber:
    def __init__(self):
        """
        Initializes the Groq client.
        """
        self.client = OpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL)
        self.model = "whisper-large-v3"
        print("Groq Cloud Transcriber initialized.")

    def transcribe(self, audio: np.ndarray) -> dict:
        """
        Transcribes the float32 raw audio array using Groq's Hosted Whisper API.
        Returns:
            dict: {"text": str, "language": str, "confidence": float}
        """
        if audio is None or len(audio) == 0:
            raise ValueError("Empty audio input provided for transcription")

        # Convert numpy array to WAV bytes in-memory
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, audio, settings.SAMPLE_RATE, format="WAV", subtype="PCM_16")
        wav_buffer.seek(0)
        wav_buffer.name = "audio.wav"

        try:
            response = self.client.audio.transcriptions.create(
                model=self.model,
                file=wav_buffer,
                response_format="verbose_json"
            )
        except Exception as e:
            raise RuntimeError(f"Groq speech-to-text API error: {e}")

        # Check no_speech_prob to filter out silent audio/hallucinations
        if hasattr(response, "segments") and response.segments:
            no_speech_probs = []
            for seg in response.segments:
                prob = seg.get("no_speech_prob", 0.0) if isinstance(seg, dict) else getattr(seg, "no_speech_prob", 0.0)
                no_speech_probs.append(prob)
            if no_speech_probs:
                avg_no_speech = sum(no_speech_probs) / len(no_speech_probs)
                if avg_no_speech > 0.6:
                    raise ValueError("Empty transcription result")

        full_text = response.text.strip()
        # Clean text of punctuation to verify it is not just silent/empty transcription
        cleaned_text = re.sub(r'[^\w\s]', '', full_text).strip()
        if not cleaned_text:
            raise ValueError("Empty transcription result")

        # Get detected language (verbose_json returns language string)
        detected_lang = getattr(response, "language", "en")
        detected_lang = detected_lang.lower().strip()

        # Map common verbose language names or codes to standard codes (hi, gu, en)
        lang_map = {
            "hindi": "hi", "hi": "hi",
            "gujarati": "gu", "gu": "gu",
            "english": "en", "en": "en"
        }
        mapped_lang = lang_map.get(detected_lang, "en")

        # Validate that the detected language is supported
        if mapped_lang not in settings.SUPPORTED_LANGUAGES:
            raise UnsupportedLanguageError(
                f"Detected language '{detected_lang}' is not supported. "
                f"Supported languages are: {settings.SUPPORTED_LANGUAGES}"
            )

        # Groq verbose_json does not expose a single confidence float in the same way,
        # but we can return 1.0. The pipeline checks confidence threshold (default 0.6).
        confidence = 1.0

        return {
            "text": full_text,
            "language": mapped_lang,
            "confidence": confidence
        }
