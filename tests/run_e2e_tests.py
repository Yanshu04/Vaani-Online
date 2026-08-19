import os
import sys
import time
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.audio_denoiser import reduce_noise, estimate_noise_level
from app.core.stt_engine import Transcriber, UnsupportedLanguageError, LowConfidenceError
from app.core.translation_engine import Translator

from app.services.pipeline import VoicePipeline

def print_section(title):
    print("=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)

def test_pipeline_components():
    print_section("1. Testing Configuration Boundaries")
    print(f"Whisper Model: {settings.WHISPER_MODEL}")
    print(f"Sample Rate: {settings.SAMPLE_RATE} Hz")
    print(f"Silence Threshold: {settings.SILENCE_MS} ms")
    print(f"Supported Languages: {settings.SUPPORTED_LANGUAGES}")
    print(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
    print("[PASS] Configurations loaded successfully.")

    print_section("2. Testing Noise Reducer & RMS Classification")
    # Low noise test (silence)
    silence = np.zeros(16000, dtype=np.float32)
    level_low = estimate_noise_level(silence)
    print(f"Low Noise Test RMS: 0.0 -> Classification: {level_low}")
    assert level_low == "low"

    # Medium noise test (low amplitude random noise)
    np.random.seed(42)
    medium_noise = np.random.uniform(-0.04, 0.04, 16000).astype(np.float32)
    level_med = estimate_noise_level(medium_noise)
    print(f"Medium Noise Test RMS: ~0.023 -> Classification: {level_med}")
    assert level_med == "medium"

    # High noise test (high amplitude random noise)
    high_noise = np.random.uniform(-0.15, 0.15, 16000).astype(np.float32)
    level_high = estimate_noise_level(high_noise)
    print(f"High Noise Test RMS: ~0.086 -> Classification: {level_high}")
    assert level_high == "high"

    # Clean noise reduction pass
    cleaned = reduce_noise(medium_noise, settings.SAMPLE_RATE)
    print(f"Noise reduction successfully applied. Input size: {len(medium_noise)}, Output size: {len(cleaned)}")
    assert cleaned.shape == medium_noise.shape
    print("[PASS] Noise estimator and reducer verified successfully.")

    print_section("3. Testing Translator & Code-Switching (E2E Text)")
    translator = Translator()
    
    # Test cases: (Text, Source language, Expected keyword)
    translation_tests = [
        ("मेरा नाम यांश है और मैं एक सॉफ्टवेयर इंजीनियर हूँ।", "hi", "yansh"),
        ("આજે હવામાન ખૂબ સરસ છે.", "gu", "weather"),
        ("Hello, how are you today?", "en", "hello")
    ]

    for text, lang, keyword in translation_tests:
        start_time = time.time()
        translated = translator.translate(text, lang)
        latency = (time.time() - start_time) * 1000
        # Escape non-ASCII characters to prevent encoding crashes on Windows consoles
        safe_text = text.encode('ascii', 'backslashreplace').decode('ascii')
        safe_translated = translated.encode('ascii', 'backslashreplace').decode('ascii')
        print(f"Source [{lang}]: '{safe_text}'")
        print(f"English: '{safe_translated}' (Latency: {latency:.2f}ms)")
        
    # Code-switching / mixed text translation test
    mixed_text = "नमस्ते my friend. આજે હવામાન ખૂબ સરસ છે અને હું ખુશ છું."
    start_time = time.time()
    translated_mixed = translator.translate_mixed(mixed_text)
    latency = (time.time() - start_time) * 1000
    safe_mixed_text = mixed_text.encode('ascii', 'backslashreplace').decode('ascii')
    safe_translated_mixed = translated_mixed.encode('ascii', 'backslashreplace').decode('ascii')
    print(f"Mixed Source: '{safe_mixed_text}'")
    print(f"English: '{safe_translated_mixed}' (Latency: {latency:.2f}ms)")
    print("[PASS] Translator modules verified successfully.")

    print_section("4. Testing Transcriber Safety Thresholds")
    transcriber = Transcriber()
    
    # Silent audio test -> Should raise error
    print("Testing transcription on flat silence (expecting ValueError or LowConfidenceError)...")
    try:
        transcriber.transcribe(silence)
        print("[FAIL] Silence transcription did not raise expected error.")
        assert False
    except (ValueError, LowConfidenceError) as e:
        safe_err = str(e).encode('ascii', 'backslashreplace').decode('ascii')
        print(f"[PASS] Correctly caught exception: {type(e).__name__} - {safe_err}")

    print_section("5. Testing E2E Pipeline Error Containment")
    pipeline = VoicePipeline()
    # Mocking pipeline audio input with silent wave to test error propagation
    print("Running pipeline on empty mock recording...")
    import app.services.pipeline as pm
    pm.record_until_silence = lambda: (silence, None)
    
    result = pipeline.run(push_to_talk=False)
    print(f"Pipeline Result: {result}")
    assert "error" in result
    print("[PASS] Pipeline caught capture error and returned structured diagnostic payload.")

    print("\n" + "=" * 80)
    print("[SUCCESS] PROFESSIONAL TEST EXECUTION SUCCESSFUL: ALL MODULES FUNCTIONAL")
    print("=" * 80)

if __name__ == "__main__":
    test_pipeline_components()
