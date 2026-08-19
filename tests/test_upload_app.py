import streamlit as st
import numpy as np
import scipy.io.wavfile as wavfile
import io
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.stt_engine import Transcriber
from app.core.translation_engine import Translator
from app.core.response_generator import LLMResponder
from app.core.audio_denoiser import estimate_noise_level, reduce_noise


st.set_page_config(page_title="Vaani File Upload Tester", page_icon="📂", layout="centered")

st.title("Vaani Audio File Upload Tester 📂")
st.markdown("##### Upload a pre-recorded `.wav` file (Hindi, Gujarati, or English) to test the pipeline without microphone permissions.")

# Caching models to avoid reloading on rerun
@st.cache_resource
def load_models():
    return Transcriber(), Translator(), LLMResponder()

try:
    transcriber, translator, llm_responder = load_models()
    st.success("✅ Models loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load models: {e}")
    st.stop()

uploaded_file = st.file_uploader("Choose a WAV audio file", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    
    if st.button("🚀 Process Uploaded Audio"):
        with st.spinner("Processing audio..."):
            try:
                # 1. Read WAV file from uploaded file-like object
                file_bytes = uploaded_file.read()
                sample_rate, data = wavfile.read(io.BytesIO(file_bytes))
                
                # Convert stereo/multi-channel to mono
                if len(data.shape) > 1:
                    data = data[:, 0]
                
                # Normalize int16 -> float32
                if data.dtype == np.int16:
                    audio_float32 = data.astype(np.float32) / 32768.0
                elif data.dtype == np.float32:
                    audio_float32 = data
                else:
                    st.error(f"Unsupported audio data type: {data.dtype}")
                    st.stop()
                
                # Resample to 16000Hz if needed (Whisper requirement)
                if sample_rate != 16000:
                    num_samples = int(len(audio_float32) * 16000 / sample_rate)
                    xp = np.arange(len(audio_float32))
                    x = np.linspace(0, len(audio_float32) - 1, num_samples)
                    audio_float32 = np.interp(x, xp, audio_float32).astype(np.float32)
                
                # Estimate noise level
                noise_level = estimate_noise_level(audio_float32)
                audio_cleaned = reduce_noise(audio_float32, 16000)
                
                # 2. Run speech-to-text
                st.info("🎙 Transcribing audio...")
                transcribe_result = transcriber.transcribe(audio_cleaned)
                original_text = transcribe_result["text"]
                detected_lang = transcribe_result["language"]
                confidence = transcribe_result["confidence"]
                
                # 3. Translate if not English
                st.info("🌐 Translating text...")
                if detected_lang == "en":
                    english_text = original_text
                else:
                    english_text = translator.translate_mixed(original_text)
                
                # Display results
                st.markdown("### 📊 Pipeline Results")
                st.write(f"**Detected Language**: `{detected_lang.upper()}` (Confidence: {confidence:.2%})")
                st.write(f"**Noise Level**: `{noise_level}`")
                st.write(f"**Original Transcription**: \"{original_text}\"")
                st.write(f"**English Translation**: \"{english_text}\"")
                
                # 4. Run through LLM
                st.markdown("### 🤖 Assistant Reply")
                payload = [{"role": "user", "content": english_text}]
                
                with st.chat_message("assistant"):
                    st.write_stream(llm_responder.generate_response_stream(payload))
                    
            except Exception as e:
                st.error(f"Error during audio processing: {e}")
