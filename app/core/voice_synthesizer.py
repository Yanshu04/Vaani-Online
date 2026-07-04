import pyttsx3
import threading
import tempfile
import os
import ctypes
import asyncio
import edge_tts

# Premium Edge-TTS Neural Voices
EDGE_VOICES = [
    {
        "id": "en-US-AvaNeural",
        "name": "Edge Ava (Neural - US Female)",
        "gender": "Female",
        "languages": ["en"],
        "type": "edge"
    },
    {
        "id": "en-US-AndrewNeural",
        "name": "Edge Andrew (Neural - US Male)",
        "gender": "Male",
        "languages": ["en"],
        "type": "edge"
    },
    {
        "id": "en-IN-NeerjaNeural",
        "name": "Edge Neerja (Neural - IN Female)",
        "gender": "Female",
        "languages": ["en"],
        "type": "edge"
    },
    {
        "id": "hi-IN-SwaraNeural",
        "name": "Edge Swara (Neural - Hindi Female)",
        "gender": "Female",
        "languages": ["hi"],
        "type": "edge"
    },
    {
        "id": "hi-IN-MadhurNeural",
        "name": "Edge Madhur (Neural - Hindi Male)",
        "gender": "Male",
        "languages": ["hi"],
        "type": "edge"
    },
    {
        "id": "gu-IN-DhwaniNeural",
        "name": "Edge Dhwani (Neural - Gujarati Female)",
        "gender": "Female",
        "languages": ["gu"],
        "type": "edge"
    },
    {
        "id": "gu-IN-NiranjanNeural",
        "name": "Edge Niranjan (Neural - Gujarati Male)",
        "gender": "Male",
        "languages": ["gu"],
        "type": "edge"
    }
]

def run_in_sta_thread(func):
    """
    Decorator/wrapper to execute pyttsx3 operations on a clean STA thread.
    This resolves SAPI5 COM threading mode conflicts (MTA vs STA) inside Streamlit worker threads.
    """
    def wrapper(*args, **kwargs):
        result = []
        error = []
        
        def target():
            try:
                # Initialize COM as STA (Single Threaded Apartment) on this fresh thread
                ctypes.windll.ole32.CoInitialize(None)
                res = func(*args, **kwargs)
                result.append(res)
            except Exception as e:
                import traceback
                traceback.print_exc()
                error.append(e)
            finally:
                try:
                    ctypes.windll.ole32.CoUninitialize()
                except Exception:
                    pass
        
        t = threading.Thread(target=target)
        t.start()
        t.join()
        
        if error:
            raise error[0]
        return result[0] if result else None
    return wrapper

class TTSGenerator:
    """
    Hybrid Text-to-Speech generator utilizing Edge-TTS with SAPI5 offline fallback.
    Executes SAPI5 queries and speech generation inside custom STA threads to prevent Streamlit COM errors.
    """
    def __init__(self):
        pass

    @run_in_sta_thread
    def _get_sapi5_voices(self) -> list[dict]:
        """
        Helper to fetch local Windows SAPI5 voices. Must run inside STA thread.
        """
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        voice_list = []
        for voice in voices:
            voice_list.append({
                "id": voice.id,
                "name": f"SAPI5: {voice.name}",
                "gender": voice.gender,
                "languages": voice.languages,
                "type": "sapi5"
            })
        return voice_list

    def get_available_voices(self) -> list[dict]:
        """
        Dynamically query available voice options. Combines premium online Edge-TTS
        voices with local SAPI5 voices.
        """
        voice_list = []
        
        # 1. Add premium online neural Edge-TTS voices first
        for ev in EDGE_VOICES:
            voice_list.append({
                "id": ev["id"],
                "name": ev["name"],
                "gender": ev["gender"],
                "languages": ev["languages"],
                "type": "edge"
            })
            
        # 2. Add offline local Windows SAPI5 voices
        try:
            sapi5_voices = self._get_sapi5_voices()
            voice_list.extend(sapi5_voices)
        except Exception as e:
            # Gracefully degrade if SAPI5 initialization fails (e.g. non-Windows)
            print(f"Warning: Failed to fetch SAPI5 local voices: {e}")
            
        return voice_list

    @run_in_sta_thread
    def generate_speech_to_file(self, text: str, voice_id: str, rate: int, volume: float, temp_file: str):
        """
        Synthesizes text and saves it directly to a temporary file using SAPI5. Must run inside STA thread.
        """
        engine = pyttsx3.init()
        if voice_id:
            engine.setProperty('voice', voice_id)
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume)
        
        engine.save_to_file(text, temp_file)
        engine.runAndWait()

    async def _generate_edge_speech(self, text: str, voice_id: str, rate: int, volume: float) -> bytes:
        """
        Synthesizes text using Edge-TTS online API directly to memory buffer.
        """
        # Convert standard SAPI5 rate (100 to 300, default 200) to Edge-TTS format ("+N%" or "-N%")
        rate_diff = int((rate - 200) / 2)
        rate_str = f"{rate_diff:+d}%" if rate_diff != 0 else "+0%"

        # Convert volume (0.0 to 1.0) to Edge-TTS format ("+N%" or "-N%")
        vol_pct = int((volume - 1.0) * 100)
        volume_str = f"{vol_pct:+d}%" if vol_pct != 0 else "+0%"

        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str, volume=volume_str)
        
        audio_chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])
                
        if not audio_chunks:
            raise ValueError("Edge-TTS returned no audio chunks")
            
        return b"".join(audio_chunks)

    def generate_speech(self, text: str, voice_id: str = None, rate: int = 200, volume: float = 1.0) -> bytes:
        """
        Synthesize text into WAV or MP3 audio bytes offline.
        Uses Edge-TTS if the voice_id is an Edge voice. Falls back to SAPI5 if Edge fails or voice is SAPI5.
        """
        # Check text script for language detection
        is_gujarati = any(0x0A80 <= ord(c) <= 0x0AFF for c in text)
        is_hindi = any(0x0900 <= ord(c) <= 0x097F for c in text)

        effective_voice_id = voice_id
        if not effective_voice_id or effective_voice_id == "null":
            if is_gujarati:
                effective_voice_id = "gu-IN-DhwaniNeural"
            elif is_hindi:
                effective_voice_id = "hi-IN-SwaraNeural"
            else:
                effective_voice_id = "en-US-AvaNeural"
            
        is_edge_voice = any(ev["id"] == effective_voice_id for ev in EDGE_VOICES)
        
        if is_edge_voice:
            try:
                print(f"Generating neural speech via Edge-TTS using voice '{effective_voice_id}'...")
                return asyncio.run(self._generate_edge_speech(text, effective_voice_id, rate, volume))
            except Exception as e:
                print(f"Edge-TTS failed ({e}). Falling back to local offline SAPI5...")
                effective_voice_id = None  # Fallback to default SAPI5 voice
                
        # SAPI5 Local Generation
        temp_dir = tempfile.gettempdir()
        temp_file = os.path.join(temp_dir, next(tempfile._get_candidate_names()) + ".wav")
        
        try:
            sapi5_voice_id = None
            if effective_voice_id and not is_edge_voice:
                sapi5_voice_id = effective_voice_id
                
            self.generate_speech_to_file(text, sapi5_voice_id, rate, volume, temp_file)
            
            if os.path.exists(temp_file):
                with open(temp_file, "rb") as f:
                    audio_bytes = f.read()
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
                return audio_bytes
            else:
                raise FileNotFoundError(f"TTS output file not found: {temp_file}")
        except Exception as e:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
            raise RuntimeError(f"Offline TTS generation failed: {e}")
