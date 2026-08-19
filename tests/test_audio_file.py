import os
import sys
import urllib.request
import numpy as np
from pathlib import Path
from scipy.io import wavfile

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.stt_engine import Transcriber
from app.core.translation_engine import Translator


def download_and_test():
    # Candidate raw speech WAV URLs to try downloading (supporting fallbacks for branches/locations)
    urls = [
        "https://raw.githubusercontent.com/HarshTrivedi/wav2vec2-hindi/main/sample.wav",
        "https://raw.githubusercontent.com/HarshTrivedi/wav2vec2-hindi/master/sample.wav",
        "https://raw.githubusercontent.com/Uberi/speech_recognition/master/reference/english.wav",
        "https://raw.githubusercontent.com/Uberi/speech_recognition/master/tests/english.wav",
        "https://github.com/huggingface/datasets-server/raw/main/cf-workers/src/assets/sample.wav"
    ]
    dest_path = Path(__file__).resolve().parent / "sample_speech.wav"

    print("=" * 80)
    print(" AUDIO FILE END-TO-END PIPELINE TEST")
    print("=" * 80)

    # Step 1: Download the test WAV file if it does not exist
    if not dest_path.exists():
        downloaded = False
        for url in urls:
            print(f"Attempting to download sample speech WAV file from:\n  {url}")
            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
                    out_file.write(response.read())
                print("[OK] Download complete.")
                downloaded = True
                break
            except Exception as e:
                print(f"  - Failed (URL: {url}): {e}")
                
        if not downloaded:
            print("[ERROR] Failed to download any test audio file from the candidate URLs.")
            sys.exit(1)
    else:
        print(f"Using cached test file at: {dest_path}")

    # Step 2: Load the WAV file using scipy
    print("\n[1/3] Loading WAV file and verifying format...")
    try:
        sample_rate, data = wavfile.read(dest_path)
        print(f"  - Sample Rate: {sample_rate} Hz")
        print(f"  - Array Shape: {data.shape}")
        print(f"  - Data Type: {data.dtype}")
        
        # If stereo, take the first channel
        if len(data.shape) > 1:
            print("  - Converting stereo/multi-channel to mono...")
            data = data[:, 0]
            
        # Normalize audio data from int16 to float32 in range [-1.0, 1.0] first
        if data.dtype == np.int16:
            audio_float32 = data.astype(np.float32) / 32768.0
        elif data.dtype == np.float32:
            audio_float32 = data
        else:
            print(f"[ERROR] Unsupported audio data type: {data.dtype}")
            sys.exit(1)
            
        # Whisper expects 16000Hz mono. If the sample rate differs, we resample dynamically.
        if sample_rate != 16000:
            print(f"  - Resampling audio from {sample_rate} Hz to 16000 Hz...")
            num_samples = int(len(audio_float32) * 16000 / sample_rate)
            xp = np.arange(len(audio_float32))
            x = np.linspace(0, len(audio_float32) - 1, num_samples)
            audio_float32 = np.interp(x, xp, audio_float32).astype(np.float32)
            
        print("[OK] Audio data loaded and normalized successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to load audio file: {e}")
        sys.exit(1)

    # Step 3: Run Speech-to-Text (Transcriber)
    print("\n[2/3] Initializing Whisper Transcriber and running transcription...")
    try:
        transcriber = Transcriber()
        result = transcriber.transcribe(audio_float32)
        print("\n--- Transcription Result ---")
        print(f"  - Text:      \"{result['text']}\"")
        print(f"  - Language:  {result['language']}")
        print(f"  - Confidence: {result['confidence']:.2%}")
        print("----------------------------")
        print("[OK] Transcription succeeded.")
    except Exception as e:
        print(f"[ERROR] Transcription failed: {e}")
        sys.exit(1)

    # Step 4: Run Translation (Translator)
    print("\n[3/3] Initializing Translator and running translation...")
    try:
        translator = Translator()
        translated_text = translator.translate_mixed(result['text'])
        print("\n--- Translation Result ---")
        print(f"  - Translated: \"{translated_text}\"")
        print("--------------------------")
        print("[OK] Translation succeeded.")
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("[SUCCESS] END-TO-END AUDIO FILE PIPELINE TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    download_and_test()
