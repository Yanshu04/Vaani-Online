import numpy as np
import pytest
from app.config import settings
from app.core.audio_denoiser import estimate_noise_level
from app.core.stt_engine import Transcriber, LowConfidenceError
from app.core.translation_engine import Translator
from app.core.response_generator import LLMResponder
from app.services.pipeline import VoicePipeline
import app.services.pipeline as pipeline_mod

def test_config_loads():
    """
    Validates that settings are loaded correctly from environment variables.
    """
    assert settings.SAMPLE_RATE == 16000
    assert "hi" in settings.SUPPORTED_LANGUAGES
    assert "en" in settings.SUPPORTED_LANGUAGES
    assert "gu" in settings.SUPPORTED_LANGUAGES

def test_noise_estimator_low():
    """
    Validates that a flat silent array is evaluated as 'low' noise.
    """
    silent_audio = np.zeros(16000, dtype=np.float32)
    assert estimate_noise_level(silent_audio) == "low"

def test_noise_estimator_high():
    """
    Validates that a loud high-amplitude array is evaluated as 'high' noise.
    """
    loud_audio = np.ones(16000, dtype=np.float32)
    assert estimate_noise_level(loud_audio) == "high"

def test_pipeline_catches_low_confidence(monkeypatch):
    """
    Validates that VoicePipeline catches LowConfidenceError gracefully.
    """
    def mock_record():
        return np.zeros(16000, dtype=np.float32), None

    monkeypatch.setattr(pipeline_mod, "record_until_silence", mock_record)

    def mock_transcribe(self, audio):
        raise LowConfidenceError("Confidence 0.20 below threshold 0.60")

    monkeypatch.setattr(Transcriber, "transcribe", mock_transcribe)

    pipeline = VoicePipeline()
    result = pipeline.run(push_to_talk=False, chat_history=[])
    assert "error" in result
    assert "Confidence" in result["error"]

    assert result["error_type"] == "LowConfidenceError"

def test_llm_responder_groq(monkeypatch):
    """
    Validates that LLMResponder queries Groq API and parses reply.
    """
    monkeypatch.setattr(settings, "GROQ_API_KEY", "mock_key")
    
    class MockChoice:
        message = type("Message", (), {"content": "Hello! How can I help you today?"})()

    class MockCompletion:
        choices = [MockChoice()]

    class MockCompletions:
        def create(self, **kwargs):
            return MockCompletion()

    class MockChat:
        completions = MockCompletions()

    class MockOpenAI:
        def __init__(self, api_key, base_url):
            self.chat = MockChat()

    import app.core.response_generator as resp_gen
    monkeypatch.setattr(resp_gen, "OpenAI", MockOpenAI)

    responder = LLMResponder()
    response = responder.generate_response([{"role": "user", "content": "Hello"}])
    assert response == "Hello! How can I help you today?"

def test_pipeline_e2e_with_mock_llm(monkeypatch):
    """
    Validates that the full VoicePipeline integrates the LLM response correctly
    when audio, transcription, and translation are mocked.
    """
    monkeypatch.setattr(pipeline_mod, "record_until_silence", lambda: (np.zeros(16000, dtype=np.float32), None))
    
    monkeypatch.setattr(Transcriber, "transcribe", lambda self, audio: {
        "text": "नमस्ते",
        "language": "hi",
        "confidence": 0.95
    })
    
    monkeypatch.setattr(Translator, "translate_mixed", lambda self, text: "Hello")
    monkeypatch.setattr(LLMResponder, "generate_response", lambda self, history: "I am doing well, thank you!")

    pipeline = VoicePipeline()
    result = pipeline.run(push_to_talk=False, chat_history=[])
    
    assert "error" not in result
    assert result["original_text"] == "नमस्ते"
    assert result["english_text"] == "Hello"
    assert result["detected_language"] == "hi"
    assert result["confidence"] == 0.95
    assert result["llm_response"] == "I am doing well, thank you!"
