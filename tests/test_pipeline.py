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
    Validates that LLMResponder successfully requests Ollama and parses the reply.
    """
    from app.core.llm_responder import LLMResponder
    import requests

    class MockResponse:
        def __init__(self, json_data, status_code=200):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def mock_post(url, json, timeout):
        # Verify request details
        assert "api/chat" in url
        assert json["model"] == settings.OLLAMA_MODEL
        assert len(json["messages"]) > 0
        assert json["messages"][0]["role"] == "system"
        return MockResponse({
            "message": {
                "role": "assistant",
                "content": "Mocked LLM reply in English."
            }
        })

    monkeypatch.setattr(requests, "post", mock_post)

    responder = LLMResponder()
    response = responder.generate_response([{"role": "user", "content": "Hello"}])
    assert response == "Mocked LLM reply in English."

def test_llm_responder_timeout(monkeypatch):
    """
    Validates that LLMResponder raises a RuntimeError on HTTP/Connection timeouts.
    """
    from app.core.llm_responder import LLMResponder
    import requests

    def mock_post_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out")

    monkeypatch.setattr(requests, "post", mock_post_timeout)

    responder = LLMResponder()
    with pytest.raises(RuntimeError) as exc_info:
        responder.generate_response([{"role": "user", "content": "Hello"}])
    assert "Ollama server timed out" in str(exc_info.value)

def test_llm_responder_connection_error(monkeypatch):
    """
    Validates that LLMResponder raises a RuntimeError on general request exception.
    """
    from app.core.llm_responder import LLMResponder
    import requests

    def mock_post_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection refused")

    monkeypatch.setattr(requests, "post", mock_post_error)

    responder = LLMResponder()
    with pytest.raises(RuntimeError) as exc_info:
        responder.generate_response([{"role": "user", "content": "Hello"}])
    assert "Cannot connect to the local Ollama server" in str(exc_info.value)

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
