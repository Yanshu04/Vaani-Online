import numpy as np
import pytest
from app.config import settings
from app.core.noise_reducer import estimate_noise_level
from app.core.transcriber import Transcriber, LowConfidenceError
from app.core.translator import Translator
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

def test_transcriber_empty_audio():
    """
    Validates that sending silent audio to the transcriber fails with an expected exception.
    """
    t = Transcriber()
    silence = np.zeros(16000, dtype=np.float32)
    with pytest.raises((ValueError, LowConfidenceError)):
        t.transcribe(silence)

def test_translator_english_passthrough():
    """
    Validates that English inputs return unchanged.
    """
    t = Translator()
    result = t.translate("Hello world", "en")
    assert result == "Hello world"

def test_translator_hindi():
    """
    Validates that the translator converts Hindi text into an English equivalent.
    """
    t = Translator()
    result = t.translate("नमस्ते", "hi")
    assert isinstance(result, str)
    assert len(result.strip()) > 0
    # "नमस्ते" typically translates to "Hello" or similar greetings
    assert "hello" in result.lower() or "hi" in result.lower() or "namaste" in result.lower()

def test_pipeline_no_mic(monkeypatch):
    """
    Validates that the pipeline handles missing audio/silence gracefully by returning
    a descriptive error code dict instead of raising unhandled runtime crashes.
    """
    # Mock audio capture to return a 1-second silent array instead of blocking on actual mic input
    monkeypatch.setattr(pipeline_mod, "record_until_silence", lambda: (np.zeros(16000, dtype=np.float32), None))
    
    pipeline = VoicePipeline()
    result = pipeline.run(push_to_talk=False)
    
    # Assert pipeline caught the ValueError/LowConfidenceError and returned it formatted
    assert isinstance(result, dict)
    assert "error" in result
    assert "error_type" in result

def test_llm_responder_success(monkeypatch):
    """
    Validates that LLMResponder successfully queries Groq and parses the reply.
    """
    from app.core.llm_responder import LLMResponder
    from unittest.mock import MagicMock

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Mocked LLM reply in English."

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    responder = LLMResponder()
    responder.client = mock_client

    response = responder.generate_response([{"role": "user", "content": "Hello"}])
    assert response == "Mocked LLM reply in English."
    mock_client.chat.completions.create.assert_called_once()

def test_llm_responder_api_error(monkeypatch):
    """
    Validates that LLMResponder raises a RuntimeError when Groq API fails.
    """
    from app.core.llm_responder import LLMResponder
    from unittest.mock import MagicMock

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API rate limit exceeded")

    responder = LLMResponder()
    responder.client = mock_client

    with pytest.raises(RuntimeError) as exc_info:
        responder.generate_response([{"role": "user", "content": "Hello"}])
    assert "Error querying Groq API" in str(exc_info.value)

def test_pipeline_e2e_with_mock_llm(monkeypatch):
    """
    Validates that the full VoicePipeline integrates the LLM response correctly
    when audio, transcription, and translation are mocked.
    """
    # Mock audio record to return a silent array
    monkeypatch.setattr(pipeline_mod, "record_until_silence", lambda: (np.zeros(16000, dtype=np.float32), None))
    
    # Mock transcriber transcribe method to succeed
    from app.core.transcriber import Transcriber
    monkeypatch.setattr(Transcriber, "transcribe", lambda self, audio: {
        "text": "नमस्ते",
        "language": "hi",
        "confidence": 0.95
    })
    
    # Mock translator to return expected translation
    from app.core.translator import Translator
    monkeypatch.setattr(Translator, "translate_mixed", lambda self, text: "Hello")
    
    # Mock LLMResponder response
    from app.core.llm_responder import LLMResponder
    monkeypatch.setattr(LLMResponder, "generate_response", lambda self, history: "I am doing well, thank you!")

    pipeline = VoicePipeline()
    result = pipeline.run(push_to_talk=False, chat_history=[])
    
    assert "error" not in result
    assert result["original_text"] == "नमस्ते"
    assert result["english_text"] == "Hello"
    assert result["detected_language"] == "hi"
    assert result["confidence"] == 0.95
    assert result["llm_response"] == "I am doing well, thank you!"
